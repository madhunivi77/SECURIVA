# Testing Guide for Multi-Tenant Credential System

## Overview

This guide covers how to test the multi-tenant credential management system locally and ensure it works correctly before deploying to production.

---

## Prerequisites

### 1. Database Setup

```bash
# Install PostgreSQL (if not already installed)
# Windows (using Chocolatey):
choco install postgresql

# Or download from: https://www.postgresql.org/download/

# Start PostgreSQL service
# Windows:
net start postgresql-x64-14

# Create test database
createdb securiva_test

# Run migrations
psql securiva_test < backend/my_app/server/migrations/001_multitenant_credentials_schema.sql
```

### 2. Environment Variables

Create a `.env.test` file:

```env
# Database
DATABASE_URL=postgresql://localhost/securiva_test

# Encryption (generate a new key for testing)
ENCRYPTION_KEY=your-base64-encoded-32-byte-key-here

# JWT Secret
JWT_SECRET_KEY=test-jwt-secret-key-for-development-only

# Optional: Real service credentials for integration testing
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
SF_CLIENT_ID=your-salesforce-client-id
SF_CLIENT_SECRET=your-salesforce-client-secret
```

Generate encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt

# Additional test dependencies
pip install pytest pytest-cov
```

---

## Running Tests

### Method 1: Run Automated Tests

```bash
# Set environment variables
$env:DATABASE_URL="postgresql://localhost/securiva_test"
$env:ENCRYPTION_KEY="your-encryption-key-here"
$env:JWT_SECRET_KEY="test-jwt-secret"

# Run credential manager tests
cd backend/my_app/server
python test_multitenant_credentials.py

# Run MCP adapter tests
python test_mcp_adapter.py

# Run with pytest (if installed)
pytest test_multitenant_credentials.py -v
pytest test_mcp_adapter.py -v

# Run with coverage
pytest test_multitenant_credentials.py --cov=multitenant_credential_manager
```

### Method 2: Interactive Testing (Python REPL)

```bash
cd backend/my_app/server
python
```

```python
import os
import uuid
from datetime import datetime, timedelta

# Set environment
os.environ['DATABASE_URL'] = 'postgresql://localhost/securiva_test'
os.environ['ENCRYPTION_KEY'] = 'your-key-here'

# Import modules
from multitenant_credential_manager import get_credential_manager
from google.oauth2.credentials import Credentials

# Get credential manager
cm = get_credential_manager()

# Create test data
org_id = str(uuid.uuid4())
user_id = str(uuid.uuid4())

print(f"Test Org ID: {org_id}")
print(f"Test User ID: {user_id}")

# Test 1: Store Google credentials
creds = Credentials(
    token="test_token",
    refresh_token="test_refresh",
    token_uri="https://oauth2.googleapis.com/token",
    client_id="test_client",
    client_secret="test_secret",
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    expiry=datetime.now() + timedelta(hours=1)
)

cred_id = cm.store_google_oauth_credentials(
    org_id=org_id,
    user_id=user_id,
    credentials=creds,
    user_email="test@example.com"
)
print(f"✓ Stored Google credentials: {cred_id}")

# Test 2: Retrieve credentials
retrieved = cm.get_google_oauth_credentials(org_id, user_id)
print(f"✓ Retrieved token: {retrieved.token}")

# Test 3: Store Telesign credentials
ts_cred_id = cm.store_telesign_credentials(
    org_id=org_id,
    customer_id="TEST123",
    api_key="test_key_xyz",
    created_by=user_id
)
print(f"✓ Stored Telesign credentials: {ts_cred_id}")

# Test 4: Retrieve Telesign
ts_creds = cm.get_telesign_credentials(org_id)
print(f"✓ Retrieved Telesign customer_id: {ts_creds['customer_id']}")

# Test 5: List all credentials
all_creds = cm.list_organization_credentials(org_id)
print(f"✓ Total credentials: {len(all_creds)}")

# Test 6: Get status
status = cm.get_org_credential_status(org_id)
print(f"✓ Status: {status}")
```

---

## Test Scenarios

### Scenario 1: Basic Credential Storage

**Test:** Store and retrieve credentials for a single organization

```bash
python test_multitenant_credentials.py
```

**Expected Output:**
```
[TEST] Storing Google credentials for Org A, User 1...
✓ Credential stored with ID: <uuid>

[TEST] Retrieving Google credentials for User 1...
✓ Retrieved credentials: test_access_token_user1...
```

### Scenario 2: Multi-Org Isolation

**Test:** Verify organizations cannot access each other's credentials

```python
# Create two organizations
org_a = str(uuid.uuid4())
org_b = str(uuid.uuid4())
user_1 = str(uuid.uuid4())

# Store credentials for both orgs
cm.store_telesign_credentials(org_a, "CUST_A", "key_a", user_1)
cm.store_telesign_credentials(org_b, "CUST_B", "key_b", user_1)

# Verify isolation
creds_a = cm.get_telesign_credentials(org_a)
creds_b = cm.get_telesign_credentials(org_b)

assert creds_a['customer_id'] == "CUST_A"
assert creds_b['customer_id'] == "CUST_B"
assert creds_a['customer_id'] != creds_b['customer_id']
print("✓ Organization isolation verified")
```

### Scenario 3: User-Level Isolation (Google)

**Test:** Verify users in same org have separate Google credentials

```python
org_id = str(uuid.uuid4())
user_1 = str(uuid.uuid4())
user_2 = str(uuid.uuid4())

# Store for User 1
creds_1 = Credentials(token="token_user_1", ...)
cm.store_google_oauth_credentials(org_id, user_1, creds_1, "user1@test.com")

# Store for User 2
creds_2 = Credentials(token="token_user_2", ...)
cm.store_google_oauth_credentials(org_id, user_2, creds_2, "user2@test.com")

# Retrieve and verify
retrieved_1 = cm.get_google_oauth_credentials(org_id, user_1)
retrieved_2 = cm.get_google_oauth_credentials(org_id, user_2)

assert retrieved_1.token == "token_user_1"
assert retrieved_2.token == "token_user_2"
print("✓ User-level isolation verified")
```

### Scenario 4: MCP Adapter Integration

**Test:** MCP adapter correctly retrieves credentials based on JWT

```bash
python test_mcp_adapter.py
```

**Expected Output:**
```
[TEST 1] Extracting org_id and user_id from JWT...
  ✓ Extracted org_id: <uuid>
  ✓ Extracted user_id: <uuid>

[TEST 2] Retrieving Google credentials via adapter...
  ✓ Retrieved token: test_google_token_user1
  ✓ Retrieved refresh_token: test_google_refresh_user1
```

### Scenario 5: Token Refresh

**Test:** Expired tokens are automatically refreshed

```python
# Store credentials with expired token
expired_creds = Credentials(
    token="expired_token",
    refresh_token="valid_refresh_token",
    token_uri="https://oauth2.googleapis.com/token",
    client_id="test_client",
    client_secret="test_secret",
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    expiry=datetime.now() - timedelta(hours=1)  # Already expired
)

cm.store_google_oauth_credentials(org_id, user_id, expired_creds, "test@test.com")

# Attempt to refresh (requires real Google OAuth credentials)
refreshed = cm.refresh_google_oauth_token(org_id, user_id)

if refreshed:
    print(f"✓ Token refreshed: {refreshed.token}")
else:
    print("⚠ Refresh failed (expected without real OAuth credentials)")
```

---

## Manual Testing Checklist

### Database Tests

- [ ] Database connection works
- [ ] Tables are created correctly
- [ ] RLS policies are enabled
- [ ] Indexes exist

```sql
-- Verify tables
\dt

-- Verify RLS
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public';

-- Verify indexes
\di

-- Test query
SELECT * FROM organizations;
SELECT * FROM organization_credentials;
```

### Credential Manager Tests

- [ ] Store Google credentials (per-user)
- [ ] Store Salesforce credentials (per-org)
- [ ] Store Telesign credentials (per-org)
- [ ] Retrieve credentials correctly
- [ ] Organization isolation works
- [ ] User isolation works (Google)
- [ ] Credential validation works
- [ ] Credential deletion works
- [ ] List credentials works
- [ ] Audit logging works

### MCP Adapter Tests

- [ ] Extract org_id from JWT
- [ ] Extract user_id from JWT
- [ ] Get Google credentials via adapter
- [ ] Get Salesforce credentials via adapter
- [ ] Get Telesign clients via adapter
- [ ] Fallback to oauth.json works
- [ ] Returns None for invalid JWT

### Integration Tests

- [ ] Full OAuth flow (Google)
- [ ] Full OAuth flow (Salesforce)
- [ ] API key storage (Telesign)
- [ ] MCP tool calls work
- [ ] Token refresh works
- [ ] Error handling works

---

## Common Issues & Solutions

### Issue 1: "DATABASE_URL not set"

```bash
# Solution: Set environment variable
$env:DATABASE_URL="postgresql://localhost/securiva_test"
```

### Issue 2: "relation 'organization_credentials' does not exist"

```bash
# Solution: Run migration
psql securiva_test < backend/my_app/server/migrations/001_multitenant_credentials_schema.sql
```

### Issue 3: "Encryption key invalid"

```bash
# Solution: Generate new key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set it
$env:ENCRYPTION_KEY="<generated-key>"
```

### Issue 4: "Cannot connect to PostgreSQL"

```bash
# Windows: Start PostgreSQL service
net start postgresql-x64-14

# Verify it's running
psql --version
psql -U postgres -c "SELECT version();"
```

### Issue 5: "Module not found"

```bash
# Ensure you're in the right directory
cd backend/my_app/server

# Or add to Python path
$env:PYTHONPATH="$pwd;$env:PYTHONPATH"
```

---

## Performance Testing

### Load Test: Concurrent Credential Access

```python
import concurrent.futures
import time

def access_credentials(org_id, user_id):
    cm = get_credential_manager()
    creds = cm.get_google_oauth_credentials(org_id, user_id)
    return creds is not None

# Test concurrent access
org_id = "test-org"
user_id = "test-user"

start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(access_credentials, org_id, user_id) 
               for _ in range(100)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

elapsed = time.time() - start
print(f"100 requests in {elapsed:.2f}s ({100/elapsed:.2f} req/s)")
```

### Stress Test: Multiple Organizations

```python
import random

# Create 100 organizations
orgs = [str(uuid.uuid4()) for _ in range(100)]
users = [str(uuid.uuid4()) for _ in range(10)]

# Store credentials for each
for org_id in orgs:
    for user_id in users:
        cm.store_google_oauth_credentials(
            org_id, user_id,
            test_credentials, f"{user_id}@{org_id}.com"
        )

print(f"✓ Stored {len(orgs) * len(users)} credentials")

# Random retrieval test
start = time.time()
for _ in range(1000):
    org = random.choice(orgs)
    user = random.choice(users)
    creds = cm.get_google_oauth_credentials(org, user)

elapsed = time.time() - start
print(f"1000 retrievals in {elapsed:.2f}s")
```

---

## Cleanup After Testing

```bash
# Drop test database
dropdb securiva_test

# Or truncate tables
psql securiva_test -c "TRUNCATE organization_credentials CASCADE;"
psql securiva_test -c "TRUNCATE organizations CASCADE;"
```

---

## Next Steps

1. ✅ Run all automated tests
2. ✅ Verify organization isolation
3. ✅ Test MCP adapter integration
4. ✅ Performance test with realistic load
5. 🔄 Integration test with real OAuth flows
6. 🔄 Security audit
7. 🔄 Deploy to staging environment
8. 🔄 Monitor and optimize

---

## Test Coverage

Target coverage: **>90%**

```bash
# Generate coverage report
pytest test_multitenant_credentials.py --cov=multitenant_credential_manager --cov-report=html

# View report
# Open htmlcov/index.html in browser
```

**What to test:**
- ✅ All public methods
- ✅ Error cases
- ✅ Edge cases (expired tokens, missing data)
- ✅ Concurrent access
- ✅ Organization isolation
- ✅ User isolation
- ⚠️ Real OAuth token refresh (requires credentials)
- ⚠️ Real API calls (Telesign, Salesforce)
