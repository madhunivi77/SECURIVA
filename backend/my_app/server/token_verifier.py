import jwt
import os
from mcp.server.auth.provider import AccessToken, TokenVerifier

# Load the secret key from an environment variable.
# This must be the same secret key used in the authorization server.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
print(f"printing jwt secret: {JWT_SECRET_KEY}")
if not JWT_SECRET_KEY:
    raise ValueError("No JWT_SECRET_KEY set for the token verifier. Please set it in your .env file.")

class SimpleTokenVerifier(TokenVerifier):
    """Verifies a JWT token."""

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verifies the token. Returns an AccessToken if valid, otherwise None."""
        try:
            # Decode the token. This automatically checks the signature and expiration time.
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            
            # If decoding is successful, the token is valid.
            # We can now create the AccessToken object from the token's payload.
            return AccessToken(
                client_id=payload.get('client_id'), 
                subject=payload.get('sub'), 
                token=token, 
                scopes=["user"] # You could also include scopes in the JWT payload
            )
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
            return None
        except jwt.InvalidTokenError as e:
            # This catches all other errors, like invalid signature or malformed token.
            print(f"Invalid token: {e}")
            return None