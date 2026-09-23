
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="想法记录", page_icon="🌿", layout="centered")

st.markdown("""
<style>
body { background-color: #FAF8F5; color: #3A3A3A; }
.stTextArea textarea { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E8E4DF; }
</style>
""", unsafe_allow_html=True)

st.title("🌿 想法记录")
st.caption("此刻，你在想什么？")

# 从 Streamlit secrets 读取密钥（云端配置）
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase = create_client(url, key)

with st.form("new_thought", clear_on_submit=True):
    content = st.text_area("写下你的想法", placeholder="一句话就够了……", height=100)
    mood = st.selectbox("情绪标签", ["🌿 平静", "☁️ 迷茫", "🔥 冲动", "🌙 孤独", "☀️ 开心", "🍃 释然"])
    submitted = st.form_submit_button("发布")

if submitted and content:
    data = {"content": content, "mood": mood}
    supabase.table("thoughts").insert(data).execute()
    st.success("已记录 🌿")
    st.rerun()

st.divider()
st.subheader("大家的想法")

response = supabase.table("thoughts").select("*").order("created_at", desc=True).execute()
thoughts = response.data

if not thoughts:
    st.info("还没有想法，写下第一条吧。")
else:
    for t in thoughts:
        with st.container():
            st.markdown(f"**{t['mood']}**")
            st.write(t['content'])
            st.caption(t['created_at'])
            st.divider()
