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
st.markdown("""
    <style>
    /* পুরো অ্যাপের টাচ রেসপন্স ঠিক করা */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        overflow-y: auto !important;
        touch-action: pan-y !important;
    }

    /* বিজ্ঞাপনের জন্য জায়গা (Ad Placeholder) */
    .ad-space {
        background-color: #111;
        color: #555;
        text-align: center;
        padding: 10px;
        border: 1px dashed #333;
        margin: 10px 0;
        font-size: 12px;
        border-radius: 5px;
    }

    /* চ্যাট বক্স ডিজাইন */
    .bot-message { 
        background: #121212; 
        padding: 15px; 
        border-radius: 15px 15px 15px 0px; 
        border: 1px solid #1f1f1f; 
        color: #e0e0e0; 
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }

    .user-message { 
        background: linear-gradient(135deg, #0056b3, #004494); 
        padding: 15px; 
        border-radius: 15px 15px 0px 15px; 
        color: white; 
        margin-bottom: 15px;
        margin-left: 20%;
    }

    /* সাইডবার ডিজাইন */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #1a1a1a;
    }
    
    /* ইমেজ ডিসপ্লে */
    .gen-image {
        border-radius: 12px;
        border: 2px solid #222;
        transition: transform 0.3s;
    }
    .gen-image:hover { transform: scale(1.02); }

    /* --- নতুন আপডেট: লোগো এবং নিচের অংশ পরিষ্কার করা --- */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden !important;} /* ফোর্সিং হাইড */
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    
    /* ইনপুট বক্সকে একদম নিচে নামানো এবং লোগো ঢাকা */
    [data-testid="stBottom"] {
        background-color: #000000 !important;
        padding-bottom: 20px !important;
    }

    /* আপনার ছবির সাথে থাকা বাড়তি এলিমেন্টগুলো লুকানোর চেষ্টা */
    .st-emotion-cache-1kyx606 {display: none !important;}
    
    /* ওপরের বাড়তি সাদা অংশ কমানো */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important; /* নিচের কন্টেন্ট যেন ইনপুট বারের নিচে না ঢাকা পড়ে */
    }

    /* একদম নিচের কোণার লোগো এবং প্রোফাইল পিকচার পুরোপুরি মুছে ফেলা */
    [data-testid="stStatusWidget"], 
    .st-emotion-cache-1kyx606, 
    .st-emotion-cache-6q9sum,
    .st-emotion-cache-1wb9457 {
        display: none !important;
        visibility: hidden !important;
    }

    /* ইনপুট বারের নিচের বাড়তি অংশ কালো করে ঢেকে দেওয়া */
    div[data-testid="stBottomBlockContainer"] {
        background-color: black !important;
    }

    /* নিচের লাল রঙের Hosted with Streamlit ব্যানার এবং প্রোফাইল পুরোপুরি ভ্যানিশ করা */
    header, footer, .viewerBadge_container__1QSob, .st-emotion-cache-1wb9457, .st-emotion-cache-6q9sum {
        display: none !important;
        visibility: hidden !important;
    }

    /* নিচের কোণার প্রোফাইল আইকন এবং লাল ব্যানার লুকানো */
    [data-testid="stStatusWidget"], .viewerBadge_link__1S137 {
        display: none !important;
    }

    /* স্ক্রিনের একদম নিচের অংশকে কালো করে দেওয়া যাতে কোনো কিছু উঁকি না দেয় */
    div[data-testid="stBottomBlockContainer"] {
        background-color: black !important;
        padding-bottom: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)
# চ্যাটের শুরুতে একটি বিজ্ঞাপন (ব্যানার)
import streamlit.components.v1 as components

# ১. আপনার আইডিগুলো এখানে সেট করুন
# আপনার পাবলিশার আইডি আপনার পেমেন্ট প্রোফাইল থেকে নেওয়া হয়েছে: 6478801956648313
publisher_id = "6478801956648313" 
# AdMob থেকে পাওয়া ca-app-pub-xxxxxxxxxxxxxxxx/xxxxxxxxxx আইডিটি এখানে বসান
ad_unit_id = "ca-app-pub-6478801956648313/5044703146" 

# ২. বিজ্ঞাপনের বক্স এবং আসল ব্যানার কোড
ad_html = f"""
<div style="display: flex; justify-content: center; background-color: #000; padding: 10px; border-radius: 10px; border: 1px solid #333; margin-bottom: 20px;">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-app-pub-{publisher_id}"
     crossorigin="anonymous"></script>
    <ins class="adsbygoogle"
     style="display:inline-block;width:320px;height:50px"
     data-ad-client="ca-app-pub-{publisher_id}"
     data-ad-slot="{ad_unit_id.split('/')[-1] if '/' in ad_unit_id else ad_unit_id}"></ins>
    <script>
     (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>
</div>
"""

# ৩. অ্যাপের একদম উপরে বিজ্ঞাপনটি দেখাবে
components.html(ad_html, height=85)

# ... (আপনার বাকি ডাটাবেজ এবং চ্যাট লজিক এখানে থাকবে)

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

# ৭. চ্যাট ইনপুট এবং স্মার্ট রেসপন্স লজিক
if prompt := st.chat_input("Ask anything or type 'image: sunset'"):
    # ইউজারের মেসেজ
    st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    title = prompt[:30]
    
    # ডাটাবেজে ইউজারের মেসেজ সেভ
    c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
              (st.session_state.current_session, title, "user", prompt))
    conn.commit()

    with st.spinner("Processing..."):
        # --- ইমেজ জেনারেশন পার্ট (শুধুমাত্র ইমেজ দিবে) ---
        if prompt.lower().startswith("image:"):
            img_prompt = prompt[6:].strip()
            img_url = generate_image(img_prompt)
            
            # সরাসরি HTML দিয়ে ইমেজ দেখাচ্ছি যাতে কোড না আসে
            st.markdown(f'''
                <div class="bot-message">
                    <p>🎨 Here is your requested image:</p>
                    <img src="{img_url}" class="gen-image">
                </div>
            ''', unsafe_allow_html=True)
            
            # ডাটাবেজে শুধু টেক্সট টুকু সেভ করছি
            c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                      (st.session_state.current_session, title, "assistant", f"Generated Image: {img_prompt}"))
            conn.commit()
        
        # --- সাধারণ চ্যাট বা কোড পার্ট ---
        else:
            try:
                model = get_configured_model()
                # ইনস্ট্রাকশন আরও কড়া করে দেওয়া হয়েছে যেন বাড়তি কথা না বলে
                system_instruction = (
                    "You are CodeCraft AI. If the user asks for code, provide ONLY clean code. "
                    "If they ask a question, answer concisely. Do not mention image generation here."
                )
                
                response = model.generate_content([system_instruction, prompt])
                full_response = response.text
                
                st.markdown(f'<div class="bot-message">{full_response}</div>', unsafe_allow_html=True)
                
                c.execute('INSERT INTO chat_history (session_id, chat_title, role, content) VALUES (?, ?, ?, ?)', 
                          (st.session_state.current_session, title, "assistant", full_response))
                conn.commit()
                
            except Exception as e:
                st.error("API Error! Please check your keys or connection.")








