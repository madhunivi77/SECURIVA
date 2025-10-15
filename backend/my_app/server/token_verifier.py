import jwt
import os
from mcp.server.auth.provider import AccessToken, TokenVerifier

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("No JWT_SECRET_KEY set for the token verifier. Please set it in your .env file.")

class SimpleTokenVerifier(TokenVerifier):
    """Verifies a JWT token."""

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verifies the token. Returns an AccessToken if valid, otherwise None."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])

            return AccessToken(
                client_id=payload.get('client_id'), 
                subject=payload.get('sub'), 
                token=token, 
                scopes=["user"]
            )
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None