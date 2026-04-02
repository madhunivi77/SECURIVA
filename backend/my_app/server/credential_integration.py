"""
Helper functions to migrate from oauth.json to DynamoDB

Drop-in replacements for oauth.json access patterns.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from tests.dynamodb_credential_manager import DynamoDBCredentialManager
import json


# Global singleton
_credential_manager: Optional[DynamoDBCredentialManager] = None


def get_credential_manager() -> DynamoDBCredentialManager:
    """Get singleton instance of credential manager"""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = DynamoDBCredentialManager()
    return _credential_manager


def get_salesforce_credentials(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get Salesforce credentials for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with Salesforce credentials or None if not found
        
    Example:
        creds = get_salesforce_credentials("user_123")
        if creds:
            access_token = creds["access_token"]
            refresh_token = creds["refresh_token"]
            instance_url = creds["instance_url"]
    """
    manager = get_credential_manager()
    
    # Try to get org_id for user (implement based on your user->org mapping)
    org_id = get_org_id_for_user(user_id)
    
    if not org_id:
        # Fallback: use user_id as org_id (single-tenant mode)
        org_id = user_id
    
    return manager.get_credentials(
        org_id=org_id,
        service_name="salesforce",
        credential_type="oauth"
    )


def get_google_credentials(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get Google credentials for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with Google OAuth credentials or None if not found
    """
    manager = get_credential_manager()
    org_id = get_org_id_for_user(user_id) or user_id
    
    return manager.get_credentials(
        org_id=org_id,
        service_name="google",
        credential_type="oauth"
    )


def get_telesign_credentials(org_id: str) -> Optional[Dict[str, Any]]:
    """
    Get Telesign API credentials for an organization
    
    Args:
        org_id: Organization ID
        
    Returns:
        Dict with Telesign credentials or None if not found
        {
            "customer_id": "...",
            "api_key": "..."
        }
    """
    manager = get_credential_manager()
    
    return manager.get_credentials(
        org_id=org_id,
        service_name="telesign",
        credential_type="api_key"
    )


def store_salesforce_credentials(
    user_id: str,
    access_token: str,
    refresh_token: str,
    instance_url: str,
    salesforce_user_id: str,
    org_id_override: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Store Salesforce OAuth credentials
    
    Args:
        user_id: User ID (who created the connection)
        access_token: Salesforce access token
        refresh_token: Salesforce refresh token
        instance_url: Salesforce instance URL
        salesforce_user_id: Salesforce user ID
        org_id_override: Optional org ID (defaults to user_id)
        metadata: Optional metadata dict
        
    Returns:
        True if successful, False otherwise
    """
    manager = get_credential_manager()
    org_id = org_id_override or get_org_id_for_user(user_id) or user_id
    
    return manager.store_credentials(
        org_id=org_id,
        service_name="salesforce",
        credential_type="oauth",
        credential_data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "instance_url": instance_url,
            "salesforce_user_id": salesforce_user_id
        },
        created_by=user_id,
        metadata=metadata or {}
    )


def get_org_id_for_user(user_id: str) -> Optional[str]:
    """
    Get organization ID for a user
    
    TODO: Implement based on your user->org mapping
    
    Options:
    1. Query SecuriVA_Users table in DynamoDB
    2. Use API key to look up org
    3. Default to user_id (single-tenant mode)
    
    For now, returns user_id as org_id (single-tenant)
    """
    # IMPLEMENTATION NEEDED:
    # manager = get_credential_manager()
    # user_data = manager.users_table.get_item(Key={'user_id': user_id})
    # return user_data.get('Item', {}).get('org_id')
    
    # Fallback: single-tenant mode
    return user_id


def update_salesforce_tokens(
    user_id: str,
    new_access_token: str,
    issued_at: str
) -> bool:
    """
    Update Salesforce access token after refresh
    
    Args:
        user_id: User ID
        new_access_token: New access token from refresh
        issued_at: Token issue timestamp
        
    Returns:
        True if successful
    """
    # Get existing credentials
    creds = get_salesforce_credentials(user_id)
    if not creds:
        return False
    
    # Update with new token
    creds["access_token"] = new_access_token
    creds["issued_at"] = issued_at
    
    # Remove metadata fields
    creds.pop("_metadata", None)
    
    # Store back
    org_id = get_org_id_for_user(user_id) or user_id
    manager = get_credential_manager()
    
    return manager.store_credentials(
        org_id=org_id,
        service_name="salesforce",
        credential_type="oauth",
        credential_data=creds,
        created_by=user_id
    )


# Legacy compatibility: Mimic oauth.json structure
class CredentialStore:
    """
    Legacy-compatible credential store
    
    Provides oauth.json-like interface backed by DynamoDB
    """
    
    def __init__(self):
        self.manager = get_credential_manager()
    
    def get_user_services(self, user_id: str) -> Dict[str, Any]:
        """
        Get all services for a user (oauth.json compatible)
        
        Returns:
            {
                "salesforce": {...},
                "google": {...}
            }
        """
        org_id = get_org_id_for_user(user_id) or user_id
        
        services = {}
        
        # Try to load Salesforce
        sf_creds = self.manager.get_credentials(org_id, "salesforce", "oauth")
        if sf_creds:
            metadata = sf_creds.pop("_metadata", {})
            services["salesforce"] = {
                "credentials": sf_creds,
                "instance_url": sf_creds.get("instance_url"),
                "salesforce_user_id": sf_creds.get("salesforce_user_id"),
                "connected_at": metadata.get("metadata", {}).get("connected_at"),
                "scopes": metadata.get("metadata", {}).get("scopes", [])
            }
        
        # Try to load Google
        google_creds = self.manager.get_credentials(org_id, "google", "oauth")
        if google_creds:
            metadata = google_creds.pop("_metadata", {})
            services["google"] = {
                "credentials": google_creds,
                "email": metadata.get("metadata", {}).get("email"),
                "connected_at": metadata.get("metadata", {}).get("connected_at"),
                "scopes": metadata.get("metadata", {}).get("scopes", [])
            }
        
        return services
    
    def has_salesforce(self, user_id: str) -> bool:
        """Check if user has Salesforce connected"""
        return get_salesforce_credentials(user_id) is not None


# Example usage in your existing code:

"""
BEFORE (oauth.json):

    with open("oauth.json", "r") as f:
        oauth_data = json.load(f)
    
    for user in oauth_data.get("users", []):
        if user["user_id"] == user_id:
            sf_creds = user["services"]["salesforce"]["credentials"]
            access_token = sf_creds["access_token"]


AFTER (DynamoDB):

    from my_app.server.credential_integration import get_salesforce_credentials
    
    sf_creds = get_salesforce_credentials(user_id)
    if sf_creds:
        access_token = sf_creds["access_token"]
"""
