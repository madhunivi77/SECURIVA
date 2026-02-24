# Multi-Tenant Implementation Summary

## What Was Created

### 1. **Enhanced Credential Manager** (`multitenant_credential_manager.py`)
   
**Features:**
- ✅ **Google OAuth Management** - Store/retrieve per-user Google credentials
- ✅ **Salesforce OAuth Management** - Store/retrieve per-org Salesforce credentials  
- ✅ **Telesign API Key Management** - Store/retrieve per-org Telesign credentials
- ✅ **Automatic Token Refresh** - Auto-refresh expired OAuth tokens
- ✅ **Credential Validation** - Test credentials before storing
- ✅ **Audit Logging** - Track all credential access and modifications
- ✅ **Encryption Support** - Secure credential storage with fallback mode

**Key Methods:**

```python
# Google OAuth (per user)
store_google_oauth_credentials(org_id, user_id, credentials, email, metadata)
get_google_oauth_credentials(org_id, user_id) -> Credentials
refresh_google_oauth_token(org_id, user_id) -> Credentials

# Salesforce OAuth (per org)
store_salesforce_credentials(org_id, user_id, access_token, refresh_token, instance_url, ...)
get_salesforce_credentials(org_id) -> Dict
refresh_salesforce_token(org_id) -> Dict

# Telesign API Keys (per org)
store_telesign_credentials(org_id, customer_id, api_key, created_by, metadata)
get_telesign_credentials(org_id) -> Dict
validate_telesign_credentials(org_id, test_phone) -> Dict
delete_telesign_credentials(org_id, deleted_by) -> bool

# Utility
list_organization_credentials(org_id) -> List[Dict]
get_org_credential_status(org_id) -> Dict[str, bool]
revoke_all_user_credentials(org_id, user_id, revoked_by) -> int
```

---

### 2. **MCP Adapter** (`multitenant_mcp_adapter.py`)

**Purpose:** Abstracts credential retrieval for MCP tools, supporting both:
- **Multi-tenant mode** (database)
- **Single-tenant mode** (oauth.json fallback)

**Features:**
- ✅ Automatic detection of multi-tenant vs legacy mode
- ✅ JWT token parsing for org_id/user_id extraction
- ✅ Service-specific credential retrieval
- ✅ Auto-refresh of expired tokens
- ✅ Graceful fallback to environment variables

**Usage in MCP Server:**

```python
from .multitenant_mcp_adapter import get_mcp_adapter

mcp_adapter = get_mcp_adapter()

def getGoogleCreds(ctx):
    return mcp_adapter.get_google_credentials(ctx)

def getSalesforceCreds(ctx):
    return mcp_adapter.get_salesforce_credentials(ctx)

def getTelesignClients(ctx):
    return mcp_adapter.get_telesign_clients(ctx)
```

---

### 3. **Database Schema** (`migrations/001_multitenant_credentials_schema.sql`)

**Tables Created:**

1. **`organizations`**
   - Organization metadata (name, slug, plan, settings)
   - Supports subdomain routing (e.g., `acme.securiva.com`)
   
2. **`users`**
   - User accounts within organizations
   - Roles: owner, admin, member, viewer
   
3. **`organization_credentials`**
   - **Encrypted storage** for all service credentials
   - Supports multiple services per org
   - Tracks usage statistics and validation status
   - Unique constraint ensures one credential per service per org/user
   
4. **`credential_audit_log`**
   - Complete audit trail of all credential operations
   - Tracks: create, access, update, delete, refresh, validate
   
5. **`usage_logs`**
   - API usage tracking for billing
   - Per-org, per-service resource consumption
   
6. **`api_keys`**
   - Organization API keys for accessing SECURIVA APIs
   - Scoped permissions and rate limiting

**Security Features:**
- ✅ Row-Level Security (RLS) policies
- ✅ Org isolation at database level
- ✅ Encrypted credential storage
- ✅ Audit logging for compliance

---

## How Services Are Isolated

### Organization-Specific Credentials

Each organization has **completely separate credentials** for each service:

```
Organization A (Acme Corp)
├── Google OAuth
│   ├── User 1 → user1@acme.com (Gmail/Calendar)
│   └── User 2 → user2@acme.com (Gmail/Calendar)
├── Salesforce → Acme's Salesforce instance
└── Telesign → Acme's Telesign account

Organization B (Beta Inc)
├── Google OAuth
│   └── User 3 → user3@beta.com (Gmail/Calendar)
├── Salesforce → Beta's Salesforce instance
└── Telesign → Beta's Telesign account
```

### Data Flow

```
User Request
    ↓
JWT Token (contains org_id + user_id)
    ↓
MCP Adapter extracts org_id
    ↓
Credential Manager queries database
    ↓
WHERE org_id = '...' AND user_id = '...'  ← ISOLATION ENFORCED
    ↓
Returns only that org's credentials
    ↓
Tool executes with org-specific credentials
```

### Why This Works

1. **JWT contains org_id** - Every request knows which organization
2. **Database filters by org_id** - Queries automatically scoped
3. **RLS policies enforce isolation** - PostgreSQL prevents cross-org access
4. **Encryption per-org** - Each org's credentials separately encrypted
5. **Audit trail per-org** - Complete visibility into credential usage

---

## Migration Path

### Phase 1: Preparation (Current)
- ✅ Create multi-tenant credential manager
- ✅ Create MCP adapter with fallback
- ✅ Design database schema
- ⚠️ **Still using oauth.json** (backward compatible)

### Phase 2: Database Setup
```bash
# 1. Set up PostgreSQL
createdb securiva

# 2. Run migration
psql securiva < backend/my_app/server/migrations/001_multitenant_credentials_schema.sql

# 3. Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/securiva"
export ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

### Phase 3: Migrate Existing Data
```bash
# Run migration script
python backend/my_app/server/migrate_oauth_json_to_db.py
```

### Phase 4: Update JWT Tokens
```python
# Update auth_server/main.py to include org_id
payload = {
    'sub': user_id,
    'org_id': org_id,  # NEW FIELD
    'role': role,
    'exp': expiry
}
```

### Phase 5: Switch to Multi-Tenant Mode
- Update `mcp_server.py` to use new adapter
- Deploy with `DATABASE_URL` set
- MCP adapter automatically switches to database mode

---

## Key Differences Between Services

### Google OAuth (Per-User)
- **Scope:** Each user has their own Google account
- **Storage:** One credential per user per org
- **Use Case:** Access user's personal Gmail/Calendar
- **Isolation:** User A cannot access User B's emails

```python
# User-specific retrieval
creds = credential_manager.get_google_oauth_credentials(
    org_id="org-123",
    user_id="user-456"  # MUST specify user
)
```

### Salesforce OAuth (Per-Organization)
- **Scope:** Organization-wide Salesforce connection
- **Storage:** One credential per org (shared by all users)
- **Use Case:** Access company's Salesforce CRM data
- **Isolation:** Org A cannot access Org B's Salesforce

```python
# Org-level retrieval (no user_id needed)
creds = credential_manager.get_salesforce_credentials(
    org_id="org-123"  # Shared by all users in org
)
```

### Telesign API Keys (Per-Organization)
- **Scope:** Organization-wide SMS/verification service
- **Storage:** One API key per org
- **Use Case:** Send SMS on behalf of company
- **Isolation:** Org A cannot use Org B's Telesign account

```python
# Org-level retrieval
creds = credential_manager.get_telesign_credentials(
    org_id="org-123"
)
```

---

## Example: Adding a New Service

To add support for Slack or another service:

```python
# 1. Add to credential manager
def store_slack_credentials(
    self,
    org_id: str,
    user_id: str,  # or None for org-level
    access_token: str,
    team_id: str,
    metadata: Optional[Dict] = None
) -> str:
    credential_data = {
        "access_token": access_token,
        "team_id": team_id,
        "metadata": metadata or {}
    }
    
    encrypted_data = self._encrypt_data(credential_data)
    
    # Store in database...
    # (similar to existing methods)

# 2. Add to MCP adapter
def get_slack_credentials(self, context) -> Optional[Dict]:
    org_id, user_id = self.extract_org_and_user(context)
    if not org_id:
        return None
    
    return self.credential_manager.get_slack_credentials(org_id, user_id)

# 3. Use in MCP tools
@mcp.tool()
def sendSlackMessage(context: Context, channel: str, message: str):
    creds = mcp_adapter.get_slack_credentials(context)
    if not creds:
        return "Slack not configured"
    
    # Use creds['access_token'] to call Slack API
```

---

## Security Considerations

### Credentials Are Encrypted
- All credentials stored as **encrypted bytes** in database
- Uses **Fernet symmetric encryption** (AES-128)
- Decryption only happens in-memory when needed

### Isolation Guarantees
1. **Database-level:** RLS policies prevent cross-org queries
2. **Application-level:** All queries filter by `org_id`
3. **Token-level:** JWT must contain valid `org_id`

### Audit Trail
Every credential operation logged:
```sql
SELECT * FROM credential_audit_log 
WHERE org_id = 'org-123' 
ORDER BY created_at DESC;
```

Shows: who accessed what credential, when, from where (IP), success/failure

---

## Testing

```python
# Test the credential manager
from multitenant_credential_manager import get_credential_manager

credential_manager = get_credential_manager()

# Store test credentials
cred_id = credential_manager.store_telesign_credentials(
    org_id="test-org-123",
    customer_id="test_customer",
    api_key="test_key_12345",
    created_by="admin-user-456"
)

# Retrieve
creds = credential_manager.get_telesign_credentials("test-org-123")
print(creds)  # {"customer_id": "test_customer", "api_key": "test_key_12345"}

# List all credentials
all_creds = credential_manager.list_organization_credentials("test-org-123")
print(all_creds)

# Check status
status = credential_manager.get_org_credential_status("test-org-123")
print(status)  # {"google": False, "salesforce": False, "telesign": True}
```

---

## Next Steps

1. **Set up database** - Run migration SQL
2. **Generate encryption key** - Set `ENCRYPTION_KEY` env var
3. **Update JWT generation** - Include `org_id` in tokens
4. **Migrate oauth.json** - Run migration script
5. **Update mcp_server.py** - Use new adapter
6. **Build admin UI** - Frontend for managing credentials
7. **Add webhook notifications** - Alert on credential expiry

---

## Questions?

- **"Do I need to change existing MCP tools?"** 
  - Minimal changes - just replace `getGoogleCreds()` implementation
  
- **"Can I still use oauth.json during migration?"**
  - Yes! The adapter has fallback mode for backward compatibility
  
- **"What happens if encryption key is lost?"**
  - All credentials become unrecoverable. **Backup your encryption key!**
  
- **"How do I handle token refresh?"**
  - Automatic! The credential manager refreshes expired tokens on retrieval

- **"Can one user belong to multiple organizations?"**
  - Yes! User can have different `user_id` in each org, or same `user_id` with org-specific credentials
