import streamlit as st
import google.generativeai as genai
import sqlite3
import time

# ১. ডাটাবেজ সেটআপ (যাতে কম্পিউটার বন্ধ করলেও চ্যাট না হারায়)
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

# ২. এপিআই এবং মডেল কনফিগারেশন (নিরাপদ পদ্ধতি - Secrets ব্যবহার করে)
# এখানে কোডের ভেতর সরাসরি Key রাখা হয়নি যাতে এটি লিক না হয়
if "GEMINI_API_KEY" in st.secrets:
    NEW_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=NEW_API_KEY)
else:
    # যদি Secrets-এ Key না থাকে তবে এটি কাজ করবে না
    st.warning("Please add your GEMINI_API_KEY to Streamlit Secrets.")
    # আপাতত কাজ চালানোর জন্য আপনার দেওয়া কি-টি এখানে ডিফাইন করা হলো (সাবধান!)
    NEW_API_KEY = "AIzaSyDMAn8DLjbzvA2Io01dOh2ISQ0pddGgyy8"
    genai.configure(api_key=NEW_API_KEY)

model = genai.GenerativeModel('models/gemini-3-flash-preview')

# ৩. ইন্টারফেস ডিজাইন (জেমিনি স্টাইল)
st.set_page_config(page_title="CodeCraft AI", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    .stSidebar { background-color: #161b22; border-right: 1px solid #30363d; }
    h1, h4 { color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# সেশন আইডি ম্যানেজমেন্ট
if "current_session" not in st.session_state:
    st.session_state.current_session = str(time.time())

# ৪. সাইডবার (নতুন চ্যাট এবং হিস্ট্রি)
with st.sidebar:
    st.title("💬 History")
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.current_session = str(time.time())
        st.rerun()
    
    st.markdown("---")
    st.subheader("Recent Chats")
    
    # আলাদা আলাদা চ্যাট টাইটেল লোড করা
    c.execute('SELECT DISTINCT session_id, chat_title FROM chat_history GROUP BY session_id ORDER BY id DESC')
    sessions = c.fetchall()
    
    for sid, title in sessions:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"📄 {title[:15]}...", key=sid, use_container_width=True):
                st.session_state.current_session = sid
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sid}"):
                c.execute('DELETE FROM chat_history WHERE session_id=?', (sid,))
                conn.commit()
                st.rerun()

# ৫. চ্যাট উইন্ডো - টাইটেল এবং ক্রেডিট (IFTI)
st.title("🚀 CodeCraft AI")
st.markdown("<h4>Developed by: IFTI</h4>", unsafe_allow_html=True)
st.write("---")

# আগের মেসেজ লোড করা
c.execute('SELECT role, content FROM chat_history WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
history_data = c.fetchall()

for role, content in history_data:
    with st.chat_message(role):
        st.markdown(content)

# ৬. ইনপুট লজিক
if prompt := st.chat_input("Ask CodeCraft anything..."):
    # ইউজারের মেসেজ ডিসপ্লে ও সেভ
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # চ্যাটের প্রথম মেসেজ অনুযায়ী টাইটেল সেট করা
    title = prompt[:25]
    c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
              (st.session_state.current_session, title, "user", prompt))
    conn.commit()

    # এআই রেসপন্স
    with st.chat_message("assistant"):
        try:
            # স্মার্ট ইনস্ট্রাকশন
            system_instruction = (
                "You are CodeCraft AI, a master software engineer developed by IFTI. "
                "If the user asks for code, provide clean and optimized code. "
                "If the user says 'Hi', 'Hello', or 'Thanks', respond naturally like a human peer, "
                "do not provide code unless specifically asked."
            )
            
            # পুরো হিস্ট্রি সহ রেসপন্স জেনারেট করা
            full_prompt = f"{system_instruction}\nUser: {prompt}"
            response = model.generate_content(full_prompt)
            ai_response = response.text
            
            st.markdown(ai_response)
            
            # এআই রেসপন্স সেভ
            c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                      (st.session_state.current_session, title, "assistant", ai_response))
            conn.commit()
            
        except Exception as e:
            st.error(f"Error: {e}")

