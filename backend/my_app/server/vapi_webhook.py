"""
Vapi webhook handler for voice AI integration.
Handles tool calls from Vapi and routes them to MCP tools.
"""

import os
import re
import json
import httpx
from pathlib import Path
from typing import Optional, Any
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from .api_key_manager import validate_api_key
from .chat_handler import execute_chat_with_tools

# Dev mode: Set to True to allow voice assistant to use tools without login
VOICE_DEV_MODE = True
VOICE_DEV_USER_ID = "voice-dev-user"  # Used for dev mode tool access


async def handle_vapi_webhook(request: Request) -> JSONResponse:
    """
    Handle incoming webhooks from Vapi.

    Vapi sends different message types:
    - tool-calls: Execute tools and return results
    - assistant-request: Return assistant config for incoming calls
    - status-update, end-of-call-report, etc.: Informational (no response needed)
    """
    try:
        body = await request.json()
        message = body.get("message", {})
        message_type = message.get("type")

        print(f"Vapi webhook received: {message_type}")

        if message_type == "tool-calls":
            return await handle_tool_calls(message, body)

        elif message_type == "assistant-request":
            return await handle_assistant_request(message, body)

        elif message_type == "function-call":
            # Legacy function call format
            return await handle_function_call(message, body)

        elif message_type in ["status-update", "end-of-call-report", "transcript",
                              "conversation-update", "speech-update", "hang"]:
            # Informational events - just acknowledge
            print(f"Vapi event: {message_type}")
            return JSONResponse({"status": "ok"})

        else:
            print(f"Unknown Vapi message type: {message_type}")
            return JSONResponse({"status": "ok"})

    except Exception as e:
        print(f"Vapi webhook error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def handle_tool_calls(message: dict, body: dict) -> JSONResponse:
    """
    Handle tool-calls from Vapi.
    Execute the requested tools via MCP and return results.
    """
    tool_calls = message.get("toolWithToolCallList", [])
    results = []

    for tool_item in tool_calls:
        tool_name = tool_item.get("name", "")
        tool_call = tool_item.get("toolCall", {})
        tool_call_id = tool_call.get("id", "")
        parameters = tool_call.get("parameters", {})

        print(f"Executing tool: {tool_name} with params: {parameters}")

        try:
            # Execute the tool via MCP
            result = await execute_mcp_tool(tool_name, parameters, body)
            results.append({
                "name": tool_name,
                "toolCallId": tool_call_id,
                "result": json.dumps(result) if isinstance(result, dict) else str(result)
            })
        except Exception as e:
            print(f"Tool execution error: {e}")
            results.append({
                "name": tool_name,
                "toolCallId": tool_call_id,
                "error": str(e)
            })

    return JSONResponse({"results": results})


async def handle_function_call(message: dict, body: dict) -> JSONResponse:
    """
    Handle legacy function-call format from Vapi.
    """
    function_call = message.get("functionCall", {})
    function_name = function_call.get("name", "")
    parameters = function_call.get("parameters", {})

    print(f"Executing function: {function_name} with params: {parameters}")

    try:
        result = await execute_mcp_tool(function_name, parameters, body)
        return JSONResponse({
            "result": json.dumps(result) if isinstance(result, dict) else str(result)
        })
    except Exception as e:
        print(f"Function execution error: {e}")
        return JSONResponse({"error": str(e)})


async def handle_assistant_request(message: dict, body: dict) -> JSONResponse:
    """
    Handle assistant-request for dynamic assistant configuration.
    Returns the assistant configuration for the call.
    """
    # Return inline assistant configuration with our tools
    return JSONResponse({
        "assistant": {
            "firstMessage": "Hi! I'm SECURIVA, your voice assistant. I can help you with emails, calendar, and Salesforce. What would you like to do?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are SECURIVA, a helpful voice assistant. You have access to:
- Gmail tools: list emails, read emails, create drafts, summarize emails
- Google Calendar: list events, create events, add attendees
- Salesforce: list accounts, create cases, list cases

Keep responses concise and conversational since they will be spoken aloud.
When using tools, briefly acknowledge what you're doing."""
                    }
                ]
            },
            "voice": {
                "provider": "deepgram",
                "voiceId": "asteria"
            },
            "serverUrl": os.getenv("VAPI_SERVER_URL", "http://localhost:8000/api/vapi/webhook"),
            "serverMessages": ["tool-calls", "end-of-call-report"]
        }
    })


async def execute_mcp_tool(tool_name: str, parameters: dict, body: dict) -> Any:
    """
    Execute an MCP tool by calling the MCP server.

    Maps Vapi tool names to MCP tool names and executes them.
    """
    # Get user context from the call metadata
    call_data = body.get("message", {}).get("call", {})
    metadata = call_data.get("metadata", {})
    api_key = metadata.get("apiKey")

    # Get user_id from the API key if available
    user_id = None
    if api_key:
        oauth_file = Path(__file__).parent / "oauth.json"
        user_id = validate_api_key(api_key, oauth_file)
        print(f"Tool execution: authenticated user_id={user_id}")

    if not user_id:
        # Fallback to customer number if no API key (for phone calls)
        customer_data = call_data.get("customer", {})
        user_id = customer_data.get("number", "guest")
        print(f"Tool execution: using fallback user_id={user_id}")

    # Map common tool names to MCP tool names
    tool_mapping = {
        # Gmail tools
        "listEmails": "listEmails",
        "list_emails": "listEmails",
        "getEmailBodies": "getEmailBodies",
        "get_email_bodies": "getEmailBodies",
        "createGmailDraft": "createGmailDraft",
        "create_gmail_draft": "createGmailDraft",
        "summarizeEmail": "summarizeEmail",
        "summarize_email": "summarizeEmail",
        "summarizeRecentEmails": "summarizeRecentEmails",
        "summarize_recent_emails": "summarizeRecentEmails",

        # Calendar tools
        "listUpcomingEvents": "listUpcomingEvents",
        "list_upcoming_events": "listUpcomingEvents",
        "listEvents": "listUpcomingEvents",
        "list_events": "listUpcomingEvents",
        "addCalendarEvent": "addCalendarEvent",
        "add_calendar_event": "addCalendarEvent",
        "createEvent": "addCalendarEvent",
        "create_event": "addCalendarEvent",

        # Salesforce tools
        "listAccounts": "listAccounts",
        "list_accounts": "listAccounts",
        "listSalesforceCases": "listSalesforceCases",
        "list_salesforce_cases": "listSalesforceCases",
        "createSalesforceCase": "createSalesforceCase",
        "create_salesforce_case": "createSalesforceCase",
    }

    mcp_tool_name = tool_mapping.get(tool_name, tool_name)

    # Call the MCP server to execute the tool
    try:
        async with httpx.AsyncClient() as client:
            # Get auth token for MCP
            token_response = await client.post(
                "http://localhost:8000/auth/token",
                json={"user_id": user_id},
                timeout=10.0
            )

            if token_response.status_code != 200:
                return {"error": "Failed to get auth token"}

            token = token_response.json().get("access_token")

            # Call the MCP tool
            mcp_response = await client.post(
                "http://localhost:8000/mcp/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": mcp_tool_name,
                        "arguments": parameters
                    }
                },
                timeout=30.0
            )

            if mcp_response.status_code == 200:
                result = mcp_response.json()
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    return {"error": result["error"]}

            return {"error": f"MCP call failed: {mcp_response.status_code}"}

    except Exception as e:
        print(f"MCP tool execution error: {e}")
        return {"error": str(e)}


async def handle_custom_llm(request: Request):
    """
    Handle custom LLM requests from Vapi.
    Vapi sends OpenAI-compatible chat completion requests.

    - If user is authenticated (has API key), route through /api/chat for full MCP tool access
    - If not authenticated, call OpenAI directly for basic chat functionality
    - Supports both streaming and non-streaming responses
    """
    try:
        body = await request.json()
        messages = body.get("messages", [])
        stream = body.get("stream", False)  # Check if VAPI wants streaming

        # Try to extract API key from call metadata first
        call_data = body.get("call", {})
        metadata = call_data.get("metadata", {})
        api_key = metadata.get("apiKey") if metadata else None

        # Fallback: extract API key from system message [AUTH:xxx] tag
        if not api_key and messages:
            for msg in messages:
                if msg.get("role") == "system":
                    content = msg.get("content", "")
                    match = re.search(r'\[AUTH:([^\]]+)\]', content)
                    if match:
                        api_key = match.group(1)
                        # Remove the AUTH tag from the message so it's not sent to LLM
                        msg["content"] = re.sub(r'\s*\[AUTH:[^\]]+\]', '', content)
                    break

        print(f"Custom LLM request with {len(messages)} messages, has_api_key={bool(api_key)}, stream={stream}, dev_mode={VOICE_DEV_MODE}")

        # Add system message if not present
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {
                "role": "system",
                "content": "You are SECURIVA, a helpful voice assistant. You have access to Gmail, Google Calendar, and Salesforce tools. Keep responses brief and conversational since they will be spoken aloud."
            })

        # Determine user_id for tool access
        user_id = None
        if api_key:
            oauth_file = Path(__file__).parent / "oauth.json"
            user_id = validate_api_key(api_key, oauth_file)

        # Dev mode: use dev user for tool access even without auth
        if not user_id and VOICE_DEV_MODE:
            user_id = VOICE_DEV_USER_ID
            print(f"Voice dev mode: using {user_id} for tool access")

        # If we have a user_id (authenticated or dev mode), use chat with MCP tools
        if user_id:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/api/chat",
                    cookies={"api_key": api_key},
                    json={
                        "messages": messages,
                        "model": "gpt-4o-mini",
                        "api": "openai"
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    assistant_response = data.get("response", "Sorry, I couldn't process that.")
                    return JSONResponse({
                        "id": "chatcmpl-securiva",
                        "object": "chat.completion",
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": assistant_response
                            },
                            "finish_reason": "stop"
                        }]
                    })
                elif response.status_code == 401:
                    print(f"Chat API auth error - falling back to direct OpenAI")
                    # Fall through to direct OpenAI call
                else:
                    print(f"Chat API error: {response.status_code} - falling back to direct OpenAI")
                    # Fall through to direct OpenAI call

        # Unauthenticated or auth failed: call OpenAI directly (no MCP tools)
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

        # If streaming is requested, proxy the stream from OpenAI
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
                    "Connection": "keep-alive"
                }
            )

        # Non-streaming response
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
                data = response.json()
                return JSONResponse(data)
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


# Create the Vapi webhook app
vapi_routes = [
    Route("/webhook", handle_vapi_webhook, methods=["POST"]),
    Route("/chat/completions", handle_custom_llm, methods=["POST"]),
]

vapi_app = Starlette(routes=vapi_routes)
