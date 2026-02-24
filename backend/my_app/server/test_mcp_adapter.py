"""
Test MCP Adapter for multi-tenant credential retrieval

Run with: python test_mcp_adapter.py
"""

import os
import sys
import uuid
import jwt
from datetime import datetime, timedelta
from pathlib import Path

# Set test environment
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://localhost/securiva_test')
os.environ['ENCRYPTION_KEY'] = os.getenv('ENCRYPTION_KEY', 'test-key-for-development')
os.environ['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'test-jwt-secret-key')

try:
    from multitenant_mcp_adapter import get_mcp_adapter, MultiTenantMCPAdapter
    from multitenant_credential_manager import get_credential_manager
    from google.oauth2.credentials import Credentials
    ADAPTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import MCP adapter: {e}")
    ADAPTER_AVAILABLE = False


class MockContext:
    """Mock MCP Context for testing"""
    
    def __init__(self, jwt_token):
        self.request_context = MockRequestContext(jwt_token)


class MockRequestContext:
    """Mock request context with headers"""
    
    def __init__(self, jwt_token):
        self.request = MockRequest(jwt_token)


class MockRequest:
    """Mock request with headers"""
    
    def __init__(self, jwt_token):
        self.headers = {"Authorization": f"Bearer {jwt_token}"}
    
    def get(self, key):
        return self.headers.get(key)


def create_test_jwt(org_id, user_id, role="member"):
    """Create a test JWT token"""
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    payload = {
        'sub': user_id,
        'org_id': org_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'client_id': 'test-client'
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')


class TestMCPAdapter:
    """Test MCP adapter functionality"""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures"""
        if not ADAPTER_AVAILABLE:
            return
        
        cls.adapter = get_mcp_adapter()
        cls.credential_manager = get_credential_manager()
        
        # Create test data
        cls.org_id = str(uuid.uuid4())
        cls.user_id_1 = str(uuid.uuid4())
        cls.user_id_2 = str(uuid.uuid4())
        
        print(f"\n{'='*70}")
        print(f"Test Setup")
        print(f"{'='*70}")
        print(f"Organization ID: {cls.org_id}")
        print(f"User 1 ID: {cls.user_id_1}")
        print(f"User 2 ID: {cls.user_id_2}")
        print(f"{'='*70}\n")
        
        # Store test credentials
        cls._setup_test_credentials()
    
    @classmethod
    def _setup_test_credentials(cls):
        """Store test credentials in database"""
        print("[SETUP] Storing test credentials...")
        
        # Store Google credentials for User 1
        google_creds = Credentials(
            token="test_google_token_user1",
            refresh_token="test_google_refresh_user1",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="test_client_id",
            client_secret="test_client_secret",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            expiry=datetime.now() + timedelta(hours=1)
        )
        
        cls.credential_manager.store_google_oauth_credentials(
            org_id=cls.org_id,
            user_id=cls.user_id_1,
            credentials=google_creds,
            user_email="testuser1@example.com"
        )
        print("  ✓ Google credentials stored for User 1")
        
        # Store Salesforce credentials (org-level)
        cls.credential_manager.store_salesforce_credentials(
            org_id=cls.org_id,
            user_id=cls.user_id_1,
            access_token="test_sf_access_token",
            refresh_token="test_sf_refresh_token",
            instance_url="https://test.salesforce.com",
            sf_user_id="005test"
        )
        print("  ✓ Salesforce credentials stored")
        
        # Store Telesign credentials (org-level)
        cls.credential_manager.store_telesign_credentials(
            org_id=cls.org_id,
            customer_id="TEST_CUSTOMER_ID",
            api_key="test_api_key_12345",
            created_by=cls.user_id_1
        )
        print("  ✓ Telesign credentials stored")
        print()
    
    def test_01_extract_org_and_user(self):
        """Test extracting org_id and user_id from JWT"""
        if not ADAPTER_AVAILABLE:
            return
        
        print("[TEST 1] Extracting org_id and user_id from JWT...")
        
        # Create JWT token
        jwt_token = create_test_jwt(self.org_id, self.user_id_1)
        
        # Create mock context
        context = MockContext(jwt_token)
        
        # Extract org and user
        org_id, user_id = self.adapter.extract_org_and_user(context)
        
        assert org_id == self.org_id
        assert user_id == self.user_id_1
        
        print(f"  ✓ Extracted org_id: {org_id}")
        print(f"  ✓ Extracted user_id: {user_id}")
        print()
    
    def test_02_get_google_credentials(self):
        """Test retrieving Google credentials via adapter"""
        if not ADAPTER_AVAILABLE:
            return
        
        print("[TEST 2] Retrieving Google credentials via adapter...")
        
        jwt_token = create_test_jwt(self.org_id, self.user_id_1)
        context = MockContext(jwt_token)
        
        creds = self.adapter.get_google_credentials(context)
        
        assert creds is not None
        assert creds.token == "test_google_token_user1"
        assert creds.refresh_token == "test_google_refresh_user1"
        
        print(f"  ✓ Retrieved token: {creds.token}")
        print(f"  ✓ Retrieved refresh_token: {creds.refresh_token}")
        print()
    
    def test_03_get_salesforce_credentials(self):
        """Test retrieving Salesforce credentials via adapter"""
        if not ADAPTER_AVAILABLE:
            return
        
        print("[TEST 3] Retrieving Salesforce credentials via adapter...")
        
        jwt_token = create_test_jwt(self.org_id, self.user_id_1)
        context = MockContext(jwt_token)
        
        creds = self.adapter.get_salesforce_credentials(context)
        
        assert creds is not None
        assert creds['access_token'] == "test_sf_access_token"
        assert creds['instance_url'] == "https://test.salesforce.com"
        
        print(f"  ✓ Retrieved access_token: {creds['access_token']}")
        print(f"  ✓ Retrieved instance_url: {creds['instance_url']}")
        print()
    
    def test_04_get_telesign_clients(self):
        """Test retrieving Telesign clients via adapter"""
        if not ADAPTER_AVAILABLE:
            return
        
        print("[TEST 4] Retrieving Telesign clients via adapter...")
        
        jwt_token = create_test_jwt(self.org_id, self.user_id_1)
        context = MockContext(jwt_token)
        
        clients = self.adapter.get_telesign_clients(context)
        
        assert clients is not None
        assert 'messaging' in clients
        assert 'verify' in clients
        assert 'score' in clients
        assert clients['credentials']['customer_id'] == "TEST_CUSTOMER_ID"
        assert clients['credentials']['api_key'] == "test_api_key_12345"
        
        print(f"  ✓ Retrieved messaging client: {type(clients['messaging']).__name__}")
        print(f"  ✓ Retrieved verify client: {type(clients['verify']).__name__}")
        print(f"  ✓ Retrieved score client: {type(clients['score']).__name__}")
        print(f"  ✓ Customer ID: {clients['credentials']['customer_id']}")
        print()
    
    def test_05_user_isolation(self):
        """Test that different users get different credentials"""
        if not ADAPTER_AVAILABLE:
            return
        
        print("[TEST 5] Testing user isolation...")
        
        # Store credentials for User 2
        google_creds_user2 = Credentials(
            token="test_google_token_user2",
            refresh_token="test_google_refresh_user2",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="test_client_id",
            client_secret="test_client_secret",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            expiry=datetime.now() + timedelta(hours=1)
        )
        
        self.credential_manager.store_google_oauth_credentials(
            org_id=self.org_id,
            user_id=self.user_id_2,
            credentials=google_creds_user2,
            user_email="testuser2@example.com"
        )
        
        # Get credentials for User 1
        jwt_token_1 = create_test_jwt(self.org_id, self.user_id_1)
        context_1 = MockContext(jwt_token_1)
        creds_1 = self.adapter.get_google_credentials(context_1)
        
        # Get credentials for User 2
        jwt_token_2 = create_test_jwt(self.org_id, self.user_id_2)
        context_2 = MockContext(jwt_token_2)
        creds_2 = self.adapter.get_google_credentials(context_2)
        
        assert creds_1.token != creds_2.token
        assert creds_1.token == "test_google_token_user1"
        assert creds_2.token == "test_google_token_user2"
        
        print(f"  ✓ User 1 token: {creds_1.token}")
        print(f"  ✓ User 2 token: {creds_2.token}")
        print(f"  ✓ Tokens are different (isolation confirmed)")
        print()
    
    def test_06_missing_org_id_in_jwt(self):
        """Test handling of JWT without org_id"""
        if not ADAPTER_AVAILABLE:
            return
        
        print("[TEST 6] Testing missing org_id in JWT...")
        
        # Create JWT without org_id
        JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
        payload = {
            'sub': self.user_id_1,
            # 'org_id': missing!
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        jwt_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        
        context = MockContext(jwt_token)
        
        # Should return None when org_id is missing
        creds = self.adapter.get_google_credentials(context)
        
        assert creds is None
        print(f"  ✓ Correctly returned None for missing org_id")
        print()


def run_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("MCP ADAPTER TEST SUITE")
    print("="*70)
    
    if not ADAPTER_AVAILABLE:
        print("\n❌ ERROR: MCP Adapter not available")
        print("\nPlease ensure:")
        print("  1. DATABASE_URL is set")
        print("  2. Database schema is created")
        print("  3. multitenant_mcp_adapter.py is in the path")
        print("  4. Required dependencies installed")
        return
    
    test_suite = TestMCPAdapter()
    test_suite.setup_class()
    
    tests = [
        ("Extract org_id and user_id from JWT", test_suite.test_01_extract_org_and_user),
        ("Get Google credentials", test_suite.test_02_get_google_credentials),
        ("Get Salesforce credentials", test_suite.test_03_get_salesforce_credentials),
        ("Get Telesign clients", test_suite.test_04_get_telesign_clients),
        ("Test user isolation", test_suite.test_05_user_isolation),
        ("Test missing org_id", test_suite.test_06_missing_org_id_in_jwt),
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
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("="*70)
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
    run_tests()
