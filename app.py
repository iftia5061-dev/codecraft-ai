import os
import random
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ════════════════════════════════════════════════════════════════
# ORIGINAL CORE LOGIC — UNCHANGED
# ════════════════════════════════════════════════════════════════

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
        model = genai.GenerativeModel('gemini-2.0-flash-preview')
        system_instruction = """
        You are LOOM AI. Your replies must be clean, professional, and well-structured using markdown.
        DO NOT give long-winded answers. Be direct.

        ARTIFACT SYSTEM INSTRUCTIONS (CRITICAL):
        When you generate ANY code block (HTML, CSS, JS, Python, etc.), you MUST wrap it in a special artifact tag like this:

        <artifact id="unique-id" type="html|css|js|python|text" title="Descriptive Title">
        ```language
        ...your code here...
        ```
        </artifact>

        Rules:
        - Use type="html" for HTML/CSS/JS combined files or pure HTML.
        - Use type="python" for Python code.
        - Use type="js" for standalone JavaScript.
        - Use type="text" for JSON, YAML, config files, etc.
        - The artifact id must be a short slug like "flask-api", "todo-app", "login-form".
        - Always include a short descriptive title.
        - Regular explanatory text goes OUTSIDE the artifact tags, in the normal chat.
        - If the user asks to UPDATE existing code, use the SAME artifact id as before so the panel updates in place.

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

# ════════════════════════════════════════════════════════════════
# HTML TEMPLATE — UPGRADED WITH ARTIFACTS SYSTEM
# ════════════════════════════════════════════════════════════════

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0e0f11">
    <link rel="icon" type="image/png" href="https://i.ibb.co/Lz9f1zY/logo.png">
    <title>LOOM AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
        import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut }
            from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

        const firebaseConfig = {
            apiKey:            "AIzaSyCa4ILv8tXw7zNeLaXKZMcHdmOcB7fpQsg",
            authDomain:        "codecraft-ai-e0c31.firebaseapp.com",
            projectId:         "codecraft-ai-e0c31",
            storageBucket:     "codecraft-ai-e0c31.firebasestorage.app",
            messagingSenderId: "120391757852",
            appId:             "1:120391757852:web:dd52dc1b373d597bd96fd9",
            measurementId:     "G-NDH3Y3PWW8"
        };

        const firebaseApp = initializeApp(firebaseConfig);
        const auth        = getAuth(firebaseApp);
        const provider    = new GoogleAuthProvider();
        window._loomAuth  = auth;

        window.signInWithGoogle = async () => {
            const btn = document.getElementById('google-btn');
            if (btn) { btn.disabled = true; btn.textContent = 'Signing in…'; }
            try {
                await signInWithPopup(auth, provider);
            } catch (err) {
                console.error('Google sign-in error:', err);
                if (btn) { btn.disabled = false; btn.innerHTML = googleBtnHTML(); }
                showAuthError(err.code);
            }
        };

        window.signOut = () => signOut(auth);

        onAuthStateChanged(auth, (user) => {
            const authPage = document.getElementById('auth-page');
            const appPage  = document.getElementById('app');
            if (user) {
                if (authPage) authPage.style.display = 'none';
                if (appPage)  appPage.style.display  = 'flex';
                const nameEl   = document.getElementById('profile-name');
                const emailEl  = document.getElementById('profile-email');
                const avatarEl = document.getElementById('profile-avatar');
                if (nameEl)  nameEl.textContent  = user.displayName || 'User';
                if (emailEl) emailEl.textContent  = user.email       || 'Sign out';
                if (avatarEl) {
                    if (user.photoURL) {
                        avatarEl.innerHTML = `<img src="${user.photoURL}" style="width:100%;height:100%;border-radius:50%;object-fit:cover" referrerpolicy="no-referrer">`;
                    } else {
                        avatarEl.textContent = (user.displayName || 'U')[0].toUpperCase();
                    }
                }
                if (typeof startNewChat === 'function') startNewChat();
            } else {
                if (authPage) authPage.style.display = 'flex';
                if (appPage)  appPage.style.display  = 'none';
            }
        });

        function googleBtnHTML() {
            return `<svg width="18" height="18" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg> Continue with Google`;
        }

        function showAuthError(code) {
            const messages = {
                'auth/popup-closed-by-user': 'Sign-in cancelled.',
                'auth/network-request-failed': 'Network error.',
                'auth/popup-blocked': 'Popup blocked — allow popups for this site.',
                'auth/unauthorized-domain': 'Domain not authorised in Firebase Console.',
            };
            const el = document.getElementById('auth-error');
            if (el) { el.textContent = messages[code] || `Sign-in failed (${code}).`; el.style.display = 'block'; }
        }
    </script>

    <style>
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
            --artifact-w:    520px;
            --font-sans:     'DM Sans', sans-serif;
            --font-display:  'Syne', sans-serif;
            --font-mono:     'DM Mono', monospace;
            --shadow-sm:     0 1px 3px rgba(0,0,0,0.4);
            --shadow-md:     0 4px 16px rgba(0,0,0,0.5);
            --shadow-lg:     0 8px 32px rgba(0,0,0,0.6);
            --transition:    0.18s ease;
            --safe-bottom:   env(safe-area-inset-bottom, 0px);
            --safe-top:      env(safe-area-inset-top, 0px);
        }

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { height: 100%; overscroll-behavior: none; }
        body {
            height: 100%; width: 100%;
            font-family: var(--font-sans);
            background: var(--bg-base);
            color: var(--text-primary);
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
            overscroll-behavior: none;
        }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333844; border-radius: 99px; }

        /* ── AUTH PAGE ── */
        #auth-page {
            position: fixed; inset: 0;
            background: var(--bg-base);
            display: flex; align-items: center; justify-content: center;
            z-index: 99999; padding: 24px;
            background-image:
                linear-gradient(rgba(108,140,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(108,140,255,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
        }
        .auth-card {
            background: var(--bg-surface); border: 1px solid var(--border-strong);
            border-radius: 24px; padding: 48px 40px 40px;
            max-width: 420px; width: 100%;
            display: flex; flex-direction: column; align-items: center; gap: 0;
            box-shadow: 0 0 80px rgba(108,140,255,0.08), var(--shadow-lg);
            animation: authCardIn 0.5s cubic-bezier(0.22,1,0.36,1) both;
        }
        @keyframes authCardIn { from { opacity:0; transform:translateY(20px) scale(0.97); } to { opacity:1; transform:none; } }
        .auth-logo {
            width:64px; height:64px;
            background: linear-gradient(135deg,#6c8cff,#a78bfa);
            border-radius:18px; display:grid; place-items:center;
            font-size:30px; box-shadow: 0 0 48px var(--accent-glow);
            margin-bottom:24px; animation: logoPulse 3s ease-in-out infinite;
        }
        @keyframes logoPulse { 0%,100% { box-shadow:0 0 48px var(--accent-glow); } 50% { box-shadow:0 0 72px rgba(108,140,255,0.45); } }
        .auth-title { font-family:var(--font-display); font-size:32px; font-weight:800; letter-spacing:-0.5px; margin-bottom:10px; text-align:center; }
        .auth-tagline { font-size:14px; color:var(--text-secondary); text-align:center; line-height:1.65; max-width:300px; margin-bottom:32px; }
        .auth-features { display:flex; flex-direction:column; gap:10px; width:100%; margin-bottom:32px; }
        .auth-feature { display:flex; align-items:center; gap:12px; padding:12px 14px; background:var(--bg-elevated); border:1px solid var(--border); border-radius:var(--radius-md); }
        .auth-feature-icon { width:32px; height:32px; border-radius:8px; display:grid; place-items:center; font-size:15px; flex-shrink:0; }
        .auth-feature-text { font-size:13px; color:var(--text-secondary); line-height:1.4; }
        .auth-feature-text strong { color:var(--text-primary); display:block; font-size:13px; margin-bottom:1px; }
        #google-btn {
            display:flex; align-items:center; justify-content:center; gap:10px;
            width:100%; padding:13px 20px; background:#fff; border:none;
            border-radius:var(--radius-md); color:#1a1a2e;
            font-family:var(--font-sans); font-size:15px; font-weight:600;
            cursor:pointer; transition:all 0.2s; box-shadow:0 2px 8px rgba(0,0,0,0.3);
        }
        #google-btn:hover { transform:translateY(-1px); box-shadow:0 6px 20px rgba(0,0,0,0.4); }
        #google-btn:disabled { opacity:0.6; cursor:not-allowed; transform:none; }
        #auth-error {
            display:none; margin-top:12px; font-size:12.5px; color:var(--danger);
            text-align:center; padding:8px 12px;
            background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.2);
            border-radius:var(--radius-sm); width:100%;
        }
        .auth-footer { margin-top:20px; font-size:11.5px; color:var(--text-muted); text-align:center; line-height:1.6; }
        .auth-footer a { color:var(--accent); text-decoration:none; }

        /* ── MAIN APP LAYOUT ── */
        #app {
            display: none;
            height: 100vh; width: 100vw;
            position: relative; overflow: hidden;
        }

        /* ── SIDEBAR ── */
        #sidebar {
            width: var(--sidebar-w); min-width: var(--sidebar-w);
            background: var(--bg-surface); border-right: 1px solid var(--border);
            display: flex; flex-direction: column; padding: 12px;
            transition: transform var(--transition); z-index: 100; overflow: hidden;
        }
        .sidebar-top { display:flex; align-items:center; justify-content:space-between; padding:6px 4px 16px; }
        .logo-mark { display:flex; align-items:center; gap:9px; font-family:var(--font-display); font-size:16px; font-weight:700; letter-spacing:-0.3px; }
        .logo-icon { width:28px; height:28px; background:linear-gradient(135deg,#6c8cff,#a78bfa); border-radius:8px; display:grid; place-items:center; font-size:14px; }
        .btn-icon { width:32px; height:32px; background:transparent; border:none; border-radius:var(--radius-sm); color:var(--text-secondary); display:grid; place-items:center; cursor:pointer; transition:background var(--transition),color var(--transition); font-size:16px; }
        .btn-icon:hover { background:var(--bg-hover); color:var(--text-primary); }
        .btn-new-chat {
            display:flex; align-items:center; gap:9px; width:100%;
            padding:9px 12px; background:var(--accent-soft);
            border:1px solid rgba(108,140,255,0.2); border-radius:var(--radius-md);
            color:var(--accent); font-family:var(--font-sans); font-size:13.5px; font-weight:500;
            cursor:pointer; transition:background var(--transition); margin-bottom:20px;
        }
        .btn-new-chat:hover { background:rgba(108,140,255,0.2); }
        .sidebar-section-label { font-size:10.5px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:var(--text-muted); padding:0 6px 8px; }
        #history-list { flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:2px; }
        .history-item { display:flex; align-items:center; gap:8px; padding:8px 10px; border-radius:var(--radius-sm); cursor:pointer; font-size:13px; color:var(--text-secondary); transition:background var(--transition),color var(--transition); position:relative; min-height:36px; }
        .history-item:hover { background:var(--bg-hover); color:var(--text-primary); }
        .history-item.active { background:var(--bg-elevated); color:var(--text-primary); }
        .history-item .chat-icon { flex-shrink:0; opacity:0.5; width:13px; height:13px; }
        .history-item .star-badge { color:var(--star-color); font-size:11px; flex-shrink:0; }
        .history-item .chat-title { flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; min-width:0; }
        .history-item .chat-title-input { flex:1; background:var(--bg-elevated); border:1px solid var(--accent); border-radius:4px; color:var(--text-primary); font-family:var(--font-sans); font-size:13px; padding:2px 6px; outline:none; min-width:0; }
        .history-item .btn-options { width:24px; height:24px; display:grid; place-items:center; background:transparent; border:none; border-radius:4px; color:var(--text-muted); cursor:pointer; flex-shrink:0; opacity:0; transition:opacity var(--transition),background var(--transition); }
        .history-item:hover .btn-options, .history-item.active .btn-options { opacity:1; }
        .history-item .btn-options:hover { background:var(--bg-hover); color:var(--text-primary); }

        /* ── CONTEXT MENU ── */
        #context-menu { position:fixed; z-index:9999; background:var(--bg-elevated); border:1px solid var(--border-strong); border-radius:var(--radius-md); box-shadow:var(--shadow-lg); padding:6px; min-width:180px; display:none; animation:menuFadeIn 0.12s ease; }
        #context-menu.open { display:block; }
        @keyframes menuFadeIn { from { opacity:0; transform:scale(0.96) translateY(-4px); } to { opacity:1; transform:none; } }
        .ctx-item { display:flex; align-items:center; gap:10px; padding:9px 12px; border-radius:var(--radius-sm); cursor:pointer; font-size:13px; color:var(--text-secondary); transition:background var(--transition),color var(--transition); border:none; background:transparent; width:100%; font-family:var(--font-sans); text-align:left; }
        .ctx-item:hover { background:var(--bg-hover); color:var(--text-primary); }
        .ctx-item.danger:hover { background:rgba(248,113,113,0.1); color:var(--danger); }
        .ctx-divider { height:1px; background:var(--border); margin:4px 0; }

        /* ── MODAL ── */
        #confirm-modal { position:fixed; inset:0; z-index:99999; background:rgba(0,0,0,0.65); display:none; align-items:center; justify-content:center; backdrop-filter:blur(3px); }
        #confirm-modal.open { display:flex; }
        .modal-box { background:var(--bg-elevated); border:1px solid var(--border-strong); border-radius:var(--radius-lg); padding:28px 28px 24px; max-width:340px; width:90%; box-shadow:var(--shadow-lg); animation:modalIn 0.18s ease; }
        @keyframes modalIn { from { opacity:0; transform:scale(0.94); } to { opacity:1; transform:none; } }
        .modal-title { font-size:16px; font-weight:600; color:var(--text-primary); margin-bottom:8px; }
        .modal-body  { font-size:13.5px; color:var(--text-secondary); margin-bottom:24px; line-height:1.6; }
        .modal-actions { display:flex; gap:10px; justify-content:flex-end; }
        .btn-cancel { padding:8px 18px; background:transparent; border:1px solid var(--border-strong); border-radius:var(--radius-sm); color:var(--text-secondary); font-family:var(--font-sans); font-size:13px; cursor:pointer; transition:all var(--transition); }
        .btn-cancel:hover { background:var(--bg-hover); color:var(--text-primary); }
        .btn-delete-confirm { padding:8px 18px; background:rgba(248,113,113,0.15); border:1px solid rgba(248,113,113,0.3); border-radius:var(--radius-sm); color:var(--danger); font-family:var(--font-sans); font-size:13px; font-weight:500; cursor:pointer; transition:all var(--transition); }
        .btn-delete-confirm:hover { background:rgba(248,113,113,0.25); }

        /* ── PROFILE / SIDEBAR FOOTER ── */
        .sidebar-footer { border-top:1px solid var(--border); padding-top:12px; margin-top:12px; }
        .profile-card { display:flex; align-items:center; gap:10px; padding:8px 10px; border-radius:var(--radius-md); cursor:pointer; transition:background var(--transition); }
        .profile-card:hover { background:var(--bg-hover); }
        .avatar { width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#6c8cff,#a78bfa); display:grid; place-items:center; font-size:13px; font-weight:600; color:white; flex-shrink:0; overflow:hidden; }
        .profile-info { flex:1; overflow:hidden; }
        .profile-name { font-size:13px; font-weight:500; color:var(--text-primary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .profile-role { font-size:11px; color:var(--text-muted); }

        /* ── MAIN AREA (chat + artifact panel) ── */
        #main { flex:1; display:flex; flex-direction:row; overflow:hidden; min-width:0; position:relative; }

        /* ── CHAT COLUMN ── */
        #chat-column { flex:1; display:flex; flex-direction:column; overflow:hidden; min-width:0; transition:flex var(--transition); }

        /* ── TOPBAR ── */
        #topbar { display:none; align-items:center; justify-content:space-between; padding:10px 16px; padding-top:calc(10px + var(--safe-top)); background:var(--bg-base); border-bottom:1px solid var(--border); z-index:50; }
        .topbar-logo { display:flex; align-items:center; gap:8px; font-family:var(--font-display); font-size:15px; font-weight:700; }

        /* ── CHAT WINDOW ── */
        #chat-window { flex:1; overflow-y:auto; padding:32px 20px 12px; display:flex; flex-direction:column; gap:0; -webkit-overflow-scrolling:touch; }

        #welcome { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:40px 20px; gap:16px; color:var(--text-secondary); }
        .welcome-icon { width:56px; height:56px; background:linear-gradient(135deg,#6c8cff,#a78bfa); border-radius:16px; display:grid; place-items:center; font-size:26px; box-shadow:0 0 40px var(--accent-glow); margin-bottom:4px; }
        .welcome-title { font-family:var(--font-display); font-size:22px; font-weight:700; color:var(--text-primary); }
        .welcome-sub { font-size:14px; line-height:1.6; max-width:380px; }
        .suggestion-grid { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:8px; }
        .suggestion-chip { padding:8px 14px; background:var(--bg-elevated); border:1px solid var(--border-strong); border-radius:99px; font-size:12.5px; color:var(--text-secondary); cursor:pointer; transition:all var(--transition); }
        .suggestion-chip:hover { background:var(--bg-hover); color:var(--text-primary); border-color:var(--accent); }

        /* ── MESSAGE ROW ── */
        .msg-row { display:flex; gap:14px; padding:16px 0; max-width:720px; width:100%; margin:0 auto; animation:fadeUp 0.22s ease both; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:none; } }
        .msg-row.user { flex-direction:row-reverse; }
        .msg-avatar { width:32px; height:32px; border-radius:50%; flex-shrink:0; display:grid; place-items:center; font-size:14px; font-weight:600; margin-top:2px; overflow:hidden; }
        .msg-avatar.ai   { background:linear-gradient(135deg,#6c8cff,#a78bfa); color:white; font-size:13px; }
        .msg-avatar.user { background:var(--bg-elevated); border:1px solid var(--border-strong); color:var(--text-secondary); font-size:13px; }
        .msg-body { flex:1; min-width:0; }
        .msg-sender { font-size:12px; font-weight:600; letter-spacing:0.02em; color:var(--text-muted); margin-bottom:6px; }
        .msg-row.user .msg-sender { text-align:right; }
        .msg-content { font-size:14.5px; line-height:1.75; color:var(--text-primary); }
        .msg-row.user .msg-content { background:var(--user-bg); border:1px solid var(--border-strong); border-radius:var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg); padding:12px 16px; display:inline-block; max-width:85%; float:right; clear:both; }

        /* ── MARKDOWN ── */
        .msg-content p { margin-bottom:10px; }
        .msg-content p:last-child { margin-bottom:0; }
        .msg-content ul, .msg-content ol { padding-left:20px; margin-bottom:10px; }
        .msg-content li { margin-bottom:4px; line-height:1.6; }
        .msg-content h1,.msg-content h2,.msg-content h3 { margin:16px 0 8px; font-weight:600; }
        .msg-content h1 { font-size:18px; } .msg-content h2 { font-size:16px; } .msg-content h3 { font-size:14px; }
        .msg-content strong { color:var(--text-primary); font-weight:600; }
        .msg-content em { color:var(--text-secondary); }
        .msg-content a { color:var(--accent); text-decoration:none; }
        .msg-content a:hover { text-decoration:underline; }
        .msg-content blockquote { border-left:3px solid var(--accent); padding-left:12px; color:var(--text-secondary); margin:10px 0; }
        .msg-content hr { border:none; border-top:1px solid var(--border); margin:16px 0; }
        .msg-content code:not(pre code) { font-family:var(--font-mono); font-size:13px; background:var(--bg-elevated); border:1px solid var(--border-strong); padding:2px 6px; border-radius:4px; color:#f87171; }

        /* ── ARTIFACT REFERENCE CHIP (in chat) ── */
        .artifact-chip {
            display: inline-flex; align-items: center; gap: 8px;
            background: var(--bg-elevated); border: 1px solid var(--border-strong);
            border-radius: var(--radius-md); padding: 9px 14px;
            cursor: pointer; transition: all var(--transition); margin: 8px 0;
            font-size: 13px; color: var(--text-secondary);
            max-width: 320px;
        }
        .artifact-chip:hover { background: var(--bg-hover); border-color: var(--accent); color: var(--text-primary); }
        .artifact-chip-icon { width: 28px; height: 28px; border-radius: 7px; display:grid; place-items:center; font-size:13px; flex-shrink:0; }
        .artifact-chip-info { flex:1; min-width:0; }
        .artifact-chip-title { font-size:13px; font-weight:500; color:var(--text-primary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .artifact-chip-meta  { font-size:11px; color:var(--text-muted); margin-top:1px; }
        .artifact-chip-arrow { color:var(--text-muted); flex-shrink:0; }

        /* ── INLINE CODE BLOCK (fallback for non-artifact code) ── */
        .code-block-wrapper { background:var(--code-bg); border:1px solid var(--border-strong); border-radius:var(--radius-md); overflow:hidden; margin:12px 0; }
        .code-block-header { display:flex; align-items:center; justify-content:space-between; background:var(--code-header); padding:8px 14px; border-bottom:1px solid var(--border); }
        .code-lang { font-family:var(--font-mono); font-size:11.5px; font-weight:500; color:var(--text-secondary); letter-spacing:0.05em; text-transform:uppercase; }
        .code-meta { display:flex; align-items:center; gap:8px; }
        .code-lines { font-family:var(--font-mono); font-size:10.5px; color:var(--text-muted); }
        .btn-copy { display:flex; align-items:center; gap:5px; background:transparent; border:1px solid var(--border-strong); border-radius:var(--radius-sm); color:var(--text-secondary); font-family:var(--font-sans); font-size:11.5px; padding:4px 10px; cursor:pointer; transition:all var(--transition); }
        .btn-copy:hover { background:var(--bg-hover); color:var(--text-primary); }
        .btn-copy.copied { color:var(--success); border-color:var(--success); }
        .code-block-wrapper pre { margin:0; padding:16px; overflow-x:auto; max-height:400px; font-family:var(--font-mono); font-size:13px; line-height:1.65; background:transparent !important; }
        .code-block-wrapper code { background:transparent !important; font-size:13px !important; }

        /* ── TYPING DOTS ── */
        .typing-dots { display:flex; gap:5px; align-items:center; padding:8px 0; }
        .typing-dots span { width:7px; height:7px; background:var(--text-muted); border-radius:50%; animation:blink 1.2s infinite; }
        .typing-dots span:nth-child(2) { animation-delay:0.2s; }
        .typing-dots span:nth-child(3) { animation-delay:0.4s; }
        @keyframes blink { 0%,80%,100% { opacity:0.2; } 40% { opacity:1; } }

        /* ── INPUT AREA ── */
        #input-area { padding:0 20px 20px; padding-bottom:calc(20px + var(--safe-bottom)); background:var(--bg-base); position:relative; }
        #input-area::before { content:''; position:absolute; top:-32px; left:0; right:0; height:32px; background:linear-gradient(to bottom,transparent,var(--bg-base)); pointer-events:none; }
        .input-wrapper-outer { max-width:720px; margin:0 auto; }
        .input-box { display:flex; align-items:flex-end; gap:8px; background:var(--bg-elevated); border:1px solid var(--border-strong); border-radius:var(--radius-lg); padding:10px 12px; transition:border-color var(--transition),box-shadow var(--transition); box-shadow:0 4px 24px rgba(0,0,0,0.3); }
        .input-box:focus-within { border-color:rgba(108,140,255,0.4); box-shadow:0 0 0 3px var(--accent-glow),0 4px 24px rgba(0,0,0,0.3); }
        #user-input { flex:1; background:transparent; border:none; outline:none; resize:none; color:var(--text-primary); font-family:var(--font-sans); line-height:1.6; max-height:200px; min-height:26px; overflow-y:auto; padding:2px 0; font-size:max(16px,14.5px); }
        #user-input::placeholder { color:var(--text-muted); }
        .input-actions { display:flex; align-items:center; gap:6px; flex-shrink:0; }
        .btn-attach { width:34px; height:34px; display:grid; place-items:center; background:transparent; border:none; border-radius:var(--radius-sm); color:var(--text-muted); cursor:pointer; transition:color var(--transition),background var(--transition); position:relative; }
        .btn-attach:hover { color:var(--text-secondary); background:var(--bg-hover); }
        .btn-attach input[type=file] { position:absolute; inset:0; opacity:0; cursor:pointer; width:100%; height:100%; }
        #btn-send { width:34px; height:34px; display:grid; place-items:center; background:var(--accent); border:none; border-radius:var(--radius-sm); color:white; cursor:pointer; transition:background var(--transition),transform var(--transition); font-size:15px; flex-shrink:0; }
        #btn-send:hover { background:#5a7aff; transform:scale(1.05); }
        #btn-send:active { transform:scale(0.96); }
        #btn-send:disabled { background:var(--bg-hover); color:var(--text-muted); cursor:not-allowed; transform:none; }
        .input-hint { text-align:center; font-size:11px; color:var(--text-muted); margin-top:10px; }

        /* ── FILE PREVIEW STRIP ── */
        #file-preview-strip { display:none; flex-wrap:wrap; gap:6px; padding:0 0 8px; max-width:720px; margin:0 auto; }
        #file-preview-strip.has-files { display:flex; }
        .file-chip { display:inline-flex; align-items:center; gap:6px; padding:5px 10px; background:var(--bg-elevated); border:1px solid var(--border-strong); border-radius:99px; font-size:12px; color:var(--text-secondary); max-width:200px; }
        .file-chip-name { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex:1; min-width:0; }
        .file-chip-remove { width:14px; height:14px; display:grid; place-items:center; background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:14px; flex-shrink:0; padding:0; line-height:1; }
        .file-chip-remove:hover { color:var(--danger); }

        /* ════════════════════════════════════
           ARTIFACT PANEL
        ════════════════════════════════════ */
        #artifact-panel {
            width: 0;
            min-width: 0;
            background: var(--bg-surface);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: width 0.28s cubic-bezier(0.22,1,0.36,1),
                        min-width 0.28s cubic-bezier(0.22,1,0.36,1),
                        opacity 0.28s ease;
            opacity: 0;
            position: relative;
        }
        #artifact-panel.open {
            width: var(--artifact-w);
            min-width: var(--artifact-w);
            opacity: 1;
        }

        /* Panel header */
        .artifact-header {
            display: flex; align-items: center; gap: 10px;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
            background: var(--bg-surface);
        }
        .artifact-header-icon { width:30px; height:30px; border-radius:8px; display:grid; place-items:center; font-size:14px; flex-shrink:0; }
        .artifact-header-title { flex:1; min-width:0; }
        .artifact-title-text { font-size:13.5px; font-weight:600; color:var(--text-primary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .artifact-title-meta  { font-size:11px; color:var(--text-muted); margin-top:1px; }
        .artifact-header-actions { display:flex; align-items:center; gap:4px; flex-shrink:0; }

        /* Panel tabs */
        .artifact-tabs {
            display: flex; gap: 0;
            border-bottom: 1px solid var(--border);
            padding: 0 16px;
            flex-shrink: 0;
        }
        .artifact-tab {
            padding: 9px 14px;
            font-size: 12.5px; font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: color var(--transition), border-color var(--transition);
            background: transparent; border-top:none; border-left:none; border-right:none;
            font-family: var(--font-sans);
        }
        .artifact-tab:hover { color: var(--text-primary); }
        .artifact-tab.active { color: var(--accent); border-bottom-color: var(--accent); }

        /* Code view */
        #artifact-code-view {
            flex: 1; overflow: auto;
            font-family: var(--font-mono);
            font-size: 13px;
            line-height: 1.65;
            padding: 0;
            background: var(--code-bg);
            position: relative;
        }
        #artifact-code-view pre {
            margin: 0; padding: 20px;
            min-height: 100%;
            background: transparent !important;
        }
        #artifact-code-view code { background: transparent !important; font-size: 13px !important; }

        /* Line numbers */
        .code-line-nums {
            display: inline-block;
            user-select: none;
            color: var(--text-muted);
            text-align: right;
            margin-right: 20px;
            min-width: 32px;
        }

        /* Preview view */
        #artifact-preview-view {
            flex: 1;
            background: #fff;
            display: none;
            position: relative;
        }
        #artifact-preview-view.active { display: flex; flex-direction: column; }
        #preview-iframe {
            flex: 1;
            width: 100%;
            border: none;
            background: #fff;
        }
        .preview-toolbar {
            display: flex; align-items: center; gap: 8px;
            padding: 6px 12px;
            background: var(--bg-elevated);
            border-top: 1px solid var(--border);
            flex-shrink: 0;
        }
        .preview-url-bar {
            flex: 1; padding: 5px 10px;
            background: var(--bg-base); border: 1px solid var(--border-strong);
            border-radius: var(--radius-sm); font-family: var(--font-mono);
            font-size: 11.5px; color: var(--text-secondary);
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .btn-preview-refresh {
            width: 28px; height: 28px; display:grid; place-items:center;
            background: transparent; border: none; border-radius: var(--radius-sm);
            color: var(--text-secondary); cursor: pointer; transition: all var(--transition);
        }
        .btn-preview-refresh:hover { background: var(--bg-hover); color: var(--text-primary); }

        /* Resize handle */
        #artifact-resize {
            position: absolute; left: -4px; top: 0; bottom: 0;
            width: 8px; cursor: col-resize; z-index: 10;
            display: flex; align-items: center; justify-content: center;
        }
        #artifact-resize::after {
            content: ''; width: 2px; height: 40px;
            background: var(--border-strong); border-radius: 2px;
            transition: background var(--transition);
        }
        #artifact-resize:hover::after { background: var(--accent); }

        /* Panel placeholder */
        .artifact-empty {
            flex: 1; display: flex; flex-direction: column; align-items: center;
            justify-content: center; gap: 12px; padding: 40px;
            color: var(--text-muted); text-align: center;
        }
        .artifact-empty-icon { font-size: 32px; opacity: 0.4; }
        .artifact-empty-text { font-size: 13px; line-height: 1.6; max-width: 240px; }

        /* Image result */
        .generated-image-wrap { margin-top:8px; }
        .generated-image-wrap img { width:100%; max-width:480px; border-radius:var(--radius-md); border:1px solid var(--border); display:block; }
        .btn-download { display:inline-flex; align-items:center; gap:6px; margin-top:10px; padding:7px 14px; background:var(--bg-elevated); border:1px solid var(--border-strong); border-radius:var(--radius-sm); color:var(--text-secondary); font-size:12.5px; cursor:pointer; transition:all var(--transition); font-family:var(--font-sans); }
        .btn-download:hover { background:var(--bg-hover); color:var(--text-primary); }

        /* ── OVERLAY ── */
        #overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:99; backdrop-filter:blur(2px); }

        /* ── MOBILE ── */
        @media (max-width: 900px) {
            :root { --artifact-w: 100vw; }
            #artifact-panel {
                position: fixed; top: 0; right: 0; bottom: 0;
                width: 0 !important; min-width: 0 !important;
                z-index: 200; box-shadow: var(--shadow-lg);
            }
            #artifact-panel.open {
                width: 100vw !important; min-width: 100vw !important;
            }
        }
        @media (max-width: 768px) {
            #sidebar { position:fixed; top:0; left:0; bottom:0; transform:translateX(-100%); box-shadow:var(--shadow-lg); }
            #sidebar.open { transform:translateX(0); }
            #overlay.show { display:block; }
            #topbar { display:flex; }
            #chat-window { padding:16px 14px 8px; }
            #input-area { padding:0 12px calc(16px + var(--safe-bottom)); }
            .welcome-title { font-size:19px; }
        }
        @media (min-width: 769px) { #topbar { display:none !important; } }
        @supports (height: 100dvh) { #app, html, body { height: 100dvh; } }
    </style>
</head>
<body>

<!-- ══════════════════════════════════════════════════════
     AUTH PAGE
══════════════════════════════════════════════════════ -->
<div id="auth-page">
    <div class="auth-card">
        <div class="auth-logo">✦</div>
        <div class="auth-title">LOOM AI</div>
        <div class="auth-tagline">Your intelligent assistant for code, ideas, and creativity. Sign in to start.</div>
        <div class="auth-features">
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(108,140,255,0.15)">⚡</div>
                <div class="auth-feature-text"><strong>Instant AI Responses</strong>Powered by Gemini — fast, accurate, and concise.</div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(63,185,80,0.12)">🎨</div>
                <div class="auth-feature-text"><strong>Live Code Artifacts</strong>Code opens in a split panel with instant live preview.</div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(167,139,250,0.12)">🖼️</div>
                <div class="auth-feature-text"><strong>Image Generation</strong>Type <code style="color:var(--accent);font-size:12px">image:</code> to generate visuals on demand.</div>
            </div>
        </div>
        <button id="google-btn" onclick="signInWithGoogle()">
            <svg width="18" height="18" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
            Continue with Google
        </button>
        <div id="auth-error"></div>
        <div class="auth-footer">By continuing, you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>.<br>Built by <strong style="color:var(--text-secondary)">Md Aminul Islam</strong></div>
    </div>
</div>


<!-- ══════════════════════════════════════════════════════
     MAIN APP
══════════════════════════════════════════════════════ -->
<div id="app">

    <aside id="sidebar">
        <div class="sidebar-top">
            <div class="logo-mark"><div class="logo-icon">✦</div>LOOM AI</div>
            <button class="btn-icon" onclick="closeSidebar()">
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
            <div class="profile-card" onclick="handleSignOut()">
                <div class="avatar" id="profile-avatar">U</div>
                <div class="profile-info">
                    <div class="profile-name" id="profile-name">User</div>
                    <div class="profile-role" id="profile-email">Sign out</div>
                </div>
                <button class="btn-icon" style="margin-left:auto">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                </button>
            </div>
        </div>
    </aside>

    <div id="overlay" onclick="closeSidebar()"></div>

    <!-- Context Menu -->
    <div id="context-menu">
        <button class="ctx-item" id="ctx-star" onclick="ctxStar()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span id="ctx-star-label">Star</span>
        </button>
        <button class="ctx-item" onclick="ctxRename()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Rename
        </button>
        <div class="ctx-divider"></div>
        <button class="ctx-item danger" onclick="ctxDelete()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/></svg>
            Delete
        </button>
    </div>

    <!-- Delete Modal -->
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

    <main id="main">

        <!-- ── CHAT COLUMN ── -->
        <div id="chat-column">
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
                    <div class="welcome-sub">Ask me anything — code, ideas, images, or analysis. Code opens as a live artifact.</div>
                    <div class="suggestion-grid">
                        <div class="suggestion-chip" onclick="fillInput('Build a beautiful todo app in HTML/CSS/JS')">Todo app with preview</div>
                        <div class="suggestion-chip" onclick="fillInput('image: futuristic city at night')">Generate an image</div>
                        <div class="suggestion-chip" onclick="fillInput('Write a Flask REST API boilerplate')">Flask API boilerplate</div>
                        <div class="suggestion-chip" onclick="fillInput('Who created you?')">Who made you?</div>
                    </div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-wrapper-outer">
                    <div id="file-preview-strip"></div>
                    <div class="input-box">
                        <button class="btn-attach" title="Attach file">
                            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
                            <input type="file" id="file-input" multiple accept="image/*,.pdf,.txt,.csv,.json,.py,.js,.html,.css" onchange="handleFileAttach(this)">
                        </button>
                        <textarea id="user-input" rows="1" placeholder="Message LOOM AI…"
                            onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
                        <div class="input-actions">
                            <button id="btn-send" onclick="send()">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 2L11 13"/><path d="M22 2L15 22 11 13 2 9l20-7z"/></svg>
                            </button>
                        </div>
                    </div>
                    <div class="input-hint">Enter to send · Shift+Enter for newline · <strong>image:</strong> to generate · 📎 attach files</div>
                </div>
            </div>
        </div>

        <!-- ════════════════════════════════════
             ARTIFACT PANEL
        ════════════════════════════════════ -->
        <div id="artifact-panel">
            <div id="artifact-resize" title="Drag to resize"></div>

            <div class="artifact-header" id="artifact-header">
                <div class="artifact-header-icon" id="artifact-header-icon" style="background:rgba(108,140,255,0.15)">📄</div>
                <div class="artifact-header-title">
                    <div class="artifact-title-text" id="artifact-title-text">Artifact</div>
                    <div class="artifact-title-meta" id="artifact-title-meta">—</div>
                </div>
                <div class="artifact-header-actions">
                    <button class="btn-icon" onclick="copyArtifactCode()" title="Copy code">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                    </button>
                    <button class="btn-icon" onclick="downloadArtifact()" title="Download">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    </button>
                    <button class="btn-icon" onclick="openArtifactInNewTab()" title="Open in new tab">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                    </button>
                    <button class="btn-icon" onclick="closeArtifactPanel()" title="Close">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
                    </button>
                </div>
            </div>

            <div class="artifact-tabs" id="artifact-tabs">
                <button class="artifact-tab active" id="tab-code" onclick="switchArtifactTab('code')">Code</button>
                <button class="artifact-tab" id="tab-preview" onclick="switchArtifactTab('preview')" style="display:none">Preview</button>
            </div>

            <div id="artifact-code-view">
                <pre><code id="artifact-code-el"></code></pre>
            </div>

            <div id="artifact-preview-view">
                <iframe id="preview-iframe" sandbox="allow-scripts allow-same-origin allow-forms" title="Live Preview"></iframe>
                <div class="preview-toolbar">
                    <button class="btn-preview-refresh" onclick="refreshPreview()" title="Refresh">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
                    </button>
                    <div class="preview-url-bar">Live Preview — LOOM AI Artifact</div>
                </div>
            </div>
        </div>

    </main>
</div>


<script>
/* ══════════════════════════════════════════════════════════
   STATE
══════════════════════════════════════════════════════════ */
let currentChatId   = null;
let chats           = JSON.parse(localStorage.getItem('loom_ai_chats') || '{}');
let attachedFiles   = [];
let currentArtifact = null;   // { id, type, title, code, lang }
let artifactStore   = {};     // id → artifact data (for this session)

function saveToLocal() {
    localStorage.setItem('loom_ai_chats', JSON.stringify(chats));
    renderHistory();
}

/* ══════════════════════════════════════════════════════════
   ARTIFACT SYSTEM
══════════════════════════════════════════════════════════ */
const LANG_META = {
    html:   { icon:'🌐', label:'HTML',   ext:'html',  color:'rgba(255,140,50,0.15)'  },
    css:    { icon:'🎨', label:'CSS',    ext:'css',   color:'rgba(100,180,255,0.15)' },
    js:     { icon:'⚡', label:'JS',     ext:'js',    color:'rgba(255,220,50,0.15)'  },
    python: { icon:'🐍', label:'Python', ext:'py',    color:'rgba(60,190,100,0.15)'  },
    text:   { icon:'📄', label:'Text',   ext:'txt',   color:'rgba(150,150,150,0.12)' },
    json:   { icon:'{}', label:'JSON',   ext:'json',  color:'rgba(150,150,150,0.12)' },
};

function getArtifactMeta(type) {
    return LANG_META[type] || LANG_META.text;
}

function openArtifactPanel(artifact) {
    currentArtifact = artifact;
    artifactStore[artifact.id] = artifact;

    const panel   = document.getElementById('artifact-panel');
    const meta    = getArtifactMeta(artifact.type);
    const isWeb   = ['html','css','js'].includes(artifact.type);

    // Header
    document.getElementById('artifact-header-icon').textContent   = meta.icon;
    document.getElementById('artifact-header-icon').style.background = meta.color;
    document.getElementById('artifact-title-text').textContent    = artifact.title || 'Untitled';
    document.getElementById('artifact-title-meta').textContent    = meta.label + ' · ' + countLines(artifact.code) + ' lines';

    // Tabs
    const previewTab = document.getElementById('tab-preview');
    previewTab.style.display = isWeb ? '' : 'none';

    // Code
    const codeEl = document.getElementById('artifact-code-el');
    codeEl.className = 'language-' + (artifact.lang || artifact.type);
    codeEl.textContent = artifact.code;
    hljs.highlightElement(codeEl);

    // Switch to code tab
    switchArtifactTab('code');

    // Open panel
    panel.classList.add('open');

    // Auto-preview for HTML
    if (isWeb) {
        setTimeout(() => {
            switchArtifactTab('preview');
        }, 180);
    }
}

function closeArtifactPanel() {
    document.getElementById('artifact-panel').classList.remove('open');
}

function switchArtifactTab(tab) {
    document.getElementById('tab-code').classList.toggle('active',    tab === 'code');
    document.getElementById('tab-preview').classList.toggle('active', tab === 'preview');
    document.getElementById('artifact-code-view').style.display    = tab === 'code'    ? '' : 'none';
    const pv = document.getElementById('artifact-preview-view');
    pv.style.display = tab === 'preview' ? 'flex' : 'none';
    if (tab === 'preview') loadPreview();
}

function loadPreview() {
    if (!currentArtifact) return;
    const iframe = document.getElementById('preview-iframe');
    const code   = currentArtifact.code;
    const type   = currentArtifact.type;
    let   html   = code;

    if (type === 'css') {
        html = `<!DOCTYPE html><html><head><style>${code}</style></head><body><div class="preview-note" style="padding:20px;font-family:sans-serif;color:#555">CSS applied — add HTML to see full preview.</div></body></html>`;
    } else if (type === 'js') {
        html = `<!DOCTYPE html><html><head></head><body><script>${code}<\/script></body></html>`;
    }
    // html type: render as-is
    const blob = new Blob([html], { type: 'text/html' });
    const url  = URL.createObjectURL(blob);
    iframe.src = url;
}

function refreshPreview() { loadPreview(); }

function copyArtifactCode() {
    if (!currentArtifact) return;
    navigator.clipboard.writeText(currentArtifact.code).then(() => {
        showToast('Code copied!');
    });
}

function downloadArtifact() {
    if (!currentArtifact) return;
    const meta = getArtifactMeta(currentArtifact.type);
    const blob = new Blob([currentArtifact.code], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href     = URL.createObjectURL(blob);
    link.download = (currentArtifact.title || 'artifact').replace(/\\s+/g,'_') + '.' + meta.ext;
    link.click();
}

function openArtifactInNewTab() {
    if (!currentArtifact) return;
    const isWeb = ['html','css','js'].includes(currentArtifact.type);
    if (isWeb) {
        const blob = new Blob([currentArtifact.code], { type: 'text/html' });
        window.open(URL.createObjectURL(blob), '_blank');
    } else {
        const blob = new Blob([currentArtifact.code], { type: 'text/plain' });
        window.open(URL.createObjectURL(blob), '_blank');
    }
}

function countLines(str) { return (str.match(/\\n/g) || []).length + 1; }

/* ─── Parse AI response for artifacts ──────────────────── */
function parseArtifacts(text) {
    // Match <artifact id="..." type="..." title="...">...</artifact>
    const artifactRx = /<artifact\\s+id="([^"]+)"\\s+type="([^"]+)"\\s+title="([^"]*)"[^>]*>([\\s\\S]*?)<\\/artifact>/gi;
    const fenceRx    = /```(\\w+)?\\n([\\s\\S]*?)```/g;

    const artifacts = [];
    let   cleanText = text;

    let m;
    while ((m = artifactRx.exec(text)) !== null) {
        const id    = m[1];
        const type  = m[2].toLowerCase();
        const title = m[3] || 'Code';
        let   inner = m[4].trim();

        // Strip fence inside artifact if present
        const fenceMatch = /```(\\w+)?\\n([\\s\\S]*?)```/.exec(inner);
        const lang  = fenceMatch ? (fenceMatch[1] || type) : type;
        const code  = fenceMatch ? fenceMatch[2].trim() : inner;

        artifacts.push({ id, type, title, lang, code });
        cleanText = cleanText.replace(m[0], `[[ARTIFACT:${id}]]`);
    }

    // Also grab bare code fences if NO artifact tags present (graceful fallback)
    if (artifacts.length === 0) {
        let fIdx = 0;
        while ((m = fenceRx.exec(text)) !== null) {
            fIdx++;
            const lang = (m[1] || 'text').toLowerCase();
            const code = m[2].trim();
            const lineCount = countLines(code);
            if (lineCount >= 8) {  // Only promote large code blocks to artifacts
                const id = `inline-${Date.now()}-${fIdx}`;
                artifacts.push({ id, type: lang, title: lang.toUpperCase() + ' Code', lang, code });
                cleanText = cleanText.replace(m[0], `[[ARTIFACT:${id}]]`);
            }
        }
    }

    return { artifacts, cleanText };
}

/* ─── Build artifact chip HTML ──────────────────────────── */
function buildArtifactChip(artifact) {
    const meta = getArtifactMeta(artifact.type);
    const div  = document.createElement('div');
    div.className = 'artifact-chip';
    div.setAttribute('data-artifact-id', artifact.id);
    div.innerHTML = `
        <div class="artifact-chip-icon" style="background:${meta.color}">${meta.icon}</div>
        <div class="artifact-chip-info">
            <div class="artifact-chip-title">${escHtml(artifact.title)}</div>
            <div class="artifact-chip-meta">${meta.label} · ${countLines(artifact.code)} lines</div>
        </div>
        <svg class="artifact-chip-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>`;
    div.addEventListener('click', () => openArtifactPanel(artifactStore[artifact.id]));
    return div;
}

function escHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ══════════════════════════════════════════════════════════
   CHAT HISTORY
══════════════════════════════════════════════════════════ */
let ctxTargetId = null;

function renderHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = '';
    const sorted = Object.keys(chats).sort((a,b) => {
        if (chats[b].starred && !chats[a].starred) return 1;
        if (chats[a].starred && !chats[b].starred) return -1;
        return b - a;
    });
    sorted.forEach(id => {
        const chat = chats[id];
        const item = document.createElement('div');
        item.className = 'history-item' + (id === currentChatId ? ' active' : '');
        item.dataset.id = id;
        item.innerHTML = `
            <svg class="chat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
            ${chat.starred ? '<span class="star-badge">★</span>' : ''}
            <span class="chat-title" title="${chat.title || 'New Chat'}">${chat.title || 'New Chat'}</span>
            <button class="btn-options" onclick="openContextMenu(event,'${id}')">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/></svg>
            </button>`;
        item.addEventListener('click', e => {
            if (e.target.closest('.btn-options')) return;
            loadChat(id); closeSidebar();
        });
        list.appendChild(item);
    });
}

function openContextMenu(e, id) {
    e.stopPropagation();
    ctxTargetId = id;
    const menu = document.getElementById('context-menu');
    const label = document.getElementById('ctx-star-label');
    const btn   = document.getElementById('ctx-star');
    if (chats[id] && chats[id].starred) {
        label.textContent = 'Unstar';
        btn.querySelector('svg').setAttribute('fill','currentColor');
        btn.style.color = 'var(--star-color)';
    } else {
        label.textContent = 'Star';
        btn.querySelector('svg').setAttribute('fill','none');
        btn.style.color = '';
    }
    const rect = e.currentTarget.getBoundingClientRect();
    let left = rect.right + 6, top = rect.top;
    if (left + 190 > window.innerWidth - 8) left = rect.left - 196;
    if (top  + 180 > window.innerHeight - 8) top = window.innerHeight - 188;
    menu.style.left = left + 'px'; menu.style.top = top + 'px';
    menu.classList.add('open');
}

document.addEventListener('click', e => { if (!e.target.closest('#context-menu') && !e.target.closest('.btn-options')) closeContextMenu(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeContextMenu(); closeModal(); } });
function closeContextMenu() { document.getElementById('context-menu').classList.remove('open'); }

function ctxStar() {
    if (!ctxTargetId || !chats[ctxTargetId]) return;
    chats[ctxTargetId].starred = !chats[ctxTargetId].starred;
    saveToLocal(); closeContextMenu();
}
function ctxRename() {
    if (!ctxTargetId) return;
    closeContextMenu();
    const item = document.querySelector(`.history-item[data-id="${ctxTargetId}"]`);
    if (!item) return;
    const titleSpan = item.querySelector('.chat-title');
    const cur = chats[ctxTargetId].title || 'New Chat';
    const input = document.createElement('input');
    input.className = 'chat-title-input'; input.value = cur;
    titleSpan.replaceWith(input); input.focus(); input.select();
    function commit() { chats[ctxTargetId].title = input.value.trim() || cur; saveToLocal(); }
    input.addEventListener('blur', commit);
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
        if (e.key === 'Escape') { input.value = cur; input.blur(); }
    });
}
function ctxDelete() { closeContextMenu(); document.getElementById('confirm-modal').classList.add('open'); }
function closeModal() { document.getElementById('confirm-modal').classList.remove('open'); }
function confirmDelete() {
    if (!ctxTargetId || !chats[ctxTargetId]) { closeModal(); return; }
    delete chats[ctxTargetId];
    if (currentChatId === ctxTargetId) { currentChatId = null; startNewChat(); }
    saveToLocal(); closeModal(); ctxTargetId = null;
}

/* ══════════════════════════════════════════════════════════
   CHAT LOGIC
══════════════════════════════════════════════════════════ */
function startNewChat() {
    currentChatId = Date.now().toString();
    const win = document.getElementById('chat-window');
    win.innerHTML = ''; win.appendChild(buildWelcome());
    closeArtifactPanel();
    renderHistory(); closeSidebar();
    document.getElementById('user-input').focus();
}

function buildWelcome() {
    const w = document.createElement('div'); w.id = 'welcome';
    w.innerHTML = `
        <div class="welcome-icon">✦</div>
        <div class="welcome-title">Good to see you.</div>
        <div class="welcome-sub">Ask me anything — code, ideas, images, or analysis. Code opens as a live artifact.</div>
        <div class="suggestion-grid">
            <div class="suggestion-chip" onclick="fillInput('Build a beautiful todo app in HTML/CSS/JS')">Todo app with preview</div>
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
    closeArtifactPanel();
    if (chats[id] && chats[id].messages) {
        chats[id].messages.forEach(m => appendMessage(m.role, m.text, m.isImage, false, m.artifacts));
    }
    renderHistory();
}

function fillInput(text) {
    const ta = document.getElementById('user-input');
    ta.value = text; autoResize(ta); ta.focus();
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
function handleSignOut() { if (window._loomAuth && confirm('Sign out?')) window.signOut(); }

/* ── File Attachment ── */
function handleFileAttach(input) {
    const files = Array.from(input.files);
    if (!files.length) return;
    attachedFiles = attachedFiles.concat(files);
    renderFileStrip();
    input.value = '';
}

function renderFileStrip() {
    const strip = document.getElementById('file-preview-strip');
    strip.innerHTML = '';
    if (!attachedFiles.length) { strip.classList.remove('has-files'); return; }
    strip.classList.add('has-files');
    attachedFiles.forEach((f, i) => {
        const chip = document.createElement('div');
        chip.className = 'file-chip';
        chip.innerHTML = `<span class="file-chip-name" title="${f.name}">${f.name}</span><button class="file-chip-remove" onclick="removeFile(${i})">×</button>`;
        strip.appendChild(chip);
    });
}

function removeFile(idx) {
    attachedFiles.splice(idx, 1);
    renderFileStrip();
}

/* ── Send ── */
async function send() {
    const input  = document.getElementById('user-input');
    const text   = input.value.trim();
    const files  = [...attachedFiles];
    if (!text && !files.length) return;
    if (!currentChatId) startNewChat();

    const welcome = document.getElementById('welcome');
    if (welcome) welcome.remove();

    appendMessage('user', text || '[Files attached]');
    input.value = ''; input.style.height = 'auto';
    attachedFiles = []; renderFileStrip();

    const sendBtn = document.getElementById('btn-send');
    sendBtn.disabled = true;

    const typingRow = buildTypingRow();
    document.getElementById('chat-window').appendChild(typingRow);
    scrollBottom();

    try {
        let message = text;
        if (files.length) message += `\\n[${files.length} file(s) attached: ${files.map(f=>f.name).join(', ')}]`;

        const res  = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await res.json();
        typingRow.remove();

        if (data.image) {
            appendMessage('bot', data.image, true);
        } else {
            const { artifacts, cleanText } = parseArtifacts(data.reply);
            appendMessage('bot', cleanText, false, true, artifacts);

            if (artifacts.length > 0) {
                const latest = artifacts[artifacts.length - 1];
                openArtifactPanel(latest);
            }
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

function appendMessage(role, text, isImage=false, save=true, artifacts=[]) {
    const win = document.getElementById('chat-window');
    const row = document.createElement('div');
    row.className = 'msg-row ' + (role === 'user' ? 'user' : 'ai');

    const avatarHtml  = role === 'user'
        ? `<div class="msg-avatar user">U</div>`
        : `<div class="msg-avatar ai">✦</div>`;
    const senderLabel = role === 'user' ? 'You' : 'LOOM AI';

    let contentHtml = '';
    if (isImage) {
        contentHtml = `<div class="generated-image-wrap">
            <img src="${text}" alt="Generated image" loading="lazy">
            <button class="btn-download" onclick="downloadImage('${text}')">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                Download image
            </button></div>`;
    } else {
        // Replace artifact placeholders with chips (they'll be added after)
        const processedText = text.replace(/\\[\\[ARTIFACT:([^\\]]+)\\]\\]/g, (_, id) => {
            return `<span class="artifact-chip-placeholder" data-id="${id}"></span>`;
        });
        contentHtml = renderMarkdown(processedText);
    }

    row.innerHTML = `${avatarHtml}<div class="msg-body"><div class="msg-sender">${senderLabel}</div><div class="msg-content">${contentHtml}</div></div>`;
    win.appendChild(row);

    // Replace placeholders with interactive chips
    if (artifacts && artifacts.length > 0) {
        artifacts.forEach(a => {
            artifactStore[a.id] = a;
            const placeholder = row.querySelector(`.artifact-chip-placeholder[data-id="${a.id}"]`);
            const chip = buildArtifactChip(a);
            if (placeholder) placeholder.replaceWith(chip);
            else row.querySelector('.msg-content').appendChild(chip);
        });
    }

    row.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));
    scrollBottom();

    if (save && currentChatId) {
        if (!chats[currentChatId]) {
            chats[currentChatId] = {
                title: (text || 'Chat').substring(0, 28) + ((text||'').length > 28 ? '…' : ''),
                starred: false, messages: []
            };
        }
        chats[currentChatId].messages.push({ role, text, isImage, artifacts: artifacts || [] });
        saveToLocal();
    }
}

/* ── Markdown renderer ── */
function renderMarkdown(text) {
    const renderer = new marked.Renderer();
    renderer.code = function(code, lang) {
        const language  = (lang || 'plaintext').toLowerCase();
        const lineCount = code.split('\\n').length;
        const escaped   = code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        return `<div class="code-block-wrapper">
            <div class="code-block-header">
                <span class="code-lang">${lang || 'plaintext'}</span>
                <div class="code-meta">
                    <span class="code-lines">${lineCount} lines</span>
                    <button class="btn-copy" onclick="copyCode(this)">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                        Copy
                    </button>
                </div>
            </div>
            <pre><code class="language-${language}">${escaped}</code></pre>
        </div>`;
    };
    marked.use({ renderer });
    return marked.parse(text);
}

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

async function downloadImage(url) {
    try {
        const res = await fetch(url);
        const blob = await res.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'LOOM_AI_Image.png';
        link.click();
    } catch(e) { alert('Download failed!'); }
}

function scrollBottom() {
    const win = document.getElementById('chat-window');
    win.scrollTo({ top: win.scrollHeight, behavior: 'smooth' });
}

/* ── Toast ── */
function showToast(msg) {
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
        position:'fixed', bottom:'90px', left:'50%', transform:'translateX(-50%)',
        background:'var(--bg-elevated)', border:'1px solid var(--border-strong)',
        borderRadius:'99px', padding:'8px 20px', fontSize:'13px',
        color:'var(--text-primary)', zIndex:'99999',
        boxShadow:'var(--shadow-md)', animation:'fadeUp 0.2s ease',
        pointerEvents:'none'
    });
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2000);
}

/* ══════════════════════════════════════════════════════════
   ARTIFACT PANEL RESIZE (drag handle)
══════════════════════════════════════════════════════════ */
(function() {
    const handle = document.getElementById('artifact-resize');
    const panel  = document.getElementById('artifact-panel');
    let   dragging = false, startX = 0, startW = 0;

    handle.addEventListener('mousedown', e => {
        dragging = true;
        startX   = e.clientX;
        startW   = panel.offsetWidth;
        document.body.style.userSelect = 'none';
        document.body.style.cursor = 'col-resize';
    });
    document.addEventListener('mousemove', e => {
        if (!dragging) return;
        const delta = startX - e.clientX;
        const newW  = Math.min(Math.max(startW + delta, 300), window.innerWidth * 0.7);
        panel.style.width    = newW + 'px';
        panel.style.minWidth = newW + 'px';
    });
    document.addEventListener('mouseup', () => {
        if (!dragging) return;
        dragging = false;
        document.body.style.userSelect = '';
        document.body.style.cursor = '';
    });
})();

/* ── INIT ── */
renderHistory();
</script>
</body>
</html>
"""

# ════════════════════════════════════════════════════════════════
# ORIGINAL ROUTES — UNCHANGED
# ════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get("message", "")
    if msg.lower().startswith("image:"):
        return jsonify({"image": generate_image_url(msg)})
    return jsonify({"reply": get_ai_response(msg)})

if __name__ == '__main__':
    app.run(debug=True)
