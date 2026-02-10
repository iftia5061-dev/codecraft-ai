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
        
        # System Instruction আরও ক্লিয়ার করা হয়েছে যাতে ভুল আউটপুট না আসে
        system_instruction = """
        You are LOOM AI. Your replies must be direct and clean. Use Markdown.
        
        CRITICAL RULE FOR IMAGES/LOGOS:
        If user asks for an image, logo, drawing or art, you MUST ONLY respond with the prefix "image:" 
        followed by a detailed English prompt. 
        Example: "image: a modern minimalist tech logo for 'LOM'".
        DO NOT provide JSON, DO NOT provide SVG code, DO NOT say you cannot do it.
        
        If the user asks for code, provide only the code block with the language name.
        """
        
        response = model.generate_content(system_instruction + "\nUser Prompt: " + prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image_url(prompt):
    clean_prompt = prompt.replace("image:", "").strip()
    seed = random.randint(0, 999999)
    # Pollinations এর সঠিক ফরম্যাট নিশ্চিত করা হয়েছে
    return f"https://pollinations.ai/p/{clean_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}&nologo=true"

# ২. প্রফেশনাল ইন্টারফেস
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
            background-color: #000; color: #fff; font-family: 'Inter', sans-serif; 
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
            overflow-y: auto; display: flex; flex-direction: column; gap: 15px; 
        }
        #chat-window::-webkit-scrollbar { width: 6px; }
        #chat-window::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }

        .user-msg { background: #0056b3; color: white; padding: 12px 16px; border-radius: 18px 18px 0 18px; align-self: flex-end; max-width: 85%; word-wrap: break-word; }
        .bot-msg { background: #1a1a1a; color: #eee; padding: 12px 16px; border-radius: 18px 18px 18px 0; align-self: flex-start; max-width: 85%; border: 1px solid #333; word-wrap: break-word; }
        .bot-msg img { width: 100%; max-width: 512px; border-radius: 10px; margin-top: 10px; display: block; background: #222; min-height: 200px; }

        .btn-new { background: #0056b3; color: white; padding: 12px; border: none; border-radius: 20px; cursor: pointer; font-weight: bold; margin-bottom: 20px; text-align: center; }
        
        .history-item { 
            position: relative; display: flex; justify-content: space-between; align-items: center;
            padding: 10px 12px; border-radius: 8px; margin-bottom: 5px; cursor: pointer; 
            transition: 0.2s; font-size: 14px; color: #ccc;
        }
        .history-item:hover, .history-item.active { background: #1a1a1a; color: white; }
        
        .dots-btn { opacity: 0; padding: 5px; font-size: 18px; line-height: 1; transition: 0.2s; }
        .history-item:hover .dots-btn { opacity: 1; }
        
        .dropdown-menu {
            display: none; position: absolute; right: 0; top: 35px; background: #222;
            border: 1px solid #444; border-radius: 8px; z-index: 2000; width: 120px;
        }

        .input-container { padding: 20px; border-top: 1px solid #222; display: flex; gap: 10px; background: #000; padding-bottom: 30px; }
        input { flex-grow: 1; background: #111; border: 1px solid #333; padding: 14px; border-radius: 12px; color: white; outline: none; font-size: 16px; }
        .btn-send { background: #0056b3; border: none; width: 50px; height: 50px; border-radius: 50%; color: white; cursor: pointer; font-size: 20px; }
        
        .download-btn { display: inline-block; margin-top: 10px; padding: 8px 15px; background: #0056b3; color: #fff; border: none; border-radius: 5px; font-size: 13px; cursor: pointer; text-decoration: none; }
    </style>
</head>
<body onclick="closeAllMenus(event)">
    <div id="app-container">
        <div class="menu-toggle" onclick="document.getElementById('sidebar').classList.toggle('active')">☰</div>
        <div id="sidebar">
            <div class="btn-new" onclick="startNewChat()">＋ New Chat</div>
            <div id="historyList" style="overflow-y: auto;"></div>
        </div>
        
        <div id="main">
            <div class="header"><h3>LOOM AI</h3></div>
            <div id="chat-window"></div>
            <div class="input-container">
                <input type="text" id="userInput" placeholder="Ask anything or 'image: cute cat'..." onkeypress="if(event.key==='Enter') send()">
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
            const sortedIds = Object.keys(chats).sort((a, b) => b - a);
            sortedIds.forEach(id => {
                const item = document.createElement('div');
                item.className = `history-item ${id === currentChatId ? 'active' : ''}`;
                item.innerHTML = `<div onclick="loadChat('${id}')" style="flex-grow:1; overflow:hidden;">${chats[id].title}</div>`;
                list.appendChild(item);
            });
        }

        function startNewChat() {
            currentChatId = Date.now().toString();
            document.getElementById('chat-window').innerHTML = '';
            renderHistory();
        }

        function loadChat(id) {
            currentChatId = id;
            const win = document.getElementById('chat-window');
            win.innerHTML = '';
            chats[id].messages.forEach(m => appendMessage(m.role, m.text, m.isImage, false));
            renderHistory();
        }

        async function downloadImage(url) {
            try {
                const response = await fetch(url);
                const blob = await response.blob();
                const blobUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = blobUrl;
                a.download = `Loom_AI_${Date.now()}.png`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            } catch (e) {
                window.open(url, '_blank');
            }
        }

        function appendMessage(role, text, isImage = false, save = true) {
            const win = document.getElementById('chat-window');
            const div = document.createElement('div');
            div.className = role === 'user' ? 'user-msg' : 'bot-msg';
            
            if (isImage) {
                div.innerHTML = `<img src="${text}" alt="Generated Image"><br><button class="download-btn" onclick="downloadImage('${text}')">Download Image</button>`;
            } else {
                let formattedText = text.replace(/\\n/g, '<br>')
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>')
                    .replace(/```(.*?)\\n([\s\S]*?)```/g, '<pre style="background:#000; padding:10px; border-radius:5px; color:#0f0; border:1px solid #333; overflow-x:auto; margin:10px 0;">$2</pre>');
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
            let text = input.value.trim();
            if (!text) return;
            if (!currentChatId) startNewChat();
            appendMessage('user', text);
            input.value = '';
            
            const loading = document.createElement('div');
            loading.className = 'bot-msg'; loading.innerText = 'Loom AI is thinking...';
            document.getElementById('chat-window').appendChild(loading);

            try {
                const res = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text }) });
                const data = await res.json();
                loading.remove();

                if (data.reply && data.reply.toLowerCase().includes("image:")) {
                   const promptMatch = data.reply.split(/image:/i)[1].trim();
                   const imgUrl = `https://pollinations.ai/p/${encodeURIComponent(promptMatch)}?width=1024&height=1024&seed=${Math.floor(Math.random() * 1000000)}&nologo=true`;
                   appendMessage('bot', imgUrl, true);
                } else if (data.image) {
                    appendMessage('bot', data.image, true);
                } else {
                    appendMessage('bot', data.reply);
                }
            } catch (e) { loading.innerText = "Error: Connection lost."; }
        }

        renderHistory();
        if (!currentChatId) startNewChat();
        function closeAllMenus() {}
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get("message", "")
    # সরাসরি image: লিখে রিকোয়েস্ট করলে
    if msg.lower().startswith("image:"):
        return jsonify({"image": generate_image_url(msg)})
    
    reply = get_ai_response(msg)
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)
