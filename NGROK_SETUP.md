# Ngrok Setup Guide (for Voice Features)

Ngrok is only needed if you're working on **Vapi voice features**. It gives Vapi a public URL to send webhooks back to your local backend. If you're not touching voice, skip this entirely.

---

## Step 1: Install ngrok

### macOS (Homebrew)

```bash
brew install ngrok
```

### Windows (Chocolatey)

```bash
choco install ngrok
```

### Or download directly

Go to [https://ngrok.com/download](https://ngrok.com/download) and follow the instructions for your OS.

---

## Step 2: Create a free ngrok account

1. Go to [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)
2. Sign up for a free account
3. Copy your **authtoken** from the dashboard: [https://dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)

---

## Step 3: Connect your authtoken

Run this once — it saves your token so you don't have to do it again:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

---

## Step 4: Start the tunnel

Make sure your backend is running on port 8000, then in a **separate terminal**:

```bash
ngrok http 8000
```

You'll see output like this:

```
Forwarding    https://some-random-words.ngrok-free.dev -> http://localhost:8000
```

Copy that `https://______.ngrok-free.dev` URL. That's your ngrok URL.

---

## Step 5: Update the two env files

You need to paste your ngrok URL in **two places**.

### File 1: `backend/.env`

Open `backend/.env` and find this line (near the bottom):

```
VAPI_SERVER_URL=https://old-url-here.ngrok-free.dev
```

Replace it with your URL:

```
VAPI_SERVER_URL=https://your-new-url.ngrok-free.dev
```

### File 2: `frontend/.env`

Open `frontend/.env` and find this line:

```
VITE_VAPI_SERVER_URL=https://old-url-here.ngrok-free.dev
```

Replace it with your URL:

```
VITE_VAPI_SERVER_URL=https://your-new-url.ngrok-free.dev
```

**Both values should be identical** — just the ngrok URL, no trailing slash, no path.

---

## Step 6: Restart your servers

After changing the env files, restart both the backend and frontend so they pick up the new values.

---

## Important notes

- Every time you restart ngrok, you get a **new URL**. You'll need to update both env files again.
- If you pay for ngrok, you can get a **static domain** that doesn't change — look into `ngrok http --domain=your-domain.ngrok-free.dev 8000`.
- **Do not commit your ngrok URL** to git. The `.env` files are already in `.gitignore`.
- The ngrok terminal must stay open while you're developing. If you close it, the tunnel dies.
