import streamlit as st
from supabase import create_client
import datetime

st.set_page_config(page_title="想法记录", page_icon="🌿", layout="centered")

# ================= 温柔视觉 CSS =================
st.markdown("""
<style>
/* 1. 隐藏顶部工具栏、页脚、和多余的菜单 */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
div[data-testid="stToolbar"] {display: none;}
div[data-testid="stDecoration"] {display: none;}

/* 2. 全局字体和温柔的米白背景 */
html, body, [class*="css"] {
    font-family: "Noto Serif SC", "STSong", "SimSun", serif;
}
.stApp {
    background-color: #FAF8F5;
    color: #3A3A3A;
}

/* 3. 居中并限制页面最大宽度，制造大留白 */
.block-container {
    max-width: 640px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

/* 4. 美化输入框 */
.stTextArea textarea {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    border: 1px solid #E8E4DF !important;
    padding: 16px !important;
    font-size: 16px !important;
    line-height: 1.8 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
}
.stTextArea textarea:focus {
    border-color: #A8C0D6 !important;
    box-shadow: 0 0 0 1px #A8C0D6 !important;
}

/* 5. 美化下拉框 */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    border: 1px solid #E8E4DF !important;
}

/* 6. 美化按钮（低饱和雾蓝色） */
div.stButton > button:first-child {
    background-color: #A8C0D6 !important;
    color: #FFFFFF !important;
    border-radius: 20px !important;
    border: none !important;
    padding: 8px 28px !important;
    font-size: 16px !important;
    font-weight: normal !important;
    transition: all 0.3s ease !important;
}
div.stButton > button:first-child:hover {
    background-color: #93AEC4 !important;
    transform: scale(1.02);
}

/* 7. 把原来的分割线变成更柔和的线条 */
hr {
    border-color: #E8E4DF !important;
    margin: 2em 0 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🌿 想法记录")
st.caption("此刻，你在想什么？")

# ================= 数据库连接 =================
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase = create_client(url, key)

# ================= 输入表单 =================
with st.form("new_thought", clear_on_submit=True):
    content = st.text_area("写下你的想法", placeholder="一句话就够了……", height=120)
    mood = st.selectbox("情绪标签", ["🌿 平静", "☁️ 迷茫", "🔥 冲动", "🌙 孤独", "☀️ 开心", "🍃 释然"])
    submitted = st.form_submit_button("发布")

if submitted and content:
    data = {"content": content, "mood": mood}
    supabase.table("thoughts").insert(data).execute()
    st.success("已记录 🌿")
    st.rerun()

st.divider()
st.subheader("大家的想法")

# ================= 读取并展示数据 =================
response = supabase.table("thoughts").select("*").order("created_at", desc=True).execute()
thoughts = response.data

if not thoughts:
    st.info("还没有想法，写下第一条吧。")
else:
    for t in thoughts:
        # 温柔地格式化时间（从 2026-09-23T02:36:04 变成 09月23日 10:36）
        try:
            dt = datetime.datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))
            dt_local = dt + datetime.timedelta(hours=8) # 假设你需要北京时间，加8小时
            time_str = dt_local.strftime("%m月%d日 %H:%M")
        except:
            time_str = t['created_at']

        # 使用卡片样式包裹每条想法
        with st.container(border=True):
            st.markdown(f"**{t['mood']}**")
            st.write(t['content'])
            st.caption(f"✨ {time_str}")
