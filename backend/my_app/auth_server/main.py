from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import jwt
import datetime
import os

# Load the secret key from an environment variable.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("No JWT_SECRET_KEY set for the authorization server. Please set it in your .env file.")

async def get_token(request):
    """Generates and issues a JWT."""
    # Parse request body to get user_id if provided
    try:
        body = await request.json()
        user_id = body.get('user_id', 'test-user')  # Default to 'test-user' for backwards compatibility
    except:
        user_id = 'test-user'

    payload = {
        # 'exp' (Expiration Time) claim: token is valid for 1 hour
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
        # 'iat' (Issued At) claim: time the token was generated
        'iat': datetime.datetime.now(datetime.timezone.utc),
        # 'sub' (Subject) claim: identifier for the user
        'sub': user_id,
        # Custom claim for the client ID
        'client_id': 'test-client'
    }

    # Encode the token with the secret key using the HS256 algorithm
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

    return JSONResponse({"access_token": encoded_jwt, "token_type": "Bearer"})

auth_app = Starlette(
    routes=[
        Route("/token", get_token, methods=["POST"]),
    ]
)