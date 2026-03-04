"""
Example usage of DynamoDB Credential Manager
Demonstrates storing and retrieving organizational credentials
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.dynamodb_credential_manager import DynamoDBCredentialManager, create_credential_tables


def demo_credential_storage():
    """Demonstrate credential storage operations"""
    
    print("\n" + "=" * 60)
    print("DynamoDB Credential Manager - Demo")
    print("=" * 60)
    
    # Initialize manager
    print("\n1. Initializing credential manager...")
    try:
        manager = DynamoDBCredentialManager()
        print("✅ Manager initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\nMake sure:")
        print("  1. AWS credentials are set in .env")
        print("  2. MASTER_ENCRYPTION_KEY is set in .env")
        print("  3. Run: python tests/dynamodb_credential_manager.py")
        return
    
    # Example org and user
    org_id = "org_demo_123"
    user_id = "user_alice"
    
    # ==================== STORE CREDENTIALS ====================
    
    print("\n2. Storing Telesign credentials...")
    success = manager.store_credentials(
        org_id=org_id,
        service_name="telesign",
        credential_type="api_key",
        credential_data={
            "customer_id": "12345678-1234-1234-1234-123456789012",
            "api_key": "super_secret_telesign_key_abc123",
            "environment": "production"
        },
        created_by=user_id,
        metadata={
            "account_name": "Production TeleSign Account",
            "tier": "premium"
        },
        expires_days=365
    )
    
    if success:
        print("✅ Telesign credentials stored")
    else:
        print("❌ Failed to store credentials")
        return
    
    # ==================== STORE MULTIPLE SERVICES ====================
    
    print("\n3. Storing Google OAuth credentials...")
    manager.store_credentials(
        org_id=org_id,
        service_name="google",
        credential_type="oauth",
        credential_data={
            "client_id": "123456789-abc.apps.googleusercontent.com",
            "client_secret": "GOCSPX-secret_key_here",
            "refresh_token": "1//refresh_token_xyz",
            "access_token": "ya29.access_token_abc"
        },
        created_by=user_id,
        metadata={"scopes": ["gmail.readonly", "calendar"]}
    )
    print("✅ Google credentials stored")
    
    print("\n4. Storing Salesforce credentials...")
    manager.store_credentials(
        org_id=org_id,
        service_name="salesforce",
        credential_type="oauth",
        credential_data={
            "instance_url": "https://yourinstance.salesforce.com",
            "access_token": "00D...!ARQAQsalesforce_token",
            "refresh_token": "5Aep861...refresh_token"
        },
        created_by=user_id,
        metadata={"sandbox": False}
    )
    print("✅ Salesforce credentials stored")
    
    # ==================== LIST CREDENTIALS ====================
    
    print(f"\n5. Listing all credentials for {org_id}...")
    credentials = manager.list_org_credentials(org_id)
    
    print(f"\nFound {len(credentials)} credential entries:")
    for cred in credentials:
        print(f"  • {cred['service']} ({cred['type']}) - Status: {cred['status']}")
        if cred.get('metadata'):
            print(f"    Metadata: {cred['metadata']}")
    
    # ==================== RETRIEVE CREDENTIALS ====================
    
    print("\n6. Retrieving Telesign credentials...")
    telesign_creds = manager.get_credentials(
        org_id=org_id,
        service_name="telesign",
        credential_type="api_key"
    )
    
    if telesign_creds:
        print("✅ Retrieved and decrypted Telesign credentials:")
        print(f"   Customer ID: {telesign_creds['customer_id']}")
        print(f"   API Key: {telesign_creds['api_key'][:10]}..." )
        print(f"   Environment: {telesign_creds['environment']}")
        print(f"   Created: {telesign_creds['_metadata']['created_at']}")
    else:
        print("❌ Failed to retrieve credentials")
    
    # ==================== USER MANAGEMENT ====================
    
    print("\n7. Creating user account...")
    success = manager.create_user(
        org_id=org_id,
        user_id=user_id,
        email="alice@example.com",
        name="Alice Johnson",
        role="admin",
        permissions=["read:credentials", "write:credentials", "admin:org"]
    )
    
    if success:
        print(f"✅ User {user_id} created")
    
    print("\n8. Looking up user by email...")
    user = manager.find_user_by_email("alice@example.com")
    if user:
        print(f"✅ Found user: {user['name']} (Role: {user['role']})")
    
    # ==================== API KEY MANAGEMENT ====================
    
    print("\n9. Storing API key...")
    api_key = "sk_live_abc123xyz789_demo_key_for_testing"
    success = manager.store_api_key(
        api_key_plaintext=api_key,
        org_id=org_id,
        user_id=user_id,
        name="Production API Key",
        scopes=["chat:read", "chat:write", "credentials:read"],
        expires_days=365
    )
    
    if success:
        print("✅ API key stored")
    
    print("\n10. Validating API key...")
    validation = manager.validate_api_key(api_key)
    if validation:
        print(f"✅ API key valid!")
        print(f"   Organization: {validation['org_id']}")
        print(f"   User: {validation['user_id']}")
        print(f"   Scopes: {', '.join(validation['scopes'])}")
    else:
        print("❌ Invalid API key")
    
    # ==================== DELETE CREDENTIALS ====================
    
    print("\n11. Soft-deleting Salesforce credentials...")
    success = manager.delete_credentials(
        org_id=org_id,
        service_name="salesforce",
        credential_type="oauth",
        deleted_by=user_id
    )
    
    if success:
        print("✅ Credentials marked as deleted")
    
    # List again to see updated status
    print("\n12. Listing credentials after deletion...")
    credentials = manager.list_org_credentials(org_id)
    for cred in credentials:
        print(f"  • {cred['service']} ({cred['type']}) - Status: {cred['status']}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review the code in dynamodb_credential_manager.py")
    print("  2. Integrate into your application")
    print("  3. Set up monitoring and alerts")
    print("  4. Configure backup strategy")


def cleanup_demo_data():
    """Clean up demo data from DynamoDB"""
    print("\nCleaning up demo data...")
    
    manager = DynamoDBCredentialManager()
    org_id = "org_demo_123"
    
    # Delete credentials
    for service, cred_type in [
        ("telesign", "api_key"),
        ("google", "oauth"),
        ("salesforce", "oauth")
    ]:
        manager.credentials_table.delete_item(
            Key={'org_id': org_id, 'service#type': f"{service}#{cred_type}"}
        )
    
    # Delete user
    manager.users_table.delete_item(
        Key={'org_id': org_id, 'user_id': 'user_alice'}
    )
    
    # Delete API key
    import hashlib
    key_hash = hashlib.sha256("sk_live_abc123xyz789_demo_key_for_testing".encode()).hexdigest()
    manager.api_keys_table.delete_item(Key={'key_hash': key_hash})
    
    print("✅ Demo data cleaned up")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        cleanup_demo_data()
    else:
        demo_credential_storage()
        
        print("\n💡 Tip: Run 'python example_credential_usage.py --cleanup' to remove demo data")
