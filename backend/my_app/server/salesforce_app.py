from flask import Blueprint, redirect, request, jsonify, Flask
import requests, os, json
from pathlib import Path
from urllib.parse import urlencode

flask_app = Flask(__name__)
salesforce_bp = Blueprint("salesforce_bp", __name__)


# Environment variables
SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
SF_CALLBACK_URL = os.getenv("SF_CALLBACK_URL")
SF_DOMAIN = os.getenv("SF_DOMAIN", "login")


# Salesforce user ID
USER_ID = "csecapstone2735@agentforce.com"


@salesforce_bp.route("/salesforce/login")
def salesforce_login():
   base = f"https://{SF_DOMAIN}.salesforce.com/services/oauth2/authorize"
   params = {
       "response_type": "code",
       "client_id": SF_CLIENT_ID,
       "redirect_uri": SF_CALLBACK_URL,
       "scope": "api refresh_token offline_access",
   }
   return redirect(f"{base}?{urlencode(params)}")


@salesforce_bp.route("/salesforce/callback")
def salesforce_callback():
   code = request.args.get("code")
   if not code:
       return jsonify({"error": "Authorization code not provided"}), 400


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
       return jsonify({"error": "Failed to get token", "details": r.text}), r.status_code


   creds = r.json()


   # Store Salesforce tokens
   oauth_path = Path(__file__).parent / "oauth.json"
   if oauth_path.exists():
       data = json.load(open(oauth_path, "r"))
   else:
       data = {"users": []}


   # Update or add credentials 
   for u in data["users"]:
       if u["user_id"] == USER_ID:
           u["salesforce_creds"] = creds
           break
   else:
       data["users"].append({"user_id": USER_ID, "salesforce_creds": creds})
   json.dump(data, open(oauth_path, "w"), indent=2)
   return jsonify({"status": "Salesforce connected", "details": creds})






