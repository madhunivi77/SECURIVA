# Multi-Tenant Architecture Diagram

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SECURIVA PLATFORM                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Organization A (acme.securiva.com)                                 │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ Users: alice@acme.com, bob@acme.com                     │       │
│  │                                                           │       │
│  │ Credentials:                                             │       │
│  │  ├── Google OAuth (alice) → alice@gmail.com             │       │
│  │  ├── Google OAuth (bob)   → bob@gmail.com               │       │
│  │  ├── Salesforce           → Acme's SF org               │       │
│  │  └── Telesign            → Acme's SMS account           │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                       │
│  Organization B (beta.securiva.com)                                 │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ Users: charlie@beta.com                                  │       │
│  │                                                           │       │
│  │ Credentials:                                             │       │
│  │  ├── Google OAuth (charlie) → charlie@gmail.com         │       │
│  │  ├── Salesforce             → Beta's SF org             │       │
│  │  └── Telesign              → Beta's SMS account         │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Request Flow

```
┌───────────────┐
│   Frontend    │
│  (Browser)    │
└───────┬───────┘
        │ 1. Request with JWT
        │    {sub: user_id, org_id: org-123, role: admin}
        ↓
┌───────────────────────────────────────────────────────────┐
│                    Backend Server                         │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tenant Middleware                              │   │
│  │  - Extract org_id from JWT                      │   │
│  │  - Set request.state.org_id                     │   │
│  │  - Set PostgreSQL session: app.current_org_id   │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MCP Server                                     │   │
│  │  - Receives request with context                │   │
│  │  - Calls tool (e.g., listEmails)               │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MultiTenantMCPAdapter                          │   │
│  │  - Extract org_id + user_id from JWT            │   │
│  │  - Call credential manager                      │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MultiTenantCredentialManager                   │   │
│  │  - Query database with org_id filter            │   │
│  │  - Decrypt credentials                          │   │
│  │  - Return to adapter                            │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                                 │
└───────────────────────────────────────────────────────────┘
        │
        ↓
┌───────────────────────────────────────────────────────────┐
│              PostgreSQL Database                          │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  organization_credentials                       │   │
│  │  WHERE org_id = 'org-123'  ← RLS ENFORCED       │   │
│  │  AND user_id = 'user-456'                       │   │
│  │  AND service_name = 'google'                    │   │
│  │  AND status = 'active'                          │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                                 │
│  Returns: encrypted_data (bytes)                         │
│                         ↓                                 │
│  Decrypted: {token, refresh_token, expiry, ...}         │
│                                                           │
└───────────────────────────────────────────────────────────┘
        │
        ↓ 4. Use credentials
┌───────────────────┐
│  External APIs    │
│  - Gmail API      │
│  - Salesforce API │
│  - Telesign API   │
└───────────────────┘
```

---

## Credential Storage Schema

```
organization_credentials table
┌──────────────┬─────────┬─────────┬──────────┬───────────────────┬────────┐
│ credential_id│ org_id  │ user_id │ service  │ encrypted_data    │ status │
├──────────────┼─────────┼─────────┼──────────┼───────────────────┼────────┤
│ cred-001     │ org-A   │ user-1  │ google   │ [encrypted bytes] │ active │
│ cred-002     │ org-A   │ user-2  │ google   │ [encrypted bytes] │ active │
│ cred-003     │ org-A   │ NULL    │salesforce│ [encrypted bytes] │ active │
│ cred-004     │ org-A   │ NULL    │ telesign │ [encrypted bytes] │ active │
│ cred-005     │ org-B   │ user-3  │ google   │ [encrypted bytes] │ active │
│ cred-006     │ org-B   │ NULL    │salesforce│ [encrypted bytes] │ active │
└──────────────┴─────────┴─────────┴──────────┴───────────────────┴────────┘

Notes:
- Google: user_id is SET (per-user credentials)
- Salesforce: user_id is NULL (org-level credentials)
- Telesign: user_id is NULL (org-level credentials)
```

---

## Credential Retrieval Logic

### Per-User Credentials (Google)

```python
def get_google_credentials(org_id, user_id):
    """
    Query:
      WHERE org_id = 'org-A' 
        AND user_id = 'user-1'  ← USER SPECIFIC
        AND service_name = 'google'
    
    Returns: User 1's Google credentials ONLY
    """
```

```
Organization A
├── User 1 → Google (alice@gmail.com)     ← Returns THIS
├── User 2 → Google (bob@gmail.com)       ← NOT this
```

### Per-Organization Credentials (Salesforce/Telesign)

```python
def get_salesforce_credentials(org_id):
    """
    Query:
      WHERE org_id = 'org-A'
        AND user_id IS NULL  ← ORG LEVEL
        AND service_name = 'salesforce'
    
    Returns: Org A's Salesforce credentials (shared by all users)
    """
```

```
Organization A
├── User 1 ─┐
├── User 2 ─┼→ Salesforce (Acme's SF Org)  ← Shared credential
├── User 3 ─┘
```

---

## Isolation Guarantees

### 1. JWT-Level Isolation

```json
// Alice's JWT (Org A)
{
  "sub": "user-1",
  "org_id": "org-A",  ← Only has access to Org A
  "role": "admin"
}

// Charlie's JWT (Org B)
{
  "sub": "user-3",
  "org_id": "org-B",  ← Only has access to Org B
  "role": "member"
}
```

### 2. Database-Level Isolation (RLS)

```sql
-- PostgreSQL Row-Level Security Policy
CREATE POLICY org_isolation_credentials ON organization_credentials
    USING (org_id = current_setting('app.current_org_id')::uuid);

-- Before each query, set org context:
SET app.current_org_id = 'org-A';

-- Now ALL queries automatically filter:
SELECT * FROM organization_credentials;
-- Implicitly becomes:
-- SELECT * FROM organization_credentials WHERE org_id = 'org-A';
```

### 3. Application-Level Isolation

```python
# Every query explicitly filters by org_id
cursor.execute("""
    SELECT encrypted_data 
    FROM organization_credentials
    WHERE org_id = %s  ← ALWAYS FILTER BY ORG
      AND service_name = %s
""", (org_id, 'google'))
```

---

## Multi-Service Support

```
┌────────────────────────────────────────────────────────────┐
│  Organization Credentials                                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Google OAuth (Per User)                                  │
│  ┌──────────────────────────────────────────────┐        │
│  │ User 1 → Gmail, Calendar                      │        │
│  │ User 2 → Gmail, Calendar                      │        │
│  │ User N → Gmail, Calendar                      │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  Salesforce OAuth (Org-Wide)                              │
│  ┌──────────────────────────────────────────────┐        │
│  │ access_token, refresh_token                   │        │
│  │ instance_url: https://acme.salesforce.com     │        │
│  │ All users share this connection               │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  Telesign API (Org-Wide)                                  │
│  ┌──────────────────────────────────────────────┐        │
│  │ customer_id: CUST12345                        │        │
│  │ api_key: secret_key_xyz                       │        │
│  │ All users share this account                  │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  [Future: Slack, Zoom, Custom APIs...]                    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Encryption Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. STORAGE (Encrypt)                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Plaintext Credentials                                  │
│  {                                                      │
│    "customer_id": "CUST12345",                         │
│    "api_key": "secret_key_xyz",                        │
│    "metadata": {...}                                   │
│  }                                                      │
│         ↓                                               │
│  JSON.stringify()                                       │
│         ↓                                               │
│  Fernet.encrypt(json_str, ENCRYPTION_KEY)              │
│         ↓                                               │
│  Encrypted Bytes                                        │
│  b'\x80\x04\x95...[random bytes]...'                   │
│         ↓                                               │
│  Store in PostgreSQL as BYTEA                          │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. RETRIEVAL (Decrypt)                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Query Database                                         │
│  SELECT encrypted_data WHERE org_id=... AND service=... │
│         ↓                                               │
│  Encrypted Bytes                                        │
│  b'\x80\x04\x95...[random bytes]...'                   │
│         ↓                                               │
│  Fernet.decrypt(encrypted_bytes, ENCRYPTION_KEY)       │
│         ↓                                               │
│  JSON String                                            │
│  '{"customer_id": "CUST12345", ...}'                   │
│         ↓                                               │
│  JSON.parse()                                           │
│         ↓                                               │
│  Plaintext Credentials (in-memory only)                │
│  {customer_id: "CUST12345", api_key: "secret_key_xyz"} │
│         ↓                                               │
│  Use in API call (never persisted unencrypted)         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Comparison: Before vs After

### BEFORE (Single-Tenant)

```json
// oauth.json (one file for everyone)
{
  "users": [
    {
      "user_id": "user-1",
      "services": {
        "google": {...},
        "salesforce": {...}
      }
    }
  ]
}
```

**Problems:**
- ❌ Not scalable (file I/O bottleneck)
- ❌ No multi-tenancy (all users in one file)
- ❌ No encryption at rest
- ❌ No audit trail
- ❌ Race conditions with concurrent writes

### AFTER (Multi-Tenant)

```
PostgreSQL Database
├── organizations (100+ orgs)
├── users (1000+ users across orgs)
├── organization_credentials (encrypted, isolated)
├── credential_audit_log (full history)
└── usage_logs (billing data)
```

**Benefits:**
- ✅ Horizontally scalable
- ✅ Complete tenant isolation
- ✅ Encryption at rest + in transit
- ✅ Full audit trail for compliance
- ✅ ACID transactions (no race conditions)
- ✅ Automatic token refresh
- ✅ Usage tracking for billing

---

## Summary

**Key Principles:**

1. **Every credential belongs to an organization** (org_id)
2. **Some credentials are per-user** (Google) - isolated by user_id
3. **Some credentials are per-org** (Salesforce, Telesign) - shared by users
4. **All credentials are encrypted** before storage
5. **All access is logged** for audit compliance
6. **Isolation is enforced at 3 levels:** JWT, database, application code

**Result:** Each organization operates as if they have their own isolated instance of SECURIVA, while sharing the same infrastructure.
