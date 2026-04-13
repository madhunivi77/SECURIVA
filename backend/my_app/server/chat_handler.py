import os
import json
import httpx
import re
import time
import uuid
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pathlib import Path
from .tool_logger import get_tool_logger
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import AIMessage, ToolMessage
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from .grounded_chat_policy import prepare_messages_for_agent, should_use_grounded_guidance
from .request_validator import should_block_request
from .tool_confirmation_handler import get_confirmation_handler
from .tool_confirmation_config import requires_confirmation


# --- Configuration ---
MCP_SERVER_URL = "http://localhost:8000/mcp/"
AUTH_SERVER_URL = "http://localhost:8000/auth/token"

# Load config for default model settings
config_path = Path(__file__).parent.parent / "client" / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

DEFAULT_API = config.get("api", "openai")
DEFAULT_MODEL = config.get("model", "gpt-3.5-turbo")

GROUNDED_GUIDANCE_TOOL_NAMES = frozenset({
    "getGroundedSecurityGuidance",
    "getComplianceOverview",
    "getComplianceRequirements",
    "getComplianceChecklist",
    "getPenaltyInformation",
    "getBreachNotificationRequirements",
    "crossReferenceComplianceTopic",
    "searchComplianceRequirements",
})

COMPLIANCE_REFERENCE_TOOL_NAMES = frozenset({
    "getComplianceOverview",
    "getComplianceRequirements",
    "getComplianceChecklist",
    "getPenaltyInformation",
    "getBreachNotificationRequirements",
    "crossReferenceComplianceTopic",
    "searchComplianceRequirements",
})

COMPLIANCE_REPORT_TOOL_NAMES = frozenset({
    "confirmComplianceUnderstanding",
    "summarizeComplianceRequest",
    "validateComplianceParameters",
    "generateComplianceReport",
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
    """Return the latest user message content, or an empty string when unavailable."""
    for message in reversed(messages):
        if isinstance(message, dict):
            role = message.get("role")
            content = message.get("content", "")
        else:
            role = getattr(message, "role", None)
            content = getattr(message, "content", "")

        if role == "user":
            return content or ""

    return ""


def classify_tool_route(messages: list) -> str:
    """Classify the request so chat only exposes tools relevant to the current intent."""
    latest_user_message = get_latest_user_message_content(messages)
    if not latest_user_message:
        return "default"

    if should_use_grounded_guidance(messages):
        return "grounded_guidance"

    if COMPLIANCE_REPORT_REQUEST_PATTERN.search(latest_user_message):
        return "compliance_report"

    has_regulation_reference = bool(COMPLIANCE_REGULATION_PATTERN.search(latest_user_message))
    has_reference_intent = bool(COMPLIANCE_REFERENCE_REQUEST_PATTERN.search(latest_user_message))
    if has_regulation_reference and has_reference_intent:
        return "compliance_reference"

    return "default"


def filter_mcp_tools_for_route(mcp_tools: list, route_name: str) -> list:
    """Reduce the tool surface for compliance requests while preserving fallback behavior."""
    route_allowlists = {
        "grounded_guidance": GROUNDED_GUIDANCE_TOOL_NAMES,
        "compliance_reference": COMPLIANCE_REFERENCE_TOOL_NAMES,
        "compliance_report": COMPLIANCE_REFERENCE_TOOL_NAMES | COMPLIANCE_REPORT_TOOL_NAMES,
    }

    allowed_names = route_allowlists.get(route_name)
    if not allowed_names:
        return mcp_tools

    filtered_tools = [tool for tool in mcp_tools if getattr(tool, "name", None) in allowed_names]
    return filtered_tools or mcp_tools


async def get_mcp_auth_token(user_id: str | None = None) -> str | None:
    """Fetches an authentication token from the authorization server."""
    try:
        async with httpx.AsyncClient() as client:
            # Include user_id in the request body if provided
            body = {"user_id": user_id} if user_id else {}
            response = await client.post(AUTH_SERVER_URL, json=body)
            response.raise_for_status()
            return response.json()["access_token"]
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Error fetching MCP auth token: {e}")
        return None


def get_llm_client(api: str, model: str):
    """Initialize the appropriate LLM client based on API choice."""
    if api == "openai":
        return ChatOpenAI(model=model, api_key=os.getenv("OPENAI_API_KEY"))
    elif api == "groq":
        return ChatGroq(model=model, api_key=os.getenv("GROQ_API_KEY"))
    else:
        raise ValueError(f"Unsupported API: {api}")

# this wrapper is used as middleware for the langgraph agent. It blocks tools that require confirmation
@wrap_tool_call
async def check_tool_confirmation(request, handler):
    """Block tool execution if confirmation is required."""
    # Debug logging
    print(f"[DEBUG] check_tool_confirmation called for tool: {request.tool_call}")
    
    tool_name = request.tool_call.get("name", "")
    
    # If this tool requires confirmation, block it and return a message
    if requires_confirmation(tool_name):
        print(f"[DEBUG] Tool {tool_name} REQUIRES CONFIRMATION - blocking execution")
        return ToolMessage(
            content=f"⚠️ BLOCKED: This tool ({tool_name}) requires user confirmation before execution. You must ask the user for explicit permission before using this tool.",
            tool_call_id=request.tool_call["id"],
            error=1,
            duration_ms=0
        )
    
    print(f"[DEBUG] Tool {tool_name} does NOT require confirmation - proceeding")
    # Otherwise, proceed with normal execution
    return await handler(request)


# this wrapper is used as middleware for the langgraph agent. It is used so that we can collect metrics and handle errors for individual tool calls
@wrap_tool_call
async def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        # time the tool call
        start_time = time.time()
        response =  await handler(request)
        duration_ms = (time.time() - start_time) * 1000
        # account for both singular and list of responses
        if isinstance(response, ToolMessage):
            # inject custom metrics
            response.error = 0
            response.duration_ms = duration_ms
        elif isinstance(response, list):
            for msg in response:
                msg.error = 0
                msg.duration_ms = duration_ms
        return response
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error:({str(e)})",
            tool_call_id=request.tool_call["id"],
            error=1,
            duration_ms = None
        )
    
async def execute_chat_with_tools(
    messages: list,
    model: str | None = None,
    api: str | None = None,
    user_id: str | None = None,
) -> dict:
    """
    Execute a chat request with MCP tool-calling capabilities.

    Args:
        messages: List of message objects in OpenAI format [{role, content}, ...]
        model: LLM model to use (defaults to config.json)
        api: Which API to use - "openai" or "groq" (defaults to config.json)
        user_id: User ID for authentication (optional)

    Returns:
        dict with:
            - response: Final assistant response text
            - tool_calls: List of tool calls made (for debugging)
            - error: Error message if something went wrong
    """
    # Use defaults if not provided
    if not model:
        model = DEFAULT_MODEL
    if not api:
        api = DEFAULT_API

    resolved_model = model
    resolved_api = api

    # Validate request for misalignment attempts
    should_block, rejection_message = should_block_request(messages)
    if should_block:
        return {
            "response": rejection_message,
            "tool_calls": [],
            "blocked": True
        }

    tool_route = classify_tool_route(messages)
    messages = prepare_messages_for_agent(messages)

    # Initialize logger and generate session ID
    logger = get_tool_logger()
    session_id = str(uuid.uuid4())[:8]  # Short session ID for readability
    
    # Check if user is responding to a pending confirmation
    confirmation_handler = get_confirmation_handler()
    latest_user_message = get_latest_user_message_content(messages)
    
    if latest_user_message:
        response_type, tool_info = confirmation_handler.process_user_response(
            latest_user_message, 
            session_id=user_id or session_id
        )
        
        if response_type == "approved" and tool_info:
            tool_name, tool_args = tool_info
            return {
                "response": f"✅ Confirmation approved! Executing {tool_name}...\n\nNote: Tool execution after confirmation is not yet implemented in this version. The tool would execute: {tool_name} with args: {tool_args}",
                "tool_calls": [tool_name],
                "confirmation_approved": True,
                "pending_execution": {"tool_name": tool_name, "tool_args": tool_args}
            }
        elif response_type == "denied":
            return {
                "response": "❌ Action cancelled. How else can I help you?",
                "tool_calls": [],
                "confirmation_denied": True
            }
        elif response_type == "expired":
            return {
                "response": "⏱️ The previous confirmation request has expired. Please make your request again if you'd like to proceed.",
                "tool_calls": [],
                "confirmation_expired": True
            }
        elif response_type == "modify_requested":
            return {
                "response": "🔧 To modify the request, please describe what you'd like to change, and I'll create a new request with the updated parameters.",
                "tool_calls": [],
                "modification_requested": True
            }

    try:
        # Get MCP authentication token with user_id
        token = await get_mcp_auth_token(user_id)
        if not token:
            return {"error": "Could not retrieve MCP auth token"}

        auth_headers = {"Authorization": f"Bearer {token}"}

        # Connect to MCP server and get tools
        async with streamablehttp_client(MCP_SERVER_URL, headers=auth_headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                try:
                    await session.initialize()
                except Exception as e:
                    return {"error": f"MCP session initialization failed: {e}"}

                # Discover available tools
                try:
                    mcp_tools_response = await load_mcp_tools(session)
                    mcp_tools_response = filter_mcp_tools_for_route(mcp_tools_response, tool_route)
                except Exception as e:
                    return {"error": f"MCP tool response failed: {e}"}

                # Initialize LLM client
                llm_client = get_llm_client(resolved_api, resolved_model)

                # Initialize the langgraph agent with confirmation check middleware first, then error handling
                graph = create_agent(
                    model = llm_client, 
                    tools = mcp_tools_response,
                    middleware = [check_tool_confirmation, handle_tool_errors])
                try:
                    # make llm query
                    agent_response = await graph.ainvoke({"messages": messages})
                except Exception as e:
                    return {"error": f"Agent response failed: {e}"}
                
                tool_calls = []
                # store the starting index of the new messages appended to the conversation
                new_index = len(messages)
                # store the final response provided by the agent
                final_response = agent_response['messages'][-1].content
                
                # Check if any tool calls require confirmation
                tools_requiring_confirmation_list = []
                
                try:
                    # extract logging information from new messages
                    for msg in agent_response['messages'][new_index:]:
                        
                        # AIMessages will contain tool name, args and id
                        if isinstance(msg, AIMessage) and getattr(msg, 'tool_calls', None):
                            for tc in msg.tool_calls:
                                tool_calls.append(tc)
                                # Check if this tool requires confirmation
                                if requires_confirmation(tc['name']):
                                    tools_requiring_confirmation_list.append(tc)
                        pass

                        # Tool messages will contain result as well as injected duration and error status info
                        if isinstance(msg, ToolMessage):
                            tool_call_id = msg.tool_call_id
                            for i in range(len(tool_calls)):
                                if tool_calls[i]['id'] == tool_call_id:
                                    tool_calls[i]['duration_ms'] = msg.duration_ms
                                    if msg.error:
                                        tool_calls[i]['error'] = msg.content
                                        tool_calls[i]['result'] = ''
                                    else:
                                        tool_calls[i]['result'] = msg.content
                                        tool_calls[i]['error'] = ''
                            pass
                except Exception as e:
                    return {"error": f"Extracting tool information failed: {e}"}
                
                # If tools require confirmation, create confirmation requests instead of executing
                if tools_requiring_confirmation_list:
                    # For now, handle the first tool requiring confirmation
                    # In a more sophisticated implementation, we could batch confirmations
                    first_tool = tools_requiring_confirmation_list[0]
                    confirmation_id, confirmation_message = confirmation_handler.create_confirmation_request(
                        tool_name=first_tool['name'],
                        tool_args=first_tool['args'],
                        user_id=user_id,
                        session_id=user_id or session_id
                    )
                    
                    return {
                        "response": confirmation_message,
                        "tool_calls": [],
                        "confirmation_required": True,
                        "confirmation_id": confirmation_id,
                        "tool_name": first_tool['name']
                    }
                try:
                    # log each tool call
                    for tool_call in tool_calls:
                        logger.log_tool_call(
                            session_id=session_id,
                            tool_name = tool_call['name'],
                            arguments = tool_call['args'],
                            result = tool_call['result'],
                            error = tool_call['error'],
                            duration_ms=tool_call['duration_ms'],
                            metadata={
                                    "model": resolved_model,
                                    "api": resolved_api,
                                    "tool_call_id": tool_call['id']
                                }
                        )
                except Exception as e:
                    return {"error": f"Logging tool information failed: {e}"}
                return {
                    "response": final_response,
                    "tool_calls": [t['name'] for t in tool_calls]
                }

    except Exception as e:
        return {"error": f"Chat execution failed: {str(e)}"}
