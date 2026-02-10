import os
import random
import time
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ১. এপিআই কনফিগারেশন
API_KEYS = [
    os.environ.get("API_KEY_1", ""),
    os.environ.get("API_KEY_2", ""),
    os.environ.get("API_KEY_3", "")
]

def get_ai_response(prompt):
    active_key = random.choice([k for k in API_KEYS if k])
    if not active_key: return "API Key Error!"
    genai.configure(api_key=active_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# ২. ইমেজ জেনারেশন
def generate_image_url(prompt):
    seed = random.randint(0, 999999)
    return f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"

# ৩. সুন্দর ইন্টারফেস ডিজাইন (HTML/CSS/JS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOOM AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #000; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; height: 100vh; }
        
        /* সাইডবার ডিজাইন */
        #sidebar { width: 260px; background-color: #050505; border-right: 1px solid #1a1a1a; padding: 15px; display: flex; flex-direction: column; }
        .new-chat { background: #1a1a1a; padding: 12px; border-radius: 8px; text-align: center; cursor: pointer; border: 1px solid #333; margin-bottom: 20px; transition: 0.3s; }
        .new-chat:hover { background: #252525; }
        .history-list { flex-grow: 1; overflow-y: auto; }
        .history-item { padding: 10px; border-radius: 5px; margin-bottom: 5px; font-size: 14px; color: #aaa; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .history-item:hover { background: #111; color: #fff; }

        /* মেইন চ্যাট এরিয়া */
        #main { flex-grow: 1; display: flex; flex-direction: column; position: relative; }
        .header { padding: 15px; text-align: center; border-bottom: 1px solid #1a1a1a; background: #000; }
        #chat-window { flex-grow: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        
        /* চ্যাট বাবল ডিজাইন */
        .user-msg { background: linear-gradient(135deg, #0056b3, #004494); padding: 12px 18px; border-radius: 15px 15px 0 15px; align-self: flex-end; max-width: 80%; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .bot-msg { background: #121212; padding: 12px 18px; border-radius: 15px 15px 15px 0; align-self: flex-start; max-width: 80%; border: 1px solid #1f1f1f; }
        
        /* ইনপুট এরিয়া */
        .input-box { padding: 20px; background: #000; display: flex; gap: 10px; border-top: 1px solid #1a1a1a; }
        input { flex-grow: 1; background: #111; border: 1px solid #333; padding: 12px 20px; border-radius: 25px; color: #fff; outline: none; }
        button { background: #0056b3; border: none; padding: 10px 20px; border-radius: 50%; color: #fff; cursor: pointer; font-size: 18px; }
        
        /* বিজ্ঞাপনের জায়গা */
        .ad-container { width: 100%; text-align: center; margin-bottom: 10px; }
        img.gen-image { width: 100%; border-radius: 10px; margin-top: 10px; border: 1px solid #333; }

        @media (max-width: 768px) { #sidebar { display: none; } }
    </style>
</head>
<body>
    <div id="sidebar">
        <div class="new-chat" onclick="location.reload()">＋ New Chat</div>
        <div class="history-list" id="history">
            <div class="history-item">📄 Previous Chat Example</div>
        </div>
    </div>
    
    <div id="main">
        <div class="header">
            <h3>🚀 CodeCraft AI</h3>
            <p style="font-size: 10px; color: #444;">Developed by IFTI</p>
        </div>

        <div class="ad-container">
            <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-app-pub-6478801956648313" crossorigin="anonymous"></script>
            <ins class="adsbygoogle" style="display:inline-block;width:320px;height:50px" data-ad-client="ca-app-pub-6478801956648313" data-ad-slot="5044703146"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>

        <div id="chat-window"></div>

        <div class="input-box">
            <input type="text" id="userInput" placeholder="Ask anything or image: sunset...">
            <button onclick="send()">➔</button>
        </div>
    </div>

    <script>
        const chatWindow = document.getElementById('chat-window');
        const historyList = document.getElementById('history');

        async function send() {
            const input = document.getElementById('userInput');
            if(!input.value) return;
            
            const text = input.value;
            chatWindow.innerHTML += `<div class="user-msg">${text}</div>`;
            
            // সাইডবারে হিস্ট্রি যোগ করা
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerText = '📄 ' + text.substring(0, 20);
            historyList.prepend(item);
            
            input.value = '';
            chatWindow.scrollTo(0, chatWindow.scrollHeight);

            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            
            if(data.image) {
                chatWindow.innerHTML += `<div class="bot-msg">🎨 Image:<br><img src="${data.image}" class="gen-image"></div>`;
            } else {
                chatWindow.innerHTML += `<div class="bot-msg">${data.reply}</div>`;
            }
            chatWindow.scrollTo(0, chatWindow.scrollHeight);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get("message", "")
    if msg.lower().startswith("image:"):
        return jsonify({"image": generate_image_url(msg[6:].strip())})
    return jsonify({"reply": get_ai_response(msg)})

if __name__ == '__main__':
    app.run(debug=True)
