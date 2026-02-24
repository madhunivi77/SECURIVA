# Multi-Tenant Credential Management

## Overview

This guide explains how to use the multi-tenant credential management system in SECURIVA. Each organization has isolated credentials for:

- **Google OAuth** (Gmail, Calendar) - per user
- **Salesforce OAuth** - per organization
- **Telesign API Keys** - per organization

## Architecture

```
┌─────────────────────────────────────────────────┐
│  MCP Server Tools (Gmail, Salesforce, SMS)     │
│                      ↓                          │
│  MultiTenantMCPAdapter (get credentials)       │
│                      ↓                          │
│  MultiTenantCredentialManager (database)       │
│                      ↓                          │
│  PostgreSQL (encrypted credentials)            │
└─────────────────────────────────────────────────┘
```

---

## Setup

### 1. Database Migration

Run the migration script to create tables:

```bash
psql $DATABASE_URL < backend/my_app/server/migrations/001_multitenant_credentials_schema.sql
```

### 2. Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/securiva

# JWT Secret
JWT_SECRET_KEY=your-secret-key-here

# Encryption Key (for credential encryption)
ENCRYPTION_KEY=base64-encoded-32-byte-key

# Google OAuth (for your app)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Salesforce OAuth (for your app)
SF_CLIENT_ID=your-salesforce-consumer-key
SF_CLIENT_SECRET=your-salesforce-consumer-secret
```

---

## Usage in MCP Server

### Update `mcp_server.py`

Replace the old `getGoogleCreds()` function with the new adapter:

```python
# backend/my_app/server/mcp_server.py

from .multitenant_mcp_adapter import get_mcp_adapter

# Initialize adapter
mcp_adapter = get_mcp_adapter()

# Updated function
def getGoogleCreds(ctx):
    """Get Google credentials using multi-tenant adapter"""
    return mcp_adapter.get_google_credentials(ctx)

# Example tool using Google credentials
@mcp.tool()
def listEmails(context: Context, max_results: int = 10):
    """List recent emails from Gmail"""
    creds = getGoogleCreds(context)
    if not creds:
        return "User not authenticated with Google OAuth"
    
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=max_results
        ).execute()
        # ... rest of implementation
    except HttpError as error:
        return f"An error occurred: {error}"
```

### Salesforce Tools

```python
# Updated Salesforce credential retrieval
def getSalesforceCreds(ctx):
    """Get Salesforce credentials using multi-tenant adapter"""
    return mcp_adapter.get_salesforce_credentials(ctx)

@mcp.tool()
def listSalesforceAccounts(context: Context, limit: int = 10):
    """List Salesforce accounts"""
    creds = getSalesforceCreds(context)
    if not creds:
        return "Organization not authenticated with Salesforce"
    
    try:
        headers = {
            "Authorization": f"Bearer {creds['access_token']}",
            "Content-Type": "application/json"
        }
        
        url = f"{creds['instance_url']}/services/data/v57.0/query/"
        params = {"q": f"SELECT Id, Name, Industry FROM Account LIMIT {limit}"}
        
        response = requests.get(url, headers=headers, params=params)
        # ... rest of implementation
    except Exception as e:
        return f"Error: {e}"
```

### Telesign Tools

```python
# Updated Telesign client retrieval
def getTelesignClients(ctx):
    """Get Telesign clients using multi-tenant adapter"""
    return mcp_adapter.get_telesign_clients(ctx)

@mcp.tool()
def sendSMS(context: Context, phone_number: str, message: str):
    """Send SMS using Telesign"""
    clients = getTelesignClients(context)
    if not clients:
        return "Organization not configured with Telesign"
    
    try:
        messaging_client = clients["messaging"]
        response = messaging_client.message(phone_number, message, "OTP")
        
        return f"SMS sent successfully. Reference ID: {response.body.get('reference_id')}"
    except Exception as e:
        return f"Error: {e}"
```

---

## API Endpoints for Credential Management

### Store Google OAuth Credentials

```python
# backend/my_app/server/credential_api.py

from starlette.routing import Route
from starlette.responses import JSONResponse
from .multitenant_credential_manager import get_credential_manager
from google.oauth2.credentials import Credentials

async def store_google_credentials(request):
    """
    Store Google OAuth credentials after user completes OAuth flow
    Called from /callback endpoint
    """
    # Get org_id and user_id from JWT or session
    org_id = request.state.org_id
    user_id = request.state.user_id
    
    # Get credentials from OAuth flow
    data = await request.json()
    creds = Credentials(
        token=data['access_token'],
        refresh_token=data['refresh_token'],
        token_uri=data['token_uri'],
        client_id=data['client_id'],
        client_secret=data['client_secret'],
        scopes=data['scopes']
    )
    
    # Store in database
    credential_manager = get_credential_manager()
    credential_id = credential_manager.store_google_oauth_credentials(
        org_id=org_id,
        user_id=user_id,
        credentials=creds,
        user_email=data['email'],
        metadata={"name": data.get('name')}
    )
    
    return JSONResponse({
        "success": True,
        "credential_id": credential_id,
        "message": "Google credentials stored successfully"
    })
```

### Store Salesforce Credentials

```python
async def store_salesforce_credentials(request):
    """
    Store Salesforce OAuth credentials after OAuth flow
    Called from /salesforce/callback endpoint
    """
    org_id = request.state.org_id
    user_id = request.state.user_id
    
    data = await request.json()
    
    credential_manager = get_credential_manager()
    credential_id = credential_manager.store_salesforce_credentials(
        org_id=org_id,
        user_id=user_id,
        access_token=data['access_token'],
        refresh_token=data['refresh_token'],
        instance_url=data['instance_url'],
        sf_user_id=data.get('id'),
        metadata={"org_name": data.get('organization_name')}
    )
    
    return JSONResponse({
        "success": True,
        "credential_id": credential_id,
        "message": "Salesforce credentials stored successfully"
    })
```

### Store Telesign Credentials

```python
async def store_telesign_credentials(request):
    """
    Store Telesign API credentials
    Called from settings/integrations page
    """
    org_id = request.state.org_id
    user_id = request.state.user_id
    
    data = await request.json()
    
    # Validate credentials first
    credential_manager = get_credential_manager()
    
    # Store credentials
    credential_id = credential_manager.store_telesign_credentials(
        org_id=org_id,
        customer_id=data['customer_id'],
        api_key=data['api_key'],
        created_by=user_id,
        metadata={"account_name": data.get('account_name')}
    )
    
    # Validate credentials
    validation = credential_manager.validate_telesign_credentials(org_id)
    
    if not validation['valid']:
        return JSONResponse({
            "success": False,
            "error": "Invalid Telesign credentials",
            "details": validation['error']
        }, status_code=400)
    
    return JSONResponse({
        "success": True,
        "credential_id": credential_id,
        "message": "Telesign credentials stored and validated successfully"
    })
```

### List Organization Credentials

```python
async def list_credentials(request):
    """
    Get status of all credentials for an organization
    """
    org_id = request.state.org_id
    
    credential_manager = get_credential_manager()
    credentials = credential_manager.list_organization_credentials(org_id)
    status = credential_manager.get_org_credential_status(org_id)
    
    return JSONResponse({
        "org_id": org_id,
        "status": status,
        "credentials": credentials
    })
```

---

## JWT Token Format

The JWT token **must** include `org_id` for multi-tenant mode:

```json
{
  "sub": "user-uuid-here",
  "org_id": "organization-uuid-here",
  "role": "admin",
  "exp": 1709567890,
  "iat": 1709564290
}
```

### Update JWT Generation

```python
# backend/my_app/auth_server/main.py

async def get_token(request):
    """Generate JWT with org_id"""
    body = await request.json()
    user_id = body.get('user_id')
    org_id = body.get('org_id')  # NEW: required for multi-tenant
    
    if not org_id:
        return JSONResponse({"error": "org_id required"}, status_code=400)
    
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': user_id,
        'org_id': org_id,  # NEW: organization identifier
        'role': body.get('role', 'member'),
        'client_id': 'securiva-app'
    }
    
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    
    return JSONResponse({
        "access_token": encoded_jwt,
        "token_type": "Bearer"
    })
```

---

## Migration from Single-Tenant

### Migration Script

```python
# backend/my_app/server/migrate_oauth_json_to_db.py

import json
from pathlib import Path
from multitenant_credential_manager import get_credential_manager
from google.oauth2.credentials import Credentials
import uuid

def migrate_oauth_json_to_database():
    """Migrate oauth.json to multi-tenant database"""
    
    oauth_file = Path(__file__).parent / "oauth.json"
    if not oauth_file.exists():
        print("No oauth.json found")
        return
    
    with open(oauth_file, 'r') as f:
        data = json.load(f)
    
    credential_manager = get_credential_manager()
    
    # Create default organization
    default_org_id = str(uuid.uuid4())
    print(f"Creating default organization: {default_org_id}")
    
    # Migrate each user
    users = data.get('users', [])
    for user in users:
        user_id = user.get('user_id')
        services = user.get('services', {})
        
        print(f"\nMigrating user: {user_id}")
        
        # Migrate Google credentials
        google_service = services.get('google')
        if google_service:
            creds_json = json.loads(google_service['credentials'])
            creds = Credentials.from_authorized_user_info(creds_json)
            
            credential_manager.store_google_oauth_credentials(
                org_id=default_org_id,
                user_id=user_id,
                credentials=creds,
                user_email=google_service.get('email', ''),
                metadata={"migrated_from": "oauth.json"}
            )
            print(f"  ✓ Google credentials migrated")
        
        # Migrate Salesforce credentials
        sf_service = services.get('salesforce')
        if sf_service:
            creds = sf_service.get('credentials', {})
            
            credential_manager.store_salesforce_credentials(
                org_id=default_org_id,
                user_id=user_id,
                access_token=creds.get('access_token'),
                refresh_token=creds.get('refresh_token'),
                instance_url=creds.get('instance_url'),
                metadata={"migrated_from": "oauth.json"}
            )
            print(f"  ✓ Salesforce credentials migrated")
    
    print(f"\nMigration complete! Default org_id: {default_org_id}")
    print(f"Update your JWT tokens to include this org_id")

if __name__ == "__main__":
    migrate_oauth_json_to_database()
```

---

## Security Best Practices

1. **Always encrypt credentials** - Use the encryption service
2. **Use RLS policies** - Set `app.current_org_id` for every request
3. **Audit all access** - Credential audit log tracks everything
4. **Rotate keys regularly** - Implement key rotation for Telesign
5. **Validate on storage** - Test credentials before saving
6. **Auto-refresh tokens** - Refresh OAuth tokens before expiry

---

## Testing

```python
# Test credential storage and retrieval
from multitenant_credential_manager import get_credential_manager

credential_manager = get_credential_manager()

# Test Telesign
org_id = "11111111-1111-1111-1111-111111111111"
user_id = "22222222-2222-2222-2222-222222222222"

credential_manager.store_telesign_credentials(
    org_id=org_id,
    customer_id="test_customer_id",
    api_key="test_api_key",
    created_by=user_id
)

creds = credential_manager.get_telesign_credentials(org_id)
print(creds)  # {"customer_id": "...", "api_key": "..."}
```

---

## Troubleshooting

### "No org_id in JWT token"

- Ensure JWT includes `org_id` field
- Update auth server to generate org-aware tokens

### "Encryption service not available"

- Install encryption dependencies
- Create encryption key: `python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"`
- Set `ENCRYPTION_KEY` environment variable

### "User not authenticated"

- Check that credentials exist in database
- Verify `org_id` and `user_id` match JWT claims
- Check credential status is 'active'

---

## Next Steps

1. **Implement frontend UI** - Organization settings page for managing credentials
2. **Add webhook notifications** - Alert when credentials expire
3. **Usage tracking** - Monitor API calls per organization
4. **Billing integration** - Connect to Stripe for usage-based billing
5. **Credential rotation** - Auto-rotate API keys periodically
