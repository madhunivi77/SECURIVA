# Multi-Tenant Quick Reference

## Files Created

1. **`multitenant_credential_manager.py`** - Core credential storage/retrieval
2. **`multitenant_mcp_adapter.py`** - Bridge between MCP tools and credentials
3. **`migrations/001_multitenant_credentials_schema.sql`** - Database schema
4. **`MULTITENANT_GUIDE.md`** - Complete usage guide
5. **`MULTITENANT_SUMMARY.md`** - Implementation summary
6. **`ARCHITECTURE_DIAGRAM.md`** - Visual architecture diagrams

---

## Quick Start

### 1. Setup Database

```bash
# Create database
createdb securiva

# Run migration
psql securiva < backend/my_app/server/migrations/001_multitenant_credentials_schema.sql

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/securiva"
export ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

### 2. Update MCP Server

```python
# backend/my_app/server/mcp_server.py

from .multitenant_mcp_adapter import get_mcp_adapter

# Initialize adapter (automatically detects mode)
mcp_adapter = get_mcp_adapter()

# Replace credential retrieval functions
def getGoogleCreds(ctx):
    return mcp_adapter.get_google_credentials(ctx)

def getSalesforceCreds(ctx):
    return mcp_adapter.get_salesforce_credentials(ctx)

def getTelesignClients(ctx):
    return mcp_adapter.get_telesign_clients(ctx)
```

### 3. Update JWT Token Generation

```python
# backend/my_app/auth_server/main.py

payload = {
    'sub': user_id,
    'org_id': org_id,  # ADD THIS FIELD
    'role': role,
    'exp': expiry,
    'iat': issued_at
}
```

### 4. Test It

```python
from multitenant_credential_manager import get_credential_manager

cm = get_credential_manager()

# Store credentials
cm.store_telesign_credentials(
    org_id="test-org-123",
    customer_id="CUST123",
    api_key="secret_key",
    created_by="admin-user"
)

# Retrieve credentials
creds = cm.get_telesign_credentials("test-org-123")
print(creds)  # {"customer_id": "CUST123", "api_key": "secret_key"}
```

---

## Cheat Sheet

### Store Credentials

```python
from multitenant_credential_manager import get_credential_manager
credential_manager = get_credential_manager()

# Google OAuth (per user)
credential_manager.store_google_oauth_credentials(
    org_id="org-uuid",
    user_id="user-uuid",
    credentials=google_credentials_object,
    user_email="user@example.com",
    metadata={"name": "John Doe"}
)

# Salesforce OAuth (per org)
credential_manager.store_salesforce_credentials(
    org_id="org-uuid",
    user_id="user-uuid-who-connected",
    access_token="00D...",
    refresh_token="5Aep...",
    instance_url="https://acme.salesforce.com",
    metadata={"org_name": "Acme Corp"}
)

# Telesign API Key (per org)
credential_manager.store_telesign_credentials(
    org_id="org-uuid",
    customer_id="CUST12345",
    api_key="secret_key_xyz",
    created_by="admin-user-uuid",
    metadata={"account_name": "Production"}
)
```

### Retrieve Credentials

```python
# Google (requires user_id)
google_creds = credential_manager.get_google_oauth_credentials(
    org_id="org-uuid",
    user_id="user-uuid"
)

# Salesforce (org-level)
sf_creds = credential_manager.get_salesforce_credentials(
    org_id="org-uuid"
)

# Telesign (org-level)
ts_creds = credential_manager.get_telesign_credentials(
    org_id="org-uuid"
)
```

### Validate & Refresh

```python
# Validate Telesign
validation = credential_manager.validate_telesign_credentials(
    org_id="org-uuid",
    test_phone="+1234567890"
)
print(validation['valid'])  # True/False

# Refresh Google token (automatic)
fresh_creds = credential_manager.refresh_google_oauth_token(
    org_id="org-uuid",
    user_id="user-uuid"
)

# Refresh Salesforce token
fresh_sf_creds = credential_manager.refresh_salesforce_token(
    org_id="org-uuid"
)
```

### List & Manage

```python
# List all credentials for an org
all_creds = credential_manager.list_organization_credentials("org-uuid")

# Get credential status
status = credential_manager.get_org_credential_status("org-uuid")
# Returns: {"google": True, "salesforce": True, "telesign": False}

# Revoke user's credentials (when removing user)
count = credential_manager.revoke_all_user_credentials(
    org_id="org-uuid",
    user_id="user-uuid",
    revoked_by="admin-uuid"
)
print(f"Revoked {count} credentials")

# Delete specific service credentials
success = credential_manager.delete_telesign_credentials(
    org_id="org-uuid",
    deleted_by="admin-uuid"
)
```

---

## Database Queries

### Check Credential Status

```sql
-- List all active credentials for an org
SELECT 
    service_name,
    credential_type,
    created_at,
    last_used_at,
    usage_count
FROM organization_credentials
WHERE org_id = 'org-uuid'
  AND status = 'active';
```

### Audit Trail

```sql
-- View credential access history
SELECT 
    action,
    performed_by,
    created_at,
    success,
    error_message
FROM credential_audit_log
WHERE org_id = 'org-uuid'
ORDER BY created_at DESC
LIMIT 50;
```

### Usage Tracking

```sql
-- Monthly usage by service
SELECT 
    service,
    COUNT(*) as api_calls,
    SUM(resource_units) as total_units
FROM usage_logs
WHERE org_id = 'org-uuid'
  AND created_at >= DATE_TRUNC('month', NOW())
GROUP BY service;
```

---

## Common Patterns

### MCP Tool with Auto-Refresh

```python
@mcp.tool()
def listEmails(context: Context, max_results: int = 10):
    """List emails with automatic token refresh"""
    creds = mcp_adapter.get_google_credentials(context)
    
    if not creds:
        return "User not authenticated with Google"
    
    # Credentials are already refreshed if needed
    service = build("gmail", "v1", credentials=creds)
    
    # Use service...
```

### Organization Settings Endpoint

```python
async def get_integrations(request):
    """Get integration status for organization"""
    org_id = request.state.org_id
    
    credential_manager = get_credential_manager()
    status = credential_manager.get_org_credential_status(org_id)
    
    return JSONResponse({
        "org_id": org_id,
        "integrations": {
            "google": {
                "enabled": status['google'],
                "description": "Gmail & Calendar"
            },
            "salesforce": {
                "enabled": status['salesforce'],
                "description": "CRM Integration"
            },
            "telesign": {
                "enabled": status['telesign'],
                "description": "SMS & Verification"
            }
        }
    })
```

### Middleware for Org Context

```python
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Extract org_id from JWT
        token = request.cookies.get('auth_token')
        if token:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            request.state.org_id = payload.get('org_id')
            request.state.user_id = payload.get('sub')
        
        response = await call_next(request)
        return response

# Add to app
app.add_middleware(TenantMiddleware)
```

---

## Troubleshooting

### Issue: "No org_id in JWT token"

**Solution:** Update JWT generation to include `org_id`:
```python
payload = {
    'sub': user_id,
    'org_id': org_id,  # ADD THIS
    'exp': expiry
}
```

### Issue: "DATABASE_URL not set"

**Solution:** Set environment variable:
```bash
export DATABASE_URL="postgresql://user:pass@localhost/securiva"
```

### Issue: "Encryption service not available"

**Solution:** Generate and set encryption key:
```bash
export ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

### Issue: "User not authenticated"

**Check:**
1. Credentials exist in database
2. JWT contains correct `org_id` and `user_id`
3. Credential status is 'active'
4. Token hasn't expired (for Google)

### Issue: "Cross-org access"

**This should never happen if:**
1. RLS policies are enabled
2. All queries filter by `org_id`
3. JWT validation is working

**Verify:**
```sql
-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'organization_credentials';
```

---

## Performance Tips

### Use Connection Pooling

```python
import psycopg2.pool

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)
```

### Cache Credentials (Redis)

```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379)

def get_cached_credentials(org_id, service):
    key = f"creds:{org_id}:{service}"
    cached = cache.get(key)
    
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    creds = credential_manager.get_credentials(org_id, service)
    
    # Cache for 5 minutes
    cache.setex(key, 300, json.dumps(creds))
    
    return creds
```

### Index Optimization

```sql
-- Already included in migration, but verify:
CREATE INDEX idx_creds_org_service 
ON organization_credentials(org_id, service_name) 
WHERE status = 'active';
```

---

## Security Checklist

- [x] Credentials encrypted at rest
- [x] RLS policies enabled on all tables
- [x] All queries filter by `org_id`
- [x] JWT tokens validated on every request
- [x] Audit logging for all credential access
- [x] HTTPS/TLS for all connections
- [ ] Rotate encryption keys periodically
- [ ] Monitor failed authentication attempts
- [ ] Set up alerts for suspicious activity
- [ ] Backup encryption keys securely

---

## References

- **Full Guide:** `MULTITENANT_GUIDE.md`
- **Architecture:** `ARCHITECTURE_DIAGRAM.md`
- **Summary:** `MULTITENANT_SUMMARY.md`
- **Database Schema:** `migrations/001_multitenant_credentials_schema.sql`
- **Code:** `multitenant_credential_manager.py`, `multitenant_mcp_adapter.py`
