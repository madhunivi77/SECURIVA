from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import HTMLResponse, JSONResponse, Response
import httpx
from .chat_handler import execute_chat_with_tools

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

    # Create response with status and token
    response_data = {
        "status": "ok",
        "source": "Starlette",
        "token": token,
        "authenticated": token is not None
    }

    response = JSONResponse(response_data)

    # Set token as HttpOnly cookie if we got one
    if token:
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=3600  # 1 hour (matches JWT expiration)
        )

    return response

# Define chat endpoint that integrates with MCP tools
async def api_chat(request):
    try:
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
    ]
)