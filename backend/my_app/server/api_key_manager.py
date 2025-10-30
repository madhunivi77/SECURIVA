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
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


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


def validate_api_key(api_key: str, oauth_file_path: Path) -> Optional[str]:
    """
    Validate an API key and return the associated user_id

    Args:
        api_key: Plaintext API key from request
        oauth_file_path: Path to oauth.json file

    Returns:
        Optional[str]: user_id if valid, None if invalid
    """
    if not oauth_file_path.exists():
        return None

    # Hash the provided key
    key_hash = hash_api_key(api_key)

    # Load oauth.json
    with open(oauth_file_path, "r") as f:
        data = json.load(f)

    # Search for matching hash
    users = data.get("users", [])
    for user in users:
        api_key_data = user.get("api_key")
        if api_key_data and api_key_data.get("key_hash") == key_hash:
            # Update last_used timestamp
            update_last_used(user.get("user_id"), oauth_file_path)
            return user.get("user_id")

    return None


def update_last_used(user_id: str, oauth_file_path: Path) -> None:
    """
    Update the last_used timestamp for a user's API key

    Args:
        user_id: User's unique identifier
        oauth_file_path: Path to oauth.json file
    """
    if not oauth_file_path.exists():
        return

    # Load oauth.json
    with open(oauth_file_path, "r") as f:
        data = json.load(f)

    # Find and update user
    users = data.get("users", [])
    for user in users:
        if user.get("user_id") == user_id:
            if "api_key" in user and user["api_key"]:
                user["api_key"]["last_used"] = datetime.now().isoformat()
                break

    # Write back
    with open(oauth_file_path, "w") as f:
        json.dump(data, f, indent=2)


def store_api_key(user_id: str, api_key: str, oauth_file_path: Path) -> None:
    """
    Store a new API key for a user (hashed)

    Args:
        user_id: User's unique identifier
        api_key: Plaintext API key to store (will be hashed)
        oauth_file_path: Path to oauth.json file
    """
    if not oauth_file_path.exists():
        return

    # Load oauth.json
    with open(oauth_file_path, "r") as f:
        data = json.load(f)

    # Find and update user
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

    # Write back
    with open(oauth_file_path, "w") as f:
        json.dump(data, f, indent=2)


def revoke_api_key(user_id: str, oauth_file_path: Path) -> bool:
    """
    Revoke (delete) a user's API key

    Args:
        user_id: User's unique identifier
        oauth_file_path: Path to oauth.json file

    Returns:
        bool: True if key was revoked, False if user not found
    """
    if not oauth_file_path.exists():
        return False

    # Load oauth.json
    with open(oauth_file_path, "r") as f:
        data = json.load(f)

    # Find and update user
    users = data.get("users", [])
    for user in users:
        if user.get("user_id") == user_id:
            user["api_key"] = None
            # Write back
            with open(oauth_file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True

    return False
