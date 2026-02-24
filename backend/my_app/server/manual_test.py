"""
Manual Interactive Testing Script
Run with: python manual_test.py
"""

import os
import uuid
from datetime import datetime, timedelta

# Set environment
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://localhost/securiva_test')
os.environ['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY', 'test-key-generate-a-real-one')
os.environ['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'test-jwt-secret')

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_info(text):
    """Print info message"""
    print(f"  {text}")

def main():
    print_header("Multi-Tenant Credential System - Manual Test")
    
    try:
        from multitenant_credential_manager import get_credential_manager
        from google.oauth2.credentials import Credentials
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nPlease ensure:")
        print("  1. DATABASE_URL is set")
        print("  2. Database exists and migration is run")
        print("  3. Dependencies are installed (pip install -r requirements.txt)")
        return
    
    # Initialize
    print("Initializing credential manager...")
    cm = get_credential_manager()
    print_success("Credential manager initialized")
    
    # Create test data
    org_id = str(uuid.uuid4())
    user_id_1 = str(uuid.uuid4())
    user_id_2 = str(uuid.uuid4())
    
    print_info(f"Test Organization: {org_id}")
    print_info(f"Test User 1: {user_id_1}")
    print_info(f"Test User 2: {user_id_2}")
    
    # Test 1: Store Google credentials
    print_header("Test 1: Store Google OAuth Credentials")
    
    google_creds_1 = Credentials(
        token="test_access_token_user1",
        refresh_token="test_refresh_token_user1",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="test_client_id",
        client_secret="test_client_secret",
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        expiry=datetime.now() + timedelta(hours=1)
    )
    
    cred_id = cm.store_google_oauth_credentials(
        org_id=org_id,
        user_id=user_id_1,
        credentials=google_creds_1,
        user_email="user1@example.com",
        metadata={"name": "Test User 1", "picture": "https://example.com/pic.jpg"}
    )
    
    print_success(f"Google credentials stored (ID: {cred_id})")
    
    # Test 2: Retrieve Google credentials
    print_header("Test 2: Retrieve Google OAuth Credentials")
    
    retrieved_creds = cm.get_google_oauth_credentials(org_id, user_id_1)
    
    if retrieved_creds:
        print_success("Credentials retrieved successfully")
        print_info(f"Token: {retrieved_creds.token}")
        print_info(f"Refresh Token: {retrieved_creds.refresh_token}")
        print_info(f"Expiry: {retrieved_creds.expiry}")
    else:
        print("❌ Failed to retrieve credentials")
    
    # Test 3: Store Salesforce credentials
    print_header("Test 3: Store Salesforce OAuth Credentials")
    
    sf_cred_id = cm.store_salesforce_credentials(
        org_id=org_id,
        user_id=user_id_1,
        access_token="00D_test_salesforce_access_token",
        refresh_token="5Aep_test_salesforce_refresh_token",
        instance_url="https://test.salesforce.com",
        sf_user_id="005_test_sf_user",
        metadata={"org_name": "Test Org", "edition": "Enterprise"}
    )
    
    print_success(f"Salesforce credentials stored (ID: {sf_cred_id})")
    
    # Test 4: Retrieve Salesforce credentials
    print_header("Test 4: Retrieve Salesforce OAuth Credentials")
    
    sf_creds = cm.get_salesforce_credentials(org_id)
    
    if sf_creds:
        print_success("Salesforce credentials retrieved")
        print_info(f"Access Token: {sf_creds['access_token'][:20]}...")
        print_info(f"Instance URL: {sf_creds['instance_url']}")
    else:
        print("❌ Failed to retrieve Salesforce credentials")
    
    # Test 5: Store Telesign credentials
    print_header("Test 5: Store Telesign API Credentials")
    
    ts_cred_id = cm.store_telesign_credentials(
        org_id=org_id,
        customer_id="TEST_CUSTOMER_12345",
        api_key="test_api_key_xyz789",
        created_by=user_id_1,
        metadata={"account_name": "Test Account", "tier": "enterprise"}
    )
    
    print_success(f"Telesign credentials stored (ID: {ts_cred_id})")
    
    # Test 6: Retrieve Telesign credentials
    print_header("Test 6: Retrieve Telesign API Credentials")
    
    ts_creds = cm.get_telesign_credentials(org_id)
    
    if ts_creds:
        print_success("Telesign credentials retrieved")
        print_info(f"Customer ID: {ts_creds['customer_id']}")
        print_info(f"API Key: {ts_creds['api_key'][:15]}...")
    else:
        print("❌ Failed to retrieve Telesign credentials")
    
    # Test 7: Store credentials for second user
    print_header("Test 7: Store Google Credentials for Second User")
    
    google_creds_2 = Credentials(
        token="test_access_token_user2",
        refresh_token="test_refresh_token_user2",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="test_client_id",
        client_secret="test_client_secret",
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        expiry=datetime.now() + timedelta(hours=1)
    )
    
    cm.store_google_oauth_credentials(
        org_id=org_id,
        user_id=user_id_2,
        credentials=google_creds_2,
        user_email="user2@example.com"
    )
    
    print_success("Google credentials stored for User 2")
    
    # Test 8: Test user isolation
    print_header("Test 8: Verify User Isolation")
    
    creds_user1 = cm.get_google_oauth_credentials(org_id, user_id_1)
    creds_user2 = cm.get_google_oauth_credentials(org_id, user_id_2)
    
    if creds_user1.token != creds_user2.token:
        print_success("User isolation confirmed")
        print_info(f"User 1 token: {creds_user1.token}")
        print_info(f"User 2 token: {creds_user2.token}")
    else:
        print("❌ User isolation FAILED - tokens are the same!")
    
    # Test 9: List all credentials
    print_header("Test 9: List All Organization Credentials")
    
    all_creds = cm.list_organization_credentials(org_id)
    
    print_success(f"Found {len(all_creds)} credential(s)")
    for cred in all_creds:
        print_info(f"  - {cred['service_name']}/{cred['credential_type']}: {cred['status']}")
    
    # Test 10: Get credential status
    print_header("Test 10: Get Credential Status Summary")
    
    status = cm.get_org_credential_status(org_id)
    
    print_info("Credential Status:")
    print_info(f"  Google: {'✓' if status['google'] else '✗'}")
    print_info(f"  Salesforce: {'✓' if status['salesforce'] else '✗'}")
    print_info(f"  Telesign: {'✓' if status['telesign'] else '✗'}")
    
    # Test 11: Test organization isolation
    print_header("Test 11: Test Organization Isolation")
    
    org_id_2 = str(uuid.uuid4())
    
    # Store Telesign for second org
    cm.store_telesign_credentials(
        org_id=org_id_2,
        customer_id="ORG2_CUSTOMER_67890",
        api_key="org2_api_key_abc123",
        created_by=user_id_1
    )
    
    # Retrieve both
    ts_org1 = cm.get_telesign_credentials(org_id)
    ts_org2 = cm.get_telesign_credentials(org_id_2)
    
    if ts_org1['customer_id'] != ts_org2['customer_id']:
        print_success("Organization isolation confirmed")
        print_info(f"Org 1 Customer ID: {ts_org1['customer_id']}")
        print_info(f"Org 2 Customer ID: {ts_org2['customer_id']}")
    else:
        print("❌ Organization isolation FAILED!")
    
    # Summary
    print_header("Test Summary")
    print_success("All manual tests completed!")
    print_info("Check the output above for any errors")
    print_info(f"\nTest Organization ID: {org_id}")
    print_info("Use this ID to query the database directly:")
    print_info(f"  SELECT * FROM organization_credentials WHERE org_id = '{org_id}';")
    print()

if __name__ == "__main__":
    main()
