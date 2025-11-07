## How to Run Backend
- install uv (using uv for the project)
- will install all libraries
` uv sync `
- start the server
`python run.py (or uv run.py)`
- start the agent
` code uv run --active my_app/client/agent.py `

---

## Authentication System

This backend implements a secure JWT-based authentication system with CSRF protection and HTTP-only cookies.

### Architecture Overview

```
Frontend → /api/status → Auth Server (/auth/token) → JWT Generation
                      ↓
                   API Server
                      ↓
              Sets HttpOnly Cookie + CSRF Token
                      ↓
Frontend → /api/chat (with cookie + CSRF header) → Validation → MCP Tools
```

### 1. JWT Token Generation (`my_app/auth_server/main.py`)

The **Auth Server** generates JWT tokens with the following claims:

```python
payload = {
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),  # Expires in 1 hour
    'iat': datetime.datetime.now(datetime.timezone.utc),  # Issued at
    'sub': 'test-user',           # Subject (user identifier)
    'client_id': 'test-client'    # Custom claim for client ID
}
```

**Endpoint:** `POST /auth/token`
**Response:** `{"access_token": "eyJhbGci...", "token_type": "Bearer"}`

### 2. Token Distribution Flow (`my_app/server/app.py`)

When the frontend calls `/api/status`, the API server:

1. **Fetches a JWT token** from the auth server internally:
   ```python
   response = await client.post("http://localhost:8000/auth/token")
   token = response.json()["access_token"]
   ```

2. **Generates a CSRF token** for additional security:
   ```python
   csrf_token = secrets.token_urlsafe(32)
   csrf_tokens[token] = csrf_token  # Store mapping
   ```

3. **Sets an HTTP-only cookie** with the JWT token:
   ```python
   response.set_cookie(
       key="auth_token",
       value=token,
       httponly=True,        # Cannot be accessed by JavaScript (XSS protection)
       secure=COOKIE_SECURE, # Only sent over HTTPS in production
       samesite=COOKIE_SAMESITE,  # CSRF protection
       max_age=3600          # 1 hour expiration
   )
   ```

4. **Returns the CSRF token** in the response body (frontend needs this for API calls):
   ```json
   {
     "status": "ok",
     "token": "eyJhbGci...",
     "authenticated": true,
     "csrf_token": "SZ2G6SbRy-PE0tnkK4ujd0kx2sTP3IYnSPJxg910mFA"
   }
   ```

### 3. Request Validation (`/api/chat` endpoint)

When the frontend makes authenticated API calls, the server validates:

1. **Cookie presence** - Extracts JWT from `auth_token` cookie:
   ```python
   auth_token = request.cookies.get("auth_token")
   ```

2. **CSRF token validation** - Checks `X-CSRF-Token` header:
   ```python
   csrf_token = request.headers.get("X-CSRF-Token")
   expected_csrf = csrf_tokens.get(auth_token)

   if expected_csrf != csrf_token:
       return JSONResponse({"error": "Invalid CSRF token"}, status_code=403)
   ```

3. **Proceeds with request** if both validations pass.

### 4. Security Configuration (`.env`)

```bash
# Security settings
ENVIRONMENT="development"           # Set to "production" for HTTPS
COOKIE_SECURE="False"               # Auto-set to True in production
COOKIE_SAMESITE="lax"              # "strict" for stronger CSRF protection

# JWT Secret
JWT_SECRET_KEY="your-secret-key"   # Used to sign JWT tokens

# Tool Logging
ENABLE_TOOL_LOGGING="true"         # Log all MCP tool calls
```

### 5. Security Features

| Feature | Description | Attack Prevention |
|---------|-------------|-------------------|
| **HTTP-only Cookies** | JWT stored in cookies inaccessible to JavaScript | XSS attacks |
| **CSRF Tokens** | Unique token required in request headers | CSRF attacks |
| **SameSite Attribute** | Cookie only sent from same-origin requests | CSRF attacks |
| **Secure Flag** | Cookies only sent over HTTPS (production) | Man-in-the-middle |
| **Token Expiration** | Tokens expire after 1 hour | Token replay attacks |

### 6. Production Deployment Checklist

Before deploying to production:

- [ ] Set `ENVIRONMENT="production"` in `.env`
- [ ] Use HTTPS (required for `Secure` cookies)
- [ ] Set `COOKIE_SAMESITE="strict"` for maximum CSRF protection
- [ ] Use a strong, randomly generated `JWT_SECRET_KEY`
- [ ] Replace in-memory `csrf_tokens` dict with Redis/database
- [ ] Remove debug logging statements
- [ ] Implement proper user authentication (replace `test-user`)

### 7. Tool Call Logging

All MCP tool executions are automatically logged to `backend/logs/`:

- **`tool_calls.json`** - Structured JSON logs (one per line)
- **`tool_calls.log`** - Human-readable logs

**Log Entry Example:**
```json
{
  "timestamp": "2025-10-14T21:30:45.123456",
  "session_id": "a3f2b8c1",
  "tool_name": "add",
  "arguments": {"a": 5, "b": 3},
  "status": "success",
  "duration_ms": 12.45,
  "result": "8",
  "metadata": {
    "model": "gpt-3.5-turbo",
    "api": "openai"
  }
}
```

Toggle logging with `ENABLE_TOOL_LOGGING="false"` in `.env`.

---

## Telesign SMS Integration

### Current Capabilities ✅
- ✅ Send SMS messages
- ✅ Phone number verification (PhoneID)
- ✅ 2FA verification codes
- ✅ Fraud risk assessment
- ✅ Message delivery status tracking
- ✅ Transaction logging

### Future Enhancements (Requires WhatsApp Business API) 🔜
- 🔜 WhatsApp message delivery
- 🔜 WhatsApp template messages
- 🔜 WhatsApp media messages (images, videos, docs)
- 🔜 WhatsApp interactive buttons

### Testing
Run the SMS test suite: