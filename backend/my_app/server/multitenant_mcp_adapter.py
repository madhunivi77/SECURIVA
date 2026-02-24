# backend/my_app/server/multitenant_mcp_adapter.py
"""
Multi-tenant adapter for MCP server tools
Provides organization-scoped credential retrieval for Gmail, Salesforce, and Telesign
"""

from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials
from telesignenterprise.messaging import MessagingClient
from telesignenterprise.verify import VerifyClient
from telesign.score import ScoreClient
import jwt
import os
from pathlib import Path
import json

# Try to import the credential manager
try:
    from .multitenant_credential_manager import get_credential_manager
    MULTITENANT_MODE = True
except ImportError:
    MULTITENANT_MODE = False
    print("Running in single-tenant mode (legacy)")


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


class MultiTenantMCPAdapter:
    """
    Adapter to retrieve organization-specific credentials for MCP tools
    
    This class abstracts away the difference between:
    - Single-tenant mode (oauth.json file)
    - Multi-tenant mode (database with encryption)
    """
    
    def __init__(self):
        if MULTITENANT_MODE:
            self.credential_manager = get_credential_manager()
        else:
            self.credential_manager = None
    
    def extract_org_and_user(self, context) -> tuple[Optional[str], Optional[str]]:
        """
        Extract org_id and user_id from MCP context
        
        Args:
            context: MCP Context object with request headers
        
        Returns:
            tuple: (org_id, user_id) or (None, None)
        """
        try:
            # Extract JWT from Authorization header
            auth_header = context.request_context.request.headers.get('Authorization')
            if not auth_header:
                return None, None
            
            encoded_token = auth_header.split(" ")[1]
            payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
            
            org_id = payload.get('org_id')  # New field in multi-tenant JWT
            user_id = payload.get('sub')     # Standard subject claim
            
            return org_id, user_id
            
        except Exception as e:
            print(f"Error extracting org/user from context: {e}")
            return None, None
    
    # ==================== GOOGLE OAUTH ====================
    
    def get_google_credentials(self, context) -> Optional[Credentials]:
        """
        Get Google OAuth credentials for the current user/org
        
        Args:
            context: MCP Context object
        
        Returns:
            Credentials: Google OAuth2 Credentials object or None
        """
        if MULTITENANT_MODE:
            return self._get_google_credentials_multitenant(context)
        else:
            return self._get_google_credentials_legacy(context)
    
    def _get_google_credentials_multitenant(self, context) -> Optional[Credentials]:
        """Get Google credentials from database (multi-tenant)"""
        org_id, user_id = self.extract_org_and_user(context)
        
        if not org_id or not user_id:
            print("No org_id or user_id in JWT token")
            return None
        
        try:
            # Get credentials from database
            creds = self.credential_manager.get_google_oauth_credentials(org_id, user_id)
            
            # Check if token needs refresh
            if creds and creds.expired and creds.refresh_token:
                print(f"Refreshing expired Google token for user {user_id}")
                creds = self.credential_manager.refresh_google_oauth_token(org_id, user_id)
            
            return creds
            
        except Exception as e:
            print(f"Error getting Google credentials: {e}")
            return None
    
    def _get_google_credentials_legacy(self, context) -> Optional[Credentials]:
        """Get Google credentials from oauth.json (single-tenant legacy)"""
        try:
            # Extract user_id from JWT
            encoded_token = context.request_context.request.headers.get('Authorization').split(" ")[1]
            payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get('sub')

            # Load from oauth.json
            oauth_file = Path(__file__).parent / "oauth.json"
            if not oauth_file.exists():
                return None
            
            with open(oauth_file, "r") as f:
                data = json.load(f)
                users = data.get("users", [])
                
                for user in users:
                    if user.get("user_id") == user_id:
                        google_service = user.get("services", {}).get("google")
                        if google_service:
                            credentials_json = google_service.get("credentials")
                            if credentials_json:
                                return Credentials.from_authorized_user_info(json.loads(credentials_json))
            
            return None

        except Exception as e:
            print(f"Error getting Google credentials (legacy): {e}")
            return None
    
    # ==================== SALESFORCE ====================
    
    def get_salesforce_credentials(self, context) -> Optional[Dict[str, Any]]:
        """
        Get Salesforce credentials for the current organization
        
        Args:
            context: MCP Context object
        
        Returns:
            dict: {"access_token": "...", "refresh_token": "...", "instance_url": "..."}
        """
        if MULTITENANT_MODE:
            return self._get_salesforce_credentials_multitenant(context)
        else:
            return self._get_salesforce_credentials_legacy(context)
    
    def _get_salesforce_credentials_multitenant(self, context) -> Optional[Dict]:
        """Get Salesforce credentials from database (multi-tenant)"""
        org_id, user_id = self.extract_org_and_user(context)
        
        if not org_id:
            print("No org_id in JWT token")
            return None
        
        try:
            creds = self.credential_manager.get_salesforce_credentials(org_id)
            
            # Auto-refresh if needed (you could add expiry checking logic)
            if creds:
                # Salesforce tokens typically expire after a period
                # You could check issued_at and refresh if needed
                pass
            
            return creds
            
        except Exception as e:
            print(f"Error getting Salesforce credentials: {e}")
            return None
    
    def _get_salesforce_credentials_legacy(self, context) -> Optional[Dict]:
        """Get Salesforce credentials from oauth.json (single-tenant legacy)"""
        try:
            from .salesforce_utils import get_fresh_salesforce_credentials
            
            # Extract user_id
            encoded_token = context.request_context.request.headers.get('Authorization').split(" ")[1]
            payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get('sub')
            
            # Use existing utility
            return get_fresh_salesforce_credentials(user_id)
            
        except Exception as e:
            print(f"Error getting Salesforce credentials (legacy): {e}")
            return None
    
    # ==================== TELESIGN ====================
    
    def get_telesign_clients(self, context) -> Optional[Dict[str, Any]]:
        """
        Get Telesign client instances for the current organization
        
        Args:
            context: MCP Context object
        
        Returns:
            dict: {
                "messaging": MessagingClient,
                "verify": VerifyClient,
                "score": ScoreClient,
                "credentials": {"customer_id": "...", "api_key": "..."}
            }
        """
        if MULTITENANT_MODE:
            return self._get_telesign_clients_multitenant(context)
        else:
            return self._get_telesign_clients_legacy()
    
    def _get_telesign_clients_multitenant(self, context) -> Optional[Dict]:
        """Get Telesign clients from database (multi-tenant)"""
        org_id, user_id = self.extract_org_and_user(context)
        
        if not org_id:
            print("No org_id in JWT token")
            return None
        
        try:
            creds = self.credential_manager.get_telesign_credentials(org_id)
            
            if not creds:
                print(f"No Telesign credentials found for org {org_id}")
                return None
            
            customer_id = creds["customer_id"]
            api_key = creds["api_key"]
            
            return {
                "messaging": MessagingClient(customer_id, api_key),
                "verify": VerifyClient(customer_id, api_key),
                "score": ScoreClient(customer_id, api_key),
                "credentials": {
                    "customer_id": customer_id,
                    "api_key": api_key
                }
            }
            
        except Exception as e:
            print(f"Error getting Telesign clients: {e}")
            return None
    
    def _get_telesign_clients_legacy(self) -> Optional[Dict]:
        """Get Telesign clients from environment variables (single-tenant legacy)"""
        try:
            customer_id = os.getenv("TELESIGN_CUSTOMER_ID")
            api_key = os.getenv("TELESIGN_API_KEY")
            
            if not customer_id or not api_key:
                print("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY not set")
                return None
            
            return {
                "messaging": MessagingClient(customer_id, api_key),
                "verify": VerifyClient(customer_id, api_key),
                "score": ScoreClient(customer_id, api_key),
                "credentials": {
                    "customer_id": customer_id,
                    "api_key": api_key
                }
            }
            
        except Exception as e:
            print(f"Error getting Telesign clients (legacy): {e}")
            return None


# Singleton instance
_adapter = None

def get_mcp_adapter() -> MultiTenantMCPAdapter:
    """Get singleton MCP adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = MultiTenantMCPAdapter()
    return _adapter
