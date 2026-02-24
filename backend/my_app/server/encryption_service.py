# backend/my_app/server/encryption_service.py

import os
import json
from typing import Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import secrets

class CredentialEncryptionService:
    """
    Handles encryption/decryption of sensitive credentials
    Uses AES-256-GCM for authenticated encryption
    """
    
    def __init__(self):
        # Load master encryption key from environment
        master_key = os.getenv("MASTER_ENCRYPTION_KEY")
        if not master_key:
            raise ValueError("MASTER_ENCRYPTION_KEY must be set in environment")
        
        # Derive encryption key from master key
        self.key = self._derive_key(master_key.encode())
        self.aesgcm = AESGCM(self.key)
    
    def _derive_key(self, master_key: bytes) -> bytes:
        """Derive 256-bit encryption key from master key"""
        salt = os.getenv("ENCRYPTION_SALT", "securiva-salt-v1").encode()
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,
        )
        
        return kdf.derive(master_key)
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> bytes:
        """
        Encrypt credential dictionary
        
        Args:
            credentials: Dict containing sensitive data
                {
                    "customer_id": "C0998FAD-...",
                    "api_key": "iaSD1BM6IM...",
                    "metadata": {...}
                }
        
        Returns:
            bytes: Encrypted data (nonce + ciphertext + tag)
        """
        # Serialize credentials to JSON
        plaintext = json.dumps(credentials).encode('utf-8')
        
        # Generate random nonce (96 bits for GCM)
        nonce = secrets.token_bytes(12)
        
        # Encrypt (also generates authentication tag)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        
        # Combine nonce + ciphertext (tag is included in ciphertext)
        encrypted_blob = nonce + ciphertext
        
        return encrypted_blob
    
    def decrypt_credentials(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Decrypt credential data
        
        Args:
            encrypted_data: bytes from database
        
        Returns:
            dict: Decrypted credentials
        
        Raises:
            ValueError: If decryption fails (wrong key or tampered data)
        """
        # Extract nonce (first 12 bytes)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        # Decrypt (also verifies authentication tag)
        try:
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
        
        # Deserialize JSON
        return json.loads(plaintext.decode('utf-8'))
    
    def rotate_encryption(self, old_encrypted_data: bytes, old_master_key: str) -> bytes:
        """
        Re-encrypt data with new master key (for key rotation)
        
        Args:
            old_encrypted_data: Data encrypted with old key
            old_master_key: Previous master encryption key
        
        Returns:
            bytes: Data encrypted with new key
        """
        # Create temporary service with old key
        old_service = CredentialEncryptionService()
        old_service.key = self._derive_key(old_master_key.encode())
        old_service.aesgcm = AESGCM(old_service.key)
        
        # Decrypt with old key
        credentials = old_service.decrypt_credentials(old_encrypted_data)
        
        # Encrypt with new key (self.key)
        return self.encrypt_credentials(credentials)


# Singleton instance
_encryption_service = None

def get_encryption_service() -> CredentialEncryptionService:
    """Get singleton encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = CredentialEncryptionService()
    return _encryption_service