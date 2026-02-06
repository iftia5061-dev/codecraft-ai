import streamlit as st
import google.generativeai as genai
import sqlite3
import time
import socket  

# ১. ইন্টারনেট কানেকশন চেক ফাংশন
def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

# ২. ডাটাবেজ সেটআপ
def get_db_connection():
    conn = sqlite3.connect('gemini_chats_v3.db', timeout=30, check_same_thread=False)
    return conn

conn = get_db_connection()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              session_id TEXT, 
              chat_title TEXT, 
              role TEXT, 
              content TEXT)''')
conn.commit()

# ৩. এপিআই কনফিগারেশন
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    else:
        st.error("Secrets-এ API Key পাওয়া যায়নি!")
        st.stop()
except Exception as e:
    st.error("Secrets লোড করতে সমস্যা হয়েছে।")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash') 

# ৪. প্রফেশনাল ইন্টারফেস ডিজাইন এবং টাচ ফিক্স
st.set_page_config(page_title="CodeCraft AI", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* ১. অ্যাপের ভেতরে টাচ এবং স্ক্রল সচল করা */
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important; /* আঙুলের স্পর্শে স্ক্রল নিশ্চিত করে */
    }

    /* ২. ব্যাকগ্রাউন্ড একদম কালো এবং টেক্সট সাদা */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* বটের মেসেজ - ডার্ক ব্যাকগ্রাউন্ডে পরিষ্কার সাদা লেখা */
    .bot-message {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333333;
        margin-bottom: 10px;
        font-size: 16px;
        line-height: 1.6;
    }

    /* ইউজার মেসেজ */
    .user-message {
        background-color: #0056b3 !important;
        color: #ffffff !important;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    /* ৩. সাইডবার ফিক্স - কালো ব্যাকগ্রাউন্ডে সাদা লেখা */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #333333;
    }
    
    /* সাইডবার এবং মেইন বডির সব টেক্সট সাদা করা */
    [data-testid="stSidebar"] *, .stMarkdown p, .stTextInput label, span, p {
        color: #ffffff !important;
    }

    /* ইনপুট বক্সের টেক্সট */
    .stTextInput input {
        color: #ffffff !important;
        background-color: #1a1a1a !important;
    }
    </style>
""", unsafe_allow_html=True)

if "current_session" not in st.session_state:
    st.session_state.current_session = str(time.time())

# ৫. সাইডবার
with st.sidebar:
    st.markdown("<h1 style='color: white;'>CodeCraft</h1>", unsafe_allow_html=True)
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.current_session = str(time.time())
        st.rerun()
    st.markdown("---")
    st.subheader("History")
    c.execute('SELECT DISTINCT session_id, chat_title FROM chat_history GROUP BY session_id ORDER BY id DESC')
    sessions = c.fetchall()
    for sid, title in sessions:
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(f"📄 {title[:18]}", key=sid, use_container_width=True):
                st.session_state.current_session = sid
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}"):
                c.execute('DELETE FROM chat_history WHERE session_id=?', (sid,))
                conn.commit()
                st.rerun()

# ৬. মেইন চ্যাট উইন্ডো
st.title("🚀 CodeCraft AI")
online_status = "Online Mode" if is_connected() else "🔴 Offline Mode"
st.markdown(f"<p style='color: #aaaaaa;'>{online_status} | Developed by <b>IFTI</b></p>", unsafe_allow_html=True)
st.write("---")

c.execute('SELECT role, content FROM chat_history WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
history_data = c.fetchall()

for role, content in history_data:
    if role == "user":
        st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{content}</div>', unsafe_allow_html=True)

# ৭. স্মার্ট ইনপুট লজিক
if prompt := st.chat_input("Ask CodeCraft anything..."):
    st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    
    title = prompt[:25]
    c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
              (st.session_state.current_session, title, "user", prompt))
    conn.commit()

    with st.spinner("Thinking..."):
        if is_connected():
            try:
                system_instruction = "You are CodeCraft AI by IFTI. Provide clean code and help naturally."
                full_prompt = f"{system_instruction}\nUser: {prompt}"
                response = model.generate_content(full_prompt)
                ai_response = response.text
                st.markdown(f'<div class="bot-message">{ai_response}</div>', unsafe_allow_html=True)
            except Exception as e:
                ai_response = "API Error occurred."
                st.error(ai_response)
        else:
            ai_response = "⚠️ Offline Mode: Please check your internet."
            st.warning(ai_response)
            
        c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                  (st.session_state.current_session, title, "assistant", ai_response))
        conn.commit()
