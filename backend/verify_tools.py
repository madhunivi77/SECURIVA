"""
Test to verify compliance tools are registered with MCP server
"""
from my_app.server.mcp_server import mcp

print("=== MCP Server Tools ===\n")

# Get all registered tools
tools = mcp.list_tools()

# Filter compliance tools
compliance_tools = [t for t in tools if 'compliance' in t.name.lower()]

print(f"Total MCP tools registered: {len(tools)}")
print(f"Compliance tools found: {len(compliance_tools)}\n")

if compliance_tools:
    print("✓ Compliance tools successfully registered:\n")
    for tool in compliance_tools:
        print(f"  • {tool.name}")
        print(f"    {tool.description[:80]}...")
        print()
else:
    print("✗ No compliance tools found!")

print("\nThe AI will now be able to use these tools when making requests to the MCP server!")
