"""
Test Salesforce MCP tools directly with mock context
This simulates calling MCP tools as if they were called through the MCP protocol

Usage: uv run python tests/test_salesforce_mcp_direct.py
"""

import os
import sys
import json
import jwt
from pathlib import Path
from unittest.mock import Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")


def create_mock_context_with_token(user_id: str):
    """Create a mock MCP Context with JWT token for a user"""
    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY not found in .env")
    
    # Create JWT token for the user
    token_payload = {
        "sub": user_id,  # subject = user_id
        "exp": 9999999999  # Far future expiration
    }
    token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm="HS256")
    
    # Create mock context
    mock_context = Mock()
    mock_context.request_context = Mock()
    mock_context.request_context.request = Mock()
    mock_context.request_context.request.headers = Mock()
    mock_context.request_context.request.headers.get = Mock(return_value=f"Bearer {token}")
    
    return mock_context


def test_salesforce_mcp_tools():
    """Test Salesforce MCP tools with direct function calls"""
    
    print("=" * 70)
    print("TESTING SALESFORCE MCP TOOLS (Direct Calls)")
    print("=" * 70)
    
    # Load oauth.json to get user_id
    oauth_path = Path(__file__).parent.parent / "my_app" / "server" / "oauth.json"
    
    if not oauth_path.exists():
        print("\n❌ Error: oauth.json not found!")
        print("\nAuthenticate first:")
        print("1. Start backend: cd backend && uv run python run.py")
        print("2. Visit: http://localhost:8000/salesforce/login")
        return
    
    with open(oauth_path, "r") as f:
        data = json.load(f)
    
    # Find user with Salesforce credentials
    sf_user = None
    for user in data.get("users", []):
        if user.get("services", {}).get("salesforce"):
            sf_user = user
            break
    
    if not sf_user:
        print("\n❌ No Salesforce credentials found!")
        print("Authenticate at: http://localhost:8000/salesforce/login")
        return
    
    user_id = sf_user["user_id"]
    print(f"\n✅ Testing with user_id: {user_id}")
    
    # Create mock context
    try:
        mock_ctx = create_mock_context_with_token(user_id)
    except Exception as e:
        print(f"❌ Error creating mock context: {e}")
        return
    
    # Import MCP tools AFTER setting up environment
    from my_app.server.mcp_server import (
        listSalesforceCases,
        listSalesforceAccounts,
        listSalesforceContacts,
        getSalesforceUserInfo,
        getSalesforceOrgLimits
    )
    
    print("\n" + "=" * 70)
    print("TEST 1: List Salesforce Cases")
    print("=" * 70)
    try:
        result = listSalesforceCases(mock_ctx, limit=5)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST 2: List Salesforce Accounts")
    print("=" * 70)
    try:
        result = listSalesforceAccounts(mock_ctx, limit=5)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST 3: List Salesforce Contacts")
    print("=" * 70)
    try:
        result = listSalesforceContacts(mock_ctx, limit=5)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST 4: Get Salesforce User Info")
    print("=" * 70)
    try:
        result = getSalesforceUserInfo(mock_ctx)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("TEST 5: Get Salesforce Org Limits")
    print("=" * 70)
    try:
        result = getSalesforceOrgLimits(mock_ctx)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Testing Complete!")
    print("=" * 70)
    print("\n💡 To test write operations (create/update), modify this script")
    print("   to call: createSalesforceCase, createSalesforceContact, etc.")


if __name__ == "__main__":
    test_salesforce_mcp_tools()
