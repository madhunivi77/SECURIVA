"""
MCP Client Connection Pool.

Manages persistent per-user MCP connections with tool caching
to eliminate per-request connection overhead (~100-300ms savings).

Each user has one connection to the internal MCP server and, if
COMPOSIO_API_KEY is set, a second connection to Composio's tool
router. Tools from both are merged into a single catalog.
"""

import asyncio
import os
import time
from dataclasses import dataclass, field
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools
from .chat_handler import get_mcp_auth_token

from ..config.settings import settings
MCP_SERVER_URL = settings.MCP_SERVER_URL

COMPOSIO_ENABLED = bool(os.getenv("COMPOSIO_API_KEY"))
_composio_client = None
if COMPOSIO_ENABLED:
    try:
        from composio import Composio
        _composio_client = Composio()
    except Exception as e:
        print(f"[MCP_POOL] Composio import failed, disabling: {e}")
        COMPOSIO_ENABLED = False

# Tool filters for A/B testing internal vs Composio coverage
_GMAIL_TOOL_NAMES = {
    "listEmails",
    "createGmailDraft",
    "listGmailDrafts",
    "editGmailDraft",
    "getEmailBodies",
    "summarizeEmail",
    "summarizeRecentEmails",
}
_DISABLED_TOOL_NAMES: set[str] = set()
if os.getenv("DISABLE_INTERNAL_GMAIL", "").lower() in ("1", "true", "yes"):
    _DISABLED_TOOL_NAMES |= _GMAIL_TOOL_NAMES
# Free-form comma list (for future overrides)
for name in filter(None, (s.strip() for s in os.getenv("DISABLED_TOOLS", "").split(","))):
    _DISABLED_TOOL_NAMES.add(name)

# Hard kill switch: drop all tools from the internal MCP server (Composio-only mode)
_DISABLE_ALL_INTERNAL = os.getenv("DISABLE_ALL_INTERNAL_TOOLS", "").lower() in ("1", "true", "yes")


def _filter_disabled(tools):
    if _DISABLE_ALL_INTERNAL:
        if tools:
            print(f"[MCP_POOL] Dropping all {len(tools)} internal tools (DISABLE_ALL_INTERNAL_TOOLS=true)")
        return []
    if not _DISABLED_TOOL_NAMES:
        return tools
    kept = [t for t in tools if getattr(t, "name", None) not in _DISABLED_TOOL_NAMES]
    dropped = len(tools) - len(kept)
    if dropped:
        print(f"[MCP_POOL] Filtered {dropped} disabled tools")
    return kept

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
    _context_stack: object = None  # AsyncExitStack — kept for ref, but NOT safe to aclose() cross-task
    _read_stream: object = None   # anyio memory stream (safe to close from any task)
    _write_stream: object = None  # anyio memory stream (safe to close from any task)
    _composio_session: ClientSession | None = None
    _composio_read_stream: object = None
    _composio_write_stream: object = None

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
                # If JWT token is near expiry, recreate connection with fresh token
                if conn.token_needs_refresh:
                    print(f"[MCP_POOL] Token near expiry for user={user_id}, recreating connection")
                    await self._close_connection(user_id)
                    return await self._create_connection(user_id)

                try:
                    # Health-check: lightweight ping to verify session is alive
                    await conn.session.list_tools()
                    print(f"[MCP_POOL] Health check passed for user={user_id}")

                    # Refresh tools if cache expired
                    if conn.tools_expired:
                        refreshed = _filter_disabled(await load_mcp_tools(conn.session))
                        if conn._composio_session is not None:
                            try:
                                refreshed = refreshed + await load_mcp_tools(conn._composio_session)
                            except Exception as e:
                                print(f"[MCP_POOL] Composio tool refresh failed for user={user_id}: {e}")
                        conn.tools = refreshed
                        conn.tools_loaded_at = time.monotonic()
                        print(f"[MCP_POOL] Refreshed tools for user={user_id} ({len(conn.tools)} tools)")

                    conn.touch()
                    return conn
                except Exception as e:
                    # Connection is dead, clean up and recreate
                    print(f"[MCP_POOL] Health check failed for user={user_id}: {e}")
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

            # Load internal tools
            tools = _filter_disabled(await load_mcp_tools(session))

            # Optionally connect to Composio as a second MCP server
            composio_session = None
            composio_read = None
            composio_write = None
            composio_tool_count = 0
            if COMPOSIO_ENABLED and _composio_client is not None:
                try:
                    composio_session_info = _composio_client.create(user_id=user_id)
                    c_read, c_write, _ = await stack.enter_async_context(
                        streamablehttp_client(
                            composio_session_info.mcp.url,
                            headers=composio_session_info.mcp.headers,
                        )
                    )
                    composio_session = await stack.enter_async_context(ClientSession(c_read, c_write))
                    await composio_session.initialize()
                    composio_tools = await load_mcp_tools(composio_session)
                    tools = tools + composio_tools
                    composio_read = c_read
                    composio_write = c_write
                    composio_tool_count = len(composio_tools)
                except Exception as e:
                    print(f"[MCP_POOL] Composio connection failed for user={user_id} (continuing without): {e}")

            now = time.monotonic()
            conn = MCPConnection(
                user_id=user_id,
                session=session,
                tools=tools,
                tools_loaded_at=now,
                token_issued_at=now,
                last_used=now,
                _context_stack=stack,
                _read_stream=read,
                _write_stream=write,
                _composio_session=composio_session,
                _composio_read_stream=composio_read,
                _composio_write_stream=composio_write,
            )

            self._connections[user_id] = conn

            elapsed = (time.perf_counter() - t0) * 1000
            print(
                f"[MCP_POOL] New connection for user={user_id} | "
                f"{len(tools)} tools total ({composio_tool_count} composio) | {elapsed:.0f}ms"
            )
            return conn

        except Exception:
            await stack.aclose()
            raise

    async def invalidate(self, user_id: str):
        """Invalidate a user's connection so the next get_connection() creates a fresh one."""
        lock = self._get_lock(user_id)
        async with lock:
            if user_id in self._connections:
                print(f"[MCP_POOL] Invalidating connection for user={user_id}")
                await self._close_connection(user_id)

    async def _close_connection(self, user_id: str):
        """Close and remove a connection.

        Closes individual memory streams instead of the AsyncExitStack,
        because the stack contains anyio CancelScopes that are task-bound
        and cannot be closed from a different task (e.g. the cleanup loop).
        anyio memory streams have no task affinity and are safe to close anywhere.
        """
        conn = self._connections.pop(user_id, None)
        if conn:
            streams = (
                conn._read_stream,
                conn._write_stream,
                conn._composio_read_stream,
                conn._composio_write_stream,
            )
            for stream in streams:
                if stream:
                    try:
                        await stream.aclose()
                    except Exception:
                        pass
            # Do NOT call conn._context_stack.aclose() — it's task-bound
        self._locks.pop(user_id, None)

    async def close_all(self):
        """Close all connections. Call during app shutdown.

        Uses the same stream-level cleanup as _close_connection() to avoid
        cross-task AsyncExitStack issues. During shutdown, remaining resources
        are reclaimed by the OS.
        """
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
