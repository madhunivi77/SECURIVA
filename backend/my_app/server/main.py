import contextlib
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.wsgi import WSGIMiddleware

# Import your app instances from the other files
from .app import flask_app
from .mcp_server import mcp # Make sure you're importing the renamed 'mcp' object
from ..auth_server.main import auth_app

# This new lifespan function is the key to the fix.
# It tells the mcp app to start its internal session manager.
@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        yield

# Create the main Starlette application, now with the lifespan function
app = Starlette(
    routes=[
        # Mount the MCP server under the /mcp path
        Mount("/mcp", app=mcp.streamable_http_app()),

        # Mount the Auth server under the /auth path
        Mount("/auth", app=WSGIMiddleware(auth_app)),

        # Mount the Flask app at the root path
        Mount("/", app=WSGIMiddleware(flask_app))
    ],
    lifespan=lifespan # Add the lifespan manager here
)

# app.py Flask app with telesign?
from flask import Flask, request, jsonify
import requests
from telesign_auth import get_token

flask_app = Flask(__name__) #I need to ask you about this one....

@flask_app.route("/send_whatsapp", methods=["POST"])
def send_whatsapp():
    """Send WhatsApp message via TeleSign API"""
    data = request.get_json()
    phone = data.get("phone")
    message = data.get("message", "Hello from Telesign!")
    
    # Validate input
    if not phone:
        return jsonify({"error": "Phone number is required"}), 400
    
    # Get authentication token
    try:
        token = get_token()
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {token}",
        "x-API-key": "YOUR_TELESIGN_API_KEY",  # Replace with actual API key or env variable
        "Content-Type": "application/json"
    }
    
    # Prepare payload
    payload = {
        "phone_number": phone,
        "message": message,
        "message_type": "ARN"  # Adjust to TeleSign WhatsApp API specs
    }
    
    # Make API request
    try:
        res = requests.post(
            "https://rest-api.telesign.com/v1/messaging",
            headers=headers,
            json=payload,
            timeout=10
        )
        return jsonify(res.json()), res.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@flask_app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

# Add other Flask routes here as needed

if __name__ == "__main__":
    # This will only run if app.py is executed directly
    # When mounted in Starlette, this won't execute
    flask_app.run(debug=True, port=5000)