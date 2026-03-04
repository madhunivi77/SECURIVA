"""
Create a test user in oauth.json for Salesforce testing
This allows you to test Salesforce without going through Google OAuth

Usage: uv run python tests/create_test_user_for_salesforce.py
"""

import json
import uuid
from pathlib import Path
from datetime import datetime


def create_test_user():
    """Create a test user entry in oauth.json"""
    
    oauth_file = Path(__file__).parent.parent / "my_app" / "server" / "oauth.json"
    
    # Load existing data or create new
    if oauth_file.exists():
        with open(oauth_file, "r") as f:
            data = json.load(f)
    else:
        data = {"users": []}
    
    # Check if test user already exists
    test_user_id = "test_user_123"
    existing_user = None
    
    for user in data.get("users", []):
        if user.get("user_id") == test_user_id:
            existing_user = user
            break
    
    if existing_user:
        print(f"✅ Test user already exists: {test_user_id}")
        print(f"   Email: {existing_user.get('email', 'N/A')}")
        
        # Check if has Salesforce credentials
        has_sf = existing_user.get("services", {}).get("salesforce")
        if has_sf:
            print(f"   ✅ Has Salesforce credentials")
            print(f"   Instance: {has_sf.get('instance_url', 'N/A')}")
        else:
            print(f"   ⚠️  No Salesforce credentials yet")
            print(f"\n💡 Now authenticate with Salesforce:")
            print(f"   http://localhost:8000/salesforce/login")
        
        return test_user_id
    
    # Create new test user
    test_user = {
        "user_id": test_user_id,
        "email": "test@example.com",
        "created_at": datetime.now().isoformat(),
        "services": {
            "google": {
                "email": "test@example.com",
                "credentials": {
                    "token": "test_token",
                    "refresh_token": "test_refresh_token",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": "test_client_id",
                    "client_secret": "test_client_secret",
                    "scopes": ["openid", "email"]
                },
                "connected_at": datetime.now().isoformat(),
                "scopes": ["openid", "email"]
            }
        },
        "api_keys": [
            {
                "key": "test_api_key_abc123",
                "created_at": datetime.now().isoformat()
            }
        ]
    }
    
    data["users"].append(test_user)
    
    # Write to oauth.json
    with open(oauth_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print("=" * 70)
    print("✅ Created test user in oauth.json")
    print("=" * 70)
    print(f"User ID: {test_user_id}")
    print(f"Email: test@example.com")
    print(f"API Key: test_api_key_abc123")
    print(f"File: {oauth_file}")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("\n1️⃣  Start the backend (if not already running):")
    print("   cd backend")
    print("   uv run python run.py")
    
    print("\n2️⃣  Authenticate with Salesforce:")
    print("   Visit: http://localhost:8000/salesforce/login")
    print("   (This should now work without Google login)")
    
    print("\n3️⃣  After Salesforce auth, run tests:")
    print("   uv run python tests/test_salesforce_mcp.py")
    print("   uv run python tests/test_salesforce_mcp_direct.py")
    
    print("\n" + "=" * 70)
    
    return test_user_id


if __name__ == "__main__":
    create_test_user()
