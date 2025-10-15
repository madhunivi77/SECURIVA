from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse, Response
import httpx
import os
import secrets
from .chat_handler import execute_chat_with_tools
from .telesign_whatsapp import send_whatsapp_message
from .telesign_auth import telesign_authenticate

# Load environment variables for security configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")

# In development with SameSite=None, we can use Secure=False (Chrome allows this for localhost)
# In production, SameSite=None REQUIRES Secure=True
if COOKIE_SAMESITE.lower() == "none":
    COOKIE_SECURE = ENVIRONMENT == "production"
else:
    COOKIE_SECURE = ENVIRONMENT == "production" or os.getenv("COOKIE_SECURE", "False").lower() == "true"

# Store CSRF tokens (in production, use Redis or database)
csrf_tokens = {}

# Define a simple root route
async def index(request):
    return HTMLResponse("<h1>Hello from your Starlette App!</h1><p>Visit /api/status to see a JSON response.</p>")

# Define an API-style route that returns status + JWT token
async def api_status(request):
    # Internally fetch JWT token from auth server
    token = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/auth/token")
            response.raise_for_status()
            token = response.json()["access_token"]
    except Exception as e:
        print(f"Error fetching token: {e}")

    # Generate CSRF token
    csrf_token = secrets.token_urlsafe(32)
    if token:
        csrf_tokens[token] = csrf_token

    # Create response with status and token
    response_data = {
        "status": "ok",
        "source": "Starlette",
        "token": token,
        "authenticated": token is not None,
        "csrf_token": csrf_token  # Send CSRF token to frontend
    }

    response = JSONResponse(response_data)

    # Set token as HttpOnly cookie if we got one
    if token:
        print(f"DEBUG - Setting cookie with: secure={COOKIE_SECURE}, samesite={COOKIE_SAMESITE}")
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            secure=COOKIE_SECURE,  # Automatically True in production
            samesite=COOKIE_SAMESITE,
            max_age=3600,  # 1 hour (matches JWT expiration)
            domain=None  # Let browser decide
        )
        print(f"DEBUG - Cookie set successfully")

    return response

# Define chat endpoint that integrates with MCP tools
async def api_chat(request):
    try:
        # Verify CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        auth_token = request.cookies.get("auth_token")

        # Debug logging
        print(f"DEBUG - CSRF Token from header: {csrf_token}")
        print(f"DEBUG - Auth Token from cookie: {auth_token}")
        print(f"DEBUG - All cookies: {request.cookies}")
        print(f"DEBUG - All headers: {dict(request.headers)}")

        if not csrf_token or not auth_token:
            return JSONResponse(
                {"error": f"Missing authentication or CSRF token. CSRF: {bool(csrf_token)}, Auth: {bool(auth_token)}"},
                status_code=401
            )

        # Validate CSRF token
        expected_csrf = csrf_tokens.get(auth_token)
        print(f"DEBUG - Expected CSRF: {expected_csrf}, Got: {csrf_token}")
        if expected_csrf != csrf_token:
            return JSONResponse(
                {"error": "Invalid CSRF token"},
                status_code=403
            )

        # Parse request body
        data = await request.json()
        messages = data.get("messages", [])
        model = data.get("model")
        api = data.get("api")

        # Validate messages
        if not messages or not isinstance(messages, list):
            return JSONResponse(
                {"error": "Invalid request: 'messages' array is required"},
                status_code=400
            )

        # Execute chat with MCP tools
        result = await execute_chat_with_tools(messages, model, api)

        # Check for errors
        if "error" in result:
            return JSONResponse(
                {"error": result["error"]},
                status_code=500
            )

        # Return successful result
        return JSONResponse(result)

    except Exception as e:
        return JSONResponse(
            {"error": f"Chat request failed: {str(e)}"},
            status_code=500
        )

# Send WhatsApp message route
async def send_whatsapp(request):
    data = await request.json()
    phone = data["phone"]
    message = data["message"]
    # Use your telesign function
    result = await send_whatsapp_message(phone, message)
    return JSONResponse({"status": "sent" if result else "failed"})

# Create the Starlette app instance with routes
# Note: CORS is handled at the top level in main.py
api_app = Starlette(
    routes=[
        Route("/", index),
        Route("/api/status", api_status),
        Route("/api/chat", api_chat, methods=["POST"]),
        Route("/api/send_whatsapp", send_whatsapp, methods=["POST"]),
    ]
)