# Tool Confirmation System

## Overview

The Tool Confirmation System adds a safety layer to AI-powered tool execution by requiring user approval before executing sensitive operations. This prevents accidental or unintended actions from being performed automatically.

## Features

- **Risk-Based Confirmation**: Tools are categorized by risk level (low, medium, high)
- **Customizable Messages**: Each tool has a tailored confirmation message
- **Session Tracking**: Confirmations are tracked per user session
- **Timeout Handling**: Confirmations expire after 5 minutes (configurable)
- **Clear User Interface**: Simple yes/no prompts for user responses

## Architecture

The system consists of three main components:

1. **tool_confirmation_config.py**: Defines which tools require confirmation and their settings
2. **tool_confirmation_handler.py**: Manages the confirmation workflow and state
3. **chat_handler.py**: Integrated confirmation checks into the chat flow

## How It Works

### Normal Flow (No Confirmation Required)

```
User: "List my emails"
  ↓
AI: [executes listEmails tool]
  ↓
Returns: Email list results
```

### Confirmation Flow

```
User: "Create a Salesforce case for customer John with issue ABC"
  ↓
AI: [attempts to call createSalesforceCase]
  ↓
System: [intercepts and creates confirmation request]
  ↓
Returns: ⚠️ Confirmation Required
         Create a new Salesforce case:
         - Subject: Issue ABC
         - Description: Customer issue
         
         Reply with:
         - yes or approve to proceed
         - no or cancel to cancel
  ↓
User: "yes"
  ↓
System: [approves and executes tool]
  ↓
Returns: ✅ Case created successfully
```

## Tools Requiring Confirmation

### High Risk (Data Modification)
- `createSalesforceCase`
- `createSalesforceContact`
- `createSalesforceAccount`
- `createSalesforceOpportunity`
- `updateSalesforceOpportunity`
- `uploadSalesforceFile`
- `createComplianceModule`

### Medium Risk (Communications)
- `sendSMS`
- `sendVoiceCall`
- `sendSalesforceEmail`
- `addCalendarEvent`
- `generateComplianceReport`

### Low Risk
- `createGmailDraft`
- `createSalesforceTask`

## Usage Examples

### Example 1: Creating a Salesforce Contact

**User**: "Create a new contact for Jane Doe at jane@example.com"

**System Response**:
```
⚠️ Confirmation Required

Create new Salesforce contact:
- Name: Jane Doe
- Email: jane@example.com

Reply with:
- yes or approve to proceed
- no or cancel to cancel
- modify to change parameters
```

**User**: "yes"

**System**: ✅ Confirmation approved! Creating contact...

### Example 2: Sending SMS

**User**: "Send an SMS to +1234567890 saying 'Meeting at 3pm'"

**System Response**:
```
📱 Confirmation Required

Send SMS:
- To: +1234567890
- Message: Meeting at 3pm

Send this message?

Reply with:
- yes or approve to proceed
- no or cancel to cancel
```

**User**: "no, cancel that"

**System**: ❌ Action cancelled. How else can I help you?

## Configuration

### Adding a New Tool to Confirmation List

Edit `tool_confirmation_config.py`:

```python
TOOLS_REQUIRING_CONFIRMATION["myNewTool"] = ToolConfirmationRule(
    tool_name="myNewTool",
    confirmation_message_template="⚠️ **Confirmation Required**\\n\\nExecute myNewTool:\\n- **Param**: {param_name}\\n\\nProceed?",
    risk_level="medium"
)
```

### Removing a Tool from Confirmation

```python
from my_app.server.tool_confirmation_config import remove_confirmation_requirement

remove_confirmation_requirement("toolName")
```

### Temporarily Disabling All Confirmations

Useful for testing or automated workflows:

```python
from my_app.server.tool_confirmation_config import disable_all_confirmations

disable_all_confirmations()
# ... run your tests ...
enable_all_confirmations()
```

### Adjusting Confirmation Timeout

Edit `tool_confirmation_handler.py`:

```python
confirmation_handler = ToolConfirmationHandler(confirmation_timeout_seconds=600)  # 10 minutes
```

## User Response Keywords

The system recognizes the following user responses:

**Approval**:
- "yes"
- "approve"
- "confirm"
- "proceed"
- "ok"
- "go ahead"

**Denial**:
- "no"
- "cancel"
- "deny"
- "stop"
- "don't"

**Modification** (future feature):
- "modify"
- "change"
- "edit"

## Future Enhancements

### Planned Features

1. **Batch Confirmations**: Handle multiple tool confirmations in one request
2. **Parameter Modification**: Allow users to modify parameters before approval
3. **Confirmation History**: Track and display confirmation history
4. **Role-Based Confirmations**: Different confirmation rules for different user roles
5. **Persistent Storage**: Use Redis/DynamoDB instead of in-memory storage
6. **Actual Tool Execution**: Currently shows "pending execution" - needs integration with tool executor
7. **Audit Logging**: Log all confirmations and their outcomes for compliance

### Integration with Compliance Features

The confirmation system integrates well with existing compliance tools:

```python
# Compliance tools can have their own specialized confirmations
TOOLS_REQUIRING_CONFIRMATION["createComplianceModule"] = ToolConfirmationRule(
    tool_name="createComplianceModule",
    confirmation_message_template="...",
    risk_level="high"
)
```

## Testing

### Manual Testing

1. Start the backend server:
   ```bash
   cd backend
   python run.py
   ```

2. Make a chat request that triggers a confirmation tool:
   ```bash
   curl -X POST http://localhost:8000/chat \\
     -H "Content-Type: application/json" \\
     -d '{
       "messages": [{"role": "user", "content": "Create a Salesforce case"}]
     }'
   ```

3. You should receive a confirmation request

4. Send approval:
   ```bash
   curl -X POST http://localhost:8000/chat \\
     -H "Content-Type: application/json" \\
     -d '{
       "messages": [{"role": "user", "content": "yes"}]
     }'
   ```

### Unit Testing

See `backend/tests/test_tool_confirmation.py` (to be created) for unit tests.

## Known Limitations

1. **In-Memory Storage**: Confirmations are stored in memory and will be lost on server restart
2. **No Actual Execution**: Tool execution after confirmation is not implemented
3. **Single Tool per Confirmation**: Only handles one tool confirmation at a time
4. **No Websocket Support**: Works with REST API only, not real-time chat

## Security Considerations

- Confirmation IDs use UUIDs to prevent guessing
- Confirmations expire after timeout
- User sessions tracked separately
- No sensitive data logged in confirmation messages

## Troubleshooting

### "No pending confirmation" message when I said yes

- Your confirmation may have expired (default: 5 minutes)
- You may be in a different session
- The confirmation was already processed

### Tool still executes without confirmation

- Check if the tool is in `TOOLS_REQUIRING_CONFIRMATION` dictionary
- Verify confirmation checking is enabled in chat_handler
- Check server logs for errors

### Confirmation message shows {placeholders}

- The tool arguments don't match expected parameters
- Default formatting will show "N/A" for missing values
- Check tool signature matches confirmation template

## Contributing

When adding new tools that modify data or communicate externally, please:

1. Add them to `TOOLS_REQUIRING_CONFIRMATION`
2. Create an appropriate confirmation message template
3. Set the correct risk level
4. Update this documentation
5. Add tests

## Related Documentation

- [CONFIRMATION_PROMPTS_GUIDE.md](./CONFIRMATION_PROMPTS_GUIDE.md) - Compliance-specific confirmations
- [COMPLIANCE_TOOLS_GUIDE.md](./COMPLIANCE_TOOLS_GUIDE.md) - Compliance tool reference
- [REQUEST_VALIDATION_GUIDE.md](./server/docs/REQUEST_VALIDATION_GUIDE.md) - Request validation

---

**Version**: 1.0.0  
**Last Updated**: April 7, 2026  
**Author**: SECURIVA Development Team
