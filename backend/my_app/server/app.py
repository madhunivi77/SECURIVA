from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from google_auth_oauthlib.flow import Flow
import json
import jwt as pyjwt
import os
import uuid
from datetime import datetime
from pathlib import Path
from .chat_handler import execute_chat_with_tools
from .salesforce_app import salesforce_app
from .api_key_manager import generate_api_key, store_api_key, validate_api_key

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
    "https://www.googleapis.com/auth/gmail.modify"
]

# Cookie settings
COOKIE_SECURE = ENVIRONMENT == "production" or (COOKIE_SAMESITE.lower() == "none" and ENVIRONMENT == "production")
SESSION_COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 days

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
    # Check if user has a valid API key in cookie
    api_key = request.cookies.get("api_key")
    authenticated = False
    user_email = None
    salesforce_connected = False

    if api_key:
        oauth_file = Path(__file__).parent / "oauth.json"
        user_id = validate_api_key(api_key, oauth_file)

        if user_id:
            authenticated = True
            # Get user email and service connections from oauth.json
            try:
                with open(oauth_file, "r") as f:
                    data = json.load(f)
                    for user in data.get("users", []):
                        if user.get("user_id") == user_id:
                            user_email = user.get("email")
                            # Check if Salesforce is connected
                            services = user.get("services", {})
                            salesforce_connected = "salesforce" in services and services["salesforce"].get("credentials") is not None
                            break
            except:
                pass

    # Create response with status
    response_data = {
        "status": "ok",
        "source": "Starlette",
        "authenticated": authenticated,
        "email": user_email if authenticated else None,
        "salesforce_connected": salesforce_connected
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

        # Extract email from credentials for user identification
        user_email = credentials_dict.get("id_token_jwt", {})

        # Try to extract email from token (simplified - in production use proper JWT decode)
        try:
            id_token = credentials_dict.get("id_token")
            if id_token:
                decoded = pyjwt.decode(id_token, options={"verify_signature": False})
                user_email = decoded.get("email", user_email)
        except:
            pass

        # Load existing oauth.json
        oauth_file = Path(__file__).parent / "oauth.json"
        if oauth_file.exists():
            with open(oauth_file, "r") as f:
                data = json.load(f)
        else:
            data = {"users": []}

        users = data.get("users", [])

        # Check if user already exists (by email)
        user_entry = None
        user_id = None
        for user in users:
            # Check if user exists by email or by Google service
            google_service = user.get("services", {}).get("google", {})
            if google_service.get("email") == user_email or user.get("email") == user_email:
                user_entry = user
                user_id = user.get("user_id")
                break

        # If user doesn't exist, create new user with UUID
        if not user_entry:
            user_id = str(uuid.uuid4())
            user_entry = {
                "user_id": user_id,
                "email": user_email,
                "created_at": datetime.now().isoformat(),
                "services": {}
            }
            users.append(user_entry)

        # Update Google service credentials
        user_entry["services"]["google"] = {
            "email": user_email,
            "credentials": credentials,
            "connected_at": datetime.now().isoformat(),
            "scopes": SCOPES
        }

        data["users"] = users

        # Write back to the storage file
        with open(oauth_file, "w") as f:
            json.dump(data, f, indent=2)

        # Generate and store API key for the user
        api_key = generate_api_key()
        store_api_key(user_id, api_key, oauth_file)

        # Create response that redirects to frontend
        response = RedirectResponse(
            url=f"{FRONTEND_URL}?auth=success&email={user_email}",
            status_code=302
        )

        # Set API key as httpOnly cookie (secure, not accessible via JavaScript)
        response.set_cookie(
            key="api_key",
            value=api_key,
            httponly=True,  # JavaScript cannot access this cookie
            secure=COOKIE_SECURE,  # Only sent over HTTPS in production
            samesite=COOKIE_SAMESITE,  # CSRF protection
            max_age=SESSION_COOKIE_MAX_AGE,  # 30 days
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
    """Clear API key cookie and logout."""

    # Create response
    response = JSONResponse({
        "status": "ok",
        "message": "Logged out successfully"
    })

    # Clear API key cookie
    response.delete_cookie(
        key="api_key",
        domain=None
    )

    return response

# Define chat endpoint that integrates with MCP tools
async def api_chat(request):
    try:
        # Get API key from cookie
        api_key = request.cookies.get("api_key")

        if not api_key:
            return JSONResponse(
                {"error": "Not authenticated. Please login first."},
                status_code=401
            )

        # Validate API key and get user_id
        oauth_file = Path(__file__).parent / "oauth.json"
        user_id = validate_api_key(api_key, oauth_file)

        if not user_id:
            return JSONResponse(
                {"error": "Invalid or expired API key. Please login again."},
                status_code=401
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

        # Execute chat with MCP tools, passing the user_id
        result = await execute_chat_with_tools(messages, model, api, user_id)

        #debug
        print(f"DEBUG - {result}")

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

# Mount Starlette Salesforce app under /salesforce
api_app.mount("/salesforce", salesforce_app)
