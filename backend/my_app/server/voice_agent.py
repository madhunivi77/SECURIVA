"""
Voice Agent — truly agentic voice pipeline with streaming.

Replaces the old 3-step execute_voice_chat() with a real LangGraph agent
that can chain multiple tools and stream tokens for low perceived latency.
"""

import asyncio
import json
import time
import uuid
from typing import AsyncGenerator

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage

from .chat_handler import get_llm_client, handle_tool_errors, TimingCallbackHandler
from .tool_logger import get_tool_logger
from .mcp_pool import mcp_pool

# Voice agent config
VOICE_MODEL = "gpt-4o-mini"
VOICE_API = "openai"
VOICE_RECURSION_LIMIT = 6  # up to 3 tool calls per turn
VOICE_TIMEOUT = 20.0  # total agent timeout (seconds)

VOICE_SYSTEM_PROMPT = (
    "You are SECURIVA, a helpful voice assistant. "
    "You have access to Gmail, Google Calendar, and Salesforce tools. "
    "Keep responses brief and conversational since they will be spoken aloud. "
    "When answering, give 1-3 sentences max. Do not mention tool names or technical details. "
    "If a single tool can answer the question, prefer that over chaining multiple tools."
)

# Filler message sent while agent is calling tools (so user doesn't hear silence)
FILLER_MESSAGE = "Let me check that for you. "


async def run_voice_agent_streaming(
    messages: list,
    user_id: str,
) -> AsyncGenerator[str, None]:
    """
    Run the voice agent and yield tokens as they stream.

    Two-phase streaming:
    1. Thinking phase: Agent is calling tools → yield filler message immediately
    2. Answer phase: Agent's final response (no tool calls) → stream tokens

    On MCP connection failure, invalidates the pool entry and retries once.

    Yields:
        str tokens: either "__FILLER__" (signal to send filler speech) or content tokens
    """
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            async for token in _run_voice_agent_inner(messages, user_id, attempt):
                yield token
            # If we get here without exception, we're done
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
            print(f"❌ [VOICE_AGENT] Unrecoverable error on attempt {attempt}: {e}")
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
    Inner voice agent loop. Raises _MCPConnectionError if the pool connection fails,
    allowing the outer loop to retry with a fresh connection.
    """
    t0 = time.perf_counter()
    logger = get_tool_logger()
    session_id = str(uuid.uuid4())[:8]

    # Get MCP connection from pool (cached tools + session)
    try:
        conn = await mcp_pool.get_connection(user_id)
    except Exception as e:
        raise _MCPConnectionError(f"Failed to get MCP connection: {e}") from e

    t1 = time.perf_counter()
    print(f"⏱️  [VOICE_AGENT]  pool_connect: {(t1-t0)*1000:.0f}ms ({len(conn.tools)} tools) [attempt={attempt}]")

    # Ensure system message is present
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": VOICE_SYSTEM_PROMPT})

    # Convert OpenAI-format messages to LangChain messages
    lc_messages = _convert_messages(messages)

    # Initialize LLM
    llm = get_llm_client(VOICE_API, VOICE_MODEL)

    # Create LangGraph agent (same pattern as text chat)
    graph = create_agent(
        model=llm,
        tools=conn.tools,
        middleware=[handle_tool_errors],
    )

    t2 = time.perf_counter()
    print(f"⏱️  [VOICE_AGENT]  agent_setup: {(t2-t1)*1000:.0f}ms")

    # Track state for two-phase streaming
    sent_filler = False
    tool_calls_made = []

    async for event in graph.astream_events(
        {"messages": lc_messages},
        version="v2",
        config={"recursion_limit": VOICE_RECURSION_LIMIT},
    ):
        kind = event["event"]

        # LLM is streaming tokens
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]

            # If this chunk has tool call info, we're in thinking phase
            if getattr(chunk, "tool_call_chunks", None):
                if not sent_filler:
                    sent_filler = True
                    yield "__FILLER__"
                continue

            # Content tokens with no tool calls = final answer, stream them
            if chunk.content:
                yield chunk.content

        # Track tool usage for logging
        elif kind == "on_tool_start":
            tool_name = event.get("name", "unknown")
            tool_input = event.get("data", {}).get("input", {})
            print(f"🔧 [VOICE_AGENT]  tool_start: {tool_name} [attempt={attempt}]")
            print(f"   ↳ args: {json.dumps(tool_input, default=str)[:500]}")
            tool_calls_made.append({
                "name": tool_name,
                "args": tool_input,
                "start_time": time.perf_counter(),
            })

        elif kind == "on_tool_end":
            try:
                if tool_calls_made:
                    last = tool_calls_made[-1]
                    duration = (time.perf_counter() - last["start_time"]) * 1000
                    output = event.get("data", {})
                    result_str = str(output.get("output", ""))[:500] if isinstance(output, dict) else str(output)[:500]
                    print(f"✅ [VOICE_AGENT]  tool_end: {last['name']} ({duration:.0f}ms) [attempt={attempt}]")
                    print(f"   ↳ result preview: {result_str[:300]}")

                    # Check if the tool returned an error message
                    if result_str.startswith("Tool error:") or result_str.startswith("Error"):
                        print(f"⚠️  [VOICE_AGENT]  tool returned error: {result_str[:500]}")

                    logger.log_tool_call(
                        session_id=session_id,
                        tool_name=last["name"],
                        arguments=last.get("args", {}),
                        result=result_str,
                        error="",
                        duration_ms=duration,
                        metadata={"model": VOICE_MODEL, "api": VOICE_API, "pipeline": "voice_agent"},
                    )
                else:
                    print(f"⚠️  [VOICE_AGENT]  on_tool_end fired but no tool_calls_made to match")
            except Exception as log_err:
                print(f"⚠️  [VOICE_AGENT]  Error in on_tool_end handler: {log_err}")

    total = (time.perf_counter() - t0) * 1000
    tools_used = [t["name"] for t in tool_calls_made]
    print(f"⏱️  [VOICE_AGENT]  TOTAL: {total:.0f}ms | tools={tools_used} [attempt={attempt}]")


async def run_voice_agent(messages: list, user_id: str) -> dict:
    """
    Non-streaming wrapper — collects all tokens and returns a dict.
    Useful for testing or fallback scenarios.
    """
    tokens = []
    tool_names = []

    async for token in run_voice_agent_streaming(messages, user_id):
        if token == "__FILLER__":
            continue
        tokens.append(token)

    return {
        "response": "".join(tokens) or "Sorry, I couldn't process that.",
        "tool_calls": tool_names,
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
            from langchain_core.messages import AIMessage
            lc_messages.append(AIMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))
    return lc_messages
