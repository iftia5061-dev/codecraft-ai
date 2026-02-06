import streamlit as st
import google.generativeai as genai
import sqlite3
import time
import socket  # অফলাইন চেক করার জন্য নতুন লাইব্রেরি

# ১. ইন্টারনেট কানেকশন চেক ফাংশন
def is_connected():
    try:
        # Google DNS এ কানেক্ট করার চেষ্টা করবে
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

# ২. ডাটাবেজ সেটআপ (অপরিবর্তিত)
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

model = genai.GenerativeModel('gemini-3-flash-preview') 

# ৪. প্রফেশনাল ইন্টারফেস ডিজাইন
st.set_page_config(page_title="CodeCraft AI", layout="wide", page_icon="🚀")

# এই অংশটুকু আপনার স্টাইল সেকশনে আপডেট করুন
# এই অংশটুকু আপনার স্টাইল সেকশনে আপডেট করুন
st.markdown("""
    <style>
    /* মোবাইলে আঙুল দিয়ে স্ক্রল করার ক্ষমতা সচল করা */
    html, body, [data-testid="stAppViewContainer"] {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important; /* iOS এবং Android টাচ স্মুথ করার জন্য */
    }

    /* চ্যাট এরিয়াকে স্ক্রলযোগ্য করা */
    .stMain {
        overflow-y: auto !important;
    }

    /* সাইডবার টাচ স্ক্রল ফিক্স */
    [data-testid="stSidebar"] {
        background-color: #1a1c24 !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }

    /* টেক্সট বক্স এবং মেসেজ যাতে স্ক্রিনে আটকে না থাকে */
    .bot-message, .user-message {
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }

    /* সাইডবার টেক্সট সাদা রাখা */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)
if "current_session" not in st.session_state:
    st.session_state.current_session = str(time.time())

# ৫. সাইডবার
with st.sidebar:
    st.markdown("<h1>CodeCraft</h1>", unsafe_allow_html=True)
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
            if st.button("Delete", key=f"del_{sid}"):
                c.execute('DELETE FROM chat_history WHERE session_id=?', (sid,))
                conn.commit()
                st.rerun()

# ৬. মেইন চ্যাট উইন্ডো
st.title("🚀 CodeCraft AI")
online_status = "Online Mode" if is_connected() else "🔴 Offline Mode (Limited)"
st.markdown(f"<p style='opacity: 0.7;'>{online_status} | Developed by <b>IFTI</b></p>", unsafe_allow_html=True)
st.write("---")

c.execute('SELECT role, content FROM chat_history WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
history_data = c.fetchall()

for role, content in history_data:
    with st.chat_message(role):
        st.markdown(content)

# ৭. স্মার্ট ইনপুট লজিক (অনলাইন/অফলাইন হ্যান্ডলিং)
if prompt := st.chat_input("Ask CodeCraft anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    title = prompt[:25]
    c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
              (st.session_state.current_session, title, "user", prompt))
    conn.commit()

    with st.chat_message("assistant"):
        # কানেকশন চেক করা হচ্ছে
        if is_connected():
            try:
                system_instruction = "You are CodeCraft AI by IFTI. Provide clean code and help naturally."
                full_prompt = f"{system_instruction}\nUser: {prompt}"
                response = model.generate_content(full_prompt)
                ai_response = response.text
                st.markdown(ai_response)
            except Exception as e:
                st.error("API Error occurred.")
                ai_response = "Sorry, I encountered an error while connecting to Gemini."
        else:
            # অফলাইন রিপ্লাই
            ai_response = "⚠️ **Offline Mode Active.** I cannot generate code or access AI without internet. Please check your connection for full features."
            st.warning(ai_response)
            
        c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                  (st.session_state.current_session, title, "assistant", ai_response))
        conn.commit()






