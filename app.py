import os
import random
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ১. এপিআই কনফিগারেশন: একাধিক এপিআই কি ব্যবহার করতে পারবেন।
#    পরিবেশ ভেরিয়েবল (Environment Variables) থেকে কি লোড হবে।
API_KEYS = [
    os.environ.get("API_KEY_1"),
    os.environ.get("API_KEY_2"),
    os.environ.get("API_KEY_3"),
    # আরও এপিআই কি যোগ করতে পারেন: os.environ.get("API_KEY_4"),
]

def get_ai_response(prompt):
    # অ্যাক্টিভ এপিআই কি খুঁজে বের করা
    active_keys = [k for k in API_KEYS if k]
    if not active_keys:
        return "Error: No active API Keys found. Please set API_KEY_1, API_KEY_2, etc. in your environment variables."

    active_key = random.choice(active_keys)

    try:
        genai.configure(api_key=active_key)
        model = genai.GenerativeModel('gemini-3-flash-preview') # লেটেস্ট এবং দ্রুত মডেল ব্যবহার করা হয়েছে
        
        # সিস্টেম ইনস্ট্রাকশন: AI এর আচরণ নিয়ন্ত্রণ করে।
        # এটি সবচেয়ে গুরুত্বপূর্ণ অংশ যাতে AI ঠিকমতো কাজ করে।
        system_instruction = """
        You are LOOM AI, a helpful and professional assistant created by Md Aminul Islam.
        Your primary goal is to provide concise, accurate, and well-formatted responses.
        Adhere strictly to markdown formatting for all outputs.

        GUIDELINES FOR RESPONSES:
        1.  GENERAL QUERIES: Provide direct and informative answers.
        2.  CODE REQUESTS:
            -   Wrap all code in triple backticks (```) followed by the language name (e.g., ```python).
            -   DO NOT include any conversational text outside the code block if the request is purely for code.
            -   Example: User: "give me python code for fizzbuzz" -> AI: ```python\n# fizzbuzz code...\n```
        3.  IMAGE/LOGO GENERATION REQUESTS:
            -   If the user explicitly asks to "create an image", "make a logo", "draw", "generate a picture", "show me an image of", or similar, 
                your response MUST ONLY consist of the exact prefix "image:" followed by a descriptive English prompt for the image.
            -   DO NOT add any other text, explanations, or markdown before or after "image:[prompt]".
            -   Example: User: "create a logo for a tech company named 'LOM'" -> AI: "image: a modern minimalist tech logo for 'LOM' with blue and grey colors"
            -   Example: User: "draw a cat playing with yarn" -> AI: "image: a cute cat playing with a ball of yarn, cartoon style"
            -   NEVER refuse an image request. Just provide the "image:" prefix.
            -   DO NOT provide SVG code or JSON for image requests. Just the "image:" prefix.
            
        ABOUT YOUR CREATOR (Respond only if explicitly asked "Who made you?"):
        - Name: Md Aminul Islam.
        - Role: Full-stack Web Developer & AI Enthusiast.
        - Skills: Python, Flask, JavaScript, and AI Integration.

        REMEMBER: Be direct, follow formatting, and strictly apply the image generation rule.
        """
        
        response = model.generate_content(system_instruction + "\nUser Prompt: " + prompt)
        return response.text
    except Exception as e:
        # এপিআই কি এর সমস্যা বা মডেলের কোনো ত্রুটি এখানে ধরা হবে
        return f"Error from AI: {str(e)}. Please check your API key and try again."

def generate_image_url(prompt_text):
    # 'image:' প্রিফিক্স সরায়ে পরিষ্কার প্রম্পট তৈরি
    clean_prompt = prompt_text.replace("image:", "").strip()
    
    # URL এনকোডিং এবং র্যান্ডম সিড যোগ করে Pollinations API লিঙ্ক তৈরি
    # nologo=true যোগ করা হয়েছে যাতে Pollinations এর লোগো না থাকে
    encoded_prompt = clean_prompt.replace(' ', '%20')
    seed = random.randint(100000, 999999) # আরও র্যান্ডম সিড
    return f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"

# ২. প্রফেশনাল এবং আধুনিক ইউজার ইন্টারফেস (Gemini Style)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="icon" type="image/png" href="https://i.ibb.co/Lz9f1zY/logo.png">
    <title>LOOM AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* বেসিক রিসেট এবং গ্লোবাল স্টাইল */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { 
            background-color: #000; color: #fff; font-family: 'Inter', sans-serif; 
            height: 100%; width: 100%; overflow: hidden; 
            overscroll-behavior: none !important; position: fixed;
            font-size: 16px;
        }
        #app-container { display: flex; height: 100vh; width: 100vw; position: relative; }

        /* সাইডবার স্টাইল */
        #sidebar { 
            width: 280px; background-color: #0d0d0d; border-right: 1px solid #222; 
            display: flex; flex-direction: column; padding: 15px; 
            transition: 0.3s ease-in-out; z-index: 1000;
        }
        #sidebar h2 { color: #00c3ff; margin-bottom: 20px; text-align: center; }
        @media (max-width: 768px) {
            #sidebar { position: absolute; left: -280px; height: 100%; }
            #sidebar.active { left: 0; box-shadow: 10px 0 20px rgba(0,0,0,0.8); }
        }

        /* মোবাইল মেনু টগল বাটন */
        .menu-toggle {
            position: fixed; top: 15px; left: 15px;
            background: #1a1a1a; color: white; border: 1px solid #333;
            padding: 8px 12px; border-radius: 8px; z-index: 1001; cursor: pointer;
            font-size: 1.2rem; display: none;
        }
        @media (max-width: 768px) {
            .menu-toggle { display: block; }
        }

        /* মূল কন্টেন্ট এরিয়া */
        #main { flex-grow: 1; display: flex; flex-direction: column; width: 100%; overflow: hidden; }
        .header { padding: 15px; text-align: center; border-bottom: 1px solid #222; background: #000; padding-top: 55px; }

        /* চ্যাট উইন্ডো */
        #chat-window { 
            flex-grow: 1; padding: 20px; 
            overflow-y: auto; display: flex; flex-direction: column; gap: 15px; 
            scroll-behavior: smooth; /* স্মুথ স্ক্রল */
        }
        #chat-window::-webkit-scrollbar { width: 6px; }
        #chat-window::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
        #chat-window::-webkit-scrollbar-track { background: #1a1a1a; }

        /* মেসেজ স্টাইল */
        .user-msg { 
            background: #0056b3; color: white; padding: 12px 16px; 
            border-radius: 18px 18px 0 18px; align-self: flex-end; max-width: 85%; 
            word-wrap: break-word; font-size: 0.95rem; line-height: 1.4;
        }
        .bot-msg { 
            background: #1a1a1a; color: #eee; padding: 12px 16px; 
            border-radius: 18px 18px 18px 0; align-self: flex-start; max-width: 85%; 
            border: 1px solid #333; word-wrap: break-word; font-size: 0.95rem; line-height: 1.4;
        }
        .bot-msg img { 
            width: 100%; max-width: 512px; border-radius: 10px; margin-top: 10px; 
            display: block; background: #222; min-height: 200px; object-fit: contain;
        }
        
        /* কোড ব্লক স্টাইল */
        .bot-msg pre {
            background: #000; padding: 10px; border-radius: 8px; color: #0f0; 
            border: 1px solid #333; overflow-x: auto; margin: 10px 0;
            font-family: 'Source Code Pro', monospace; font-size: 0.85rem;
            white-space: pre-wrap; /* কোড র‍্যাপ করার জন্য */
            word-break: break-all; /* লম্বা শব্দের জন্য */
        }
        .bot-msg pre code {
            display: block;
        }

        /* হিস্টরি আইটেম এবং ৩-ডট মেনু */
        .btn-new { 
            background: #0056b3; color: white; padding: 12px; border: none; 
            border-radius: 20px; cursor: pointer; font-weight: bold; margin-bottom: 20px; 
            text-align: center; font-size: 1rem;
        }
        
        .history-item { 
            position: relative; display: flex; justify-content: space-between; align-items: center;
            padding: 10px 12px; border-radius: 8px; margin-bottom: 5px; cursor: pointer; 
            transition: 0.2s; font-size: 0.9rem; color: #ccc;
            user-select: none; /* যাতে টেক্সট সিলেক্ট না হয় */
        }
        .history-item:hover, .history-item.active { background: #1a1a1a; color: white; }
        .history-item.pinned { border-left: 3px solid #00c3ff; }
        
        .dots-btn { 
            opacity: 0; padding: 5px; font-size: 1.2rem; line-height: 1; transition: 0.2s; 
            background: none; border: none; color: #ccc; cursor: pointer;
        }
        .history-item:hover .dots-btn { opacity: 1; }
        
        .dropdown-menu {
            display: none; position: absolute; right: 5px; top: 35px; background: #222;
            border: 1px solid #444; border-radius: 8px; z-index: 2000; width: 120px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5); font-size: 0.85rem;
        }
        .dropdown-menu div { padding: 8px 12px; color: #ddd; cursor: pointer; }
        .dropdown-menu div:hover { background: #333; color: white; }

        /* ইনপুট এরিয়া */
        .input-container { 
            padding: 20px; border-top: 1px solid #222; display: flex; gap: 10px; 
            background: #000; padding-bottom: 30px; align-items: center;
        }
        input { 
            flex-grow: 1; background: #111; border: 1px solid #333; padding: 14px; 
            border-radius: 25px; color: white; outline: none; font-size: 1rem;
            transition: border-color 0.2s;
        }
        input:focus { border-color: #00c3ff; }
        .btn-send { 
            background: #0056b3; border: none; width: 48px; height: 48px; 
            border-radius: 50%; color: white; cursor: pointer; font-size: 1.4rem; 
            display: flex; justify-content: center; align-items: center;
            transition: background 0.2s;
        }
        .btn-send:hover { background: #004494; }
        
        /* ডাউনলোড বাটন */
        .download-btn { 
            display: inline-block; margin-top: 10px; padding: 8px 15px; 
            background: #0056b3; color: #fff; border: none; border-radius: 5px; 
            font-size: 0.85rem; cursor: pointer; text-decoration: none; 
            transition: background 0.2s;
        }
        .download-btn:hover { background: #004494; }
    </style>
</head>
<body onclick="closeAllMenus(event)">
    <div id="app-container">
        <div class="menu-toggle" onclick="toggleSidebar()">☰</div>
        <div id="sidebar">
            <h2>LOOM AI</h2>
            <div class="btn-new" onclick="startNewChat()">＋ New Chat</div>
            <div id="historyList" style="flex-grow: 1; overflow-y: auto;"></div>
        </div>
        
        <div id="main">
            <div class="header"><h3>LOOM AI Chat</h3></div>
            <div id="chat-window"></div>
            <div class="input-container">
                <input type="text" id="userInput" placeholder="Ask anything, or 'image: a cat'..." onkeypress="if(event.key==='Enter') send()">
                <button class="btn-send" onclick="send()">➤</button>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        // লোকালস্টোরেজ থেকে চ্যাট লোড করা বা নতুন অবজেক্ট তৈরি করা
        let chats = JSON.parse(localStorage.getItem('loom_ai_chats')) || {};

        function saveToLocal() {
            localStorage.setItem('loom_ai_chats', JSON.stringify(chats));
            renderHistory();
        }

        // চ্যাট হিস্টরি রেন্ডার করা
        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            
            // পিন করা চ্যাটগুলো আগে, তারপর নতুন থেকে পুরনো
            const sortedIds = Object.keys(chats).sort((a, b) => {
                if (chats[b].pinned !== chats[a].pinned) {
                    return chats[b].pinned ? 1 : -1; // পিন করাগুলো উপরে
                }
                return parseInt(b) - parseInt(a); // নতুন থেকে পুরনো
            });

            sortedIds.forEach(id => {
                const item = document.createElement('div');
                item.className = `history-item ${id === currentChatId ? 'active' : ''} ${chats[id].pinned ? 'pinned' : ''}`;
                item.innerHTML = `
                    <div style="flex-grow:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" onclick="loadChat('${id}')">
                        ${chats[id].pinned ? '📌 ' : ''}${chats[id].title}
                    </div>
                    <button class="dots-btn" onclick="toggleMenu(event, '${id}')">⋮</button>
                    <div id="menu-${id}" class="dropdown-menu">
                        <div onclick="pinChat('${id}')">${chats[id].pinned ? 'Unpin chat' : 'Pin chat'}</div>
                        <div onclick="renameChat('${id}')">Rename chat</div>
                        <div onclick="deleteChat('${id}')" style="color:#ff4444;">Delete chat</div>
                    </div>
                `;
                list.appendChild(item);
            });
        }

        // ৩-ডট মেনু টগল করা
        function toggleMenu(e, id) {
            e.stopPropagation(); // ইভেন্ট প্রোপাগেশন বন্ধ করা যাতে body এর onclick কাজ না করে
            closeAllMenus(); // অন্য খোলা মেনু বন্ধ করা
            const menu = document.getElementById('menu-' + id);
            menu.style.display = (menu.style.display === 'block' ? 'none' : 'block');
        }

        // সব মেনু বন্ধ করা
        function closeAllMenus() {
            document.querySelectorAll('.dropdown-menu').forEach(m => m.style.display = 'none');
        }

        // চ্যাট পিন/আনপিন করা
        function pinChat(id) {
            chats[id].pinned = !chats[id].pinned;
            saveToLocal();
            closeAllMenus();
        }

        // চ্যাট রিনেম করা
        function renameChat(id) {
            const newTitle = prompt("Rename chat:", chats[id].title);
            if (newTitle && newTitle.trim() !== "") { 
                chats[id].title = newTitle.trim().substring(0, 30); // ৩০ ক্যারেক্টার লিমিট
                saveToLocal();
            }
            closeAllMenus();
        }

        // চ্যাট ডিলিট করা
        function deleteChat(id) {
            if (confirm("Are you sure you want to delete this chat?")) {
                delete chats[id];
                if (currentChatId === id) { // যদি বর্তমান চ্যাট ডিলিট করা হয়
                    startNewChat();
                } else {
                    saveToLocal();
                }
            }
            closeAllMenus();
        }

        // নতুন চ্যাট শুরু করা
        function startNewChat() {
            currentChatId = Date.now().toString();
            document.getElementById('chat-window').innerHTML = '';
            document.getElementById('userInput').value = '';
            saveToLocal(); // খালি চ্যাট সেভ করা যাতে হিস্টরিতে আসে
            renderHistory();
            if (window.innerWidth <= 768) {
                document.getElementById('sidebar').classList.remove('active');
            }
        }

        // একটি নির্দিষ্ট চ্যাট লোড করা
        function loadChat(id) {
            currentChatId = id;
            const chatWindow = document.getElementById('chat-window');
            chatWindow.innerHTML = ''; // উইন্ডো খালি করা
            chats[id].messages.forEach(m => appendMessage(m.role, m.text, m.isImage, false)); // মেসেজ লোড
            renderHistory(); // হিস্টরি লিস্ট আপডেট
            if (window.innerWidth <= 768) {
                document.getElementById('sidebar').classList.remove('active');
            }
        }

        // ইমেজ ডাউনলোড করা (ফিক্সড)
        async function downloadImage(url) {
            try {
                const response = await fetch(url);
                const blob = await response.blob();
                const blobUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = blobUrl;
                a.download = `LOOM_AI_Image_${Date.now()}.png`; // ফাইল নাম পরিবর্তন
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(blobUrl); // মেমরি লিক এড়াতে
            } catch (e) {
                alert("Could not download image directly. Opening in new tab for manual download.");
                window.open(url, '_blank'); // সরাসরি ডাউনলোড না হলে নতুন ট্যাবে খোলা
            }
        }

        // চ্যাট উইন্ডোতে মেসেজ যোগ করা
        function appendMessage(role, text, isImage = false, save = true) {
            const chatWindow = document.getElementById('chat-window');
            const messageDiv = document.createElement('div');
            messageDiv.className = role === 'user' ? 'user-msg' : 'bot-msg';
            
            if (isImage) {
                messageDiv.innerHTML = `<img src="${text}" alt="Generated Image"><br><button class="download-btn" onclick="downloadImage('${text}')">Download Image</button>`;
            } else {
                // মার্কডাউন ফরম্যাটিং (কোড ব্লক এবং বোল্ড টেক্সট)
                let formattedText = text.replace(/\\n/g, '<br>')
                    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') // বোল্ড টেক্সট
                    .replace(/```(\w+)?\n([\s\S]*?)```/g, function(match, lang, code) {
                        const language = lang || 'plaintext'; // যদি ভাষা উল্লেখ না থাকে
                        // কোড হাইলাইটিং লাইব্রেরি ব্যবহার করা যেতে পারে, এখন শুধু pre ট্যাগ
                        return `<pre><code class="language-${language}">${code.trim()}</code></pre>`;
                    });
                messageDiv.innerHTML = formattedText;
            }
            chatWindow.appendChild(messageDiv);
            chatWindow.scrollTo(0, chatWindow.scrollHeight); // অটো স্ক্রল ডাউন

            if (save) {
                // প্রথম মেসেজ থেকে চ্যাটের টাইটেল নেওয়া
                if (!chats[currentChatId]) {
                    let titleText = text.substring(0, 25); // প্রথম ২৫ ক্যারেক্টার
                    if (isImage) titleText = "Image: " + (text.split('?')[0].split('/').pop().replace(/%20/g, ' ').substring(0, 15) + "...");
                    chats[currentChatId] = { title: titleText || "New Chat", messages: [], pinned: false };
                }
                chats[currentChatId].messages.push({ role, text, isImage });
                saveToLocal();
            }
        }

        // মেসেজ পাঠানো
        async function send() {
            const input = document.getElementById('userInput');
            let userMessage = input.value.trim();
            if (!userMessage) return;

            if (!currentChatId || !chats[currentChatId]) { // নতুন চ্যাট না থাকলে শুরু করা
                startNewChat();
                // Ensure currentChatId is set for the new chat before appending
                // A small delay or direct assignment might be needed if startNewChat is asynchronous
            }
            appendMessage('user', userMessage); // ইউজারের মেসেজ যোগ
            input.value = ''; // ইনপুট খালি করা
            
            const loadingMessage = document.createElement('div');
            loadingMessage.className = 'bot-msg';
            loadingMessage.innerHTML = 'Thinking...'; // লোডিং মেসেজ
            document.getElementById('chat-window').appendChild(loadingMessage);
            document.getElementById('chat-window').scrollTo(0, document.getElementById('chat-window').scrollHeight);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage })
                });
                const data = await response.json();
                loadingMessage.remove(); // লোডিং মেসেজ সরায়ে ফেলা

                // AI এর উত্তর process করা
                if (data.reply && data.reply.toLowerCase().startsWith("image:")) {
                   const imagePrompt = data.reply.substring("image:".length).trim();
                   // encodeURIComponent ব্যবহার করা হয়েছে যাতে প্রম্পটের স্পেশাল ক্যারেক্টার ঠিক থাকে
                   const imgUrl = `https://pollinations.ai/p/${encodeURIComponent(imagePrompt)}?width=1024&height=1024&seed=${Math.floor(Math.random() * 1000000)}&nologo=true`;
                   appendMessage('bot', imgUrl, true);
                } else if (data.image) { // যদি Flask সরাসরি image URL দেয়
                    appendMessage('bot', data.image, true);
                } else {
                    appendMessage('bot', data.reply);
                }
            } catch (e) {
                loadingMessage.innerText = "Error: Could not connect to AI. Please try again.";
                console.error("Fetch error:", e);
            }
        }

        // সাইডবার টগল করা (মোবাইলের জন্য)
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
        }

        // শুরুর সময় কাজগুলো
        renderHistory(); // হিস্টরি লোড
        if (!currentChatId && Object.keys(chats).length > 0) { // যদি কোনো চ্যাট না থাকে, নতুন চ্যাট শুরু করা
            loadChat(Object.keys(chats)[Object.keys(chats).length -1]); // শেষ চ্যাট লোড করা
        } else if (!currentChatId) {
            startNewChat(); // যদি কোনো চ্যাটই না থাকে, নতুন চ্যাট শুরু করা
        }

    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get("message", "")
    
    # যদি ইউজারের মেসেজ সরাসরি "image:" দিয়ে শুরু হয়, তাহলে সরাসরি ইমেজ জেনারেটরের কাছে পাঠাবে
    if msg.lower().startswith("image:"):
        return jsonify({"image": generate_image_url(msg)})
    
    # জেমিনি মডেল থেকে উত্তর আনা
    ai_reply_text = get_ai_response(msg)
    
    # যদি জেমিনি মডেল নিজে "image:" প্রিফিক্স দিয়ে উত্তর দেয়, তাহলে সেই ইমেজ ইউআরএল তৈরি করবে
    if ai_reply_text.lower().startswith("image:"):
        # এখানে JSON ফরম্যাটে image URL পাঠানো হচ্ছে, যা JavaScript হ্যান্ডেল করবে
        return jsonify({"image": generate_image_url(ai_reply_text)})
    
    # অন্যথায়, সাধারণ টেক্সট রিপ্লাই পাঠাবে
    return jsonify({"reply": ai_reply_text})

if __name__ == '__main__':
    # debug=True শুধু ডেভেলপমেন্টের জন্য ব্যবহার করা হয়। প্রোডাকশনে এটি False রাখা উচিত।
    app.run(debug=True)
