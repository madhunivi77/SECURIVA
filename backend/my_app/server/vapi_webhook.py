"""
Vapi Custom LLM handler for voice AI integration.
Routes voice conversations through our backend for full MCP tool access.

Auth flow:
  Frontend → POST /api/voice-session → short-lived JWT (5min)
  Frontend → passes JWT in VAPI metadata.voiceToken
  VAPI → sends to this webhook → decode JWT → extract user_id → voice agent
"""

import os
import json
import time
import uuid
import httpx
import jwt as pyjwt  # PyJWT package
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from .voice_agent import run_voice_agent_streaming, FILLER_MESSAGE

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Dev mode: Set to True to allow voice assistant to use tools without login
VOICE_DEV_MODE = False
VOICE_DEV_USER_ID = "voice-dev-user"


def _extract_user_id(body: dict) -> str | None:
    """
    Extract user_id from the voice session JWT in VAPI metadata.
    Returns user_id or None if unauthenticated.
    """
    call_data = body.get("call", {})
    metadata = call_data.get("metadata", {})
    voice_token = metadata.get("voiceToken") if metadata else None

    if not voice_token:
        return None

    try:
        payload = pyjwt.decode(voice_token, JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "voice_session":
            print(f"[VAPI] Invalid token type: {payload.get('type')}")
            return None
        return payload.get("sub")
    except pyjwt.ExpiredSignatureError:
        print("[VAPI] Voice session token expired")
        return None
    except pyjwt.InvalidTokenError as e:
        print(f"[VAPI] Invalid voice token: {e}")
        return None


async def _stream_from_agent(messages: list, user_id: str):
    """
    True SSE streaming — yields OpenAI-compatible SSE chunks
    as tokens arrive from the voice agent.
    """
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    first_chunk = True

    async for token in run_voice_agent_streaming(messages, user_id):
        # Filler message: agent is calling tools, fill the silence
        if token == "__FILLER__":
            data = json.dumps({
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "choices": [{
                    "index": 0,
                    "delta": {"role": "assistant", "content": FILLER_MESSAGE} if first_chunk else {"content": FILLER_MESSAGE},
                    "finish_reason": None,
                }]
            })
            yield f"data: {data}\n\n"
            first_chunk = False
            continue

        # Regular content token
        delta = {"role": "assistant", "content": token} if first_chunk else {"content": token}
        first_chunk = False

        data = json.dumps({
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "choices": [{
                "index": 0,
                "delta": delta,
                "finish_reason": None,
            }]
        })
        yield f"data: {data}\n\n"

    # Send finish chunk
    finish = json.dumps({
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
    })
    yield f"data: {finish}\n\n"
    yield "data: [DONE]\n\n"


async def handle_custom_llm(request: Request):
    """
    Handle custom LLM requests from Vapi.
    Vapi sends OpenAI-compatible chat completion requests.

    - If user is authenticated (has voice session JWT), route through voice agent with MCP tools
    - If not authenticated, call OpenAI directly for basic chat functionality
    """
    t_start = time.perf_counter()
    try:
        body = await request.json()
        messages = body.get("messages", [])
        stream = body.get("stream", False)

        # Extract user_id from voice session JWT in metadata
        user_id = _extract_user_id(body)

        # Dev mode fallback
        if not user_id and VOICE_DEV_MODE:
            user_id = VOICE_DEV_USER_ID

        t_auth = time.perf_counter()
        print(f"\n⏱️  [VAPI] Request | {len(messages)} msgs | user={user_id} | stream={stream} | auth: {(t_auth-t_start)*1000:.0f}ms")

        # Authenticated: route through voice agent with MCP tools
        if user_id:
            try:
                return StreamingResponse(
                    _stream_from_agent(messages, user_id),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no",
                    },
                )
            except Exception as e:
                print(f"[VAPI] Voice agent error: {e} — falling back to direct OpenAI")
                # Fall through to direct OpenAI call

        # Unauthenticated or agent failed: call OpenAI directly (no MCP tools)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return JSONResponse({
                "id": "chatcmpl-error",
                "object": "chat.completion",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Sorry, the voice assistant is not configured properly."
                    },
                    "finish_reason": "stop"
                }]
            })

        # Proxy streaming from OpenAI
        if stream:
            async def stream_openai():
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {openai_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "gpt-4o-mini",
                            "messages": messages,
                            "max_tokens": 500,
                            "stream": True
                        },
                        timeout=60.0
                    ) as response:
                        async for chunk in response.aiter_bytes():
                            yield chunk

            return StreamingResponse(
                stream_openai(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )

        # Non-streaming fallback
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "max_tokens": 500
                },
                timeout=30.0
            )

            if response.status_code == 200:
                return JSONResponse(response.json())
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return JSONResponse({
                    "id": "chatcmpl-error",
                    "object": "chat.completion",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Sorry, I encountered an error. Please try again."
                        },
                        "finish_reason": "stop"
                    }]
                })

    except Exception as e:
        import traceback
        print(f"Custom LLM error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse({
            "id": "chatcmpl-error",
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Error: {str(e)}"
                },
                "finish_reason": "stop"
            }]
        })


async def handle_vapi_events(request: Request) -> JSONResponse:
    """
    Handle server-side events from Vapi (status-update, end-of-call-report, etc.).
    Vapi requires a serverUrl even when using custom-llm — this just acknowledges events.
    """
    try:
        body = await request.json()
        message = body.get("message", {})
        message_type = message.get("type", "unknown")
        print(f"Vapi event: {message_type}")
    except Exception:
        pass
    return JSONResponse({"status": "ok"})


# Create the Vapi app
vapi_routes = [
    Route("/chat/completions", handle_custom_llm, methods=["POST"]),
    Route("/events", handle_vapi_events, methods=["POST"]),
]

vapi_app = Starlette(routes=vapi_routes)
