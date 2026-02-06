import streamlit as st
import google.generativeai as genai
import sqlite3
import time

# ১. ডাটাবেজ সেটআপ (আরও নিরাপদ কানেকশন হ্যান্ডলিং)
def init_db():
    conn = sqlite3.connect('gemini_chats_v3.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  session_id TEXT, 
                  chat_title TEXT, 
                  role TEXT, 
                  content TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# ২. এপিআই কনফিগারেশন
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Secrets-এ API Key পাওয়া যায়নি!")
        st.stop()
except Exception as e:
    st.error("Secrets লোড করতে সমস্যা হয়েছে।")
    st.stop()

# ৩. ইন্টারফেস ডিজাইন
st.set_page_config(page_title="CodeCraft AI", layout="wide", page_icon="🚀")

# কাস্টম সিএসএস (ডিজাইন আরও উন্নত করা হয়েছে)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stSidebar { background-color: #161b22; border-right: 1px solid #30363d; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
    .stChatInputContainer { padding-bottom: 20px; }
    h1 { color: #f3ba2f; font-weight: 800; }
    .developer-tag { color: #a0a5b1; font-size: 14px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# মডেল সেটআপ
model = genai.GenerativeModel('gemini-3-flash-preview') # লেটেস্ট স্টেবল মডেল

if "current_session" not in st.session_state:
    st.session_state.current_session = str(time.time())

# ৪. সাইডবার লজিক
with st.sidebar:
    st.title("💬 History")
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.current_session = str(time.time())
        st.rerun()
    
    st.markdown("---")
    st.subheader("Recent Chats")
    
    c = conn.cursor()
    c.execute('SELECT DISTINCT session_id, chat_title FROM chat_history GROUP BY session_id ORDER BY id DESC')
    sessions = c.fetchall()
    
    for sid, title in sessions:
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(f"📄 {title[:18]}", key=sid, use_container_width=True):
                st.session_state.current_session = sid
                st.rerun()
        with col2:
            if st.button("Delet", key=f"del_{sid}"):
                c.execute('DELETE FROM chat_history WHERE session_id=?', (sid,))
                conn.commit()
                st.rerun()

# ৫. মূল উইন্ডো
st.title("🚀 CodeCraft AI")
st.markdown('<p class="developer-tag">Developed by: <b>IFTI</b></p>', unsafe_allow_html=True)
st.write("---")

# চ্যাট হিস্ট্রি লোড করা
c.execute('SELECT role, content FROM chat_history WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
history_data = c.fetchall()

for role, content in history_data:
    with st.chat_message(role):
        st.markdown(content)

# ৬. চ্যাট ইনপুট এবং রেসপন্স লজিক
if prompt := st.chat_input("Ask CodeCraft anything..."):
    # ইউজারের মেসেজ দেখানো
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # টাইটেল হ্যান্ডলিং
    title = prompt[:30]
    c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
              (st.session_state.current_session, title, "user", prompt))
    conn.commit()

    # এআই রেসপন্স জেনারেট করা
    with st.chat_message("assistant"):
        message_placeholder = st.empty() # স্ট্রিমিং ইফেক্টের জন্য
        try:
            system_instruction = (
                "You are CodeCraft AI, a master software engineer developed by IFTI. "
                "Provide clean, optimized, and well-commented code. "
                "For general talk, be friendly and concise."
            )
            
            # মডেল কল
            response = model.generate_content([system_instruction, prompt], stream=True)
            
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌") # টাইপিং ইফেক্ট
            
            message_placeholder.markdown(full_response)
            
            # ডাটাবেজে সেভ করা
            c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                      (st.session_state.current_session, title, "assistant", full_response))
            conn.commit()
            
        except Exception as e:
            st.error(f"এপিআই এরর: {e}")


