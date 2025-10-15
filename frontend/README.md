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

## React Compiler

The React Compiler is not enabled on this template. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
