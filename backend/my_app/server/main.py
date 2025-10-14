import contextlib
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware

# Import your app instances from the other files
from .app import api_app
from .mcp_server import mcp
from ..auth_server.main import auth_app

# This lifespan function manages the MCP server's session manager
@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        yield

# Create the main Starlette application with all services mounted
app = Starlette(
    routes=[
        # Mount the MCP server under the /mcp path
        Mount("/mcp", app=mcp.streamable_http_app()),

        # Mount the Auth server under the /auth path
        Mount("/auth", app=auth_app),

        # Mount the API app at the root path
        Mount("/", app=api_app)
    ],
    lifespan=lifespan
)

# Add CORS middleware at the top level to cover all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
