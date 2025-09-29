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
