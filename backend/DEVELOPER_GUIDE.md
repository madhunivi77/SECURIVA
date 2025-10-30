# SECURIVA Developer Guide

## Adding New Tools to the System

This guide explains how to extend SECURIVA with new Google Workspace tools, Salesforce tools, or entirely new OAuth services.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Adding Google Workspace Tools](#adding-google-workspace-tools)
3. [Adding Salesforce Tools](#adding-salesforce-tools)
4. [Adding a New OAuth Service](#adding-a-new-oauth-service)
5. [Testing Your Tools](#testing-your-tools)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ AUTHENTICATION LAYER (Collect OAuth tokens)             │
├─────────────────────────────────────────────────────────┤
│ app.py              → Google OAuth (Gmail, Calendar)    │
│ salesforce_app.py   → Salesforce OAuth                  │
│ [future]_app.py     → Other services                    │
└─────────────────────────────────────────────────────────┘
                      ↓ stores tokens in
┌─────────────────────────────────────────────────────────┐
│ oauth.json - Centralized credential storage             │
└─────────────────────────────────────────────────────────┘
                      ↑ reads tokens from
┌─────────────────────────────────────────────────────────┐
│ TOOLS LAYER (Use tokens to perform actions)             │
├─────────────────────────────────────────────────────────┤
│ mcp_server.py - AI tools registry                       │
│  - getGoogleCreds() → Fetch Google tokens               │
│  - getSalesforceCreds() → Fetch Salesforce tokens       │
│  - @mcp.tool() listEmails() → Gmail tool                │
│  - @mcp.tool() listAccounts() → Salesforce tool         │
└─────────────────────────────────────────────────────────┘
```

**Key Principle**:
- OAuth apps (app.py, salesforce_app.py) = Get credentials
- MCP server (mcp_server.py) = Use credentials

---

## Adding Google Workspace Tools

### 1. Update OAuth Scopes (if needed)

**File**: `backend/my_app/server/app.py`

**Location**: Lines 28-34

```python
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    # ADD NEW SCOPES HERE:
    # "https://www.googleapis.com/auth/drive.readonly",  # For Google Drive
    # "https://www.googleapis.com/auth/documents.readonly",  # For Google Docs
]
```

**Important**: After adding scopes, users must re-authenticate to grant new permissions.

### 2. Add Tool Function

**File**: `backend/my_app/server/mcp_server.py`

**Location**: Add after existing Google tools (after line 163)

**Template**:
```python
@mcp.tool()
def yourToolName(context: Context, param1: str, param2: int = 10) -> str:
    """
    Brief description of what this tool does

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: 10)
    """
    # Get Google credentials
    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"

    try:
        # Build the Google API service
        service = build("service_name", "v1", credentials=creds)

        # Make API call
        result = service.users().yourMethod().execute()

        # Format and return result
        return f"Result: {result}"

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred: {error}"
```

### 3. Example: Adding Google Drive Tool

```python
@mcp.tool()
def listDriveFiles(context: Context, max_results: int = 10) -> str:
    """
    List files from Google Drive

    Args:
        max_results: Maximum number of files to return (default: 10, max: 100)
    """
    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"

    try:
        max_results = min(max(1, max_results), 100)

        # Build Drive API service
        service = build("drive", "v3", credentials=creds)

        # List files
        results = service.files().list(
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()

        files = results.get("files", [])

        if not files:
            return "No files found in Drive."

        # Format output
        res = f"Found {len(files)} files:\n\n"
        for i, file in enumerate(files, 1):
            res += f"{i}. {file['name']}\n"
            res += f"   Type: {file.get('mimeType', 'Unknown')}\n"
            res += f"   Modified: {file.get('modifiedTime', 'Unknown')}\n"
            res += f"   ID: {file['id']}\n\n"

        return res

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred: {error}"
```

### 4. Available Google APIs

Common Google Workspace APIs you can integrate:

| Service | API Name | Scope Required |
|---------|----------|----------------|
| Gmail | `gmail` | `https://www.googleapis.com/auth/gmail.readonly` |
| Calendar | `calendar` | `https://www.googleapis.com/auth/calendar.readonly` |
| Drive | `drive` | `https://www.googleapis.com/auth/drive.readonly` |
| Docs | `docs` | `https://www.googleapis.com/auth/documents.readonly` |
| Sheets | `sheets` | `https://www.googleapis.com/auth/spreadsheets.readonly` |
| Tasks | `tasks` | `https://www.googleapis.com/auth/tasks.readonly` |
| Contacts | `people` | `https://www.googleapis.com/auth/contacts.readonly` |

**Documentation**: https://developers.google.com/apis-explorer

---

## Adding Salesforce Tools

### 1. Update OAuth Scopes (if needed)

**File**: `backend/my_app/server/salesforce_app.py`

**Location**: Line 60

```python
params = {
    "response_type": "code",
    "client_id": SF_CLIENT_ID,
    "redirect_uri": SF_CALLBACK_URL,
    "scope": "api refresh_token offline_access",  # ADD MORE SCOPES HERE
    "state": user_id
}
```

**Common Salesforce Scopes**:
- `api` - Access REST API
- `refresh_token` - Get refresh token
- `full` - Full access to all data
- `web` - Access to Web service APIs
- `chatter_api` - Access to Chatter

### 2. Add Tool Function

**File**: `backend/my_app/server/mcp_server.py`

**Location**: Add after existing Salesforce tools (after line 206)

**Template**:
```python
@mcp.tool()
def yourSalesforceTool(context: Context, param1: str) -> str:
    """
    Brief description of what this Salesforce tool does

    Args:
        param1: Description of parameter
    """
    # Get Salesforce credentials
    creds = getSalesforceCreds(context)
    if not creds:
        return "User not authenticated with Salesforce."

    access_token = creds["access_token"]
    instance_url = creds["instance_url"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Make Salesforce API request
    r = requests.get(
        f"{instance_url}/services/data/v61.0/sobjects/YourObject",
        headers=headers
    )

    if r.status_code == 200:
        return json.dumps(r.json(), indent=2)
    return f"Error: {r.text}"
```

### 3. Example: Query Salesforce Opportunities

```python
@mcp.tool()
def listOpportunities(context: Context, max_results: int = 10) -> str:
    """
    List recent opportunities from Salesforce

    Args:
        max_results: Maximum number of opportunities to return (default: 10)
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return "User not authenticated with Salesforce."

    access_token = creds["access_token"]
    instance_url = creds["instance_url"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # SOQL query to get opportunities
    query = f"SELECT Id, Name, Amount, StageName, CloseDate FROM Opportunity ORDER BY CreatedDate DESC LIMIT {max_results}"

    r = requests.get(
        f"{instance_url}/services/data/v61.0/query",
        headers=headers,
        params={"q": query}
    )

    if r.status_code == 200:
        data = r.json()
        records = data.get("records", [])

        if not records:
            return "No opportunities found."

        res = f"Found {len(records)} opportunities:\n\n"
        for i, opp in enumerate(records, 1):
            res += f"{i}. {opp.get('Name', 'Unknown')}\n"
            res += f"   Amount: ${opp.get('Amount', 0):,.2f}\n"
            res += f"   Stage: {opp.get('StageName', 'Unknown')}\n"
            res += f"   Close Date: {opp.get('CloseDate', 'Unknown')}\n"
            res += f"   ID: {opp.get('Id')}\n\n"

        return res

    return f"Error: {r.text}"
```

### 4. Common Salesforce Objects

| Object | API Name | Description |
|--------|----------|-------------|
| Accounts | `Account` | Companies/organizations |
| Contacts | `Contact` | People |
| Opportunities | `Opportunity` | Sales deals |
| Leads | `Lead` | Potential customers |
| Cases | `Case` | Customer support cases |
| Tasks | `Task` | To-do items |
| Events | `Event` | Calendar events |

**SOQL Query Examples**:
```sql
-- Get all accounts
SELECT Id, Name, Industry FROM Account LIMIT 10

-- Get contacts with email
SELECT Id, Name, Email FROM Contact WHERE Email != null LIMIT 10

-- Get open opportunities
SELECT Id, Name, Amount FROM Opportunity WHERE IsClosed = false LIMIT 10
```

**Documentation**: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/

---

## Adding a New OAuth Service

If you want to add a completely new service (e.g., Microsoft, Slack, GitHub):

### Step 1: Create OAuth App File

**File**: `backend/my_app/server/[service]_app.py` (e.g., `microsoft_app.py`)

**Template**:
```python
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import RedirectResponse, JSONResponse
import requests
import os
import json
from pathlib import Path
from urllib.parse import urlencode
from datetime import datetime
from .api_key_manager import validate_api_key

# Environment variables
SERVICE_CLIENT_ID = os.getenv("SERVICE_CLIENT_ID")
SERVICE_CLIENT_SECRET = os.getenv("SERVICE_CLIENT_SECRET")
SERVICE_CALLBACK_URL = os.getenv("SERVICE_CALLBACK_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


async def service_login(request):
    """
    Initiate [Service] OAuth flow

    Gets user_id from API key cookie
    """
    # Get API key from cookie
    api_key = request.cookies.get("api_key")

    if not api_key:
        return JSONResponse(
            {"error": "Not authenticated. Please login with Google first."},
            status_code=401
        )

    # Validate API key
    oauth_file = Path(__file__).parent / "oauth.json"
    user_id = validate_api_key(api_key, oauth_file)

    if not user_id:
        return JSONResponse(
            {"error": "Invalid API key. Please login again."},
            status_code=401
        )

    # Build OAuth authorization URL
    base = "https://[service].com/oauth/authorize"
    params = {
        "client_id": SERVICE_CLIENT_ID,
        "redirect_uri": SERVICE_CALLBACK_URL,
        "scope": "your_scopes_here",
        "state": user_id  # Pass user_id to callback
    }
    return RedirectResponse(f"{base}?{urlencode(params)}")


async def service_callback(request):
    """Handle [Service] OAuth callback"""
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # user_id

    if not code or not state:
        return JSONResponse(
            {"error": "Authorization code or state not provided"},
            status_code=400
        )

    user_id = state

    # Exchange code for tokens
    token_url = "https://[service].com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": SERVICE_CLIENT_ID,
        "client_secret": SERVICE_CLIENT_SECRET,
        "redirect_uri": SERVICE_CALLBACK_URL,
    }

    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return JSONResponse(
            {"error": "Failed to get token", "details": r.text},
            status_code=r.status_code
        )

    creds = r.json()

    # Store tokens in oauth.json
    oauth_path = Path(__file__).parent / "oauth.json"
    if oauth_path.exists():
        with open(oauth_path, "r") as f:
            oauth_data = json.load(f)
    else:
        oauth_data = {"users": []}

    users = oauth_data.get("users", [])

    # Find user entry by user_id
    user_entry = None
    for user in users:
        if user.get("user_id") == user_id:
            user_entry = user
            break

    if not user_entry:
        return JSONResponse(
            {"error": "User not found. Please login with Google first."},
            status_code=400
        )

    # Update service credentials
    if "services" not in user_entry:
        user_entry["services"] = {}

    user_entry["services"]["[service_name]"] = {
        "credentials": creds,
        "connected_at": datetime.now().isoformat(),
        "scopes": ["your", "scopes", "here"]
    }

    oauth_data["users"] = users

    with open(oauth_path, "w") as f:
        json.dump(oauth_data, f, indent=2)

    # Redirect to frontend
    return RedirectResponse(
        url=f"{FRONTEND_URL}?[service]=connected",
        status_code=302
    )


# Create Starlette app for [Service] OAuth
service_app = Starlette(
    routes=[
        Route("/login", service_login),
        Route("/callback", service_callback),
    ]
)
```

### Step 2: Mount in Main App

**File**: `backend/my_app/server/app.py`

**Add import** (around line 12):
```python
from .[service]_app import service_app
```

**Mount the app** (around line 296):
```python
api_app.mount("/[service]", service_app)
```

### Step 3: Add Credential Helper in MCP Server

**File**: `backend/my_app/server/mcp_server.py`

**Add after `getSalesforceCreds()`** (around line 192):
```python
def getServiceCreds(ctx):
    """Retrieve [Service] credentials for the logged-in user"""
    try:
        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        encoded_token = ctx.request_context.request.headers.get('Authorization').split(" ")[1]
        payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('sub')

        with open(Path(__file__).parent / "oauth.json", "r") as f:
            data = json.load(f)
            for user in data.get("users", []):
                if user["user_id"] == user_id:
                    service = user.get("services", {}).get("[service_name]")
                    if service:
                        return service.get("credentials")
        return None

    except Exception as e:
        print(f"Error getting [Service] credentials: {e}")
        return None
```

### Step 4: Add Tools

**File**: `backend/my_app/server/mcp_server.py`

```python
@mcp.tool()
def yourServiceTool(context: Context) -> str:
    """Your service tool description"""
    creds = getServiceCreds(context)
    if not creds:
        return "User not authenticated with [Service]."

    access_token = creds["access_token"]
    # Make API calls using the token
    # ...
```

### Step 5: Add Environment Variables

**File**: `backend/.env`

```bash
# [Service] OAuth
SERVICE_CLIENT_ID=your_client_id
SERVICE_CLIENT_SECRET=your_client_secret
SERVICE_CALLBACK_URL=http://localhost:8000/[service]/callback
```

### Step 6: Update Frontend (Optional)

**File**: `frontend/src/App.jsx`

Add a "Connect [Service]" button similar to the Salesforce button.

---

## Testing Your Tools

### 1. Test OAuth Flow

```bash
# Start backend
cd backend
python -m my_app.server.main

# Visit in browser:
http://localhost:8000/login  # For Google
http://localhost:8000/salesforce/login  # For Salesforce
http://localhost:8000/[service]/login  # For new service
```

### 2. Test Tool via Chat

Start the frontend and ask the AI:

```
"List my emails"
"Show my calendar events"
"List Salesforce accounts"
```

The AI will automatically call your tools.

### 3. Debug Tips

**Check if credentials are stored**:
```bash
cat backend/my_app/server/oauth.json | jq
```

**Enable verbose logging** in `mcp_server.py`:
```python
@mcp.tool()
def yourTool(context: Context):
    creds = getGoogleCreds(context)
    print(f"DEBUG: Credentials = {creds}")  # Add debug prints
    # ...
```

**Check MCP server logs**:
Look at terminal output when running the backend.

---

## File Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `app.py` | Main app + Google OAuth | Add Google scopes, mount new services |
| `salesforce_app.py` | Salesforce OAuth | Update Salesforce scopes |
| `mcp_server.py` | All AI tools | Add new tools for any service |
| `api_key_manager.py` | API key utilities | Rarely (only for auth changes) |
| `chat_handler.py` | Chat logic | Rarely (only for MCP integration changes) |
| `oauth.json` | Credential storage | Never edit manually |

---

## Questions?

- **OAuth not working?** Check `.env` file has correct CLIENT_ID and CLIENT_SECRET
- **Tool not appearing?** Make sure you used `@mcp.tool()` decorator
- **Credentials not found?** Check `oauth.json` has the service under `services` key
- **API errors?** Verify scopes are correct and user has re-authenticated

---

**Last Updated**: 2025-01-29
**SECURIVA Version**: 1.0
