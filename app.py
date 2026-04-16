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

# ════════════════════════════════════════════════════════════════
# UPGRADED FRONTEND
# ════════════════════════════════════════════════════════════════

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <!-- START OF NEW MOBILE VIEWPORT FIX -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#0e0f11">
    <!-- END OF NEW MOBILE VIEWPORT FIX -->
    <link rel="icon" type="image/png" href="https://i.ibb.co/Lz9f1zY/logo.png">
    <title>LOOM AI</title>

    <!-- FONTS -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">

    <!-- CODE HIGHLIGHTING -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>

    <!-- START OF NEW AUTH LOGIC — Firebase SDK -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
        import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut }
            from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

        // ══════════════════════════════════════════════
        // PLUG IN YOUR FIREBASE CREDENTIALS HERE
  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
  import { 
    getAuth, 
    signInWithPopup, 
    GoogleAuthProvider, 
    onAuthStateChanged, 
    signOut 
  } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

  // ২. আপনার Firebase Credentials
  const firebaseConfig = {
    apiKey: "AIzaSyCa4ILv8tXw7zNeLaXKZMcHdmOcB7fpQsg",
    authDomain: "codecraft-ai-e0c31.firebaseapp.com",
    projectId: "codecraft-ai-e0c31",
    storageBucket: "codecraft-ai-e0c31.firebasestorage.app",
    messagingSenderId: "120391757852",
    appId: "1:120391757852:web:dd52dc1b373d597bd96fd9",
    measurementId: "G-NDH3Y3PWW8"
  };

  // ৩. ইনিশিয়ালাইজেশন
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const provider = new GoogleAuthProvider();

  // ৪. গুগল সাইন-ইন ফাংশন
  window.signInWithGoogle = async () => {
    const btn = document.getElementById('google-btn');
    const errorEl = document.getElementById('auth-error');
    
    if (btn) { btn.disabled = true; btn.textContent = 'Signing in...'; }
    if (errorEl) errorEl.style.display = 'none';

    try {
      // পপআপ ওপেন হবে
      await signInWithPopup(auth, provider);
    } catch (e) {
      console.error("Auth Error:", e);
      if (btn) { 
        btn.disabled = false; 
        btn.innerHTML = 'Continue with Google'; 
      }
      showAuthError(e.code);
    }
  };

  // ৫. সাইন আউট ফাংশন
  window.logOut = async () => {
    try {
      await signOut(auth);
    } catch (e) {
      console.error("Sign Out Error:", e);
    }
  };

  // ৬. অথেন্টিকেশন স্টেট ওয়াচার (অটোমেটিক পেজ সুইচ করবে)
  onAuthStateChanged(auth, (user) => {
    const authPage = document.getElementById('auth-page');
    const appPage = document.getElementById('app');

    if (user) {
      // ইউজার লগইন থাকলে মেইন অ্যাপ দেখাবে
      if (authPage) authPage.style.display = 'none';
      if (appPage) appPage.style.display = 'flex';
      
      // প্রোফাইল তথ্য আপডেট
      updateProfileUI(user);
    } else {
      // লগআউট থাকলে ওয়েলকাম পেজ দেখাবে
      if (authPage) authPage.style.display = 'flex';
      if (appPage) appPage.style.display = 'none';
    }
  });

  function updateProfileUI(user) {
    const nameEl = document.getElementById('profile-name');
    const emailEl = document.getElementById('profile-email');
    const avatarEl = document.getElementById('profile-avatar');

    if (nameEl) nameEl.textContent = user.displayName || 'User';
    if (emailEl) emailEl.textContent = user.email || '';
    if (avatarEl) {
      if (user.photoURL) {
        avatarEl.innerHTML = `<img src="${user.photoURL}" style="width:100%;height:100%;border-radius:50%;object-fit:cover">`;
      } else {
        avatarEl.textContent = (user.displayName || 'U')[0].toUpperCase();
      }
    }
  }

  function showAuthError(code) {
    const map = {
      'auth/popup-closed-by-user': 'Sign-in cancelled.',
      'auth/network-request-failed': 'Network error. Check connection.',
      'auth/popup-blocked': 'Popup blocked. Please allow popups for this site.',
      'auth/operation-not-allowed': 'Google Sign-in not enabled in Firebase console.',
      'auth/unauthorized-domain': 'This domain is not authorized in Firebase console.'
    };
    const el = document.getElementById('auth-error');
    if (el) { 
      el.textContent = map[code] || 'Sign-in failed. Try again.'; 
      el.style.display = 'block'; 
    }
  }
</script>
    <!-- END OF NEW AUTH LOGIC -->

    <style>
        /* ═══════════════════════════════════
           DESIGN TOKENS
        ═══════════════════════════════════ */
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
            --font-display:  'Syne', sans-serif;
            --font-mono:     'DM Mono', monospace;
            --shadow-sm:     0 1px 3px rgba(0,0,0,0.4);
            --shadow-md:     0 4px 16px rgba(0,0,0,0.5);
            --shadow-lg:     0 8px 32px rgba(0,0,0,0.6);
            --transition:    0.18s ease;
            /* Mobile safe areas */
            --safe-bottom:   env(safe-area-inset-bottom, 0px);
            --safe-top:      env(safe-area-inset-top, 0px);
        }

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        html {
            height: 100%;
            /* START OF NEW MOBILE FIX — disable pull-to-refresh */
            overscroll-behavior: none;
            /* END OF NEW MOBILE FIX */
        }

        body {
            height: 100%;
            width: 100%;
            font-family: var(--font-sans);
            background: var(--bg-base);
            color: var(--text-primary);
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
            /* START OF NEW MOBILE FIX — prevent bounce scroll */
            overscroll-behavior: none;
            -webkit-overflow-scrolling: touch;
            /* END OF NEW MOBILE FIX */
        }

        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333844; border-radius: 99px; }
        ::-webkit-scrollbar-thumb:hover { background: #4a5060; }

        /* ═══════════════════════════════════
           START OF NEW AUTH LOGIC — Welcome Page Styles
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
            /* Subtle grid texture */
            background-image:
                linear-gradient(rgba(108,140,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(108,140,255,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
        }

        .auth-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-strong);
            border-radius: 24px;
            padding: 48px 40px 40px;
            max-width: 420px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0;
            box-shadow: 0 0 80px rgba(108,140,255,0.08), var(--shadow-lg);
            animation: authCardIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        }
        @keyframes authCardIn {
            from { opacity: 0; transform: translateY(20px) scale(0.97); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
        }

        .auth-logo {
            width: 64px; height: 64px;
            background: linear-gradient(135deg, #6c8cff 0%, #a78bfa 100%);
            border-radius: 18px;
            display: grid;
            place-items: center;
            font-size: 30px;
            box-shadow: 0 0 48px var(--accent-glow);
            margin-bottom: 24px;
            animation: logoPulse 3s ease-in-out infinite;
        }
        @keyframes logoPulse {
            0%,100% { box-shadow: 0 0 48px var(--accent-glow); }
            50%      { box-shadow: 0 0 72px rgba(108,140,255,0.45); }
        }

        .auth-title {
            font-family: var(--font-display);
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: var(--text-primary);
            margin-bottom: 10px;
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
            background: var(--bg-elevated);
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
            background: #fff;
            border: none;
            border-radius: var(--radius-md);
            color: #1a1a2e;
            font-family: var(--font-sans);
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        #google-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
        #google-btn:active { transform: translateY(0); }
        #google-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

        #auth-error {
            display: none;
            margin-top: 12px;
            font-size: 12.5px;
            color: var(--danger);
            text-align: center;
            padding: 8px 12px;
            background: rgba(248,113,113,0.08);
            border: 1px solid rgba(248,113,113,0.2);
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
        /* END OF NEW AUTH LOGIC — Welcome Page Styles */

        /* ═══════════════════════════════════
           MAIN APP LAYOUT
        ═══════════════════════════════════ */
        #app {
            display: none; /* Hidden until auth confirmed */
            height: 100vh;
            width: 100vw;
            position: relative;
            overflow: hidden;
        }

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
            font-family: var(--font-display);
            font-size: 16px;
            font-weight: 700;
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

        /* START OF NEW SIDEBAR FEATURE — 3-dot History Items */
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
        .history-item .star-badge { color: var(--star-color); font-size: 11px; flex-shrink: 0; line-height: 1; }
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
            transition: opacity var(--transition), background var(--transition), color var(--transition);
        }
        .history-item:hover .btn-options,
        .history-item.active .btn-options { opacity: 1; }
        .history-item .btn-options:hover { background: var(--bg-hover); color: var(--text-primary); }
        /* END OF NEW SIDEBAR FEATURE */

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

        /* ── DELETE CONFIRM MODAL ── */
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

        /* ── PROFILE / SIDEBAR FOOTER ── */
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
            background: linear-gradient(135deg, #6c8cff, #a78bfa);
            display: grid;
            place-items: center;
            font-size: 13px;
            font-weight: 600;
            color: white;
            flex-shrink: 0;
            overflow: hidden;
        }
        .profile-info { flex: 1; overflow: hidden; }
        .profile-name  { font-size: 13px; font-weight: 500; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .profile-role  { font-size: 11px; color: var(--text-muted); }

        /* ── MAIN AREA ── */
        #main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

        #topbar {
            display: none;
            align-items: center;
            justify-content: space-between;
            padding: 10px 16px;
            padding-top: calc(10px + var(--safe-top));
            background: var(--bg-base);
            border-bottom: 1px solid var(--border);
            z-index: 50;
        }
        .topbar-logo { display: flex; align-items: center; gap: 8px; font-family: var(--font-display); font-size: 15px; font-weight: 700; }

        /* ── CHAT WINDOW ── */
        #chat-window {
            flex: 1;
            overflow-y: auto;
            padding: 32px 20px 12px;
            display: flex;
            flex-direction: column;
            gap: 0;
            /* START OF NEW MOBILE FIX — smooth scroll on iOS */
            -webkit-overflow-scrolling: touch;
            /* END OF NEW MOBILE FIX */
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
        .welcome-title { font-family: var(--font-display); font-size: 22px; font-weight: 700; color: var(--text-primary); }
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
            overflow: hidden;
        }
        .msg-avatar.ai   { background: linear-gradient(135deg, #6c8cff 0%, #a78bfa 100%); color: white; font-size: 13px; }
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

        /* START OF NEW CODE BLOCK FEATURE — High-Capacity Zero-Lag Code Blocks */
        .code-block-wrapper {
            background: var(--code-bg);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            overflow: hidden;
            margin: 12px 0;
            /* Contain stacking context */
            contain: layout style;
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
        .code-meta {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .code-lines {
            font-family: var(--font-mono);
            font-size: 10.5px;
            color: var(--text-muted);
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
        .btn-copy:hover  { background: var(--bg-hover); color: var(--text-primary); }
        .btn-copy.copied { color: var(--success); border-color: var(--success); }

        /* PERFORMANCE: max-height + overflow-y stops layout explosion from huge outputs */
        .code-block-wrapper pre {
            margin: 0;
            padding: 16px;
            overflow-x: auto;
            overflow-y: auto;
            max-height: 480px;      /* hard cap — prevents browser freeze */
            font-family: var(--font-mono);
            font-size: 13px;
            line-height: 1.65;
            background: transparent !important;
            /* GPU-accelerated scrolling for large code */
            will-change: scroll-position;
        }
        .code-block-wrapper code { background: transparent !important; font-size: 13px !important; }

        /* Expand button for truncated blocks */
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
        /* END OF NEW CODE BLOCK FEATURE */

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

        /* START OF NEW INPUT BOX FEATURE — Floating Premium Input */
        #input-area {
            padding: 0 20px 20px;
            padding-bottom: calc(20px + var(--safe-bottom));
            background: var(--bg-base);
            /* Gradient fade above input to blend chat into it */
            position: relative;
        }
        #input-area::before {
            content: '';
            position: absolute;
            top: -32px; left: 0; right: 0;
            height: 32px;
            background: linear-gradient(to bottom, transparent, var(--bg-base));
            pointer-events: none;
        }
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
            box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        }
        .input-box:focus-within {
            border-color: rgba(108,140,255,0.4);
            box-shadow: 0 0 0 3px var(--accent-glow), 0 4px 24px rgba(0,0,0,0.3);
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
            /* START OF NEW MOBILE FIX — prevent iOS zoom on focus */
            font-size: max(16px, 14.5px);
            /* END OF NEW MOBILE FIX */
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
        #btn-send:hover    { background: #5a7aff; transform: scale(1.05); }
        #btn-send:active   { transform: scale(0.96); }
        #btn-send:disabled { background: var(--bg-hover); color: var(--text-muted); cursor: not-allowed; transform: none; }
        .input-hint { text-align: center; font-size: 11px; color: var(--text-muted); margin-top: 10px; }
        /* END OF NEW INPUT BOX FEATURE */

        /* ── OVERLAY ── */
        #overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 99; backdrop-filter: blur(2px); }

        /* ── MOBILE RESPONSIVE ── */
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
            #input-area  { padding: 0 12px calc(16px + var(--safe-bottom)); }
            .msg-row  { gap: 10px; }
            .msg-avatar { width: 28px; height: 28px; font-size: 12px; }
            .welcome-title { font-size: 19px; }
            #context-menu { min-width: 160px; }
            .auth-card { padding: 36px 24px 28px; }
            .auth-title { font-size: 26px; }
        }
        @media (min-width: 769px) { #topbar { display: none !important; } }

        /* START OF NEW MOBILE FIX — keyboard-aware layout */
        @supports (height: 100dvh) {
            #app, html, body { height: 100dvh; }
        }
        /* END OF NEW MOBILE FIX */
    </style>
</head>
<body>

<!-- ══════════════════════════════════════════════════════════
     START OF NEW AUTH LOGIC — Welcome / Sign-In Page
══════════════════════════════════════════════════════════ -->
<div id="auth-page">
    <div class="auth-card">
        <div class="auth-logo">✦</div>
        <div class="auth-title">LOOM AI</div>
        <div class="auth-tagline">
            Your intelligent assistant for code, ideas, and creativity.
            Sign in to start a conversation.
        </div>

        <div class="auth-features">
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(108,140,255,0.15)">⚡</div>
                <div class="auth-feature-text">
                    <strong>Instant AI Responses</strong>
                    Powered by Gemini — fast, accurate, and concise.
                </div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(63,185,80,0.12)">🖼️</div>
                <div class="auth-feature-text">
                    <strong>Image Generation</strong>
                    Type <code style="color:var(--accent);font-size:12px">image:</code> to generate visuals on demand.
                </div>
            </div>
            <div class="auth-feature">
                <div class="auth-feature-icon" style="background:rgba(167,139,250,0.12)">💾</div>
                <div class="auth-feature-text">
                    <strong>Persistent History</strong>
                    All your chats are saved locally and easy to revisit.
                </div>
            </div>
        </div>

        <button id="google-btn" onclick="signInWithGoogle()">
            <!-- Google G logo SVG -->
            <svg width="18" height="18" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                <path fill="none" d="M0 0h48v48H0z"/>
            </svg>
            Continue with Google
        </button>

        <div id="auth-error"></div>

        <div class="auth-footer">
            By continuing, you agree to our
            <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.<br>
            Built by <strong style="color:var(--text-secondary)">Md Aminul Islam</strong>
        </div>
    </div>
</div>
<!-- END OF NEW AUTH LOGIC — Welcome / Sign-In Page -->


<!-- ══════════════════════════════════════════════════════════
     MAIN APP (shown only after successful auth)
══════════════════════════════════════════════════════════ -->
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

        <!-- START OF NEW INPUT BOX FEATURE — Premium Floating Input -->
        <div id="input-area">
            <div class="input-wrapper-outer">
                <div class="input-box">
                    <button class="btn-attach" title="Attach file (coming soon)">
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
        <!-- END OF NEW INPUT BOX FEATURE -->

    </main>
</div>

<script>
/* ═══════════════════════════════════════════════════════════
   ORIGINAL CORE STATE — UNCHANGED
═══════════════════════════════════════════════════════════ */
let currentChatId = null;
let chats = JSON.parse(localStorage.getItem('loom_ai_chats')) || {};

function saveToLocal() {
    localStorage.setItem('loom_ai_chats', JSON.stringify(chats));
    renderHistory();
}

/* ═══════════════════════════════════════════════════════════
   START OF NEW AUTH LOGIC — Sign Out Handler
═══════════════════════════════════════════════════════════ */
function handleSignOut() {
    if (window._loomAuth && confirm('Sign out of LOOM AI?')) {
        window.signOut();
    }
}
/* END OF NEW AUTH LOGIC — Sign Out Handler */

/* ═══════════════════════════════════════════════════════════
   START OF NEW SIDEBAR FEATURE — History + 3-dot Menu
═══════════════════════════════════════════════════════════ */
let ctxTargetId = null;

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
            <span class="chat-title" title="${chat.title || 'New Chat'}">${chat.title || 'New Chat'}</span>
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

/* Star / Unstar */
function ctxStar() {
    if (!ctxTargetId || !chats[ctxTargetId]) return;
    chats[ctxTargetId].starred = !chats[ctxTargetId].starred;
    saveToLocal();
    closeContextMenu();
}

/* Rename — inline input */
function ctxRename() {
    if (!ctxTargetId) return;
    closeContextMenu();
    const item = document.querySelector(`.history-item[data-id="${ctxTargetId}"]`);
    if (!item) return;
    const titleSpan   = item.querySelector('.chat-title');
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

/* Add to Project — placeholder for your integration */
function ctxAddToProject() {
    closeContextMenu();
    // ADD TO PROJECT LOGIC HERE — wire to your project system
    console.log('Add to project:', ctxTargetId);
}

/* Delete — confirmation modal */
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
/* END OF NEW SIDEBAR FEATURE */

/* ═══════════════════════════════════════════════════════════
   ORIGINAL CHAT LOGIC — UNCHANGED BEHAVIOUR
═══════════════════════════════════════════════════════════ */
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

/* ORIGINAL SEND — UNCHANGED */
async function send() {
    const input = document.getElementById('user-input');
    const text  = input.value.trim();
    if (!text) return;

    if (!currentChatId) startNewChat();

    const welcome = document.getElementById('welcome');
    if (welcome) welcome.remove();

    appendMessage('user', text);
    input.value = '';
    input.style.height = 'auto';

    const sendBtn   = document.getElementById('btn-send');
    sendBtn.disabled = true;

    const typingRow = buildTypingRow();
    document.getElementById('chat-window').appendChild(typingRow);
    scrollBottom();

    try {
        const res  = await fetch('/chat', {
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

function appendMessage(role, text, isImage = false, save = true) {
    const win = document.getElementById('chat-window');
    const row = document.createElement('div');
    row.className = 'msg-row ' + (role === 'user' ? 'user' : 'ai');

    const avatarHtml  = role === 'user'
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
                title:    text.substring(0, 28) + (text.length > 28 ? '…' : ''),
                starred:  false,
                messages: []
            };
        }
        chats[currentChatId].messages.push({ role, text, isImage });
        saveToLocal();
    }
}

/* START OF NEW CODE BLOCK FEATURE — Premium Renderer with line count + expand */
function renderMarkdown(text) {
    const renderer = new marked.Renderer();

    renderer.code = function(code, lang) {
        const language   = (lang || 'plaintext').toLowerCase();
        const displayLang = lang || 'plaintext';
        const lineCount  = code.split('\\n').length;
        const isTall     = lineCount > 25; // show expand hint if >25 lines

        const escaped = code
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

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
                        <button class="btn-copy" onclick="copyCode(this)">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                            Copy
                        </button>
                    </div>
                </div>
                <pre><code class="language-${language}">${escaped}</code></pre>
                ${expandBtn}
            </div>`;
    };

    marked.use({ renderer });
    return marked.parse(text);
}

/* Toggle code block max-height (expand/collapse) */
function toggleExpandCode(btn) {
    const pre = btn.closest('.code-block-wrapper').querySelector('pre');
    const expanded = pre.style.maxHeight === 'none';
    if (expanded) {
        pre.style.maxHeight = '';
        btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg> Show all lines`;
    } else {
        pre.style.maxHeight = 'none';
        btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"/></svg> Collapse`;
    }
}

/* Copy code button */
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
/* END OF NEW CODE BLOCK FEATURE */

/* ORIGINAL DOWNLOAD — UNCHANGED */
async function downloadImage(url) {
    try {
        const res  = await fetch(url);
        const blob = await res.blob();
        const link = document.createElement('a');
        link.href     = URL.createObjectURL(blob);
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
/* Note: startNewChat() is now triggered after auth confirms user is logged in.
   If auth is not configured, the app page is hidden. To bypass auth during dev,
   you can manually call: document.getElementById('auth-page').style.display='none';
   document.getElementById('app').style.display='flex'; startNewChat(); */
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
