import os
import random
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ১. এপিআই কনফিগারেশন (Vercel Environment Variables)
API_KEYS = [
    os.environ.get("API_KEY_1", ""),
    os.environ.get("API_KEY_2", ""),
    os.environ.get("API_KEY_3", "")
]

def get_ai_response(prompt):
    active_key = random.choice([k for k in API_KEYS if k])
    if not active_key: return "API Key missing in Vercel settings!"
    try:
        genai.configure(api_key=active_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image_url(prompt):
    seed = random.randint(0, 999999)
    return f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"

# ২. প্রফেশনাল ইউজার ইন্টারফেস (নতুন কালার এবং ফিচারসহ)
# ২. প্রফেশনাল ইউজার ইন্টারফেস (ফোন রেসপন্সিভ এবং রিফ্রেশ ফিক্সসহ)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CodeCraft AI</title>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <style>
        /* ১. রিফ্রেশ বন্ধ এবং ফুল স্ক্রিন ফিক্স */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { 
        background-color: #000; color: #fff; 
        height: 100%; width: 100%; overflow: hidden; 
        overscroll-behavior: none !important; /* রিফ্রেশ পুরোপুরি বন্ধ করবে */
        position: fixed; /* স্ক্রিন নড়াচড়া বন্ধ করবে */
        }
        
        #app-container { display: flex; height: 100vh; width: 100vw; position: relative; }

        /* ২. সাইডবার - ফোনে স্লাইড হয়ে আসবে */
        #sidebar { 
            width: 280px; background-color: #0a0a0a; border-right: 1px solid #222; 
            display: flex; flex-direction: column; padding: 15px; 
            transition: 0.3s ease-in-out; z-index: 1000;
        }
        
        @media (max-width: 768px) {
            #sidebar { position: absolute; left: -280px; height: 100%; }
            #sidebar.active { left: 0; box-shadow: 5px 0 15px rgba(0,0,0,0.5); }
            .menu-toggle { display: block !important; }
        }

        /* ৩. মেনু বাটন (☰) */
        .menu-toggle {
            display: none; position: fixed; top: 15px; left: 15px;
            background: #1a1a1a; color: white; border: 1px solid #333;
            padding: 8px 12px; border-radius: 8px; z-index: 1001; cursor: pointer;
        }

        /* ৪. মেইন চ্যাট এরিয়া */
        #main { flex-grow: 1; display: flex; flex-direction: column; width: 100%; }
        .header { padding: 15px; text-align: center; border-bottom: 1px solid #222; background: #000; padding-top: 55px; }
        .ad-space { width: 100%; height: 60px; background: #111; border: 1px dashed #333; margin: 5px auto; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #444; }
        
        #chat-window { 
        flex-grow: 1; padding: 20px; 
        overflow-y: auto !important; /* শুধুমাত্র চ্যাট উইন্ডো স্ক্রল হবে */
        display: flex; flex-direction: column; gap: 15px; 
        -webkit-overflow-scrolling: touch; 
        }

        /* চ্যাট বাবল */
        .user-msg { background: #0056b3; color: white; padding: 12px 16px; border-radius: 18px 18px 0 18px; align-self: flex-end; max-width: 80%; }
        .bot-msg { background: #1a1a1a; color: #eee; padding: 12px 16px; border-radius: 18px 18px 18px 0; align-self: flex-start; max-width: 80%; border: 1px solid #333; }

        /* ইনপুট বক্স */
        .input-container { padding: 20px; border-top: 1px solid #222; display: flex; gap: 10px; background: #000; padding-bottom: 30px; }
        input { flex-grow: 1; background: #111; border: 1px solid #333; padding: 14px; border-radius: 12px; color: white; outline: none; font-size: 16px; }
        .btn-send { background: #0056b3; border: none; width: 50px; height: 50px; border-radius: 50%; color: white; cursor: pointer; font-size: 20px; }
        
        .btn-new { background: #0056b3; color: white; padding: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; }
        .history-list { flex-grow: 1; overflow-y: auto; }
        .history-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-radius: 6px; margin-bottom: 8px; background: #161616; cursor: pointer; font-size: 13px; }
        .action-btns button { background: none; border: none; color: #666; cursor: pointer; margin-left: 5px; }
    </style>
</head>
<body>
    <div id="app-container">
        <button class="menu-toggle" onclick="document.getElementById('sidebar').classList.toggle('active')">☰</button>
        
        <div id="sidebar">
            <button class="btn-new" onclick="startNewChat()">＋ New Chat</button>
            <div class="history-list" id="historyList"></div>
        </div>
        
        <div id="main">
            <div class="header">
                <h3>LOOM AI</h3>
                <div class="ad-space">
                    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-app-pub-6478801956648313" crossorigin="anonymous"></script>
                    <ins class="adsbygoogle" style="display:inline-block;width:320px;height:50px" data-ad-client="ca-app-pub-6478801956648313" data-ad-slot="5044703146"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
                </div>
            </div>

            <div id="chat-window"></div>

            <div class="input-container">
                <input type="text" id="userInput" placeholder="Type message..." onkeypress="if(event.key==='Enter') send()">
                <button class="btn-send" onclick="send()">➔</button>
            </div>
        </div>
    </div>

    <script>
        // আপনার আগের সব স্ক্রিপ্ট লজিক (chats, renderHistory, send, loadChat, etc.) এখানে হুবহু থাকবে
        let currentChatId = Date.now();
        let chats = JSON.parse(localStorage.getItem('loom_chats')) || {};

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            Object.keys(chats).reverse().forEach(id => {
                const item = document.createElement('div');
                item.className = 'history-item';
                item.innerHTML = `
                    <span onclick="loadChat('${id}')">📄 ${chats[id].title}</span>
                    <div class="action-btns">
                        <button onclick="renameChat('${id}')">Rename</button>
                        <button onclick="deleteChat('${id}')">Delete</button>
                    </div>
                `;
                list.appendChild(item);
            });
        }

        function startNewChat() {
            currentChatId = Date.now();
            document.getElementById('chat-window').innerHTML = '';
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('userInput').focus();
        }

        function loadChat(id) {
            currentChatId = id;
            document.getElementById('chat-window').innerHTML = '';
            document.getElementById('sidebar').classList.remove('active');
            chats[id].messages.forEach(m => appendMessage(m.role, m.text));
        }

       function loadChat(id) {
        currentChatId = id;
        const win = document.getElementById('chat-window');
        win.innerHTML = ''; // আগের চ্যাট পরিষ্কার করা
    
        // সাইডবার বন্ধ করা (মোবাইলের জন্য)
        document.getElementById('sidebar').classList.remove('active');
    
        // মেসেজগুলো আবার দেখানো
        if (chats[id] && chats[id].messages) {
        chats[id].messages.forEach(m => {
            appendMessage(m.role, m.text);
        });
        }
    }

// হিস্ট্রি রেন্ডার করার সময় টাইটেল ক্লিক ঠিক করা
    function renderHistory() {
    const list = document.getElementById('historyList');
    list.innerHTML = '';
    Object.keys(chats).sort((a, b) => b - a).forEach(id => {
        const item = document.createElement('div');
        item.className = 'history-item';
        // পুরো আইটেমে ক্লিক করলে চ্যাট লোড হবে
        item.innerHTML = `
            <div onclick="loadChat('${id}')" style="flex-grow:1; cursor:pointer;">
                📄 ${chats[id].title}
            </div>
            <div class="action-btns">
                <button onclick="event.stopPropagation(); renameChat('${id}')">✏️</button>
                <button onclick="event.stopPropagation(); deleteChat('${id}')">🗑️</button>
            </div>
        `;
        list.appendChild(item);
        });
        }

        function renameChat(id) {
            const newName = prompt("Enter new name:", chats[id].title);
            if(newName) {
                chats[id].title = newName;
                localStorage.setItem('loom_chats', JSON.stringify(chats));
                renderHistory();
            }
        }

        function appendMessage(role, text) {
            const win = document.getElementById('chat-window');
            const div = document.createElement('div');
            div.className = role === 'user' ? 'user-msg' : 'bot-msg';
            div.innerHTML = text;
            win.appendChild(div);
            win.scrollTo(0, win.scrollHeight);
        }

        async function send() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if(!text) return;

            if(!chats[currentChatId]) {
                chats[currentChatId] = { title: text.substring(0, 20), messages: [] };
            }

            appendMessage('user', text);
            chats[currentChatId].messages.push({role: 'user', text: text});
            input.value = '';

            const tempBotMsg = document.createElement('div');
            tempBotMsg.className = 'bot-msg';
            tempBotMsg.innerText = 'Processing...';
            document.getElementById('chat-window').appendChild(tempBotMsg);

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                tempBotMsg.remove();

                let replyHtml = data.image ? `<img src="${data.image}" style="width:100%; border-radius:10px;">` : data.reply;
                appendMessage('bot', replyHtml);
                chats[currentChatId].messages.push({role: 'bot', text: replyHtml});
                localStorage.setItem('loom_chats', JSON.stringify(chats));
                renderHistory();
            } catch (e) {
                tempBotMsg.innerText = "Error: Could not connect to server.";
            }
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
    if msg.lower().startswith("image:"):
        return jsonify({"image": generate_image_url(msg[6:].strip())})
    return jsonify({"reply": get_ai_response(msg)})

if __name__ == '__main__':
    app.run(debug=True)



