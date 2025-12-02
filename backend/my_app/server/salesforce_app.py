from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import RedirectResponse, JSONResponse
import requests
import os
import json
from pathlib import Path
from urllib.parse import urlencode, parse_qs
from datetime import datetime
from .api_key_manager import validate_api_key


# Environment variables
SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
SF_CALLBACK_URL = os.getenv("SF_CALLBACK_URL")
SF_DOMAIN = os.getenv("SF_DOMAIN", "login")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Define logout endpoint
async def salesforce_logout(request):
    """Clear credentials and logout"""

    # Get API key from cookie
    api_key = request.cookies.get("api_key")
    
    oauth_path = Path(__file__).parent / "oauth.json"

    # Validate API key and get user_id mapping
    user_id = validate_api_key(api_key, oauth_path)

    if oauth_path.exists():
        with open(oauth_path, "r") as f:
            oauth_data = json.load(f)

        users = oauth_data.get("users", [])

        # Find user entry by user_id
        user_entry = None
        for user in users:
            if user.get("user_id") == user_id:
                user_entry = user
                break
        # user found
        if user_entry:
            # remove salesforce creds
            user_entry["services"].pop("salesforce", None)

            # write back to oauth.json
            oauth_data["users"] = users

            with open(oauth_path, "w") as f:
                json.dump(oauth_data, f, indent=2)

    # Successful response
    response = JSONResponse({
        "status": "ok",
        "message": "Logged out successfully"
    })

    return response


async def salesforce_login(request):
    """
    Initiate Salesforce OAuth flow

    Gets user_id from API key cookie
    """
    # Get API key from cookie
    api_key = request.cookies.get("api_key")

    if not api_key:
        return JSONResponse(
            {"error": "Not authenticated. Please login with Google first."},
            status_code=401
        )

    # Validate API key
    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)

    if not user_id:
        return JSONResponse(
            {"error": "Invalid API key. Please login again."},
            status_code=401
        )

    # Pass user_id via state parameter (will be returned in callback)
    base = f"https://{SF_DOMAIN}.salesforce.com/services/oauth2/authorize"
    params = {
        "response_type": "code",
        "client_id": SF_CLIENT_ID,
        "redirect_uri": SF_CALLBACK_URL,
        "scope": "api refresh_token offline_access",
        "state": user_id  # Pass user_id to callback
    }
    return RedirectResponse(f"{base}?{urlencode(params)}")


async def salesforce_callback(request):
    """Handle Salesforce OAuth callback"""
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # user_id passed from login

    if not code:
        return JSONResponse(
            {"error": "Authorization code not provided"},
            status_code=400
        )

    if not state:
        return JSONResponse(
            {"error": "State parameter (user_id) not provided"},
            status_code=400
        )

    user_id = state

    # Exchange code for tokens
    token_url = f"https://{SF_DOMAIN}.salesforce.com/services/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": SF_CLIENT_ID,
        "client_secret": SF_CLIENT_SECRET,
        "redirect_uri": SF_CALLBACK_URL,
    }

    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return JSONResponse(
            {"error": "Failed to get token", "details": r.text},
            status_code=r.status_code
        )

    creds = r.json()

    # Store Salesforce tokens with new schema
    oauth_path = Path(__file__).parent / "oauth.json"
    if oauth_path.exists():
        with open(oauth_path, "r") as f:
            oauth_data = json.load(f)
    else:
        oauth_data = {"users": []}

    users = oauth_data.get("users", [])

    # Find user entry by user_id
    user_entry = None
    for user in users:
        if user.get("user_id") == user_id:
            user_entry = user
            break

    if not user_entry:
        # User doesn't exist - this shouldn't happen if they logged in with Google first
        return JSONResponse(
            {"error": "User not found. Please login with Google first."},
            status_code=400
        )

    # Extract Salesforce metadata
    sf_instance_url = creds.get("instance_url", "")
    sf_id = creds.get("id", "")
    sf_org_id = sf_id.split("/")[-2] if sf_id else ""

    # Update Salesforce service credentials
    if "services" not in user_entry:
        user_entry["services"] = {}

    user_entry["services"]["salesforce"] = {
        "instance_url": sf_instance_url,
        "salesforce_user_id": sf_id,
        "org_id": sf_org_id,
        "credentials": creds,
        "connected_at": datetime.now().isoformat(),
        "scopes": creds.get("scope", "api refresh_token offline_access").split()
    }

    oauth_data["users"] = users

    with open(oauth_path, "w") as f:
        json.dump(oauth_data, f, indent=2)

    # Redirect to frontend with success message
    return RedirectResponse(
        url=f"{FRONTEND_URL}?salesforce=connected",
        status_code=302
    )


# Create Starlette app for Salesforce OAuth
salesforce_app = Starlette(
    routes=[
        Route("/login", salesforce_login),
        Route("/callback", salesforce_callback),
        Route("/logout", salesforce_logout, methods=["POST"]),
    ]
)