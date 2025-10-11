from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
from google_auth_oauthlib.flow import Flow
from pathlib import Path
import os
import json


# 1. Create the Flask app instance
flask_app = Flask(__name__)
CORS(flask_app, origins=["https://localhost:5173"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = "https://localhost:8000/callback" # endpoint for google to refer user to after authentication

# define the scopes granted via access tokens using principle of least priviledge
SCOPES = [  "openid", 
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/gmail.readonly"]

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

# 2. Define a simple root route
@flask_app.route("/")
def index():
    return "<h1>Hello from your Flask App!</h1><p>Visit /api/status to see a JSON response.</p>"

# 3. Define an API-style route
@flask_app.route("/api/status")
def api_status():
    return jsonify({"status": "ok", "source": "Flask"})

# Define a route to initiate oAuth
@flask_app.route("/login")
def login():
    # Generate the Google OAuth URL
    authorization_url, state = flow.authorization_url(
        access_type="offline",  # get refresh token
        prompt="consent", # force new refresh token
        include_granted_scopes="true"
    )
    # Redirect the user’s browser to Google
    return redirect(authorization_url)

# Define a route to handle the oAuth redirection
@flask_app.route("/callback")
def callback():
    # Exchange authorization code for tokens
    flow.fetch_token(authorization_response=request.url)
    
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
    return f"Credentials successfully stored!"
        