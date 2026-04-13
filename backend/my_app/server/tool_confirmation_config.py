"""
Tool Confirmation Configuration

This module defines which tools require user confirmation before execution
and provides utilities for managing confirmation workflows.
"""

from typing import Set, Dict, Optional
from dataclasses import dataclass


@dataclass
class ToolConfirmationRule:
    """Configuration for a tool that requires confirmation."""
    tool_name: str
    confirmation_message_template: str
    risk_level: str  # "low", "medium", "high"
    requires_user_confirmation: bool = True


# Tools that require confirmation before execution
# Organized by risk level and category
TOOLS_REQUIRING_CONFIRMATION: Dict[str, ToolConfirmationRule] = {
    # HIGH RISK - Data Modification/Deletion Tools
    "createSalesforceCase": ToolConfirmationRule(
        tool_name="createSalesforceCase",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate a new Salesforce case:\n- **Subject**: {subject}\n- **Description**: {description}\n\nProceed with creation?",
        risk_level="high"
    ),
    "create_salesforce_case": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="create_salesforce_case",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate a new Salesforce case:\n- **Subject**: {subject}\n- **Description**: {description}\n\nProceed with creation?",
        risk_level="high"
    ),
    "createSalesforceContact": ToolConfirmationRule(
        tool_name="createSalesforceContact",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate new Salesforce contact:\n- **Name**: {first_name} {last_name}\n- **Email**: {email}\n\nProceed?",
        risk_level="high"
    ),
    "create_salesforce_contact": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="create_salesforce_contact",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate new Salesforce contact:\n- **Name**: {first_name} {last_name}\n- **Email**: {email}\n\nProceed?",
        risk_level="high"
    ),
    "createSalesforceAccount": ToolConfirmationRule(
        tool_name="createSalesforceAccount",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate new Salesforce account:\n- **Name**: {name}\n- **Industry**: {industry}\n\nProceed?",
        risk_level="high"
    ),
    "create_salesforce_account": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="create_salesforce_account",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate new Salesforce account:\n- **Name**: {name}\n- **Industry**: {industry}\n\nProceed?",
        risk_level="high"
    ),
    "createSalesforceOpportunity": ToolConfirmationRule(
        tool_name="createSalesforceOpportunity",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate new Salesforce opportunity:\n- **Name**: {name}\n- **Stage**: {stage}\n- **Close Date**: {close_date}\n- **Amount**: {amount}\n\nProceed?",
        risk_level="high"
    ),
    "create_salesforce_opportunity": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="create_salesforce_opportunity",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate new Salesforce opportunity:\n- **Name**: {name}\n- **Stage**: {stage}\n- **Close Date**: {close_date}\n- **Amount**: {amount}\n\nProceed?",
        risk_level="high"
    ),
    "updateSalesforceOpportunity": ToolConfirmationRule(
        tool_name="updateSalesforceOpportunity",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nUpdate Salesforce opportunity:\n- **ID**: {opportunity_id}\n- **New Stage**: {stage}\n\nProceed with update?",
        risk_level="high"
    ),
    "update_salesforce_opportunity": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="update_salesforce_opportunity",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nUpdate Salesforce opportunity:\n- **ID**: {opportunity_id}\n- **New Stage**: {stage}\n\nProceed with update?",
        risk_level="high"
    ),
    
    # MEDIUM RISK - Communication Tools
    "sendSMS": ToolConfirmationRule(
        tool_name="sendSMS",
        confirmation_message_template="📱 **Confirmation Required**\n\nSend SMS:\n- **To**: {phone_number}\n- **Message**: {message}\n\nSend this message?",
        risk_level="medium"
    ),
    "send_sms": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="send_sms",
        confirmation_message_template="📱 **Confirmation Required**\n\nSend SMS:\n- **To**: {phone_number}\n- **Message**: {message}\n\nSend this message?",
        risk_level="medium"
    ),
    "sendVoiceCall": ToolConfirmationRule(
        tool_name="sendVoiceCall",
        confirmation_message_template="📞 **Confirmation Required**\n\nMake voice call:\n- **To**: {phone_number}\n- **Message**: {message}\n\nPlace this call?",
        risk_level="medium"
    ),
    "send_voice_call": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="send_voice_call",
        confirmation_message_template="📞 **Confirmation Required**\n\nMake voice call:\n- **To**: {phone_number}\n- **Message**: {message}\n\nPlace this call?",
        risk_level="medium"
    ),
    "sendSalesforceEmail": ToolConfirmationRule(
        tool_name="sendSalesforceEmail",
        confirmation_message_template="📧 **Confirmation Required**\n\nSend email via Salesforce:\n- **To**: {to_addresses}\n- **Subject**: {subject}\n\nSend this email?",
        risk_level="medium"
    ),
    "send_salesforce_email": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="send_salesforce_email",
        confirmation_message_template="📧 **Confirmation Required**\n\nSend email via Salesforce:\n- **To**: {to_addresses}\n- **Subject**: {subject}\n\nSend this email?",
        risk_level="medium"
    ),
    "createGmailDraft": ToolConfirmationRule(
        tool_name="createGmailDraft",
        confirmation_message_template="✉️ **Confirmation Required**\n\nCreate Gmail draft:\n- **To**: {receiver}\n- **Subject**: {subject}\n\nCreate this draft?",
        risk_level="low"
    ),
    "create_gmail_draft": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="create_gmail_draft",
        confirmation_message_template="✉️ **Confirmation Required**\n\nCreate Gmail draft:\n- **To**: {receiver}\n- **Subject**: {subject}\n\nCreate this draft?",
        risk_level="low"
    ),
    
    # MEDIUM RISK - Calendar/Scheduling
    "addCalendarEvent": ToolConfirmationRule(
        tool_name="addCalendarEvent",
        confirmation_message_template="📅 **Confirmation Required**\n\nAdd calendar event:\n- **Title**: {summary}\n- **Start**: {startTime}\n- **End**: {endTime}\n- **Attendees**: {attendees}\n\nCreate this event?",
        risk_level="medium"
    ),
    "add_calendar_event": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="add_calendar_event",
        confirmation_message_template="📅 **Confirmation Required**\n\nAdd calendar event:\n- **Title**: {summary}\n- **Start**: {start_time}\n- **End**: {end_time}\n- **Attendees**: {attendees}\n\nCreate this event?",
        risk_level="medium"
    ),
    "createSalesforceTask": ToolConfirmationRule(
        tool_name="createSalesforceTask",
        confirmation_message_template="✅ **Confirmation Required**\n\nCreate Salesforce task:\n- **Subject**: {subject}\n- **Priority**: {priority}\n- **Due Date**: {due_date}\n\nCreate this task?",
        risk_level="low"
    ),
    "create_salesforce_task": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="create_salesforce_task",
        confirmation_message_template="✅ **Confirmation Required**\n\nCreate Salesforce task:\n- **Subject**: {subject}\n- **Priority**: {priority}\n- **Due Date**: {due_date}\n\nCreate this task?",
        risk_level="low"
    ),
    
    # HIGH RISK - File Operations
    "uploadSalesforceFile": ToolConfirmationRule(
        tool_name="uploadSalesforceFile",
        confirmation_message_template="📁 **Confirmation Required**\n\nUpload file to Salesforce:\n- **Title**: {title}\n- **Description**: {description}\n\nProceed with upload?",
        risk_level="high"
    ),
    "upload_salesforce_file": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="upload_salesforce_file",
        confirmation_message_template="📁 **Confirmation Required**\n\nUpload file to Salesforce:\n- **Title**: {title}\n- **Description**: {description}\n\nProceed with upload?",
        risk_level="high"
    ),
    
    # HIGH RISK - Compliance Document Generation
    "generateComplianceReport": ToolConfirmationRule(
        tool_name="generateComplianceReport",
        confirmation_message_template="📋 **Confirmation Required**\n\nGenerate compliance report:\n- **Standards**: {standards_json}\n- **Include Checklist**: {include_checklist}\n- **Include Penalties**: {include_penalties}\n\nGenerate this report?",
        risk_level="medium"
    ),
    "generate_compliance_report": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="generate_compliance_report",
        confirmation_message_template="📋 **Confirmation Required**\n\nGenerate compliance report:\n- **Standards**: {standards_json}\n- **Include Checklist**: {include_checklist}\n- **Include Penalties**: {include_penalties}\n\nGenerate this report?",
        risk_level="medium"
    ),
    
    # HIGH RISK - Compliance Module Creation
    "createComplianceModule": ToolConfirmationRule(
        tool_name="createComplianceModule",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate compliance module:\n- **Filename**: {filename}\n- **Overwrite**: {allow_overwrite}\n\nThis will create/modify code. Proceed?",
        risk_level="high"
    ),
    "create_compliance_module": ToolConfirmationRule(  # MCP tools use snake_case
        tool_name="create_compliance_module",
        confirmation_message_template="⚠️ **Confirmation Required**\n\nCreate compliance module:\n- **Filename**: {filename}\n- **Overwrite**: {allow_overwrite}\n\nThis will create/modify code. Proceed?",
        risk_level="high"
    ),
}


# Quick lookup set for performance
CONFIRMATION_REQUIRED_TOOL_NAMES: Set[str] = set(TOOLS_REQUIRING_CONFIRMATION.keys())


def requires_confirmation(tool_name: str) -> bool:
    """Check if a tool requires user confirmation before execution."""
    return tool_name in CONFIRMATION_REQUIRED_TOOL_NAMES


def get_confirmation_rule(tool_name: str) -> Optional[ToolConfirmationRule]:
    """Get the confirmation rule for a specific tool."""
    return TOOLS_REQUIRING_CONFIRMATION.get(tool_name)


def format_confirmation_message(tool_name: str, tool_args: dict) -> str:
    """
    Format a confirmation message for a tool based on its arguments.
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments that will be passed to the tool
    
    Returns:
        Formatted confirmation message string
    """
    rule = get_confirmation_rule(tool_name)
    if not rule:
        return f"⚠️ Confirm execution of {tool_name}?"
    
    try:
        # Format the template with available args, using "N/A" for missing values
        formatted_args = {}
        for key in tool_args:
            value = tool_args[key]
            # Handle common types
            if isinstance(value, (list, dict)):
                formatted_args[key] = str(value) if value else "N/A"
            elif value is None:
                formatted_args[key] = "N/A"
            else:
                formatted_args[key] = str(value)
        
        # Use safe formatting - only replace available placeholders
        message = rule.confirmation_message_template
        for key, value in formatted_args.items():
            placeholder = f"{{{key}}}"
            if placeholder in message:
                message = message.replace(placeholder, value)
        
        # Remove any unreplaced placeholders
        import re
        message = re.sub(r'\{[^}]+\}', 'N/A', message)
        
        return message
    except Exception as e:
        # Fallback to simple message if formatting fails
        return f"⚠️ Confirm execution of {tool_name} with the following parameters?\n{json.dumps(tool_args, indent=2)}"


def get_tools_by_risk_level(risk_level: str) -> list[str]:
    """Get all tools of a specific risk level."""
    return [
        name for name, rule in TOOLS_REQUIRING_CONFIRMATION.items()
        if rule.risk_level == risk_level
    ]


# Allow runtime modification of confirmation requirements
def add_confirmation_requirement(rule: ToolConfirmationRule):
    """Add a new tool to the confirmation requirements."""
    TOOLS_REQUIRING_CONFIRMATION[rule.tool_name] = rule
    CONFIRMATION_REQUIRED_TOOL_NAMES.add(rule.tool_name)


def remove_confirmation_requirement(tool_name: str):
    """Remove a tool from confirmation requirements."""
    if tool_name in TOOLS_REQUIRING_CONFIRMATION:
        del TOOLS_REQUIRING_CONFIRMATION[tool_name]
        CONFIRMATION_REQUIRED_TOOL_NAMES.discard(tool_name)


def disable_all_confirmations():
    """Disable all tool confirmations (useful for testing or automated workflows)."""
    for rule in TOOLS_REQUIRING_CONFIRMATION.values():
        rule.requires_user_confirmation = False


def enable_all_confirmations():
    """Re-enable all tool confirmations."""
    for rule in TOOLS_REQUIRING_CONFIRMATION.values():
        rule.requires_user_confirmation = True


import json
