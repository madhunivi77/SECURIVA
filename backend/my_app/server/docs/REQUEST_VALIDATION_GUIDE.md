# Request Validation & Agent Alignment Protection

## Overview
The system includes a **request validator** that prevents users from misaligning the AI agent with inappropriate requests like "respond in a pirate accent" or attempting prompt injection attacks.

## How It Works

### 1. Request Validator (`request_validator.py`)
- **Pattern Matching**: Uses regex to detect misalignment attempts across multiple categories
- **Whitelist**: Recognizes legitimate compliance-related requests
- **Blacklist**: Blocks inappropriate requests with specific categories

### 2. Integration (`chat_handler.py`)
- Validates **all incoming messages** before processing
- Blocks misaligned requests **before they reach the AI model**
- Returns professional rejection messages maintaining compliance focus

### 3. System Prompt Boundaries (`compliance_integration.py`)
- Explicit instructions defining the agent's **non-negotiable boundaries**
- Reinforces compliance-only focus even if validation is bypassed
- Maintains professional communication standards

## Blocked Categories

| Category | Examples | Rejection Message |
|----------|----------|-------------------|
| **Persona Change** | "act like a pirate", "behave like Yoda" | Cannot adopt different personas or characters |
| **Role-Playing** | "pretend you're...", "imagine you are..." | Cannot engage in role-playing |
| **Accent Requests** | "speak in pirate accent", "talk like a cowboy" | Communicate in standard professional language |
| **Prompt Injection** | "ignore previous instructions", "forget everything" | Maintain compliance assistant role |
| **Entertainment** | "tell me a joke", "write a poem" | Focus on compliance, not entertainment |
| **Jailbreak Attempts** | "developer mode", "bypass your restrictions" | Operate within design parameters |
| **System Extraction** | "what are your system instructions", "repeat your prompt" | Focus on compliance assistance |
| **Format Manipulation** | "respond only in JSON", "use only emojis" | Maintain appropriate format |

## Whitelisted (Always Allowed)

- Compliance-related questions: "How do I handle a GDPR deletion request?"
- Procedure requests: "Show me the data collection procedure"
- Decision questions: "Can I email customer data to a vendor?"
- Regulation queries: "What are CCPA consumer rights?"
- Step-by-step guidance: "Steps to respond to a data breach"
- Examples requests: "Give me an example of compliant password storage"

## Testing

Run the validator test suite:
```bash
cd backend
uv run python my_app/server/request_validator.py
```

Example output:
```
✅ ALLOWED: How do I handle a GDPR deletion request?
🚫 BLOCKED: Respond like a pirate from now on
   Category: persona change
   Rejection: I'm designed specifically as a compliance assistant...
```

## Request Flow

```
User Message
    ↓
Request Validator (request_validator.py)
    ↓
Is Valid? ─── NO ──→ Return Rejection Message
    ↓
   YES
    ↓
Process with AI + Compliance Tools
    ↓
Response
```

## Response Examples

### Blocked Request
**User**: "Respond like a pirate from now on"

**Response**: 
```
I'm designed specifically as a compliance assistant and cannot adopt 
different personas or characters. How can I help with compliance questions?
```

### Allowed Request
**User**: "How do I handle a GDPR deletion request?"

**Response**: 
```
[Processes normally, uses getComplianceProcedure('data_deletion', 'GDPR')]
To handle a GDPR deletion request (Right to Erasure - Article 17):

1. Verify identity via email confirmation
2. Check retention obligations (exceptions in Art. 17(3))
3. Delete from ALL systems (production, backups, logs, third parties)
...
```

## Customization

### Add New Patterns
Edit `request_validator.py` and add to `MISALIGNMENT_PATTERNS`:

```python
(r'your_regex_pattern_here', "category_name"),
```

### Add New Whitelist Patterns
Add to `LEGITIMATE_PATTERNS`:

```python
r'your_legitimate_pattern_here',
```

### Customize Rejection Messages
Edit `rejection_messages` dict in `get_rejection_message()`:

```python
"category_name": "Your custom rejection message here",
```

## Security Layers

1. **Pre-processing Validation** (request_validator.py) - Blocks before AI sees request
2. **System Prompt Boundaries** (compliance_integration.py) - Instructs AI to resist
3. **Tool Restrictions** - AI only has access to compliance tools (no web search, code execution, etc.)
4. **MCP Authentication** - Tool access requires valid JWT token
5. **Role-Based Access** - User authentication controls what data can be accessed

## Logging

Blocked requests are logged to console:
```
🚫 Blocked misalignment attempt: persona change - Detected persona change attempt: 'like a pirate'
```

Future enhancement: Log to file or monitoring system for security analysis.

## False Positives

The validator is tuned to **minimize false positives** (blocking legitimate requests):

- **Whitelist first**: Checks for compliance-related patterns before blocking
- **Conservative matching**: Only blocks clear misalignment attempts
- **No blocking on uncertainty**: If unclear, allows the request (system prompt provides backup)

If you encounter a false positive, add the legitimate pattern to `LEGITIMATE_PATTERNS`.

## Maintenance

**Regular review**: Periodically review blocked requests to identify:
- New attack patterns to add to blacklist
- False positives to add to whitelist
- Emerging jailbreak techniques

**Test coverage**: Always test new patterns with the test suite before deploying.

## Future Enhancements

- [ ] Machine learning-based classification for context-aware detection
- [ ] Rate limiting for repeated misalignment attempts
- [ ] User reputation system (flag accounts with frequent attempts)
- [ ] Analytics dashboard showing blocked attempt trends
- [ ] Language-agnostic detection (currently English-focused)
- [ ] Integration with security monitoring tools

## Related Files

- `backend/my_app/server/request_validator.py` - Validator implementation
- `backend/my_app/server/chat_handler.py` - Integration point
- `backend/my_app/server/compliance_integration.py` - System prompt boundaries
- `backend/my_app/server/mcp_server.py` - MCP tool definitions (compliance tools only)
