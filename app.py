import streamlit as st
import google.generativeai as genai
import sqlite3
import time
import random

# ১. ডাটাবেজ সেটআপ
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

# ২. এপিআই কনফিগারেশন (মাল্টিপল এপিআই কী ব্যবহারের জন্য)
# আপনার সব জিমেইল থেকে নেওয়া এপিআই কীগুলো এই লিস্টে বসান
API_KEYS = [
    st.secrets.get("API_KEY_1", ""),
    st.secrets.get("API_KEY_2", ""),
    st.secrets.get("API_KEY_3", "")
]

def get_configured_model():
    # র্যান্ডমলি একটি এপিআই কী সিলেক্ট করা হচ্ছে যাতে লিমিট না আসে
    active_key = random.choice([k for k in API_KEYS if k])
    if not active_key:
        st.error("Secrets-এ কোনো API Key পাওয়া যায়নি!")
        st.stop()
    genai.configure(api_key=active_key)
    return genai.GenerativeModel('gemini-3-flash-preview')

# ৩. ইমেজ জেনারেশন ফাংশন (ফ্রি এবং আনলিমিটেড)
def generate_image(prompt):
    seed = random.randint(0, 999999)
    # পোলিনেশন এআই ব্যবহার করা হয়েছে যা আপনার কমান্ড অনুযায়ী ছবি দেবে
    image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"
    return image_url

# ৪. ইন্টারফেস ডিজাইন
st.set_page_config(page_title="CodeCraft AI", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* মোবাইলে টাচ এবং স্ক্রল সচল করার জন্য */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #000000 !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        touch-action: pan-y !important;
    }
    .stSidebar { background-color: #000000; border-right: 1px solid #333; }
    
    /* মেসেজ বক্স ডিজাইন */
    .bot-message { background: #1a1a1a; padding: 15px; border-radius: 12px; border: 1px solid #333; color: white; margin-bottom: 10px; }
    .user-message { background: #0056b3; padding: 15px; border-radius: 12px; color: white; margin-bottom: 10px; }
    
    /* টেক্সট এবং টাইটেল কালার */
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .developer-tag { color: #aaaaaa; font-size: 14px; margin-bottom: 20px; }
    
    /* ইমেজ স্টাইল */
    .gen-image { border-radius: 15px; border: 2px solid #333; margin-top: 10px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

if "current_session" not in st.session_state:
    st.session_state.current_session = str(time.time())

# ৫. সাইডবার লজিক
with st.sidebar:
    st.title("💬 History")
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.current_session = str(time.time())
        st.rerun()
    st.markdown("---")
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
            if st.button("🗑️", key=f"del_{sid}"):
                c.execute('DELETE FROM chat_history WHERE session_id=?', (sid,))
                conn.commit()
                st.rerun()

# ৬. মূল উইন্ডো
st.title("🚀 CodeCraft AI")
st.markdown('<p class="developer-tag">Developed by: <b>IFTI</b></p>', unsafe_allow_html=True)
st.write("---")

# চ্যাট হিস্ট্রি লোড করা
c.execute('SELECT role, content FROM chat_history WHERE session_id=? ORDER BY id ASC', (st.session_state.current_session,))
history_data = c.fetchall()

for role, content in history_data:
    if role == "user":
        st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{content}</div>', unsafe_allow_html=True)

# ৭. চ্যাট ইনপুট এবং রেসপন্স লজিক
if prompt := st.chat_input("Ask anything or type 'image: sunset'"):
    # ইউজারের মেসেজ
    st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    title = prompt[:30]
    c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
              (st.session_state.current_session, title, "user", prompt))
    conn.commit()

    with st.spinner("Generating..."):
        # ইমেজ জেনারেশন চেক (যদি ইউজার image: দিয়ে শুরু করে)
        if prompt.lower().startswith("image:"):
            img_prompt = prompt[6:].strip()
            img_url = generate_image(img_prompt)
            reply = f"Here is the image you requested for: **{img_prompt}**"
            st.markdown(f'<div class="bot-message">{reply}<br><img src="{img_url}" class="gen-image"></div>', unsafe_allow_html=True)
            
            c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                      (st.session_state.current_session, title, "assistant", reply))
            conn.commit()
        
        else:
            # সাধারণ চ্যাট রেসপন্স
            try:
                model = get_configured_model()
                system_instruction = "You are CodeCraft AI by IFTI. Provide clean code or helpful answers."
                response = model.generate_content([system_instruction, prompt])
                full_response = response.text
                
                st.markdown(f'<div class="bot-message">{full_response}</div>', unsafe_allow_html=True)
                
                c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                          (st.session_state.current_session, title, "assistant", full_response))
                conn.commit()
            except Exception as e:
                st.error("API limit reached or error occurred. Retrying with another key...")
