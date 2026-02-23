"""
Telesign WhatsApp Token Manager

Handles secure storage, encryption, retrieval, and refresh of Telesign OAuth tokens
for WhatsApp Business API integration.

Features:
- AES-256 encryption for token storage
- Automatic token refresh before expiration
- Thread-safe token operations
- Audit logging of token operations
"""

import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from dotenv import load_dotenv
import base64

load_dotenv()


@dataclass
class TelesignToken:
    """Data class for Telesign OAuth tokens"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_in: int
    expires_at: float  # Unix timestamp
    scope: str
    customer_id: str
    created_at: float
    last_refreshed_at: Optional[float] = None
    refresh_count: int = 0


class TokenEncryption:
    """
    Handles encryption/decryption of tokens using AES-256
    
    Uses environment-based encryption key with PBKDF2 key derivation
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption handler
        
        Args:
            encryption_key: Base encryption key (from env var ENCRYPTION_KEY)
        """
        if encryption_key is None:
            encryption_key = os.getenv("ENCRYPTION_KEY")
        
        if not encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY must be set in .env file. "
                "Generate one with: python -c \"import os; print(os.urandom(32).hex())\""
            )
        
        # Derive a proper encryption key using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'securiva_telesign_salt',  # Static salt for consistency
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


class TelesignTokenManager:
    """
    Manages Telesign OAuth tokens with encryption and auto-refresh
    
    Features:
    - Secure encrypted storage
    - Automatic token refresh
    - Thread-safe operations
    - Audit logging
    """
    
    def __init__(
        self,
        storage_file: Optional[Path] = None,
        encryption_key: Optional[str] = None,
        auto_refresh: bool = True
    ):
        """
        Initialize token manager
        
        Args:
            storage_file: Path to encrypted token storage file
            encryption_key: Encryption key (defaults to env var)
            auto_refresh: Enable automatic token refresh
        """
        if storage_file is None:
            storage_file = Path(__file__).parent / "telesign_tokens.encrypted"
        
        self.storage_file = storage_file
        self.encryption = TokenEncryption(encryption_key)
        self.auto_refresh = auto_refresh
        self._lock = threading.Lock()
        self._tokens: Dict[str, TelesignToken] = {}
        self._refresh_timers: Dict[str, threading.Timer] = {}
        
        # Load existing tokens
        self._load_tokens()
        
        # Start auto-refresh if enabled
        if self.auto_refresh:
            self._start_auto_refresh()
    
    def _load_tokens(self):
        """Load and decrypt tokens from storage"""
        if not self.storage_file.exists():
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                encrypted_data = f.read()
            
            # Decrypt the entire file
            decrypted_data = self.encryption.decrypt(encrypted_data)
            tokens_dict = json.loads(decrypted_data)
            
            # Convert to TelesignToken objects
            for customer_id, token_data in tokens_dict.items():
                self._tokens[customer_id] = TelesignToken(**token_data)
            
            print(f"✅ Loaded {len(self._tokens)} token(s) from encrypted storage")
            
        except Exception as e:
            print(f"⚠️ Failed to load tokens: {e}")
    
    def _save_tokens(self):
        """Encrypt and save tokens to storage"""
        try:
            # Convert tokens to dict
            tokens_dict = {
                customer_id: asdict(token)
                for customer_id, token in self._tokens.items()
            }
            
            # Encrypt the entire structure
            json_data = json.dumps(tokens_dict, indent=2)
            encrypted_data = self.encryption.encrypt(json_data)
            
            # Write to file
            with open(self.storage_file, 'w') as f:
                f.write(encrypted_data)
            
            print(f"✅ Saved {len(self._tokens)} token(s) to encrypted storage")
            
        except Exception as e:
            print(f"❌ Failed to save tokens: {e}")
    
    def store_token(
        self,
        customer_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600,
        token_type: str = "Bearer",
        scope: str = "whatsapp"
    ) -> TelesignToken:
        """
        Store a new token with encryption
        
        Args:
            customer_id: Telesign customer ID
            access_token: OAuth access token
            refresh_token: OAuth refresh token (optional)
            expires_in: Token lifetime in seconds
            token_type: Token type (usually "Bearer")
            scope: Token scope
        
        Returns:
            TelesignToken object
        """
        with self._lock:
            now = time.time()
            
            token = TelesignToken(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                expires_in=expires_in,
                expires_at=now + expires_in,
                scope=scope,
                customer_id=customer_id,
                created_at=now,
                last_refreshed_at=None,
                refresh_count=0
            )
            
            self._tokens[customer_id] = token
            self._save_tokens()
            
            # Schedule auto-refresh
            if self.auto_refresh and refresh_token:
                self._schedule_refresh(customer_id)
            
            # Log the operation
            self._log_token_operation("store", customer_id, success=True)
            
            return token
    
    def get_token(self, customer_id: str) -> Optional[TelesignToken]:
        """
        Retrieve token for a customer
        
        Args:
            customer_id: Telesign customer ID
        
        Returns:
            TelesignToken if found, None otherwise
        """
        with self._lock:
            token = self._tokens.get(customer_id)
            
            if token:
                # Check if token is expired
                if self._is_token_expired(token):
                    print(f"⚠️ Token for {customer_id} is expired")
                    
                    # Try to refresh if possible
                    if token.refresh_token:
                        return self._refresh_token(customer_id)
                    else:
                        return None
            
            return token
    
    def get_valid_token(self, customer_id: str) -> Optional[str]:
        """
        Get a valid access token (auto-refreshes if needed)
        
        Args:
            customer_id: Telesign customer ID
        
        Returns:
            Valid access token string or None
        """
        token = self.get_token(customer_id)
        return token.access_token if token else None
    
    def refresh_token(self, customer_id: str) -> Optional[TelesignToken]:
        """
        Manually refresh a token
        
        Args:
            customer_id: Telesign customer ID
        
        Returns:
            Updated TelesignToken or None if failed
        """
        with self._lock:
            return self._refresh_token(customer_id)
    
    def _refresh_token(self, customer_id: str) -> Optional[TelesignToken]:
        """
        Internal token refresh logic (NOT thread-safe - must be called within lock)
        
        Args:
            customer_id: Telesign customer ID
        
        Returns:
            Updated TelesignToken or None
        """
        token = self._tokens.get(customer_id)
        
        if not token or not token.refresh_token:
            print(f"❌ Cannot refresh token for {customer_id} - no refresh token available")
            return None
        
        try:
            # Call Telesign OAuth refresh endpoint
            new_token_data = self._call_telesign_refresh_api(
                customer_id,
                token.refresh_token
            )
            
            # Update token
            now = time.time()
            token.access_token = new_token_data['access_token']
            token.expires_in = new_token_data.get('expires_in', 3600)
            token.expires_at = now + token.expires_in
            token.last_refreshed_at = now
            token.refresh_count += 1
            
            # Update refresh token if new one provided
            if 'refresh_token' in new_token_data:
                token.refresh_token = new_token_data['refresh_token']
            
            self._save_tokens()
            
            # Reschedule next refresh
            if self.auto_refresh:
                self._schedule_refresh(customer_id)
            
            # Log the operation
            self._log_token_operation("refresh", customer_id, success=True)
            
            print(f"✅ Token refreshed for {customer_id} (refresh #{token.refresh_count})")
            
            return token
            
        except Exception as e:
            print(f"❌ Token refresh failed for {customer_id}: {e}")
            self._log_token_operation("refresh", customer_id, success=False, error=str(e))
            return None
    
    def _call_telesign_refresh_api(self, customer_id: str, refresh_token: str) -> Dict[str, Any]:
        """
        Call Telesign OAuth token refresh endpoint
        
        Args:
            customer_id: Telesign customer ID
            refresh_token: Refresh token
        
        Returns:
            New token data from API
        """
        import requests
        
        # Telesign OAuth endpoint (update with actual endpoint when available)
        token_url = os.getenv(
            "TELESIGN_TOKEN_URL",
            "https://rest-api.telesign.com/v1/oauth/token"
        )
        
        api_key = os.getenv("TELESIGN_API_KEY")
        
        response = requests.post(
            token_url,
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': customer_id,
                'client_secret': api_key
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")
        
        return response.json()
    
    def _is_token_expired(self, token: TelesignToken, buffer_seconds: int = 300) -> bool:
        """
        Check if token is expired or will expire soon
        
        Args:
            token: Token to check
            buffer_seconds: Refresh buffer (default 5 minutes before expiry)
        
        Returns:
            True if expired or expiring soon
        """
        now = time.time()
        return now >= (token.expires_at - buffer_seconds)
    
    def _schedule_refresh(self, customer_id: str):
        """
        Schedule automatic token refresh
        
        Args:
            customer_id: Telesign customer ID
        """
        # Cancel existing timer
        if customer_id in self._refresh_timers:
            self._refresh_timers[customer_id].cancel()
        
        token = self._tokens.get(customer_id)
        if not token or not token.refresh_token:
            return
        
        # Schedule refresh 5 minutes before expiry
        refresh_in = token.expires_at - time.time() - 300
        
        if refresh_in > 0:
            timer = threading.Timer(
                refresh_in,
                lambda: self.refresh_token(customer_id)
            )
            timer.daemon = True
            timer.start()
            self._refresh_timers[customer_id] = timer
            
            print(f"⏰ Token refresh scheduled for {customer_id} in {refresh_in:.0f} seconds")
    
    def _start_auto_refresh(self):
        """Start auto-refresh for all tokens with refresh tokens"""
        for customer_id in self._tokens.keys():
            self._schedule_refresh(customer_id)
    
    def revoke_token(self, customer_id: str) -> bool:
        """
        Revoke and delete a token
        
        Args:
            customer_id: Telesign customer ID
        
        Returns:
            True if revoked successfully
        """
        with self._lock:
            if customer_id not in self._tokens:
                return False
            
            # Cancel refresh timer
            if customer_id in self._refresh_timers:
                self._refresh_timers[customer_id].cancel()
                del self._refresh_timers[customer_id]
            
            # Remove token
            del self._tokens[customer_id]
            self._save_tokens()
            
            # Log the operation
            self._log_token_operation("revoke", customer_id, success=True)
            
            print(f"✅ Token revoked for {customer_id}")
            
            return True
    
    def list_tokens(self) -> Dict[str, Dict[str, Any]]:
        """
        List all stored tokens (without exposing actual token values)
        
        Returns:
            Dictionary of token metadata
        """
        with self._lock:
            return {
                customer_id: {
                    "customer_id": token.customer_id,
                    "token_type": token.token_type,
                    "scope": token.scope,
                    "expires_at": datetime.fromtimestamp(token.expires_at, tz=timezone.utc).isoformat(),
                    "is_expired": self._is_token_expired(token),
                    "has_refresh_token": token.refresh_token is not None,
                    "created_at": datetime.fromtimestamp(token.created_at, tz=timezone.utc).isoformat(),
                    "last_refreshed_at": (
                        datetime.fromtimestamp(token.last_refreshed_at, tz=timezone.utc).isoformat()
                        if token.last_refreshed_at else None
                    ),
                    "refresh_count": token.refresh_count
                }
                for customer_id, token in self._tokens.items()
            }
    
    def _log_token_operation(
        self,
        operation: str,
        customer_id: str,
        success: bool,
        error: Optional[str] = None
    ):
        """
        Log token operations for audit trail
        
        Args:
            operation: Operation type (store, refresh, revoke, etc.)
            customer_id: Telesign customer ID
            success: Whether operation succeeded
            error: Error message if failed
        """
        log_file = Path(__file__).parent / "logs" / "telesign" / "token_operations.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "customer_id": customer_id,
            "success": success,
            "error": error
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


# Global instance
_token_manager_instance: Optional[TelesignTokenManager] = None
_manager_lock = threading.Lock()


def get_token_manager() -> TelesignTokenManager:
    """Get or create global token manager instance"""
    global _token_manager_instance
    
    with _manager_lock:
        if _token_manager_instance is None:
            auto_refresh = os.getenv("TELESIGN_AUTO_REFRESH", "true").lower() == "true"
            _token_manager_instance = TelesignTokenManager(auto_refresh=auto_refresh)
        
        return _token_manager_instance