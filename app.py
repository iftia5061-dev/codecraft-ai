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
        # Gemini 3 Flash Preview মডেল ব্যবহার করা হয়েছে
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        system_instruction = "Give direct answers. If the user asks for code, provide it inside markdown blocks. Do not return JSON tools or actions."
        response = model.generate_content(system_instruction + " User Prompt: " + prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image_url(prompt):
    clean_prompt = prompt.replace("image:", "").strip()
    seed = random.randint(0, 999999)
    return f"https://pollinations.ai/p/{clean_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"

# ২. প্রফেশনাল ইন্টারফেস (হিস্ট্রি ফিক্সসহ)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>LOOM AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { 
            background-color: #000; color: #fff; font-family: 'Inter', 'Segoe UI', sans-serif; 
            height: 100%; width: 100%; overflow: hidden; 
            overscroll-behavior: none !important; position: fixed;
        }
        #app-container { display: flex; height: 100vh; width: 100vw; position: relative; }

        /* সাইডবার ডিজাইন */
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

        /* চ্যাট উইন্ডো ও স্ক্রলবার */
        #chat-window { 
            flex-grow: 1; padding: 20px; 
            overflow-y: scroll; display: flex; flex-direction: column; gap: 15px; 
        }
        #chat-window::-webkit-scrollbar { width: 8px; }
        #chat-window::-webkit-scrollbar-track { background: #000; }
        #chat-window::-webkit-scrollbar-thumb { 
            background: #0056b3; border-radius: 10px;
        }

        .user-msg { background: #0056b3; color: white; padding: 12px 16px; border-radius: 18px 18px 0 18px; align-self: flex-end; max-width: 85%; word-wrap: break-word; }
        .bot-msg { background: #1a1a1a; color: #eee; padding: 12px 16px; border-radius: 18px 18px 18px 0; align-self: flex-start; max-width: 85%; border: 1px solid #333; }
        .bot-msg img { width: 100%; border-radius: 10px; margin-top: 10px; }
        pre { background: #000; padding: 12px; border-radius: 8px; overflow-x: auto; color: #0f0; border: 1px solid #333; margin: 10px 0; font-size: 14px; }

        .input-container { padding: 20px; border-top: 1px solid #222; display: flex; gap: 10px; background: #000; padding-bottom: 30px; }
        input { flex-grow: 1; background: #111; border: 1px solid #333; padding: 14px; border-radius: 12px; color: white; outline: none; font-size: 16px; }
        .btn-send { background: #0056b3; border: none; width: 50px; height: 50px; border-radius: 50%; color: white; cursor: pointer; font-size: 20px; }

        /* হিস্ট্রি আইটেম ডিজাইন */
        .btn-new { background: #0056b3; color: white; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; text-align: center; }
        #historyList { flex-grow: 1; overflow-y: auto; }
        .history-item { 
            padding: 12px; border-radius: 8px; background: #161616; margin-bottom: 10px; 
            cursor: pointer; border: 1px solid #222; transition: 0.2s;
        }
        .history-item:hover { background: #222; }
        .history-item .title { font-size: 14px; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .history-controls { display: flex; gap: 10px; font-size: 12px; color: #888; }
        .history-controls span:hover { color: #fff; }
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
                <div style="margin-top:10px;">
                    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-app-pub-6478801956648313" crossorigin="anonymous"></script>
                    <ins class="adsbygoogle" style="display:inline-block;width:320px;height:50px" data-ad-client="ca-app-pub-6478801956648313" data-ad-slot="5044703146"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
                </div>
            </div>
            <div id="chat-window"></div>
            <div class="input-container">
                <input type="text" id="userInput" placeholder="Ask code or 'image: flower'..." onkeypress="if(event.key==='Enter') send()">
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
                item.innerHTML = `
                    <div class="title" onclick="loadChat('${id}')">${chats[id].title}</div>
                    <div class="history-controls">
                        <span onclick="renameChat('${id}')">Rename</span>
                        <span onclick="deleteChat('${id}')">Delete</span>
                    </div>
                `;
                list.appendChild(item);
            });
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
            chats[id].messages.forEach(m => appendMessage(m.role, m.text, false));
            document.getElementById('sidebar').classList.remove('active');
            win.scrollTo(0, win.scrollHeight);
        }

        function renameChat(id) {
            const newName = prompt("Enter new title:", chats[id].title);
            if (newName) {
                chats[id].title = newName;
                saveToLocal();
            }
        }

        function deleteChat(id) {
            if (confirm("Delete this chat?")) {
                delete chats[id];
                if (currentChatId === id) startNewChat();
                saveToLocal();
            }
        }

        function appendMessage(role, text, save = true) {
            const win = document.getElementById('chat-window');
            const div = document.createElement('div');
            div.className = role === 'user' ? 'user-msg' : 'bot-msg';
            
            let formattedText = text;
            if (text.includes('```')) {
                formattedText = text.replace(/```(?:html|css|javascript|python|js|)?([\s\S]*?)```/g, '<pre>$1</pre>');
            }
            div.innerHTML = formattedText;
            win.appendChild(div);
            win.scrollTo(0, win.scrollHeight);

            if (save && currentChatId) {
                if (!chats[currentChatId]) {
                    chats[currentChatId] = { title: text.substring(0, 20) + "...", messages: [] };
                }
                chats[currentChatId].messages.push({ role, text });
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
            loading.innerText = 'Processing...';
            document.getElementById('chat-window').appendChild(loading);

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                loading.remove();

                const reply = data.image ? `<img src="${data.image}" alt="AI Image">` : data.reply;
                appendMessage('bot', reply);
            } catch (e) {
                loading.innerText = "Error: Connection failed.";
            }
        }

        // শুরুতে হিস্ট্রি লোড করা
        renderHistory();
        if (Object.keys(chats).length > 0) {
            loadChat(Object.keys(chats).sort((a, b) => b - a)[0]);
        } else {
            startNewChat();
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
        return jsonify({"image": generate_image_url(msg)})
    return jsonify({"reply": get_ai_response(msg)})

if __name__ == '__main__':
    app.run(debug=True)
