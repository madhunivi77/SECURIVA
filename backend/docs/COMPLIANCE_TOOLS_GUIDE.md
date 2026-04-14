# Compliance Standards Integration Guide

## Overview

This integration provides AI agents with access to detailed compliance standards information for **GDPR**, **HIPAA**, and **PCI-DSS**. The AI can query, search, and generate reports about compliance requirements to help users with audit preparation.

## Architecture

The system consists of three main components:

1. **`compliance_data.py`** - Static knowledge base containing structured compliance standards data
2. **`compliance_tools.py`** - Python functions that can be called by the AI or directly by your application
3. **`compliance_mcp_server.py`** - MCP (Model Context Protocol) server that exposes tools to AI agents

## Available Tools

### 1. `get_compliance_overview`
Get a high-level overview of a compliance standard.

**Parameters:**
- `standard` (string): "gdpr", "hipaa", or "pci_dss"

**Returns:**
- Name, region, effective date, overview description, and official reference

**Example:**
```python
from my_app.server.compliance_tools import get_compliance_overview

result = get_compliance_overview("gdpr")
print(result["overview"])
# "EU regulation on data protection and privacy for individuals within the EU..."
```

### 2. `get_compliance_requirements`
Get detailed compliance requirements for a standard.

**Parameters:**
- `standard` (string): Compliance standard name
- `requirement_id` (optional): Specific requirement ID to retrieve

**Returns:**
- Detailed requirements with descriptions, articles/sections, and implementation guidance

**Example:**
```python
from my_app.server.compliance_tools import get_compliance_requirements

# Get all GDPR principles
result = get_compliance_requirements("gdpr")
print(f"Found {result['total_count']} principles")

# Get specific PCI-DSS requirement
result = get_compliance_requirements("pci_dss", requirement_id=3)
print(result["requirements"][0]["name"])
# "Protect Stored Account Data"
```

### 3. `get_compliance_checklist`
Get a compliance checklist for audit preparation.

**Parameters:**
- `standard` (string): Compliance standard name

**Returns:**
- Checklist items grouped by category

**Example:**
```python
from my_app.server.compliance_tools import get_compliance_checklist

result = get_compliance_checklist("hipaa")
print(f"Total checklist items: {result['total_items']}")

# Items grouped by category
for category, items in result["categories"].items():
    print(f"\n{category}:")
    for item in items:
        print(f"  - {item['requirement']}")
```

### 4. `get_penalty_information`
Get penalty/fine information for non-compliance.

**Parameters:**
- `standard` (string): Compliance standard name

**Returns:**
- Penalty tiers with amounts and violation types

**Example:**
```python
from my_app.server.compliance_tools import get_penalty_information

result = get_penalty_information("gdpr")
tier_2 = result["penalties"]["tier_2"]
print(f"Maximum penalty: {tier_2['amount']}")
# "Up to €20 million or 4% of annual global turnover"
```

### 5. `get_breach_notification_requirements`
Get breach notification requirements and timelines.

**Parameters:**
- `standard` (string): Compliance standard name

**Returns:**
- Notification timelines and requirements

**Example:**
```python
from my_app.server.compliance_tools import get_breach_notification_requirements

result = get_breach_notification_requirements("hipaa")
breach_rule = result["breach_notification"]
```

### 6. `cross_reference_compliance_topic`
Cross-reference a topic across all three standards.

**Parameters:**
- `topic` (string): "data_encryption", "access_control", "audit_logging", "breach_notification", or "data_retention"

**Returns:**
- How each standard (GDPR, HIPAA, PCI-DSS) addresses the topic

**Example:**
```python
from my_app.server.compliance_tools import cross_reference_compliance_topic

result = cross_reference_compliance_topic("data_encryption")

print("GDPR requirements:")
for req in result["cross_references"]["gdpr"]:
    print(f"  - {req}")

print("\nHIPAA requirements:")
for req in result["cross_references"]["hipaa"]:
    print(f"  - {req}")

print("\nPCI-DSS requirements:")
for req in result["cross_references"]["pci_dss"]:
    print(f"  - {req}")
```

### 7. `search_compliance_requirements`
Search for requirements matching a query.

**Parameters:**
- `query` (string): Search query
- `standards` (optional): List of standards to search (default: all)

**Returns:**
- Matching requirements from specified standards

**Example:**
```python
from my_app.server.compliance_tools import search_compliance_requirements

# Search for encryption-related requirements
result = search_compliance_requirements("encryption")
print(f"Found {result['total_matches']} matches")

for match in result["matches"]:
    print(f"{match['standard']}: {match['item']['name']}")
```

### 8. `generate_compliance_report`
Generate a comprehensive compliance report.

**Parameters:**
- `standards` (list): List of standards to include
- `include_checklist` (boolean): Include checklists (default: True)
- `include_penalties` (boolean): Include penalty info (default: True)
- `include_breach_info` (boolean): Include breach notification info (default: True)

**Returns:**
- Comprehensive report with all requested information

**Example:**
```python
from my_app.server.compliance_tools import generate_compliance_report

# Generate report for all standards
result = generate_compliance_report(
    standards=["gdpr", "hipaa", "pci_dss"],
    include_checklist=True,
    include_penalties=True,
    include_breach_info=True
)

report = result["report"]
print(f"Generated at: {report['generated_at']}")
print(f"Total requirements: {report['summary']['total_requirements']}")
print(f"Total checklist items: {report['summary']['total_checklist_items']}")
```

## Integration with AI Agent

### Method 1: Direct Function Calls (Existing Chatbot)

Add compliance tools to your existing chat handler:

```python
# In chat_handler.py or app.py

from my_app.server.compliance_tools import *

# Define available tools for the AI
COMPLIANCE_TOOLS = {
    "get_compliance_overview": get_compliance_overview,
    "get_compliance_requirements": get_compliance_requirements,
    "get_compliance_checklist": get_compliance_checklist,
    "get_penalty_information": get_penalty_information,
    "get_breach_notification_requirements": get_breach_notification_requirements,
    "cross_reference_compliance_topic": cross_reference_compliance_topic,
    "search_compliance_requirements": search_compliance_requirements,
    "generate_compliance_report": generate_compliance_report
}

# In your chat completion call
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_compliance_overview",
            "description": "Get an overview of a compliance standard (GDPR, HIPAA, or PCI-DSS)",
            "parameters": {
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "enum": ["gdpr", "hipaa", "pci_dss"],
                        "description": "Compliance standard name"
                    }
                },
                "required": ["standard"]
            }
        }
    }
    # Add other tools...
]

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Execute the function
        if function_name in COMPLIANCE_TOOLS:
            result = COMPLIANCE_TOOLS[function_name](**arguments)
```

### Method 2: MCP Server (For MCP-Compatible AI Systems)

Run the MCP server:

```bash
python -m my_app.server.compliance_mcp_server
```

Configure your MCP client (add to `config.json`):

```json
{
  "mcpServers": {
    "compliance-standards": {
      "command": "python",
      "args": ["-m", "my_app.server.compliance_mcp_server"],
      "description": "Compliance standards information for GDPR, HIPAA, and PCI-DSS"
    }
  }
}
```

## Use Cases

### 1. Answering User Questions
**User:** "What are the GDPR breach notification requirements?"

**AI Tool Call:**
```python
get_breach_notification_requirements("gdpr")
```

**AI Response:** "Under GDPR, you must notify the relevant supervisory authority within 72 hours of becoming aware of a breach. If the breach poses a high risk to individuals' rights and freedoms, you must also notify affected individuals without undue delay."

### 2. Audit Preparation
**User:** "Give me a HIPAA audit checklist"

**AI Tool Call:**
```python
get_compliance_checklist("hipaa")
```

**AI Response:** Lists all checklist items grouped by category (Administrative, Physical, Technical, etc.)

### 3. Cross-Standard Comparison
**User:** "How do all three standards handle data encryption?"

**AI Tool Call:**
```python
cross_reference_compliance_topic("data_encryption")
```

**AI Response:** Provides encryption requirements from GDPR Article 32, HIPAA Security Rule, and PCI-DSS Requirements 3 & 4

### 4. Comprehensive Compliance Report
**User:** "Generate a full compliance report for my healthcare company"

**AI Tool Call:**
```python
generate_compliance_report(
    standards=["hipaa", "gdpr"],
    include_checklist=True,
    include_penalties=True,
    include_breach_info=True
)
```

**AI Response:** Returns a structured report with all requirements, checklists, and breach procedures

## Logging and Monitoring

All tool calls are automatically logged using the existing `tool_logger` system. Check logs at:

```
backend/logs/tool_calls.json
```

Each log entry includes:
- Tool name
- Input parameters
- Output summary
- Success/failure status
- Timestamp
- Reference IDs

## Extending the System

### Adding New Compliance Standards

1. Add data to `compliance_data.py`:
```python
SOC2_STANDARDS = {
    "name": "SOC 2",
    "region": "Global",
    # ... rest of data
}
```

2. Update tool functions in `compliance_tools.py` to include new standard

3. Update MCP server enum lists in `compliance_mcp_server.py`

### Adding New Compliance Topics

Add to `COMPLIANCE_CROSS_REFERENCE` in `compliance_data.py`:
```python
COMPLIANCE_CROSS_REFERENCE = {
    "your_new_topic": {
        "gdpr": ["..."],
        "hipaa": ["..."],
        "pci_dss": ["..."]
    }
}
```

## Testing

See `test_compliance_tools.py` for examples of how to test each tool function.

## Best Practices

1. **Cite Sources**: Always include article/section references when citing requirements
2. **Keep Data Updated**: Compliance standards evolve - update data files as standards change
3. **Log Everything**: Use the tool_logger to track all compliance queries for audit trails
4. **Validate Input**: The tools validate standard names and provide helpful error messages
5. **Cache Reports**: Consider caching generated reports if they're requested frequently

## Security Considerations

- Compliance data is read-only and stored in Python files
- No sensitive user data is processed by these tools
- All tool calls are logged for audit purposes
- Consider implementing rate limiting for public-facing deployments

## Support

For questions or issues:
1. Check the tool's error messages (they include available options)
2. Review logs at `backend/logs/tool_calls.json`
3. Test tools individually before integrating with AI agent
