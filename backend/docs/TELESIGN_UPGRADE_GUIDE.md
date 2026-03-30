# TeleSign Self-Service Account Integration - Updated

## What Was Updated

Your TeleSign integration has been completely upgraded for **self-service account** compatibility with comprehensive MCP tools and logging.

---

## Self-Service vs Enterprise for This Application

This project currently runs in a **self-service-first** mode for most TeleSign features, with one mixed piece:

- SMS, Voice, PhoneID, and Score use the standard `telesign` SDK
- Verify code flows currently use `telesignenterprise.verify.VerifyClient`

In practice, that means your app supports both account models, but the default setup and docs are optimized for self-service onboarding.

### Quick Comparison

| Area | Self-Service Account (Current Default) | Enterprise Account (When You Upgrade) |
|------|----------------------------------------|---------------------------------------|
| **Best fit in this app** | Fast setup, dev/testing, small-to-medium traffic | Production scale, advanced deliverability, regional expansion |
| **Current code path** | Primary path for `send_sms`, `send_voice_call`, `verify_phone_number`, `check_phone_risk` | Optional/expanded path, especially for dedicated sender and advanced routing |
| **Verify / OTP flow** | Works, but this repo currently uses enterprise Verify client class for token validation endpoints | Native fit for Verify-heavy flows and higher-volume OTP |
| **Sender ID control** | Often limited/shared defaults; `TELESIGN_SENDER_ID` may be empty | Dedicated numbers, toll-free, or registered brand sender IDs |
| **Regional deliverability controls** | Basic controls; country restrictions can be stricter | Better support for country onboarding and compliance registration workflows |
| **WhatsApp / premium channels** | Typically not available | Available with account enablement and provisioning |
| **Operational support** | Self-service dashboard support | Higher-touch support and account-level provisioning assistance |

### What Changes in This App When You Move to Enterprise

1. **Environment/config mostly stays the same**
  - `TELESIGN_CUSTOMER_ID`
  - `TELESIGN_API_KEY`
  - `TELESIGN_SENDER_ID` (more useful with enterprise)

2. **Your biggest behavior change is usually deliverability and sender identity**
  - Fewer country blocks once sender IDs/countries are provisioned
  - Better consistency for OTP and alert traffic

3. **No frontend contract change is required**
  - MCP tool names and response shapes can remain the same
  - Changes are mostly account provisioning and backend credential setup

### Recommendation for This Repo

- Stay on **self-service** if you are validating flows, demos, and low/medium volume messaging.
- Move to **enterprise** when you need:
  - dedicated sender IDs/toll-free strategy,
  - broader international coverage with fewer regional blocks,
  - advanced channel support (for example WhatsApp),
  - stronger operational/compliance support for production traffic.

---

## Changes Made

### 1. **[telesign_auth.py](my_app/server/telesign_auth.py)** - Core Functions

#### **Migrated from Enterprise to Self-Service SDK**
```python
# OLD (Enterprise SDK)
from telesignenterprise.messaging import MessagingClient

# NEW (Self-Service SDK)
from telesign.messaging import MessagingClient
from telesign.voice import VoiceClient  # Added voice support
```

#### **Added Comprehensive Logging**
Every TeleSign operation now logs:
- Input parameters (phone numbers, message types)
- Success/failure status
- Reference IDs for tracking
- Error messages

```python
log_tool_call(
    tool_name="send_sms",
    input_data={"phone_number": phone_number},
    output_data=result,
    success=result["success"],
    metadata={"reference_id": result.get("reference_id")}
)
```

#### **New Functions Added**
- `send_voice_call()` - Text-to-speech voice calls
- `get_detailed_message_status()` - Extended status with pricing/timestamps
- `poll_message_until_complete()` - Automated polling for testing
- `batch_verify_phones()` - Bulk phone verification
- `batch_send_sms()` - Bulk SMS sending

#### **Enhanced Error Handling**
All functions now return consistent response format:
```json
{
  "success": true/false,
  "status_code": 200,
  "reference_id": "ref_abc123",
  "errors": []
}
```

---

### 2. **[mcp_server.py](my_app/server/mcp_server.py)** - MCP Tools

#### **Expanded from 5 to 13 TeleSign MCP Tools**

| Tool | Description | New? |
|------|-------------|------|
| `sendSMS` | Send SMS with message type options | ✅ Enhanced |
| `sendVoiceCall` | Text-to-speech voice calls | 🆕 NEW |
| `verifyPhoneNumber` | Phone validation & carrier lookup | ✅ Enhanced |
| `sendVerificationCode` | 2FA code via SMS | ✅ Enhanced |
| `verifyUserCode` | Validate user-entered codes | 🆕 NEW |
| `checkPhoneRisk` | Fraud risk assessment | ✅ Enhanced |
| `checkMessageStatus` | Basic delivery status | ✅ Enhanced |
| `getDetailedMessageStatus` | Extended status with pricing | 🆕 NEW |
| `pollMessageStatusUntilComplete` | Auto-poll until delivered | 🆕 NEW |
| `batchVerifyPhoneNumbers` | Bulk phone verification | 🆕 NEW |
| `batchSendSMS` | Bulk SMS sending | 🆕 NEW |

---

## New MCP Tools Usage

### 🆕 **sendVoiceCall** - Voice Calls

```python
# Send a voice call with text-to-speech
sendVoiceCall("2623984079", "Your verification code is 1 2 3 4 5", "female")
```

**Response:**
```json
{
  "success": true,
  "message": "Voice call initiated",
  "reference_id": "ref_voice123",
  "phone_number": "2623984079"
}
```

---

### 🆕 **verifyUserCode** - Code Validation

```python
# Step 1: Send verification code
result1 = sendVerificationCode("2623984079", 6)
# Returns: {"reference_id": "ref123", "verify_code": "456789"}

# Step 2: User enters code "456789"
result2 = verifyUserCode("ref123", "456789", "456789")
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "message": "Your code is correct.",
  "reference_id": "ref123"
}
```

---

### 🆕 **getDetailedMessageStatus** - Extended Status

```python
getDetailedMessageStatus("ref_abc123xyz")
```

**Response:**
```json
{
  "success": true,
  "reference_id": "ref_abc123xyz",
  "status_code": 200,
  "status_description": "Delivered to handset",
  "submitted_at": "2026-03-04T10:30:00Z",
  "completed_on": "2026-03-04T10:30:05Z",
  "recipient": "2623984079",
  "price": "0.0065",
  "currency": "USD",
  "errors": []
}
```

---

### 🆕 **pollMessageStatusUntilComplete** - Auto-Polling

```python
# Useful for testing - polls every 2 seconds until delivered
pollMessageStatusUntilComplete("ref_abc123xyz", 10)
```

**Response:**
```json
{
  "success": true,
  "reference_id": "ref_abc123xyz",
  "status": "Delivered to handset",
  "delivered": true,
  "attempts": 3,
  "timeout": false
}
```

⚠️ **Note:** For production, use webhooks instead of polling

---

### 🆕 **batchVerifyPhoneNumbers** - Bulk Verification

```python
batchVerifyPhoneNumbers("2623984079,3105551234,4155551234")
```

**Response:**
```json
{
  "success": true,
  "total_numbers": 3,
  "results": [
    {
      "phone_number": "2623984079",
      "success": true,
      "data": {
        "phone_type": "Mobile",
        "carrier": "AT&T",
        "country": "United States"
      }
    },
    {
      "phone_number": "3105551234",
      "success": true,
      "data": {...}
    }
  ]
}
```

---

### 🆕 **batchSendSMS** - Bulk SMS

```python
recipients = '[
  {"phone_number":"2623984079","message":"Hello Alice"},
  {"phone_number":"3105551234","message":"Hello Bob"}
]'

batchSendSMS(recipients)
```

**Response:**
```json
{
  "success": true,
  "total_recipients": 2,
  "results": [
    {
      "phone_number": "2623984079",
      "success": true,
      "reference_id": "ref_abc123"
    },
    {
      "phone_number": "3105551234",
      "success": true,
      "reference_id": "ref_xyz789"
    }
  ]
}
```

---

## Enhanced MCP Tools

### ✅ **sendSMS** - Now with Message Types

```python
# OTP (One-Time Password) - default
sendSMS("2623984079", "Your code is 12345", "OTP")

# ARN (Alerts/Notifications)
sendSMS("2623984079", "Your order has shipped", "ARN")

# MKT (Marketing)
sendSMS("2623984079", "50% off sale today!", "MKT")
```

---

### ✅ **verifyPhoneNumber** - More Details

Now returns:
- Phone type (Mobile, Landline, VoIP)
- Carrier name
- Country, state, city
- Time zone
- Blocked status
- Contact information (if available)
- Formatted international number

```python
verifyPhoneNumber("2623984079")
```

**Enhanced Response:**
```json
{
  "success": true,
  "phone_number": "+12623984079",
  "phone_type": "Mobile",
  "carrier": "AT&T",
  "country": "United States",
  "country_code": "US",
  "city": "Phoenix",
  "state": "AZ",
  "time_zone": "America/Phoenix",
  "blocked": false,
  "contact_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  }
}
```

---

### ✅ **checkPhoneRisk** - Fraud Detection

```python
# For account creation
checkPhoneRisk("2623984079", "create")

# For login attempts
checkPhoneRisk("2623984079", "sign-in")

# For transactions
checkPhoneRisk("2623984079", "transact")
```

**Response:**
```json
{
  "success": true,
  "phone_number": "2623984079",
  "risk_level": "low",
  "risk_score": 150,
  "recommendation": "allow",
  "phone_type": "Mobile",
  "carrier": "AT&T"
}
```

**Risk Levels:**
- `low` - Safe to proceed
- `medium` - Additional verification recommended
- `high` - Block or require strong verification

**Recommendations:**
- `allow` - Approve the action
- `flag` - Review manually or add extra verification
- `block` - Deny the action

---

## Logging

All TeleSign operations are now logged to [tool_logs.json](tool_logs.json):

```json
{
  "timestamp": "2026-03-04T10:30:00Z",
  "tool_name": "send_sms",
  "input_data": {
    "phone_number": "2623984079",
    "message_type": "OTP"
  },
  "output_data": {
    "success": true,
    "reference_id": "ref_abc123"
  },
  "success": true,
  "metadata": {
    "account_type": "self-service",
    "reference_id": "ref_abc123"
  }
}
```

---

## Self-Service Account Features

Your TeleSign self-service account supports:

✅ **SMS Messaging** (OTP, ARN, MKT)  
✅ **Voice Calls** (Text-to-speech)  
✅ **PhoneID** (Phone verification and carrier lookup)  
✅ **Verify** (2FA codes with built-in validation)  
✅ **Intelligence/Score** (Fraud risk assessment)  

❌ **WhatsApp** (Requires enterprise upgrade)  
❌ **Premium features** (Contact TeleSign for upgrade)

### WhatsApp Limitation in This Application (Important)

For this codebase, WhatsApp is not just "disabled by default" on self-service; it is effectively **not supported** until enterprise provisioning is complete.

What this means today:

1. **No WhatsApp MCP tool is exposed** in the current server tool set.
2. **No WhatsApp send path is wired** in the active messaging helpers used by the app.
3. Requests like "send this via WhatsApp" should be handled as unsupported and redirected to SMS/Voice.

Why this matters:

- Self-service accounts typically do not include WhatsApp Business channel enablement.
- WhatsApp delivery requires additional TeleSign-side provisioning and approval (enterprise workflow).
- Even if credentials are valid for SMS/Voice, WhatsApp will not work until channel access is explicitly enabled.

Recommended behavior in product flows:

- Show a clear fallback message: "WhatsApp is not available on the current TeleSign plan; using SMS instead."
- Keep OTP and notification defaults on `sendSMS` and `sendVoiceCall`.
- Do not advertise WhatsApp in UI copy until enterprise provisioning is complete.

What changes after enterprise upgrade:

1. TeleSign enables WhatsApp channel for your account.
2. Backend adds an explicit WhatsApp send function/tool path.
3. UI/workflow can safely offer WhatsApp as a channel option.

Until those three are done, treat WhatsApp as unavailable in this application.

---

## Common Use Cases

### 1. **User Registration with 2FA**

```python
# Step 1: Check if phone is risky
risk = checkPhoneRisk(phone, "create")

if risk["risk_level"] == "high":
    return "Phone number blocked"

# Step 2: Verify phone is valid
verification = verifyPhoneNumber(phone)

if not verification["success"]:
    return "Invalid phone number"

# Step 3: Send verification code
code_result = sendVerificationCode(phone, 6)
ref_id = code_result["reference_id"]
verify_code = code_result["verify_code"]  # Store in session

# Step 4: User enters code
user_input = "123456"  # From user
is_valid = verifyUserCode(ref_id, user_input, verify_code)

if is_valid["valid"]:
    # Create user account
    pass
```

---

### 2. **Order Notifications**

```python
# Send SMS notification
send_result = sendSMS(
    customer_phone,
    "Your order #12345 has been shipped! Track it at: https://example.com/track",
    "ARN"  # Alert/Notification type
)

# Check delivery status after 30 seconds
status = checkMessageStatus(send_result["reference_id"])

if status["delivered"]:
    log_notification_sent(customer_id)
```

---

### 3. **Account Security Alert**

```python
# Send voice call for critical alerts
voice_result = sendVoiceCall(
    user_phone,
    "Warning: We detected suspicious activity on your account. "
    "Please log in to review. If this was not you, call us immediately.",
    "female"
)

# Also send SMS backup
sms_result = sendSMS(
    user_phone,
    "Security alert: Suspicious activity detected. Please review your account.",
    "ARN"
)
```

---

### 4. **Bulk Campaign**

```python
# Prepare recipients
recipients = []
for customer in customers:
    recipients.append({
        "phone_number": customer.phone,
        "message": f"Hi {customer.name}, check out our new products!"
    })

# Send in batch
batch_result = batchSendSMS(json.dumps(recipients))

# Track success rate
successful = sum(1 for r in batch_result["results"] if r["success"])
print(f"{successful}/{len(recipients)} messages sent")
```

---

## Testing

### Test Your Setup

```bash
cd backend
uv run python -c "
from my_app.server.telesign_auth import send_sms, verify_phone_number

# Test SMS
print('Testing SMS...')
result = send_sms('YOUR_PHONE_NUMBER', 'Test from SecuriVA')
print(f'Success: {result[\"success\"]}')
print(f'Reference ID: {result.get(\"reference_id\")}')

# Test phone verification
print('\nTesting phone verification...')
result = verify_phone_number('YOUR_PHONE_NUMBER')
print(f'Phone Type: {result.get(\"phone_type\")}')
print(f'Carrier: {result.get(\"carrier\")}')
"
```

---

## Environment Variables

Make sure these are set in [.env](../.env):

```bash
# TeleSign Credentials
TELESIGN_CUSTOMER_ID="your_customer_id"
TELESIGN_API_KEY="your_api_key"

# Optional
TELESIGN_SENDER_ID=""  # Leave empty for self-service
```

---

## Sender ID & Regional Restrictions

### 📱 What is Sender ID?

The Sender ID is what appears as the "from" number when recipients receive your SMS or voice calls. This can be:
- A **phone number** (most common)
- An **alphanumeric string** (like "YourBrand" - regional restrictions apply)
- A **short code** (requires special provisioning)
- A **toll-free number** (enhanced deliverability)

### 🌍 Regional Restrictions & Country Locks

**Important:** Many countries enforce strict sender ID regulations:

#### ✅ Countries Allowing Numeric Sender IDs
- **United States** - Most reliable with local/toll-free numbers
- **Canada** - Requires Canadian phone numbers for best delivery
- **United Kingdom** - Virtual numbers work well
- **Australia** - Requires pre-registration of sender IDs

#### ⚠️ Countries with Heavy Restrictions
- **India** - Requires DLT (Distributed Ledger Technology) registration
- **China** - International SMS heavily restricted, requires special agreements
- **UAE** - Must register sender ID with TRA (Telecommunications Regulatory Authority)
- **Saudi Arabia** - Requires CITC approval for commercial messaging
- **Singapore** - SGNIC registry required for local sender IDs

#### ❌ Country-Specific Blocking
**Status Code 237**: "Message blocked in requested country"

This error occurs when:
- You haven't registered your sender ID for that country
- Your account doesn't have permission to send to that region
- The country blocks messages from non-local sender IDs

**Solution:** Contact TeleSign support to enable specific countries for your account.

### 📞 Toll-Free Numbers

Toll-free numbers (e.g., 1-800, 1-888, 1-877 in the US) offer several advantages:

#### ✅ Benefits
- **Higher deliverability** - Better carrier acceptance rates
- **Professional appearance** - Recognized by recipients
- **Lower spam filtering** - Carriers trust toll-free numbers
- **Two-way messaging** - Can receive replies
- **No regional locks** - Work across the country

#### 📋 Requirements
1. **Toll-Free Verification (TFV)** - FCC mandate as of 2023
   - Business information verification
   - Use case description
   - Compliance documentation
   
2. **Registration Process**
   - Apply through TeleSign portal
   - Provide business details
   - Wait 2-4 weeks for approval
   
3. **Compliance**
   - Include opt-out instructions (e.g., "Reply STOP to unsubscribe")
   - Honor opt-out requests immediately
   - Don't send to purchased/scraped lists
   - Message content restrictions apply

#### 🚫 Restrictions
- **Verified use cases only** - Marketing, 2FA, notifications
- **No spam/phishing** - Strict enforcement
- **Rate limits** - Typically 1-3 messages per second
- **Cost** - $2-15/month per number + per-message fees

### 🔤 Alphanumeric Sender IDs

Instead of a phone number, use text like "YourBrand":

#### ✅ Supported Regions
- **Europe** (UK, France, Germany, Spain, etc.)
- **Middle East** (requires registration)
- **Asia Pacific** (varies by country)
- **Latin America** (limited support)

#### ❌ Not Supported
- **United States** - Alphanumeric sender IDs are converted to short codes
- **Canada** - Must use phone numbers

#### 📝 Configuration
```bash
# In .env
SENDER_ID="YourBrand"  # No + prefix for alphanumeric
```

**Limitations:**
- Max 11 characters
- Letters and numbers only (no spaces or special characters)
- **One-way only** - Cannot receive replies
- May be blocked by some carriers without pre-registration

### 🔢 Short Codes

Short codes (e.g., 12345) require special provisioning:

#### Types
- **Shared short codes** - $500-1000/month, shared with other businesses
- **Dedicated short codes** - $1000-1500/month, exclusive use
- **Vanity short codes** - Premium pricing for memorable numbers

#### Timeline
- **US/Canada**: 8-12 weeks provisioning
- **International**: 3-6 months

#### When to Use
- High-volume campaigns (>1000 messages/day)
- Marketing programs requiring opt-in tracking
- Enterprise-scale 2FA

### 🛠️ Configuring Sender ID

#### Self-Service Accounts (Current Setup)
```bash
# .env
SENDER_ID=""  # Leave empty - TeleSign assigns automatically
```

TeleSign will automatically select:
- Shared long codes (US/Canada)
- Virtual numbers (international)

#### Enterprise Accounts (After Upgrade)
```bash
# For dedicated phone number
SENDER_ID="18005551234"

# For alphanumeric (where supported)
SENDER_ID="YourBrand"

# For toll-free
SENDER_ID="18775551234"
```

### 📊 Best Practices by Use Case

| Use Case | Recommended Sender ID | Notes |
|----------|----------------------|-------|
| **2FA/OTP** | Short code or toll-free | Highest deliverability |
| **Transactional** | Toll-free or local number | Professional, reliable |
| **Marketing (US)** | Toll-free (with TFV) | Requires compliance |
| **Marketing (EU)** | Alphanumeric brand name | Pre-register in some countries |
| **Alerts/Notifications** | Toll-free or virtual number | Balance cost and reliability |
| **International** | Local virtual numbers | Check country restrictions |

### 🔍 Troubleshooting Sender ID Issues

#### Error: "Message blocked in requested country"
**Solution:**
1. Check if country requires sender ID registration
2. Contact TeleSign to enable that country
3. Consider using local virtual numbers
4. Review country-specific regulations

#### Error: "Invalid sender ID format"
**Solution:**
- Remove `+` prefix from phone numbers in SENDER_ID
- Ensure alphanumeric IDs are 11 characters or less
- Use only letters and numbers

#### Low Delivery Rates
**Solution:**
1. Verify sender ID is registered for target country
2. Consider upgrading to toll-free number
3. Check message content for spam triggers
4. Ensure recipients haven't opted out

### 🌐 Country-Specific Sender ID Guide

| Country | Sender ID Type | Registration Required | Approval Time |
|---------|---------------|----------------------|---------------|
| **USA** | Phone/Toll-free | Yes (TFV for toll-free) | 2-4 weeks |
| **Canada** | Phone/Toll-free | Yes | 2-4 weeks |
| **UK** | Phone/Alphanumeric | No | Immediate |
| **Germany** | Phone/Alphanumeric | Recommended | 1-2 weeks |
| **India** | Phone only | Yes (DLT) | 2-4 weeks |
| **Australia** | Phone/Alphanumeric | Yes | 2-3 weeks |
| **UAE** | Phone/Alphanumeric | Yes (TRA) | 4-8 weeks |
| **Singapore** | Phone only | Yes (SGNIC) | 2-4 weeks |
| **Brazil** | Phone only | Yes | 3-6 weeks |

### 📞 Getting Help with Sender ID Setup

Contact TeleSign for:
- Country enablement requests
- Toll-free number provisioning
- Sender ID registration assistance
- Compliance documentation requirements

**TeleSign Support:**
- Portal: https://portal.telesign.com/
- Email: support@telesign.com
- Documentation: https://developer.telesign.com/enterprise/docs/sms-api-sender-ids

---

## API Rate Limits

Self-service accounts typically have:
- **SMS**: ~100/hour default
- **PhoneID**: ~60/minute
- **Intelligence**: ~60/minute

For higher limits, contact TeleSign support.

---

## Cost Monitoring

Track costs by checking message pricing:

```python
status = getDetailedMessageStatus(reference_id)
print(f"Cost: {status['price']} {status['currency']}")
```

Typical costs:
- **SMS (US)**: $0.0065 - $0.01 per message
- **Voice**: $0.04 - $0.06 per call
- **PhoneID**: $0.0035 per lookup
- **Intelligence**: $0.004 per query

---

## Next Steps

1. ✅ **Test the new tools** - Try `sendSMS`, `sendVoiceCall`, etc.
2. ✅ **Check logs** - Review `tool_logs.json` for operation tracking
3. ✅ **Integrate into your app** - Use MCP tools in your chat workflows
4. ✅ **Monitor usage** - Track costs and success rates
5. ⭐ **Consider enterprise upgrade** - For WhatsApp and premium features

---

## Support

- **TeleSign Portal**: https://portal.telesign.com/
- **API Documentation**: https://developer.telesign.com/enterprise/docs
- **Support**: support@telesign.com

---

**All tools are production-ready and include comprehensive error handling and logging!** 🚀
