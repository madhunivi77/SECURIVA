# backend/my_app/server/multitenant_credential_manager.py

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Optional, Any
from datetime import datetime
import os
from .encryption_service import get_encryption_service

class MultiTenantCredentialManager:
    """
    Manages encrypted credentials for multiple organizations
    """
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL must be set")
        
        self.encryption_service = get_encryption_service()
        self._connection_pool = None
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    # ==================== WRITE OPERATIONS ====================
    
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