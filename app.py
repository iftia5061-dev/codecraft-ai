import os
import random
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ১. এপিআই কনফিগারেশন
API_KEYS = [
    os.environ.get("API_KEY_1"),
    os.environ.get("API_KEY_2"),
    # আরও কি থাকলে এখানে যোগ করতে পারবেন
]

def get_ai_response(prompt):
    active_keys = [k for k in API_KEYS if k]
    if not active_keys:
        return "Error: No active API Keys found."

    active_key = random.choice(active_keys)

    try:
        genai.configure(api_key=active_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # আপনার আগের সিস্টেম ইনস্ট্রাকশন
        system_instruction = """
        You are LOOM AI, created by Md Aminul Islam.
        IMAGE RULE: If user asks for an image, respond ONLY with "image: [description]".
        CODE RULE: Wrap code in ``` blocks.
        """
        
        response = model.generate_content(system_instruction + "\nUser Prompt: " + prompt)
        return response.text
    except Exception as e:
        return f"Error from AI: {str(e)}"

def generate_image_url(prompt_text):
    clean_prompt = prompt_text.replace("image:", "").strip()
    encoded_prompt = clean_prompt.replace(' ', '%20')
    seed = random.randint(100000, 999999)
    return f"[https://pollinations.ai/p/](https://pollinations.ai/p/){encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"

# ২. আপনার UI এবং স্ক্রিপ্ট (Enter Key Fix সহ)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOOM AI</title>
    <style>
        /* আপনার আগের স্টাইলগুলো এখানে থাকবে */
        body { background-color: #000; color: #fff; font-family: sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        #chat-window { flex-grow: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .user-msg { background: #0056b3; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; align-self: flex-end; max-width: 80%; }
        .bot-msg { background: #1a1a1a; color: #eee; padding: 10px 15px; border-radius: 15px 15px 15px 0; align-self: flex-start; max-width: 80%; border: 1px solid #333; }
        .bot-msg img { width: 100%; border-radius: 10px; margin-top: 10px; }
        .input-container { padding: 20px; border-top: 1px solid #222; display: flex; gap: 10px; }
        input { flex-grow: 1; background: #111; border: 1px solid #333; padding: 12px; border-radius: 20px; color: white; outline: none; }
        .btn-send { background: #0056b3; border: none; padding: 10px 20px; border-radius: 20px; color: white; cursor: pointer; }
        pre { background: #000; padding: 10px; border-radius: 5px; overflow-x: auto; border: 1px solid #333; color: #0f0; }
    </style>
</head>
<body>
    <div id="chat-window"></div>
    <div class="input-container">
        <input type="text" id="userInput" placeholder="Ask anything..." onkeypress="handleKeyPress(event)" autocomplete="off">
        <button class="btn-send" onclick="send()">Send</button>
    </div>

    <script>
        let currentChatId = Date.now().toString();

        // ১. এন্টার বাটন হ্যান্ডেল করার ফাংশন (NEW)
        function handleKeyPress(event) {
            if (event.key === "Enter") {
                event.preventDefault(); 
                send(); 
            }
        }

        // ২. আপনার পাঠানো অরিজিনাল send ফাংশন
        async function send() {
            const input = document.getElementById('userInput');
            let userMessage = input.value.trim();
            
            if (!userMessage) return; 

            appendMessage('user', userMessage); 
            input.value = ''; 
            
            const chatWindow = document.getElementById('chat-window');
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'bot-msg';
            loadingDiv.id = 'temp-loading';
            loadingDiv.innerText = 'LOOM AI is thinking...';
            chatWindow.appendChild(loadingDiv);
            chatWindow.scrollTo(0, chatWindow.scrollHeight);

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage })
                });
                
                const data = await response.json();
                const loadingElement = document.getElementById('temp-loading');
                if (loadingElement) loadingElement.remove(); 

                if (data.image) {
                    appendMessage('bot', data.image, true);
                } else if (data.reply && data.reply.startsWith("image:")) {
                    // যদি AI টেক্সট হিসেবে image: পাঠায়
                    const imgUrl = "[https://pollinations.ai/p/](https://pollinations.ai/p/)" + encodeURIComponent(data.reply.replace("image:", "").trim()) + "?width=1024&height=1024&nologo=true";
                    appendMessage('bot', imgUrl, true);
                } else {
                    appendMessage('bot', data.reply);
                }
            } catch (e) {
                const loadingElement = document.getElementById('temp-loading');
                if (loadingElement) loadingElement.remove();
                appendMessage('bot', "Error: Server connect hoschena!");
            }
        }

        function appendMessage(role, text, isImage = false) {
            const chatWindow = document.getElementById('chat-window');
            const messageDiv = document.createElement('div');
            messageDiv.className = role === 'user' ? 'user-msg' : 'bot-msg';
            
            if (isImage) {
                messageDiv.innerHTML = `<img src="${text}" alt="Image"><br><a href="${text}" target="_blank" style="color:#00c3ff; font-size:12px;">Download Image</a>`;
            } else {
                let formattedText = text.replace(/\\n/g, '<br>')
                    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
                messageDiv.innerHTML = formattedText;
            }
            chatWindow.appendChild(messageDiv);
            chatWindow.scrollTo(0, chatWindow.scrollHeight);
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
    if msg.lower().startswith("image:"):
        return jsonify({"image": generate_image_url(msg)})
    
    ai_reply = get_ai_response(msg)
    return jsonify({"reply": ai_reply})

if __name__ == '__main__':
    app.run(debug=True)
