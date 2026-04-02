# Testing Salesforce MCP Tools

Since Salesforce uses OAuth 2.0 authentication (not just API keys), you need to authenticate first before testing the MCP tools.

## Quick Start

### Step 1: Configure Environment

Make sure these are in `backend/.env`:
```bash
SF_CLIENT_ID=your_salesforce_connected_app_client_id
SF_CLIENT_SECRET=your_salesforce_connected_app_client_secret
SF_CALLBACK_URL=http://localhost:8000/salesforce/callback
SF_DOMAIN=login  # or "test" for sandbox
JWT_SECRET_KEY=your_jwt_secret
```

### Step 2: Authenticate with Salesforce

**Option A: Browser Authentication (Easiest)**
```bash
# Terminal 1: Start backend
cd backend
uv run python run.py

# Browser: Navigate to
http://localhost:8000/salesforce/login

# Login and authorize your Salesforce account
# This creates backend/my_app/server/oauth.json with your credentials
```

**Option B: Manual oauth.json Creation (For Testing)**

If you already have Salesforce OAuth credentials, create `backend/my_app/server/oauth.json`:
```json
{
  "users": [
    {
      "user_id": "test_user_123",
      "services": {
        "salesforce": {
          "instance_url": "https://yourorg.salesforce.com",
          "salesforce_user_id": "https://login.salesforce.com/id/00D.../005...",
          "org_id": "00D...",
          "credentials": {
            "access_token": "your_access_token",
            "refresh_token": "your_refresh_token",
            "issued_at": "1709583600000",
            "signature": "...",
            "instance_url": "https://yourorg.salesforce.com",
            "id": "https://login.salesforce.com/id/00D.../005...",
            "token_type": "Bearer"
          },
          "connected_at": "2026-03-04T12:00:00",
          "scopes": ["api", "refresh_token", "offline_access"]
        }
      }
    }
  ]
}
```

### Step 3: Run Tests

#### Test Method 1: API-Level Testing (Simple)
Tests the Salesforce API connection directly:
```bash
cd backend
uv run python tests/test_salesforce_mcp.py
```

**What it tests:**
- ✅ OAuth credentials exist
- ✅ Token auto-refresh works
- ✅ Basic Salesforce API calls
- ✅ Query execution

#### Test Method 2: Direct Function Calls (Medium)
Tests MCP tools by calling them directly with mock context:
```bash
cd backend
uv run python tests/test_salesforce_mcp_direct.py
```

**What it tests:**
- ✅ MCP tool functions
- ✅ Context/JWT handling
- ✅ getSalesforceCreds() function
- ✅ Tool-specific logic

#### Test Method 3: MCP Client Protocol (Most Realistic)
Tests through the actual MCP HTTP protocol:
```bash
# Terminal 1: Start backend
cd backend
uv run python run.py

# Terminal 2: Run test
cd backend
uv run python tests/test_salesforce_via_mcp_client.py
```

**What it tests:**
- ✅ Full MCP protocol flow
- ✅ HTTP authentication
- ✅ Real server responses
- ✅ End-to-end integration

---

## Testing Individual Tools

### Example: Test Creating a Case

Add to any test script:
```python
from my_app.server.mcp_server import createSalesforceCase

result = createSalesforceCase(
    mock_ctx,
    subject="Test Case from MCP",
    description="Testing Salesforce MCP integration",
    origin="Web",
    status="New"
)
print(result)
```

### Example: Test SOQL Query

```python
from my_app.server.mcp_server import salesforceSOQLQuery

result = salesforceSOQLQuery(
    mock_ctx,
    query="SELECT Id, Name, Email FROM Contact WHERE LastName = 'Smith' LIMIT 5"
)
print(result)
```

---

## Available Salesforce MCP Tools

### Cases
- `createSalesforceCase` - Create a new case
- `listSalesforceCases` - List recent cases

### Contacts & Accounts
- `createSalesforceContact` - Create a new contact
- `listSalesforceContacts` - List contacts
- `createSalesforceAccount` - Create a new account
- `listSalesforceAccounts` - List accounts

### Opportunities
- `createSalesforceOpportunity` - Create new opportunity
- `listSalesforceOpportunities` - List opportunities
- `updateSalesforceOpportunity` - Update opportunity

### Tasks & Events
- `createSalesforceTask` - Create task
- `listSalesforceTasks` - List tasks
- `createSalesforceEvent` - Create calendar event
- `listSalesforceEvents` - List events

### Queries & Search
- `salesforceSOQLQuery` - Execute SOQL query
- `salesforceSOSLSearch` - Execute SOSL search

### Chatter & Social
- `postSalesforceChatter` - Post to Chatter feed
- `getSalesforceChatterFeed` - Get Chatter feed

### Info & Metadata
- `getSalesforceUserInfo` - Get current user info
- `getSalesforceOrgLimits` - Get org API limits
- `sendSalesforceEmail` - Send email via Salesforce

---

## Troubleshooting

### ❌ "User not authenticated with Salesforce"

**Solution:** Complete OAuth authentication first:
```bash
# Start backend
uv run python run.py

# Visit in browser
http://localhost:8000/salesforce/login
```

### ❌ "Token expired" or 401 errors

**Solution:** Tokens auto-refresh, but if refresh fails:
1. Delete `backend/my_app/server/oauth.json`
2. Re-authenticate via `/salesforce/login`

### ❌ "Invalid_grant" error

**Cause:** Refresh token expired (happens if password changed or app access revoked)

**Solution:** Re-authenticate to get new tokens

### ❌ SOQL query fails

**Check:**
- Query syntax is valid Salesforce SOQL
- Field names exist on the object
- User has access to queried objects

---

## Production Testing

For production/staging environments:

1. Update `SF_DOMAIN` in `.env`:
   - `login` - Production
   - `test` - Sandbox

2. Use proper callback URL:
   - `SF_CALLBACK_URL=https://yourdomain.com/salesforce/callback`

3. Update `FRONTEND_URL` for proper redirects

4. Test with multiple users to ensure multi-tenant isolation

---

## Key Differences from Other APIs

| Feature | Telesign (API Key) | Salesforce (OAuth) |
|---------|-------------------|-------------------|
| **Auth Method** | Static API key | Dynamic OAuth tokens |
| **Setup** | Add to `.env` | Browser OAuth flow |
| **Token Refresh** | Not needed | Auto-refresh every 90 min |
| **Testing** | Direct calls work | Need oauth.json first |
| **User Context** | Optional | Required (from JWT) |

---

## Next Steps

1. ✅ Authenticate via browser
2. ✅ Run test scripts to verify
3. ✅ Test your most-used tools
4. 🚀 Integrate with frontend chat interface
5. 📊 Monitor API usage via `getSalesforceOrgLimits`
