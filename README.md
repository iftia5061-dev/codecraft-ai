# CODECRAFT AI

CodeCraft AI is a browser-first AI assistant distributed as a Flask/Vercel app. Users sign in with Google and provide their **own Gemini API key**.

## Architecture

- Flask serves the application UI and static policy pages.
- Firebase Authentication handles Google sign-in.
- Gemini requests are made directly from the browser to Google's Gemini API.
- The CodeCraft Flask/Vercel server does **not** receive the user's Gemini API key or chat/file payloads.
- Gemini API keys and local chat history are stored in browser `localStorage`, namespaced by Firebase user ID.
- Image generation uses the existing Pollinations URL flow.

## AI API key

Open **API Settings**, paste the user's own Gemini API key, and choose **Save & Test**. The key is stored locally in that browser and sent directly to Gemini when an AI request is made.

Users are responsible for their own Gemini project, quota, billing, and key security. Never hard-code a private key into this repository.

## File analysis

The app sends the actual attached file data to Gemini using inline file parts. Supported formats include:

- PDF
- PNG/JPEG/WEBP/GIF/SVG images
- TXT
- CSV
- JSON
- HTML
- CSS
- JavaScript/TypeScript
- XML

Limits are intentionally conservative: **10 MB per file** and **15 MB total per message** to avoid oversized browser requests. Unsupported files are rejected before upload.

## Local run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open the local Flask URL, sign in with Google, and configure the Gemini API key.

## Vercel deployment

The included `vercel.json` uses the Flask app as the Python entry point. Configure the Firebase Authentication authorized domain in Firebase Console for the deployed domain.

## Firebase

The current repository contains the original Firebase web configuration. Firebase web config values are client-visible, but the Firebase project owner must control authorized domains, authentication providers, and any backend security rules.

If this is being distributed as a commercial product, use a Firebase project owned and controlled by the product operator rather than someone else's project.

## Security notes

- API keys are not sent to the CodeCraft Flask backend.
- Do not use shared/public computers for private API keys.
- Browser storage is not a hardware security module; an XSS vulnerability could expose stored credentials, so keep dependencies and frontend rendering secure.
- AI output is untrusted content. Markdown is sanitized before rendering.
- Code previews run inside a sandboxed iframe.
- Do not upload confidential information unless you are authorized to send it to the Google AI service associated with the user's key.

## Included pages

- `/` — CodeCraft AI
- `/privacy.html` — Privacy Policy
- `/terms.html` — Terms of Use

## Pre-release checklist

1. Replace the Firebase project with the product owner's Firebase project if the existing project is not yours.
2. Add the production domain to Firebase Authentication authorized domains.
3. Configure Google Sign-In in Firebase.
4. Test a real Gemini key with chat and file analysis.
5. Test invalid-key, quota, network, and unsupported-file errors.
6. Test mobile and desktop layouts.
7. Confirm no private API key exists in source, Git history, or deployment settings.
8. Review Google Gemini terms, pricing, quotas, and key restrictions before selling access.
