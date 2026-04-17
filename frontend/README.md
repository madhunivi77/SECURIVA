# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

---

## Authentication Flow

This frontend implements secure cookie-based authentication with CSRF protection for communicating with the backend API.

### Architecture Overview

```
Page Load → fetch('/api/status') → Backend
                                      ↓
                            Sets HttpOnly Cookie
                            Returns CSRF Token
                                      ↓
React State: {authToken, csrfToken}
                                      ↓
User Interaction → fetch('/api/chat')
                      ↓
        Browser auto-sends cookie
        + X-CSRF-Token header
                      ↓
                  Backend validates → MCP Tools
```

### 1. Initial Token Acquisition (`src/App.jsx`)

On page load, the app fetches authentication credentials:

```javascript
useEffect(() => {
  fetchStatus();  // Called immediately when component mounts
}, []);

const fetchStatus = () => {
  fetch("http://localhost:8000/api/status", {
    credentials: "include"  // CRITICAL: Allows cookies to be sent/received
  })
    .then((res) => res.json())
    .then((data) => {
      // Backend sets HttpOnly cookie automatically
      setAuthToken(data.token);           // Store for display only
      setCsrfToken(data.csrf_token);      // Store for API requests
      setIsAuthenticated(data.authenticated);
    });
};
```

**What happens:**
1. Frontend makes GET request to `/api/status`
2. Backend generates JWT token and CSRF token
3. Backend sets **HTTP-only cookie** with JWT (browser stores automatically)
4. Backend returns CSRF token in response body
5. Frontend stores CSRF token in React state

### 2. Token Storage Strategy

| Token Type | Storage Method | Accessible to JS? | Purpose |
|------------|----------------|-------------------|---------|
| **JWT Token** | HTTP-only Cookie | ❌ No | Authentication (auto-sent by browser) |
| **CSRF Token** | React State | ✅ Yes | CSRF protection (sent in headers) |

**Why HTTP-only Cookies?**
- Cannot be accessed via `document.cookie` or JavaScript
- Prevents XSS attacks from stealing authentication tokens
- Browser automatically includes cookie in requests to same origin

**Why Store CSRF in State?**
- Needed to include in custom request headers
- Proves the request originated from our frontend
- Prevents CSRF attacks (attackers can't read this token)

### 3. Making Authenticated API Requests (`src/components/ChatBox.jsx`)

When sending messages to the chat API:

```javascript
const response = await fetch("http://localhost:8000/api/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRF-Token": csrfToken,  // CSRF token from state
  },
  credentials: "include",  // Browser auto-sends auth_token cookie
  body: JSON.stringify({
    messages: newMessages,
    model: "gpt-3.5-turbo",
    api: "openai"
  }),
});
```

**Request breakdown:**
1. **`credentials: "include"`** - Browser includes `auth_token` cookie automatically
2. **`X-CSRF-Token` header** - Frontend includes CSRF token manually
3. **Backend validates both** - Checks cookie AND CSRF token before processing

### 4. CSRF Token Flow

```
Initial Request:
  Frontend → /api/status → Backend generates CSRF token
                         → Returns: csrf_token = "abc123..."
                         → Frontend: setCsrfToken("abc123...")

Subsequent Requests:
  Frontend → /api/chat
    Headers: {
      "X-CSRF-Token": "abc123..."  ← From React state
    }
    Cookies: {
      "auth_token": "eyJhbGci..."   ← Automatically sent by browser
    }

  Backend validates:
    ✓ Cookie exists
    ✓ CSRF token matches expected value
    → Processes request
```

### 5. Cookie Management

**The browser handles cookies automatically:**

- **Setting cookies**: When backend sends `Set-Cookie` header, browser stores it
- **Sending cookies**: When `credentials: "include"` is set, browser sends cookie with every request
- **Cross-origin**: Works because both frontend (`localhost:5173`) and backend (`localhost:8000`) use `localhost`

**Important:** The cookie is **never accessed by JavaScript**. It's managed entirely by the browser's cookie storage.

### 6. Security Features Implemented

| Feature | Implementation | Protection Against |
|---------|----------------|-------------------|
| **HTTP-only Cookies** | `httponly=True` on backend | XSS (token theft via JS) |
| **CSRF Tokens** | Required in `X-CSRF-Token` header | CSRF (forged requests) |
| **SameSite Cookie** | `samesite=lax` on backend | CSRF (cross-site requests) |
| **Credentials Mode** | `credentials: "include"` in fetch | Ensures cookies are sent |
| **Token Expiration** | 1-hour JWT expiration | Limits damage from stolen tokens |

### 7. Debugging Authentication

**Check if cookie is set:**
1. Open DevTools → Application → Cookies → `http://localhost:8000`
2. Look for `auth_token` cookie with `HttpOnly` flag

**Check if CSRF token is received:**
```javascript
console.log("CSRF Token:", csrfToken);  // Should show long random string
console.log("All cookies:", document.cookie);  // Will be EMPTY (HttpOnly)
```

**Common issues:**
- **401 Unauthorized**: Cookie not being sent (check `credentials: "include"`)
- **403 Forbidden**: CSRF token mismatch or missing
- **CORS errors**: Backend CORS not configured for `localhost:5173`

### 8. Development vs Production

**Development (`localhost`):**
- Uses HTTP (no TLS)
- `COOKIE_SECURE=False` allows HTTP cookies
- `COOKIE_SAMESITE=lax` allows same-site requests

**Production (HTTPS):**
- Requires HTTPS
- `COOKIE_SECURE=True` enforces HTTPS-only cookies
- `COOKIE_SAMESITE=strict` for maximum security
- Update API URLs to production domain

### 9. React State Management

```javascript
// App.jsx maintains authentication state
const [authToken, setAuthToken] = useState(null);      // For display
const [csrfToken, setCsrfToken] = useState(null);      // For API calls
const [isAuthenticated, setIsAuthenticated] = useState(false);

// Passed down to ChatBox component
<ChatBox authToken={authToken} csrfToken={csrfToken} />
```

**Note:** `authToken` in state is only for displaying in the UI. The actual authentication happens via the HTTP-only cookie that JavaScript cannot access.

---

---

## VAPI Voice Widget

The frontend includes a voice-enabled AI assistant widget powered by [VAPI](https://vapi.ai).

### Component: `VapiVoiceWidget`

**Location:** `src/components/VapiVoiceWidget.jsx`

A full-screen 3D animated voice interface that allows users to interact with the AI assistant using voice.

### Features

- **3D Animated Orb**: WebGL sphere with distortion effects (React Three Fiber)
- **Color-coded States**:
  - Gray (`#71717a`) - Idle
  - Purple (`#8b5cf6`) - Active/Connected
  - Green (`#10b981`) - Listening
  - Indigo (`#6366f1`) - Speaking
- **Audio-reactive**: Orb scale and distortion respond to volume levels
- **Particle Background**: Floating particles for visual depth

### Configuration

**Environment Variables (`.env`):**
```bash
# VAPI public key (from VAPI dashboard)
VITE_VAPI_PUBLIC_KEY=your-public-key

# Backend webhook URL (use ngrok for local dev)
VITE_VAPI_SERVER_URL=https://your-ngrok-url.ngrok-free.dev

# Optional: Pre-configured assistant ID (leave empty for inline config)
# VITE_VAPI_ASSISTANT_ID=
```

### Assistant Configuration

The widget uses an inline (transient) assistant configuration:

```javascript
const assistantConfig = {
  name: 'SECURIVA',
  transcriber: {
    provider: 'deepgram',
    model: 'nova-2',
    language: 'en'
  },
  model: {
    provider: 'custom-llm',
    model: 'gpt-4o-mini',
    url: `${serverUrl}/api/vapi/chat/completions`,
    messages: [{
      role: 'system',
      content: 'You are SECURIVA, a helpful voice assistant...'
    }]
  },
  voice: {
    provider: 'deepgram',
    voiceId: 'asteria'  // Female voice
  },
  firstMessage: 'Hi! How can I help you today?',
  serverUrl: `${serverUrl}/api/vapi/webhook`
};
```

### Available Deepgram Voices

| Voice ID | Gender | Description |
|----------|--------|-------------|
| `asteria` | Female | Natural, friendly |
| `luna` | Female | Warm, conversational |
| `stella` | Female | Professional |
| `athena` | Female | Clear, authoritative |
| `orion` | Male | Deep, professional |
| `arcas` | Male | Friendly, casual |
| `perseus` | Male | Clear, articulate |
| `zeus` | Male | Deep, commanding |

### Usage

```jsx
import VapiVoiceWidget from './components/VapiVoiceWidget';

function App() {
  return (
    <div>
      <VapiVoiceWidget />
    </div>
  );
}
```

### VAPI SDK Events

The widget handles these VAPI events:

| Event | Handler |
|-------|---------|
| `call-start` | Sets connected state, shows listening indicator |
| `call-end` | Resets all states |
| `speech-start` | Shows speaking indicator |
| `speech-end` | Shows listening indicator |
| `volume-level` | Updates orb animation intensity |
| `error` | Displays error message |

### Authentication Flow

If the user is logged in (has `api_key` cookie), it's embedded in the system message:

```javascript
const systemContent = apiKey
  ? `You are SECURIVA... [AUTH:${apiKey}]`
  : 'You are SECURIVA...';
```

The backend extracts this token to authenticate MCP tool access.

### Styling

**CSS:** `src/components/VapiVoiceWidget.css`

The widget is styled as a full-screen overlay with:
- Dark background (`#0a0a0b`)
- Centered orb (400x400px on desktop, 280x280px on mobile)
- Status text below orb (uppercase, letter-spaced)

### Dependencies

```json
{
  "@vapi-ai/web": "^2.x",
  "@react-three/fiber": "^8.x",
  "@react-three/drei": "^9.x",
  "three": "^0.x"
}
```

---

## React Compiler

The React Compiler is not enabled on this template. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
