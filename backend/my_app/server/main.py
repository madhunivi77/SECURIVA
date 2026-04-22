import contextlib
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware

from .app import api_app
from .mcp_server import mcp
from ..auth_server.main import auth_app
from .vapi_webhook import vapi_app
from .mcp_pool import mcp_pool


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        mcp_pool.start_cleanup_task()
        yield
        await mcp_pool.close_all()


app = Starlette(
    routes=[
        Mount("/mcp", app=mcp.streamable_http_app()),
        Mount("/auth", app=auth_app),
        Mount("/api/vapi", app=vapi_app),
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
    expose_headers=["*"],  # Allow frontend to read response headers
)
