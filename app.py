import os
import random
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
    if not active_key: return "API Key missing!"
    try:
        genai.configure(api_key=active_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # আপনার পরিচয় এবং উত্তরের স্টাইল এখানে সেট করা হয়েছে
        system_instruction = """
        You are LOOM AI. Your replies must be clean, professional, and well-structured using markdown.
        DO NOT give long-winded answers. Be direct.
        
        About your creator (Provide only when asked about who made you):
        - Name: Md Aminul Islam.
        - Role: Full-stack Web Developer & AI Enthusiast.
        - Skills: Python, Flask, JavaScript, and AI Integration.
        """
        
        response = model.generate_content(system_instruction + " User Prompt: " + prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image_url(prompt):
    clean_prompt = prompt.replace("image:", "").strip()
    seed = random.randint(0, 999999)
    return f"https://pollinations.ai/p/{clean_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"

# ২. প্রফেশনাল ইন্টারফেস (ইমেজ ডাউনলোডসহ)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="icon" type="image/png" href="https://i.ibb.co/Lz9f1zY/logo.png">
    <title>LOOM AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { 
            background-color: #000; color: #fff; font-family: 'Inter', 'Segoe UI', sans-serif; 
            height: 100%; width: 100%; overflow: hidden; 
            overscroll-behavior: none !important; position: fixed;
        }
        #app-container { display: flex; height: 100vh; width: 100vw; position: relative; }

        #sidebar { 
            width: 280px; background-color: #0d0d0d; border-right: 1px solid #222; 
            display: flex; flex-direction: column; padding: 15px; 
            transition: 0.3s ease-in-out; z-index: 1000;
        }
        @media (max-width: 768px) {
            #sidebar { position: absolute; left: -280px; height: 100%; }
            #sidebar.active { left: 0; box-shadow: 10px 0 20px rgba(0,0,0,0.8); }
        }

        .menu-toggle {
            position: fixed; top: 15px; left: 15px;
            background: #1a1a1a; color: white; border: 1px solid #333;
            padding: 8px 12px; border-radius: 8px; z-index: 1001; cursor: pointer;
        }

        #main { flex-grow: 1; display: flex; flex-direction: column; width: 100%; overflow: hidden; }
        .header { padding: 15px; text-align: center; border-bottom: 1px solid #222; background: #000; padding-top: 55px; }

        #chat-window { 
            flex-grow: 1; padding: 20px; 
            overflow-y: scroll; display: flex; flex-direction: column; gap: 15px; 
        }
        #chat-window::-webkit-scrollbar { width: 8px; }
        #chat-window::-webkit-scrollbar-thumb { background: #0056b3; border-radius: 10px; }

        .user-msg { background: #0056b3; color: white; padding: 12px 16px; border-radius: 18px 18px 0 18px; align-self: flex-end; max-width: 85%; word-wrap: break-word; }
        .bot-msg { background: #1a1a1a; color: #eee; padding: 12px 16px; border-radius: 18px 18px 18px 0; align-self: flex-start; max-width: 85%; border: 1px solid #333; line-height: 1.5; }
        .bot-msg img { width: 100%; border-radius: 10px; margin-top: 10px; display: block; }
        
        /* ডাউনলোড বাটন স্টাইল */
        .download-btn {
            display: inline-block; margin-top: 8px; padding: 6px 12px;
            background: #222; border: 1px solid #444; color: #00c3ff;
            text-decoration: none; border-radius: 5px; font-size: 13px; cursor: pointer;
        }

        pre { background: #000; padding: 12px; border-radius: 8px; overflow-x: auto; color: #0f0; border: 1px solid #333; margin: 10px 0; font-size: 14px; }

        .input-container { padding: 20px; border-top: 1px solid #222; display: flex; gap: 10px; background: #000; padding-bottom: 30px; }
        input { flex-grow: 1; background: #111; border: 1px solid #333; padding: 14px; border-radius: 12px; color: white; outline: none; font-size: 16px; }
        .btn-send { background: #0056b3; border: none; width: 50px; height: 50px; border-radius: 50%; color: white; cursor: pointer; font-size: 20px; }

        .btn-new { background: #0056b3; color: white; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; text-align: center; }
        .history-item { padding: 12px; border-radius: 8px; background: #161616; margin-bottom: 10px; cursor: pointer; border: 1px solid #222; }
    </style>
</head>
<body>
    <div id="app-container">
        <div class="menu-toggle" onclick="document.getElementById('sidebar').classList.toggle('active')">☰</div>
        <div id="sidebar">
            <div class="btn-new" onclick="startNewChat()">＋ New Chat</div>
            <div id="historyList"></div>
        </div>
        
        <div id="main">
            <div class="header">
                <h3>LOOM AI</h3>
            </div>
            <div id="chat-window"></div>
            <div class="input-container">
                <input type="text" id="userInput" placeholder="Ask anything or 'image: cat'..." onkeypress="if(event.key==='Enter') send()">
                <button class="btn-send" onclick="send()">➔</button>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        let chats = JSON.parse(localStorage.getItem('loom_ai_chats')) || {};

        function saveToLocal() {
            localStorage.setItem('loom_ai_chats', JSON.stringify(chats));
            renderHistory();
        }

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            Object.keys(chats).sort((a, b) => b - a).forEach(id => {
                const item = document.createElement('div');
                item.className = 'history-item';
                item.innerHTML = `<div onclick="loadChat('${id}')">${chats[id].title}</div>`;
                list.appendChild(item);
            });
        }

        // ইমেজ ডাউনলোড ফাংশন
        async function downloadImage(url) {
            try {
                const res = await fetch(url);
                const blob = await res.blob();
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = "LOOM_AI_Image.png";
                link.click();
            } catch(e) { alert("Download failed!"); }
        }

        function appendMessage(role, text, isImage = false, save = true) {
            const win = document.getElementById('chat-window');
            const div = document.createElement('div');
            div.className = role === 'user' ? 'user-msg' : 'bot-msg';
            
            if (isImage) {
                div.innerHTML = `<img src="${text}"><button class="download-btn" onclick="downloadImage('${text}')">Download Image</button>`;
            } else {
                let formattedText = text.replace(/\\n/g, '<br>')
                                        .replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>')
                                        .replace(/```([\s\S]*?)```/g, '<pre>$1</pre>');
                div.innerHTML = formattedText;
            }
            
            win.appendChild(div);
            win.scrollTo(0, win.scrollHeight);

            if (save && currentChatId) {
                if (!chats[currentChatId]) chats[currentChatId] = { title: text.substring(0, 20), messages: [] };
                chats[currentChatId].messages.push({ role, text, isImage });
                saveToLocal();
            }
        }

        async function send() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text) return;

            if (!currentChatId) startNewChat();
            appendMessage('user', text);
            input.value = '';

            const loading = document.createElement('div');
            loading.className = 'bot-msg';
            loading.innerText = 'LOOM AI is thinking...';
            document.getElementById('chat-window').appendChild(loading);

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                loading.remove();

                if (data.image) {
                    appendMessage('bot', data.image, true);
                } else {
                    appendMessage('bot', data.reply);
                }
            } catch (e) { loading.innerText = "Error: Connection failed."; }
        }

        function startNewChat() {
            currentChatId = Date.now().toString();
            document.getElementById('chat-window').innerHTML = '';
            document.getElementById('sidebar').classList.remove('active');
        }

        function loadChat(id) {
            currentChatId = id;
            const win = document.getElementById('chat-window');
            win.innerHTML = '';
            chats[id].messages.forEach(m => appendMessage(m.role, m.text, m.isImage, false));
            document.getElementById('sidebar').classList.remove('active');
        }

        renderHistory();
        if (!currentChatId) startNewChat();
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
        return jsonify({"image": generate_image_url(msg)})
    return jsonify({"reply": get_ai_response(msg)})

if __name__ == '__main__':
    app.run(debug=True)
