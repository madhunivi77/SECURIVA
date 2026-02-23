from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from google_auth_oauthlib.flow import Flow
import json
import bcrypt
import jwt as pyjwt
import os
import uuid
import secrets
import httpx
from datetime import datetime
from pathlib import Path
from .chat_handler import execute_chat_with_tools
from .salesforce_app import salesforce_app
from .api_key_manager import generate_api_key, store_api_key, validate_api_key
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
from .telesign_token_api import telesign_token_app

# Load environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Enable insecure transport for development
if ENVIRONMENT == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
else:
    if "OAUTHLIB_INSECURE_TRANSPORT" in os.environ:
        del os.environ["OAUTHLIB_INSECURE_TRANSPORT"]

# OAuth configuration
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.modify"
]

# Cookie settings
if COOKIE_SAMESITE.lower() == "none":
    COOKIE_SECURE = ENVIRONMENT == "production"
else:
    COOKIE_SECURE = ENVIRONMENT == "production" or os.getenv("COOKIE_SECURE", "False").lower() == "true"

SESSION_COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 days

# Logging configuration
import logging
from logging.handlers import RotatingFileHandler

log_path = Path(__file__).parent / "ai_calls.log"
handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log_ai_call(user_id, model, messages, result):
    """Log AI request/response in a readable format."""
    entry = (
        f"\n{'='*80}\n"
        f"User ID: {user_id}\n"
        f"Model: {model}\n"
        f"Messages:\n{json.dumps(messages, indent=2)}\n\n"
        f"Response:\n{json.dumps(result, indent=2)}\n"
        f"{'='*80}\n"
    )
    logging.info(entry)

# Configure Google OAuth flow
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

# Store CSRF tokens
csrf_tokens = {}

# ==================== ROUTES ====================

async def index(request):
    """Root endpoint"""
    return HTMLResponse("<h1>Hello from your Starlette App!</h1><p>Visit /api/status to see a JSON response.</p>")

async def api_status(request):
    """API status endpoint"""
    api_key = request.cookies.get("api_key")
    authenticated = False
    user_email = None
    salesforce_connected = False

    if api_key:
        oauth_file = Path(__file__).parent / "oauth.json"
        user_id = validate_api_key(api_key, oauth_file)

        if user_id:
            authenticated = True
            try:
                with open(oauth_file, "r") as f:
                    data = json.load(f)
                    for user in data.get("users", []):
                        if user.get("user_id") == user_id:
                            user_email = user.get("email")
                            salesforce_connected = "salesforce" in user.get("services", {})
                            break
            except:
                pass

    response_data = {
        "status": "ok",
        "source": "Starlette",
        "authenticated": authenticated,
        "email": user_email if authenticated else None,
        "salesforce_connected": salesforce_connected
    }

    return JSONResponse(response_data)

async def login(request):
    """Initiate Google OAuth"""
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true"
    )
    return RedirectResponse(authorization_url)

async def callback(request):
    """Handle Google OAuth callback"""
    try:
        flow.fetch_token(authorization_response=str(request.url))
        credentials = flow.credentials.to_json()
        credentials_dict = json.loads(credentials)

        user_email = None
        try:
            id_token = credentials_dict.get("id_token")
            if id_token:
                decoded = pyjwt.decode(id_token, options={"verify_signature": False})
                user_email = decoded.get("email")
        except:
            pass

        oauth_file = Path(__file__).parent / "oauth.json"
        if oauth_file.exists():
            with open(oauth_file, "r") as f:
                data = json.load(f)
        else:
            data = {"users": []}

        users = data.get("users", [])
        user_entry = None
        user_id = None

        for user in users:
            google_service = user.get("services", {}).get("google", {})
            if google_service.get("email") == user_email or user.get("email") == user_email:
                user_entry = user
                user_id = user.get("user_id")
                break

        if not user_entry:
            user_id = str(uuid.uuid4())
            user_entry = {
                "user_id": user_id,
                "email": user_email,
                "created_at": datetime.now().isoformat(),
                "services": {}
            }
            users.append(user_entry)

        user_entry["services"]["google"] = {
            "email": user_email,
            "credentials": credentials,
            "connected_at": datetime.now().isoformat(),
            "scopes": SCOPES
        }

        data["users"] = users

        with open(oauth_file, "w") as f:
            json.dump(data, f, indent=2)

        api_key = generate_api_key()
        store_api_key(user_id, api_key, oauth_file)

        response = RedirectResponse(
            url=f"{FRONTEND_URL}?auth=success&email={user_email}",
            status_code=302
        )

        response.set_cookie(
            key="api_key",
            value=api_key,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            max_age=SESSION_COOKIE_MAX_AGE,
            domain=None
        )

        return response

    except Exception as e:
        print(f"OAuth callback error: {e}")
        return JSONResponse(
            {"error": f"Authentication failed: {str(e)}"},
            status_code=500
        )

async def api_logout(request):
    """Clear authentication cookies and logout."""
    response = JSONResponse({
        "status": "ok",
        "message": "Logged out successfully"
    })

    response.delete_cookie(key="api_key", domain=None)
    response.delete_cookie(key="auth_token", domain=None)

    return response

async def api_chat(request):
    """Chat endpoint with MCP tools"""
    try:
        api_key = request.cookies.get("api_key")

        if not api_key:
            return JSONResponse(
                {"error": "Not authenticated. Please login first."},
                status_code=401
            )

        oauth_file = Path(__file__).parent / "oauth.json"
        user_id = validate_api_key(api_key, oauth_file)

        if not user_id:
            return JSONResponse(
                {"error": "Invalid or expired API key. Please login again."},
                status_code=401
            )

        data = await request.json()
        messages = data.get("messages", [])
        model = data.get("model")
        api = data.get("api")

        if not messages or not isinstance(messages, list):
            return JSONResponse(
                {"error": "Invalid request: 'messages' array is required"},
                status_code=400
            )

        result = await execute_chat_with_tools(messages, model, api, user_id)
        log_ai_call(user_id, model, messages, result)

        return JSONResponse(result)

    except json.JSONDecodeError:
        return JSONResponse(
            {"error": "Invalid JSON in request body"},
            status_code=400
        )
    except Exception as e:
        print(f"Internal error: {str(e)}")
        return JSONResponse(
            {"error": "An internal error occurred"},
            status_code=500
        )

# Telesign endpoints (add authentication in production)
async def api_send_sms(request):
    """Send SMS"""
    try:
        data = await request.json()
        phone = data.get('phone_number')
        message = data.get('message')
        
        if not phone or not message:
            return JSONResponse(
                {"error": "phone_number and message required"},
                status_code=400
            )
        
        phone = phone.lstrip('+')
        result = send_sms(phone, message)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse(
            {"error": "Failed to send SMS"},
            status_code=500
        )


# ==================== APPLICATION SETUP ====================
api_app = Starlette(
    routes=[
        Route("/", index),
        Route("/api/status", api_status),
        Route("/api/chat", api_chat, methods=["POST"]),
        Route("/api/logout", api_logout, methods=["POST"]),
        Route("/login", login, methods=["GET"]),
        Route("/callback", callback),
        Route("/api/whatsapp/send-sms", api_send_sms, methods=["POST"]),
        # Add other routes as needed
    ]
)

api_app.mount("/salesforce", salesforce_app)
api_app.mount("/api/telesign", telesign_token_app)
