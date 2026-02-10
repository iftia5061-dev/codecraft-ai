import os
import random
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ১. এপিআই কনফিগারেশন (Vercel Environment Variables থেকে নেবে)
API_KEYS = [
    os.environ.get("API_KEY_1", ""),
    os.environ.get("API_KEY_2", ""),
    os.environ.get("API_KEY_3", "")
]

def get_ai_response(prompt):
    active_key = random.choice([k for k in API_KEYS if k])
    if not active_key:
        return "Error: No API Key found in Environment Variables!"
    
    genai.configure(api_key=active_key)
    model = genai.GenerativeModel('gemini-1.5-flash') # Vercel-এর জন্য স্টেবল মডেল
    
    system_instruction = "You are CodeCraft AI. Provide clean code or concise answers."
    response = model.generate_content([system_instruction, prompt])
    return response.text

# ২. ইমেজ জেনারেশন লজিক
def generate_image_url(prompt):
    seed = random.randint(0, 999999)
    return f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}"

# ৩. ইন্টারফেস (HTML + CSS) - কোনো লোগো থাকবে না
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LOOM AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background-color: #000; color: #e0e0e0; font-family: sans-serif; margin: 0; padding: 20px; }
        .header { text-align: center; padding: 10px; border-bottom: 1px solid #222; }
        #chat-container { margin-bottom: 100px; }
        .user-message { background: linear-gradient(135deg, #0056b3, #004494); padding: 15px; border-radius: 15px 15px 0 15px; margin: 10px 0; margin-left: 20%; }
        .bot-message { background: #121212; padding: 15px; border-radius: 15px 15px 15px 0; border: 1px solid #1f1f1f; margin: 10px 0; }
        .input-area { position: fixed; bottom: 0; left: 0; width: 100%; background: #000; padding: 20px; box-sizing: border-box; }
        input { width: 85%; padding: 12px; border-radius: 25px; border: 1px solid #333; background: #111; color: white; }
        button { width: 10%; padding: 12px; border-radius: 50%; border: none; background: #0056b3; color: white; cursor: pointer; }
        img { max-width: 100%; border-radius: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>🚀 CodeCraft AI</h2>
        <p style="font-size: 12px; color: #555;">Developed by: IFTI</p>
    </div>
    <div id="chat-container"></div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Ask anything or image: sunset">
        <button onclick="sendMessage()">➔</button>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const container = document.getElementById('chat-container');
            if(!input.value) return;

            const userText = input.value;
            container.innerHTML += `<div class="user-message">${userText}</div>`;
            input.value = '';

            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: userText})
            });
            const data = await response.json();
            
            if(data.image) {
                container.innerHTML += `<div class="bot-message"><p>🎨 Image Generated:</p><img src="${data.image}"></div>`;
            } else {
                container.innerHTML += `<div class="bot-message">${data.reply}</div>`;
            }
            window.scrollTo(0, document.body.scrollHeight);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get("message", "")
    if msg.lower().startswith("image:"):
        img_url = generate_image_url(msg[6:].strip())
        return jsonify({"image": img_url})
    else:
        reply = get_ai_response(msg)
        return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
