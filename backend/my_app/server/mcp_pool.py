"""
MCP Client Connection Pool.

Manages persistent per-user MCP connections with tool caching
to eliminate per-request connection overhead (~100-300ms savings).
"""

import asyncio
import time
from dataclasses import dataclass, field
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools
from .chat_handler import get_mcp_auth_token

MCP_SERVER_URL = "http://localhost:8000/mcp/"

# How long before we refresh cached tools (seconds)
TOOL_CACHE_TTL = 300  # 5 minutes

# How long before we close idle connections (seconds)
IDLE_TIMEOUT = 300  # 5 minutes

# JWT tokens expire after 1 hour; refresh at 55 min
TOKEN_REFRESH_THRESHOLD = 55 * 60  # 55 minutes


@dataclass
class MCPConnection:
    """Holds an active MCP connection for a single user."""
    user_id: str
    session: ClientSession
    tools: list = field(default_factory=list)
    tools_loaded_at: float = 0.0
    token_issued_at: float = 0.0
    last_used: float = field(default_factory=time.monotonic)
    _context_stack: object = None  # AsyncExitStack holding the transport

    def touch(self):
        self.last_used = time.monotonic()

    @property
    def is_idle(self) -> bool:
        return (time.monotonic() - self.last_used) > IDLE_TIMEOUT

    @property
    def tools_expired(self) -> bool:
        return (time.monotonic() - self.tools_loaded_at) > TOOL_CACHE_TTL

    @property
    def token_needs_refresh(self) -> bool:
        return (time.monotonic() - self.token_issued_at) > TOKEN_REFRESH_THRESHOLD


class MCPClientPool:
    """
    Per-user MCP connection pool with tool caching.

    Usage:
        pool = MCPClientPool()

        # In app lifespan startup:
        pool.start_cleanup_task()

        # Per request:
        conn = await pool.get_connection(user_id)
        tools = conn.tools  # cached LangChain StructuredTool objects

        # In app lifespan shutdown:
        await pool.close_all()
    """

    def __init__(self):
        self._connections: dict[str, MCPConnection] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None

    def _get_lock(self, user_id: str) -> asyncio.Lock:
        if user_id not in self._locks:
            self._locks[user_id] = asyncio.Lock()
        return self._locks[user_id]

    async def get_connection(self, user_id: str) -> MCPConnection:
        """
        Get or create an MCP connection for a user.
        Returns a connection with cached tools ready to use.
        """
        lock = self._get_lock(user_id)
        async with lock:
            conn = self._connections.get(user_id)

            # Reuse existing connection if still valid
            if conn is not None:
                try:
                    # Refresh tools if cache expired
                    if conn.tools_expired:
                        conn.tools = await load_mcp_tools(conn.session)
                        conn.tools_loaded_at = time.monotonic()
                        print(f"[MCP_POOL] Refreshed tools for user={user_id} ({len(conn.tools)} tools)")

                    conn.touch()
                    return conn
                except Exception:
                    # Connection is dead, clean up and recreate
                    await self._close_connection(user_id)

            # Create new connection
            return await self._create_connection(user_id)

    async def _create_connection(self, user_id: str) -> MCPConnection:
        """Create a new MCP connection for a user."""
        t0 = time.perf_counter()

        # Get JWT token
        token = await get_mcp_auth_token(user_id)
        if not token:
            raise RuntimeError(f"Could not retrieve MCP auth token for user={user_id}")

        auth_headers = {"Authorization": f"Bearer {token}"}

        # We need to manually manage the async context managers
        # since we're keeping the connection alive beyond a single `async with` block
        from contextlib import AsyncExitStack
        stack = AsyncExitStack()

        try:
            read, write, _ = await stack.enter_async_context(
                streamablehttp_client(MCP_SERVER_URL, headers=auth_headers)
            )
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            # Load tools
            tools = await load_mcp_tools(session)

            now = time.monotonic()
            conn = MCPConnection(
                user_id=user_id,
                session=session,
                tools=tools,
                tools_loaded_at=now,
                token_issued_at=now,
                last_used=now,
                _context_stack=stack,
            )

            self._connections[user_id] = conn

            elapsed = (time.perf_counter() - t0) * 1000
            print(f"[MCP_POOL] New connection for user={user_id} | {len(tools)} tools | {elapsed:.0f}ms")
            return conn

        except Exception:
            await stack.aclose()
            raise

    async def _close_connection(self, user_id: str):
        """Close and remove a connection."""
        conn = self._connections.pop(user_id, None)
        if conn and conn._context_stack:
            try:
                await conn._context_stack.aclose()
            except Exception as e:
                print(f"[MCP_POOL] Error closing connection for user={user_id}: {e}")
        self._locks.pop(user_id, None)

    async def close_all(self):
        """Close all connections. Call during app shutdown."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        user_ids = list(self._connections.keys())
        for uid in user_ids:
            await self._close_connection(uid)
        print(f"[MCP_POOL] Closed all connections ({len(user_ids)} total)")

    async def _cleanup_loop(self):
        """Periodically close idle connections."""
        while True:
            await asyncio.sleep(60)  # Check every minute
            idle_users = [
                uid for uid, conn in self._connections.items()
                if conn.is_idle
            ]
            for uid in idle_users:
                print(f"[MCP_POOL] Closing idle connection for user={uid}")
                await self._close_connection(uid)

    def start_cleanup_task(self):
        """Start the background cleanup task. Call during app startup."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())


# Singleton instance
mcp_pool = MCPClientPool()
