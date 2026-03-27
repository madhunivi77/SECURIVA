# Secure Business Transactions & Private Data Management

## Architecture Overview

SECURIVA uses a **dual-storage architecture** for maximum security and compliance:

```
┌─────────────────────────────────────────────────────────┐
│                   SECURIVA Application                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐        ┌──────────────────┐     │
│  │   Salesforce     │        │    DynamoDB      │     │
│  │   (CRM Data)     │        │  (Encrypted      │     │
│  │                  │        │   Credentials)   │     │
│  └──────────────────┘        └──────────────────┘     │
│         │                             │                │
│         ├─ Contacts                   ├─ API Keys     │
│         ├─ Accounts                   ├─ OAuth Tokens │
│         ├─ Opportunities               ├─ Encrypted    │
│         ├─ Cases                       │   Customer    │
│         └─ Business Data               │   Data        │
│                                        └─ Audit Logs   │
└─────────────────────────────────────────────────────────┘
```

---

## When to Use Each System

### 🔐 DynamoDB (Encrypted Storage)

**Use for ANY sensitive credentials or private customer data:**

| Data Type | Example | Why DynamoDB |
|-----------|---------|--------------|
| **API Keys** | Telesign, OpenAI, AWS | Encrypted at rest, audit trail |
| **OAuth Tokens** | Google, Salesforce refresh tokens | Automatic rotation support |
| **Payment Info** | Credit cards, bank details | PCI-DSS compliance required |
| **PHI/PII** | SSN, medical records, personal IDs | HIPAA/GDPR encryption mandatory |
| **Customer Secrets** | User passwords, security questions | Never store plaintext |
| **Org Credentials** | Multi-tenant API credentials | Isolation per organization |

**Security Features:**
- ✅ AES-256-GCM encryption at rest
- ✅ Key derivation with PBKDF2
- ✅ Per-tenant data isolation
- ✅ TTL for credential expiration
- ✅ Audit logging for compliance
- ✅ Automatic key rotation support

---

### 🏢 Salesforce (Business Data)

**Use for CRM and business workflow data:**

| Data Type | Example | Why Salesforce |
|-----------|---------|---------------|
| **Customer Relationships** | Contacts, Accounts | Native CRM features |
| **Sales Pipeline** | Opportunities, Quotes | Business intelligence |
| **Support Operations** | Cases, Tickets | Workflow automation |
| **Business Reports** | Dashboards, Analytics | Pre-built reporting |
| **Team Collaboration** | Tasks, Events, Notes | Salesforce ecosystem |

**Benefits:**
- ✅ Industry-standard CRM
- ✅ Built-in workflows and approvals
- ✅ Powerful reporting and dashboards
- ✅ Mobile app and ecosystem
- ✅ API for integration

---

## Migration from `oauth.json` to DynamoDB

### Current State (Insecure)

Your current [oauth.json](backend/my_app/server/oauth.json) stores credentials in **plaintext**:

```json
{
  "users": [
    {
      "user_id": "abc123",
      "services": {
        "salesforce": {
          "credentials": {
            "access_token": "PLAINTEXT_TOKEN",  // ❌ Security risk!
            "refresh_token": "PLAINTEXT_TOKEN"   // ❌ Security risk!
          }
        }
      }
    }
  ]
}
```

**Problems:**
- ❌ Plaintext credentials on disk
- ❌ No encryption at rest
- ❌ No audit trail
- ❌ Doesn't scale for multiple organizations
- ❌ Fails PCI-DSS/HIPAA/GDPR compliance

---

### Target State (Secure)

**DynamoDB Tables:**

#### 1. `SecuriVA_OrgCredentials` Table
```
Primary Key: org_id (HASH)
Sort Key: service#type (RANGE)

Example Items:
┌──────────┬───────────────────┬──────────────────┬────────────┐
│ org_id   │ service#type      │ encrypted_data   │ created_at │
├──────────┼───────────────────┼──────────────────┼────────────┤
│ org_001  │ salesforce#oauth  │ [AES-GCM blob]   │ 2026-03-27 │
│ org_001  │ telesign#api_key  │ [AES-GCM blob]   │ 2026-03-27 │
│ org_002  │ salesforce#oauth  │ [AES-GCM blob]   │ 2026-03-27 │
└──────────┴───────────────────┴──────────────────┴────────────┘
```

#### 2. `SecuriVA_Users` Table
```
Primary Key: user_id (HASH)

Example Items:
┌──────────┬───────────────────┬─────────┬─────────────────┐
│ user_id  │ email             │ org_id  │ roles           │
├──────────┼───────────────────┼─────────┼─────────────────┤
│ usr_001  │ john@acme.com     │ org_001 │ [admin, user]   │
│ usr_002  │ jane@acme.com     │ org_001 │ [user]          │
│ usr_003  │ bob@techcorp.com  │ org_002 │ [admin, user]   │
└──────────┴───────────────────┴─────────┴─────────────────┘
```

#### 3. `SecuriVA_APIKeys` Table
```
Primary Key: api_key_hash (HASH)

Example Items:
┌──────────────────┬──────────┬────────────┬────────────┐
│ api_key_hash     │ user_id  │ created_at │ expires_at │
├──────────────────┼──────────┼────────────┼────────────┤
│ sha256(key1)     │ usr_001  │ 2026-03-27 │ 2026-04-27 │
│ sha256(key2)     │ usr_002  │ 2026-03-27 │ 2026-04-27 │
└──────────────────┴──────────┴────────────┴────────────┘
```

---

## Implementation Steps

### Step 1: Create DynamoDB Tables

```bash
cd backend
uv run python tests/create_dynamodb_table.py
```

This creates all three tables with proper indexes and schema.

---

### Step 2: Integrate Encryption Service

The [encryption_service.py](backend/my_app/server/encryption_service.py) is already built. Add to your `.env`:

```bash
# Add to backend/.env
MASTER_ENCRYPTION_KEY=your-256-bit-key-here
ENCRYPTION_SALT=securiva-salt-production-v1

# Use a secure random key generator:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### Step 3: Migrate Existing Credentials

Create a migration script:

```python
# backend/migrate_credentials_to_dynamodb.py

from tests.dynamodb_credential_manager import DynamoDBCredentialManager
import json
from pathlib import Path

def migrate_oauth_to_dynamodb():
    """Migrate oauth.json credentials to DynamoDB"""
    manager = DynamoDBCredentialManager()
    
    # Load existing oauth.json
    oauth_path = Path(__file__).parent / "my_app/server/oauth.json"
    with open(oauth_path, "r") as f:
        oauth_data = json.load(f)
    
    for user in oauth_data.get("users", []):
        user_id = user["user_id"]
        org_id = user.get("org_id", user_id)  # Default org_id to user_id
        
        # Migrate Salesforce credentials
        if "salesforce" in user.get("services", {}):
            sf_data = user["services"]["salesforce"]
            
            manager.store_credentials(
                org_id=org_id,
                service_name="salesforce",
                credential_type="oauth",
                credential_data={
                    "access_token": sf_data["credentials"]["access_token"],
                    "refresh_token": sf_data["credentials"]["refresh_token"],
                    "instance_url": sf_data["instance_url"],
                    "salesforce_user_id": sf_data.get("salesforce_user_id")
                },
                created_by=user_id,
                metadata={
                    "email": user.get("email"),
                    "connected_at": sf_data.get("connected_at")
                }
            )
            print(f"✅ Migrated Salesforce credentials for {user.get('email')}")
        
        # Migrate Google credentials (optional)
        if "google" in user.get("services", {}):
            google_data = user["services"]["google"]
            
            manager.store_credentials(
                org_id=org_id,
                service_name="google",
                credential_type="oauth",
                credential_data=google_data["credentials"],
                created_by=user_id,
                metadata={"email": google_data.get("email")}
            )
            print(f"✅ Migrated Google credentials for {user.get('email')}")
    
    print("\n✅ Migration complete!")
    print("⚠️  NEXT: Update your app to use DynamoDB instead of oauth.json")
    print("⚠️  THEN: Securely delete oauth.json")

if __name__ == "__main__":
    migrate_oauth_to_dynamodb()
```

Run migration:
```bash
cd backend
uv run python migrate_credentials_to_dynamodb.py
```

---

### Step 4: Update Your Application Code

Replace oauth.json lookups with DynamoDB calls:

**Before (Insecure):**
```python
# In salesforce_app.py or mcp_server.py
with open("oauth.json", "r") as f:
    oauth_data = json.load(f)
    # Find user credentials...
```

**After (Secure):**
```python
# In salesforce_app.py or mcp_server.py
from tests.dynamodb_credential_manager import DynamoDBCredentialManager

manager = DynamoDBCredentialManager()

# Get credentials
credentials = manager.get_credentials(
    org_id=org_id,
    service_name="salesforce",
    credential_type="oauth"
)

if credentials:
    access_token = credentials["access_token"]
    refresh_token = credentials["refresh_token"]
```

---

### Step 5: Update Salesforce OAuth Flow

Modify [salesforce_app.py](backend/my_app/server/salesforce_app.py) callback to store in DynamoDB:

```python
async def salesforce_callback(request):
    """Handle Salesforce OAuth callback"""
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # user_id
    
    # Exchange code for tokens (existing code)
    creds = exchange_code_for_tokens(code)
    
    # NEW: Store in DynamoDB instead of oauth.json
    from tests.dynamodb_credential_manager import DynamoDBCredentialManager
    manager = DynamoDBCredentialManager()
    
    # Determine org_id (for multi-tenant support)
    org_id = get_org_id_for_user(state)  # Implement this based on your org structure
    
    success = manager.store_credentials(
        org_id=org_id,
        service_name="salesforce",
        credential_type="oauth",
        credential_data={
            "access_token": creds["access_token"],
            "refresh_token": creds["refresh_token"],
            "instance_url": creds["instance_url"],
            "salesforce_user_id": creds["id"]
        },
        created_by=state,  # user_id
        metadata={
            "connected_at": datetime.now().isoformat(),
            "scopes": ["api", "refresh_token", "offline_access"]
        },
        expires_days=90  # Optional: auto-expire after 90 days
    )
    
    if success:
        return RedirectResponse(
            url=f"{FRONTEND_URL}?salesforce=connected",
            status_code=302
        )
```

---

### Step 6: Implement Multi-Tenant Architecture

Your DynamoDB setup supports **organization-level isolation**:

```python
# Example: Multiple users from same company share org credentials

# User 1 from ACME Corp
manager.store_credentials(
    org_id="org_acme_001",  # Same org
    service_name="salesforce",
    credential_type="oauth",
    credential_data={...},
    created_by="user_john"
)

# User 2 from ACME Corp
# Uses SAME org credentials
credentials = manager.get_credentials(
    org_id="org_acme_001",  # Same org
    service_name="salesforce",
    credential_type="oauth"
)
```

**Benefits:**
- One Salesforce connection per organization (not per user)
- Reduced API costs
- Centralized credential management
- Easy org-level revocation

---

## Security Best Practices

### 1. Environment Variables

**NEVER commit these to git:**

```bash
# backend/.env
MASTER_ENCRYPTION_KEY=your-secure-key-here
ENCRYPTION_SALT=your-salt-here
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
SF_CLIENT_SECRET=your-salesforce-secret
```

### 2. Key Rotation

Periodically rotate your master encryption key:

```python
from tests.dynamodb_credential_manager import DynamoDBCredentialManager

manager = DynamoDBCredentialManager()

# Update MASTER_ENCRYPTION_KEY in .env first
# Then re-encrypt all credentials:

credentials = manager.get_credentials(org_id, "salesforce", "oauth")
encrypted_data = manager.encryption.encrypt_credentials(credentials)

# Store back with new encryption
manager.store_credentials(org_id, "salesforce", "oauth", credentials, user_id)
```

### 3. Audit Logging

All credential access is automatically logged:

```python
# Check audit trail
logs = manager.get_audit_log(org_id, limit=50)

for log in logs:
    print(f"{log['timestamp']}: {log['action']} by {log['user_id']}")
```

---

## Compliance Mapping

### PCI-DSS (Payment Card Industry)

| Requirement | Implementation |
|-------------|----------------|
| 3.4 - Encrypt cardholder data | ✅ AES-256-GCM encryption |
| 3.5 - Protect keys | ✅ AWS KMS integration ready |
| 8.2 - Multi-factor auth | ✅ Telesign SMS/WhatsApp MFA |
| 10.2 - Audit trail | ✅ DynamoDB audit logs |

### HIPAA (Healthcare)

| Safeguard | Implementation |
|-----------|----------------|
| §164.312(a)(2)(iv) Encryption | ✅ AES-256-GCM |
| §164.308(a)(1) Access Control | ✅ Org-level isolation |
| §164.312(b) Audit Controls | ✅ Compliance audit logs |

### GDPR (Data Protection)

| Article | Implementation |
|---------|----------------|
| Art. 32 - Security | ✅ Encryption at rest |
| Art. 17 - Right to erasure | ✅ Delete user data API |
| Art. 30 - Records | ✅ Processing activity logs |

---

## Testing Your Implementation

### Test DynamoDB Credentials

```bash
cd backend
uv run python tests/test_dynamodb_connection.py
```

### Test Encryption

```python
from tests.dynamodb_credential_manager import DynamoDBCredentialManager

manager = DynamoDBCredentialManager()

# Store test credentials
manager.store_credentials(
    org_id="test_org",
    service_name="telesign",
    credential_type="api_key",
    credential_data={
        "customer_id": "ABCD1234",
        "api_key": "super_secret_key"
    },
    created_by="test_user"
)

# Retrieve and verify
creds = manager.get_credentials("test_org", "telesign", "api_key")
assert creds["customer_id"] == "ABCD1234"
print("✅ Encryption test passed!")
```

---

## Cost Comparison

### Current (oauth.json)
- **Cost:** $0/month
- **Security:** ❌ Plaintext
- **Scalability:** ❌ Single file
- **Compliance:** ❌ Fails audits

### DynamoDB
- **Cost:** ~$1-5/month (25 GB free tier)
- **Security:** ✅ Encrypted at rest
- **Scalability:** ✅ Millions of records
- **Compliance:** ✅ Passes audits

### Salesforce
- **Cost:** $25-300/user/month (Professional to Enterprise)
- **Features:** Full CRM, workflows, reporting
- **Integration:** REST API, SOAP, Bulk API
- **Ecosystem:** AppExchange, mobile apps

---

## FAQ

**Q: Do I need both DynamoDB AND Salesforce?**

A: Yes, for different purposes:
- **DynamoDB**: Encrypted credentials and sensitive config
- **Salesforce**: CRM data and business workflows

**Q: Can I store Salesforce tokens in Salesforce?**

A: No! Salesforce stores business data, not credentials for accessing Salesforce itself. That would be circular and insecure.

**Q: What if I don't have AWS?**

A: Alternatives:
1. **AWS KMS Encryption SDK** (recommended)
2. **HashiCorp Vault** (enterprise)
3. **Azure Key Vault** (if using Azure)
4. **Google Secret Manager** (if using GCP)

**Q: Is oauth.json ever acceptable?**

A: Only for local development with test accounts. NEVER in production.

---

## Next Steps

1. ✅ **Read this guide**
2. ⏭️ Create DynamoDB tables (`create_dynamodb_table.py`)
3. ⏭️ Set up encryption keys in `.env`
4. ⏭️ Run migration script
5. ⏭️ Update application code
6. ⏭️ Test thoroughly
7. ⏭️ Deploy to production
8. ⏭️ Delete `oauth.json` (securely)

---

## Support

- **DynamoDB**: [AWS Documentation](https://docs.aws.amazon.com/dynamodb/)
- **Salesforce**: [Developer Documentation](https://developer.salesforce.com/docs)
- **Compliance**: See [COMPLIANCE_TOOLS_GUIDE.md](COMPLIANCE_TOOLS_GUIDE.md)
- **Encryption**: See [encryption_service.py](../my_app/server/encryption_service.py)

---

**Remember:** Security is not optional. Encrypt everything, audit everything, test everything.
