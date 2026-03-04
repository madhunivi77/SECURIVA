# Authentication Flows

Complete authentication flow documentation for all integrated services.

## Table of Contents

- [User Authentication (JWT)](#user-authentication-jwt)
- [Google OAuth 2.0](#google-oauth-20)
- [Salesforce OAuth 2.0](#salesforce-oauth-20)
- [API Key Authentication (Telesign)](#api-key-authentication-telesign)
- [MCP Server Authentication](#mcp-server-authentication)

---

## User Authentication (JWT)

### Overview

SECURIVA uses JWT (JSON Web Tokens) stored in HttpOnly cookies combined with CSRF tokens for secure user authentication.

### Authentication Flow

```
┌─────────┐                                                    ┌─────────┐
│ Browser │                                                    │ Backend │
└────┬────┘                                                    └────┬────┘
     │                                                              │
     │  1. GET /api/status                                          │
     │─────────────────────────────────────────────────────────────▶│
     │                                                              │
     │  2. Generate JWT + CSRF Token                                │
     │                                                              │◀─┐
     │                                                              │  │
     │  3. Set HttpOnly Cookie: auth_token=JWT                      │◀─┘
     │     Return: { csrf_token: "abc123..." }                      │
     │◀─────────────────────────────────────────────────────────────│
     │                                                              │
     │  Store CSRF token in React state                             │
     ├─┐                                                            │
     │ │                                                            │
     │◀┘                                                            │
     │                                                              │
     │  4. POST /api/chat                                           │
     │     Headers: X-CSRF-Token: abc123...                         │
     │     Cookie: auth_token=JWT (sent automatically)              │
     │─────────────────────────────────────────────────────────────▶│
     │                                                              │
     │  5. Validate JWT (from cookie)                               │
     │     Validate CSRF (from header)                              │
     │                                                              ├─┐
     │                                                              │ │
     │                                                              │◀┘
     │  6. Process request                                          │
     │                                                              │
     │  7. Return response                                          │
     │◀─────────────────────────────────────────────────────────────│
```

### Implementation

#### 1. Token Generation (`backend/my_app/auth_server/main.py`)

```python
import jwt
import datetime
import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def generate_jwt(user_id: str) -> str:
    """Generate JWT token for user"""
    payload = {
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'sub': user_id,  # Subject: user identifier
        'client_id': 'securiva-client'
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
```

#### 2. Token Distribution (`backend/my_app/server/app.py`)

```python
import secrets

async def api_status(request):
    """Distribute JWT and CSRF tokens"""
    
    # Generate tokens
    token = generate_jwt(user_id='test-user')  # TODO: Get from authenticated session
    csrf_token = secrets.token_urlsafe(32)
    
    # Store CSRF mapping (in production: use Redis)
    csrf_tokens[token] = csrf_token
    
    # Create response
    response = JSONResponse({
        "status": "ok",
        "csrf_token": csrf_token,
        "authenticated": True
    })
    
    # Set HttpOnly cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,     # Cannot be accessed by JavaScript
        secure=True,       # Only sent over HTTPS (production)
        samesite="lax",    # CSRF protection
        max_age=3600       # 1 hour
    )
    
    return response
```

#### 3. Token Validation (`backend/my_app/server/app.py`)

```python
async def api_chat(request):
    """Validate JWT and CSRF before processing"""
    
    # Extract tokens
    auth_token = request.cookies.get("auth_token")
    csrf_token = request.headers.get("X-CSRF-Token")
    
    # Validate presence
    if not auth_token or not csrf_token:
        return JSONResponse(
            {"error": "Missing authentication tokens"},
            status_code=401
        )
    
    # Validate CSRF
    expected_csrf = csrf_tokens.get(auth_token)
    if expected_csrf != csrf_token:
        return JSONResponse(
            {"error": "Invalid CSRF token"},
            status_code=403
        )
    
    # Decode JWT
    try:
        payload = jwt.decode(auth_token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('sub')
    except jwt.ExpiredSignatureError:
        return JSONResponse({"error": "Token expired"}, status_code=401)
    except jwt.InvalidTokenError:
        return JSONResponse({"error": "Invalid token"}, status_code=401)
    
    # Process authenticated request
    # ...
```

### Frontend Implementation

```javascript
// src/App.jsx

const [csrfToken, setCsrfToken] = useState(null);

// 1. Get tokens on mount
useEffect(() => {
  fetch("http://localhost:8000/api/status", {
    credentials: "include"  // CRITICAL: Send/receive cookies
  })
    .then(res => res.json())
    .then(data => {
      setCsrfToken(data.csrf_token);  // Store CSRF in state
      // JWT stored automatically in HttpOnly cookie
    });
}, []);

// 2. Send authenticated request
const sendMessage = async (message) => {
  const response = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken  // Include CSRF token
    },
    credentials: "include",  // Include HttpOnly cookie
    body: JSON.stringify({ messages: [{ role: "user", content: message }] })
  });
  
  return response.json();
};
```

### Security Considerations

| Feature | Protection | Implementation |
|---------|------------|----------------|
| **HttpOnly Cookie** | XSS attacks | Cookie cannot be accessed by JavaScript |
| **CSRF Token** | CSRF attacks | Requires custom header that attackers can't set |
| **SameSite Attribute** | CSRF attacks | Cookie only sent to same-origin requests |
| **Token Expiration** | Token replay | Tokens expire after 1 hour |
| **Secure Flag** | MITM attacks | Cookie only sent over HTTPS |

---

## Google OAuth 2.0

### Flow Diagram

```
┌──────┐                                         ┌─────────┐                  ┌────────┐
│ User │                                         │ Backend │                  │ Google │
└──┬───┘                                         └────┬────┘                  └───┬────┘
   │                                                  │                            │
   │  1. Click "Login with Google"                   │                            │
   │─────────────────────────────────────────────────▶│                            │
   │                                                  │                            │
   │  2. Generate authorization URL                   │                            │
   │     (with scopes + redirect_uri)                 │                            │
   │                                                  ├─┐                          │
   │                                                  │ │                          │
   │                                                  │◀┘                          │
   │  3. Redirect to Google OAuth                     │                            │
   │◀─────────────────────────────────────────────────│                            │
   │                                                  │                            │
   │  4. Redirect to Google                           │                            │
   │──────────────────────────────────────────────────────────────────────────────▶│
   │                                                  │                            │
   │  5. Google login page                            │                            │
   │◀──────────────────────────────────────────────────────────────────────────────│
   │                                                  │                            │
   │  6. User enters credentials + consents           │                            │
   ├─┐                                                │                            │
   │ │                                                │                            │
   │◀┘                                                │                            │
   │                                                  │                            │
   │  7. Redirect to callback with code               │                            │
   │──────────────────────────────────────────────────▶│                            │
   │                                                  │                            │
   │  8. Exchange code for tokens                     │                            │
   │                                                  │───────────────────────────▶│
   │                                                  │                            │
   │  9. Return access + refresh tokens               │                            │
   │                                                  │◀───────────────────────────│
   │                                                  │                            │
   │  10. Store encrypted tokens in oauth.json        │                            │
   │                                                  ├─┐                          │
   │                                                  │ │                          │
   │                                                  │◀┘                          │
   │  11. Set API key cookie                          │                            │
   │     Redirect to frontend                         │                            │
   │◀─────────────────────────────────────────────────│                            │
```

### Implementation

#### 1. Initiate OAuth Flow

```python
# backend/my_app/server/app.py

from google_auth_oauthlib.flow import Flow

# OAuth configuration
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]

flow = Flow.from_client_config(
    {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    },
    scopes=SCOPES,
)
flow.redirect_uri = "http://localhost:8000/callback"

async def login(request):
    """Initiate Google OAuth flow"""
    authorization_url, state = flow.authorization_url(
        access_type="offline",  # Get refresh token
        prompt="consent",       # Force new consent (ensures refresh token)
        include_granted_scopes="true"
    )
    
    # TODO: Store state in session for validation
    return RedirectResponse(authorization_url)
```

#### 2. Handle OAuth Callback

```python
async def callback(request):
    """Handle OAuth callback and store tokens"""
    
    # Exchange authorization code for tokens
    flow.fetch_token(authorization_response=str(request.url))
    
    # Extract credentials
    credentials = flow.credentials.to_json()
    credentials_dict = json.loads(credentials)
    
    # Extract user email from ID token
    id_token = credentials_dict.get("id_token")
    decoded = jwt.decode(id_token, options={"verify_signature": False})
    user_email = decoded.get("email")
    
    # Generate user ID
    user_id = str(uuid.uuid4())
    
    # Store in oauth.json
    oauth_data = {
        "users": [{
            "user_id": user_id,
            "email": user_email,
            "services": {
                "google": {
                    "email": user_email,
                    "credentials": credentials,  # TODO: Encrypt this
                    "connected_at": datetime.now().isoformat(),
                    "scopes": SCOPES
                }
            }
        }]
    }
    
    with open("oauth.json", "w") as f:
        json.dump(oauth_data, f, indent=2)
    
    # Generate API key for user
    api_key = generate_api_key()
    store_api_key(user_id, api_key, oauth_file)
    
    # Set API key cookie and redirect
    response = RedirectResponse(f"{FRONTEND_URL}?auth=success")
    response.set_cookie(
        key="api_key",
        value=api_key,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=30 * 24 * 3600  # 30 days
    )
    
    return response
```

#### 3. Use Stored Credentials

```python
# backend/my_app/server/mcp_server.py

from google.oauth2.credentials import Credentials

def getGoogleCreds(ctx) -> Credentials:
    """Retrieve Google credentials for authenticated user"""
    
    # Extract user ID from JWT
    encoded_token = ctx.request_context.request.headers.get('Authorization').split(" ")[1]
    payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get('sub')
    
    # Load oauth.json
    with open("oauth.json", "r") as f:
        data = json.load(f)
    
    # Find user's credentials
    for user in data.get("users", []):
        if user.get("user_id") == user_id:
            google_service = user.get("services", {}).get("google")
            if google_service:
                credentials_json = google_service.get("credentials")
                return Credentials.from_authorized_user_info(json.loads(credentials_json))
    
    return None
```

### Scopes Explained

| Scope | Purpose | Access Level |
|-------|---------|--------------|
| `openid` | Basic OpenID Connect | Required for OAuth |
| `gmail.readonly` | Read Gmail messages | Read-only |
| `gmail.modify` | Send emails, modify labels | Write access |
| `calendar.readonly` | Read calendar events | Read-only |
| `calendar` | Create/modify events | Full access |
| `userinfo.profile` | User's name, photo | Read-only |
| `userinfo.email` | User's email address | Read-only |

### Token Refresh

Google tokens expire after 1 hour. Use refresh tokens to get new access tokens:

```python
from google.auth.transport.requests import Request

def refresh_google_token(creds: Credentials) -> Credentials:
    """Refresh expired Google credentials"""
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds
```

---

## Salesforce OAuth 2.0

### Flow Diagram

```
[Similar to Google OAuth, but with Salesforce endpoints]

User → /salesforce/login → Backend → Salesforce Auth → Callback → Store Tokens
```

### Implementation

See [SALESFORCE_INTEGRATION.md](./SALESFORCE_INTEGRATION.md) for complete details.

**Key Differences from Google:**
- Uses Salesforce-specific endpoints
- Returns `instance_url` for API calls
- Requires different scopes: `api refresh_token offline_access`

---

## API Key Authentication (Telesign)

### Overview

Telesign uses simple API key authentication with Customer ID.

### Implementation

```python
# backend/my_app/server/telesign_auth.py

from telesignenterprise.messaging import MessagingClient

CUSTOMER_ID = os.getenv("TELESIGN_CUSTOMER_ID")
API_KEY = os.getenv("TELESIGN_API_KEY")

def get_messaging_client() -> MessagingClient:
    """Get authenticated Telesign client"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("Telesign credentials not configured")
    
    return MessagingClient(CUSTOMER_ID, API_KEY)
```

### Authentication Headers

Telesign SDK automatically adds authentication headers:

```
Authorization: TSA <Customer_ID>:<Base64(HMAC-SHA256(Request))>
Date: <RFC2616_Date>
```

### Security Best Practices

```python
# ✅ GOOD: Load from environment
CUSTOMER_ID = os.getenv("TELESIGN_CUSTOMER_ID")
API_KEY = os.getenv("TELESIGN_API_KEY")

# ❌ BAD: Hardcode credentials
CUSTOMER_ID = "C0998FAD-108D-483D-B2B0-CB5F756F3CC4"  # Never do this!
```

---

## MCP Server Authentication

### Overview

MCP (Model Context Protocol) server uses JWT token verification for all tool calls.

### Token Verification

```python
# backend/my_app/server/token_verifier.py

import jwt
from mcp.server.auth.provider import AccessToken, TokenVerifier

class SimpleTokenVerifier(TokenVerifier):
    """Verifies JWT tokens for MCP server"""
    
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            
            return AccessToken(
                client_id=payload.get('client_id'),
                subject=payload.get('sub'),
                token=token,
                scopes=["user"]
            )
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None
```

### Tool Call Authentication

```python
# backend/my_app/server/mcp_server.py

from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP(
    name="IntegratedDemo",
    stateless_http=True,
    token_verifier=SimpleTokenVerifier(),
    auth=AuthSettings(
        issuer_url="http://localhost:8000/auth",
        resource_server_url="http://localhost:8000/mcp",
    ),
)

@mcp.tool()
def listEmails(context: Context, max_results: int = 10) -> str:
    """List Gmail emails - requires authentication"""
    
    # Get user ID from context (injected by token verifier)
    user_id = context.get('sub', 'unknown')
    
    # Get user's Google credentials
    creds = getGoogleCreds(context)
    if not creds:
        return "User not authenticated with Google OAuth"
    
    # Use credentials to call Gmail API
    # ...
```

---

## Troubleshooting Authentication

### Common Issues

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed solutions.

**Quick Fixes:**

| Issue | Cause | Solution |
|-------|-------|----------|
| "Invalid CSRF token" | CSRF token mismatch | Clear cookies and re-login |
| "Token expired" | JWT expired (> 1 hour) | Refresh page to get new token |
| "User not authenticated" | Missing OAuth tokens | Re-connect service in settings |
| 401 Unauthorized | Missing/invalid API key cookie | Clear cookies and re-login |

---

## Security Checklist

- [ ] All OAuth tokens encrypted at rest
- [ ] HTTPS enabled in production
- [ ] JWT secret key rotated regularly
- [ ] CSRF tokens validated on all POST requests
- [ ] HttpOnly cookies used for authentication
- [ ] SameSite cookie attribute set
- [ ] Token expiration implemented
- [ ] Refresh token rotation enabled
- [ ] API rate limiting configured
- [ ] Input validation on all endpoints
