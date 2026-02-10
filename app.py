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
        # এখানে 'gemini-1.5-flash' ব্যবহার করা হয়েছে যা দ্রুত রেসপন্স দেয়
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # গুরুত্বপূর্ণ: এআই-কে নির্দেশ দেওয়া যাতে সে JSON না পাঠায়
        system_instruction = "Give direct answers. If the user asks for code, provide it inside markdown blocks. Do not return JSON tools or actions."
        response = model.generate_content(system_instruction + " User Prompt: " + prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image_url(prompt):
    clean_prompt = prompt.replace("image:", "").strip()
    seed = random.randint(0, 999999)
    # পোলিনেশন এআই সরাসরি ইমেজ লিংক দেয়
    return f"https://pollinations.ai/p/{clean_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"

# ২. সম্পূর্ণ রেসপন্সিভ ইন্টারফেস (স্ক্রলবার এবং অ্যাডসহ)
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
            background-color: #000; color: #fff; font-family: 'Segoe UI', sans-serif; 
            height: 100%; width: 100%; overflow: hidden; 
            overscroll-behavior: none !important; position: fixed;
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
        .header { padding: 15px; text-align: center; border-bottom: 1px solid #222; background: #000; padding-top: 55px; }

        /* কাস্টম স্ক্রলবার (আপনার সেই লাঠি) */
        #chat-window { 
            flex-grow: 1; padding: 20px; 
            overflow-y: scroll; display: flex; flex-direction: column; gap: 15px; 
        }
        #chat-window::-webkit-scrollbar { width: 10px; }
        #chat-window::-webkit-scrollbar-track { background: #000; }
        #chat-window::-webkit-scrollbar-thumb { 
            background: #0056b3; border-radius: 10px; border: 2px solid #000;
        }

        .user-msg { background: #0056b3; color: white; padding: 12px 16px; border-radius: 18px 18px 0 18px; align-self: flex-end; max-width: 85%; word-wrap: break-word; }
        .bot-msg { background: #1a1a1a; color: #eee; padding: 12px 16px; border-radius: 18px 18px 18px 0; align-self: flex-start; max-width: 85%; border: 1px solid #333; }
        .bot-msg img { width: 100%; border-radius: 10px; margin-top: 10px; }
        pre { background: #000; padding: 10px; border-radius: 5px; overflow-x: auto; color: #0f0; margin: 10px 0; }

        .input-container { padding: 20px; border-top: 1px solid #222; display: flex; gap: 10px; background: #000; padding-bottom: 30px; }
        input { flex-grow: 1; background: #111; border: 1px solid #333; padding: 14px; border-radius: 12px; color: white; outline: none; font-size: 16px; }
        .btn-send { background: #0056b3; border: none; width: 50px; height: 50px; border-radius: 50%; color: white; cursor: pointer; font-size: 20px; }
    </style>
</head>
<body>
    <div id="app-container">
        <div class="menu-toggle" onclick="document.getElementById('sidebar').classList.toggle('active')">☰</div>
        <div id="sidebar">
            <button style="background: #0056b3; color: white; padding: 12px; border: none; border-radius: 8px; margin-bottom: 20px;" onclick="location.reload()">＋ New Chat</button>
            <div id="historyList" style="font-size: 14px; opacity: 0.6;">History (Local Only)</div>
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
        function appendMessage(role, text) {
            const win = document.getElementById('chat-window');
            const div = document.createElement('div');
            div.className = role === 'user' ? 'user-msg' : 'bot-msg';
            
            // কোড ব্লক ফরম্যাট করা
            if (text.includes('```')) {
                div.innerHTML = text.replace(/```html([\s\S]*?)```/g, '<pre>$1</pre>')
                                    .replace(/```css([\s\S]*?)```/g, '<pre>$1</pre>')
                                    .replace(/```javascript([\s\S]*?)```/g, '<pre>$1</pre>')
                                    .replace(/```python([\s\S]*?)```/g, '<pre>$1</pre>')
                                    .replace(/```([\s\S]*?)```/g, '<pre>$1</pre>');
            } else {
                div.innerHTML = text;
            }
            
            win.appendChild(div);
            win.scrollTo(0, win.scrollHeight);
        }

        async function send() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if(!text) return;

            appendMessage('user', text);
            input.value = '';

            const loading = document.createElement('div');
            loading.className = 'bot-msg';
            loading.innerText = 'Processing...';
            document.getElementById('chat-window').appendChild(loading);

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                loading.remove();

                if (data.image) {
                    appendMessage('bot', `<img src="${data.image}" alt="AI Image">`);
                } else {
                    appendMessage('bot', data.reply);
                }
            } catch (e) {
                loading.innerText = "Error: Connection failed.";
            }
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
