"""
Test Salesforce MCP tools via MCP Client (Most Realistic)
This tests through the actual MCP HTTP protocol with authentication

Usage: 
1. Start backend: uv run python run.py
2. In another terminal: uv run python tests/test_salesforce_via_mcp_client.py
"""

import asyncio
import os
import sys
import json
import httpx
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")


async def get_mcp_auth_token():
    """Get authentication token from the auth server"""
    auth_url = "http://localhost:8000/auth/token"
    
    try:
        async with httpx.AsyncClient() as client:
            # Get token for a specific user (optional)
            response = await client.post(auth_url, json={})
            response.raise_for_status()
            return response.json()["access_token"]
    except Exception as e:
        print(f"❌ Error getting auth token: {e}")
        print("\n💡 Make sure the backend is running:")
        print("   cd backend && uv run python run.py")
        return None


async def call_mcp_tool(tool_name: str, arguments: dict, auth_token: str):
    """Call an MCP tool with authentication"""
    
    mcp_url = "http://localhost:8000/mcp/tools/call"
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": tool_name,
        "arguments": arguments
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(mcp_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP {e.response.status_code}",
            "details": e.response.text
        }
    except Exception as e:
        return {"error": str(e)}


async def test_salesforce_mcp_via_client():
    """Test Salesforce MCP tools via actual MCP client protocol"""
    
    print("=" * 70)
    print("TESTING SALESFORCE MCP TOOLS (Via MCP Client)")
    print("=" * 70)
    
    # Check if oauth.json exists
    oauth_path = Path(__file__).parent.parent / "my_app" / "server" / "oauth.json"
    if not oauth_path.exists():
        print("\n❌ oauth.json not found!")
        print("\nSteps to authenticate:")
        print("1. Start backend: cd backend && uv run python run.py")
        print("2. Visit: http://localhost:8000/salesforce/login")
        print("3. Authorize Salesforce")
        return
    
    with open(oauth_path, "r") as f:
        data = json.load(f)
    
    # Check for Salesforce credentials
    has_sf = any(
        user.get("services", {}).get("salesforce")
        for user in data.get("users", [])
    )
    
    if not has_sf:
        print("\n❌ No Salesforce credentials found!")
        print("Authenticate at: http://localhost:8000/salesforce/login")
        return
    
    print("\n✅ Salesforce credentials found")
    print("🔄 Getting MCP authentication token...")
    
    # Get auth token
    auth_token = await get_mcp_auth_token()
    if not auth_token:
        return
    
    print("✅ Got authentication token")
    
    # Test cases
    tests = [
        {
            "name": "List Salesforce Cases",
            "tool": "listSalesforceCases",
            "args": {"limit": 5}
        },
        {
            "name": "List Salesforce Accounts", 
            "tool": "listSalesforceAccounts",
            "args": {"limit": 5}
        },
        {
            "name": "List Salesforce Contacts",
            "tool": "listSalesforceContacts",
            "args": {"limit": 5}
        },
        {
            "name": "Get Salesforce User Info",
            "tool": "getSalesforceUserInfo",
            "args": {}
        },
        {
            "name": "Get Salesforce Org Limits",
            "tool": "getSalesforceOrgLimits",
            "args": {}
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'=' * 70}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'=' * 70}")
        
        result = await call_mcp_tool(test["tool"], test["args"], auth_token)
        
        # Pretty print result
        if isinstance(result, dict) and "error" in result:
            print(f"❌ Error: {result['error']}")
            if "details" in result:
                print(f"   Details: {result['details'][:200]}")
        else:
            print(json.dumps(result, indent=2)[:1000])  # Limit output
            if len(json.dumps(result)) > 1000:
                print("\n... (truncated)")
    
    print(f"\n{'=' * 70}")
    print("✅ All tests completed!")
    print(f"{'=' * 70}")
    
    print("\n💡 Advanced Testing:")
    print("   - Test write operations (createSalesforceCase, etc.)")
    print("   - Test SOQL queries (salesforceSOQLQuery)")
    print("   - Test with different users/contexts")
    print("\n📚 Available Salesforce MCP Tools:")
    print("   - createSalesforceCase / listSalesforceCases")
    print("   - createSalesforceContact / listSalesforceContacts")
    print("   - createSalesforceAccount / listSalesforceAccounts")
    print("   - createSalesforceOpportunity / listSalesforceOpportunities")
    print("   - salesforceSOQLQuery / salesforceSOSLSearch")
    print("   - getSalesforceUserInfo / getSalesforceOrgLimits")
    print("   - createSalesforceTask / createSalesforceEvent")
    print("   - postSalesforceChatter / getSalesforceChatterFeed")


if __name__ == "__main__":
    asyncio.run(test_salesforce_mcp_via_client())
