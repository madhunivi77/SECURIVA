import os
import json
import httpx
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


# --- Configuration ---
MCP_SERVER_URL = "http://localhost:8000/mcp/"
AUTH_SERVER_URL = "http://localhost:8000/auth/token"

# Load config for default model settings
config_path = Path(__file__).parent.parent / "client" / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

DEFAULT_API = config.get("api", "openai")
DEFAULT_MODEL = config.get("model", "gpt-3.5-turbo")


async def get_mcp_auth_token(user_id: str = None) -> str | None:
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


def get_llm_client(api: str):
    """Initialize the appropriate LLM client based on API choice."""
    if api == "openai":
        return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif api == "groq":
        return ChatGroq(api_key=os.getenv("GROQ_API_KEY"))
    else:
        raise ValueError(f"Unsupported API: {api}")

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
    
async def execute_chat_with_tools(messages: list, model: str = None, api: str = None, user_id: str = None) -> dict:
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

    # Initialize logger and generate session ID
    logger = get_tool_logger()
    session_id = str(uuid.uuid4())[:8]  # Short session ID for readability

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
                except Exception as e:
                    return {"error": f"MCP tool response failed: {e}"}

                # Initialize LLM client
                llm_client = get_llm_client(api)

                # Initialize the langgraph agent
                graph = create_agent(
                    model = llm_client, 
                    tools = mcp_tools_response,
                    middleware = [handle_tool_errors])
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
                try:
                    # extract logging information from new messages
                    for msg in agent_response['messages'][new_index:]:
                        
                        # AIMessages will contain tool name, args and id
                        if isinstance(msg, AIMessage) and getattr(msg, 'tool_calls', None):
                            tool_calls.extend(msg.tool_calls)
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
                                    "model": model,
                                    "api": api,
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
