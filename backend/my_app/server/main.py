import contextlib
import os
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware

from .app import api_app
from .mcp_server import mcp
from ..auth_server.main import auth_app
from .vapi_webhook import vapi_app
from .mcp_pool import mcp_pool
from ..config.settings import settings

def validate_production_security_config() -> None:
    """Fail fast if required production security secrets are missing."""
    if settings.ENVIRONMENT != "production":
        return

    required_secrets = {
        "MASTER_ENCRYPTION_KEY": os.getenv("MASTER_ENCRYPTION_KEY"),
        "ENCRYPTION_SALT": os.getenv("ENCRYPTION_SALT"),
        "JWT_SECRET_KEY": settings.JWT_SECRET_KEY,
    }

    missing = [name for name, value in required_secrets.items() if not value]

    if missing:
        raise RuntimeError(
            "Missing required production security configuration: "
            + ", ".join(missing)
        )
    
@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    validate_production_security_config()
    
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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Allow frontend to read response headers
)
