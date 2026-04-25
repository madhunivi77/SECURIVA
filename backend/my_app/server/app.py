from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse, Response, RedirectResponse, StreamingResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import json
import bcrypt
import jwt as pyjwt
import os
import uuid
import secrets
import httpx
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .chat_handler import (
    execute_chat_with_tools,
    execute_chat_with_tools_stream,
    ensure_tool_catalog_ready,
)
from .salesforce_app import salesforce_app
from .stripe_app import stripe_app
from .db import db_app
from .api_key_manager import generate_api_key, store_api_key, validate_api_key
from .activity_logger import log_activity, get_activity_logs
from .security_tools import security_app
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
        credentials = flow.credentials
        user_email = None
        try:
            idinfo = id_token.verify_oauth2_token(
                credentials.id_token,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )

            user_email = idinfo.get("email")
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
            "credentials": credentials.to_json(),
            "connected_at": datetime.now().isoformat(),
            "scopes": SCOPES
        }

        data["users"] = users

        with open(oauth_file, "w") as f:
            json.dump(data, f, indent=2)

        api_key = generate_api_key()
        store_api_key(user_id, api_key, oauth_file)

        log_activity("signin", user_email=user_email, user_id=user_id, details={"method": "google_oauth"})

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
        log_activity("signin", error=str(e), details={"method": "google_oauth"})
        print(f"OAuth callback error: {e}")
        return JSONResponse(
            {"error": f"Authentication failed: {str(e)}"},
            status_code=500
        )

async def api_logout(request):
    """Clear authentication cookies and logout."""
    # Try to identify the user before clearing cookies
    api_key = request.cookies.get("api_key")
    user_email = None
    if api_key:
        oauth_file = Path(__file__).parent / "oauth.json"
        user_id = validate_api_key(api_key, oauth_file)
        if user_id:
            try:
                with open(oauth_file, "r") as f:
                    data = json.load(f)
                    for user in data.get("users", []):
                        if user.get("user_id") == user_id:
                            user_email = user.get("email")
                            break
            except:
                pass

    log_activity("logout", user_email=user_email)

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

        # Count user messages (exclude system)
        user_msgs = [m for m in messages if m.get("role") == "user"]
        tool_calls = result.get("tool_calls", [])
        log_activity("chat", user_id=user_id, details={
            "model": model,
            "api": api,
            "user_message": user_msgs[-1].get("content", "")[:200] if user_msgs else "",
            "tool_calls_count": len(tool_calls) if tool_calls else 0,
        })

        return JSONResponse(result)

    except json.JSONDecodeError:
        return JSONResponse(
            {"error": "Invalid JSON in request body"},
            status_code=400
        )
    except Exception as e:
        log_activity("chat", user_id=user_id if 'user_id' in dir() else None, error=str(e))
        print(f"Internal error: {str(e)}")
        return JSONResponse(
            {"error": "An internal error occurred"},
            status_code=500
        )


async def api_chat_stream(request):
    """Streaming chat — Server-Sent Events.

    Auth: cookie api_key → user_id.
    Body: {"messages": [...], "model"?: str, "api"?: str}
    Stream: lines of `data: <json>\\n\\n` where each json is an event dict
    (see execute_chat_with_tools_stream). Terminates with `data: [DONE]\\n\\n`.
    """
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    if not user_id:
        return JSONResponse({"error": "Invalid or expired API key"}, status_code=401)

    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    messages = body.get("messages", [])
    model = body.get("model")
    api = body.get("api")

    if not messages or not isinstance(messages, list):
        return JSONResponse(
            {"error": "'messages' array is required"}, status_code=400
        )

    async def sse():
        tool_call_names: list[str] = []
        try:
            async for event in execute_chat_with_tools_stream(
                messages, model, api, user_id
            ):
                if event.get("type") == "tool_end" and event.get("name"):
                    tool_call_names.append(event["name"])
                yield f"data: {json.dumps(event, default=str)}\n\n"
        except Exception as e:
            err = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(err)}\n\n"
        finally:
            yield "data: [DONE]\n\n"
            # Log activity after the stream finishes
            try:
                user_msgs = [m for m in messages if m.get("role") == "user"]
                log_activity("chat", user_id=user_id, details={
                    "model": model, "api": api,
                    "user_message": (user_msgs[-1].get("content", "")[:200] if user_msgs else ""),
                    "tool_calls_count": len(tool_call_names),
                    "stream": True,
                })
            except Exception:
                pass

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
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
        log_activity("sms", details={"phone": phone[:3] + "****"})
        return JSONResponse(result)
    except Exception as e:
        log_activity("sms", error=str(e))
        return JSONResponse(
            {"error": "Failed to send SMS"},
            status_code=500
        )

    users_file = Path(__file__).parent / "users.json"
    users = []
    if users_file.exists():
        with open(users_file, "r") as f:
            users = json.load(f)

    if any(u["email"] == email for u in users):
        return JSONResponse({"error": "User already exists"}, status_code=400)

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users.append({"email": email, "password": hashed})
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)

    return JSONResponse({"message": "Signup successful"})

async def manual_login(request):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")

    users_file = Path(__file__).parent / "users.json"
    if not users_file.exists():
        return JSONResponse({"error": "User not found"}, status_code=404)

    with open(users_file, "r") as f:
        users = json.load(f)

    user = next((u for u in users if u["email"] == email), None)
    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        log_activity("signin", user_email=email, error="Invalid credentials", details={"method": "local"})
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)

    log_activity("signin", user_email=email, details={"method": "local"})

    token = pyjwt.encode(
        {"sub": email, "iat": datetime.now().timestamp()},
        os.getenv("JWT_SECRET_KEY"),
        # "dev-secret",
        algorithm="HS256"
    )

    response = JSONResponse({
        "message": "Login successful",
        "redirect": f"{FRONTEND_URL}?auth=success&email={email}"
    })
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=SESSION_COOKIE_MAX_AGE,
        domain=None
    )

    return response

# Voice token endpoint - returns the API key so the voice widget can pass it to VAPI
# (The api_key cookie is httpOnly, so JavaScript can't read it directly)
# DEPRECATED: Use /api/voice-session instead
async def api_voice_token(request):
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    if not user_id:
        return JSONResponse({"error": "Invalid API key"}, status_code=401)

    return JSONResponse({"token": api_key})


# Voice session endpoint - issues a short-lived JWT for voice auth
# The raw API key never leaves the browser-to-backend channel
async def api_voice_session(request):
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    if not user_id:
        return JSONResponse({"error": "Invalid API key"}, status_code=401)

    JWT_SECRET = os.getenv("JWT_SECRET_KEY")
    voice_token = pyjwt.encode(
        {
            "sub": user_id,
            "type": "voice_session",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "iat": datetime.now(timezone.utc),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    log_activity("voice_session", user_id=user_id)

    return JSONResponse({"voice_token": voice_token})


async def api_voice_prewarm(request):
    """
    Fire-and-forget: kick off semantic-index build for the authenticated user.
    Frontend hits this as soon as the voice widget mounts, so by the time
    the user actually taps to speak the index is ready (or nearly ready),
    avoiding the 2-3s cold-start penalty inside the first tool-selection.
    """
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    if not user_id:
        return JSONResponse({"error": "Invalid API key"}, status_code=401)

    import asyncio
    async def _warm():
        try:
            t0 = datetime.now(timezone.utc)
            ok = await ensure_tool_catalog_ready(user_id)
            ms = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
            print(f"[PREWARM] user={user_id} ready={ok} | {ms:.0f}ms")
        except Exception as e:
            print(f"[PREWARM] user={user_id} failed: {e}")

    asyncio.create_task(_warm())
    return JSONResponse({"status": "prewarming"})


async def api_logs(request):
    """Return activity logs and/or tool call logs."""
    api_key = request.cookies.get("api_key")
    if not api_key:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)
    if not user_id:
        return JSONResponse({"error": "Invalid API key"}, status_code=401)

    # Query params
    limit = int(request.query_params.get("limit", "200"))
    status_filter = request.query_params.get("status")
    event_filter = request.query_params.get("event")  # signin, logout, chat, tool_call, etc.
    search = request.query_params.get("search", "")

    # Get activity logs
    activity_logs = get_activity_logs(limit=limit, event_filter=event_filter)

    # Get tool call logs and normalize them into activity format
    if not event_filter or event_filter == "tool_call":
        from .tool_logger import get_tool_logger
        logger = get_tool_logger()
        tool_logs = logger.get_recent_logs(limit=limit)
        for tl in tool_logs:
            activity_logs.append({
                "timestamp": tl.get("timestamp"),
                "event": "tool_call",
                "status": tl.get("status"),
                "user_id": None,
                "user_email": None,
                "details": {
                    "tool_name": tl.get("tool_name"),
                    "arguments": tl.get("arguments"),
                    "result": tl.get("result"),
                    "duration_ms": tl.get("duration_ms"),
                    "session_id": tl.get("session_id"),
                },
                "error": tl.get("error"),
                "metadata": tl.get("metadata"),
            })

    # Sort all logs by timestamp descending
    activity_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Apply filters
    if status_filter:
        activity_logs = [l for l in activity_logs if l.get("status") == status_filter]
    if search:
        search_lower = search.lower()
        activity_logs = [l for l in activity_logs if search_lower in json.dumps(l).lower()]

    activity_logs = activity_logs[:limit]

    return JSONResponse({"logs": activity_logs, "total": len(activity_logs)})


async def dashboard_refresh(request):
    """Fetch integration data to update dashboard"""
    # query database
    # test information
    data = [
      {
        "id": 1,
        "title": "Email Notification",
        "description": "Send email when new lead is created",
        "isActive": True,
        "lastRun": "2 hours ago",
        "triggerCount": 142,
      },
      {
        "id": 2,
        "title": "Slack Alert",
        "description": "Post to Slack on high-priority tickets",
        "isActive": True,
        "lastRun": "5 mins ago",
        "triggerCount": 89,
      },
      {
        "id": 3,
        "title": "Data Sync",
        "description": "Sync CRM data every hour",
        "isActive": False,
        "lastRun": "1 day ago",
        "triggerCount": 456,
      },
      {
        "id": 4,
        "title": "Report Generator",
        "description": "Generate weekly reports on Monday",
        "isActive": True,
        "lastRun": "3 days ago",
        "triggerCount": 24,
      },
      {
        "id": 5,
        "title": "Lead Scoring",
        "description": "Auto-score leads based on activity",
        "isActive": True,
        "lastRun": "Just now",
        "triggerCount": 1203,
      },
      {
        "id": 6,
        "title": "Task Assignment",
        "description": "Assign tasks to team based on workload",
        "isActive": False,
        "lastRun": "1 week ago",
        "triggerCount": 67,
      },
    ]
    return JSONResponse({"cards": data}, status_code=200)

# ==================== APPLICATION SETUP ====================
api_app = Starlette(
    routes=[
        Route("/", index),
        Route("/api/status", api_status),
        Route("/api/chat", api_chat, methods=["POST"]),
        Route("/api/chat/stream", api_chat_stream, methods=["POST"]),
        Route("/api/logout", api_logout, methods=["POST"]),
        Route("/api/voice-token", api_voice_token, methods=["GET"]),
        Route("/api/voice-session", api_voice_session, methods=["POST"]),
        Route("/api/voice/prewarm", api_voice_prewarm, methods=["POST"]),
        Route("/login", login, methods=["GET"]),
        Route("/callback", callback),
        Route("/api/whatsapp/send-sms", api_send_sms, methods=["POST"]),
        Route("/api/dashboard/refresh", dashboard_refresh, methods=["GET"]),
        Route("/api/logs", api_logs, methods=["GET"]),
    ]
)

api_app.mount("/salesforce", salesforce_app)
api_app.mount("/stripe", stripe_app)
api_app.mount("/chat",db_app)
api_app.mount("/security", security_app)

from .composio_app import composio_app
api_app.mount("/api/composio", composio_app)
