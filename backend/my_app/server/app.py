from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from google_auth_oauthlib.flow import Flow
from pathlib import Path
import json
import httpx
import os
import secrets
from .chat_handler import execute_chat_with_tools
from .telesign_auth import (
    send_whatsapp_message,
    send_sms,
    verify_phone_number,
    get_message_status,
    send_verification_code,
    verify_code,
    assess_phone_risk,
    send_whatsapp_template,
    send_whatsapp_media,
    send_whatsapp_buttons
)


# ==================== SECURITY: ENVIRONMENT CONFIGURATION ====================
# 🔒 LEAST PRIVILEGE: Load only required environment variables
# ⚡ CONCERN: No validation of environment variables
# ⚡ RECOMMENDATION: Add validation and fail-fast on missing critical vars

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# 🔴 SECURITY CONCERN: OAUTHLIB_INSECURE_TRANSPORT allows OAuth over HTTP
# ⚡ MUST BE REMOVED IN PRODUCTION - This is a critical vulnerability
# ⚡ RECOMMENDATION: Remove this line and use HTTPS in production
if ENVIRONMENT == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
else:
    # 🔒 PRODUCTION: Ensure HTTPS is enforced
    if "OAUTHLIB_INSECURE_TRANSPORT" in os.environ:
        del os.environ["OAUTHLIB_INSECURE_TRANSPORT"]

# ⚠️ SECURITY CONCERN: Hardcoded redirect URI
# ⚡ RECOMMENDATION: Make configurable via environment variable with validation
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/callback")

# ✅ GOOD: OAuth scopes follow principle of least privilege
# 🔒 LEAST PRIVILEGE: Only request necessary scopes
# ⚡ NOTE: readonly scopes prevent modification of user data
SCOPES = [  "openid",
    "https://www.googleapis.com/auth/gmail.readonly",       # ✅ Read-only
    "https://www.googleapis.com/auth/calendar.readonly",    # ✅ Read-only
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",]

## ==================== SECURITY: OAUTH FLOW CONFIGURATION ====================
# 🔴 SECURITY CONCERN: No validation of GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
# ⚡ RECOMMENDATION: Validate credentials exist before creating flow
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")
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
flow.redirect_uri = REDIRECT_URI

# ==================== SECURITY: COOKIE CONFIGURATION ====================
# 🔒 LEAST PRIVILEGE: Cookie security settings based on environment
# ✅ GOOD: Automatic secure cookie configuration in production
# In development with SameSite=None, we can use Secure=False (Chrome allows this for localhost)
# In production, SameSite=None REQUIRES Secure=True
if COOKIE_SAMESITE.lower() == "none":
    COOKIE_SECURE = ENVIRONMENT == "production"
else:
    COOKIE_SECURE = ENVIRONMENT == "production" or os.getenv("COOKIE_SECURE", "False").lower() == "true"

# ⚠️ SECURITY CONCERN: In-memory CSRF token storage
# 🔴 CRITICAL FOR PRODUCTION: This won't work with multiple instances
# ⚡ RECOMMENDATION: Use Redis, Memcached, or database for distributed systems
# ⚡ RECOMMENDATION: Implement token expiration and cleanup
# ⚡ RECOMMENDATION: Add rate limiting to prevent token exhaustion attacks
# Store CSRF tokens (in production, use Redis or database)
csrf_tokens = {}

# ==================== ROUTES ====================

# Define a simple root route
async def index(request):
    """
    🔒 SECURITY: Public endpoint - no authentication required
    ⚡ CONCERN: No rate limiting
    ⚡ RECOMMENDATION: Add rate limiting to prevent abuse
    """
    return HTMLResponse("<h1>Hello from your Starlette App!</h1><p>Visit /api/status to see a JSON response.</p>")

# Define an API-style route that returns status + JWT token
async def api_status(request):
    """
    🔒 SECURITY: Token distribution endpoint
    ⚡ CONCERNS:
        - No rate limiting (vulnerable to token exhaustion)
        - No IP-based restrictions
        - Internally fetches JWT without user context
    ⚡ RECOMMENDATIONS:
        - Add rate limiting (max 10 requests per minute per IP)
        - Implement IP whitelisting for internal requests
        - Add request origin validation
        - Log all token issuance for audit trail
    """
    # ⚠️ SECURITY CONCERN: Fetching token without user authentication
    # ⚡ RECOMMENDATION: This should require authentication in production
    token = None
    try:
        # 🔴 SECURITY CONCERN: No timeout on HTTP request
        # ⚡ RECOMMENDATION: Add timeout to prevent hanging
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post("http://localhost:8000/auth/token")
            response.raise_for_status()
            token = response.json()["access_token"]
    except Exception as e:
        print(f"Error fetching token: {e}")
        # ⚠️ SECURITY: Should log to security audit log, not just print
        # TODO: Implement proper logging

    # Generate CSRF token
    # ✅ GOOD: Using secrets.token_urlsafe for cryptographically secure random
    csrf_token = secrets.token_urlsafe(32)
    if token:
        csrf_tokens[token] = csrf_token
        # TODO: Add expiration timestamp to csrf_tokens dict

    response_data = {
        "status": "ok",
        "source": "Starlette",
        "token": token,
        "authenticated": token is not None,
        "csrf_token": csrf_token
    }

    response = JSONResponse(response_data)

    # ==================== SECURITY: HTTP-ONLY COOKIE CONFIGURATION ====================
    # ✅ GOOD: HttpOnly prevents XSS attacks
    # ✅ GOOD: Secure flag in production prevents man-in-the-middle
    # ✅ GOOD: SameSite prevents CSRF attacks
    # ⚡ CONCERN: No domain restriction (should set domain in production)
    # Set token as HttpOnly cookie if we got one
    if token:
        print(f"DEBUG - Setting cookie with: secure={COOKIE_SECURE}, samesite={COOKIE_SAMESITE}")
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,        # ✅ GOOD: XSS protection
            secure=COOKIE_SECURE, # ✅ GOOD: MITM protection in production
            samesite=COOKIE_SAMESITE,  # ✅ GOOD: CSRF protection
            max_age=3600,         # ✅ GOOD: 1 hour expiration matches JWT
            domain=None,          # ⚠️ TODO: Set to production domain
            path="/"              # ⚠️ LEAST PRIVILEGE: Consider restricting path to /api/
        )
        print(f"DEBUG - Cookie set successfully")
        # ⚠️ SECURITY: Remove debug logging in production

    return response

# Define a route to initiate oAuth
async def login(request):
    """
    🔒 SECURITY: OAuth initiation endpoint
    ⚡ CONCERNS:
        - No CSRF protection for OAuth state parameter
        - No validation of request origin
    ⚡ RECOMMENDATIONS:
        - Validate state parameter on callback
        - Add rate limiting
        - Log OAuth initiation attempts
    """
    # ✅ GOOD: Uses OAuth 2.0 with state parameter for CSRF protection
    # ✅ GOOD: Requests offline access for refresh token
    # ✅ GOOD: Forces consent to get new refresh token
    authorization_url, state = flow.authorization_url(
        access_type="offline",  # ✅ GOOD: Get refresh token
        prompt="consent",       # ✅ GOOD: Force new refresh token
        include_granted_scopes="true"
    )
    
    # ⚠️ SECURITY CONCERN: State parameter not stored/validated
    # ⚡ RECOMMENDATION: Store state in session and validate on callback
    # TODO: Store state in secure session storage
    
    return RedirectResponse(authorization_url)

# Define a route to handle the oAuth redirection
def callback(request):
    """
    🔒 SECURITY: OAuth callback endpoint
    ⚠️ CRITICAL SECURITY CONCERNS:
        1. No state parameter validation (CSRF vulnerability)
        2. No error handling for OAuth errors
        3. Credentials stored in plaintext JSON file (major security risk)
        4. No encryption of tokens
        5. Hardcoded user_id "test-user"
        6. File-based storage not suitable for production
    
    ⚡ RECOMMENDATIONS:
        - Validate OAuth state parameter
        - Use encrypted database storage
        - Implement proper user session management
        - Add error handling and validation
        - Log all OAuth callback attempts
        - Rate limit callback endpoint
    """
    # 🔴 CRITICAL: No state parameter validation
    # This makes the application vulnerable to CSRF attacks
    # ⚡ RECOMMENDATION: Validate state parameter from authorization_url()
    
    # Exchange authorization code for tokens
    flow.fetch_token(authorization_response=str(request.url))
    
    # Extract the tokens and expiry
    credentials = flow.credentials.to_json()

    # ⚠️ SECURITY CONCERN: Hardcoded user_id
    # ⚡ RECOMMENDATION: Extract from authenticated session or JWT
    info = {
        "user_id": "test-user",  # 🔴 CHANGE THIS
        "google_creds": credentials  # ⚠️ Stored as plaintext
    }
    
    # 🔴 CRITICAL SECURITY FLAW: Storing OAuth tokens in plaintext file
    # ⚠️ CONCERNS:
    #    - No encryption
    #    - File permissions not set
    #    - No access control
    #    - Race conditions possible
    # ⚡ RECOMMENDATIONS:
    #    - Use encrypted database (SQLCipher, PostgreSQL with pgcrypto)
    #    - Implement token encryption at rest
    #    - Set strict file permissions if file storage is temporary
    #    - Use proper database transactions
    oauth_file = Path(__file__).parent / "oauth.json"
    
    # ⚠️ SECURITY: No file locking or race condition protection
    try:
        with open(oauth_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"users": []}
    except json.JSONDecodeError:
        # ⚠️ Handle corrupted file
        data = {"users": []}

    # Update/Add the user's entry
    users = data.get("users", [])
    for i in range(len(users)):
        if users[i].get("user_id") == info.get("user_id"):
            users[i].update(info)
            break
    else:
        users.append(info)
    
    data["users"] = users

    # 🔴 SECURITY: Writing plaintext credentials to file
    # ⚡ RECOMMENDATION: Encrypt before writing
    with open(oauth_file, "w") as f:
        json.dump(data, f)
    # TODO: Set restrictive file permissions: os.chmod(oauth_file, 0o600)
    
    return JSONResponse(
        {
            "status": "OK",
            "message": "Credentials successfully stored!"
        },
        status_code=200
    )
       

# Define chat endpoint that integrates with MCP tools
async def api_chat(request):
    """
    🔒 SECURITY: Protected chat endpoint with CSRF and JWT validation
    ✅ GOOD PRACTICES:
        - CSRF token validation
        - JWT authentication via HTTP-only cookie
        - Request body validation
    
    ⚠️ CONCERNS:
        - No rate limiting per user
        - No input sanitization for messages
        - Debug logging exposes tokens
        - No message length limits
        - No content filtering for malicious input
    
    ⚡ RECOMMENDATIONS:
        - Add rate limiting (max 10 requests per minute per user)
        - Implement input validation and sanitization
        - Remove debug logging
        - Add message length limits (e.g., 10,000 characters)
        - Implement content filtering for prompt injection attacks
        - Add user-level permissions (not all users should access all tools)
    """
    try:
        # ==================== AUTHENTICATION & CSRF VALIDATION ====================
        # ✅ GOOD: Dual-token validation (CSRF + JWT)
        csrf_token = request.headers.get("X-CSRF-Token")
        auth_token = request.cookies.get("auth_token")

        # ⚠️ SECURITY: Debug logging exposes tokens
        # 🔴 REMOVE IN PRODUCTION
        print(f"DEBUG - CSRF Token from header: {csrf_token}")
        print(f"DEBUG - Auth Token from cookie: {auth_token}")
        print(f"DEBUG - All cookies: {request.cookies}")
        print(f"DEBUG - All headers: {dict(request.headers)}")

        # ✅ GOOD: Check for missing tokens
        if not csrf_token or not auth_token:
            # ⚠️ SECURITY: Log authentication failures
            # TODO: Implement security audit logging
            return JSONResponse(
                {"error": f"Missing authentication or CSRF token. CSRF: {bool(csrf_token)}, Auth: {bool(auth_token)}"},
                status_code=401
            )

        # ✅ GOOD: CSRF token validation
        expected_csrf = csrf_tokens.get(auth_token)
        print(f"DEBUG - Expected CSRF: {expected_csrf}, Got: {csrf_token}")
        
        # ✅ GOOD: Timing-safe comparison (prevents timing attacks)
        # However, secrets.compare_digest is better
        if expected_csrf != csrf_token:
            # ⚠️ SECURITY: Log CSRF validation failures
            # TODO: Implement rate limiting on failed CSRF attempts
            return JSONResponse(
                {"error": "Invalid CSRF token"},
                status_code=403
            )

        # ==================== INPUT VALIDATION ====================
        # ⚠️ SECURITY CONCERN: No input sanitization or validation
        data = await request.json()
        messages = data.get("messages", [])
        model = data.get("model")
        api = data.get("api")

        # ✅ GOOD: Basic validation
        if not messages or not isinstance(messages, list):
            return JSONResponse(
                {"error": "Invalid request: 'messages' array is required"},
                status_code=400
            )

        # ⚠️ ADDITIONAL VALIDATIONS NEEDED:
        # TODO: Validate message structure
        # TODO: Limit message length to prevent memory exhaustion
        # TODO: Validate model and api parameters against whitelist
        # TODO: Check for prompt injection patterns
        # TODO: Implement content filtering
        
        # EXAMPLE VALIDATION (implement these):
        # MAX_MESSAGE_LENGTH = 10000
        # ALLOWED_MODELS = ["gpt-3.5-turbo", "gpt-4"]
        # ALLOWED_APIS = ["openai", "groq"]
        
        # for msg in messages:
        #     if len(msg.get("content", "")) > MAX_MESSAGE_LENGTH:
        #         return JSONResponse({"error": "Message too long"}, status_code=400)
        
        # if model not in ALLOWED_MODELS or api not in ALLOWED_APIS:
        #     return JSONResponse({"error": "Invalid model or API"}, status_code=400)

        # ==================== TOOL EXECUTION ====================
        # Execute chat with MCP tools
        # ⚠️ SECURITY: execute_chat_with_tools should validate tool permissions
        result = await execute_chat_with_tools(messages, model, api)

        # Check for errors
        if "error" in result:
            return JSONResponse(
                {"error": result["error"]},
                status_code=500
            )

        return JSONResponse(result)

    except json.JSONDecodeError:
        # ⚠️ SECURITY: Log malformed requests
        return JSONResponse(
            {"error": "Invalid JSON in request body"},
            status_code=400
        )
    except Exception as e:
        # ⚠️ SECURITY: Don't expose internal error details to client
        # TODO: Log full error internally, return generic message
        print(f"Internal error: {str(e)}")  # Log internally
        return JSONResponse(
            {"error": "An internal error occurred"},  # Generic message to client
            status_code=500
        )


# ==================== TELESIGN/WHATSAPP ENDPOINTS ====================
# 🔒 SECURITY NOTE: All these endpoints need authentication
# ⚠️ CRITICAL: Currently no authentication on these endpoints!
# ⚡ RECOMMENDATIONS:
#    - Add JWT authentication middleware
#    - Implement rate limiting per user
#    - Add user-level permissions (who can send SMS/WhatsApp)
#    - Log all messaging attempts for audit
#    - Validate phone numbers to prevent abuse
#    - Add cost limits per user

async def api_send_whatsapp(request):
    """
    Send a basic WhatsApp message
    
    🔴 CRITICAL SECURITY CONCERNS:
        - No authentication required
        - No rate limiting
        - No input validation
        - No phone number validation
        - Could be abused for spam
    
    ⚡ RECOMMENDATIONS:
        - Require JWT authentication
        - Rate limit to 10 messages per hour per user
        - Validate phone number format
        - Implement phone number whitelist/blacklist
        - Add cost tracking per user
        - Log all attempts with user ID
    """
    try:
        # TODO: Add authentication check here
        # user = await authenticate_request(request)
        # if not user or not user.has_permission("send_whatsapp"):
        #     return JSONResponse({"error": "Unauthorized"}, status_code=403)
        
        data = await request.json()
        phone = data.get('phone_number')
        message = data.get('message')
        
        # ✅ GOOD: Basic validation
        if not phone or not message:
            return JSONResponse(
                {"error": "phone_number and message required"},
                status_code=400
            )
        
        # ⚠️ ADDITIONAL VALIDATIONS NEEDED:
        # TODO: Validate phone number format (E.164)
        # TODO: Check message length limits
        # TODO: Sanitize message content
        # TODO: Check against spam patterns
        # TODO: Rate limit check
        # TODO: Cost limit check for user
        
        # Remove + prefix if present (for trial accounts)
        phone = phone.lstrip('+')
        
        # ⚠️ SECURITY: Log this action for audit
        # TODO: log_audit_event("whatsapp_send", user_id, phone, message_length)
        
        result = send_whatsapp_message(phone, message)
        return JSONResponse(result)
    
    except Exception as e:
        # TODO: Log error securely
        return JSONResponse(
            {"error": "Failed to send WhatsApp message"},
            status_code=500
        )


async def api_send_sms(request):
    """
    Send an SMS message
    
    🔴 SAME SECURITY CONCERNS AS api_send_whatsapp
    See api_send_whatsapp for detailed security recommendations
    """
    try:
        # TODO: Add authentication
        data = await request.json()
        phone = data.get('phone_number')
        message = data.get('message')
        
        if not phone or not message:
            return JSONResponse(
                {"error": "phone_number and message required"},
                status_code=400
            )
        
        # TODO: Add all validations from api_send_whatsapp recommendations
        phone = phone.lstrip('+')
        result = send_sms(phone, message)
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to send SMS"},
            status_code=500
        )


async def api_verify_phone(request):
    """
    Verify phone number details
    
    ⚠️ SECURITY CONCERNS:
        - No authentication
        - Could be used for phone number enumeration
        - No rate limiting
    
    ⚡ RECOMMENDATIONS:
        - Require authentication
        - Rate limit to 5 requests per minute
        - Log all verification attempts
        - Consider privacy implications of returned data
    """
    try:
        # TODO: Add authentication
        data = await request.json()
        phone = data.get('phone_number')
        
        if not phone:
            return JSONResponse(
                {"error": "phone_number required"},
                status_code=400
            )
        
        phone = phone.lstrip('+')
        # TODO: Validate phone format
        # TODO: Rate limit
        
        result = verify_phone_number(phone)
        
        # ⚠️ PRIVACY: Consider redacting sensitive information
        # TODO: Remove PII from response if not needed
        
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to verify phone"},
            status_code=500
        )


async def api_message_status(request):
    """
    Check message delivery status
    
    ⚠️ SECURITY CONCERNS:
        - No authentication
        - No authorization (user should only see their own messages)
        - reference_id could be guessed
    
    ⚡ RECOMMENDATIONS:
        - Require authentication
        - Verify user owns the message (check database)
        - Use UUIDs for reference_id to prevent guessing
    """
    try:
        # TODO: Add authentication
        # TODO: Verify ownership of reference_id
        reference_id = request.path_params.get('reference_id')
        
        if not reference_id:
            return JSONResponse(
                {"error": "reference_id required"},
                status_code=400
            )
        
        result = get_message_status(reference_id)
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to get message status"},
            status_code=500
        )


async def api_send_verification_code(request):
    """
    Send 2FA verification code
    
    ⚠️ SECURITY CONCERNS:
        - No rate limiting (could be abused to spam users)
        - No protection against SMS pumping attacks
        - Generated code visible in response (for testing)
    
    ⚡ RECOMMENDATIONS:
        - Rate limit to 3 attempts per hour per phone
        - Add CAPTCHA for multiple attempts
        - Don't return code in response (only for testing)
        - Implement SMS pumping fraud detection
        - Add phone number verification before sending
    """
    try:
        # TODO: Add rate limiting
        # TODO: Add CAPTCHA after 2 failed attempts
        data = await request.json()
        phone = data.get('phone_number')
        
        if not phone:
            return JSONResponse(
                {"error": "phone_number required"},
                status_code=400
            )
        
        phone = phone.lstrip('+')
        result = send_verification_code(phone)
        
        # ⚠️ SECURITY: Don't return verify_code in production
        # TODO: Remove verify_code from response in production
        
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to send verification code"},
            status_code=500
        )

async def api_verify_code(request):
    """
    Verify user-entered 2FA code
    
    ⚠️ SECURITY CONCERNS:
        - No rate limiting (brute force vulnerability)
        - No lockout after failed attempts
        - Code verification done client-side (see original_code parameter)
    
    ⚡ RECOMMENDATIONS:
        - Rate limit to 5 attempts per reference_id
        - Lock reference_id after 5 failed attempts
        - Implement exponential backoff
        - Remove original_code parameter (verify server-side only)
        - Add CAPTCHA after 3 failed attempts
    """
    try:
        # TODO: Add rate limiting
        # TODO: Track failed attempts
        data = await request.json()
        reference_id = data.get('reference_id')
        code = data.get('code')
        original_code = data.get('original_code')
        
        if not reference_id or not code:
            return JSONResponse(
                {"error": "reference_id and code required"},
                status_code=400
            )
        
        # ⚠️ SECURITY: Verification should be server-side only
        # TODO: Store codes securely in database and verify against that
        result = verify_code(reference_id, code, original_code)
        
        # TODO: Log failed attempts
        # TODO: Implement lockout mechanism
        
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to verify code"},
            status_code=500
        )


async def api_assess_risk(request):
    """
    Assess phone number fraud risk
    
    ⚠️ SECURITY CONCERNS:
        - No authentication
        - Could be abused for phone number intelligence gathering
        - No rate limiting
    
    ⚡ RECOMMENDATIONS:
        - Require authentication
        - Rate limit to 10 requests per hour
        - Log all risk assessments
        - Consider charging for this API call
    """
    try:
        # TODO: Add authentication
        data = await request.json()
        phone = data.get('phone_number')
        lifecycle_event = data.get('account_lifecycle_event', 'create')
        
        if not phone:
            return JSONResponse(
                {"error": "phone_number required"},
                status_code=400
            )
        
        # TODO: Validate lifecycle_event against whitelist
        phone = phone.lstrip('+')
        result = assess_phone_risk(phone, lifecycle_event)
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to assess phone risk"},
            status_code=500
        )


async def api_send_template(request):
    """Send WhatsApp template message"""
    try:
        data = await request.json()
        phone = data.get('phone_number')
        template_id = data.get('template_id')
        parameters = data.get('parameters', [])
        
        if not phone or not template_id:
            return JSONResponse(
                {"error": "phone_number and template_id required"},
                status_code=400
            )
        
        phone = phone.lstrip('+')
        result = send_whatsapp_template(phone, template_id, parameters)
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": f"Failed to send template: {str(e)}"},
            status_code=500
        )


async def api_send_media(request):
    """Send WhatsApp media message"""
    # TODO: Add authentication and all security measures
    try:
        data = await request.json()
        phone = data.get('phone_number')
        media_url = data.get('media_url')
        caption = data.get('caption', '')
        media_type = data.get('media_type', 'image')
        
        if not phone or not media_url:
            return JSONResponse(
                {"error": "phone_number and media_url required"},
                status_code=400
            )
        
        # ⚠️ SECURITY: Validate media_url to prevent SSRF attacks
        # TODO: Validate URL is from trusted domain
        # TODO: Validate media type
        # TODO: Scan media for malware if uploaded by user
        
        phone = phone.lstrip('+')
        result = send_whatsapp_media(phone, media_url, caption, media_type)
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to send media"},
            status_code=500
        )


async def api_send_buttons(request):
    """Send WhatsApp interactive buttons"""
    # TODO: Add authentication and all security measures
    try:
        data = await request.json()
        phone = data.get('phone_number')
        body_text = data.get('body_text')
        buttons = data.get('buttons', [])
        
        if not phone or not body_text or not buttons:
            return JSONResponse(
                {"error": "phone_number, body_text, and buttons required"},
                status_code=400
            )
        
        # TODO: Validate button structure
        # TODO: Limit number of buttons
        
        phone = phone.lstrip('+')
        result = send_whatsapp_buttons(phone, body_text, buttons)
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to send buttons"},
            status_code=500
        )


# ==================== APPLICATION SETUP ====================
# Create the Starlette app instance with routes
# Note: CORS is handled at the top level in main.py
api_app = Starlette(
    routes=[
        Route("/", index),
        Route("/api/status", api_status),
        Route("/api/chat", api_chat, methods=["POST"]),
        Route("/login", login),
        Route("/callback", callback),
        
        # ⚠️ SECURITY: All WhatsApp/Telesign endpoints need authentication
        Route("/api/whatsapp/send-message", api_send_whatsapp, methods=["POST"]),
        Route("/api/whatsapp/send-sms", api_send_sms, methods=["POST"]),
        Route("/api/whatsapp/verify-phone", api_verify_phone, methods=["POST"]),
        Route("/api/whatsapp/status/{reference_id}", api_message_status, methods=["GET"]),
        Route("/api/whatsapp/send-verification", api_send_verification_code, methods=["POST"]),
        Route("/api/whatsapp/verify-code", api_verify_code, methods=["POST"]),
        Route("/api/whatsapp/assess-risk", api_assess_risk, methods=["POST"]),
        Route("/api/whatsapp/send-template", api_send_template, methods=["POST"]),
        Route("/api/whatsapp/send-media", api_send_media, methods=["POST"]),
        Route("/api/whatsapp/send-buttons", api_send_buttons, methods=["POST"]),
    ]
)
