"""
Migrate credentials from oauth.json to DynamoDB

This script safely migrates all stored credentials from the plaintext
oauth.json file to encrypted DynamoDB storage.

Usage:
    uv run python migrate_credentials_to_dynamodb.py

Prerequisites:
    1. DynamoDB tables created (run tests/create_dynamodb_table.py)
    2. MASTER_ENCRYPTION_KEY set in .env
    3. AWS credentials configured
"""

from tests.dynamodb_credential_manager import DynamoDBCredentialManager
import json
from pathlib import Path
from datetime import datetime


def migrate_oauth_to_dynamodb(dry_run=True):
    """
    Migrate oauth.json credentials to DynamoDB
    
    Args:
        dry_run: If True, only shows what would be migrated without writing
    """
    print("=" * 60)
    print("SECURIVA Credential Migration: oauth.json → DynamoDB")
    print("=" * 60)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    else:
        print("\n🚨 LIVE MODE - Credentials will be encrypted and stored\n")
    
    # Initialize manager
    try:
        manager = DynamoDBCredentialManager()
        print("✅ DynamoDB connection established")
    except Exception as e:
        print(f"❌ Failed to connect to DynamoDB: {e}")
        print("\nTroubleshooting:")
        print("  1. Run: uv run python tests/create_dynamodb_table.py")
        print("  2. Check AWS credentials in .env")
        print("  3. Verify MASTER_ENCRYPTION_KEY is set")
        return False
    
    # Load existing oauth.json
    oauth_path = Path(__file__).parent / "my_app/server/oauth.json"
    
    if not oauth_path.exists():
        print(f"❌ oauth.json not found at {oauth_path}")
        print("   Nothing to migrate.")
        return False
    
    with open(oauth_path, "r") as f:
        oauth_data = json.load(f)
    
    users = oauth_data.get("users", [])
    if not users:
        print("⚠️  No users found in oauth.json")
        return False
    
    print(f"\n📋 Found {len(users)} user(s) to migrate:\n")
    
    migration_count = 0
    
    for idx, user in enumerate(users, 1):
        user_id = user.get("user_id", f"unknown_{idx}")
        email = user.get("email", "No email")
        org_id = user.get("org_id", user_id)  # Default org_id to user_id
        
        print(f"\n[User {idx}] {email}")
        print(f"  User ID: {user_id}")
        print(f"  Org ID:  {org_id}")
        
        services = user.get("services", {})
        
        # Migrate Salesforce credentials
        if "salesforce" in services:
            sf_data = services["salesforce"]
            credentials = sf_data.get("credentials", {})
            
            if "access_token" in credentials:
                print(f"  📦 Salesforce OAuth:")
                print(f"     - Access Token: {'*' * 20}")
                print(f"     - Refresh Token: {'*' * 20}")
                print(f"     - Instance URL: {sf_data.get('instance_url', 'N/A')}")
                
                if not dry_run:
                    success = manager.store_credentials(
                        org_id=org_id,
                        service_name="salesforce",
                        credential_type="oauth",
                        credential_data={
                            "access_token": credentials.get("access_token"),
                            "refresh_token": credentials.get("refresh_token"),
                            "instance_url": sf_data.get("instance_url"),
                            "salesforce_user_id": sf_data.get("salesforce_user_id"),
                            "org_id": sf_data.get("org_id"),
                            "issued_at": credentials.get("issued_at"),
                            "signature": credentials.get("signature"),
                            "id": credentials.get("id"),
                            "token_type": credentials.get("token_type", "Bearer")
                        },
                        created_by=user_id,
                        metadata={
                            "email": email,
                            "connected_at": sf_data.get("connected_at"),
                            "scopes": sf_data.get("scopes", [])
                        }
                    )
                    
                    if success:
                        print(f"     ✅ Migrated to DynamoDB (encrypted)")
                        migration_count += 1
                    else:
                        print(f"     ❌ Failed to migrate")
        
        # Migrate Google credentials
        if "google" in services:
            google_data = services["google"]
            credentials = google_data.get("credentials", {})
            
            if credentials:
                print(f"  📦 Google OAuth:")
                print(f"     - Token: {'*' * 20}")
                print(f"     - Email: {google_data.get('email', 'N/A')}")
                
                if not dry_run:
                    success = manager.store_credentials(
                        org_id=org_id,
                        service_name="google",
                        credential_type="oauth",
                        credential_data=credentials,
                        created_by=user_id,
                        metadata={
                            "email": google_data.get("email"),
                            "connected_at": google_data.get("connected_at"),
                            "scopes": google_data.get("scopes", [])
                        }
                    )
                    
                    if success:
                        print(f"     ✅ Migrated to DynamoDB (encrypted)")
                        migration_count += 1
                    else:
                        print(f"     ❌ Failed to migrate")
    
    print("\n" + "=" * 60)
    
    if dry_run:
        print("✅ DRY RUN COMPLETE")
        print(f"\nFound {migration_count} credential set(s) to migrate")
        print("\nTo perform actual migration:")
        print("  python migrate_credentials_to_dynamodb.py --live")
    else:
        print("✅ MIGRATION COMPLETE")
        print(f"\nSuccessfully migrated {migration_count} credential set(s)")
        
        # Create backup
        backup_path = oauth_path.with_suffix('.json.backup')
        import shutil
        shutil.copy(oauth_path, backup_path)
        print(f"\n📋 Backup created: {backup_path}")
        
        print("\n⚠️  NEXT STEPS:")
        print("  1. Test your application with DynamoDB credentials")
        print("  2. Verify Salesforce integration still works")
        print("  3. Once confirmed, securely delete oauth.json:")
        print(f"     rm {oauth_path}")
        print("  4. Update your application code to use DynamoDB")
    
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import sys
    
    # Check for --live flag
    dry_run = "--live" not in sys.argv
    
    if not dry_run:
        print("\n⚠️  WARNING: This will modify your DynamoDB tables!")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != "yes":
            print("Migration cancelled.")
            sys.exit(0)
    
    migrate_oauth_to_dynamodb(dry_run=dry_run)
