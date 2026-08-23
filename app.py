import os
import random
from flask import Flask, render_template_string, send_from_directory

app = Flask(__name__)

@app.after_request
def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
    return response

# ════════════════════════════════════════════════════════════════
# BACKEND — NO USER GEMINI KEY IS STORED OR SENT TO THIS SERVER
# ════════════════════════════════════════════════════════════════

def generate_image_url(prompt):
    """Generate an image URL without requiring a Gemini API key."""
    clean_prompt = prompt.replace("image:", "", 1).strip()
    seed = random.randint(0, 999999)
    from urllib.parse import quote
    return (
        "https://pollinations.ai/p/"
        f"{quote(clean_prompt)}?width=1024&height=1024&seed={seed}"
    )

# ════════════════════════════════════════════════════════════════
# UPGRADED FRONTEND
# ════════════════════════════════════════════════════════════════

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#f5f0e8">
    <link rel="icon" type="image/png" href="https://i.ibb.co/Lz9f1zY/logo.png">
    <title>CODECRAFT AI</title>

    <!-- FONTS -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,400;0,600;1,300&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">

    <!-- CODE HIGHLIGHTING -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.min.js"></script>

    <!-- FIREBASE AUTH — UNCHANGED -->
    <script type="module">
        import { initializeApp }
            from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
        import {
            getAuth,
            GoogleAuthProvider,
            signInWithPopup,
            onAuthStateChanged,
            signOut
        } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

        const firebaseConfig = {
            apiKey:            "{{ firebase_api_key }}",
            authDomain:        "{{ firebase_auth_domain }}",
            projectId:         "{{ firebase_project_id }}",
            storageBucket:     "{{ firebase_storage_bucket }}",
            messagingSenderId: "{{ firebase_sender_id }}",
            appId:             "{{ firebase_app_id }}",
            measurementId:     "{{ firebase_measurement_id }}"
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
                if (btn) { btn.disabled = false; btn.innerHTML = googleBtnInnerHTML(); }
                showAuthError(err.code);
            }
        };

        window.signOut = () => signOut(auth);

        onAuthStateChanged(auth, (user) => {
            const authPage = document.getElementById('auth-page');
            const appPage  = document.getElementById('app');

            if (user) {
                window._loomUser = user;
                if (typeof loadChats === 'function') { chats = loadChats(); renderHistory(); }
                if (authPage) authPage.style.display = 'none';
                if (appPage)  appPage.style.display  = 'flex';

                const nameEl   = document.getElementById('profile-name');
                const emailEl  = document.getElementById('profile-email');
                const avatarEl = document.getElementById('profile-avatar');

                if (nameEl)  nameEl.textContent  = user.displayName || 'User';
                if (emailEl) emailEl.textContent  = user.email       || 'Sign out';

                if (avatarEl) {
                    if (user.photoURL) {
                        avatarEl.innerHTML = `<img src="${user.photoURL}"
                            style="width:100%;height:100%;border-radius:50%;object-fit:cover"
                            referrerpolicy="no-referrer">`;
                    } else {
                        avatarEl.textContent = (user.displayName || 'U')[0].toUpperCase();
                    }
                }

                if (typeof startNewChat === 'function') startNewChat();
            } else {
                window._loomUser = null;
                if (authPage) authPage.style.display = 'flex';
                if (appPage)  appPage.style.display  = 'none';
            }
        });

        function googleBtnInnerHTML() {
            return `<svg width="18" height="18" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                <path fill="none" d="M0 0h48v48H0z"/>
            </svg>
            Continue with Google`;
        }

        function showAuthError(code) {
            const messages = {
                'auth/popup-closed-by-user':   'Sign-in cancelled.',
                'auth/network-request-failed': 'Network error. Check your connection.',
                'auth/popup-blocked':          'Popup blocked — please allow popups for this site.',
                'auth/cancelled-popup-request':'Sign-in cancelled.',
                'auth/unauthorized-domain':    'This domain is not authorised in Firebase Console.',
            };
            const el = document.getElementById('auth-error');
            if (el) {
                el.textContent    = messages[code] || `Sign-in failed (${code}). Please try again.`;
                el.style.display  = 'block';
            }
        }
    </script>

    <style>
        /* ═══════════════════════════════════
           DESIGN TOKENS — LIGHT CREAM THEME
        ═══════════════════════════════════ */
        :root {
            --bg-base:       #f5f0e8;
            --bg-surface:    #faf7f2;
            --bg-elevated:   #ffffff;
            --bg-hover:      #ede8df;
            --bg-sidebar:    #f0ebe1;
            --border:        rgba(0,0,0,0.08);
            --border-strong: rgba(0,0,0,0.12);
            --text-primary:  #1a1814;
            --text-secondary:#5a5550;
            --text-muted:    #9a9590;
            --accent:        #2c6e49;
            --accent-2:      #c17f3a;
            --accent-3:      #5b6abf;
            --accent-soft:   rgba(44,110,73,0.08);
            --accent-glow:   rgba(44,110,73,0.15);
            --user-bg:       #2c3e30;
            --user-text:     #e8f0ea;
            --code-bg:       #f8f6f1;
            --code-header:   #edeae3;
            --success:       #2c6e49;
            --danger:        #c0392b;
            --star-color:    #c17f3a;
            --radius-sm:     6px;
            --radius-md:     12px;
            --radius-lg:     18px;
            --radius-xl:     24px;
            --sidebar-w:     272px;
            --font-sans:     'DM Sans', sans-serif;
            --font-display:  'Fraunces', serif;
            --font-mono:     'DM Mono', monospace;
            --shadow-sm:     0 1px 3px rgba(0,0,0,0.06);
            --shadow-md:     0 4px 16px rgba(0,0,0,0.08);
            --shadow-lg:     0 8px 32px rgba(0,0,0,0.10);
            --transition:    0.18s ease;
            --safe-bottom:   env(safe-area-inset-bottom, 0px);
            --safe-top:      env(safe-area-inset-top, 0px);
        }

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        html { height: 100%; overscroll-behavior: none; }

        body {
            height: 100%;
            width: 100%;
            font-family: var(--font-sans);
            background: var(--bg-base);
            color: var(--text-primary);
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
            overscroll-behavior: none;
        }

        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #d4cfc5; border-radius: 99px; }
        ::-webkit-scrollbar-thumb:hover { background: #b8b3a8; }

        /* ═══════════════════════════════════
           AUTH PAGE
        ═══════════════════════════════════ */
        #auth-page {
            position: fixed;
            inset: 0;
            background: var(--bg-base);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 99999;
            padding: 24px;
            background-image: radial-gradient(circle at 20% 80%, rgba(44,110,73,0.06) 0%, transparent 50%),
                              radial-gradient(circle at 80% 20%, rgba(193,127,58,0.06) 0%, transparent 50%);
        }

        .auth-card {
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-xl);
            padding: 48px 40px 40px;
            max-width: 420px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: var(--shadow-lg);
            animation: authCardIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        }
        @keyframes authCardIn {
            from { opacity: 0; transform: translateY(20px) scale(0.97); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
        }

        .auth-logo {
            width: 64px; height: 64px;
            background: var(--user-bg);
            border-radius: 18px;
            display: grid;
            place-items: center;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(44,110,73,0.2);
        }
        .auth-logo svg { width: 32px; height: 32px; }

        .auth-title {
            font-family: var(--font-display);
            font-size: 30px;
            font-weight: 600;
            letter-spacing: -0.5px;
            color: var(--text-primary);
            margin-bottom: 8px;
            text-align: center;
        }

        .auth-tagline {
            font-size: 14px;
            color: var(--text-secondary);
            text-align: center;
            line-height: 1.65;
            max-width: 300px;
            margin-bottom: 32px;
        }

        .auth-features {
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 100%;
            margin-bottom: 32px;
        }

        .auth-feature {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 14px;
            background: var(--bg-base);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
        }
        .auth-feature-icon {
            width: 32px; height: 32px;
            border-radius: 8px;
            display: grid;
            place-items: center;
            font-size: 15px;
            flex-shrink: 0;
        }
        .auth-feature-text { font-size: 13px; color: var(--text-secondary); line-height: 1.4; }
        .auth-feature-text strong { color: var(--text-primary); display: block; font-size: 13px; margin-bottom: 1px; }

        #google-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            padding: 13px 20px;
            background: var(--text-primary);
            border: none;
            border-radius: var(--radius-md);
            color: var(--bg-base);
            font-family: var(--font-sans);
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-sm);
        }
        #google-btn:hover { background: #2d2a26; transform: translateY(-1px); box-shadow: var(--shadow-md); }
        #google-btn:active { transform: translateY(0); }
        #google-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

        #auth-error {
            display: none;
            margin-top: 12px;
            font-size: 12.5px;
            color: var(--danger);
            text-align: center;
            padding: 8px 12px;
            background: rgba(192,57,43,0.06);
            border: 1px solid rgba(192,57,43,0.15);
            border-radius: var(--radius-sm);
            width: 100%;
        }

        .auth-footer {
            margin-top: 20px;
            font-size: 11.5px;
            color: var(--text-muted);
            text-align: center;
            line-height: 1.6;
        }
        .auth-footer a { color: var(--accent); text-decoration: none; }

        /* ═══════════════════════════════════
           MAIN APP
        ═══════════════════════════════════ */
        #app {
            display: none;
            height: 100vh;
            width: 100vw;
            position: relative;
            overflow: hidden;
        }

        /* ── SIDEBAR ── */
        #sidebar {
            width: var(--sidebar-w);
            min-width: var(--sidebar-w);
            background: var(--bg-sidebar);
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
        }

        .logo-icon {
            width: 28px; height: 28px;
            background: var(--user-bg);
            border-radius: 8px;
            display: grid;
            place-items: center;
        }
        .logo-icon svg { width: 14px; height: 14px; }

        .logo-name {
            font-family: var(--font-display);
            font-size: 15px;
            font-weight: 600;
            letter-spacing: -0.2px;
            color: var(--text-primary);
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
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            color: var(--text-secondary);
            font-family: var(--font-sans);
            font-size: 13.5px;
            font-weight: 500;
            cursor: pointer;
            transition: background var(--transition), border-color var(--transition), color var(--transition);
            margin-bottom: 20px;
            box-shadow: var(--shadow-sm);
        }
        .btn-new-chat:hover { background: var(--bg-hover); color: var(--text-primary); border-color: var(--border-strong); }

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
        .history-item.active { background: var(--bg-elevated); color: var(--text-primary); box-shadow: var(--shadow-sm); }
        .history-item .chat-icon { flex-shrink: 0; opacity: 0.4; width: 13px; height: 13px; }
        .history-item .star-badge { color: var(--star-color); font-size: 11px; flex-shrink: 0; }
        .history-item .chat-title { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
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
            transition: opacity var(--transition), background var(--transition);
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
        .ctx-item.danger:hover { background: rgba(192,57,43,0.08); color: var(--danger); }
        .ctx-divider { height: 1px; background: var(--border); margin: 4px 0; }

        /* ── API SETTINGS ── */
        #settings-modal {
            position: fixed; inset: 0; z-index: 100001;
            display: none; align-items: center; justify-content: center;
            background: rgba(20,18,15,.42); backdrop-filter: blur(6px);
            padding: 20px;
        }
        #settings-modal.open { display: flex; }
        .settings-box {
            width: min(520px, 100%); background: var(--bg-elevated);
            border: 1px solid var(--border-strong); border-radius: var(--radius-xl);
            box-shadow: var(--shadow-lg); padding: 28px;
            animation: modalIn .18s ease;
        }
        .settings-title { font-size: 20px; font-weight: 600; margin-bottom: 6px; }
        .settings-subtitle { color: var(--text-secondary); font-size: 13px; line-height: 1.55; margin-bottom: 20px; }
        .settings-label { display:block; font-size:12px; font-weight:600; margin-bottom:7px; }
        .settings-input {
            width:100%; height:44px; border:1px solid var(--border-strong);
            border-radius:10px; padding:0 12px; background:var(--bg-surface);
            color:var(--text-primary); outline:none; font-family:var(--font-mono); font-size:12px;
        }
        .settings-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
        .settings-note {
            margin-top:10px; padding:10px 12px; border-radius:10px;
            background:var(--accent-soft); color:var(--text-secondary);
            font-size:11.5px; line-height:1.5;
        }
        .settings-status { min-height:18px; margin-top:10px; font-size:12px; }
        .settings-actions { display:flex; gap:9px; justify-content:flex-end; margin-top:20px; }
        .btn-settings-save {
            border:0; border-radius:9px; padding:10px 15px; cursor:pointer;
            background:var(--accent); color:white; font-weight:600;
        }
        .btn-settings-clear {
            border:1px solid var(--border-strong); border-radius:9px; padding:10px 15px;
            cursor:pointer; background:transparent; color:var(--text-primary);
        }
        .api-badge {
            display:inline-flex; align-items:center; gap:5px; margin-left:8px;
            font-size:10px; color:var(--success); font-weight:600;
        }

        /* ── MODAL ── */
        #confirm-modal {
            position: fixed;
            inset: 0;
            z-index: 99999;
            background: rgba(0,0,0,0.3);
            display: none;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(4px);
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
            background: rgba(192,57,43,0.1);
            border: 1px solid rgba(192,57,43,0.25);
            border-radius: var(--radius-sm);
            color: var(--danger);
            font-family: var(--font-sans);
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all var(--transition);
        }
        .btn-delete-confirm:hover { background: rgba(192,57,43,0.18); }

        /* ── PROFILE ── */
        .sidebar-footer { border-top: 1px solid var(--border); padding-top: 12px; margin-top: 12px; }
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
            background: var(--user-bg);
            display: grid;
            place-items: center;
            font-size: 13px;
            font-weight: 600;
            color: #e8f0ea;
            flex-shrink: 0;
            overflow: hidden;
        }
        .profile-info { flex: 1; overflow: hidden; }
        .profile-name  { font-size: 13px; font-weight: 500; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .profile-role  { font-size: 11px; color: var(--text-muted); }

        /* ── MAIN AREA ── */
        #main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

        /* ── TOPBAR (header with centered CODECRAFT name) ── */
        #topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            height: 56px;
            padding-top: var(--safe-top);
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            z-index: 50;
        }

        .topbar-center {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 8px;
            pointer-events: none;
        }

        .topbar-logo-icon {
            width: 22px; height: 22px;
            background: var(--user-bg);
            border-radius: 6px;
            display: grid;
            place-items: center;
        }
        .topbar-logo-icon svg { width: 11px; height: 11px; }

        .topbar-name {
            font-family: var(--font-display);
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.2px;
        }

        /* Desktop: always show topbar for brand visibility */
        @media (min-width: 769px) {
            #topbar {
                display: flex !important;
                padding: 0 20px;
            }
            #topbar .btn-icon:first-child { display: none; }
        }

        /* ── CHAT WINDOW ── */
        #chat-window {
            flex: 1;
            overflow-y: auto;
            padding: 32px 20px 12px;
            display: flex;
            flex-direction: column;
            gap: 0;
            -webkit-overflow-scrolling: touch;
        }

        /* ── WELCOME / HOME SCREEN ── */
        #welcome {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 40px 20px;
            gap: 8px;
        }

        .welcome-logo {
            width: 52px; height: 52px;
            background: var(--user-bg);
            border-radius: 16px;
            display: grid;
            place-items: center;
            margin-bottom: 8px;
            box-shadow: 0 4px 20px rgba(44,110,73,0.18);
        }
        .welcome-logo svg { width: 26px; height: 26px; }

        .welcome-title {
            font-family: var(--font-display);
            font-size: 26px;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.3px;
            margin-bottom: 6px;
        }
        .welcome-sub {
            font-size: 14px;
            line-height: 1.65;
            max-width: 380px;
            color: var(--text-secondary);
            margin-bottom: 28px;
        }

        /* ── SUGGESTION CARDS ── */
        .suggestion-cards {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            max-width: 560px;
            width: 100%;
            margin: 0 auto;
        }

        .suggestion-card {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
            padding: 16px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all var(--transition);
            text-align: left;
            box-shadow: var(--shadow-sm);
        }
        .suggestion-card:hover {
            background: var(--bg-hover);
            border-color: rgba(0,0,0,0.18);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .card-icon {
            width: 34px; height: 34px;
            border-radius: 10px;
            display: grid;
            place-items: center;
            font-size: 16px;
            flex-shrink: 0;
        }

        .card-title {
            font-size: 13.5px;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.3;
        }
        .card-sub {
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.5;
        }

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
            width: 30px; height: 30px;
            border-radius: 50%;
            flex-shrink: 0;
            display: grid;
            place-items: center;
            font-size: 12px;
            font-weight: 600;
            margin-top: 2px;
            overflow: hidden;
        }
        .msg-avatar.ai   { background: var(--user-bg); color: #e8f0ea; font-size: 11px; }
        .msg-avatar.user { background: var(--bg-elevated); border: 1px solid var(--border-strong); color: var(--text-secondary); }
        .msg-body { flex: 1; min-width: 0; }
        .msg-sender { font-size: 11.5px; font-weight: 600; letter-spacing: 0.02em; color: var(--text-muted); margin-bottom: 5px; text-transform: uppercase; }
        .msg-row.user .msg-sender { text-align: right; }
        .msg-content { font-size: 14.5px; line-height: 1.75; color: var(--text-primary); }
        .msg-row.user .msg-content {
            background: var(--user-bg);
            color: var(--user-text);
            border-radius: var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg);
            padding: 12px 16px;
            display: inline-block;
            max-width: 85%;
            float: right;
            clear: both;
            font-size: 14.5px;
        }

        /* ── FILE CHIP (attached files shown above input) ── */
        #file-chips-area {
            display: none;
            flex-wrap: wrap;
            gap: 6px;
            padding: 8px 0 4px;
            max-width: 780px;
            margin: 0 auto;
            width: 100%;
        }
        #file-chips-area.has-files { display: flex; }

        .file-chip {
            display: flex;
            align-items: center;
            gap: 7px;
            padding: 5px 10px 5px 8px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: 99px;
            font-size: 12.5px;
            color: var(--text-secondary);
            box-shadow: var(--shadow-sm);
            animation: chipIn 0.18s ease;
        }
        @keyframes chipIn {
            from { opacity: 0; transform: scale(0.9); }
            to   { opacity: 1; transform: scale(1); }
        }
        .chip-icon { font-size: 14px; }
        .chip-name { font-weight: 500; color: var(--text-primary); max-width: 140px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .chip-remove {
            width: 16px; height: 16px;
            display: grid;
            place-items: center;
            background: var(--bg-hover);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            color: var(--text-muted);
            font-size: 10px;
            transition: all var(--transition);
            flex-shrink: 0;
        }
        .chip-remove:hover { background: rgba(192,57,43,0.15); color: var(--danger); }

        /* ── MARKDOWN ── */
        .msg-content p { margin-bottom: 10px; }
        .msg-content p:last-child { margin-bottom: 0; }
        .msg-content ul, .msg-content ol { padding-left: 20px; margin-bottom: 10px; }
        .msg-content li { margin-bottom: 4px; line-height: 1.6; }
        .msg-content h1, .msg-content h2, .msg-content h3 { margin: 16px 0 8px; font-weight: 600; font-family: var(--font-display); }
        .msg-content h1 { font-size: 20px; }
        .msg-content h2 { font-size: 17px; }
        .msg-content h3 { font-size: 15px; }
        .msg-content strong { color: var(--text-primary); font-weight: 600; }
        .msg-content a { color: var(--accent); text-decoration: none; }
        .msg-content a:hover { text-decoration: underline; }
        .msg-content blockquote { border-left: 3px solid var(--accent); padding-left: 12px; color: var(--text-secondary); margin: 10px 0; }
        .msg-content hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
        .msg-content code:not(pre code) {
            font-family: var(--font-mono);
            font-size: 13px;
            background: rgba(44,110,73,0.08);
            border: 1px solid rgba(44,110,73,0.15);
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--accent);
        }
        .msg-content table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13.5px; }
        .msg-content th { background: var(--bg-base); padding: 8px 12px; text-align: left; font-weight: 600; border: 1px solid var(--border-strong); }
        .msg-content td { padding: 8px 12px; border: 1px solid var(--border); }
        .msg-content tr:nth-child(even) td { background: rgba(0,0,0,0.02); }

        /* ── CODE BLOCKS ── */
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
            font-size: 11px;
            font-weight: 500;
            color: var(--text-secondary);
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .code-meta { display: flex; align-items: center; gap: 8px; }
        .code-lines { font-family: var(--font-mono); font-size: 10.5px; color: var(--text-muted); }

        .code-actions { display: flex; gap: 6px; align-items: center; }

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
        .btn-copy:hover  { background: var(--bg-hover); color: var(--text-primary); }
        .btn-copy.copied { color: var(--success); border-color: var(--success); }

        /* Preview button */
        .btn-preview {
            display: flex;
            align-items: center;
            gap: 5px;
            background: rgba(44,110,73,0.08);
            border: 1px solid rgba(44,110,73,0.2);
            border-radius: var(--radius-sm);
            color: var(--accent);
            font-family: var(--font-sans);
            font-size: 11.5px;
            padding: 4px 10px;
            cursor: pointer;
            transition: all var(--transition);
        }
        .btn-preview:hover { background: rgba(44,110,73,0.15); }

        .code-block-wrapper pre {
            margin: 0;
            padding: 16px;
            overflow-x: auto;
            overflow-y: auto;
            max-height: 480px;
            font-family: var(--font-mono);
            font-size: 13px;
            line-height: 1.65;
            background: transparent !important;
        }
        .code-block-wrapper code { background: transparent !important; font-size: 13px !important; }

        .btn-expand-code {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            width: 100%;
            padding: 8px;
            background: var(--code-header);
            border: none;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
            font-family: var(--font-sans);
            font-size: 12px;
            cursor: pointer;
            transition: color var(--transition), background var(--transition);
        }
        .btn-expand-code:hover { color: var(--text-primary); background: var(--bg-hover); }

        /* ── LIVE PREVIEW PANEL ── */
        .preview-panel {
            margin: 8px 0;
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            overflow: hidden;
            animation: fadeUp 0.2s ease;
        }
        .preview-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 14px;
            background: var(--code-header);
            border-bottom: 1px solid var(--border);
        }
        .preview-label {
            display: flex;
            align-items: center;
            gap: 7px;
            font-size: 12px;
            font-weight: 500;
            color: var(--accent);
        }
        .preview-dot { width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: pulse 2s ease infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        .btn-close-preview {
            width: 22px; height: 22px;
            display: grid;
            place-items: center;
            background: transparent;
            border: none;
            border-radius: 4px;
            color: var(--text-muted);
            cursor: pointer;
            transition: all var(--transition);
        }
        .btn-close-preview:hover { background: var(--bg-hover); color: var(--text-primary); }
        .preview-iframe {
            width: 100%;
            height: 360px;
            border: none;
            background: white;
            display: block;
        }

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
        #input-area {
            padding: 0 20px 20px;
            padding-bottom: calc(20px + var(--safe-bottom));
            background: var(--bg-base);
            position: relative;
        }
        #input-area::before {
            content: '';
            position: absolute;
            top: -28px; left: 0; right: 0;
            height: 28px;
            background: linear-gradient(to bottom, transparent, var(--bg-base));
            pointer-events: none;
        }

        .input-wrapper-outer { max-width: 780px; margin: 0 auto; }

        /* Hidden file input */
        #file-input { display: none; }

        .input-box {
            display: flex;
            align-items: flex-end;
            gap: 8px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-xl);
            padding: 10px 10px 10px 14px;
            transition: border-color var(--transition), box-shadow var(--transition);
            box-shadow: 0 2px 12px rgba(0,0,0,0.06), var(--shadow-sm);
        }
        .input-box:focus-within {
            border-color: rgba(44,110,73,0.35);
            box-shadow: 0 0 0 3px var(--accent-glow), 0 2px 12px rgba(0,0,0,0.06);
        }

        #user-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            resize: none;
            color: var(--text-primary);
            font-family: var(--font-sans);
            line-height: 1.6;
            max-height: 200px;
            min-height: 26px;
            overflow-y: auto;
            padding: 3px 0;
            font-size: max(16px, 14.5px);
        }
        #user-input::placeholder { color: var(--text-muted); }

        .input-actions { display: flex; align-items: center; gap: 5px; flex-shrink: 0; }

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

        /* Send button — grey up arrow, clean */
        #btn-send {
            width: 34px; height: 34px;
            display: grid;
            place-items: center;
            background: var(--text-primary);
            border: none;
            border-radius: var(--radius-md);
            color: var(--bg-base);
            cursor: pointer;
            transition: background var(--transition), transform var(--transition);
            flex-shrink: 0;
        }
        #btn-send:hover    { background: #2d2a26; transform: scale(1.05); }
        #btn-send:active   { transform: scale(0.96); }
        #btn-send:disabled { background: var(--bg-hover); color: var(--text-muted); cursor: not-allowed; transform: none; }

        .input-hint { text-align: center; font-size: 11px; color: var(--text-muted); margin-top: 10px; }

        /* ── OVERLAY ── */
        #overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 99; backdrop-filter: blur(2px); }

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
            #topbar .btn-icon:first-child { display: grid !important; }
            #chat-window { padding: 16px 14px 8px; }
            #input-area  { padding: 0 12px calc(16px + var(--safe-bottom)); }
            .msg-row  { gap: 10px; }
            .suggestion-cards { grid-template-columns: 1fr 1fr; }
            .auth-card { padding: 36px 24px 28px; }
        }

        @media (min-width: 769px) {
            #topbar .btn-icon:first-child { display: none; }
        }

        @supports (height: 100dvh) {
            #app, html, body { height: 100dvh; }
        }
    </style>
</head>
<body>

<!-- ══════════════════════════════════════════════════════════
     AUTH PAGE
══════════════════════════════════════════════════════════ -->
<div id="auth-page">
    <div class="auth-card">
        <div class="auth-logo">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 8h4v4H8zM20 8h4v4h-4zM14 14h4v4h-4zM8 20h4v4H8zM20 20h4v4h-4z" fill="#e8f0ea"/>
                <path d="M12 8h8v2h-8zM8 12v8h2v-8zM22 12v8h2v-8zM12 22h8v2h-8z" fill="rgba(232,240,234,0.4)"/>
            </svg>
        </div>
        <div class="auth-title">CODECRAFT AI</div>
        <div class="auth-tagline">
            Your intelligent assistant for code, ideas, and creativity.
            Sign in to start a conversation.
        </div>

        <div class="auth-features">
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(44,110,73,0.1)">⚡</div>
                <div class="auth-feature-text">
                    <strong>Instant AI Responses</strong>
                    Powered by Gemini — fast, accurate, and concise.
                </div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(193,127,58,0.1)">🖼️</div>
                <div class="auth-feature-text">
                    <strong>Image Generation</strong>
                    Type <code style="color:var(--accent);font-size:12px">image:</code> to generate visuals on demand.
                </div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(91,106,191,0.1)">💾</div>
                <div class="auth-feature-text">
                    <strong>Persistent History</strong>
                    All your chats are saved locally and easy to revisit.
                </div>
            </div>
        </div>

        <button id="google-btn" onclick="signInWithGoogle()">
            <svg width="18" height="18" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            </svg>
            Continue with Google
        </button>

        <div id="auth-error"></div>

        <div class="auth-footer">
            By continuing, you agree to our
            <a href="/privacy.html" target="_blank" rel="noopener noreferrer">Privacy Policy</a> and <a href="/terms.html" target="_blank" rel="noopener noreferrer">Terms</a>.<br>
            Built by <strong style="color:var(--text-secondary)">Md Aminul Islam</strong>
        </div>
    </div>
</div>


<!-- ══════════════════════════════════════════════════════════
     MAIN APP
══════════════════════════════════════════════════════════ -->
<div id="app">

    <!-- ── SIDEBAR ── -->
    <aside id="sidebar">
        <div class="sidebar-top">
            <div class="logo-mark">
                <div class="logo-icon">
                    <svg viewBox="0 0 32 32" fill="none">
                        <path d="M8 8h4v4H8zM20 8h4v4h-4zM14 14h4v4h-4zM8 20h4v4H8zM20 20h4v4h-4z" fill="#e8f0ea"/>
                    </svg>
                </div>
                <span class="logo-name">CODECRAFT</span>
            </div>
            <button class="btn-icon" onclick="closeSidebar()" title="Close">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
        </div>

        <button class="btn-new-chat" onclick="startNewChat()">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            New conversation
        </button>

        <div class="sidebar-section-label">Recent</div>
        <div id="history-list"></div>

        <div class="sidebar-footer">
            <button class="btn-new-chat" onclick="openSettings()" style="margin-bottom:10px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-1.41 1.41-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.55V20h-2v-.5a1.7 1.7 0 0 0-1.03-1.55 1.7 1.7 0 0 0-1.88.34l-.06.06-1.41-1.41.06-.06A1.7 1.7 0 0 0 9.45 15a1.7 1.7 0 0 0-1.55-1.03H7v-2h.5A1.7 1.7 0 0 0 9.05 11a1.7 1.7 0 0 0-.34-1.88l-.06-.06 1.41-1.41.06.06A1.7 1.7 0 0 0 11.94 8a1.7 1.7 0 0 0 1.03-1.55V6h2v.5A1.7 1.7 0 0 0 16.52 8a1.7 1.7 0 0 0 1.88-.34l.06-.06 1.41 1.41-.06.06A1.7 1.7 0 0 0 19.53 11a1.7 1.7 0 0 0 1.55 1H21v2h-.5A1.7 1.7 0 0 0 19.4 15z"/></svg>
                API Settings
            </button>
            <div class="profile-card" onclick="handleSignOut()">
                <div class="avatar" id="profile-avatar">U</div>
                <div class="profile-info">
                    <div class="profile-name" id="profile-name">User</div>
                    <div class="profile-role" id="profile-email">Sign out</div>
                </div>
                <button class="btn-icon" style="margin-left:auto" title="Sign out">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
                        <polyline points="16 17 21 12 16 7"/>
                        <line x1="21" y1="12" x2="9" y2="12"/>
                    </svg>
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

    <!-- ── API SETTINGS ── -->
    <div id="settings-modal" onclick="if(event.target===this) closeSettings()">
        <div class="settings-box">
            <div class="settings-title">Gemini API Settings <span id="api-status-badge"></span></div>
            <div class="settings-subtitle">
                Use your own Google Gemini API key. It is stored only in this browser and is sent directly to Google's Gemini API — it is never sent to the CODECRAFT server.
            </div>
            <label class="settings-label" for="gemini-api-key">Gemini API key</label>
            <input id="gemini-api-key" class="settings-input" type="password"
                   placeholder="AIza..." autocomplete="off" spellcheck="false">
            <div class="settings-note">
                ⚠️ Treat your API key like a password. Do not paste it into public screenshots, chat messages, GitHub, or shared computers. API usage and billing are controlled by your own Google AI project.
            </div>
            <div id="settings-status" class="settings-status"></div>
            <div class="settings-actions">
                <button class="btn-settings-clear" onclick="clearApiKey()">Remove key</button>
                <button class="btn-cancel" onclick="closeSettings()">Cancel</button>
                <button class="btn-settings-save" id="save-api-key" onclick="saveApiKey(true)">Save & Test</button>
            </div>
        </div>
    </div>

    <!-- ── MAIN ── -->
    <main id="main">

        <!-- Always-visible topbar with centered CODECRAFT branding -->
        <div id="topbar">
            <button class="btn-icon" onclick="openSidebar()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
            </button>
            <div class="topbar-center">
                <div class="topbar-logo-icon">
                    <svg viewBox="0 0 32 32" fill="none">
                        <path d="M8 8h4v4H8zM20 8h4v4h-4zM14 14h4v4h-4zM8 20h4v4H8zM20 20h4v4h-4z" fill="#e8f0ea"/>
                    </svg>
                </div>
                <span class="topbar-name">CODECRAFT</span>
            </div>
            <button class="btn-icon" onclick="startNewChat()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
            </button>
        </div>

        <div id="chat-window">
            <div id="welcome">
                <div class="welcome-logo">
                    <svg viewBox="0 0 32 32" fill="none">
                        <path d="M8 8h4v4H8zM20 8h4v4h-4zM14 14h4v4h-4zM8 20h4v4H8zM20 20h4v4h-4z" fill="#e8f0ea"/>
                        <path d="M12 8h8v2h-8zM8 12v8h2v-8zM22 12v8h2v-8zM12 22h8v2h-8z" fill="rgba(232,240,234,0.4)"/>
                    </svg>
                </div>
                <div class="welcome-title">How can I help you?</div>
                <div class="welcome-sub">Ask me anything — code, ideas, images, or analysis. I'm CODECRAFT AI.</div>

                <div class="suggestion-cards">
                    <div class="suggestion-card" onclick="fillInput('Help me write a professional email to my team about project delays')">
                        <div class="card-icon" style="background:rgba(44,110,73,0.1)">✍️</div>
                        <div class="card-title">Help me write</div>
                        <div class="card-sub">Emails, docs, reports, and more</div>
                    </div>
                    <div class="suggestion-card" onclick="fillInput('Brainstorm 10 creative ideas for a mobile app for students')">
                        <div class="card-icon" style="background:rgba(193,127,58,0.1)">💡</div>
                        <div class="card-title">Brainstorm ideas</div>
                        <div class="card-sub">Creative thinking and ideation</div>
                    </div>
                    <div class="suggestion-card" onclick="fillInput('Explain how async/await works in JavaScript with examples')">
                        <div class="card-icon" style="background:rgba(91,106,191,0.1)">📖</div>
                        <div class="card-title">Explain a concept</div>
                        <div class="card-sub">Clear, simple explanations</div>
                    </div>
                    <div class="suggestion-card" onclick="fillInput('Make a 30-day plan to learn Python from scratch')">
                        <div class="card-icon" style="background:rgba(192,57,43,0.08)">📋</div>
                        <div class="card-title">Make a plan</div>
                        <div class="card-sub">Step-by-step roadmaps & goals</div>
                    </div>
                </div>
            </div>
        </div>

        <div id="input-area">
            <div class="input-wrapper-outer">
                <!-- File chips shown here when files are attached -->
                <div id="file-chips-area"></div>

                <!-- Hidden file input -->
                <input type="file" id="file-input" multiple accept=".pdf,.txt,.csv,.json,.html,.htm,.css,.js,.mjs,.ts,.xml,.png,.jpg,.jpeg,.webp,.gif,.svg" onchange="handleFileSelect(this)">

                <div class="input-box">
                    <button class="btn-attach" title="Attach file" onclick="document.getElementById('file-input').click()">
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
                    </button>
                    <textarea
                        id="user-input"
                        rows="1"
                        placeholder="Message CODECRAFT AI…"
                        onkeydown="handleKey(event)"
                        oninput="autoResize(this)"
                        onpaste="handlePaste(event)"
                    ></textarea>
                    <div class="input-actions">
                        <button id="btn-send" onclick="send()" title="Send (Enter)">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
                        </button>
                    </div>
                </div>
                <div class="input-hint">Enter to send · Shift+Enter for new line · type <strong>image:</strong> to generate</div>
            </div>
        </div>

    </main>
</div>

<script>
/* ═══════════════════════════════════════════════════════════
   CORE STATE — UNCHANGED
═══════════════════════════════════════════════════════════ */
const CHAT_STORAGE = 'codecraft_ai_chats_v2';
const GEMINI_KEY_STORAGE = 'codecraft_gemini_api_key';

let currentChatId = null;
function storageKey(base) {
    const uid = window._loomUser?.uid || 'guest';
    return `${base}:${uid}`;
}

function loadChats() {
    try { return JSON.parse(localStorage.getItem(storageKey(CHAT_STORAGE)) || '{}'); }
    catch { return {}; }
}

let chats = loadChats();

/* ── Attached files state ── */
let attachedFiles = [];

function saveToLocal() {
    localStorage.setItem(storageKey(CHAT_STORAGE), JSON.stringify(chats));
    renderHistory();
}

/* ─── Sign Out Handler ─────────────────────────────────── */
function handleSignOut() {
    if (window._loomAuth && confirm('Sign out of CODECRAFT AI?')) {
        window.signOut();
    }
}

/* ─── History + 3-dot Context Menu ────────────────────── */
let ctxTargetId = null;

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({
        '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
    })[ch]);
}

function renderHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = '';

    const sorted = Object.keys(chats).sort((a, b) => {
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
            <svg class="chat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
            </svg>
            ${chat.starred ? '<span class="star-badge">★</span>' : ''}
            <span class="chat-title" title="${escapeHtml(chat.title || 'New Chat')}">${escapeHtml(chat.title || 'New Chat')}</span>
            <button class="btn-options" data-id="${id}" onclick="openContextMenu(event, '${id}')" title="Options">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/>
                </svg>
            </button>`;

        item.addEventListener('click', (e) => {
            if (e.target.closest('.btn-options')) return;
            loadChat(id);
            closeSidebar();
        });

        list.appendChild(item);
    });
}

function openContextMenu(e, id) {
    e.stopPropagation();
    ctxTargetId = id;

    const menu        = document.getElementById('context-menu');
    const starLabel   = document.getElementById('ctx-star-label');
    const ctxStarBtn  = document.getElementById('ctx-star');

    if (chats[id] && chats[id].starred) {
        starLabel.textContent = 'Unstar';
        ctxStarBtn.querySelector('svg').setAttribute('fill', 'currentColor');
        ctxStarBtn.style.color = 'var(--star-color)';
    } else {
        starLabel.textContent = 'Star';
        ctxStarBtn.querySelector('svg').setAttribute('fill', 'none');
        ctxStarBtn.style.color = '';
    }

    const rect  = e.currentTarget.getBoundingClientRect();
    const menuW = 190, menuH = 180;
    let left = rect.right + 6;
    let top  = rect.top;
    if (left + menuW > window.innerWidth  - 8) left = rect.left - menuW - 6;
    if (top  + menuH > window.innerHeight - 8) top  = window.innerHeight - menuH - 8;

    menu.style.left = left + 'px';
    menu.style.top  = top  + 'px';
    menu.classList.add('open');
}

document.addEventListener('click',   (e) => {
    if (!e.target.closest('#context-menu') && !e.target.closest('.btn-options')) closeContextMenu();
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { closeContextMenu(); closeModal(); } });

function closeContextMenu() { document.getElementById('context-menu').classList.remove('open'); }

function ctxStar() {
    if (!ctxTargetId || !chats[ctxTargetId]) return;
    chats[ctxTargetId].starred = !chats[ctxTargetId].starred;
    saveToLocal();
    closeContextMenu();
}

function ctxRename() {
    if (!ctxTargetId) return;
    closeContextMenu();
    const item = document.querySelector(`.history-item[data-id="${ctxTargetId}"]`);
    if (!item) return;
    const titleSpan    = item.querySelector('.chat-title');
    const currentTitle = chats[ctxTargetId].title || 'New Chat';
    const input = document.createElement('input');
    input.className = 'chat-title-input';
    input.value = currentTitle;
    titleSpan.replaceWith(input);
    input.focus();
    input.select();

    function commitRename() {
        const newTitle = input.value.trim() || currentTitle;
        chats[ctxTargetId].title = newTitle;
        saveToLocal();
    }
    input.addEventListener('blur',    commitRename);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter')  { e.preventDefault(); input.blur(); }
        if (e.key === 'Escape') { input.value = currentTitle; input.blur(); }
    });
}

function ctxAddToProject() {
    closeContextMenu();
    console.log('Add to project:', ctxTargetId);
}

function ctxDelete()   { closeContextMenu(); document.getElementById('confirm-modal').classList.add('open'); }
function closeModal()  { document.getElementById('confirm-modal').classList.remove('open'); }

function confirmDelete() {
    if (!ctxTargetId || !chats[ctxTargetId]) { closeModal(); return; }
    delete chats[ctxTargetId];
    if (currentChatId === ctxTargetId) { currentChatId = null; startNewChat(); }
    saveToLocal();
    closeModal();
    ctxTargetId = null;
}

/* ─── File Attachment System ──────────────────────────── */
function handleFileSelect(input) {
    const files = Array.from(input.files);
    files.forEach(file => {
        if (!attachedFiles.find(f => f.name === file.name && f.size === file.size)) {
            attachedFiles.push(file);
        }
    });
    renderFileChips();
    // Reset input so same file can be re-attached if removed
    input.value = '';
}

function renderFileChips() {
    const area = document.getElementById('file-chips-area');
    area.innerHTML = '';

    if (attachedFiles.length === 0) {
        area.classList.remove('has-files');
        return;
    }
    area.classList.add('has-files');

    attachedFiles.forEach((file, idx) => {
        const ext  = file.name.split('.').pop().toLowerCase();
        const icon = getFileIcon(ext);
        const chip = document.createElement('div');
        chip.className = 'file-chip';
        chip.innerHTML = `
            <span class="chip-icon">${icon}</span>
            <span class="chip-name">${escapeHtml(file.name)}</span>
            <button class="chip-remove" onclick="removeFile(${idx})" title="Remove">✕</button>`;
        area.appendChild(chip);
    });
}

function getFileIcon(ext) {
    const map = {
        pdf: '📄', doc: '📝', docx: '📝', txt: '📃',
        py: '🐍', js: '🟨', ts: '🔷', html: '🌐', css: '🎨',
        json: '📋', csv: '📊', xlsx: '📊', xls: '📊',
        png: '🖼️', jpg: '🖼️', jpeg: '🖼️', gif: '🖼️', svg: '🖼️',
        zip: '🗜️', tar: '🗜️', gz: '🗜️',
        mp4: '🎬', mp3: '🎵', wav: '🎵',
    };
    return map[ext] || '📎';
}

function removeFile(idx) {
    attachedFiles.splice(idx, 1);
    renderFileChips();
}

/* ─── Chat Logic — UNCHANGED ──────────────────────────── */
function startNewChat() {
    currentChatId = Date.now().toString();
    attachedFiles = [];
    renderFileChips();
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
        <div class="welcome-logo">
            <svg viewBox="0 0 32 32" fill="none">
                <path d="M8 8h4v4H8zM20 8h4v4h-4zM14 14h4v4h-4zM8 20h4v4H8zM20 20h4v4h-4z" fill="#e8f0ea"/>
                <path d="M12 8h8v2h-8zM8 12v8h2v-8zM22 12v8h2v-8zM12 22h8v2h-8z" fill="rgba(232,240,234,0.4)"/>
            </svg>
        </div>
        <div class="welcome-title">How can I help you?</div>
        <div class="welcome-sub">Ask me anything — code, ideas, images, or analysis. I'm CODECRAFT AI.</div>
        <div class="suggestion-cards">
            <div class="suggestion-card" onclick="fillInput('Help me write a professional email to my team about project delays')">
                <div class="card-icon" style="background:rgba(44,110,73,0.1)">✍️</div>
                <div class="card-title">Help me write</div>
                <div class="card-sub">Emails, docs, reports, and more</div>
            </div>
            <div class="suggestion-card" onclick="fillInput('Brainstorm 10 creative ideas for a mobile app for students')">
                <div class="card-icon" style="background:rgba(193,127,58,0.1)">💡</div>
                <div class="card-title">Brainstorm ideas</div>
                <div class="card-sub">Creative thinking and ideation</div>
            </div>
            <div class="suggestion-card" onclick="fillInput('Explain how async/await works in JavaScript with examples')">
                <div class="card-icon" style="background:rgba(91,106,191,0.1)">📖</div>
                <div class="card-title">Explain a concept</div>
                <div class="card-sub">Clear, simple explanations</div>
            </div>
            <div class="suggestion-card" onclick="fillInput('Make a 30-day plan to learn Python from scratch')">
                <div class="card-icon" style="background:rgba(192,57,43,0.08)">📋</div>
                <div class="card-title">Make a plan</div>
                <div class="card-sub">Step-by-step roadmaps & goals</div>
            </div>
        </div>`;
    return w;
}

function loadChat(id) {
    currentChatId = id;
    attachedFiles = [];
    renderFileChips();
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

const GEMINI_MODEL = 'gemini-2.5-flash';
const MAX_FILE_BYTES = 10 * 1024 * 1024;
const MAX_TOTAL_FILE_BYTES = 15 * 1024 * 1024;
const SUPPORTED_FILE_TYPES = new Set([
    'application/pdf','text/plain','text/csv','application/json','text/html','text/css','text/javascript',
    'application/javascript','application/xml','text/xml','image/png','image/jpeg','image/webp','image/gif','image/svg+xml'
]);
const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

const CODECRAFT_SYSTEM_PROMPT = `
You are CODECRAFT AI. Your replies must be clean, professional, and well-structured using markdown.
Be direct and useful. When writing code, provide complete working implementations and never intentionally truncate code.
Do not claim to have executed code or accessed files unless the user actually provided them and the app processed them.
About your creator, only when explicitly asked:
- Name: Md Aminul Islam.
- Role: Full-stack Web Developer & AI Enthusiast.
- Skills: Python, Flask, JavaScript, and AI Integration.
`;

function getApiKey() {
    return (localStorage.getItem(storageKey(GEMINI_KEY_STORAGE)) || '').trim();
}

function updateApiStatus() {
    const badge = document.getElementById('api-status-badge');
    if (!badge) return;
    badge.innerHTML = getApiKey()
        ? '<span class="api-badge">● Key saved</span>'
        : '<span class="api-badge" style="color:var(--danger)">● Key missing</span>';
}

function openSettings() {
    const input = document.getElementById('gemini-api-key');
    if (input) input.value = getApiKey();
    const status = document.getElementById('settings-status');
    if (status) status.textContent = '';
    updateApiStatus();
    document.getElementById('settings-modal').classList.add('open');
    setTimeout(() => input && input.focus(), 50);
}

function closeSettings() {
    document.getElementById('settings-modal').classList.remove('open');
}

function clearApiKey() {
    localStorage.removeItem(storageKey(GEMINI_KEY_STORAGE));
    const input = document.getElementById('gemini-api-key');
    if (input) input.value = '';
    const status = document.getElementById('settings-status');
    if (status) {
        status.textContent = 'API key removed from this browser.';
        status.style.color = 'var(--success)';
    }
    updateApiStatus();
}

async function saveApiKey(test = false) {
    const input = document.getElementById('gemini-api-key');
    const key = (input?.value || '').trim();
    const status = document.getElementById('settings-status');
    const btn = document.getElementById('save-api-key');

    if (!key) {
        if (status) { status.textContent = 'Please enter a Gemini API key.'; status.style.color = 'var(--danger)'; }
        return false;
    }

    localStorage.setItem(storageKey(GEMINI_KEY_STORAGE), key);
    updateApiStatus();

    if (!test) {
        closeSettings();
        return true;
    }

    if (btn) { btn.disabled = true; btn.textContent = 'Testing…'; }
    if (status) { status.textContent = 'Testing your key…'; status.style.color = 'var(--text-secondary)'; }

    try {
        const result = await callGemini([{ role: 'user', text: 'Reply with exactly: API connection successful.' }], key);
        if (!result) throw new Error('Empty response');
        if (status) { status.textContent = '✓ API key works. You can start chatting.'; status.style.color = 'var(--success)'; }
        setTimeout(closeSettings, 700);
        return true;
    } catch (err) {
        localStorage.removeItem(storageKey(GEMINI_KEY_STORAGE));
        updateApiStatus();
        if (status) { status.textContent = '✕ ' + friendlyGeminiError(err); status.style.color = 'var(--danger)'; }
        return false;
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = 'Save & Test'; }
    }
}

function friendlyGeminiError(err) {
    const msg = String(err?.message || err || '');
    if (/401|403|API key|permission|unauthenticated/i.test(msg)) return 'Invalid API key or Gemini API is not enabled.';
    if (/429|quota|rate/i.test(msg)) return 'Quota or rate limit reached for this API key.';
    if (/Failed to fetch|network/i.test(msg)) return 'Network error. Check your internet connection.';
    return msg.slice(0, 220) || 'Gemini request failed.';
}

async function callGemini(contents, key = getApiKey()) {
    if (!key) throw new Error('No Gemini API key. Open API Settings and add your key.');

    const normalized = contents.map(m => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: Array.isArray(m.parts) ? m.parts : [{ text: String(m.text || '') }]
    }));

    const res = await fetch(GEMINI_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-goog-api-key': key
        },
        body: JSON.stringify({
            systemInstruction: { parts: [{ text: CODECRAFT_SYSTEM_PROMPT }] },
            contents: normalized,
            generationConfig: {
                temperature: 0.7,
                maxOutputTokens: 65536,
                thinkingConfig: { thinkingBudget: 2048 }
            }
        })
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        const apiMessage = data?.error?.message || `Gemini API error (${res.status})`;
        throw new Error(apiMessage);
    }

    const parts = data?.candidates?.[0]?.content?.parts || [];
    const text = parts.map(part => part.text || '').join('').trim();
    if (!text) {
        const blockReason = data?.promptFeedback?.blockReason;
        throw new Error(blockReason ? `Gemini blocked this request: ${blockReason}` : 'Gemini returned an empty response.');
    }
    return text;
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const result = String(reader.result || '');
            const comma = result.indexOf(',');
            resolve(comma >= 0 ? result.slice(comma + 1) : result);
        };
        reader.onerror = () => reject(new Error(`Could not read ${file.name}.`));
        reader.readAsDataURL(file);
    });
}

function getFileMime(file) {
    if (file.type) return file.type.toLowerCase();
    const ext = file.name.split('.').pop().toLowerCase();
    const map = {
        pdf:'application/pdf', txt:'text/plain', csv:'text/csv', json:'application/json',
        html:'text/html', htm:'text/html', css:'text/css', js:'text/javascript',
        mjs:'text/javascript', ts:'text/javascript', xml:'application/xml',
        png:'image/png', jpg:'image/jpeg', jpeg:'image/jpeg', webp:'image/webp',
        gif:'image/gif', svg:'image/svg+xml'
    };
    return map[ext] || '';
}

function validateAttachedFiles(files) {
    let total = 0;
    for (const file of files) {
        const mime = getFileMime(file);
        if (!SUPPORTED_FILE_TYPES.has(mime)) {
            throw new Error(`${file.name}: unsupported file type. Use PDF, images, TXT, CSV, JSON, HTML, CSS, XML, or code files.`);
        }
        if (file.size > MAX_FILE_BYTES) {
            throw new Error(`${file.name}: file is too large. Maximum is 10 MB per file.`);
        }
        total += file.size;
    }
    if (total > MAX_TOTAL_FILE_BYTES) {
        throw new Error('Attached files are too large together. Maximum total size is 15 MB per message.');
    }
}

async function buildFileParts(files) {
    validateAttachedFiles(files);
    return Promise.all(files.map(async file => ({
        inlineData: {
            mimeType: getFileMime(file),
            data: await fileToBase64(file)
        }
    })));
}
async function send() {
    const input = document.getElementById('user-input');
    let text = input.value.trim();
    const filesForTurn = [...attachedFiles];
    if (!text && filesForTurn.length === 0) return;

    const key = getApiKey();
    if (!key) {
        openSettings();
        return;
    }

    if (filesForTurn.length > 0) {
        try { validateAttachedFiles(filesForTurn); }
        catch (e) {
            appendMessage('bot', '**File error:** ' + e.message);
            return;
        }
        if (!text) text = 'Please analyse the attached file(s) and explain the important findings.';
    }

    if (!currentChatId) startNewChat();

    const welcome = document.getElementById('welcome');
    if (welcome) welcome.remove();

    const displayText = text + (filesForTurn.length > 0 ? `\n\n📎 ${filesForTurn.length} file(s) attached` : '');
    appendMessage('user', displayText);

    input.value = '';
    input.style.height = 'auto';
    attachedFiles = [];
    renderFileChips();

    const sendBtn = document.getElementById('btn-send');
    sendBtn.disabled = true;

    const typingRow = buildTypingRow();
    document.getElementById('chat-window').appendChild(typingRow);
    scrollBottom();

    try {
        const messages = (chats[currentChatId]?.messages || [])
            .filter(m => !m.isImage)
            .map(m => ({
                role: m.role === 'user' ? 'user' : 'assistant',
                text: String(m.text || '').replace(/\\n\\n📎 [0-9]+ file[(]s[)] attached$/, '')
            }));

        const currentParts = [{ text }];
        if (filesForTurn.length > 0) {
            currentParts.push(...await buildFileParts(filesForTurn));
        }
        messages[messages.length - 1] = { role: 'user', parts: currentParts };
        const reply = await callGemini(messages, key);
        typingRow.remove();
        appendMessage('bot', reply);
    } catch (e) {
        typingRow.remove();
        appendMessage('bot', '**Gemini API error:** ' + friendlyGeminiError(e));
    } finally {
        sendBtn.disabled = false;
        document.getElementById('user-input').focus();
    }
}
function buildTypingRow() {
    const row = document.createElement('div');
    row.className = 'msg-row ai';
    row.innerHTML = `
        <div class="msg-avatar ai">
            <svg width="14" height="14" viewBox="0 0 32 32" fill="none">
                <path d="M8 8h4v4H8zM20 8h4v4h-4zM14 14h4v4h-4zM8 20h4v4H8zM20 20h4v4h-4z" fill="#e8f0ea"/>
            </svg>
        </div>
        <div class="msg-body">
            <div class="msg-sender">CODECRAFT AI</div>
            <div class="msg-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>
        </div>`;
    return row;
}

function appendMessage(role, text, isImage = false, save = true) {
    const win = document.getElementById('chat-window');
    const row = document.createElement('div');
    row.className = 'msg-row ' + (role === 'user' ? 'user' : 'ai');

    const aiAvatarSvg = `<svg width="14" height="14" viewBox="0 0 32 32" fill="none">
        <path d="M8 8h4v4H8zM20 8h4v4h-4zM14 14h4v4h-4zM8 20h4v4H8zM20 20h4v4h-4z" fill="#e8f0ea"/>
    </svg>`;

    const avatarHtml  = role === 'user'
        ? `<div class="msg-avatar user">U</div>`
        : `<div class="msg-avatar ai">${aiAvatarSvg}</div>`;
    const senderLabel = role === 'user' ? 'You' : 'CODECRAFT AI';

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
                title:    text.substring(0, 28) + (text.length > 28 ? '…' : ''),
                starred:  false,
                messages: []
            };
        }
        chats[currentChatId].messages.push({ role, text, isImage });
        saveToLocal();
    }
}

/* ── renderMarkdown — with live preview support ── */
function renderMarkdown(text) {
    const renderer = new marked.Renderer();

    renderer.code = function(code, lang) {
        const language    = (lang || 'plaintext').toLowerCase();
        const displayLang = lang || 'plaintext';
        const lineCount   = code.split('\\n').length;
        const isTall      = lineCount > 25;

        // Detect if previewable (html / css+js / svg)
        const isPreviewable = ['html', 'svg'].includes(language) ||
            (language === 'javascript' && code.includes('<')) ;

        const escaped = code
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Store code in a data attribute for preview retrieval (base64 to avoid escaping issues)
        const encoded = btoa(unescape(encodeURIComponent(code)));

        const previewBtn = isPreviewable ? `
            <button class="btn-preview" onclick="showPreview(this)" data-code="${encoded}" data-lang="${language}">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                Preview
            </button>` : '';

        const expandBtn = isTall ? `
            <button class="btn-expand-code" onclick="toggleExpandCode(this)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
                Show all ${lineCount} lines
            </button>` : '';

        return `
            <div class="code-block-wrapper">
                <div class="code-block-header">
                    <span class="code-lang">${displayLang}</span>
                    <div class="code-meta">
                        <span class="code-lines">${lineCount} lines</span>
                        <div class="code-actions">
                            ${previewBtn}
                            <button class="btn-copy" onclick="copyCode(this)">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                                Copy
                            </button>
                        </div>
                    </div>
                </div>
                <pre><code class="language-${language}">${escaped}</code></pre>
                ${expandBtn}
            </div>`;
    };

    marked.use({ renderer });
    const rendered = marked.parse(text);
    return window.DOMPurify ? DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } }) : rendered;
}

/* ── Live Preview ── */
function showPreview(btn) {
    const wrapper = btn.closest('.code-block-wrapper');
    // Remove existing preview if toggling
    const existing = wrapper.nextElementSibling;
    if (existing && existing.classList.contains('preview-panel')) {
        existing.remove();
        return;
    }

    const encoded = btn.dataset.code;
    const lang    = btn.dataset.lang;
    let code;
    try {
        code = decodeURIComponent(escape(atob(encoded)));
    } catch(e) {
        code = '';
    }

    // Build iframe content
    let iframeContent = code;
    if (lang === 'svg') {
        iframeContent = `<!DOCTYPE html><html><body style="margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#fff">${code}</body></html>`;
    } else if (!code.includes('<!DOCTYPE') && !code.includes('<html')) {
        iframeContent = `<!DOCTYPE html><html><head><style>body{font-family:sans-serif;padding:16px;margin:0}</style></head><body>${code}</body></html>`;
    }

    const panel = document.createElement('div');
    panel.className = 'preview-panel';
    panel.innerHTML = `
        <div class="preview-header">
            <div class="preview-label">
                <div class="preview-dot"></div>
                Live Preview
            </div>
            <button class="btn-close-preview" onclick="this.closest('.preview-panel').remove()" title="Close preview">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
        </div>
        <iframe class="preview-iframe" sandbox="allow-scripts allow-same-origin"></iframe>`;

    wrapper.insertAdjacentElement('afterend', panel);

    const iframe = panel.querySelector('iframe');
    iframe.srcdoc = iframeContent;

    scrollBottom();
}

function toggleExpandCode(btn) {
    const pre      = btn.closest('.code-block-wrapper').querySelector('pre');
    const expanded = pre.style.maxHeight === 'none';
    if (expanded) {
        pre.style.maxHeight = '';
        btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg> Show all lines`;
    } else {
        pre.style.maxHeight = 'none';
        btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"/></svg> Collapse`;
    }
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
        const res  = await fetch(url);
        const blob = await res.blob();
        const link = document.createElement('a');
        link.href     = URL.createObjectURL(blob);
        link.download = "CODECRAFT_AI_Image.png";
        link.click();
    } catch(e) { alert("Download failed!"); }
}

function scrollBottom() {
    const win = document.getElementById('chat-window');
    win.scrollTo({ top: win.scrollHeight, behavior: 'smooth' });
}

/* ── INIT ── */
renderHistory();
updateApiStatus();
</script>
</body>
</html>
"""

# ════════════════════════════════════════════════════════════════
# ORIGINAL ROUTES — UNCHANGED
# ════════════════════════════════════════════════════════════════

@app.route('/privacy.html')
def privacy():
    return send_from_directory(os.path.dirname(__file__), 'privacy.html')

@app.route('/terms.html')
def terms():
    return send_from_directory(os.path.dirname(__file__), 'terms.html')

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        firebase_api_key=os.environ.get('FIREBASE_API_KEY', 'AIzaSyCa4ILv8tXw7zNeLaXKZMcHdmOcB7fpQsg'),
        firebase_auth_domain=os.environ.get('FIREBASE_AUTH_DOMAIN', 'codecraft-ai-e0c31.firebaseapp.com'),
        firebase_project_id=os.environ.get('FIREBASE_PROJECT_ID', 'codecraft-ai-e0c31'),
        firebase_storage_bucket=os.environ.get('FIREBASE_STORAGE_BUCKET', 'codecraft-ai-e0c31.firebasestorage.app'),
        firebase_sender_id=os.environ.get('FIREBASE_SENDER_ID', '120391757852'),
        firebase_app_id=os.environ.get('FIREBASE_APP_ID', '1:120391757852:web:dd52dc1b373d597bd96fd9'),
        firebase_measurement_id=os.environ.get('FIREBASE_MEASUREMENT_ID', 'G-NDH3Y3PWW8'),
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')), debug=False)
