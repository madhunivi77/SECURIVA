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
from .salesforce_app import salesforce_bp, flask_app
from starlette.middleware.wsgi import WSGIMiddleware

flask_app.register_blueprint(salesforce_bp)


# Load environment variables for security configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

REDIRECT_URI = "http://localhost:8000/callback" # endpoint for google to refer user to after authentication

# define the scopes granted via access tokens using principle of least priviledge
SCOPES = [  "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",]

# define flow object representing the securiva application and the means of authentication
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

# Define a route to initiate oAuth
async def login(request):
    # Generate the Google OAuth URL
    authorization_url, state = flow.authorization_url(
        access_type="offline",  # get refresh token
        prompt="consent", # force new refresh token
        include_granted_scopes="true"
    )
    # Redirect the user’s browser to Google
    return RedirectResponse(authorization_url)

# Define a route to handle the oAuth redirection
def callback(request):
    # Exchange authorization code for tokens
    flow.fetch_token(authorization_response=str(request.url))
    
    # extract the tokens and expiry
    credentials = flow.credentials.to_json()

    info = {
        "user_id": "test-user",
        "google_creds": credentials
    }
    # read the stored user data
    with open(Path(__file__).parent / "oauth.json", "r") as f:
        data = json.load(f)

    # Update/Add the user's entry
    users = data.get("users", [])
    for i in range(len(users)):
        if users[i].get("user_id") == info.get("user_id"):
            users[i].update(info)
            break
    else:
        users.append(info)
    
    data["users"] = users

    # write back to the storage file
    with open(Path(__file__).parent / "oauth.json", "w") as f:
        json.dump(data, f)
    
    # display success
    return JSONResponse(
            {
                "status": "OK",
                "message": "Credentials successfully stored!"
            },
            status_code=200
        )
       

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

# Create the Starlette app instance with routes
# Note: CORS is handled at the top level in main.py
api_app = Starlette(
    routes=[
        Route("/", index),
        Route("/api/status", api_status),
        Route("/api/chat", api_chat, methods=["POST"]),
        Route("/login", login),
        Route("/callback", callback),
        Route("/salesforce", app=WSGIMiddleware(flask_app))
    ]
)
