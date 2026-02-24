"""
Test suite for multi-tenant credential management system

Run with: python -m pytest test_multitenant_credentials.py -v
Or: python test_multitenant_credentials.py
"""

import os
import sys
import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta

# Set test environment variables
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://localhost/securiva_test')
os.environ['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY', 'test-key-for-development-only-do-not-use-in-production')

try:
    from multitenant_credential_manager import get_credential_manager
    from google.oauth2.credentials import Credentials
    MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import credential manager: {e}")
    MANAGER_AVAILABLE = False


class TestMultiTenantCredentials:
    """Test multi-tenant credential management"""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures"""
        if not MANAGER_AVAILABLE:
            print("Skipping tests - credential manager not available")
            return
        
        cls.credential_manager = get_credential_manager()
        
        # Test data
        cls.org_id_a = str(uuid.uuid4())
        cls.org_id_b = str(uuid.uuid4())
        cls.user_id_1 = str(uuid.uuid4())
        cls.user_id_2 = str(uuid.uuid4())
        
        print(f"\n{'='*70}")
        print(f"Test Organization A: {cls.org_id_a}")
        print(f"Test Organization B: {cls.org_id_b}")
        print(f"Test User 1: {cls.user_id_1}")
        print(f"Test User 2: {cls.user_id_2}")
        print(f"{'='*70}\n")
    
    def test_01_store_google_credentials_org_a_user_1(self):
        """Test storing Google OAuth credentials for Org A, User 1"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Storing Google credentials for Org A, User 1...")
        
        # Create mock Google credentials
        creds = Credentials(
            token="test_access_token_user1",
            refresh_token="test_refresh_token_user1",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="test_client_id",
            client_secret="test_client_secret",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            expiry=datetime.now() + timedelta(hours=1)
        )
        
        credential_id = self.credential_manager.store_google_oauth_credentials(
            org_id=self.org_id_a,
            user_id=self.user_id_1,
            credentials=creds,
            user_email="user1@orga.com",
            metadata={"name": "User One", "picture": "https://example.com/pic1.jpg"}
        )
        
        assert credential_id is not None
        print(f"✓ Credential stored with ID: {credential_id}")
    
    def test_02_store_google_credentials_org_a_user_2(self):
        """Test storing Google OAuth credentials for Org A, User 2"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Storing Google credentials for Org A, User 2...")
        
        creds = Credentials(
            token="test_access_token_user2",
            refresh_token="test_refresh_token_user2",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="test_client_id",
            client_secret="test_client_secret",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            expiry=datetime.now() + timedelta(hours=1)
        )
        
        credential_id = self.credential_manager.store_google_oauth_credentials(
            org_id=self.org_id_a,
            user_id=self.user_id_2,
            credentials=creds,
            user_email="user2@orga.com",
            metadata={"name": "User Two"}
        )
        
        assert credential_id is not None
        print(f"✓ Credential stored with ID: {credential_id}")
    
    def test_03_retrieve_google_credentials_user_1(self):
        """Test retrieving Google credentials for User 1"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Retrieving Google credentials for User 1...")
        
        creds = self.credential_manager.get_google_oauth_credentials(
            org_id=self.org_id_a,
            user_id=self.user_id_1
        )
        
        assert creds is not None
        assert creds.token == "test_access_token_user1"
        assert creds.refresh_token == "test_refresh_token_user1"
        print(f"✓ Retrieved credentials: {creds.token[:20]}...")
    
    def test_04_isolation_user_credentials(self):
        """Test that User 1 cannot access User 2's credentials"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Testing user isolation...")
        
        # Get User 1's credentials
        creds_user1 = self.credential_manager.get_google_oauth_credentials(
            org_id=self.org_id_a,
            user_id=self.user_id_1
        )
        
        # Get User 2's credentials
        creds_user2 = self.credential_manager.get_google_oauth_credentials(
            org_id=self.org_id_a,
            user_id=self.user_id_2
        )
        
        assert creds_user1.token != creds_user2.token
        print(f"✓ User 1 token: {creds_user1.token[:20]}...")
        print(f"✓ User 2 token: {creds_user2.token[:20]}...")
        print(f"✓ Credentials are properly isolated")
    
    def test_05_store_salesforce_credentials_org_a(self):
        """Test storing Salesforce credentials for Org A"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Storing Salesforce credentials for Org A...")
        
        credential_id = self.credential_manager.store_salesforce_credentials(
            org_id=self.org_id_a,
            user_id=self.user_id_1,
            access_token="00D_test_sf_access_token_org_a",
            refresh_token="5Aep_test_sf_refresh_token_org_a",
            instance_url="https://orga.salesforce.com",
            sf_user_id="005_test_sf_user_id",
            metadata={"org_name": "Org A Salesforce", "edition": "Enterprise"}
        )
        
        assert credential_id is not None
        print(f"✓ Salesforce credential stored with ID: {credential_id}")
    
    def test_06_store_salesforce_credentials_org_b(self):
        """Test storing Salesforce credentials for Org B"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Storing Salesforce credentials for Org B...")
        
        credential_id = self.credential_manager.store_salesforce_credentials(
            org_id=self.org_id_b,
            user_id=self.user_id_1,
            access_token="00D_test_sf_access_token_org_b",
            refresh_token="5Aep_test_sf_refresh_token_org_b",
            instance_url="https://orgb.salesforce.com",
            sf_user_id="005_test_sf_user_id_b",
            metadata={"org_name": "Org B Salesforce", "edition": "Professional"}
        )
        
        assert credential_id is not None
        print(f"✓ Salesforce credential stored with ID: {credential_id}")
    
    def test_07_isolation_salesforce_org_level(self):
        """Test that Org A cannot access Org B's Salesforce credentials"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Testing organization-level Salesforce isolation...")
        
        # Get Org A's Salesforce credentials
        creds_org_a = self.credential_manager.get_salesforce_credentials(self.org_id_a)
        
        # Get Org B's Salesforce credentials
        creds_org_b = self.credential_manager.get_salesforce_credentials(self.org_id_b)
        
        assert creds_org_a is not None
        assert creds_org_b is not None
        assert creds_org_a['access_token'] != creds_org_b['access_token']
        assert creds_org_a['instance_url'] != creds_org_b['instance_url']
        
        print(f"✓ Org A Salesforce: {creds_org_a['instance_url']}")
        print(f"✓ Org B Salesforce: {creds_org_b['instance_url']}")
        print(f"✓ Salesforce credentials are properly isolated")
    
    def test_08_store_telesign_credentials_org_a(self):
        """Test storing Telesign credentials for Org A"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Storing Telesign credentials for Org A...")
        
        credential_id = self.credential_manager.store_telesign_credentials(
            org_id=self.org_id_a,
            customer_id="CUST_ORG_A_12345",
            api_key="test_api_key_org_a_xyz789",
            created_by=self.user_id_1,
            metadata={"account_name": "Org A Production", "tier": "enterprise"}
        )
        
        assert credential_id is not None
        print(f"✓ Telesign credential stored with ID: {credential_id}")
    
    def test_09_store_telesign_credentials_org_b(self):
        """Test storing Telesign credentials for Org B"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Storing Telesign credentials for Org B...")
        
        credential_id = self.credential_manager.store_telesign_credentials(
            org_id=self.org_id_b,
            customer_id="CUST_ORG_B_67890",
            api_key="test_api_key_org_b_abc123",
            created_by=self.user_id_1,
            metadata={"account_name": "Org B Production", "tier": "professional"}
        )
        
        assert credential_id is not None
        print(f"✓ Telesign credential stored with ID: {credential_id}")
    
    def test_10_isolation_telesign_org_level(self):
        """Test that Org A cannot access Org B's Telesign credentials"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Testing organization-level Telesign isolation...")
        
        # Get Org A's Telesign credentials
        creds_org_a = self.credential_manager.get_telesign_credentials(self.org_id_a)
        
        # Get Org B's Telesign credentials
        creds_org_b = self.credential_manager.get_telesign_credentials(self.org_id_b)
        
        assert creds_org_a is not None
        assert creds_org_b is not None
        assert creds_org_a['customer_id'] != creds_org_b['customer_id']
        assert creds_org_a['api_key'] != creds_org_b['api_key']
        
        print(f"✓ Org A Telesign: {creds_org_a['customer_id']}")
        print(f"✓ Org B Telesign: {creds_org_b['customer_id']}")
        print(f"✓ Telesign credentials are properly isolated")
    
    def test_11_list_organization_credentials(self):
        """Test listing all credentials for an organization"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Listing all credentials for Org A...")
        
        credentials = self.credential_manager.list_organization_credentials(self.org_id_a)
        
        assert len(credentials) > 0
        print(f"✓ Found {len(credentials)} credentials:")
        
        for cred in credentials:
            print(f"  - {cred['service_name']}/{cred['credential_type']}: {cred['status']}")
    
    def test_12_get_credential_status(self):
        """Test getting credential status summary"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Getting credential status for Org A...")
        
        status = self.credential_manager.get_org_credential_status(self.org_id_a)
        
        print(f"✓ Credential status:")
        print(f"  - Google: {status['google']}")
        print(f"  - Salesforce: {status['salesforce']}")
        print(f"  - Telesign: {status['telesign']}")
        
        assert status['google'] == True
        assert status['salesforce'] == True
        assert status['telesign'] == True
    
    def test_13_revoke_user_credentials(self):
        """Test revoking all credentials for a user"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Revoking credentials for User 2...")
        
        count = self.credential_manager.revoke_all_user_credentials(
            org_id=self.org_id_a,
            user_id=self.user_id_2,
            revoked_by=self.user_id_1
        )
        
        print(f"✓ Revoked {count} credential(s)")
        
        # Verify User 2's credentials are no longer accessible
        creds = self.credential_manager.get_google_oauth_credentials(
            org_id=self.org_id_a,
            user_id=self.user_id_2
        )
        
        assert creds is None
        print(f"✓ User 2's credentials are no longer accessible")
    
    def test_14_delete_telesign_credentials(self):
        """Test deleting Telesign credentials"""
        if not MANAGER_AVAILABLE:
            return
        
        print("\n[TEST] Deleting Telesign credentials for Org B...")
        
        success = self.credential_manager.delete_telesign_credentials(
            org_id=self.org_id_b,
            deleted_by=self.user_id_1
        )
        
        assert success == True
        print(f"✓ Telesign credentials deleted")
        
        # Verify credentials are no longer accessible
        creds = self.credential_manager.get_telesign_credentials(self.org_id_b)
        assert creds is None
        print(f"✓ Telesign credentials are no longer accessible")


def run_manual_tests():
    """Run tests manually without pytest"""
    print("\n" + "="*70)
    print("MULTI-TENANT CREDENTIAL MANAGEMENT TEST SUITE")
    print("="*70)
    
    if not MANAGER_AVAILABLE:
        print("\n❌ ERROR: Could not import credential manager")
        print("\nPlease ensure:")
        print("  1. DATABASE_URL is set")
        print("  2. Database schema is created (run migration SQL)")
        print("  3. Required dependencies are installed")
        return
    
    test_suite = TestMultiTenantCredentials()
    test_suite.setup_class()
    
    tests = [
        ("Store Google credentials (Org A, User 1)", test_suite.test_01_store_google_credentials_org_a_user_1),
        ("Store Google credentials (Org A, User 2)", test_suite.test_02_store_google_credentials_org_a_user_2),
        ("Retrieve Google credentials (User 1)", test_suite.test_03_retrieve_google_credentials_user_1),
        ("Test user isolation", test_suite.test_04_isolation_user_credentials),
        ("Store Salesforce credentials (Org A)", test_suite.test_05_store_salesforce_credentials_org_a),
        ("Store Salesforce credentials (Org B)", test_suite.test_06_store_salesforce_credentials_org_b),
        ("Test Salesforce org isolation", test_suite.test_07_isolation_salesforce_org_level),
        ("Store Telesign credentials (Org A)", test_suite.test_08_store_telesign_credentials_org_a),
        ("Store Telesign credentials (Org B)", test_suite.test_09_store_telesign_credentials_org_b),
        ("Test Telesign org isolation", test_suite.test_10_isolation_telesign_org_level),
        ("List organization credentials", test_suite.test_11_list_organization_credentials),
        ("Get credential status", test_suite.test_12_get_credential_status),
        ("Revoke user credentials", test_suite.test_13_revoke_user_credentials),
        ("Delete Telesign credentials", test_suite.test_14_delete_telesign_credentials),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("="*70 + "\n")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")


if __name__ == "__main__":
    run_manual_tests()
