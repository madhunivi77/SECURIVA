"""
Voice Agent — GPT main model, Groq only for tool routing.

Flow per turn:
  1. Groq router (in chat_handler) picks top-5 tool names from the catalog
  2. Round 1 (tool decision):  GPT-4o-mini streaming (~800ms-2s)
  3. Execute tool via composio.tools.execute
  4. Round 2 (response):       GPT-4o-mini streaming (~800ms-2s)

Groq is great at classification ("which tool applies?") but weak at filling
tool-call arguments reliably — it hallucinated `message_id="last_message_id"`
as a literal string. GPT handles arg generation far better. We still use Groq
for routing because it's ~5× faster and the task is structured JSON.
"""

import json
import os
import time
import uuid
from typing import AsyncGenerator

from .tool_logger import get_tool_logger
from .chat_handler import (
    _route_tools_via_llm,
    _get_openai,
    _composio,
)
from .grounded_chat_policy import _current_time_block

MAX_TOOL_ROUNDS = 2
VOICE_TIMEOUT = 20.0
VOICE_TOOL_TOP_K = 5                                 # voice gets a tighter list
OPENAI_MODEL = "gpt-4o-mini"

VOICE_SYSTEM_PROMPT = (
    "You are SECURIVA, a concise voice assistant. Responses are SPOKEN, so "
    "keep them short and conversational. One or two sentences is ideal.\n\n"
    "Tool-use rules:\n"
    "1. ACT, DON'T ANNOUNCE. If the request needs a tool, invoke it "
    "IMMEDIATELY. Never say 'let me check' — just call.\n"
    "2. NEVER fabricate external data. Call the tool or, if no matching tool "
    "is available, briefly say the integration isn't connected.\n"
    "3. Never ask the user to connect an app — that happens elsewhere.\n"
    "4. For list/fetch tools, pick small defaults (max_results=3-5).\n\n"
    "Native capabilities (no tool needed): summarize, rephrase, translate, "
    "reason, compose. Don't mention tool names out loud."
)

FILLER_MESSAGE = "One moment. "


async def run_voice_agent_streaming(
    messages: list,
    user_id: str,
) -> AsyncGenerator[str, None]:
    """Public entry point — yields token strings + `__FILLER__` sentinel."""
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            async for token in _run_voice_agent_inner(messages, user_id, attempt):
                yield token
            return
        except Exception as e:
            if attempt < max_attempts:
                print(f"⚠️  [VOICE] error on attempt {attempt}: {e} — retrying")
                continue
            print(f"❌ [VOICE] failed after {attempt} attempts: {e}")
            yield "Sorry, I had trouble processing that. Could you try again?"
            return


async def _run_voice_agent_inner(
    messages: list,
    user_id: str,
    attempt: int = 1,
) -> AsyncGenerator[str, None]:
    t0 = time.perf_counter()
    logger = get_tool_logger()
    session_id = str(uuid.uuid4())[:8]

    # Inject system prompt + current-time block. Built fresh per turn so
    # relative-time requests ("today", "in an hour") resolve against the
    # real clock, not the LLM's training cutoff.
    sys_content = f"{VOICE_SYSTEM_PROMPT}\n\n{_current_time_block()}"
    if not messages or messages[0].get("role") != "system":
        messages = [{"role": "system", "content": sys_content}] + list(messages)
    else:
        # Existing system message — refresh it so time info stays current
        messages = list(messages)
        existing = (messages[0].get("content") or "").strip()
        messages[0] = {"role": "system", "content": f"{existing}\n\n{sys_content}".strip() if existing else sys_content}

    # LLM router picks tools from the full conversation (mid-turn corrections
    # resolve correctly). Falls back to embedding search if Groq is down.
    t_tools_start = time.perf_counter()
    tools = await _route_tools_via_llm(user_id, messages, top_k=VOICE_TOOL_TOP_K)
    t_tools_ms = (time.perf_counter() - t_tools_start) * 1000
    last_user = ""
    for m in reversed(messages):
        if isinstance(m, dict) and m.get("role") == "user":
            last_user = (m.get("content") or "")[:80]
            break
    print(
        f"⏱️  [VOICE] tool_select: {t_tools_ms:.0f}ms ({len(tools)} tools) "
        f"[attempt={attempt}] | last_user='{last_user}'"
    )

    openai_client = _get_openai()
    current = list(messages)
    emitted_filler = False

    for round_num in range(1, MAX_TOOL_ROUNDS + 1):
        async for event in _one_round(
            client=openai_client,
            model=OPENAI_MODEL,
            messages=current,
            tools=tools,
            round_num=round_num,
        ):
            kind, payload = event
            if kind == "content":
                yield payload
            elif kind == "filler":
                if not emitted_filler:
                    emitted_filler = True
                    yield "__FILLER__"
            elif kind == "tool_calls":
                ordered = payload  # list of {id, name, args}
                current.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {"id": tc["id"], "type": "function",
                         "function": {"name": tc["name"], "arguments": tc["args"]}}
                        for tc in ordered
                    ],
                })
                for tc in ordered:
                    await _execute_tool_and_append(
                        tc, current, user_id, logger, session_id, round_num
                    )
                break  # next outer round
            elif kind == "error":
                # Let the outer retry wrapper handle it
                raise RuntimeError(f"OpenAI round {round_num} failed: {payload}")
            elif kind == "done":
                total = (time.perf_counter() - t0) * 1000
                print(f"⏱️  [VOICE] TOTAL: {total:.0f}ms [attempt={attempt}]")
                return

    # Hit MAX_TOOL_ROUNDS with no final content — force a GPT final stream
    print(f"⚠️  [VOICE] hit MAX_TOOL_ROUNDS={MAX_TOOL_ROUNDS}, forcing GPT final stream")
    try:
        final = await openai_client.chat.completions.create(
            model=OPENAI_MODEL, messages=current, stream=True, max_tokens=200,
        )
        async for chunk in final:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print(f"❌ [VOICE] final stream failed: {e}")
        yield "Sorry, I couldn't wrap that up."
    total = (time.perf_counter() - t0) * 1000
    print(f"⏱️  [VOICE] TOTAL: {total:.0f}ms [attempt={attempt}] (max_rounds)")


async def _one_round(
    *, client, model: str, messages: list, tools: list, round_num: int,
):
    """
    Single streaming LLM round. Yields events:
      ('filler', None)       — first tool_call fragment seen
      ('content', str)       — content token to stream to caller
      ('tool_calls', ordered) — accumulated tool_calls after stream ends
      ('done', None)         — stream ended with only content, no tool_calls
      ('error', str)         — unrecoverable error; caller may fall back
    """
    kw = {"model": model, "messages": messages, "stream": True, "max_tokens": 200}
    if tools:
        kw["tools"] = tools

    t_start = time.perf_counter()
    try:
        stream = await client.chat.completions.create(**kw)
    except Exception as e:
        yield ("error", f"{type(e).__name__}: {e}")
        return

    content_buf = ""
    tool_calls_buf: dict[int, dict] = {}
    finish_reason: str | None = None
    filler_fired = False
    emitted_content = False

    try:
        async for chunk in stream:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta
            if choice.finish_reason:
                finish_reason = choice.finish_reason

            if delta.tool_calls:
                for tc_d in delta.tool_calls:
                    idx = tc_d.index
                    slot = tool_calls_buf.setdefault(idx, {"id": "", "name": "", "args": ""})
                    if tc_d.id:
                        slot["id"] = tc_d.id
                    if tc_d.function:
                        if tc_d.function.name:
                            slot["name"] += tc_d.function.name
                        if tc_d.function.arguments:
                            slot["args"] += tc_d.function.arguments
                if not filler_fired:
                    filler_fired = True
                    yield ("filler", None)

            if delta.content:
                content_buf += delta.content
                if not tool_calls_buf:
                    emitted_content = True
                    yield ("content", delta.content)
    except Exception as e:
        yield ("error", f"stream error: {type(e).__name__}: {e}")
        return

    t_round_ms = (time.perf_counter() - t_start) * 1000
    print(
        f"⏱️  [VOICE] round_{round_num} ({model.split('-')[0]}): "
        f"{t_round_ms:.0f}ms | tool_calls={len(tool_calls_buf)} "
        f"| content_len={len(content_buf)}"
    )

    if tool_calls_buf:
        ordered = [tool_calls_buf[i] for i in sorted(tool_calls_buf.keys())]
        yield ("tool_calls", ordered)
    else:
        yield ("done", None)


async def _execute_tool_and_append(
    tc: dict, current: list, user_id: str, logger, session_id: str, round_num: int,
):
    import asyncio
    name = tc["name"]
    try:
        args = json.loads(tc["args"] or "{}")
    except json.JSONDecodeError:
        args = {}

    print(f"🔧 [VOICE] round_{round_num} tool_start: {name}")
    t_tool_start = time.perf_counter()
    error_msg = ""
    try:
        def _exec(_n=name, _a=args):
            return _composio.tools.execute(
                _n, user_id=user_id, arguments=_a,
                dangerously_skip_version_check=True,
            )
        result = await asyncio.to_thread(_exec)
        result_str = json.dumps(result, default=str) if not isinstance(result, str) else result
    except Exception as e:
        error_msg = str(e)
        result_str = f"Tool error: {e}"
    t_tool_ms = (time.perf_counter() - t_tool_start) * 1000
    print(f"✅ [VOICE] round_{round_num} tool_end: {name} ({t_tool_ms:.0f}ms) {'err' if error_msg else 'ok'}")

    current.append({
        "role": "tool",
        "tool_call_id": tc["id"],
        "content": result_str[:6000],
    })

    try:
        logger.log_tool_call(
            session_id=session_id, tool_name=name, arguments=args,
            result=result_str[:2000] if not error_msg else "",
            error=error_msg, duration_ms=t_tool_ms,
            metadata={"pipeline": "voice_llm_router", "round": round_num},
        )
    except Exception as log_err:
        print(f"⚠️  [VOICE] log error: {log_err}")


async def run_voice_agent(messages: list, user_id: str) -> dict:
    """Non-streaming wrapper — accumulates tokens into a single string."""
    tokens = []
    async for token in run_voice_agent_streaming(messages, user_id):
        if token == "__FILLER__":
            continue
        tokens.append(token)
    return {"response": "".join(tokens) or "Sorry, I couldn't process that."}
