"""
Voice Agent — simple two-model pipeline for low-latency voice.

Groq (fast) picks the tool → tool executes → GPT-4o-mini streams the spoken response.
No LangGraph overhead — just a straight async pipeline.
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

VOICE_SYSTEM_PROMPT = (
    "You are SECURIVA, a helpful voice assistant. "
    "You have access to Gmail, Google Calendar, and Salesforce tools. "
    "Keep responses brief and conversational since they will be spoken aloud. "
    "IMPORTANT: Only call a tool when you need NEW information that is not already in the conversation. "
    "If the user asks a follow-up about data you already have, answer directly without calling any tool. "
    "When tool results contain summaries or data, relay them directly — do not rephrase or re-summarize. "
    "Do not mention tool names or technical details."
)

FILLER_MESSAGE = "Let me check that for you. "

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
    Simple two-model pipeline. No LangGraph.
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

    # Filter to only voice-relevant tools (demo: email only)
    VOICE_TOOL_WHITELIST = {"summarizeRecentEmails", "listEmails", "getEmailBodies"}
    voice_tools = [t for t in conn.tools if t.name in VOICE_TOOL_WHITELIST]
    print(f"⏱️  [VOICE_AGENT]  filtered tools: {len(voice_tools)}/{len(conn.tools)} ({[t.name for t in voice_tools]})")

    # Ensure system message is present
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": VOICE_SYSTEM_PROMPT})

    lc_messages = _convert_messages(messages)

    # Step 1: Groq picks the tool (fast, ~200ms)
    groq_llm = _get_groq_client()
    groq_with_tools = groq_llm.bind_tools(voice_tools)

    t2 = time.perf_counter()
    print(f"⏱️  [VOICE_AGENT]  setup: {(t2-t1)*1000:.0f}ms")

    router_response = await groq_with_tools.ainvoke(lc_messages)

    t3 = time.perf_counter()
    has_tool_call = bool(router_response.tool_calls)
    print(f"⏱️  [VOICE_AGENT]  groq_route: {(t3-t2)*1000:.0f}ms | tool_call={has_tool_call} [attempt={attempt}]")

    if has_tool_call:
        # Step 2: Execute ALL tool calls from Groq
        tool_messages = []
        for tool_call in router_response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
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

        # Step 3: GPT-4o-mini streams the final spoken response
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

    else:
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
