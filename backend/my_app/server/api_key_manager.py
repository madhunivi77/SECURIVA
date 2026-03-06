"""
API Key Manager - Handles generation, validation, and management of API keys

API Key Format: sk_live_<32_random_bytes_base64>
Example: sk_live_abc123xyz789...

Security:
- Keys are hashed using SHA-256 before storage
- Only key prefix stored in plaintext for identification
- Plaintext key shown to user only once during generation
"""

import secrets
import hashlib
import time
from datetime import datetime
from typing import Optional


def generate_api_key() -> str:
    """
    Generate a new API key with format: sk_live_<random>

    Returns:
        str: Plaintext API key (to be shown to user once)
    """
    # Generate 32 random bytes and encode as base64-like string
    random_part = secrets.token_urlsafe(32)
    api_key = f"sk_live_{random_part}"
    return api_key


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using SHA-256

    Args:
        api_key: Plaintext API key

    Returns:
        str: Hexadecimal hash of the key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_key_prefix(api_key: str, length: int = 12) -> str:
    """
    Extract a safe prefix from the API key for display purposes

    Args:
        api_key: Plaintext API key
        length: Number of characters to include in prefix

    Returns:
        str: Key prefix (e.g., "sk_live_abc...")
    """
    if len(api_key) <= length:
        return api_key
    return api_key[:length] + "..."


def validate_api_key(api_key: str) -> Optional[str]:
    """
    Validate an API key and return the associated user_id

    Args:
        api_key: Plaintext API key from request

    Returns:
        Optional[str]: user_id if valid, None if invalid
    """
    from .salesforce_utils import load_oauth_data, save_oauth_data

    t0 = time.perf_counter()

    # Hash the provided key
    key_hash = hash_api_key(api_key)
    t1 = time.perf_counter()

    # Load oauth data
    data = load_oauth_data()
    t2 = time.perf_counter()

    # Search for matching hash
    users = data.get("users", [])
    for user in users:
        api_key_data = user.get("api_key")
        if api_key_data and api_key_data.get("key_hash") == key_hash:
            # Update last_used timestamp
            api_key_data["last_used"] = datetime.now().isoformat()
            save_oauth_data(data)
            t3 = time.perf_counter()
            print(f"\u23f1\ufe0f  [AUTH]   validate_key: hash={(.0 if not t1 else (t1-t0)*1000):.0f}ms | read={((t2-t1)*1000):.0f}ms | write={((t3-t2)*1000):.0f}ms | total={((t3-t0)*1000):.0f}ms")
            return user.get("user_id")

    return None


def update_last_used(user_id: str) -> None:
    """
    Update the last_used timestamp for a user's API key

    Args:
        user_id: User's unique identifier
    """
    from .salesforce_utils import load_oauth_data, save_oauth_data

    data = load_oauth_data()

    users = data.get("users", [])
    for user in users:
        if user.get("user_id") == user_id:
            if "api_key" in user and user["api_key"]:
                user["api_key"]["last_used"] = datetime.now().isoformat()
                break

    save_oauth_data(data)


def store_api_key(user_id: str, api_key: str) -> None:
    """
    Store a new API key for a user (hashed)

    Args:
        user_id: User's unique identifier
        api_key: Plaintext API key to store (will be hashed)
    """
    from .salesforce_utils import load_oauth_data, save_oauth_data

    data = load_oauth_data()

    users = data.get("users", [])
    for user in users:
        if user.get("user_id") == user_id:
            user["api_key"] = {
                "key_hash": hash_api_key(api_key),
                "key_prefix": get_key_prefix(api_key),
                "created_at": datetime.now().isoformat(),
                "last_used": None
            }
            break

    save_oauth_data(data)


def revoke_api_key(user_id: str) -> bool:
    """
    Revoke (delete) a user's API key

    Args:
        user_id: User's unique identifier

    Returns:
        bool: True if key was revoked, False if user not found
    """
    from .salesforce_utils import load_oauth_data, save_oauth_data

    data = load_oauth_data()

    users = data.get("users", [])
    for user in users:
        if user.get("user_id") == user_id:
            user["api_key"] = None
            save_oauth_data(data)
            return True

    return False
