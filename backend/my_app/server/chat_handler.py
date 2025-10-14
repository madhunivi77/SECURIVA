import os
import json
import httpx
from groq import Groq
from openai import OpenAI
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pathlib import Path

# --- Configuration ---
MCP_SERVER_URL = "http://localhost:8000/mcp/"
AUTH_SERVER_URL = "http://localhost:8000/auth/token"

# Load config for default model settings
config_path = Path(__file__).parent.parent / "client" / "config.json"
with open(config_path, "r") as f:
    config = json.load(f)

DEFAULT_API = config.get("api", "openai")
DEFAULT_MODEL = config.get("model", "gpt-3.5-turbo")


async def get_mcp_auth_token() -> str | None:
    """Fetches an authentication token from the authorization server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(AUTH_SERVER_URL)
            response.raise_for_status()
            return response.json()["access_token"]
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Error fetching MCP auth token: {e}")
        return None


def get_llm_client(api: str):
    """Initialize the appropriate LLM client based on API choice."""
    if api == "openai":
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif api == "groq":
        return Groq(api_key=os.getenv("GROQ_API_KEY"))
    else:
        raise ValueError(f"Unsupported API: {api}")


async def execute_chat_with_tools(messages: list, model: str = None, api: str = None) -> dict:
    """
    Execute a chat request with MCP tool-calling capabilities.

    Args:
        messages: List of message objects in OpenAI format [{role, content}, ...]
        model: LLM model to use (defaults to config.json)
        api: Which API to use - "openai" or "groq" (defaults to config.json)

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

    try:
        # Get MCP authentication token
        token = await get_mcp_auth_token()
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
                mcp_tools_response = await session.list_tools()

                # Format tools for LLM API
                agent_tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                    for tool in mcp_tools_response.tools
                ]

                # Initialize LLM client
                llm_client = get_llm_client(api)

                # Call LLM with tools
                response = llm_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=agent_tools,
                    tool_choice="auto"
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls
                tool_calls_made = []

                # Execute tool calls if LLM requested them
                if tool_calls:
                    messages.append(response_message)

                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        tool_calls_made.append({
                            "name": tool_name,
                            "arguments": tool_args
                        })

                        # Execute tool via MCP
                        tool_result = await session.call_tool(tool_name, arguments=tool_args)

                        if tool_result.isError:
                            result_text = f"Error: {tool_result.content[0].text}"
                        else:
                            result_text = tool_result.content[0].text

                        # Add tool result to messages
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": result_text,
                        })

                    # Get final response from LLM with tool results
                    final_response = llm_client.chat.completions.create(
                        model=model,
                        messages=messages
                    )
                    final_text = final_response.choices[0].message.content
                else:
                    # No tool calls, just return the response
                    final_text = response_message.content

                return {
                    "response": final_text,
                    "tool_calls": tool_calls_made
                }

    except Exception as e:
        return {"error": f"Chat execution failed: {str(e)}"}
