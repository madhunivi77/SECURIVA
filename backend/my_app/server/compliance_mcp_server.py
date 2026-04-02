"""
MCP Server Integration for Compliance Tools
Exposes compliance standards tools via Model Context Protocol
"""

from typing import Any, Dict, List, Optional
import json
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Import compliance tools
from .compliance_tools import (
    get_compliance_overview,
    get_compliance_requirements,
    get_compliance_checklist,
    get_penalty_information,
    get_breach_notification_requirements,
    cross_reference_compliance_topic,
    search_compliance_requirements,
    generate_compliance_report
)


# Create MCP server instance
compliance_server = Server("compliance-standards-server")


@compliance_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List all available compliance tools for the AI agent
    """
    return [
        types.Tool(
            name="get_compliance_overview",
            description="Get an overview of a compliance standard (GDPR, HIPAA, or PCI-DSS) including its name, region, effective date, and description",
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": "Compliance standard name (gdpr, hipaa, or pci_dss)",
                        "enum": ["gdpr", "hipaa", "pci_dss"]
                    }
                },
                "required": ["standard"]
            }
        ),
        types.Tool(
            name="get_compliance_requirements",
            description="Get detailed compliance requirements for a standard. Can retrieve all requirements or a specific requirement by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": "Compliance standard name",
                        "enum": ["gdpr", "hipaa", "pci_dss"]
                    },
                    "requirement_id": {
                        "type": ["integer", "string", "null"],
                        "description": "Optional specific requirement ID to retrieve"
                    }
                },
                "required": ["standard"]
            }
        ),
        types.Tool(
            name="get_compliance_checklist",
            description="Get a compliance checklist for audit preparation with categorized items to verify",
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": "Compliance standard name",
                        "enum": ["gdpr", "hipaa", "pci_dss"]
                    }
                },
                "required": ["standard"]
            }
        ),
        types.Tool(
            name="get_penalty_information",
            description="Get penalty and fine information for non-compliance with a standard",
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": "Compliance standard name",
                        "enum": ["gdpr", "hipaa", "pci_dss"]
                    }
                },
                "required": ["standard"]
            }
        ),
        types.Tool(
            name="get_breach_notification_requirements",
            description="Get breach notification requirements including timelines and who to notify",
            inputSchema={
                "type": "object",
                "properties": {
                    "standard": {
                        "type": "string",
                        "description": "Compliance standard name",
                        "enum": ["gdpr", "hipaa", "pci_dss"]
                    }
                },
                "required": ["standard"]
            }
        ),
        types.Tool(
            name="cross_reference_compliance_topic",
            description="Cross-reference a compliance topic (like 'data_encryption', 'access_control', 'audit_logging') across GDPR, HIPAA, and PCI-DSS to see how each standard addresses it",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Compliance topic to cross-reference",
                        "enum": ["data_encryption", "access_control", "audit_logging", "breach_notification", "data_retention"]
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="search_compliance_requirements",
            description="Search for compliance requirements matching a query string across one or more standards",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "standards": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["gdpr", "hipaa", "pci_dss"]
                        },
                        "description": "Optional list of standards to search (default: all)"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="generate_compliance_report",
            description="Generate a comprehensive compliance report for specified standards including requirements, checklists, penalties, and breach notification info",
            inputSchema={
                "type": "object",
                "properties": {
                    "standards": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["gdpr", "hipaa", "pci_dss"]
                        },
                        "description": "List of standards to include in report"
                    },
                    "include_checklist": {
                        "type": "boolean",
                        "description": "Include compliance checklists",
                        "default": True
                    },
                    "include_penalties": {
                        "type": "boolean",
                        "description": "Include penalty information",
                        "default": True
                    },
                    "include_breach_info": {
                        "type": "boolean",
                        "description": "Include breach notification requirements",
                        "default": True
                    }
                },
                "required": ["standards"]
            }
        )
    ]


@compliance_server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests from the AI agent
    """
    if not arguments:
        arguments = {}
    
    result = None
    
    try:
        if name == "get_compliance_overview":
            result = get_compliance_overview(arguments.get("standard", ""))
            
        elif name == "get_compliance_requirements":
            result = get_compliance_requirements(
                arguments.get("standard", ""),
                arguments.get("requirement_id")
            )
            
        elif name == "get_compliance_checklist":
            result = get_compliance_checklist(arguments.get("standard", ""))
            
        elif name == "get_penalty_information":
            result = get_penalty_information(arguments.get("standard", ""))
            
        elif name == "get_breach_notification_requirements":
            result = get_breach_notification_requirements(arguments.get("standard", ""))
            
        elif name == "cross_reference_compliance_topic":
            result = cross_reference_compliance_topic(arguments.get("topic", ""))
            
        elif name == "search_compliance_requirements":
            result = search_compliance_requirements(
                arguments.get("query", ""),
                arguments.get("standards")
            )
            
        elif name == "generate_compliance_report":
            result = generate_compliance_report(
                arguments.get("standards", []),
                arguments.get("include_checklist", True),
                arguments.get("include_penalties", True),
                arguments.get("include_breach_info", True)
            )
            
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {name}"
            }
        
        # Return result as TextContent
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "tool": name
        }
        return [
            types.TextContent(
                type="text",
                text=json.dumps(error_result, indent=2)
            )
        ]


async def run_compliance_mcp_server():
    """
    Run the compliance MCP server
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await compliance_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="compliance-standards-server",
                server_version="1.0.0",
                capabilities=compliance_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


# For standalone execution
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_compliance_mcp_server())
