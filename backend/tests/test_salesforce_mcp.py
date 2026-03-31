"""
Test Salesforce MCP tools with OAuth credentials
Usage: uv run python tests/test_salesforce_mcp.py
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from my_app.server.salesforce_utils import (
    load_oauth_data,
    get_fresh_salesforce_credentials,
    salesforce_api_request
)


def test_salesforce_connection():
    """Test basic Salesforce connectivity using stored OAuth credentials"""
    
    print("=" * 60)
    print("SALESFORCE MCP TOOLS TEST")
    print("=" * 60)
    
    # Load oauth.json
    oauth_path = Path(__file__).parent.parent / "my_app" / "server" / "oauth.json"
    
    if not oauth_path.exists():
        print("\n❌ Error: oauth.json not found!")
        print("\nTo create it:")
        print("1. Start backend: cd backend && uv run python run.py")
        print("2. Visit: http://localhost:8000/salesforce/login")
        print("3. Authorize your Salesforce account")
        return
    
    try:
        data = load_oauth_data()
        users = data.get("users", [])
        
        if not users:
            print("\n❌ No users found in oauth.json")
            return
        
        # Use first user with Salesforce credentials
        sf_user = None
        for user in users:
            if user.get("services", {}).get("salesforce"):
                sf_user = user
                break
        
        if not sf_user:
            print("\n❌ No Salesforce credentials found!")
            print("\nAuthenticate at: http://localhost:8000/salesforce/login")
            return
        
        user_id = sf_user["user_id"]
        sf_service = sf_user["services"]["salesforce"]
        
        print(f"\n✅ Found Salesforce credentials for user: {user_id}")
        print(f"   Instance URL: {sf_service.get('instance_url')}")
        print(f"   Org ID: {sf_service.get('org_id')}")
        print(f"   Connected at: {sf_service.get('connected_at')}")
        
        # Get fresh credentials (auto-refresh if needed)
        current_creds = sf_service.get("credentials")
        fresh_creds = get_fresh_salesforce_credentials(user_id, current_creds)
        
        if not fresh_creds:
            print("\n❌ Failed to get fresh credentials")
            return
        
        access_token = fresh_creds.get("access_token")
        instance_url = fresh_creds.get("instance_url")
        
        print("\n" + "=" * 60)
        print("Testing Salesforce API Calls")
        print("=" * 60)
        
        # Test 1: Get user info
        print("\n1️⃣  Getting Salesforce User Info...")
        result = salesforce_api_request(
            instance_url,
            access_token,
            "GET",
            "/services/data/v60.0/sobjects/User/describe"
        )
        
        if result.get("success"):
            print("   ✅ User Info retrieved successfully")
            print(f"   Label: {result['data'].get('label', 'N/A')}")
        else:
            print(f"   ❌ Error: {result.get('error')}")
        
        # Test 2: List Cases (limited)
        print("\n2️⃣  Listing Salesforce Cases...")
        query = "SELECT Id, Subject, Status, CreatedDate FROM Case ORDER BY CreatedDate DESC LIMIT 5"
        result = salesforce_api_request(
            instance_url,
            access_token,
            "GET",
            "/services/data/v60.0/query",
            params={"q": query}
        )
        
        if result.get("success"):
            cases = result["data"].get("records", [])
            print(f"   ✅ Found {len(cases)} cases:")
            for case in cases[:3]:
                print(f"      - {case.get('Subject')} (Status: {case.get('Status')})")
        else:
            print(f"   ❌ Error: {result.get('error')}")
        
        # Test 3: List Accounts
        print("\n3️⃣  Listing Salesforce Accounts...")
        query = "SELECT Id, Name, Industry FROM Account LIMIT 5"
        result = salesforce_api_request(
            instance_url,
            access_token,
            "GET",
            "/services/data/v60.0/query",
            params={"q": query}
        )
        
        if result.get("success"):
            accounts = result["data"].get("records", [])
            print(f"   ✅ Found {len(accounts)} accounts:")
            for account in accounts[:3]:
                print(f"      - {account.get('Name')} ({account.get('Industry', 'N/A')})")
        else:
            print(f"   ❌ Error: {result.get('error')}")
        
        # Test 4: Get Org Limits
        print("\n4️⃣  Getting Organization Limits...")
        result = salesforce_api_request(
            instance_url,
            access_token,
            "GET",
            "/services/data/v60.0/limits"
        )
        
        if result.get("success"):
            limits = result["data"]
            print("   ✅ Organization Limits:")
            print(f"      - Daily API Requests: {limits.get('DailyApiRequests', {}).get('Remaining', 'N/A')}/{limits.get('DailyApiRequests', {}).get('Max', 'N/A')}")
            print(f"      - Single Email: {limits.get('SingleEmail', {}).get('Remaining', 'N/A')}/{limits.get('SingleEmail', {}).get('Max', 'N/A')}")
        else:
            print(f"   ❌ Error: {result.get('error')}")
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        print("\n💡 Tips:")
        print("   - All Salesforce MCP tools will work now")
        print("   - Tokens auto-refresh every 90 minutes")
        print("   - Test via MCP client or frontend chat interface")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_salesforce_connection()
