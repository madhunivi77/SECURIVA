"""
Chat handler — OpenAI SDK + Composio direct (no LangChain, no MCP router)

Flow:
  1. classify route + run policy validation
  2. fetch internal tools via our MCP (only when route needs them)
  3. fetch Composio tools directly via SDK with semantic search — no SEARCH_TOOLS meta-round
  4. manual tool-call loop: call OpenAI → if tool_calls, execute, loop (max 3 rounds)
  5. log tool calls to tool_logger
"""

import os
import json
import httpx
import re
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from .tool_logger import get_tool_logger
from .grounded_chat_policy import prepare_messages_for_agent, should_use_grounded_guidance
from .request_validator import should_block_request
from ..config.settings import settings

# ─────────────────────────────── Composio ───────────────────────────────
_composio = None
if os.getenv("COMPOSIO_API_KEY"):
    try:
        from composio import Composio
        from composio_openai import OpenAIProvider
        _composio = Composio(provider=OpenAIProvider())
    except Exception as _e:
        print(f"[CHAT] Composio import failed: {_e}")

# Composio meta-tools we never want to expose to the chat LLM
# (connections are managed via /integrations UI, not by the agent)
_COMPOSIO_HIDDEN = {"COMPOSIO_MANAGE_CONNECTIONS"}

# ─────────────────────────────── Env flags ──────────────────────────────
_DISABLE_ALL_INTERNAL_TOOLS = (
    os.getenv("DISABLE_ALL_INTERNAL_TOOLS", "").lower() in ("1", "true", "yes")
)
_GMAIL_TOOL_NAMES = {
    "listEmails", "createGmailDraft", "listGmailDrafts", "editGmailDraft",
    "getEmailBodies", "summarizeEmail", "summarizeRecentEmails",
}
_DISABLED_TOOLS_SET: set[str] = set()
if os.getenv("DISABLE_INTERNAL_GMAIL", "").lower() in ("1", "true", "yes"):
    _DISABLED_TOOLS_SET |= _GMAIL_TOOL_NAMES
for _name in filter(None, (s.strip() for s in os.getenv("DISABLED_TOOLS", "").split(","))):
    _DISABLED_TOOLS_SET.add(_name)

# ─────────────────────────────── Config ─────────────────────────────────
MCP_SERVER_URL = settings.MCP_SERVER_URL
AUTH_SERVER_URL = settings.AUTH_SERVER_URL

config_path = Path(__file__).parent.parent / "client" / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

DEFAULT_MODEL = config.get("model", "gpt-4.1")
MAX_TOOL_ROUNDS = 3
COMPOSIO_TOOL_LIMIT = 25  # ~5 tools × 5 toolkits. ~8-10K tokens of tool schemas.

# Explicit high-value tool slugs per toolkit. Composio's `toolkits=[...]` filter
# returns tools ALPHABETICALLY (not by importance), which starves us of the
# actual fetch/send/list tools (they sort late). By requesting tool slugs
# explicitly we sidestep issue #2978 and guarantee coverage.
TOOLKIT_DEFAULTS: dict[str, list[str]] = {
    "gmail": [
        "GMAIL_FETCH_EMAILS",
        "GMAIL_SEND_EMAIL",
        "GMAIL_CREATE_EMAIL_DRAFT",
        "GMAIL_LIST_THREADS",
        "GMAIL_SEARCH_EMAIL",
        "GMAIL_REPLY_TO_THREAD",
    ],
    "googlecalendar": [
        "GOOGLECALENDAR_EVENTS_LIST",
        "GOOGLECALENDAR_CREATE_EVENT",
        "GOOGLECALENDAR_UPDATE_EVENT",
        "GOOGLECALENDAR_DELETE_EVENT",
        "GOOGLECALENDAR_LIST_CALENDARS",
        "GOOGLECALENDAR_FIND_FREE_SLOTS",
    ],
    "googledrive": [
        "GOOGLEDRIVE_LIST_FILES",
        "GOOGLEDRIVE_SEARCH_FILES",
        "GOOGLEDRIVE_GET_FILE",
        "GOOGLEDRIVE_CREATE_FILE",
        "GOOGLEDRIVE_DELETE_FILE",
    ],
    "googledocs": [
        "GOOGLEDOCS_CREATE_DOCUMENT",
        "GOOGLEDOCS_GET_DOCUMENT_BY_ID",
        "GOOGLEDOCS_UPDATE_DOCUMENT",
        "GOOGLEDOCS_INSERT_TEXT",
    ],
    "googlesheets": [
        "GOOGLESHEETS_SPREADSHEETS_CREATE",
        "GOOGLESHEETS_GET_SPREADSHEET",
        "GOOGLESHEETS_BATCH_UPDATE_SPREADSHEET",
        "GOOGLESHEETS_VALUES_APPEND",
        "GOOGLESHEETS_VALUES_GET",
    ],
    "slack": [
        "SLACK_SEND_MESSAGE",
        "SLACK_LIST_CHANNELS",
        "SLACK_LIST_MESSAGES",
        "SLACK_SEARCH_MESSAGES",
    ],
    "github": [
        "GITHUB_LIST_REPOSITORIES",
        "GITHUB_CREATE_ISSUE",
        "GITHUB_LIST_ISSUES",
        "GITHUB_SEARCH_REPOSITORIES",
    ],
    "notion": [
        "NOTION_SEARCH",
        "NOTION_CREATE_PAGE",
        "NOTION_GET_PAGE",
        "NOTION_UPDATE_PAGE",
    ],
}

# Singleton OpenAI client
_openai_client: AsyncOpenAI | None = None
def _get_openai() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client


# Groq uses the OpenAI-compatible API at a different base URL. Same SDK, same
# streaming semantics, ~5-10× faster inference. Used by voice for tool-call
# decisions (see voice_agent.py); chat stays on OpenAI for determinism.
_groq_client: AsyncOpenAI | None = None
def _get_groq() -> AsyncOpenAI | None:
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    _groq_client = AsyncOpenAI(
        api_key=key, base_url="https://api.groq.com/openai/v1"
    )
    return _groq_client

# Cache connected toolkits per user (5s TTL) — short enough that newly-connected
# toolkits show up within a turn or two without hammering Composio on every message.
_CONNECTED_TOOLKITS_TTL = 5.0
_connected_toolkits_cache: dict[str, tuple[float, list[str]]] = {}

# Cache the merged tool list per user (20s TTL, keyed on the toolkit set).
# Saves ~200ms of parallel per-toolkit fetches on every chat turn.
_TOOLS_CACHE_TTL = 20.0
_tools_cache: dict[str, tuple[float, tuple, list[dict]]] = {}
# value = (expires_at, toolkits_snapshot, tool_list)

# Tool catalog — per user, one lightweight list of {name, short description}.
# Built once per toolkit set, reused by the LLM router every turn. No
# embeddings. No cosine similarity. Just strings the router LLM reads.
MAX_TOOLS_PER_TOOLKIT = 200


class _ToolCatalog:
    """Per-user cached tool list + prebuilt catalog string for the router."""

    def __init__(self, tools: list[dict], toolkits_snapshot: tuple[str, ...]):
        self.tools = tools
        self.toolkits_snapshot = toolkits_snapshot
        self.built_at = time.time()
        self._catalog_str: str | None = None

    @property
    def catalog_str(self) -> str:
        if self._catalog_str is None:
            self._catalog_str = _build_tool_catalog(self.tools)
        return self._catalog_str


# user_id → _ToolCatalog. Rebuilt when connected toolkit set changes.
_tool_catalog_cache: dict[str, _ToolCatalog] = {}


async def _get_connected_toolkits(user_id: str) -> list[str]:
    if not user_id or _composio is None:
        return []
    now = time.time()
    cached = _connected_toolkits_cache.get(user_id)
    if cached and (now - cached[0]) < _CONNECTED_TOOLKITS_TTL:
        return cached[1]
    try:
        import asyncio
        def _list():
            return _composio.connected_accounts.list(user_ids=[user_id])
        res = await asyncio.to_thread(_list)
        slugs: list[str] = []
        for item in getattr(res, "items", []) or []:
            status = getattr(item, "status", None)
            if status and status != "ACTIVE":
                continue
            toolkit = getattr(item, "toolkit", None)
            slug = getattr(toolkit, "slug", None) if toolkit else None
            if slug:
                slugs.append(slug)
        _connected_toolkits_cache[user_id] = (now, slugs)
        return slugs
    except Exception as e:
        print(f"[CHAT] connected_toolkits fetch failed for user={user_id}: {e}")
        return []

# ───────────────────────── Route classification ─────────────────────────
GROUNDED_GUIDANCE_TOOL_NAMES = frozenset({
    "getGroundedSecurityGuidance",
    "getComplianceOverview", "getComplianceRequirements", "getComplianceChecklist",
    "getPenaltyInformation", "getBreachNotificationRequirements",
    "crossReferenceComplianceTopic", "searchComplianceRequirements",
})
COMPLIANCE_REFERENCE_TOOL_NAMES = frozenset({
    "getComplianceOverview", "getComplianceRequirements", "getComplianceChecklist",
    "getPenaltyInformation", "getBreachNotificationRequirements",
    "crossReferenceComplianceTopic", "searchComplianceRequirements",
})
COMPLIANCE_REPORT_TOOL_NAMES = frozenset({
    "confirmComplianceUnderstanding", "summarizeComplianceRequest",
    "validateComplianceParameters", "generateComplianceReport",
})
COMPLIANCE_REFERENCE_REQUEST_PATTERN = re.compile(
    r"\b(requirements?|checklist|penalt(?:y|ies)|fine|fines|breach notification|overview|"
    r"compare|comparison|cross[- ]reference|search|standard|standards)\b",
    re.IGNORECASE,
)
COMPLIANCE_REPORT_REQUEST_PATTERN = re.compile(
    r"\b(generate|create|build|draft|prepare)\b.*\b(report|checklist|assessment|summary)\b|"
    r"\bcompliance report\b",
    re.IGNORECASE,
)
COMPLIANCE_REGULATION_PATTERN = re.compile(
    r"\b(gdpr|hipaa|pci[ -]?dss|ccpa|sox)\b",
    re.IGNORECASE,
)


def get_latest_user_message_content(messages: list) -> str:
    for m in reversed(messages):
        role = m.get("role") if isinstance(m, dict) else getattr(m, "role", None)
        content = m.get("content", "") if isinstance(m, dict) else getattr(m, "content", "")
        if role == "user":
            return content or ""
    return ""


def classify_tool_route(messages: list) -> str:
    latest = get_latest_user_message_content(messages)
    if not latest:
        return "default"
    if should_use_grounded_guidance(messages):
        return "grounded_guidance"
    if COMPLIANCE_REPORT_REQUEST_PATTERN.search(latest):
        return "compliance_report"
    has_reg = bool(COMPLIANCE_REGULATION_PATTERN.search(latest))
    has_ref = bool(COMPLIANCE_REFERENCE_REQUEST_PATTERN.search(latest))
    if has_reg and has_ref:
        return "compliance_reference"
    return "default"


def _route_allowlist(route: str) -> frozenset | None:
    return {
        "grounded_guidance": GROUNDED_GUIDANCE_TOOL_NAMES,
        "compliance_reference": COMPLIANCE_REFERENCE_TOOL_NAMES,
        "compliance_report": COMPLIANCE_REFERENCE_TOOL_NAMES | COMPLIANCE_REPORT_TOOL_NAMES,
    }.get(route)


# ────────────────────────── Internal MCP helpers ────────────────────────
async def get_mcp_auth_token(user_id: str | None = None) -> str | None:
    """Fetch internal MCP auth token (still needed for voice + internal routes)."""
    try:
        async with httpx.AsyncClient() as client:
            body = {"user_id": user_id} if user_id else {}
            r = await client.post(AUTH_SERVER_URL, json=body)
            r.raise_for_status()
            return r.json()["access_token"]
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"[CHAT] auth token fetch failed: {e}")
        return None


def _tool_name(openai_tool: dict) -> str:
    """OpenAI tool shape: {'type': 'function', 'function': {'name': ...}}."""
    return openai_tool.get("function", {}).get("name", "")


def _mcp_to_openai(mcp_tool) -> dict:
    """Convert an MCP tool schema into OpenAI tool-format dict."""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": (mcp_tool.description or "")[:1024],
            "parameters": mcp_tool.inputSchema or {"type": "object", "properties": {}},
        },
    }


@asynccontextmanager
async def _internal_mcp_session(user_id: str | None):
    """Open an MCP session to our own server. Yields (session, [openai_tools])."""
    token = await get_mcp_auth_token(user_id)
    if not token:
        yield None, []
        return
    auth_headers = {"Authorization": f"Bearer {token}"}
    try:
        async with streamablehttp_client(MCP_SERVER_URL, headers=auth_headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                tools = []
                for t in result.tools:
                    if t.name in _DISABLED_TOOLS_SET:
                        continue
                    tools.append(_mcp_to_openai(t))
                yield session, tools
    except Exception as e:
        print(f"[CHAT] internal MCP session failed: {e}")
        yield None, []


# ────────────────────── Composio direct-tool fetch ──────────────────────
async def ensure_tool_catalog_ready(user_id: str) -> bool:
    """
    Idempotently build the user's tool catalog. Safe to call from a
    fire-and-forget pre-warm endpoint. No embeddings — just fetch tools
    and cache the (name, description) list.
    """
    if _composio is None or not user_id:
        return False
    connected = await _get_connected_toolkits(user_id)
    if not connected:
        return False
    snap = tuple(sorted(connected))
    cat = _tool_catalog_cache.get(user_id)
    if cat is not None and cat.toolkits_snapshot == snap:
        return True  # already warm
    cat = await _build_tool_catalog_index(user_id, list(snap))
    if cat is not None:
        _tool_catalog_cache[user_id] = cat
        return True
    return False


async def _build_tool_catalog_index(user_id: str, toolkits: list[str]) -> _ToolCatalog | None:
    """Fetch tools per connected toolkit, dedupe, cache. No embedding step."""
    if _composio is None or not toolkits:
        return None
    import asyncio

    async def _fetch_one(tk: str) -> list[dict]:
        def _run():
            return _composio.tools.get(
                user_id=user_id,
                toolkits=[tk],
                limit=MAX_TOOLS_PER_TOOLKIT,
            )
        try:
            return await asyncio.to_thread(_run)
        except Exception as e:
            print(f"[CHAT][catalog]   toolkit={tk} fetch failed: {e}")
            return []

    t_fetch_start = time.time()
    results = await asyncio.gather(*[_fetch_one(tk) for tk in toolkits])
    seen: set[str] = set()
    all_tools: list[dict] = []
    per_kit_counts: dict[str, int] = {}
    for tk, tools in zip(toolkits, results):
        kept = 0
        for t in tools:
            name = _tool_name(t)
            if not name or name in _COMPOSIO_HIDDEN or name in seen:
                continue
            seen.add(name)
            all_tools.append(t)
            kept += 1
        per_kit_counts[tk] = kept
    t_fetch_ms = (time.time() - t_fetch_start) * 1000

    if not all_tools:
        return None

    print(
        f"[CHAT][catalog] built for user={user_id} | fetch={t_fetch_ms:.0f}ms "
        f"| {len(all_tools)} tools | counts={per_kit_counts}"
    )
    return _ToolCatalog(
        tools=all_tools,
        toolkits_snapshot=tuple(sorted(toolkits)),
    )


# ─────────────────────────── LLM tool router ───────────────────────────
# Groq reads the actual conversation + a lightweight catalog and picks
# the tools relevant to the user's LATEST intent. If it fails, fall back
# to hardcoded TOOLKIT_DEFAULTS so chat never ends up toolless.

ROUTE_MODEL = "llama-3.1-8b-instant"    # ~80ms TTFT, 620 tok/s on Groq LPU
CHAT_ROUTE_TOP_K = 10
ROUTE_MAX_MSGS = 6                      # last N user/assistant turns sent to router
ROUTE_MAX_MSG_CHARS = 500               # truncate each message before routing
ROUTE_TIMEOUT_S = 3.0                   # fall back to defaults past this

# Groq's llama-3.1-8b-instant free tier has a 6000 TPM limit. After reserving
# ~1500 tokens for the system prompt, trimmed messages, and response, the
# catalog itself can use ~4500 tokens. If the full catalog (name + description)
# exceeds that, _build_tool_catalog progressively shortens — 80→40→20→names-only.
_ROUTER_CATALOG_TOKEN_BUDGET = 4500
_CHARS_PER_TOKEN = 4                    # rough estimate for English


def _build_tool_catalog(tools: list[dict]) -> str:
    """One line per tool (hidden tools excluded). Adaptive: shrinks description
    length if the full catalog would blow the router's token budget. Tool names
    follow Composio's `TOOLKIT_ACTION` convention and are self-documenting —
    dropping descriptions entirely is still usable as a last resort.
    """
    visible: list[tuple[str, str]] = []
    for t in tools:
        fn = t.get("function", {}) or {}
        name = fn.get("name", "") or ""
        if not name or name in _COMPOSIO_HIDDEN:
            continue
        desc = (fn.get("description", "") or "").replace("\n", " ").strip()
        visible.append((name, desc))

    budget_chars = _ROUTER_CATALOG_TOKEN_BUDGET * _CHARS_PER_TOKEN
    for desc_len in (80, 40, 20, 0):
        if desc_len == 0:
            lines = [name for name, _ in visible]
        else:
            lines = [
                f"{name} — {desc[:desc_len]}" if desc else name
                for name, desc in visible
            ]
        catalog = "\n".join(lines)
        if len(catalog) <= budget_chars:
            if desc_len < 80:
                print(
                    f"[CHAT][catalog] shrunk desc→{desc_len} chars "
                    f"({len(visible)} tools, catalog≈{len(catalog)//_CHARS_PER_TOKEN} tok, budget={_ROUTER_CATALOG_TOKEN_BUDGET})"
                )
            return catalog
    # Names-only still over budget — return it anyway; router will get a 413 and fall back
    return catalog


def _trim_messages_for_router(messages: list) -> list[dict]:
    """Last N user/assistant turns, each truncated. Skips system/tool roles."""
    kept: list[dict] = []
    for m in reversed(messages):
        if not isinstance(m, dict):
            continue
        role = m.get("role")
        if role not in ("user", "assistant"):
            continue
        content = m.get("content") or ""
        if not content:
            continue
        kept.append({"role": role, "content": content[:ROUTE_MAX_MSG_CHARS]})
        if len(kept) >= ROUTE_MAX_MSGS:
            break
    kept.reverse()
    return kept


# Counter for how often we silently degrade to a fallback. Visible in [CHAT][DEGRADED]
# log lines so drift is impossible to miss during operation.
_DEGRADED_ROUTER_CALLS = {"count": 0}


async def _router_degraded(
    user_id: str, connected: list[str], top_k: int, reason: str
) -> list[dict]:
    """Groq router failed — log loudly, bump the counter, then use hardcoded
    TOOLKIT_DEFAULTS. We deliberately do NOT pass the full catalog to the main
    LLM: the whole point of the router is to select tools; bypassing it defeats
    the design and burns main-LLM tokens. Fix the router instead of routing
    around it — the warning and counter exist so this degradation is visible.
    """
    _DEGRADED_ROUTER_CALLS["count"] += 1
    print(
        f"⚠️  [CHAT][DEGRADED] router failed, using TOOLKIT_DEFAULTS: {reason} | "
        f"user={user_id} | total_degraded_calls={_DEGRADED_ROUTER_CALLS['count']}"
    )
    return await _fallback_to_defaults(user_id, connected, top_k)


async def _fallback_to_defaults(user_id: str, connected: list[str], top_k: int) -> list[dict]:
    """
    Last-resort fallback when the Groq router is down or misbehaves.
    Fetches the hardcoded TOOLKIT_DEFAULTS for each connected toolkit. If the
    user has a toolkit we don't have defaults for, it contributes zero tools.
    """
    if _composio is None:
        return []
    slugs: list[str] = []
    covered: list[str] = []
    missing: list[str] = []
    for tk in connected:
        defaults = TOOLKIT_DEFAULTS.get(tk.lower())
        if defaults:
            slugs.extend(defaults)
            covered.append(tk)
        else:
            missing.append(tk)
    if not slugs:
        print(f"[CHAT][fallback] user={user_id}: no defaults for any connected toolkit")
        return []

    import asyncio
    def _run():
        return _composio.tools.get(user_id=user_id, tools=slugs)
    try:
        tools = await asyncio.to_thread(_run)
    except Exception as e:
        print(f"[CHAT][fallback] tools.get failed: {e}")
        return []
    result = [t for t in tools if _tool_name(t) not in _COMPOSIO_HIDDEN][:top_k]
    print(
        f"[CHAT][fallback] user={user_id}: defaults → {len(result)} tools | "
        f"covered={covered} missing={missing}"
    )
    return result


async def _route_tools_via_llm(
    user_id: str,
    messages: list,
    top_k: int = CHAT_ROUTE_TOP_K,
) -> list[dict]:
    """
    LLM-as-router: Groq reads full conversation + catalog → picks tool names.
    Returns the corresponding full tool schemas. Falls back to
    TOOLKIT_DEFAULTS (no embeddings) if Groq is down.
    """
    if _composio is None or not user_id:
        return []
    connected = await _get_connected_toolkits(user_id)
    if not connected:
        print(f"[CHAT][route] user={user_id}: no connected toolkits → zero tools")
        return []

    toolkits_snap = tuple(sorted(connected))

    # Load / build the tool catalog (no embeddings; just fetch + dedupe)
    cat = _tool_catalog_cache.get(user_id)
    if cat is None or cat.toolkits_snapshot != toolkits_snap:
        cat = await _build_tool_catalog_index(user_id, list(toolkits_snap))
        if cat is not None:
            _tool_catalog_cache[user_id] = cat
    if cat is None or not cat.tools:
        return await _fallback_to_defaults(user_id, connected, top_k)

    groq = _get_groq()
    if groq is None:
        return await _router_degraded(
            user_id, connected, top_k, reason="GROQ_API_KEY not set"
        )

    trimmed = _trim_messages_for_router(messages)
    if not trimmed:
        return await _router_degraded(
            user_id, connected, top_k, reason="empty trimmed-messages payload"
        )

    sys_prompt = (
        "You are a tool router for a productivity assistant. Given a "
        "conversation and a catalog of available tools, select the tools "
        "most useful for fulfilling the user's LATEST intent. If the user "
        "corrected themselves mid-turn, trust the most recent clarification "
        "and ignore the earlier intent.\n\n"
        f"Return strict JSON: {{\"tools\": [\"TOOL_NAME_1\", \"TOOL_NAME_2\"]}}. "
        f"Pick up to {top_k} tools. Only include names that appear verbatim in "
        "the catalog below. No prose, no explanations.\n\n"
        "Catalog (one per line: NAME — description):\n"
        f"{cat.catalog_str}"
    )

    import asyncio
    t0 = time.time()
    try:
        resp = await asyncio.wait_for(
            groq.chat.completions.create(
                model=ROUTE_MODEL,
                messages=[{"role": "system", "content": sys_prompt}] + trimmed,
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.0,
            ),
            timeout=ROUTE_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        return await _router_degraded(
            user_id, connected, top_k,
            reason=f"groq timed out >{ROUTE_TIMEOUT_S}s",
        )
    except Exception as e:
        return await _router_degraded(
            user_id, connected, top_k, reason=f"groq call failed: {e}"
        )
    t_ms = (time.time() - t0) * 1000

    raw = (resp.choices[0].message.content or "").strip()
    try:
        parsed = json.loads(raw)
        names = parsed.get("tools") if isinstance(parsed, dict) else None
        if not isinstance(names, list):
            raise ValueError(f"shape={type(parsed).__name__} raw={raw[:200]}")
    except Exception as e:
        return await _router_degraded(
            user_id, connected, top_k, reason=f"router JSON parse failed: {e}"
        )

    # Map names → full schemas, preserving router's ordering
    by_name = {_tool_name(t): t for t in cat.tools}
    ordered: list[dict] = []
    seen: set[str] = set()
    for n in names:
        if not isinstance(n, str) or n in seen:
            continue
        seen.add(n)
        t = by_name.get(n)
        if t and _tool_name(t) not in _COMPOSIO_HIDDEN:
            ordered.append(t)
    ordered = ordered[:top_k]

    if not ordered:
        return await _router_degraded(
            user_id, connected, top_k,
            reason=f"router returned 0 valid tools (raw names={names[:10]})",
        )

    print(
        f"[CHAT][route] user={user_id} groq={t_ms:.0f}ms | "
        f"picked {len(ordered)}/{len(names)} valid | "
        f"names={[_tool_name(t) for t in ordered]}"
    )
    return ordered


async def _handle_composio_tool_calls(user_id: str, response) -> list:
    """
    Delegate to Composio's provider.handle_tool_calls — the canonical pattern.
    It knows about version-skip, arg-coercion, and provider-level telemetry.
    Returns a list of results in tool_call order.
    """
    import asyncio
    def _run():
        return _composio.provider.handle_tool_calls(
            user_id=user_id,
            response=response,
        )
    return await asyncio.to_thread(_run)


# ─────────────────────────── Main chat flow ─────────────────────────────
async def execute_chat_with_tools(
    messages: list,
    model: str | None = None,
    api: str | None = None,   # kept for signature compat; unused
    user_id: str | None = None,
) -> dict:
    """
    Execute a chat turn with tool-calling. Returns {response, tool_calls} or {error}.
    """
    model = model or DEFAULT_MODEL

    # 1. Validate / block
    should_block, rejection = should_block_request(messages)
    if should_block:
        return {"response": rejection, "tool_calls": [], "blocked": True}

    # 2. Route + policy
    route = classify_tool_route(messages)
    messages = prepare_messages_for_agent(messages)

    logger = get_tool_logger()
    session_id = str(uuid.uuid4())[:8]
    t0 = time.time()

    try:
        # 3. Fetch tools in parallel where possible. Internal MCP needs an open
        #    session for execution, so its context manager wraps the LLM loop.
        needs_internal = not (_DISABLE_ALL_INTERNAL_TOOLS and route == "default")

        composio_tools: list[dict] = []
        if route == "default":
            composio_tools = await _route_tools_via_llm(user_id, messages)

        if not needs_internal:
            # Pure Composio path — no MCP session needed
            print(
                f"[CHAT] user={user_id} route={route} (composio-only) "
                f"tools={len(composio_tools)}"
            )
            return await _run_tool_loop(
                messages=messages,
                model=model,
                openai_tools=composio_tools,
                internal_session=None,
                internal_tool_names=set(),
                user_id=user_id,
                session_id=session_id,
                logger=logger,
                t0=t0,
            )

        # Internal MCP path — session must stay open for tool execution
        async with _internal_mcp_session(user_id) as (session, internal_tools):
            internal_names = {_tool_name(t) for t in internal_tools}

            # Apply route allowlist to internal tools only
            allow = _route_allowlist(route)
            if allow:
                internal_tools = [t for t in internal_tools if _tool_name(t) in allow]

            all_tools = internal_tools + composio_tools
            print(
                f"[CHAT] user={user_id} route={route} tools: "
                f"internal={len(internal_tools)} composio={len(composio_tools)} "
                f"total={len(all_tools)}"
            )

            return await _run_tool_loop(
                messages=messages,
                model=model,
                openai_tools=all_tools,
                internal_session=session,
                internal_tool_names=internal_names,
                user_id=user_id,
                session_id=session_id,
                logger=logger,
                t0=t0,
            )

    except Exception as e:
        return {"error": f"Chat execution failed: {e}"}


# ─────────────────────────── Streaming flow ─────────────────────────────
async def execute_chat_with_tools_stream(
    messages: list,
    model: str | None = None,
    api: str | None = None,
    user_id: str | None = None,
):
    """
    Streaming variant of execute_chat_with_tools.

    Yields event dicts:
      {"type": "tool_start", "name": "...", "args": {...}}
      {"type": "tool_end",   "name": "...", "duration_ms": N, "error": ""}
      {"type": "token",      "content": "..."}
      {"type": "done",       "tool_calls": [...]}
      {"type": "error",      "error": "..."}
      {"type": "blocked",    "response": "..."}
    """
    model = model or DEFAULT_MODEL

    should_block, rejection = should_block_request(messages)
    if should_block:
        yield {"type": "blocked", "response": rejection}
        return

    route = classify_tool_route(messages)
    messages = prepare_messages_for_agent(messages)

    logger = get_tool_logger()
    session_id = str(uuid.uuid4())[:8]
    t0 = time.time()

    try:
        needs_internal = not (_DISABLE_ALL_INTERNAL_TOOLS and route == "default")

        composio_tools: list[dict] = []
        if route == "default":
            composio_tools = await _route_tools_via_llm(user_id, messages)

        if not needs_internal:
            print(
                f"[CHAT] user={user_id} route={route} (composio-only, stream) "
                f"tools={len(composio_tools)}"
            )
            async for event in _run_streaming_loop(
                messages=messages, model=model,
                openai_tools=composio_tools,
                internal_session=None, internal_tool_names=set(),
                user_id=user_id, session_id=session_id, logger=logger, t0=t0,
            ):
                yield event
            return

        async with _internal_mcp_session(user_id) as (session, internal_tools):
            internal_names = {_tool_name(t) for t in internal_tools}
            allow = _route_allowlist(route)
            if allow:
                internal_tools = [t for t in internal_tools if _tool_name(t) in allow]
            all_tools = internal_tools + composio_tools
            print(
                f"[CHAT] user={user_id} route={route} (stream) tools: "
                f"internal={len(internal_tools)} composio={len(composio_tools)} "
                f"total={len(all_tools)}"
            )
            async for event in _run_streaming_loop(
                messages=messages, model=model, openai_tools=all_tools,
                internal_session=session, internal_tool_names=internal_names,
                user_id=user_id, session_id=session_id, logger=logger, t0=t0,
            ):
                yield event
    except Exception as e:
        yield {"type": "error", "error": f"Chat execution failed: {e}"}


async def _run_streaming_loop(
    *, messages, model, openai_tools, internal_session, internal_tool_names,
    user_id, session_id, logger, t0,
):
    """
    Tool-calling loop with streamed tokens on the final (no-tool-call) round.

    Strategy: use OpenAI `stream=True` every round. Accumulate tool_call fragments
    server-side. If finish_reason is `tool_calls`, execute them and loop. If
    finish_reason is `stop`, we've already yielded tokens as they arrived.
    """
    client = _get_openai()
    tool_calls_log: list[dict] = []
    current = list(messages)

    def _llm_kwargs(msgs):
        kw = {"model": model, "messages": msgs, "stream": True}
        if openai_tools:
            kw["tools"] = openai_tools
        return kw

    for round_num in range(1, MAX_TOOL_ROUNDS + 1):
        t_llm_start = time.time()
        try:
            stream = await client.chat.completions.create(**_llm_kwargs(current))
        except Exception as e:
            yield {"type": "error", "error": f"LLM call failed (round {round_num}): {e}"}
            return

        # Accumulate stream: tokens can stream to client; tool_calls must be buffered
        content_buf = ""
        tool_calls_buf: dict[int, dict] = {}
        finish_reason: str | None = None
        assistant_content_for_history: str | None = None

        async for chunk in stream:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta

            # Capture finish reason
            if choice.finish_reason:
                finish_reason = choice.finish_reason

            # Tool-call fragments arrive incrementally (by index)
            if delta.tool_calls:
                for tc_d in delta.tool_calls:
                    idx = tc_d.index
                    slot = tool_calls_buf.setdefault(
                        idx, {"id": "", "name": "", "args": ""}
                    )
                    if tc_d.id:
                        slot["id"] = tc_d.id
                    if tc_d.function:
                        if tc_d.function.name:
                            slot["name"] += tc_d.function.name
                        if tc_d.function.arguments:
                            slot["args"] += tc_d.function.arguments

            # Content tokens — stream live UNLESS we've seen tool_calls this round
            if delta.content:
                content_buf += delta.content
                if not tool_calls_buf:
                    yield {"type": "token", "content": delta.content}

        t_llm_ms = (time.time() - t_llm_start) * 1000
        print(
            f"[CHAT] round_{round_num} llm(stream): {t_llm_ms:.0f}ms "
            f"| tool_calls={len(tool_calls_buf)} | content_len={len(content_buf)}"
        )

        # Final round (no tool calls) — content already yielded; emit done
        if not tool_calls_buf:
            total = (time.time() - t0) * 1000
            print(f"[CHAT] TOTAL: {total:.0f}ms | rounds={round_num} | stream")
            yield {"type": "done", "tool_calls": [tc["name"] for tc in tool_calls_log]}
            return

        # Tool-calling round — record assistant tool_calls in message history
        ordered = [tool_calls_buf[i] for i in sorted(tool_calls_buf.keys())]
        current.append({
            "role": "assistant",
            "content": content_buf or None,
            "tool_calls": [
                {"id": tc["id"], "type": "function",
                 "function": {"name": tc["name"], "arguments": tc["args"]}}
                for tc in ordered
            ],
        })

        # Execute tool calls
        for tc in ordered:
            name = tc["name"]
            try:
                args = json.loads(tc["args"] or "{}")
            except json.JSONDecodeError:
                args = {}

            yield {"type": "tool_start", "name": name, "args": args}

            t_tool_start = time.time()
            error_msg = ""
            try:
                if name in internal_tool_names:
                    if internal_session is None:
                        raise RuntimeError("Internal session is closed")
                    raw = await internal_session.call_tool(name, args)
                    content_parts = getattr(raw, "content", []) or []
                    text = "\n".join(
                        getattr(p, "text", "") or ""
                        for p in content_parts
                        if getattr(p, "text", None) is not None
                    )
                    result = text or json.dumps(raw, default=str)
                else:
                    def _exec(_n=name, _a=args):
                        return _composio.tools.execute(
                            _n, user_id=user_id or "", arguments=_a,
                            dangerously_skip_version_check=True,
                        )
                    import asyncio
                    result = await asyncio.to_thread(_exec)
                    result = (
                        json.dumps(result, default=str)
                        if not isinstance(result, str) else result
                    )
            except Exception as e:
                error_msg = str(e)
                result = f"Tool error: {e}"

            duration_ms = (time.time() - t_tool_start) * 1000
            print(f"[CHAT] tool {name}: {duration_ms:.0f}ms {'err' if error_msg else 'ok'} (stream)")

            yield {
                "type": "tool_end", "name": name,
                "duration_ms": duration_ms, "error": error_msg,
            }

            current.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": str(result)[:8000],
            })

            tool_calls_log.append({
                "id": tc["id"], "name": name, "args": args,
                "result": str(result)[:2000] if not error_msg else "",
                "error": error_msg, "duration_ms": duration_ms,
            })
            try:
                logger.log_tool_call(
                    session_id=session_id, tool_name=name, arguments=args,
                    result=str(result)[:2000] if not error_msg else "",
                    error=error_msg, duration_ms=duration_ms,
                    metadata={"model": model, "round": round_num,
                             "tool_call_id": tc["id"], "stream": True},
                )
            except Exception as log_err:
                print(f"[CHAT] log error: {log_err}")

    # Ran out of rounds — force a final non-tool stream
    print(f"[CHAT] hit MAX_TOOL_ROUNDS={MAX_TOOL_ROUNDS}, forcing final stream")
    try:
        final = await client.chat.completions.create(
            model=model, messages=current, stream=True,
        )
        async for chunk in final:
            if chunk.choices and chunk.choices[0].delta.content:
                yield {"type": "token", "content": chunk.choices[0].delta.content}
        total = (time.time() - t0) * 1000
        print(f"[CHAT] TOTAL: {total:.0f}ms | rounds=max | stream")
        yield {"type": "done", "tool_calls": [tc["name"] for tc in tool_calls_log]}
    except Exception as e:
        yield {"type": "error", "error": f"Final LLM call failed: {e}"}


async def _run_tool_loop(
    *,
    messages: list,
    model: str,
    openai_tools: list[dict],
    internal_session: ClientSession | None,
    internal_tool_names: set[str],
    user_id: str | None,
    session_id: str,
    logger,
    t0: float,
) -> dict:
    """Manual tool-calling loop — bounded to MAX_TOOL_ROUNDS."""
    client = _get_openai()
    tool_calls_log: list[dict] = []

    # OpenAI client accepts {"tools": ...} only when non-empty
    def _llm_kwargs(msgs):
        kw = {"model": model, "messages": msgs}
        if openai_tools:
            kw["tools"] = openai_tools
        return kw

    current = list(messages)

    for round_num in range(1, MAX_TOOL_ROUNDS + 1):
        t_llm_start = time.time()
        try:
            resp = await client.chat.completions.create(**_llm_kwargs(current))
        except Exception as e:
            return {"error": f"LLM call failed (round {round_num}): {e}"}
        t_llm = (time.time() - t_llm_start) * 1000
        print(f"[CHAT] round_{round_num} llm: {t_llm:.0f}ms")

        msg = resp.choices[0].message

        if not msg.tool_calls:
            # Terminal round — return the content
            total = (time.time() - t0) * 1000
            print(f"[CHAT] TOTAL: {total:.0f}ms | rounds={round_num}")
            return {
                "response": msg.content or "",
                "tool_calls": [tc["name"] for tc in tool_calls_log],
            }

        # Append assistant message with tool calls
        current.append({
            "role": "assistant",
            "content": msg.content or None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        })

        # Fast path: every tool call is Composio-owned (no internal MCP).
        # Use provider.handle_tool_calls — canonical Composio pattern.
        all_composio = internal_session is None or all(
            tc.function.name not in internal_tool_names for tc in msg.tool_calls
        )

        if all_composio and _composio is not None:
            t_batch_start = time.time()
            try:
                results = await _handle_composio_tool_calls(user_id or "", resp)
            except Exception as e:
                print(f"[CHAT] handle_tool_calls failed: {e} — falling back to per-call")
                results = None
            batch_ms = (time.time() - t_batch_start) * 1000

            if results is not None and len(results) == len(msg.tool_calls):
                for tc, result in zip(msg.tool_calls, results):
                    name = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    # Normalize result → string for message content + logging
                    content = (
                        result if isinstance(result, str)
                        else json.dumps(result, default=str)
                    )
                    print(f"[CHAT] tool {name}: ok (batch {batch_ms:.0f}ms for {len(results)} calls)")
                    current.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": content[:8000],
                    })
                    tool_calls_log.append({
                        "id": tc.id, "name": name, "args": args,
                        "result": content[:2000], "error": "",
                        "duration_ms": batch_ms / max(len(results), 1),
                    })
                    try:
                        logger.log_tool_call(
                            session_id=session_id, tool_name=name, arguments=args,
                            result=content[:2000], error="",
                            duration_ms=batch_ms / max(len(results), 1),
                            metadata={"model": model, "round": round_num, "tool_call_id": tc.id, "batched": True},
                        )
                    except Exception as log_err:
                        print(f"[CHAT] log error: {log_err}")
                continue  # next round

        # Slow path: mixed (internal + Composio) OR batch call failed.
        # Execute each tool individually.
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            t_tool_start = time.time()
            error_msg = ""
            try:
                if name in internal_tool_names:
                    if internal_session is None:
                        raise RuntimeError("Internal session is closed")
                    raw = await internal_session.call_tool(name, args)
                    content_parts = getattr(raw, "content", []) or []
                    text = "\n".join(
                        getattr(p, "text", "") or ""
                        for p in content_parts
                        if getattr(p, "text", None) is not None
                    )
                    result = text or json.dumps(raw, default=str)
                else:
                    # Single-call Composio execute (fallback path only)
                    def _exec():
                        return _composio.tools.execute(
                            name, user_id=user_id or "", arguments=args,
                            dangerously_skip_version_check=True,
                        )
                    import asyncio
                    result = await asyncio.to_thread(_exec)
                    result = json.dumps(result, default=str) if not isinstance(result, str) else result
            except Exception as e:
                error_msg = str(e)
                result = f"Tool error: {e}"

            duration_ms = (time.time() - t_tool_start) * 1000
            print(f"[CHAT] tool {name}: {duration_ms:.0f}ms {'err' if error_msg else 'ok'}")

            current.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)[:8000],
            })
            tool_calls_log.append({
                "id": tc.id, "name": name, "args": args,
                "result": str(result)[:2000] if not error_msg else "",
                "error": error_msg, "duration_ms": duration_ms,
            })
            try:
                logger.log_tool_call(
                    session_id=session_id, tool_name=name, arguments=args,
                    result=str(result)[:2000] if not error_msg else "",
                    error=error_msg, duration_ms=duration_ms,
                    metadata={"model": model, "round": round_num, "tool_call_id": tc.id},
                )
            except Exception as log_err:
                print(f"[CHAT] log error: {log_err}")

    # Ran out of rounds — ask the LLM to finalize without tools
    print(f"[CHAT] hit MAX_TOOL_ROUNDS={MAX_TOOL_ROUNDS}, forcing final response")
    try:
        final = await client.chat.completions.create(model=model, messages=current)
        total = (time.time() - t0) * 1000
        print(f"[CHAT] TOTAL: {total:.0f}ms | rounds=max")
        return {
            "response": final.choices[0].message.content or "",
            "tool_calls": [tc["name"] for tc in tool_calls_log],
        }
    except Exception as e:
        return {"error": f"Final LLM call failed: {e}"}
