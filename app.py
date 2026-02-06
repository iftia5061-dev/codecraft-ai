import streamlit as st
import google.generativeai as genai
import sqlite3
import time

# ১. ডাটাবেজ সেটআপ
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

# ২. এপিআই এবং মডেল কনফিগারেশন (নিরাপদ পদ্ধতি)
# কোডে সরাসরি Key না লিখে Streamlit Secrets ব্যবহার করা হয়েছে
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

# আপনার পছন্দের মডেলটি এখানে সেট করা হয়েছে
model = genai.GenerativeModel('gemini-3-flash-preview') 

# ৩. ইন্টারফেস ডিজাইন
st.set_page_config(page_title="CodeCraft AI", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    .stSidebar { background-color: #161b22; border-right: 1px solid #30363d; }
    h1, h4 { color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

if "current_session" not in st.session_state:
    st.session_state.current_session = str(time.time())

# ৪. সাইডবার
with st.sidebar:
    st.title("💬 History")
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.current_session = str(time.time())
        st.rerun()
    
    st.markdown("---")
    st.subheader("Recent Chats")
    
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

# ৫. চ্যাট উইন্ডো
st.title("🚀 CodeCraft AI")
st.markdown("<h4>Developed by: IFTI</h4>", unsafe_allow_html=True)
st.write("---")

c.execute('SELECT role, content FROM chat_history WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
history_data = c.fetchall()

for role, content in history_data:
    with st.chat_message(role):
        st.markdown(content)

# ৬. ইনপুট লজিক
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
