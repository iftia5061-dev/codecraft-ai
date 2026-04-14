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

# ২. PREMIUM REDESIGNED FRONTEND — Logic hooks preserved via identical /chat route
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="icon" type="image/png" href="https://i.ibb.co/Lz9f1zY/logo.png">
    <title>LOOM AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
    <!-- Highlight.js for syntax highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <!-- Marked.js for Markdown parsing -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>

    <style>
        /* ── DESIGN TOKENS ──────────────────────────────── */
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

        /* ── RESET ──────────────────────────────────────── */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html, body {
            height: 100%; width: 100%;
            font-family: var(--font-sans);
            background: var(--bg-base);
            color: var(--text-primary);
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
        }

        /* ── SCROLLBAR ───────────────────────────────────── */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333844; border-radius: 99px; }
        ::-webkit-scrollbar-thumb:hover { background: #4a5060; }

        /* ── APP SHELL ───────────────────────────────────── */
        #app { display: flex; height: 100vh; width: 100vw; position: relative; overflow: hidden; }

        /* ── SIDEBAR ─────────────────────────────────────── */
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
        .btn-new-chat svg { flex-shrink: 0; }

        .sidebar-section-label {
            font-size: 10.5px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
            padding: 0 6px 8px;
        }

        #history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; }

        .history-item {
            display: flex;
            align-items: center;
            gap: 9px;
            padding: 9px 10px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 13px;
            color: var(--text-secondary);
            transition: background var(--transition), color var(--transition);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .history-item:hover { background: var(--bg-hover); color: var(--text-primary); }
        .history-item.active { background: var(--bg-elevated); color: var(--text-primary); }
        .history-item svg { flex-shrink: 0; opacity: 0.5; }

        /* ── SIDEBAR PROFILE ─────────────────────────────── */
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

        /* ── MAIN AREA ───────────────────────────────────── */
        #main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

        /* ── TOP BAR (mobile) ────────────────────────────── */
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

        /* ── CHAT WINDOW ─────────────────────────────────── */
        #chat-window {
            flex: 1;
            overflow-y: auto;
            padding: 32px 20px 12px;
            display: flex;
            flex-direction: column;
            gap: 0;
        }

        /* ── WELCOME STATE ───────────────────────────────── */
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

        /* ── MESSAGE ROW ─────────────────────────────────── */
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

        .msg-avatar.ai {
            background: linear-gradient(135deg, #6c8cff 0%, #a78bfa 100%);
            color: white;
            font-size: 13px;
        }

        .msg-avatar.user {
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            color: var(--text-secondary);
            font-size: 13px;
        }

        .msg-body { flex: 1; min-width: 0; }

        .msg-sender {
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.02em;
            color: var(--text-muted);
            margin-bottom: 6px;
        }

        .msg-row.user .msg-sender { text-align: right; }

        .msg-content {
            font-size: 14.5px;
            line-height: 1.75;
            color: var(--text-primary);
        }

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

        .msg-row.ai .msg-content {
            background: transparent;
        }

        /* ── MARKDOWN CONTENT ────────────────────────────── */
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
        .msg-content blockquote {
            border-left: 3px solid var(--accent);
            padding-left: 12px;
            color: var(--text-secondary);
            margin: 10px 0;
        }
        .msg-content hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }

        /* Inline code */
        .msg-content code:not(pre code) {
            font-family: var(--font-mono);
            font-size: 13px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            padding: 2px 6px;
            border-radius: 4px;
            color: #f87171;
        }

        /* ── CODE BLOCK ──────────────────────────────────── */
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
        .btn-copy:hover { background: var(--bg-hover); color: var(--text-primary); border-color: var(--border-strong); }
        .btn-copy.copied { color: var(--success); border-color: var(--success); }

        .code-block-wrapper pre {
            margin: 0;
            padding: 16px;
            overflow-x: auto;
            font-family: var(--font-mono);
            font-size: 13px;
            line-height: 1.65;
            max-height: 520px;
            overflow-y: auto;
            background: transparent !important;
        }

        .code-block-wrapper code { background: transparent !important; font-size: 13px !important; }

        /* ── IMAGE IN CHAT ───────────────────────────────── */
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

        /* ── TYPING INDICATOR ────────────────────────────── */
        .typing-dots { display: flex; gap: 5px; align-items: center; padding: 8px 0; }
        .typing-dots span {
            width: 7px; height: 7px;
            background: var(--text-muted);
            border-radius: 50%;
            animation: blink 1.2s infinite;
        }
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink { 0%,80%,100% { opacity: 0.2; } 40% { opacity: 1; } }

        /* ── INPUT AREA ──────────────────────────────────── */
        #input-area {
            padding: 0 20px 20px;
            background: var(--bg-base);
        }

        .input-wrapper-outer {
            max-width: 780px;
            margin: 0 auto;
        }

        .input-box {
            display: flex;
            align-items: flex-end;
            gap: 8px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-lg);
            padding: 10px 12px;
            box-shadow: 0 0 0 0 transparent;
            transition: border-color var(--transition), box-shadow var(--transition);
        }
        .input-box:focus-within {
            border-color: rgba(108,140,255,0.4);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }

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
            font-size: 16px;
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

        .input-hint {
            text-align: center;
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 10px;
        }

        /* ── OVERLAY (mobile sidebar) ────────────────────── */
        #overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            z-index: 99;
            backdrop-filter: blur(2px);
        }

        /* ── MOBILE RESPONSIVE ───────────────────────────── */
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
        }

        @media (min-width: 769px) {
            #topbar { display: none !important; }
        }
    </style>
</head>
<body>
<div id="app">

    <!-- ── SIDEBAR ───────────────────────────────────────── -->
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

        <!-- ── USER PROFILE — keep your own user data here ── -->
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

    <!-- ── OVERLAY ────────────────────────────────────────── -->
    <div id="overlay" onclick="closeSidebar()"></div>

    <!-- ── MAIN ──────────────────────────────────────────── -->
    <main id="main">

        <!-- Mobile Top Bar -->
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

        <!-- Chat Window -->
        <div id="chat-window">
            <!-- Welcome screen shown when chat is empty -->
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

        <!-- Input Area -->
        <div id="input-area">
            <div class="input-wrapper-outer">
                <div class="input-box">
                    <!-- Attachment button — wire to your own file handler -->
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
    /* ═══════════════════════════════════════════════════════
       ORIGINAL APP LOGIC — UNCHANGED
       (startNewChat, loadChat, saveToLocal, renderHistory,
        send, appendMessage, downloadImage, generateImageUrl
        all preserved below with only UI-layer additions)
    ═══════════════════════════════════════════════════════ */

    let currentChatId = null;
    let chats = JSON.parse(localStorage.getItem('loom_ai_chats')) || {};

    /* ── STORAGE ─────────────────────────────────────────── */
    function saveToLocal() {
        localStorage.setItem('loom_ai_chats', JSON.stringify(chats));
        renderHistory();
    }

    /* ── RENDER HISTORY LIST ─────────────────────────────── */
    function renderHistory() {
        const list = document.getElementById('history-list');
        list.innerHTML = '';
        Object.keys(chats).sort((a, b) => b - a).forEach(id => {
            const item = document.createElement('div');
            item.className = 'history-item' + (id === currentChatId ? ' active' : '');
            item.innerHTML = `
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                ${chats[id].title || 'New Chat'}
            `;
            item.onclick = () => { loadChat(id); closeSidebar(); };
            list.appendChild(item);
        });
    }

    /* ── NEW CHAT ────────────────────────────────────────── */
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

    /* ── LOAD CHAT ───────────────────────────────────────── */
    function loadChat(id) {
        currentChatId = id;
        const win = document.getElementById('chat-window');
        win.innerHTML = '';
        if (chats[id] && chats[id].messages) {
            chats[id].messages.forEach(m => appendMessage(m.role, m.text, m.isImage, false));
        }
        renderHistory();
    }

    /* ── FILL INPUT (suggestion chips) ──────────────────── */
    function fillInput(text) {
        const ta = document.getElementById('user-input');
        ta.value = text;
        autoResize(ta);
        ta.focus();
    }

    /* ── AUTO-RESIZE TEXTAREA ────────────────────────────── */
    function autoResize(el) {
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 200) + 'px';
    }

    /* ── KEYBOARD HANDLER ────────────────────────────────── */
    function handleKey(e) {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
    }

    /* ── SIDEBAR OPEN/CLOSE ──────────────────────────────── */
    function openSidebar()  { document.getElementById('sidebar').classList.add('open'); document.getElementById('overlay').classList.add('show'); }
    function closeSidebar() { document.getElementById('sidebar').classList.remove('open'); document.getElementById('overlay').classList.remove('show'); }

    /* ══════════════════════════════════════════════════════
       ORIGINAL SEND + APPEND LOGIC — UNCHANGED BEHAVIOUR
    ══════════════════════════════════════════════════════ */
    async function send() {
        const input = document.getElementById('user-input');
        const text = input.value.trim();
        if (!text) return;

        if (!currentChatId) startNewChat();

        // Remove welcome screen on first message
        const welcome = document.getElementById('welcome');
        if (welcome) welcome.remove();

        appendMessage('user', text);
        input.value = '';
        input.style.height = 'auto';

        // Disable send while waiting
        const sendBtn = document.getElementById('btn-send');
        sendBtn.disabled = true;

        // Typing indicator
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

    /* ── APPEND MESSAGE ──────────────────────────────────── */
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

        // Apply syntax highlighting to any new code blocks
        row.querySelectorAll('pre code').forEach(el => { hljs.highlightElement(el); });

        scrollBottom();

        if (save && currentChatId) {
            if (!chats[currentChatId]) {
                chats[currentChatId] = { title: text.substring(0, 28) + (text.length > 28 ? '…' : ''), messages: [] };
            }
            chats[currentChatId].messages.push({ role, text, isImage });
            saveToLocal();
        }
    }

    /* ── MARKDOWN RENDERER ───────────────────────────────── */
    function renderMarkdown(text) {
        // Configure marked to use code block wrapper
        const renderer = new marked.Renderer();
        renderer.code = function(code, lang) {
            const language = (lang || 'plaintext').toLowerCase();
            const displayLang = lang || 'plaintext';
            const escaped = code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
            const id = 'cb_' + Math.random().toString(36).slice(2,8);
            return `
                <div class="code-block-wrapper">
                    <div class="code-block-header">
                        <span class="code-lang">${displayLang}</span>
                        <button class="btn-copy" id="${id}" onclick="copyCode(this)">
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

    /* ── COPY CODE ───────────────────────────────────────── */
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

    /* ── DOWNLOAD IMAGE — ORIGINAL LOGIC UNCHANGED ──────── */
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

    /* ── SCROLL BOTTOM ───────────────────────────────────── */
    function scrollBottom() {
        const win = document.getElementById('chat-window');
        win.scrollTo({ top: win.scrollHeight, behavior: 'smooth' });
    }

    /* ── INIT ────────────────────────────────────────────── */
    renderHistory();
    if (!currentChatId) startNewChat();
</script>
</body>
</html>
"""

# ── ORIGINAL ROUTES — UNCHANGED ──────────────────────────
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
