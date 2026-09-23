import streamlit as st
from supabase import create_client
import datetime
import base64

st.set_page_config(page_title="情绪地球", page_icon="🌍", layout="centered")

st.markdown("""
st.markdown("""
<style>
/* 1. 隐藏顶部工具栏和页脚 */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
div[data-testid="stToolbar"] {display: none;}

/* 2. background image (File name must match exactly) */
[data-testid="stAppViewContainer"] {
    background-image: url("bg.png") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

/* 3. 给内容区加半透明毛玻璃卡片 */
.block-container {
    max-width: 640px;
    background-color: rgba(250, 248, 245, 0.85);
    backdrop-filter: blur(10px);
    border-radius: 24px;
    padding: 3rem 2rem;
    margin-top: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

/* 4. 输入框、按钮等细节美化 */
.stTextArea textarea {background-color: #FFFFFF !important; border-radius: 12px !important; border: 1px solid #E8E4DF !important; padding: 16px !important; font-size: 16px !important; line-height: 1.8 !important;}
div[data-baseweb="select"] > div {background-color: #FFFFFF !important; border-radius: 10px !important; border: 1px solid #E8E4DF !important;}
div.stButton > button:first-child {background-color: #A8C0D6 !important; color: #FFFFFF !important; border-radius: 20px !important; padding: 8px 28px !important; border: none !important; transition: all 0.3s ease !important;}
div.stButton > button:first-child:hover {background-color: #93AEC4 !important; transform: scale(1.02);}
hr {border-color: #E8E4DF !important;}
</style>
""", unsafe_allow_html=True)
""", unsafe_allow_html=True)

st.title("🌍 情绪地球")
st.caption("此刻，你在哪里，在想什么？")

url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase = create_client(url, key)

# ================= 输入表单（增加照片与地点） =================
with st.form("new_thought", clear_on_submit=True):
    content = st.text_area("写下你的想法", placeholder="一句话就够了……", height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        mood = st.selectbox("情绪标签", ["🌿 平静", "☁️ 迷茫", "🔥 冲动", "🌙 孤独", "☀️ 开心", "🍃 释然"])
    with col2:
        location = st.text_input("你在哪里", placeholder="南京")
    
    uploaded_file = st.file_uploader("配一张图吧（可选）", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("发布")

if submitted and content:
    image_url = None
    
    # 1. 上传图片到 Supabase Storage
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_name = f"photo_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        try:
            supabase.storage.from_("photos").upload(file_name, file_bytes)
            image_url = supabase.storage.from_("photos").get_public_url(file_name)
        except Exception as e:
            st.error(f"图片上传失败: {e}")
    
    # 2. 写入数据库
    data = {
        "content": content, 
        "mood": mood, 
        "location": location if location else "未知星球",
        "image_url": image_url
    }
    supabase.table("thoughts").insert(data).execute()
    st.success("已记录 🌍")
    st.rerun()

st.divider()
st.subheader("地球上的记录")

# ================= 读取与地点筛选 =================
response = supabase.table("thoughts").select("*").order("created_at", desc=True).execute()
thoughts = response.data

if not thoughts:
    st.info("这颗星球还很安静，写下第一条吧。")
else:
    # 提取所有非重复的地点（过滤掉空值）
    locations = list(set([t.get('location', '未知星球') for t in thoughts if t.get('location')]))
    # 过滤掉 "未知星球"
    if "未知星球" in locations:
        locations.remove("未知星球")
    
    # 使用 radio 按钮做地点筛选
    if locations:
        selected_location = st.radio("你想去哪颗星球看看？", ["全部"] + sorted(locations), horizontal=True)
    else:
        selected_location = "全部"

    # 根据选择的地点筛选内容
    if selected_location != "全部":
        filtered_thoughts = [t for t in thoughts if t.get('location') == selected_location]
    else:
        filtered_thoughts = thoughts

    # 渲染卡片

# 渲染卡片
for t in filtered_thoughts:
    try:
        dt = datetime.datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))
        dt_local = dt + datetime.timedelta(hours=8)
        time_str = dt_local.strftime("%m月%d日 %H:%M")
    except:
        time_str = t['created_at']
        
    with st.container(border=True):
        # 如果有图片，显示图片
        if t.get('image_url'):
            st.image(t['image_url'], use_container_width=True)
        
        st.markdown(f"**{t['mood']}**")
        st.write(t['content'])
        # 显示地点与时间
        st.caption(f"📍 {t.get('location') or '未知星球'} | ✨ {time_str}")
