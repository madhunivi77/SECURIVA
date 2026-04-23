## How to Run Backend
- install uv (using uv for the project)
- will install all libraries
` uv sync `
- start the server
`python run.py (or uv run run.py)`
- start the agent
` uv run --active my_app/client/agent.py `

Compliance report DynamoDB testing: see [docs/COMPLIANCE_REPORTS_DYNAMODB_TESTING.md](docs/COMPLIANCE_REPORTS_DYNAMODB_TESTING.md).
Compliance feature/module improvements: see [docs/COMPLIANCE_IMPROVEMENT_GUIDE.md](docs/COMPLIANCE_IMPROVEMENT_GUIDE.md).

---

## Stripe Integration

Stripe is mounted in the API app at `/stripe` and currently provides:

- `GET /stripe/config`
- `POST /stripe/checkout/session`
- `POST /stripe/billing-portal/session`
- `POST /stripe/webhook`

When `STRIPE_SECRET_KEY` is not configured, Stripe routes return a configuration error while the rest of the backend remains available.

### Setting up Stripe for development

**1. Get test credentials**
- Log in to [dashboard.stripe.com](https://dashboard.stripe.com) and enable **Test mode** (top-right toggle)
- Go to **Developers → API keys** and copy the **Secret key** (`sk_test_...`) and **Publishable key** (`pk_test_...`)

**2. Create a Product + Price**
- Go to **Product catalog → Add product**, name it (e.g. `Securiva Pro`), set a recurring price
- Copy the resulting **Price ID** (`price_1ABC...`)

**3. Fill in `.env`**
```
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_PRICE_ID="price_1ABC..."
```

**4. Forward webhooks locally (Stripe CLI)**

The Stripe CLI is a **system tool** — install it separately, not via uv:
```powershell
winget install Stripe.StripeCLI
stripe login
stripe listen --forward-to localhost:8000/stripe/webhook
```
The CLI will print a webhook signing secret (`whsec_...`). Add it to `.env`:
```
STRIPE_WEBHOOK_SECRET="whsec_..."
```
Restart the backend after updating `.env`.

**5. Test the flow**
```powershell
# Trigger a synthetic event
stripe trigger checkout.session.completed
```
Or go to the frontend `/billing` page and use Stripe's test card `4242 4242 4242 4242` (any future expiry, any CVC).

After a successful checkout, `my_app/server/oauth.json` will show `"subscription_status": "active"` under the user's `services.stripe` object.

### What the webhook handler covers

| Event | Effect |
|---|---|
| `checkout.session.completed` | Sets `subscription_status: "active"` in `oauth.json` |
| `customer.subscription.updated` | Mirrors Stripe status (e.g. `past_due`, `paused`) |
| `customer.subscription.deleted` | Sets `subscription_status: "canceled"` |

### Known limitations / next steps

- Subscription status is stored in `oauth.json` (flat file — fine for dev, not for production)
- No feature gating yet — add a `get_subscription_status(user_id)` helper and guard premium endpoints behind `status == "active"`
- The `stripe` Python package (SDK) is already in `pyproject.toml`; the Stripe CLI is a separate system install

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

## VAPI Voice AI Integration

The backend includes webhook handlers for [VAPI](https://vapi.ai) voice AI integration, enabling voice-controlled access to MCP tools.

### Architecture Overview

```
VAPI Cloud
    ↓ (HTTP POST)
/api/vapi/chat/completions  ←── Custom LLM endpoint
    ↓
┌─────────────────────────────────┐
│  Has API key (authenticated)?   │
└─────────────────────────────────┘
       ↓ YES              ↓ NO
/api/chat (LangGraph     OpenAI Direct
 + MCP tools)            (basic chat)
       ↓                      ↓
Full tool access         Conversation only
```

### Endpoints

#### `POST /api/vapi/chat/completions`
Custom LLM endpoint that VAPI calls for AI responses.

**Request (from VAPI):**
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "What's on my calendar?"}
  ],
  "stream": true,
  "call": {
      "assistant": {
         "metadata": {"voiceToken": "short-lived-voice-jwt"}
      }
  }
}
```

**Response (OpenAI-compatible):**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "You have 3 events today..."
    },
    "finish_reason": "stop"
  }]
}
```

**Features:**
- Supports streaming responses (SSE) for faster voice output
- Extracts `voiceToken` from call metadata (`call.assistant.metadata.voiceToken`)
- Falls back to direct OpenAI if not authenticated
- Dev mode allows tool access without authentication

#### `POST /api/vapi/events`
Handles VAPI webhook events (tool calls, status updates, etc.).

**Supported Message Types:**
| Type | Description |
|------|-------------|
| `tool-calls` | Execute MCP tools and return results |
| `assistant-request` | Return dynamic assistant configuration |
| `function-call` | Legacy function call format |
| `status-update` | Call status changes |
| `end-of-call-report` | Call completion summary |
| `conversation-update` | Transcript updates |
| `hang` | User hangup event |

### Configuration

**Environment Variables (`.env`):**
```bash
# VAPI webhook URL (use ngrok for local development)
VAPI_SERVER_URL=https://your-ngrok-url.ngrok-free.dev

# OpenAI API key (required for voice responses)
OPENAI_API_KEY=sk-proj-xxx

# Deepgram API key (for transcription/TTS)
DEEPGRAM_API_KEY=xxx
```

**Dev Mode (`vapi_webhook.py`):**
```python
# Set to True to allow voice assistant to use tools without login
VOICE_DEV_MODE = True
VOICE_DEV_USER_ID = "voice-dev-user"
```

### Tool Mappings

The webhook handler maps VAPI tool names to MCP tools:

| VAPI Tool Name | MCP Tool | Description |
|---------------|----------|-------------|
| `listEmails` | `listEmails` | List inbox emails |
| `getEmailBodies` | `getEmailBodies` | Get full email content |
| `createGmailDraft` | `createGmailDraft` | Create email draft |
| `summarizeEmail` | `summarizeEmail` | Summarize single email |
| `summarizeRecentEmails` | `summarizeRecentEmails` | Summarize recent emails |
| `listUpcomingEvents` | `listUpcomingEvents` | List calendar events |
| `addCalendarEvent` | `addCalendarEvent` | Create calendar event |
| `listAccounts` | `listAccounts` | List Salesforce accounts |
| `listSalesforceCases` | `listSalesforceCases` | List Salesforce cases |
| `createSalesforceCase` | `createSalesforceCase` | Create Salesforce case |

### Local Development with ngrok

1. Start the backend server:
   ```bash
   uv run python run.py
   ```

2. Start ngrok tunnel:
   ```bash
   ngrok http 8000
   ```

3. Update `.env` with ngrok URL:
   ```bash
   VAPI_SERVER_URL=https://xxx.ngrok-free.dev
   ```

4. Update frontend `.env`:
   ```bash
   VITE_VAPI_SERVER_URL=https://xxx.ngrok-free.dev
   ```

### Streaming Support

The custom LLM endpoint supports streaming responses when `stream: true` is in the request:

```python
# Proxies OpenAI's SSE stream directly to VAPI
return StreamingResponse(
    stream_openai(),
    media_type="text/event-stream"
)
```

This enables faster voice responses as VAPI can start speaking before the full response is generated.
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

```bash
cd backend
uv run python tests/test_telesign.py
```

### Sender ID Configuration

- Preferred env key: `TELESIGN_SENDER_ID`
- Legacy fallback key still accepted: `SENDER_ID`
- SMS send path passes configured sender ID explicitly when present.

### Reusable SMS Templates

Reusable templates for OTP and customer contact are defined in `my_app/server/telesign_auth.py` (`SMS_TEMPLATES`) and can be used through:

- `get_sms_templates()`
- `render_sms_template(...)`
- `send_sms_from_template(...)`

### Tool Mappings

The MCP server provides these Telesign SMS tools: (trial version restricted to verified numbers only)

| Tool Name | Description | Example Usage |
|-----------|-------------|---------------|
| `sendSMS` | Send SMS message | "Send SMS to (___): Meeting at 3pm" |
| `verifyPhoneNumber` | Verify phone details | "Verify phone number (____)" |
| `sendVerificationCode` | Send 2FA code | "Send verification code to (___)" |
| `checkPhoneRisk` | Assess fraud risk | "Check risk for phone 2623984079" |
| `checkMessageStatus` | Check delivery status | "Check status of message ABC123" |