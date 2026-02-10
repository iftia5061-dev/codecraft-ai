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
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image_url(prompt):
    # ইমেজ তৈরির প্রম্পট থেকে 'image:' শব্দটা বাদ দিয়ে ক্লিন করা
    clean_prompt = prompt.replace("image:", "").strip()
    seed = random.randint(0, 999999)
    # পোলিনেশন এআই সরাসরি ইমেজ রিটার্ন করে
    return f"https://pollinations.ai/p/{clean_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"

# ২. সম্পূর্ণ রেসপন্সিভ ইউআই (Ads + Image Fix + Scrollbar)
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
            background-color: #000; color: #fff; font-family: 'Inter', sans-serif; 
            height: 100%; width: 100%; overflow: hidden; 
            overscroll-behavior: none !important;
            position: fixed;
        }
        
        #app-container { display: flex; height: 100vh; width: 100vw; position: relative; }

        #sidebar { 
            width: 280px; background-color: #0a0a0a; border-right: 1px solid #222; 
            display: flex; flex-direction: column; padding: 15px; 
            transition: 0.3s ease-in-out; z-index: 1000;
        }
        
        @media (max-width: 768px) {
            #sidebar { position: absolute; left: -280px; height: 100%; }
            #sidebar.active { left: 0; box-shadow: 5px 0 15px rgba(0,0,0,0.5); }
        }

        .menu-toggle {
            position: fixed; top: 15px; left: 15px;
            background: #1a1a1a; color: white; border: 1px solid #333;
            padding: 8px 12px; border-radius: 8px; z-index: 1001; cursor: pointer;
        }

        #main { flex-grow: 1; display: flex; flex-direction: column; width: 100%; overflow: hidden; }
        
        /* হেডার ও অ্যাড স্লট */
        .header { padding: 15px; text-align: center; border-bottom: 1px solid #222; background: #000; padding-top: 55px; }
        .ad-container { 
            width: 100%; min-height: 50px; background: #0a0a0a; 
            margin: 10px 0; display: flex; justify-content: center; align-items: center;
        }

        /* কাস্টম স্ক্রলবার (আপনার লাঠি) */
        #chat-window { 
            flex-grow: 1; padding: 20px; 
            overflow-y: scroll; 
            display: flex; flex-direction: column; gap: 15px; 
        }

        #chat-window::-webkit-scrollbar { width: 10px; }
        #chat-window::-webkit-scrollbar-track { background: #000; }
        #chat-window::-webkit-scrollbar-thumb { 
            background: #0056b3; border-radius: 10px; border: 2px solid #000;
        }

        .user-msg { background: #0056b3; color: white; padding: 12px 16px; border-radius: 18px 18px 0 18px; align-self: flex-end; max-width: 85%; word-wrap: break-word; }
        .bot-msg { background: #1a1a1a; color: #eee; padding: 12px 16px; border-radius: 18px 18px 18px 0; align-self: flex-start; max-width: 85%; border: 1px solid #333; }
        .bot-msg img { width: 100%; border-radius: 10px; margin-top: 10px; border: 1px solid #444; }

        .input-container { padding: 20px; border-top: 1px solid #222; display: flex; gap: 10px; background: #000; padding-bottom: 30px; }
        input { flex-grow: 1; background: #111; border: 1px solid #333; padding: 14px; border-radius: 12px; color: white; outline: none; font-size: 16px; }
        .btn-send { background: #0056b3; border: none; width: 50px; height: 50px; border-radius: 50%; color: white; cursor: pointer; font-size: 20px; }
        
        .btn-new { background: #0056b3; color: white; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; }
        .history-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-radius: 6px; margin-bottom: 8px; background: #161616; cursor: pointer; font-size: 14px; }
    </style>
</head>
<body>
    <div id="app-container">
        <div class="menu-toggle" onclick="document.getElementById('sidebar').classList.toggle('active')">☰</div>
        
        <div id="sidebar">
            <button class="btn-new" onclick="startNewChat()">＋ New Chat</button>
            <div id="historyList"></div>
        </div>
        
        <div id="main">
            <div class="header">
                <h3>LOOM AI</h3>
                <div class="ad-container">
                    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-app-pub-6478801956648313" crossorigin="anonymous"></script>
                    <ins class="adsbygoogle" style="display:inline-block;width:320px;height:50px" data-ad-client="ca-app-pub-6478801956648313" data-ad-slot="5044703146"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
                </div>
            </div>

            <div id="chat-window"></div>

            <div class="input-container">
                <input type="text" id="userInput" placeholder="Type message or 'image: cat'..." onkeypress="if(event.key==='Enter') send()">
                <button class="btn-send" onclick="send()">➔</button>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = Date.now();
        let chats = JSON.parse(localStorage.getItem('loom_chats')) || {};

        function loadChat(id) {
            currentChatId = id;
            const win = document.getElementById('chat-window');
            win.innerHTML = '';
            chats[id].messages.forEach(m => appendMessage(m.role, m.text));
            document.getElementById('sidebar').classList.remove('active');
            setTimeout(() => { win.scrollTop = win.scrollHeight; }, 100);
        }

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            Object.keys(chats).sort((a, b) => b - a).forEach(id => {
                const item = document.createElement('div');
                item.className = 'history-item';
                item.innerHTML = `
                    <div onclick="loadChat('${id}')" style="flex-grow:1;">📄 ${chats[id].title}</div>
                    <div style="display:flex; gap:10px;">
                        <span onclick="deleteChat('${id}')">🗑️</span>
                    </div>
                `;
                list.appendChild(item);
            });
        }

        function startNewChat() {
            currentChatId = Date.now();
            document.getElementById('chat-window').innerHTML = '';
            document.getElementById('sidebar').classList.remove('active');
        }

        function appendMessage(role, text) {
            const win = document.getElementById('chat-window');
            const div = document.createElement('div');
            div.className = role === 'user' ? 'user-msg' : 'bot-msg';
            div.innerHTML = text;
            win.appendChild(div);
            win.scrollTop = win.scrollHeight;
        }

        async function send() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if(!text) return;
            
            if(!chats[currentChatId]) chats[currentChatId] = { title: text.substring(0, 15), messages: [] };
            
            appendMessage('user', text);
            chats[currentChatId].messages.push({role:'user', text: text});
            input.value = '';

            // 'Processing' মেসেজ দেখানো
            const tempMsg = document.createElement('div');
            tempMsg.className = 'bot-msg';
            tempMsg.innerText = 'Thinking...';
            document.getElementById('chat-window').appendChild(tempMsg);

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                tempMsg.remove();
                
                let reply = data.image ? `<img src="${data.image}" alt="AI Image">` : data.reply;
                appendMessage('bot', reply);
                chats[currentChatId].messages.push({role:'bot', text: reply});
                localStorage.setItem('loom_chats', JSON.stringify(chats));
                renderHistory();
            } catch (e) {
                tempMsg.innerText = "Connection Error!";
            }
        }

        function deleteChat(id) {
            delete chats[id];
            localStorage.setItem('loom_chats', JSON.stringify(chats));
            renderHistory();
            startNewChat();
        }

        renderHistory();
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get("message", "")
    # ইমেজ রিকোয়েস্ট চেক করা
    if msg.lower().startswith("image:"):
        img_url = generate_image_url(msg)
        return jsonify({"image": img_url})
    
    # সাধারণ টেক্সট রিপ্লাই
    reply = get_ai_response(msg)
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)
