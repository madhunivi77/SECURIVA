# backend/my_app/server/multitenant_credential_manager.py

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import os
from pathlib import Path
import json
from google.oauth2.credentials import Credentials

# Conditional import for encryption service
try:
    from .encryption_service import get_encryption_service
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("Warning: Encryption service not available, using basic encryption")

class MultiTenantCredentialManager:
    """
    Manages encrypted credentials for multiple organizations.
    Supports: Google OAuth (Gmail/Calendar), Salesforce OAuth, Telesign API Keys
    
    Each organization can have:
    - Multiple Google OAuth connections (per user)
    - One Salesforce connection (org-level or per-user)
    - One Telesign API key (org-level)
    """
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL must be set")
        
        if ENCRYPTION_AVAILABLE:
            self.encryption_service = get_encryption_service()
        else:
            self.encryption_service = None
        
        self._connection_pool = None
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def _encrypt_data(self, data: Dict) -> bytes:
        """Encrypt credential data"""
        if self.encryption_service:
            return self.encryption_service.encrypt_credentials(data)
        else:
            # Fallback: basic JSON encoding (NOT SECURE - for development only)
            return json.dumps(data).encode('utf-8')
    
    def _decrypt_data(self, encrypted_data: bytes) -> Dict:
        """Decrypt credential data"""
        if self.encryption_service:
            return self.encryption_service.decrypt_credentials(encrypted_data)
        else:
            # Fallback: basic JSON decoding
            return json.loads(encrypted_data.decode('utf-8'))
    
    # ==================== GOOGLE OAUTH OPERATIONS ====================
    
    def store_google_oauth_credentials(
        self,
        org_id: str,
        user_id: str,
        credentials: Credentials,
        user_email: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store Google OAuth credentials for a user in an organization
        
        Args:
            org_id: Organization UUID
            user_id: User UUID
            credentials: Google OAuth2 Credentials object
            user_email: User's Google email address
            metadata: Optional metadata (name, profile picture, etc.)
        
        Returns:
            str: credential_id
        """
        # Prepare credential data
        credential_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            "user_email": user_email,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        # Encrypt credentials
        encrypted_data = self._encrypt_data(credential_data)
        
        # Store in database
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Upsert credentials (one Google account per user per org)
            cursor.execute("""
                INSERT INTO organization_credentials 
                    (org_id, user_id, service_name, credential_type, encrypted_data, 
                     created_by, status, encryption_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (org_id, user_id, service_name, credential_type)
                DO UPDATE SET
                    encrypted_data = EXCLUDED.encrypted_data,
                    updated_at = NOW(),
                    status = 'active'
                RETURNING credential_id
            """, (
                org_id,
                user_id,
                'google',
                'oauth',
                encrypted_data,
                user_id,
                'active',
                'v1'
            ))
            
            credential_id = cursor.fetchone()['credential_id']
            
            # Log action
            self._log_credential_action(
                org_id, credential_id, 'created', user_id, success=True
            )
            
            conn.commit()
            return str(credential_id)
            
        except Exception as e:
            conn.rollback()
            self._log_credential_action(
                org_id, None, 'created', user_id, 
                success=False, error=str(e)
            )
            raise
        finally:
            conn.close()
    
    def get_google_oauth_credentials(
        self, 
        org_id: str, 
        user_id: str
    ) -> Optional[Credentials]:
        """
        Retrieve and decrypt Google OAuth credentials for a user
        
        Args:
            org_id: Organization UUID
            user_id: User UUID
        
        Returns:
            Credentials: Google OAuth2 Credentials object
            None: If no credentials found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT credential_id, encrypted_data, status
                FROM organization_credentials
                WHERE org_id = %s 
                  AND user_id = %s
                  AND service_name = 'google'
                  AND credential_type = 'oauth'
                  AND status = 'active'
            """, (org_id, user_id))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Decrypt credentials
            decrypted = self._decrypt_data(bytes(row['encrypted_data']))
            
            # Update usage statistics
            cursor.execute("""
                UPDATE organization_credentials
                SET last_used_at = NOW(),
                    usage_count = usage_count + 1
                WHERE credential_id = %s
            """, (row['credential_id'],))
            
            conn.commit()
            
            # Reconstruct Credentials object
            expiry = None
            if decrypted.get("expiry"):
                expiry = datetime.fromisoformat(decrypted["expiry"])
            
            return Credentials(
                token=decrypted["token"],
                refresh_token=decrypted.get("refresh_token"),
                token_uri=decrypted["token_uri"],
                client_id=decrypted["client_id"],
                client_secret=decrypted["client_secret"],
                scopes=decrypted["scopes"],
                expiry=expiry
            )
            
        finally:
            conn.close()
    
    def refresh_google_oauth_token(
        self, 
        org_id: str, 
        user_id: str
    ) -> Optional[Credentials]:
        """
        Refresh an expired Google OAuth token
        
        Args:
            org_id: Organization UUID
            user_id: User UUID
        
        Returns:
            Credentials: Updated Credentials object
            None: If refresh failed
        """
        from google.auth.transport.requests import Request
        
        creds = self.get_google_oauth_credentials(org_id, user_id)
        
        if not creds:
            return None
        
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                
                # Store updated credentials
                self.store_google_oauth_credentials(
                    org_id=org_id,
                    user_id=user_id,
                    credentials=creds,
                    user_email=""  # Email doesn't change
                )
                
                return creds
                
            except Exception as e:
                print(f"Failed to refresh Google token: {e}")
                return None
        
        return creds
    
    # ==================== SALESFORCE OAUTH OPERATIONS ====================
    
    def store_salesforce_credentials(
        self,
        org_id: str,
        user_id: str,
        access_token: str,
        refresh_token: str,
        instance_url: str,
        sf_user_id: str = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store Salesforce OAuth credentials for an organization
        
        Args:
            org_id: Organization UUID
            user_id: User UUID who connected Salesforce
            access_token: Salesforce access token
            refresh_token: Salesforce refresh token
            instance_url: Salesforce instance URL
            sf_user_id: Salesforce user ID
            metadata: Optional metadata (org name, edition, etc.)
        
        Returns:
            str: credential_id
        """
        credential_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "instance_url": instance_url,
            "sf_user_id": sf_user_id,
            "issued_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        encrypted_data = self._encrypt_data(credential_data)
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Upsert - one Salesforce connection per org
            cursor.execute("""
                INSERT INTO organization_credentials 
                    (org_id, user_id, service_name, credential_type, encrypted_data, 
                     created_by, status, encryption_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (org_id, service_name, credential_type)
                DO UPDATE SET
                    encrypted_data = EXCLUDED.encrypted_data,
                    user_id = EXCLUDED.user_id,
                    updated_at = NOW(),
                    status = 'active'
                RETURNING credential_id
            """, (
                org_id,
                user_id,
                'salesforce',
                'oauth',
                encrypted_data,
                user_id,
                'active',
                'v1'
            ))
            
            credential_id = cursor.fetchone()['credential_id']
            
            self._log_credential_action(
                org_id, credential_id, 'created', user_id, success=True
            )
            
            conn.commit()
            return str(credential_id)
            
        except Exception as e:
            conn.rollback()
            self._log_credential_action(
                org_id, None, 'created', user_id, 
                success=False, error=str(e)
            )
            raise
        finally:
            conn.close()
    
    def get_salesforce_credentials(self, org_id: str) -> Optional[Dict[str, str]]:
        """
        Retrieve and decrypt Salesforce credentials for an organization
        
        Args:
            org_id: Organization UUID
        
        Returns:
            dict: {"access_token": "...", "refresh_token": "...", "instance_url": "...", ...}
            None: If no credentials found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT credential_id, encrypted_data, status
                FROM organization_credentials
                WHERE org_id = %s 
                  AND service_name = 'salesforce'
                  AND credential_type = 'oauth'
                  AND status = 'active'
            """, (org_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Decrypt credentials
            decrypted = self._decrypt_data(bytes(row['encrypted_data']))
            
            # Update usage statistics
            cursor.execute("""
                UPDATE organization_credentials
                SET last_used_at = NOW(),
                    usage_count = usage_count + 1
                WHERE credential_id = %s
            """, (row['credential_id'],))
            
            conn.commit()
            
            return decrypted
            
        finally:
            conn.close()
    
    def refresh_salesforce_token(self, org_id: str) -> Optional[Dict[str, str]]:
        """
        Refresh Salesforce access token using refresh token
        
        Args:
            org_id: Organization UUID
        
        Returns:
            dict: Updated credentials with new access_token
            None: If refresh failed
        """
        import requests
        
        creds = self.get_salesforce_credentials(org_id)
        
        if not creds or not creds.get("refresh_token"):
            return None
        
        # Get Salesforce OAuth app credentials from environment
        SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
        SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
        
        if not SF_CLIENT_ID or not SF_CLIENT_SECRET:
            print("Error: SF_CLIENT_ID and SF_CLIENT_SECRET must be set")
            return None
        
        try:
            # Refresh token request
            response = requests.post(
                f"{creds['instance_url']}/services/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": SF_CLIENT_ID,
                    "client_secret": SF_CLIENT_SECRET,
                    "refresh_token": creds["refresh_token"]
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update credentials with new token
                creds["access_token"] = token_data["access_token"]
                creds["issued_at"] = datetime.now().isoformat()
                
                # Store updated credentials
                conn = self._get_connection()
                cursor = conn.cursor()
                
                encrypted_data = self._encrypt_data(creds)
                
                cursor.execute("""
                    UPDATE organization_credentials
                    SET encrypted_data = %s,
                        updated_at = NOW()
                    WHERE org_id = %s 
                      AND service_name = 'salesforce'
                      AND credential_type = 'oauth'
                """, (encrypted_data, org_id))
                
                conn.commit()
                conn.close()
                
                return creds
            else:
                print(f"Failed to refresh Salesforce token: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error refreshing Salesforce token: {e}")
            return None
    
    # ==================== TELESIGN API KEY OPERATIONS ====================
    
    def store_telesign_credentials(
        self,
        org_id: str,
        customer_id: str,
        api_key: str,
        created_by: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store Telesign credentials for an organization
        
        Args:
            org_id: Organization UUID
            customer_id: Telesign Customer ID
            api_key: Telesign API Key
            created_by: User ID who added credentials
            metadata: Optional metadata (e.g., account name, tier)
        
        Returns:
            str: credential_id
        """
        # Prepare credential data
        credential_data = {
            "customer_id": customer_id,
            "api_key": api_key,
            "service": "telesign",
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        # Encrypt credentials
        encrypted_data = self.encryption_service.encrypt_credentials(credential_data)
        
        # Store in database
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Upsert credentials (update if exists, insert if not)
            cursor.execute("""
                INSERT INTO organization_credentials 
                    (org_id, service_name, credential_type, encrypted_data, 
                     created_by, status, encryption_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (org_id, service_name, credential_type)
                DO UPDATE SET
                    encrypted_data = EXCLUDED.encrypted_data,
                    updated_at = NOW(),
                    status = 'active'
                RETURNING credential_id
            """, (
                org_id,
                'telesign',
                'api_key',
                encrypted_data,
                created_by,
                'active',
                'v1'
            ))
            
            credential_id = cursor.fetchone()['credential_id']
            
            # Log action
            self._log_credential_action(
                org_id, credential_id, 'created', created_by, success=True
            )
            
            conn.commit()
            return str(credential_id)
            
        except Exception as e:
            conn.rollback()
            self._log_credential_action(
                org_id, None, 'created', created_by, 
                success=False, error=str(e)
            )
            raise
        finally:
            conn.close()
    
    # ==================== READ OPERATIONS ====================
    
    def get_telesign_credentials(self, org_id: str) -> Optional[Dict[str, str]]:
        """
        Retrieve and decrypt Telesign credentials for an organization
        
        Args:
            org_id: Organization UUID
        
        Returns:
            dict: {"customer_id": "...", "api_key": "...", "metadata": {...}}
            None: If no credentials found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT credential_id, encrypted_data, status
                FROM organization_credentials
                WHERE org_id = %s 
                  AND service_name = 'telesign'
                  AND credential_type = 'api_key'
                  AND status = 'active'
            """, (org_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Decrypt credentials
            decrypted = self.encryption_service.decrypt_credentials(
                bytes(row['encrypted_data'])
            )
            
            # Update usage statistics
            cursor.execute("""
                UPDATE organization_credentials
                SET last_used_at = NOW(),
                    usage_count = usage_count + 1
                WHERE credential_id = %s
            """, (row['credential_id'],))
            
            conn.commit()
            
            return {
                "customer_id": decrypted["customer_id"],
                "api_key": decrypted["api_key"],
                "metadata": decrypted.get("metadata", {})
            }
            
        finally:
            conn.close()
    
    def validate_telesign_credentials(
        self, 
        org_id: str,
        test_phone: str = None
    ) -> Dict[str, Any]:
        """
        Validate Telesign credentials by making a test API call
        
        Args:
            org_id: Organization UUID
            test_phone: Optional test phone number
        
        Returns:
            dict: {"valid": bool, "error": str, "details": {...}}
        """
        creds = self.get_telesign_credentials(org_id)
        
        if not creds:
            return {
                "valid": False,
                "error": "No credentials found for organization"
            }
        
        try:
            # Test credentials with Telesign API
            from telesignenterprise.messaging import MessagingClient
            
            client = MessagingClient(
                creds["customer_id"],
                creds["api_key"]
            )
            
            # Make a lightweight API call to validate (e.g., check balance)
            # For now, we'll just check if client creation succeeds
            
            # Update validation timestamp
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE organization_credentials
                SET validated_at = NOW()
                WHERE org_id = %s 
                  AND service_name = 'telesign'
            """, (org_id,))
            conn.commit()
            conn.close()
            
            return {
                "valid": True,
                "error": None,
                "details": {
                    "customer_id": creds["customer_id"][:10] + "...",
                    "validated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "details": {}
            }
    
    # ==================== DELETE OPERATIONS ====================
    
    def delete_telesign_credentials(
        self, 
        org_id: str,
        deleted_by: str
    ) -> bool:
        """
        Delete (revoke) Telesign credentials for an organization
        
        Args:
            org_id: Organization UUID
            deleted_by: User ID who deleted credentials
        
        Returns:
            bool: True if deleted, False if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Soft delete (mark as revoked)
            cursor.execute("""
                UPDATE organization_credentials
                SET status = 'revoked',
                    updated_at = NOW()
                WHERE org_id = %s 
                  AND service_name = 'telesign'
                  AND credential_type = 'api_key'
                RETURNING credential_id
            """, (org_id,))
            
            result = cursor.fetchone()
            
            if result:
                self._log_credential_action(
                    org_id, result['credential_id'], 
                    'deleted', deleted_by, success=True
                )
                conn.commit()
                return True
            
            conn.commit()
            return False
            
        finally:
            conn.close()
    
    # ==================== UTILITY METHODS ====================
    
    def list_organization_credentials(self, org_id: str) -> List[Dict[str, Any]]:
        """
        List all credentials for an organization (metadata only, no secrets)
        
        Args:
            org_id: Organization UUID
        
        Returns:
            list: List of credential metadata dicts
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    credential_id,
                    service_name,
                    credential_type,
                    status,
                    created_at,
                    updated_at,
                    last_used_at,
                    usage_count,
                    validated_at
                FROM organization_credentials
                WHERE org_id = %s
                ORDER BY service_name, created_at DESC
            """, (org_id,))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        finally:
            conn.close()
    
    def get_org_credential_status(self, org_id: str) -> Dict[str, bool]:
        """
        Get a summary of which services are configured for an organization
        
        Args:
            org_id: Organization UUID
        
        Returns:
            dict: {"google": bool, "salesforce": bool, "telesign": bool}
        """
        credentials = self.list_organization_credentials(org_id)
        
        status = {
            "google": False,
            "salesforce": False,
            "telesign": False
        }
        
        for cred in credentials:
            if cred['status'] == 'active':
                service = cred['service_name']
                if service in status:
                    status[service] = True
        
        return status
    
    def revoke_all_user_credentials(self, org_id: str, user_id: str, revoked_by: str) -> int:
        """
        Revoke all credentials associated with a specific user
        (Used when removing a user from an organization)
        
        Args:
            org_id: Organization UUID
            user_id: User UUID to revoke credentials for
            revoked_by: User ID performing the revocation
        
        Returns:
            int: Number of credentials revoked
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE organization_credentials
                SET status = 'revoked',
                    updated_at = NOW()
                WHERE org_id = %s 
                  AND user_id = %s
                  AND status = 'active'
                RETURNING credential_id
            """, (org_id, user_id))
            
            revoked_creds = cursor.fetchall()
            
            # Log each revocation
            for cred in revoked_creds:
                self._log_credential_action(
                    org_id, cred['credential_id'], 
                    'revoked', revoked_by, success=True
                )
            
            conn.commit()
            return len(revoked_creds)
            
        finally:
            conn.close()
    
    def _log_credential_action(
        self,
        org_id: str,
        credential_id: Optional[str],
        action: str,
        performed_by: str,
        success: bool = True,
        error: str = None,
        ip_address: str = None
    ):
        """Log credential access for audit trail"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO credential_audit_log
                    (org_id, credential_id, action, performed_by, 
                     success, error_message, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                org_id, credential_id, action, performed_by,
                success, error, ip_address
            ))
            conn.commit()
        except Exception as e:
            print(f"Failed to log credential action: {e}")
        finally:
            conn.close()


# Singleton instance
_credential_manager = None

def get_credential_manager() -> MultiTenantCredentialManager:
    """Get singleton credential manager instance"""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = MultiTenantCredentialManager()
    return _credential_manager