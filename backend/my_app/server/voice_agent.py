"""
Voice Agent — three-stage pipeline for low-latency voice.

Stage 1: Groq selects which tool(s) are relevant (no tools bound, just text) ~200ms
Stage 2: Groq calls the selected tool with proper args (1-3 tools bound) ~200ms
Stage 3: GPT-4o-mini streams the spoken response

This avoids binding all 46 MCP tools to Groq, which causes malformed tool calls.
"""

import json
import time
import uuid
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

from .chat_handler import get_llm_client, handle_tool_errors
from .tool_logger import get_tool_logger
from .mcp_pool import mcp_pool

# Voice agent config
VOICE_RECURSION_LIMIT = 6  # unused now but kept for reference
VOICE_TIMEOUT = 20.0

VOICE_SYSTEM_PROMPT_TEMPLATE = (
    "You are SECURIVA, a helpful voice assistant. "
    "You have access to the following tool categories: {tool_categories}. "
    "Keep responses brief and conversational since they will be spoken aloud. "
    "IMPORTANT: Only call a tool when you need NEW information that is not already in the conversation. "
    "If the user asks a follow-up about data you already have, answer directly without calling any tool. "
    "When tool results contain summaries or data, relay them directly — do not rephrase or re-summarize. "
    "Do not mention tool names or technical details."
)

FILLER_MESSAGE = "Let me check that for you. "

TOOL_SELECTOR_PROMPT = (
    "You are a tool router. Given the user's message and a list of available tools, "
    "pick the ONE best tool to answer the request. You can only pick ONE tool — "
    "the tool will be called once and must handle the full request on its own.\n\n"
    "Respond with ONLY a JSON array containing the single tool name. Examples:\n"
    '- ["toolName"] — if one tool can handle the full request\n'
    '- [] — if no tool is needed and you can answer directly\n\n'
    "IMPORTANT: Always prefer high-level tools that do everything in one step "
    "over combining multiple lower-level tools.\n\n"
    "Available tools:\n{tool_list}\n\n"
    "Respond with ONLY the JSON array, nothing else."
)

# Cached LLM clients (stateless, safe to share across requests)
_groq_client = None
_gpt_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = get_llm_client("groq", "llama-3.3-70b-versatile")
    return _groq_client


def _get_gpt_client():
    global _gpt_client
    if _gpt_client is None:
        _gpt_client = get_llm_client("openai", "gpt-4o-mini")
    return _gpt_client


async def run_voice_agent_streaming(
    messages: list,
    user_id: str,
) -> AsyncGenerator[str, None]:
    """
    Run the voice agent and yield tokens as they stream.

    Pipeline:
    1. Groq picks the tool (fast, ~200ms)
    2. Tool executes (~1s)
    3. GPT-4o-mini streams the spoken response

    Yields:
        str tokens: either "__FILLER__" (signal to send filler speech) or content tokens
    """
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            async for token in _run_voice_agent_inner(messages, user_id, attempt):
                yield token
            return
        except _MCPConnectionError as e:
            if attempt < max_attempts:
                print(f"⚠️  [VOICE_AGENT] MCP connection error (attempt {attempt}), invalidating pool and retrying: {e}")
                await mcp_pool.invalidate(user_id)
                continue
            else:
                print(f"❌ [VOICE_AGENT] MCP connection error after {attempt} attempts: {e}")
                yield "Sorry, I had trouble connecting to your tools. Could you try again?"
                return
        except Exception as e:
            if attempt < max_attempts:
                print(f"⚠️  [VOICE_AGENT] Error on attempt {attempt}, retrying: {e}")
                continue
            else:
                print(f"❌ [VOICE_AGENT] Failed after {attempt} attempts: {e}")
                yield "Sorry, I had trouble processing that request. Could you try again?"
                return


class _MCPConnectionError(Exception):
    """Raised when the MCP pool connection is stale/dead and should be retried."""
    pass


async def _run_voice_agent_inner(
    messages: list,
    user_id: str,
    attempt: int = 1,
) -> AsyncGenerator[str, None]:
    """
    Three-stage pipeline:
      1. Groq (no tools) selects relevant tool names from plain text list
      2. Groq (selected tools bound) makes the actual tool call with args
      3. GPT-4o-mini streams the spoken response
    """
    t0 = time.perf_counter()
    logger = get_tool_logger()
    session_id = str(uuid.uuid4())[:8]

    # Get MCP connection from pool (cached tools)
    try:
        conn = await mcp_pool.get_connection(user_id)
    except Exception as e:
        raise _MCPConnectionError(f"Failed to get MCP connection: {e}") from e

    t1 = time.perf_counter()
    print(f"⏱️  [VOICE_AGENT]  pool_connect: {(t1-t0)*1000:.0f}ms ({len(conn.tools)} tools) [attempt={attempt}]")

    # Ensure system message is present (dynamic based on available tools)
    if not messages or messages[0].get("role") != "system":
        tool_categories = _get_tool_categories(conn.tools)
        system_prompt = VOICE_SYSTEM_PROMPT_TEMPLATE.format(tool_categories=tool_categories)
        messages.insert(0, {"role": "system", "content": system_prompt})

    lc_messages = _convert_messages(messages)
    groq_llm = _get_groq_client()

    # ── Stage 1: Tool selection (Groq, no tools bound, plain text) ──
    tool_list_text = "\n".join(
        f"- {t.name}: {t.description[:120]}" for t in conn.tools
    )
    selector_prompt = TOOL_SELECTOR_PROMPT.format(tool_list=tool_list_text)

    # Build selector messages: system prompt for selection + user's last message
    user_msg = next(
        (m.content for m in reversed(lc_messages) if isinstance(m, HumanMessage)),
        ""
    )
    selector_messages = [
        SystemMessage(content=selector_prompt),
        HumanMessage(content=user_msg),
    ]

    t2 = time.perf_counter()
    selector_response = await groq_llm.ainvoke(selector_messages)
    t3 = time.perf_counter()

    # Parse selected tool names from JSON response
    selected_names = _parse_tool_selection(selector_response.content, conn.tools)
    print(f"⏱️  [VOICE_AGENT]  groq_select: {(t3-t2)*1000:.0f}ms | selected={selected_names} [attempt={attempt}]")

    if not selected_names:
        # No tool needed — GPT-4o-mini generates the response directly
        print(f"⏱️  [VOICE_AGENT]  no tool needed, routing to GPT")
        gpt_llm = _get_gpt_client()
        t_gpt_start = time.perf_counter()
        first_token = True
        async for chunk in gpt_llm.astream(lc_messages):
            if chunk.content:
                if first_token:
                    t_first = time.perf_counter()
                    print(f"⏱️  [VOICE_AGENT]  gpt_first_token: {(t_first-t_gpt_start)*1000:.0f}ms")
                    first_token = False
                yield chunk.content
        total = (time.perf_counter() - t0) * 1000
        print(f"⏱️  [VOICE_AGENT]  TOTAL: {total:.0f}ms [attempt={attempt}]")
        return

    # ── Stage 2: Tool call (Groq, only selected tools bound) ──
    selected_tools = [t for t in conn.tools if t.name in selected_names]
    groq_with_tools = groq_llm.bind_tools(selected_tools)

    t4 = time.perf_counter()
    router_response = await groq_with_tools.ainvoke(lc_messages)
    t5 = time.perf_counter()

    has_tool_call = bool(router_response.tool_calls)
    print(f"⏱️  [VOICE_AGENT]  groq_call: {(t5-t4)*1000:.0f}ms | tool_call={has_tool_call} [attempt={attempt}]")

    if not has_tool_call:
        # Groq decided no tool after all — stream GPT response
        print(f"⏱️  [VOICE_AGENT]  groq declined tool call, routing to GPT")
        gpt_llm = _get_gpt_client()
        t_gpt_start = time.perf_counter()
        first_token = True
        async for chunk in gpt_llm.astream(lc_messages):
            if chunk.content:
                if first_token:
                    t_first = time.perf_counter()
                    print(f"⏱️  [VOICE_AGENT]  gpt_first_token: {(t_first-t_gpt_start)*1000:.0f}ms")
                    first_token = False
                yield chunk.content
        total = (time.perf_counter() - t0) * 1000
        print(f"⏱️  [VOICE_AGENT]  TOTAL: {total:.0f}ms [attempt={attempt}]")
        return

    # Execute tool calls
    tool_messages = []
    for tool_call in router_response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = _coerce_tool_args(tool_call["args"])
        tool_call_id = tool_call["id"]

        tool = next((t for t in conn.tools if t.name == tool_name), None)
        if not tool:
            print(f"❌ [VOICE_AGENT]  tool not found: {tool_name}")
            tool_messages.append(ToolMessage(content=f"Tool not found: {tool_name}", tool_call_id=tool_call_id))
            continue

        print(f"🔧 [VOICE_AGENT]  tool_start: {tool_name} [attempt={attempt}]")
        print(f"   ↳ args: {json.dumps(tool_args, default=str)[:500]}")

        t_tool_start = time.perf_counter()
        try:
            tool_result = await tool.ainvoke(tool_args)
        except Exception as e:
            print(f"❌ [VOICE_AGENT]  tool_error: {tool_name}: {e}")
            tool_result = f"Tool error: {e}"

        t_tool_end = time.perf_counter()
        tool_duration = (t_tool_end - t_tool_start) * 1000
        result_str = str(tool_result)[:500]
        print(f"✅ [VOICE_AGENT]  tool_end: {tool_name} ({tool_duration:.0f}ms) [attempt={attempt}]")
        print(f"   ↳ result preview: {result_str[:300]}")

        tool_messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call_id))

        try:
            logger.log_tool_call(
                session_id=session_id,
                tool_name=tool_name,
                arguments=tool_args,
                result=result_str,
                error="",
                duration_ms=tool_duration,
                metadata={"pipeline": "voice_agent", "router": "groq", "responder": "gpt-4o-mini"},
            )
        except Exception as log_err:
            print(f"⚠️  [VOICE_AGENT]  log error: {log_err}")

    # ── Stage 3: GPT-4o-mini streams the spoken response ──
    gpt_llm = _get_gpt_client()
    response_messages = lc_messages + [router_response] + tool_messages

    t_gpt_start = time.perf_counter()
    first_token = True
    async for chunk in gpt_llm.astream(response_messages):
        if chunk.content:
            if first_token:
                t_first = time.perf_counter()
                print(f"⏱️  [VOICE_AGENT]  gpt_first_token: {(t_first-t_gpt_start)*1000:.0f}ms")
                first_token = False
            yield chunk.content

    total = (time.perf_counter() - t0) * 1000
    print(f"⏱️  [VOICE_AGENT]  TOTAL: {total:.0f}ms [attempt={attempt}]")


async def run_voice_agent(messages: list, user_id: str) -> dict:
    """Non-streaming wrapper for testing."""
    tokens = []
    async for token in run_voice_agent_streaming(messages, user_id):
        if token == "__FILLER__":
            continue
        tokens.append(token)
    return {
        "response": "".join(tokens) or "Sorry, I couldn't process that.",
    }


def _coerce_tool_args(args: dict) -> dict:
    """Coerce Groq's string values to int/float where possible.
    Groq/Llama often passes '10' instead of 10 for numeric params."""
    coerced = {}
    for k, v in args.items():
        if isinstance(v, str):
            try:
                coerced[k] = int(v)
                continue
            except ValueError:
                pass
            try:
                coerced[k] = float(v)
                continue
            except ValueError:
                pass
        coerced[k] = v
    return coerced


def _parse_tool_selection(response_text: str, all_tools: list) -> set[str]:
    """Parse the JSON array of tool names from the selector LLM response."""
    valid_names = {t.name for t in all_tools}
    try:
        # Strip markdown code fences if present
        text = response_text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        selected = json.loads(text)
        if isinstance(selected, list):
            return {name for name in selected if name in valid_names}
    except (json.JSONDecodeError, TypeError):
        # Fallback: look for any valid tool names in the response text
        return {name for name in valid_names if name in response_text}
    return set()


def _get_tool_categories(tools: list) -> str:
    """Derive human-readable category names from tool names.
    e.g. ['listEmails', 'getEmailBodies', 'listUpcomingEvents', 'getSalesforceContacts']
    -> 'email, calendar events, and Salesforce'
    """
    import re
    categories = set()
    for t in tools:
        # Split camelCase name into words and take meaningful keywords
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', t.name)
        lower_words = [w.lower() for w in words]
        # Map common keywords to category names
        if any(w in lower_words for w in ("email", "emails", "gmail")):
            categories.add("email")
        elif any(w in lower_words for w in ("calendar", "event", "events")):
            categories.add("calendar")
        elif any(w in lower_words for w in ("salesforce",)):
            categories.add("Salesforce")
        elif any(w in lower_words for w in ("telesign", "whatsapp", "sms")):
            categories.add("messaging")
        else:
            # Use the first descriptive word as category
            desc_words = [w for w in lower_words if w not in ("get", "list", "create", "update", "delete", "search", "find")]
            if desc_words:
                categories.add(desc_words[0])
    if not categories:
        return "various tools"
    cats = sorted(categories)
    if len(cats) == 1:
        return cats[0]
    return ", ".join(cats[:-1]) + ", and " + cats[-1]


def _convert_messages(messages: list) -> list:
    """Convert OpenAI-format messages to LangChain message objects."""
    lc_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))
    return lc_messages
