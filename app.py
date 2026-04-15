import os
import random
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ১. এপিআই কনফিগারেশন — ORIGINAL LOGIC UNCHANGED
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

# ── UPGRADED FRONTEND — Backend logic hooks preserved via identical /chat route ──
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="icon" type="image/png" href="https://i.ibb.co/Lz9f1zY/logo.png">
    <title>LOOM AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>

    <style>
        /* ── DESIGN TOKENS ── */
        :root {
            --bg-base:       #0e0f11;
            --bg-surface:    #16181c;
            --bg-elevated:   #1e2025;
            --bg-hover:      #23262d;
            --border:        rgba(255,255,255,0.07);
            --border-strong: rgba(255,255,255,0.13);
            --text-primary:  #e8eaed;
            --text-secondary:#8b8f9a;
            --text-muted:    #555a66;
            --accent:        #6c8cff;
            --accent-soft:   rgba(108,140,255,0.12);
            --accent-glow:   rgba(108,140,255,0.25);
            --user-bg:       #1f2937;
            --code-bg:       #0d1117;
            --code-header:   #161b22;
            --success:       #3fb950;
            --danger:        #f87171;
            --star-color:    #f5c542;
            --radius-sm:     6px;
            --radius-md:     12px;
            --radius-lg:     18px;
            --sidebar-w:     272px;
            --font-sans:     'DM Sans', sans-serif;
            --font-mono:     'DM Mono', monospace;
            --shadow-sm:     0 1px 3px rgba(0,0,0,0.4);
            --shadow-md:     0 4px 16px rgba(0,0,0,0.5);
            --shadow-lg:     0 8px 32px rgba(0,0,0,0.6);
            --transition:    0.18s ease;
        }

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html, body {
            height: 100%; width: 100%;
            font-family: var(--font-sans);
            background: var(--bg-base);
            color: var(--text-primary);
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
        }

        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333844; border-radius: 99px; }
        ::-webkit-scrollbar-thumb:hover { background: #4a5060; }

        #app { display: flex; height: 100vh; width: 100vw; position: relative; overflow: hidden; }

        /* ── SIDEBAR ── */
        #sidebar {
            width: var(--sidebar-w);
            min-width: var(--sidebar-w);
            background: var(--bg-surface);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            padding: 12px;
            transition: transform var(--transition), opacity var(--transition);
            z-index: 100;
            overflow: hidden;
        }

        .sidebar-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 4px 16px;
        }

        .logo-mark {
            display: flex;
            align-items: center;
            gap: 9px;
            font-size: 15px;
            font-weight: 600;
            letter-spacing: -0.3px;
            color: var(--text-primary);
        }

        .logo-icon {
            width: 28px; height: 28px;
            background: linear-gradient(135deg, #6c8cff 0%, #a78bfa 100%);
            border-radius: 8px;
            display: grid;
            place-items: center;
            font-size: 14px;
        }

        .btn-icon {
            width: 32px; height: 32px;
            background: transparent;
            border: none;
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            display: grid;
            place-items: center;
            cursor: pointer;
            transition: background var(--transition), color var(--transition);
            font-size: 16px;
        }
        .btn-icon:hover { background: var(--bg-hover); color: var(--text-primary); }

        .btn-new-chat {
            display: flex;
            align-items: center;
            gap: 9px;
            width: 100%;
            padding: 9px 12px;
            background: var(--accent-soft);
            border: 1px solid rgba(108,140,255,0.2);
            border-radius: var(--radius-md);
            color: var(--accent);
            font-family: var(--font-sans);
            font-size: 13.5px;
            font-weight: 500;
            cursor: pointer;
            transition: background var(--transition), border-color var(--transition);
            margin-bottom: 20px;
        }
        .btn-new-chat:hover { background: rgba(108,140,255,0.2); border-color: rgba(108,140,255,0.35); }

        .sidebar-section-label {
            font-size: 10.5px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
            padding: 0 6px 8px;
        }

        #history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; }

        /* ── HISTORY ITEM with hover 3-dot ── */
        .history-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 10px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 13px;
            color: var(--text-secondary);
            transition: background var(--transition), color var(--transition);
            position: relative;
            min-height: 36px;
        }
        .history-item:hover { background: var(--bg-hover); color: var(--text-primary); }
        .history-item.active { background: var(--bg-elevated); color: var(--text-primary); }

        .history-item .chat-icon { flex-shrink: 0; opacity: 0.5; width: 13px; height: 13px; }

        .history-item .star-badge {
            color: var(--star-color);
            font-size: 11px;
            flex-shrink: 0;
            line-height: 1;
        }

        .history-item .chat-title {
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            min-width: 0;
        }

        .history-item .chat-title-input {
            flex: 1;
            background: var(--bg-elevated);
            border: 1px solid var(--accent);
            border-radius: 4px;
            color: var(--text-primary);
            font-family: var(--font-sans);
            font-size: 13px;
            padding: 2px 6px;
            outline: none;
            min-width: 0;
        }

        .history-item .btn-options {
            width: 24px; height: 24px;
            display: grid;
            place-items: center;
            background: transparent;
            border: none;
            border-radius: 4px;
            color: var(--text-muted);
            cursor: pointer;
            flex-shrink: 0;
            opacity: 0;
            transition: opacity var(--transition), background var(--transition), color var(--transition);
        }
        .history-item:hover .btn-options,
        .history-item.active .btn-options { opacity: 1; }
        .history-item .btn-options:hover { background: var(--bg-hover); color: var(--text-primary); }

        /* ── CONTEXT MENU ── */
        #context-menu {
            position: fixed;
            z-index: 9999;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            padding: 6px;
            min-width: 180px;
            display: none;
            animation: menuFadeIn 0.12s ease;
        }
        #context-menu.open { display: block; }

        @keyframes menuFadeIn {
            from { opacity: 0; transform: scale(0.96) translateY(-4px); }
            to   { opacity: 1; transform: scale(1) translateY(0); }
        }

        .ctx-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 9px 12px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 13px;
            color: var(--text-secondary);
            transition: background var(--transition), color var(--transition);
            border: none;
            background: transparent;
            width: 100%;
            font-family: var(--font-sans);
            text-align: left;
        }
        .ctx-item:hover { background: var(--bg-hover); color: var(--text-primary); }
        .ctx-item.danger:hover { background: rgba(248,113,113,0.1); color: var(--danger); }
        .ctx-item svg { flex-shrink: 0; opacity: 0.7; }
        .ctx-item.danger svg { color: var(--danger); }
        .ctx-divider { height: 1px; background: var(--border); margin: 4px 0; }

        /* ── CONFIRM MODAL ── */
        #confirm-modal {
            position: fixed;
            inset: 0;
            z-index: 99999;
            background: rgba(0,0,0,0.65);
            display: none;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(3px);
        }
        #confirm-modal.open { display: flex; }

        .modal-box {
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-lg);
            padding: 28px 28px 24px;
            max-width: 340px;
            width: 90%;
            box-shadow: var(--shadow-lg);
            animation: modalIn 0.18s ease;
        }
        @keyframes modalIn {
            from { opacity: 0; transform: scale(0.94); }
            to   { opacity: 1; transform: scale(1); }
        }

        .modal-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px; }
        .modal-body  { font-size: 13.5px; color: var(--text-secondary); margin-bottom: 24px; line-height: 1.6; }
        .modal-actions { display: flex; gap: 10px; justify-content: flex-end; }

        .btn-cancel {
            padding: 8px 18px;
            background: transparent;
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            font-family: var(--font-sans);
            font-size: 13px;
            cursor: pointer;
            transition: all var(--transition);
        }
        .btn-cancel:hover { background: var(--bg-hover); color: var(--text-primary); }

        .btn-delete-confirm {
            padding: 8px 18px;
            background: rgba(248,113,113,0.15);
            border: 1px solid rgba(248,113,113,0.3);
            border-radius: var(--radius-sm);
            color: var(--danger);
            font-family: var(--font-sans);
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all var(--transition);
        }
        .btn-delete-confirm:hover { background: rgba(248,113,113,0.25); border-color: rgba(248,113,113,0.5); }

        /* ── SIDEBAR PROFILE ── */
        .sidebar-footer {
            border-top: 1px solid var(--border);
            padding-top: 12px;
            margin-top: 12px;
        }
        .profile-card {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 10px;
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: background var(--transition);
        }
        .profile-card:hover { background: var(--bg-hover); }
        .avatar {
            width: 32px; height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6c8cff, #a78bfa);
            display: grid;
            place-items: center;
            font-size: 13px;
            font-weight: 600;
            color: white;
            flex-shrink: 0;
        }
        .profile-info { flex: 1; overflow: hidden; }
        .profile-name { font-size: 13px; font-weight: 500; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .profile-role { font-size: 11px; color: var(--text-muted); }

        /* ── MAIN AREA ── */
        #main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

        #topbar {
            display: none;
            align-items: center;
            justify-content: space-between;
            padding: 10px 16px;
            background: var(--bg-base);
            border-bottom: 1px solid var(--border);
            z-index: 50;
        }
        .topbar-logo { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 600; }

        /* ── CHAT WINDOW ── */
        #chat-window {
            flex: 1;
            overflow-y: auto;
            padding: 32px 20px 12px;
            display: flex;
            flex-direction: column;
            gap: 0;
        }

        #welcome {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 40px 20px;
            gap: 16px;
            color: var(--text-secondary);
        }
        .welcome-icon {
            width: 56px; height: 56px;
            background: linear-gradient(135deg, #6c8cff 0%, #a78bfa 100%);
            border-radius: 16px;
            display: grid;
            place-items: center;
            font-size: 26px;
            box-shadow: 0 0 40px var(--accent-glow);
            margin-bottom: 4px;
        }
        .welcome-title { font-size: 22px; font-weight: 600; color: var(--text-primary); }
        .welcome-sub { font-size: 14px; line-height: 1.6; max-width: 380px; }
        .suggestion-grid { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 8px; }
        .suggestion-chip {
            padding: 8px 14px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: 99px;
            font-size: 12.5px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all var(--transition);
        }
        .suggestion-chip:hover { background: var(--bg-hover); color: var(--text-primary); border-color: var(--accent); }

        /* ── MESSAGE ROW ── */
        .msg-row {
            display: flex;
            gap: 14px;
            padding: 16px 0;
            max-width: 780px;
            width: 100%;
            margin: 0 auto;
            animation: fadeUp 0.22s ease both;
        }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .msg-row.user { flex-direction: row-reverse; }

        .msg-avatar {
            width: 32px; height: 32px;
            border-radius: 50%;
            flex-shrink: 0;
            display: grid;
            place-items: center;
            font-size: 14px;
            font-weight: 600;
            margin-top: 2px;
        }
        .msg-avatar.ai { background: linear-gradient(135deg, #6c8cff 0%, #a78bfa 100%); color: white; font-size: 13px; }
        .msg-avatar.user { background: var(--bg-elevated); border: 1px solid var(--border-strong); color: var(--text-secondary); font-size: 13px; }

        .msg-body { flex: 1; min-width: 0; }
        .msg-sender { font-size: 12px; font-weight: 600; letter-spacing: 0.02em; color: var(--text-muted); margin-bottom: 6px; }
        .msg-row.user .msg-sender { text-align: right; }

        .msg-content { font-size: 14.5px; line-height: 1.75; color: var(--text-primary); }
        .msg-row.user .msg-content {
            background: var(--user-bg);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg);
            padding: 12px 16px;
            display: inline-block;
            max-width: 85%;
            float: right;
            clear: both;
        }

        /* ── MARKDOWN ── */
        .msg-content p { margin-bottom: 10px; }
        .msg-content p:last-child { margin-bottom: 0; }
        .msg-content ul, .msg-content ol { padding-left: 20px; margin-bottom: 10px; }
        .msg-content li { margin-bottom: 4px; line-height: 1.6; }
        .msg-content h1, .msg-content h2, .msg-content h3 { margin: 16px 0 8px; font-weight: 600; }
        .msg-content h1 { font-size: 18px; }
        .msg-content h2 { font-size: 16px; }
        .msg-content h3 { font-size: 14px; }
        .msg-content strong { color: var(--text-primary); font-weight: 600; }
        .msg-content em { color: var(--text-secondary); }
        .msg-content a { color: var(--accent); text-decoration: none; }
        .msg-content a:hover { text-decoration: underline; }
        .msg-content blockquote { border-left: 3px solid var(--accent); padding-left: 12px; color: var(--text-secondary); margin: 10px 0; }
        .msg-content hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
        .msg-content code:not(pre code) {
            font-family: var(--font-mono);
            font-size: 13px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            padding: 2px 6px;
            border-radius: 4px;
            color: #f87171;
        }

        /* ── CODE BLOCK — max-height + scroll to prevent lag ── */
        .code-block-wrapper {
            background: var(--code-bg);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            overflow: hidden;
            margin: 12px 0;
        }
        .code-block-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--code-header);
            padding: 8px 14px;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 2;
        }
        .code-lang {
            font-family: var(--font-mono);
            font-size: 11.5px;
            font-weight: 500;
            color: var(--text-secondary);
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .btn-copy {
            display: flex;
            align-items: center;
            gap: 5px;
            background: transparent;
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            font-family: var(--font-sans);
            font-size: 11.5px;
            padding: 4px 10px;
            cursor: pointer;
            transition: all var(--transition);
        }
        .btn-copy:hover { background: var(--bg-hover); color: var(--text-primary); }
        .btn-copy.copied { color: var(--success); border-color: var(--success); }

        /* CRITICALLY IMPORTANT: max-height + overflow-y to prevent browser lag on large code */
        .code-block-wrapper pre {
            margin: 0;
            padding: 16px;
            overflow-x: auto;
            overflow-y: auto;          /* vertical scroll for long code */
            max-height: 480px;         /* prevents layout explosion */
            font-family: var(--font-mono);
            font-size: 13px;
            line-height: 1.65;
            background: transparent !important;
        }
        .code-block-wrapper code { background: transparent !important; font-size: 13px !important; }

        /* ── IMAGE ── */
        .generated-image-wrap { margin-top: 8px; }
        .generated-image-wrap img { width: 100%; max-width: 480px; border-radius: var(--radius-md); border: 1px solid var(--border); display: block; }
        .btn-download {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-top: 10px;
            padding: 7px 14px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            font-size: 12.5px;
            cursor: pointer;
            transition: all var(--transition);
            font-family: var(--font-sans);
        }
        .btn-download:hover { background: var(--bg-hover); color: var(--text-primary); }

        /* ── TYPING DOTS ── */
        .typing-dots { display: flex; gap: 5px; align-items: center; padding: 8px 0; }
        .typing-dots span { width: 7px; height: 7px; background: var(--text-muted); border-radius: 50%; animation: blink 1.2s infinite; }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink { 0%,80%,100% { opacity: 0.2; } 40% { opacity: 1; } }

        /* ── INPUT AREA ── */
        #input-area { padding: 0 20px 20px; background: var(--bg-base); }
        .input-wrapper-outer { max-width: 780px; margin: 0 auto; }
        .input-box {
            display: flex;
            align-items: flex-end;
            gap: 8px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-lg);
            padding: 10px 12px;
            transition: border-color var(--transition), box-shadow var(--transition);
        }
        .input-box:focus-within { border-color: rgba(108,140,255,0.4); box-shadow: 0 0 0 3px var(--accent-glow); }
        #user-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            resize: none;
            color: var(--text-primary);
            font-family: var(--font-sans);
            font-size: 14.5px;
            line-height: 1.6;
            max-height: 200px;
            min-height: 26px;
            overflow-y: auto;
            padding: 2px 0;
        }
        #user-input::placeholder { color: var(--text-muted); }
        .input-actions { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
        .btn-attach {
            width: 34px; height: 34px;
            display: grid;
            place-items: center;
            background: transparent;
            border: none;
            border-radius: var(--radius-sm);
            color: var(--text-muted);
            cursor: pointer;
            transition: color var(--transition), background var(--transition);
        }
        .btn-attach:hover { color: var(--text-secondary); background: var(--bg-hover); }
        #btn-send {
            width: 34px; height: 34px;
            display: grid;
            place-items: center;
            background: var(--accent);
            border: none;
            border-radius: var(--radius-sm);
            color: white;
            cursor: pointer;
            transition: background var(--transition), transform var(--transition);
            font-size: 15px;
            flex-shrink: 0;
        }
        #btn-send:hover { background: #5a7aff; transform: scale(1.05); }
        #btn-send:active { transform: scale(0.96); }
        #btn-send:disabled { background: var(--bg-hover); color: var(--text-muted); cursor: not-allowed; transform: none; }
        .input-hint { text-align: center; font-size: 11px; color: var(--text-muted); margin-top: 10px; }

        /* ── OVERLAY ── */
        #overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 99; backdrop-filter: blur(2px); }

        /* ── MOBILE ── */
        @media (max-width: 768px) {
            #sidebar {
                position: fixed;
                top: 0; left: 0; bottom: 0;
                transform: translateX(-100%);
                box-shadow: var(--shadow-lg);
            }
            #sidebar.open { transform: translateX(0); }
            #overlay.show { display: block; }
            #topbar { display: flex; }
            #chat-window { padding: 16px 14px 8px; }
            #input-area { padding: 0 12px 16px; }
            .msg-row { gap: 10px; }
            .msg-avatar { width: 28px; height: 28px; font-size: 12px; }
            .welcome-title { font-size: 19px; }
            /* Context menu full-width on very small screens */
            #context-menu { min-width: 160px; }
        }
        @media (min-width: 769px) { #topbar { display: none !important; } }
    </style>
</head>
<body>
<div id="app">

    <!-- ── SIDEBAR ── -->
    <aside id="sidebar">
        <div class="sidebar-top">
            <div class="logo-mark">
                <div class="logo-icon">✦</div>
                LOOM AI
            </div>
            <button class="btn-icon" onclick="closeSidebar()" title="Close">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
        </div>

        <button class="btn-new-chat" onclick="startNewChat()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            New conversation
        </button>

        <div class="sidebar-section-label">Recent</div>
        <div id="history-list"></div>

        <div class="sidebar-footer">
            <div class="profile-card">
                <div class="avatar">M</div>
                <div class="profile-info">
                    <div class="profile-name">Md Aminul Islam</div>
                    <div class="profile-role">Developer & AI Enthusiast</div>
                </div>
                <button class="btn-icon" style="margin-left:auto">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/></svg>
                </button>
            </div>
        </div>
    </aside>

    <!-- ── OVERLAY ── -->
    <div id="overlay" onclick="closeSidebar()"></div>

    <!-- ── CONTEXT MENU ── -->
    <div id="context-menu">
        <button class="ctx-item" id="ctx-star" onclick="ctxStar()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span id="ctx-star-label">Star</span>
        </button>
        <button class="ctx-item" onclick="ctxRename()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Rename
        </button>
        <button class="ctx-item" onclick="ctxAddToProject()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
            Add to Project
        </button>
        <div class="ctx-divider"></div>
        <button class="ctx-item danger" onclick="ctxDelete()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
            Delete
        </button>
    </div>

    <!-- ── DELETE CONFIRM MODAL ── -->
    <div id="confirm-modal">
        <div class="modal-box">
            <div class="modal-title">Delete conversation?</div>
            <div class="modal-body">This conversation will be permanently deleted and cannot be recovered.</div>
            <div class="modal-actions">
                <button class="btn-cancel" onclick="closeModal()">Cancel</button>
                <button class="btn-delete-confirm" onclick="confirmDelete()">Delete</button>
            </div>
        </div>
    </div>

    <!-- ── MAIN ── -->
    <main id="main">

        <div id="topbar">
            <button class="btn-icon" onclick="openSidebar()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
            </button>
            <div class="topbar-logo">
                <div class="logo-icon" style="width:24px;height:24px;font-size:12px;border-radius:6px">✦</div>
                LOOM AI
            </div>
            <button class="btn-icon" onclick="startNewChat()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
            </button>
        </div>

        <div id="chat-window">
            <div id="welcome">
                <div class="welcome-icon">✦</div>
                <div class="welcome-title">Good to see you.</div>
                <div class="welcome-sub">Ask me anything — code, ideas, images, or analysis. I'm LOOM AI.</div>
                <div class="suggestion-grid">
                    <div class="suggestion-chip" onclick="fillInput('Explain async/await in Python')">Explain async/await</div>
                    <div class="suggestion-chip" onclick="fillInput('image: futuristic city at night')">Generate an image</div>
                    <div class="suggestion-chip" onclick="fillInput('Write a Flask REST API boilerplate')">Flask API boilerplate</div>
                    <div class="suggestion-chip" onclick="fillInput('Who created you?')">Who made you?</div>
                </div>
            </div>
        </div>

        <div id="input-area">
            <div class="input-wrapper-outer">
                <div class="input-box">
                    <button class="btn-attach" title="Attach file">
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
                    </button>
                    <textarea
                        id="user-input"
                        rows="1"
                        placeholder="Message LOOM AI…"
                        onkeydown="handleKey(event)"
                        oninput="autoResize(this)"
                    ></textarea>
                    <div class="input-actions">
                        <button id="btn-send" onclick="send()" title="Send (Enter)">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 2L11 13"/><path d="M22 2L15 22 11 13 2 9l20-7z"/></svg>
                        </button>
                    </div>
                </div>
                <div class="input-hint">Enter to send · Shift+Enter for new line · type <strong>image:</strong> to generate</div>
            </div>
        </div>
    </main>
</div>

<script>
    /* ═══════════════════════════════════════════════════
       ORIGINAL CORE STATE — UNCHANGED
    ═══════════════════════════════════════════════════ */
    let currentChatId = null;
    // LOOM AI chats data structure:
    // { [chatId]: { title, starred, messages: [{role, text, isImage}] } }
    let chats = JSON.parse(localStorage.getItem('loom_ai_chats')) || {};

    /* ── STORAGE ── */
    function saveToLocal() {
        localStorage.setItem('loom_ai_chats', JSON.stringify(chats));
        renderHistory();
    }

    /* ═══════════════════════════════════════════════════
       FEATURE 1 + 2 + 3: PERSISTENT HISTORY + 3-DOT MENU
    ═══════════════════════════════════════════════════ */

    /* Track which chat the context menu is operating on */
    let ctxTargetId = null;

    function renderHistory() {
        const list = document.getElementById('history-list');
        list.innerHTML = '';

        const sorted = Object.keys(chats).sort((a, b) => {
            // Starred chats float to top
            if (chats[b].starred && !chats[a].starred) return 1;
            if (chats[a].starred && !chats[b].starred) return -1;
            return b - a; // then newest first
        });

        sorted.forEach(id => {
            const chat = chats[id];
            const item = document.createElement('div');
            item.className = 'history-item' + (id === currentChatId ? ' active' : '');
            item.dataset.id = id;

            item.innerHTML = `
                <svg class="chat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                </svg>
                ${chat.starred ? '<span class="star-badge">★</span>' : ''}
                <span class="chat-title" title="${chat.title || 'New Chat'}">${chat.title || 'New Chat'}</span>
                <button class="btn-options" data-id="${id}" onclick="openContextMenu(event, '${id}')" title="Options">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/>
                    </svg>
                </button>`;

            // Click on item body loads chat (not the options button)
            item.addEventListener('click', (e) => {
                if (e.target.closest('.btn-options')) return;
                loadChat(id);
                closeSidebar();
            });

            list.appendChild(item);
        });
    }

    /* ── CONTEXT MENU OPEN ── */
    function openContextMenu(e, id) {
        e.stopPropagation();
        ctxTargetId = id;

        const menu = document.getElementById('context-menu');
        const starLabel = document.getElementById('ctx-star-label');
        const ctxStarBtn = document.getElementById('ctx-star');

        // Update star label based on current state
        if (chats[id] && chats[id].starred) {
            starLabel.textContent = 'Unstar';
            ctxStarBtn.querySelector('svg').setAttribute('fill', 'currentColor');
            ctxStarBtn.style.color = 'var(--star-color)';
        } else {
            starLabel.textContent = 'Star';
            ctxStarBtn.querySelector('svg').setAttribute('fill', 'none');
            ctxStarBtn.style.color = '';
        }

        // Position menu near the button, keeping within viewport
        const rect = e.currentTarget.getBoundingClientRect();
        const menuW = 190;
        const menuH = 180;
        let left = rect.right + 6;
        let top  = rect.top;

        if (left + menuW > window.innerWidth - 8)  left = rect.left - menuW - 6;
        if (top  + menuH > window.innerHeight - 8) top  = window.innerHeight - menuH - 8;

        menu.style.left = left + 'px';
        menu.style.top  = top  + 'px';
        menu.classList.add('open');
    }

    /* Close context menu when clicking elsewhere */
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#context-menu') && !e.target.closest('.btn-options')) {
            closeContextMenu();
        }
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { closeContextMenu(); closeModal(); } });

    function closeContextMenu() {
        document.getElementById('context-menu').classList.remove('open');
    }

    /* ── CONTEXT MENU ACTIONS ── */

    /* STAR / UNSTAR */
    function ctxStar() {
        if (!ctxTargetId || !chats[ctxTargetId]) return;
        // HANDLE STAR LOGIC HERE — toggle starred state
        chats[ctxTargetId].starred = !chats[ctxTargetId].starred;
        saveToLocal();
        closeContextMenu();
    }

    /* RENAME — converts title span into an inline input */
    function ctxRename() {
        if (!ctxTargetId) return;
        closeContextMenu();

        const item = document.querySelector(`.history-item[data-id="${ctxTargetId}"]`);
        if (!item) return;

        const titleSpan = item.querySelector('.chat-title');
        const currentTitle = chats[ctxTargetId].title || 'New Chat';

        // Replace span with input
        const input = document.createElement('input');
        input.className = 'chat-title-input';
        input.value = currentTitle;
        titleSpan.replaceWith(input);
        input.focus();
        input.select();

        function commitRename() {
            const newTitle = input.value.trim() || currentTitle;
            // HANDLE RENAME LOGIC HERE — save the new title
            chats[ctxTargetId].title = newTitle;
            saveToLocal();
            // renderHistory() will rebuild the item with the new title
        }

        input.addEventListener('blur', commitRename);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
            if (e.key === 'Escape') { input.value = currentTitle; input.blur(); }
        });
    }

    /* ADD TO PROJECT — placeholder for your custom integration */
    function ctxAddToProject() {
        closeContextMenu();
        // ADD TO PROJECT LOGIC HERE — wire to your project system
        // e.g. openProjectPicker(ctxTargetId);
        console.log('Add to project:', ctxTargetId);
    }

    /* DELETE — shows confirmation modal */
    function ctxDelete() {
        closeContextMenu();
        document.getElementById('confirm-modal').classList.add('open');
    }

    function closeModal() {
        document.getElementById('confirm-modal').classList.remove('open');
    }

    function confirmDelete() {
        if (!ctxTargetId || !chats[ctxTargetId]) { closeModal(); return; }
        // HANDLE DELETE LOGIC HERE
        delete chats[ctxTargetId];
        if (currentChatId === ctxTargetId) {
            currentChatId = null;
            startNewChat();
        }
        saveToLocal();
        closeModal();
        ctxTargetId = null;
    }

    /* ═══════════════════════════════════════════════════
       ORIGINAL CHAT LOGIC — UNCHANGED BEHAVIOUR
    ═══════════════════════════════════════════════════ */

    function startNewChat() {
        currentChatId = Date.now().toString();
        const win = document.getElementById('chat-window');
        win.innerHTML = '';
        win.appendChild(buildWelcome());
        renderHistory();
        closeSidebar();
        document.getElementById('user-input').focus();
    }

    function buildWelcome() {
        const w = document.createElement('div');
        w.id = 'welcome';
        w.innerHTML = `
            <div class="welcome-icon">✦</div>
            <div class="welcome-title">Good to see you.</div>
            <div class="welcome-sub">Ask me anything — code, ideas, images, or analysis. I'm LOOM AI.</div>
            <div class="suggestion-grid">
                <div class="suggestion-chip" onclick="fillInput('Explain async/await in Python')">Explain async/await</div>
                <div class="suggestion-chip" onclick="fillInput('image: futuristic city at night')">Generate an image</div>
                <div class="suggestion-chip" onclick="fillInput('Write a Flask REST API boilerplate')">Flask API boilerplate</div>
                <div class="suggestion-chip" onclick="fillInput('Who created you?')">Who made you?</div>
            </div>`;
        return w;
    }

    function loadChat(id) {
        currentChatId = id;
        const win = document.getElementById('chat-window');
        win.innerHTML = '';
        if (chats[id] && chats[id].messages) {
            chats[id].messages.forEach(m => appendMessage(m.role, m.text, m.isImage, false));
        }
        renderHistory();
    }

    function fillInput(text) {
        const ta = document.getElementById('user-input');
        ta.value = text;
        autoResize(ta);
        ta.focus();
    }

    function autoResize(el) {
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 200) + 'px';
    }

    function handleKey(e) {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
    }

    function openSidebar()  { document.getElementById('sidebar').classList.add('open'); document.getElementById('overlay').classList.add('show'); }
    function closeSidebar() { document.getElementById('sidebar').classList.remove('open'); document.getElementById('overlay').classList.remove('show'); }

    /* ── ORIGINAL SEND — UNCHANGED ── */
    async function send() {
        const input = document.getElementById('user-input');
        const text = input.value.trim();
        if (!text) return;

        if (!currentChatId) startNewChat();

        const welcome = document.getElementById('welcome');
        if (welcome) welcome.remove();

        appendMessage('user', text);
        input.value = '';
        input.style.height = 'auto';

        const sendBtn = document.getElementById('btn-send');
        sendBtn.disabled = true;

        const typingRow = buildTypingRow();
        document.getElementById('chat-window').appendChild(typingRow);
        scrollBottom();

        try {
            /* ── ORIGINAL FETCH — UNCHANGED ── */
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();
            typingRow.remove();

            if (data.image) {
                appendMessage('bot', data.image, true);
            } else {
                appendMessage('bot', data.reply);
            }
        } catch (e) {
            typingRow.remove();
            appendMessage('bot', '**Connection error.** Please try again.');
        } finally {
            sendBtn.disabled = false;
            document.getElementById('user-input').focus();
        }
    }

    function buildTypingRow() {
        const row = document.createElement('div');
        row.className = 'msg-row ai';
        row.innerHTML = `
            <div class="msg-avatar ai">✦</div>
            <div class="msg-body">
                <div class="msg-sender">LOOM AI</div>
                <div class="msg-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>
            </div>`;
        return row;
    }

    /* ── APPEND MESSAGE — ORIGINAL LOGIC UNCHANGED ── */
    function appendMessage(role, text, isImage = false, save = true) {
        const win = document.getElementById('chat-window');
        const row = document.createElement('div');
        row.className = 'msg-row ' + (role === 'user' ? 'user' : 'ai');

        const avatarHtml = role === 'user'
            ? `<div class="msg-avatar user">U</div>`
            : `<div class="msg-avatar ai">✦</div>`;
        const senderLabel = role === 'user' ? 'You' : 'LOOM AI';

        let contentHtml = '';
        if (isImage) {
            contentHtml = `
                <div class="generated-image-wrap">
                    <img src="${text}" alt="Generated image" loading="lazy">
                    <button class="btn-download" onclick="downloadImage('${text}')">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                        Download image
                    </button>
                </div>`;
        } else {
            contentHtml = renderMarkdown(text);
        }

        row.innerHTML = `
            ${avatarHtml}
            <div class="msg-body">
                <div class="msg-sender">${senderLabel}</div>
                <div class="msg-content">${contentHtml}</div>
            </div>`;

        win.appendChild(row);
        row.querySelectorAll('pre code').forEach(el => { hljs.highlightElement(el); });
        scrollBottom();

        if (save && currentChatId) {
            if (!chats[currentChatId]) {
                chats[currentChatId] = {
                    title: text.substring(0, 28) + (text.length > 28 ? '…' : ''),
                    starred: false,
                    messages: []
                };
            }
            chats[currentChatId].messages.push({ role, text, isImage });
            saveToLocal();
        }
    }

    /* ── FEATURE 4: PREMIUM CODE BLOCK RENDERER with max-height scroll ── */
    function renderMarkdown(text) {
        const renderer = new marked.Renderer();
        renderer.code = function(code, lang) {
            const language = (lang || 'plaintext').toLowerCase();
            const displayLang = lang || 'plaintext';
            const escaped = code
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
            // Code block with sticky header, max-height 480px, overflow-y auto
            // This prevents browser lag when AI returns thousands of lines
            return `
                <div class="code-block-wrapper">
                    <div class="code-block-header">
                        <span class="code-lang">${displayLang}</span>
                        <button class="btn-copy" onclick="copyCode(this)">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                            Copy
                        </button>
                    </div>
                    <pre><code class="language-${language}">${escaped}</code></pre>
                </div>`;
        };
        marked.use({ renderer });
        return marked.parse(text);
    }

    /* ── COPY CODE ── */
    function copyCode(btn) {
        const pre = btn.closest('.code-block-wrapper').querySelector('pre');
        navigator.clipboard.writeText(pre.innerText).then(() => {
            btn.classList.add('copied');
            btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Copy`;
            }, 2000);
        });
    }

    /* ── DOWNLOAD IMAGE — ORIGINAL LOGIC UNCHANGED ── */
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

    function scrollBottom() {
        const win = document.getElementById('chat-window');
        win.scrollTo({ top: win.scrollHeight, behavior: 'smooth' });
    }

    /* ── INIT ── */
    renderHistory();
    if (!currentChatId) startNewChat();
</script>
</body>
</html>
"""

# ── ORIGINAL ROUTES — UNCHANGED ──
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
