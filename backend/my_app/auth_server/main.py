from flask import Flask, jsonify
import jwt
import datetime
import os

auth_app = Flask(__name__)

# Load the secret key from an environment variable.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("No JWT_SECRET_KEY set for the authorization server. Please set it in your .env file.")

@auth_app.route("/token", methods=["POST"])
def get_token():
    """Generates and issues a JWT."""
    payload = {
        # 'exp' (Expiration Time) claim: token is valid for 1 hour
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
        # 'iat' (Issued At) claim: time the token was generated
        'iat': datetime.datetime.now(datetime.timezone.utc),
        # 'sub' (Subject) claim: identifier for the user
        'sub': 'test-user',
        # Custom claim for the client ID
        'client_id': 'test-client'
    }
    
    # Encode the token with the secret key using the HS256 algorithm
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    
    return jsonify({"access_token": encoded_jwt, "token_type": "Bearer"})