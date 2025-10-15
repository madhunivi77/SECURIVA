import asyncio
import os
import json
import httpx
from dotenv import load_dotenv
from groq import Groq # Import the Groq client
from openai import OpenAI
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pathlib import Path
from typing import Any

# --- Configuration ---
load_dotenv()
MCP_SERVER_URL = "https://localhost:8000/mcp/"
AUTH_SERVER_URL = "https://localhost:8000/auth/token"
RESERVED_TOOL_PARAMS = {"session", "context"}

with open(Path(__file__).parent / "config.json", "r") as f:
    config = json.load(f)

# 1. Initialize the client
api = config.get("api")
model = config.get("model")
match api:
    case "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    case "groq":
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    case _:
        print("Invalid model configuration: (Check config.json)")
        exit(-1)

# Override definition in mcp.shared.httpx_utils
def create_mcp_https_client(
    headers: dict[str, str] | None = None,
    timeout: httpx.Timeout | None = None,
    auth: httpx.Auth | None = None,
    ) -> httpx.AsyncClient:

        # Set MCP defaults
        kwargs: dict[str, Any] = {
            "follow_redirects": True,
        }

        # Handle timeout
        if timeout is None:
            kwargs["timeout"] = httpx.Timeout(30.0)
        else:
            kwargs["timeout"] = timeout

        # Handle headers
        if headers is not None:
            kwargs["headers"] = headers

        # Handle authentication
        if auth is not None:
            kwargs["auth"] = auth

        return httpx.AsyncClient(verify=False, **kwargs) # Allows us to either disable or implement custom ssl certificate via verify parameter

async def get_auth_token() -> str | None:
    """Fetches an authentication token from the authorization server."""
    try:
        async with httpx.AsyncClient(verify=False) as client: # TODO: Change to certificate 
            response = await client.post(AUTH_SERVER_URL)
            response.raise_for_status()
            return response.json()["access_token"]
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Error fetching auth token: {e}")
        return None

async def main():
    """The main function to run our AI agent with the selected api."""
    print("Attempting to get authentication token...")
    token = await get_auth_token()
    if not token:
        print("Could not retrieve auth token. Exiting.")
        return

    print("Successfully retrieved auth token.")
    print("Connecting to MCP server to discover tools...")

    auth_headers = {"Authorization": f"Bearer {token}"}

    async with streamablehttp_client(MCP_SERVER_URL, headers=auth_headers, httpx_client_factory=create_mcp_https_client) as (read, write, _):
        async with ClientSession(read, write) as session:
            try:
                await session.initialize()
            except Exception as e:
                print(f"Error initializing MCP session: {e}")
                print("This may be due to an authentication failure.")
                return

            mcp_tools_response = await session.list_tools()
            print(f"Discovered tools: {[t.name for t in mcp_tools_response.tools]}")

            # 2. Format the discovered tools for the Groq/OpenAI API
            # This format is a standard for many tool-calling APIs.
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

            print(f"\n--- AI Agent is Ready (Powered by {api}) ---")
            
            # 3. Manage conversation history manually
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. You have access to a set of tools. Only use these tools when the user asks you to perform a specific action that requires them (e.g., 'add 5 and 3'). If the user asks what tools you have, simply list them by name and description without trying to call them.",
                }
            ]

            while True:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break

                messages.append({"role": "user", "content": user_input})

                # 4. Call the Groq API
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=agent_tools,
                    tool_choice="auto"
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                # 5. Check if the model wants to call a tool
                if tool_calls:
                    messages.append(response_message) # Add the model's decision to the history

                    # Loop through each tool call the model wants to make
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        # filter out reserved parameters for injection by mcp
                        tool_args = {k: v for k, v in json.loads(tool_call.function.arguments).items() if k not in RESERVED_TOOL_PARAMS}
                        
                        print(f"🤖 {api} wants to call tool '{tool_name}' with args {tool_args}")

                        # Use the MCP session to call the actual tool on your server
                        tool_result = await session.call_tool(tool_name, arguments=(tool_args if tool_args else {"_": None}))
                        
                        if tool_result.isError:
                            print(f"❌ Tool call failed: {tool_result.content[0].text}")
                            # Add error to history so model is aware
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": tool_name,
                                    "content": f"Error: {tool_result.content[0].text}",
                                }
                            )
                            continue

                        result_text = tool_result.content[0].text
                        print(f"✅ Tool returned: {result_text}")

                        # Add the tool's result to the message history
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_name,
                                "content": result_text,
                            }
                        )
                    
                    # 6. Make a second call to api with the tool results
                    # This allows the model to generate a natural language summary.
                    final_response = client.chat.completions.create(
                        model=model,
                        messages=messages
                    )
                    print(f"Agent: {final_response.choices[0].message.content}")
                    messages.append(final_response.choices[0].message) # Add final response to history
                else:
                    # If no tool was called, just print the response
                    print(f"Agent: {response_message.content}")
                    messages.append(response_message) # Add response to history

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting agent.")
