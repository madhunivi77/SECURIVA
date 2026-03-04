"""
Example Integration: Adding Compliance Tools to Chat Handler
Shows how to integrate compliance tools into the existing chat system
"""

# Option 1: Direct Integration (Without MCP Server)
# ================================================
# Add compliance tools directly to the chat system as regular functions

import json
from typing import List, Dict, Any
from langchain.tools import Tool
from my_app.server.compliance_tools import (
    get_compliance_overview,
    get_compliance_requirements,
    get_compliance_checklist,
    get_penalty_information,
    get_breach_notification_requirements,
    cross_reference_compliance_topic,
    search_compliance_requirements,
    generate_compliance_report
)


def create_compliance_langchain_tools() -> List[Tool]:
    """
    Create LangChain Tool objects for compliance functions
    These can be added to your existing MCP tools
    """
    
    tools = [
        Tool(
            name="get_compliance_overview",
            description="Get an overview of a compliance standard (GDPR, HIPAA, or PCI-DSS). Use this when the user asks about what a compliance standard is, its scope, or general information. Input should be one of: 'gdpr', 'hipaa', or 'pci_dss'",
            func=lambda standard: json.dumps(get_compliance_overview(standard), indent=2)
        ),
        Tool(
            name="get_compliance_requirements",
            description="Get detailed compliance requirements for a standard. Use this when the user asks about specific requirements, principles, or rules of a standard. Input should be a JSON string with 'standard' (gdpr/hipaa/pci_dss) and optionally 'requirement_id'",
            func=lambda input_str: json.dumps(
                get_compliance_requirements(
                    **json.loads(input_str)
                ), indent=2
            )
        ),
        Tool(
            name="get_compliance_checklist",
            description="Get a compliance audit checklist for a standard. Use this when the user asks about audit preparation, checklist items, or what to verify for compliance. Input should be: 'gdpr', 'hipaa', or 'pci_dss'",
            func=lambda standard: json.dumps(get_compliance_checklist(standard), indent=2)
        ),
        Tool(
            name="get_penalty_information",
            description="Get penalty and fine information for non-compliance. Use this when the user asks about fines, penalties, or consequences of non-compliance. Input should be: 'gdpr', 'hipaa', or 'pci_dss'",
            func=lambda standard: json.dumps(get_penalty_information(standard), indent=2)
        ),
        Tool(
            name="get_breach_notification_requirements",
            description="Get breach notification requirements and timelines. Use this when the user asks about breach response, notification deadlines, or who to notify. Input should be: 'gdpr', 'hipaa', or 'pci_dss'",
            func=lambda standard: json.dumps(get_breach_notification_requirements(standard), indent=2)
        ),
        Tool(
            name="cross_reference_compliance_topic",
            description="Cross-reference a compliance topic across GDPR, HIPAA, and PCI-DSS. Use this when the user asks how different standards handle the same topic. Input should be: 'data_encryption', 'access_control', 'audit_logging', 'breach_notification', or 'data_retention'",
            func=lambda topic: json.dumps(cross_reference_compliance_topic(topic), indent=2)
        ),
        Tool(
            name="search_compliance_requirements",
            description="Search for compliance requirements matching a query. Use this when the user asks about a specific topic that might appear in multiple standards. Input should be a JSON string with 'query' and optionally 'standards' list",
            func=lambda input_str: json.dumps(
                search_compliance_requirements(
                    **json.loads(input_str)
                ), indent=2
            )
        ),
        Tool(
            name="generate_compliance_report",
            description="Generate a comprehensive compliance report. Use this when the user asks for a full report, complete overview, or consolidated compliance information. Input should be a JSON string with 'standards' list and optional boolean flags",
            func=lambda input_str: json.dumps(
                generate_compliance_report(
                    **json.loads(input_str)
                ), indent=2
            )
        )
    ]
    
    return tools


# Option 2: Modify chat_handler.py to include compliance tools
# =============================================================

"""
# In chat_handler.py, modify the execute_chat_with_tools function:

async def execute_chat_with_tools(messages: list, model: str = None, api: str = None, user_id: str = None) -> dict:
    # ... existing code ...
    
    # After loading MCP tools, add compliance tools
    try:
        mcp_tools_response = await load_mcp_tools(session)
        
        # Add compliance tools
        from my_app.server.compliance_integration import create_compliance_langchain_tools
        compliance_tools = create_compliance_langchain_tools()
        
        # Combine MCP tools with compliance tools
        all_tools = mcp_tools_response + compliance_tools
        
    except Exception as e:
        return {"error": f"MCP tool response failed: {e}"}
    
    # Initialize the langgraph agent with all tools
    graph = create_agent(
        model = llm_client, 
        tools = all_tools,  # Use combined tools instead of just mcp_tools_response
        middleware = [handle_tool_errors]
    )
    
    # ... rest of existing code ...
"""


# Option 3: System Prompt with Compliance Context
# ================================================

COMPLIANCE_SYSTEM_PROMPT = """
You are a compliance assistant with expertise in GDPR, HIPAA, and PCI-DSS standards.
You have access to tools that provide detailed, accurate information about compliance requirements.

When answering compliance questions:
1. Always use the compliance tools to fetch accurate, up-to-date information
2. Cite specific articles, sections, or requirements (e.g., "Article 32 of GDPR")
3. Provide practical implementation guidance when appropriate
4. Mention potential penalties when discussing non-compliance
5. Cross-reference standards when relevant (e.g., how GDPR and HIPAA both handle encryption)

Available compliance tools:
- get_compliance_overview: Get basic information about a standard
- get_compliance_requirements: Get detailed requirements and principles
- get_compliance_checklist: Get audit preparation checklists
- get_penalty_information: Get fine and penalty information
- get_breach_notification_requirements: Get breach response requirements
- cross_reference_compliance_topic: Compare how standards handle the same topic
- search_compliance_requirements: Search across standards
- generate_compliance_report: Create comprehensive reports

You should proactively suggest relevant compliance tools based on user questions.
"""


def add_system_prompt_to_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Add compliance system prompt to messages if not present
    
    Usage in chat_handler.py:
        messages = add_system_prompt_to_messages(messages)
    """
    # Check if first message is a system message
    if messages and messages[0].get("role") == "system":
        # Append to existing system message
        messages[0]["content"] += "\n\n" + COMPLIANCE_SYSTEM_PROMPT
    else:
        # Insert new system message at the beginning
        messages.insert(0, {
            "role": "system",
            "content": COMPLIANCE_SYSTEM_PROMPT
        })
    
    return messages


# Option 4: Example Usage in a Chat Route
# ========================================

"""
# In app.py or similar, add a compliance-specific endpoint:

from flask import Flask, request, jsonify
from my_app.server.chat_handler import execute_chat_with_tools
from my_app.server.compliance_integration import add_system_prompt_to_messages

@app.route("/api/chat/compliance", methods=["POST"])
async def compliance_chat():
    '''
    Dedicated endpoint for compliance-related queries
    Automatically includes compliance system prompt and tools
    '''
    data = request.json
    messages = data.get("messages", [])
    user_id = data.get("user_id")
    
    # Add compliance system prompt
    messages = add_system_prompt_to_messages(messages)
    
    # Execute chat with all tools (including compliance)
    result = await execute_chat_with_tools(
        messages=messages,
        user_id=user_id
    )
    
    return jsonify(result)


# Example request to the endpoint:
# POST /api/chat/compliance
# {
#   "messages": [
#     {"role": "user", "content": "What are the GDPR data retention requirements?"}
#   ],
#   "user_id": "user123"
# }

# The AI will:
# 1. Recognize this is a compliance question
# 2. Use get_compliance_requirements("gdpr") to fetch accurate data
# 3. Extract retention-related requirements
# 4. Cite Article 5(1)(e) - Storage Limitation
# 5. Provide practical guidance on implementing retention policies
"""


# Option 5: Standalone Compliance Report Generator
# =================================================

async def generate_user_compliance_report(
    user_id: str,
    standards: List[str],
    format: str = "json"
) -> Dict[str, Any]:
    """
    Generate a compliance report for a specific user
    Can be used independently or triggered by the AI
    
    Args:
        user_id: User identifier
        standards: List of standards to include (gdpr, hipaa, pci_dss)
        format: Output format (json, markdown, pdf)
    
    Returns:
        dict: Report data or file path
    """
    from datetime import datetime
    
    # Generate report
    result = generate_compliance_report(
        standards=standards,
        include_checklist=True,
        include_penalties=True,
        include_breach_info=True
    )
    
    if not result["success"]:
        return {"error": result.get("error")}
    
    report = result["report"]
    
    # Add user context
    report["user_id"] = user_id
    report["report_id"] = f"COMP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    if format == "json":
        return {"success": True, "report": report}
    
    elif format == "markdown":
        # Convert to markdown format
        md_content = f"# Compliance Report\n\n"
        md_content += f"**Generated:** {report['generated_at']}\n"
        md_content += f"**User ID:** {user_id}\n"
        md_content += f"**Report ID:** {report['report_id']}\n\n"
        
        md_content += f"## Summary\n\n"
        md_content += f"- Standards Covered: {report['summary']['total_standards']}\n"
        md_content += f"- Total Requirements: {report['summary']['total_requirements']}\n"
        md_content += f"- Checklist Items: {report['summary']['total_checklist_items']}\n\n"
        
        for std in report["standards"]:
            md_content += f"## {std['name']}\n\n"
            md_content += f"**Region:** {std['region']}\n\n"
            md_content += f"**Overview:** {std['overview']}\n\n"
            
            md_content += f"### Requirements ({std['requirement_count']})\n\n"
            for req in std["requirements"]:
                md_content += f"#### {req.get('name', req.get('id'))}\n"
                md_content += f"{req.get('description', '')}\n\n"
        
        # Save to file
        report_path = f"compliance_reports/{report['report_id']}.md"
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            f.write(md_content)
        
        return {"success": True, "report_path": report_path, "format": "markdown"}
    
    else:
        return {"error": f"Unsupported format: {format}"}


# Example API endpoint for report generation
"""
@app.route("/api/compliance/report", methods=["POST"])
async def create_compliance_report():
    data = request.json
    user_id = data.get("user_id")
    standards = data.get("standards", ["gdpr", "hipaa", "pci_dss"])
    format = data.get("format", "json")
    
    report = await generate_user_compliance_report(user_id, standards, format)
    
    if format in ["markdown", "pdf"] and report.get("report_path"):
        return send_file(report["report_path"])
    else:
        return jsonify(report)
"""


# Quick Start: Minimal Integration
# =================================

"""
To quickly add compliance tools to your existing system:

1. Add this to your chat_handler.py after loading MCP tools:

    from my_app.server.compliance_integration import create_compliance_langchain_tools
    compliance_tools = create_compliance_langchain_tools()
    all_tools = mcp_tools_response + compliance_tools

2. Use all_tools in your agent:

    graph = create_agent(
        model=llm_client,
        tools=all_tools,
        middleware=[handle_tool_errors]
    )

3. That's it! The AI can now answer compliance questions with accurate, cited information.

Test it with questions like:
- "What are the GDPR data breach notification requirements?"
- "Give me a HIPAA security checklist"
- "How do all three standards handle encryption?"
- "What are the penalties for PCI-DSS non-compliance?"
"""


if __name__ == "__main__":
    # Demo: Create tools and show their descriptions
    tools = create_compliance_langchain_tools()
    
    print("=== Compliance Tools Available ===\n")
    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}\n")
    
    print(f"Total tools: {len(tools)}")
    print("\nThese tools can now be used by the AI to answer compliance questions!")
