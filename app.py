import streamlit as st
import google.generativeai as genai
import sqlite3
import time

# ১. ডাটাবেজ সেটআপ (অপরিবর্তিত)
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

# ২. এপিআই কনফিগারেশন (অপরিবর্তিত)
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

model = genai.GenerativeModel('gemini-3-flash-preview') 

# ৩. প্রফেশনাল ইন্টারফেস ডিজাইন (নতুন স্টাইল যোগ করা হয়েছে)
st.set_page_config(page_title="CodeCraft AI", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* মেইন অ্যাপ ব্যাকগ্রাউন্ড */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f8fafc;
    }
    
    /* সাইডবার ডিজাইন */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* চ্যাট বাবল স্টাইল */
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* হেডলাইন এবং টেক্সট */
    h1 {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* বাটন স্টাইল */
    .stButton>button {
        border-radius: 10px !important;
        border: 1px solid #38bdf8 !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #38bdf8 !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

if "current_session" not in st.session_state:
    st.session_state.current_session = str(time.time())

# ৪. সাইডবার (অপরিবর্তিত লজিক)
with st.sidebar:
    st.markdown("<h1>CodeCraft</h1>", unsafe_allow_html=True)
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.current_session = str(time.time())
        st.rerun()
    
    st.markdown("---")
    st.subheader("📜 History")
    
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

# ৫. মেইন চ্যাট উইন্ডো
st.title("🚀 CodeCraft AI")
st.markdown("<p style='opacity: 0.7;'>The Future of Intelligent Coding | Developed by <b>IFTI</b></p>", unsafe_allow_html=True)
st.write("---")

c.execute('SELECT role, content FROM chat_history WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
history_data = c.fetchall()

for role, content in history_data:
    with st.chat_message(role):
        st.markdown(content)

# ৬. ইনপুট লজিক (অপরিবর্তিত সিস্টেম)
if prompt := st.chat_input("Ask CodeCraft anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    title = prompt[:25]
    c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
              (st.session_state.current_session, title, "user", prompt))
    conn.commit()

    with st.chat_message("assistant"):
        try:
            system_instruction = (
                "You are CodeCraft AI, a master software engineer developed by IFTI. "
                "Provide clean and optimized code when asked. "
                "Respond naturally like a peer for casual talk."
            )
            
            full_prompt = f"{system_instruction}\nUser: {prompt}"
            response = model.generate_content(full_prompt)
            ai_response = response.text
            
            st.markdown(ai_response)
            
            c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                      (st.session_state.current_session, title, "assistant", ai_response))
            conn.commit()
            
        except Exception as e:
            st.error(f"Error: {e}")

