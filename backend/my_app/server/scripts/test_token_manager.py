"""
Test Telesign Token Manager

Run: python -m my_app.server.scripts.test_token_manager
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from my_app.server.telesign_token_manager import get_token_manager
import time

def test_token_storage():
    """Test storing and retrieving tokens"""
    print("=" * 60)
    print("TEST: Token Storage and Retrieval")
    print("=" * 60)
    
    manager = get_token_manager()
    
    # Store a test token
    print("\n1. Storing test token...")
    token = manager.store_token(
        customer_id="TEST_CUSTOMER_123",
        access_token="test_access_token_abc123",
        refresh_token="test_refresh_token_xyz789",
        expires_in=3600
    )
    
    print(f"✅ Token stored:")
    print(f"   Customer ID: {token.customer_id}")
    print(f"   Expires at: {token.expires_at}")
    print(f"   Has refresh token: {token.refresh_token is not None}")
    
    # Retrieve token
    print("\n2. Retrieving token...")
    retrieved = manager.get_valid_token("TEST_CUSTOMER_123")
    
    if retrieved:
        print(f"✅ Token retrieved successfully")
        print(f"   Token (masked): {retrieved[:20]}...")
    else:
        print("❌ Token retrieval failed")
    
    # List all tokens
    print("\n3. Listing all tokens...")
    tokens = manager.list_tokens()
    print(f"✅ Found {len(tokens)} token(s)")
    for customer_id, metadata in tokens.items():
        print(f"\n   Customer: {customer_id}")
        print(f"   Expires: {metadata['expires_at']}")
        print(f"   Refresh count: {metadata['refresh_count']}")
    
    # Revoke token
    print("\n4. Revoking token...")
    success = manager.revoke_token("TEST_CUSTOMER_123")
    print(f"{'✅' if success else '❌'} Token revoke {'succeeded' if success else 'failed'}")
    
    print("\n" + "=" * 60)


def test_encryption():
    """Test encryption/decryption"""
    print("=" * 60)
    print("TEST: Encryption and Decryption")
    print("=" * 60)
    
    from my_app.server.telesign_token_manager import TokenEncryption
    import os
    
    # Test with sample data
    encryption = TokenEncryption(os.getenv("ENCRYPTION_KEY"))
    
    test_data = "sensitive_token_data_12345"
    
    print(f"\n1. Original data: {test_data}")
    
    encrypted = encryption.encrypt(test_data)
    print(f"2. Encrypted: {encrypted[:50]}...")
    
    decrypted = encryption.decrypt(encrypted)
    print(f"3. Decrypted: {decrypted}")
    
    if decrypted == test_data:
        print("\n✅ Encryption/decryption test passed")
    else:
        print("\n❌ Encryption/decryption test failed")
    
    print("=" * 60)


def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "TELESIGN TOKEN MANAGER TEST SUITE" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Run tests
    test_encryption()
    print()
    test_token_storage()
    
    print("\n✅ All tests completed!\n")


if __name__ == "__main__":
    main()