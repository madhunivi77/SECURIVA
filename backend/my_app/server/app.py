from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from google_auth_oauthlib.flow import Flow
import json
import secrets
import os
from pathlib import Path
from .chat_handler import execute_chat_with_tools

# Load environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")

# Enable insecure transport for development
if ENVIRONMENT == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# OAuth configuration
REDIRECT_URI = "http://localhost:8000/callback"
FRONTEND_URL = "http://localhost:5173"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]

# Cookie settings
COOKIE_SECURE = ENVIRONMENT == "production" or (COOKIE_SAMESITE.lower() == "none" and ENVIRONMENT == "production")
SESSION_COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 days

# Store CSRF tokens (in production, use Redis or database)
csrf_tokens = {}

# Store sessions (in production, use Redis or database)
sessions = {}

# Configure Google OAuth flow
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

# Define a simple root route
async def index(request):
    return HTMLResponse("<h1>Hello from your Starlette App!</h1><p>Visit /api/status to see a JSON response.</p>")

# Define an API-style route that returns status
async def api_status(request):
    # Check if user has a session
    session_id = request.cookies.get("session_id")
    authenticated = session_id and session_id in sessions

    # Generate CSRF token
    csrf_token = secrets.token_urlsafe(32)
    if authenticated:
        csrf_tokens[session_id] = csrf_token

    # Create response with status
    response_data = {
        "status": "ok",
        "source": "Starlette",
        "authenticated": authenticated,
        "csrf_token": csrf_token if authenticated else None,
        "token": session_id if authenticated else None
    }

    return JSONResponse(response_data)

# Define a route to initiate Google OAuth
async def login(request):
    # Generate the Google OAuth URL
    authorization_url, state = flow.authorization_url(
        access_type="offline",  # Get refresh token
        prompt="consent",  # Force new refresh token
        include_granted_scopes="false"  # Don't include previously granted scopes
    )
    # Redirect the user's browser to Google
    return RedirectResponse(authorization_url)

# Define a route to handle the Google OAuth callback
async def callback(request):
    try:
        # Exchange authorization code for tokens
        flow.fetch_token(authorization_response=str(request.url))

        # Extract the tokens
        credentials = flow.credentials.to_json()
        credentials_dict = json.loads(credentials)

        # Create a simple session
        session_id = secrets.token_urlsafe(32)
        sessions[session_id] = {
            "google_credentials": credentials_dict,
            "user_id": "google-user"
        }

        # Store credentials in oauth.json for MCP tools to use
        oauth_file = Path(__file__).parent / "oauth.json"
        if oauth_file.exists():
            with open(oauth_file, "r") as f:
                data = json.load(f)
        else:
            data = {"users": []}

        # Update/Add the user's entry
        user_entry = {
            "user_id": "google-user",
            "google_creds": credentials
        }

        users = data.get("users", [])
        found = False
        for i, user in enumerate(users):
            if user.get("user_id") == "google-user":
                users[i] = user_entry
                found = True
                break
        if not found:
            users.append(user_entry)

        data["users"] = users

        # Write back to the storage file
        with open(oauth_file, "w") as f:
            json.dump(data, f, indent=2)

        # Create response that redirects to frontend
        response = RedirectResponse(
            url=FRONTEND_URL,
            status_code=302
        )

        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
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


# Define logout endpoint
async def api_logout(request):
    """Clear user session and logout."""
    session_id = request.cookies.get("session_id")

    # Remove session from memory
    if session_id and session_id in sessions:
        del sessions[session_id]

    # Remove CSRF token
    if session_id and session_id in csrf_tokens:
        del csrf_tokens[session_id]

    # Create response
    response = JSONResponse({
        "status": "ok",
        "message": "Logged out successfully"
    })

    # Clear session cookie
    response.delete_cookie(
        key="session_id",
        domain=None
    )

    return response

# Define chat endpoint that integrates with MCP tools
async def api_chat(request):
    try:
        # Get session ID from cookie
        session_id = request.cookies.get("session_id")
        if not session_id or session_id not in sessions:
            return JSONResponse(
                {"error": "Not authenticated. Please login first."},
                status_code=401
            )

        # Verify CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")

        if not csrf_token:
            return JSONResponse(
                {"error": "Missing CSRF token"},
                status_code=401
            )

        # Validate CSRF token
        expected_csrf = csrf_tokens.get(session_id)

        if expected_csrf is None:
            # CSRF token mapping lost (e.g., server restart)
            # If session is still valid, accept it and regenerate mapping
            csrf_tokens[session_id] = csrf_token
        elif expected_csrf != csrf_token:
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

        # Get user_id from session
        session = sessions.get(session_id, {})
        user_id = session.get("user_id")

        # Execute chat with MCP tools, passing the user_id
        result = await execute_chat_with_tools(messages, model, api, user_id)

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

# Create the Starlette app instance with routes
# Note: CORS is handled at the top level in main.py
api_app = Starlette(
    routes=[
        Route("/", index),
        Route("/api/status", api_status),
        Route("/api/chat", api_chat, methods=["POST"]),
        Route("/api/logout", api_logout, methods=["POST"]),
        Route("/login", login),
        Route("/callback", callback),
    ]
)
