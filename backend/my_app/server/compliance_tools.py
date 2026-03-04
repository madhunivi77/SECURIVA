"""
Compliance Tools for AI Agent
Provides tool functions for querying compliance standards (GDPR, HIPAA, PCI-DSS)
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .compliance_data import (
    GDPR_STANDARDS,
    HIPAA_STANDARDS,
    PCI_DSS_STANDARDS,
    COMPLIANCE_CHECKLISTS,
    COMPLIANCE_CROSS_REFERENCE,
    get_all_standards,
    get_standard,
    get_checklist,
    get_cross_reference
)
from .tool_logger import log_tool_call


def get_compliance_overview(standard: str) -> Dict[str, Any]:
    """
    Get an overview of a compliance standard
    
    Args:
        standard: Compliance standard name (gdpr, hipaa, pci_dss)
    
    Returns:
        dict: Overview information including name, region, effective date, and description
    """
    log_tool_call(
        tool_name="get_compliance_overview",
        input_data={"standard": standard}
    )
    
    try:
        standard_lower = standard.lower().replace("-", "_")
        data = get_standard(standard_lower)
        
        if not data:
            result = {
                "success": False,
                "error": f"Unknown compliance standard: {standard}",
                "available_standards": ["gdpr", "hipaa", "pci_dss"]
            }
        else:
            result = {
                "success": True,
                "standard": data.get("name"),
                "region": data.get("region"),
                "effective_date": data.get("effective_date"),
                "overview": data.get("overview"),
                "official_reference": data.get("official_reference"),
                "current_version": data.get("current_version"),
                "managed_by": data.get("managed_by")
            }
        
        log_tool_call(
            tool_name="get_compliance_overview",
            input_data={"standard": standard},
            output_data=result,
            success=result.get("success", False)
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="get_compliance_overview",
            input_data={"standard": standard},
            output_data=error_result,
            success=False
        )
        
        return error_result


def get_compliance_requirements(standard: str, requirement_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get detailed compliance requirements for a standard
    
    Args:
        standard: Compliance standard name (gdpr, hipaa, pci_dss)
        requirement_id: Optional specific requirement ID to retrieve
    
    Returns:
        dict: Detailed requirements information
    """
    log_tool_call(
        tool_name="get_compliance_requirements",
        input_data={"standard": standard, "requirement_id": requirement_id}
    )
    
    try:
        standard_lower = standard.lower().replace("-", "_")
        data = get_standard(standard_lower)
        
        if not data:
            result = {
                "success": False,
                "error": f"Unknown compliance standard: {standard}"
            }
        else:
            # Handle different data structures for different standards
            if standard_lower == "gdpr":
                requirements = data.get("key_principles", [])
                if requirement_id:
                    # For GDPR, search by id field
                    requirements = [r for r in requirements if r.get("id") == requirement_id]
            elif standard_lower == "hipaa":
                requirements = data.get("key_rules", [])
                if requirement_id:
                    requirements = [r for r in requirements if r.get("id") == requirement_id]
            elif standard_lower == "pci_dss":
                requirements = data.get("requirements", [])
                if requirement_id:
                    requirements = [r for r in requirements if r.get("id") == requirement_id]
            else:
                requirements = []
            
            result = {
                "success": True,
                "standard": data.get("name"),
                "requirements": requirements,
                "total_count": len(requirements)
            }
        
        log_tool_call(
            tool_name="get_compliance_requirements",
            input_data={"standard": standard, "requirement_id": requirement_id},
            output_data={k: v for k, v in result.items() if k != "requirements"},  # Don't log full requirements
            success=result.get("success", False)
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="get_compliance_requirements",
            input_data={"standard": standard, "requirement_id": requirement_id},
            output_data=error_result,
            success=False
        )
        
        return error_result


def get_compliance_checklist(standard: str) -> Dict[str, Any]:
    """
    Get a compliance checklist for audit preparation
    
    Args:
        standard: Compliance standard name (gdpr, hipaa, pci_dss)
    
    Returns:
        dict: Checklist items with requirements and categories
    """
    log_tool_call(
        tool_name="get_compliance_checklist",
        input_data={"standard": standard}
    )
    
    try:
        standard_lower = standard.lower().replace("-", "_")
        checklist = get_checklist(standard_lower)
        
        if not checklist:
            result = {
                "success": False,
                "error": f"No checklist available for: {standard}",
                "available_standards": ["gdpr", "hipaa", "pci_dss"]
            }
        else:
            # Group by category
            categories = {}
            for item in checklist:
                category = item.get("category", "Other")
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
            
            result = {
                "success": True,
                "standard": standard.upper(),
                "checklist": checklist,
                "categories": categories,
                "total_items": len(checklist)
            }
        
        log_tool_call(
            tool_name="get_compliance_checklist",
            input_data={"standard": standard},
            output_data={k: v for k, v in result.items() if k not in ["checklist", "categories"]},
            success=result.get("success", False)
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="get_compliance_checklist",
            input_data={"standard": standard},
            output_data=error_result,
            success=False
        )
        
        return error_result


def get_penalty_information(standard: str) -> Dict[str, Any]:
    """
    Get penalty/fine information for non-compliance
    
    Args:
        standard: Compliance standard name (gdpr, hipaa, pci_dss)
    
    Returns:
        dict: Penalty tiers and amounts
    """
    log_tool_call(
        tool_name="get_penalty_information",
        input_data={"standard": standard}
    )
    
    try:
        standard_lower = standard.lower().replace("-", "_")
        data = get_standard(standard_lower)
        
        if not data:
            result = {
                "success": False,
                "error": f"Unknown compliance standard: {standard}"
            }
        else:
            penalties = data.get("penalties", {})
            result = {
                "success": True,
                "standard": data.get("name"),
                "penalties": penalties
            }
        
        log_tool_call(
            tool_name="get_penalty_information",
            input_data={"standard": standard},
            output_data=result,
            success=result.get("success", False)
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="get_penalty_information",
            input_data={"standard": standard},
            output_data=error_result,
            success=False
        )
        
        return error_result


def get_breach_notification_requirements(standard: str) -> Dict[str, Any]:
    """
    Get breach notification requirements for a compliance standard
    
    Args:
        standard: Compliance standard name (gdpr, hipaa, pci_dss)
    
    Returns:
        dict: Breach notification timelines and requirements
    """
    log_tool_call(
        tool_name="get_breach_notification_requirements",
        input_data={"standard": standard}
    )
    
    try:
        standard_lower = standard.lower().replace("-", "_")
        data = get_standard(standard_lower)
        
        if not data:
            result = {
                "success": False,
                "error": f"Unknown compliance standard: {standard}"
            }
        else:
            breach_info = data.get("breach_notification", {})
            
            # Add standard-specific breach notification info
            if standard_lower == "pci_dss":
                breach_info = {
                    "description": "Immediate notification to payment brands and acquiring bank",
                    "requirements": [
                        "Notify acquiring bank immediately upon suspicion of breach",
                        "Notify payment brands per their specific requirements",
                        "Conduct forensic investigation",
                        "Submit remediation plan"
                    ]
                }
            
            result = {
                "success": True,
                "standard": data.get("name"),
                "breach_notification": breach_info
            }
        
        log_tool_call(
            tool_name="get_breach_notification_requirements",
            input_data={"standard": standard},
            output_data=result,
            success=result.get("success", False)
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="get_breach_notification_requirements",
            input_data={"standard": standard},
            output_data=error_result,
            success=False
        )
        
        return error_result


def cross_reference_compliance_topic(topic: str) -> Dict[str, Any]:
    """
    Cross-reference a compliance topic across GDPR, HIPAA, and PCI-DSS
    
    Args:
        topic: Compliance topic (e.g., "data_encryption", "access_control", "audit_logging")
    
    Returns:
        dict: Cross-referenced requirements from all three standards
    """
    log_tool_call(
        tool_name="cross_reference_compliance_topic",
        input_data={"topic": topic}
    )
    
    try:
        topic_lower = topic.lower().replace(" ", "_")
        cross_ref = get_cross_reference(topic_lower)
        
        if not cross_ref:
            # List available topics
            available_topics = list(COMPLIANCE_CROSS_REFERENCE.keys())
            result = {
                "success": False,
                "error": f"No cross-reference available for topic: {topic}",
                "available_topics": available_topics
            }
        else:
            result = {
                "success": True,
                "topic": topic,
                "cross_references": cross_ref,
                "standards_covered": list(cross_ref.keys())
            }
        
        log_tool_call(
            tool_name="cross_reference_compliance_topic",
            input_data={"topic": topic},
            output_data=result,
            success=result.get("success", False)
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="cross_reference_compliance_topic",
            input_data={"topic": topic},
            output_data=error_result,
            success=False
        )
        
        return error_result


def search_compliance_requirements(query: str, standards: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for compliance requirements matching a query across standards
    
    Args:
        query: Search query string
        standards: Optional list of standards to search (default: all)
    
    Returns:
        dict: Matching requirements from specified standards
    """
    log_tool_call(
        tool_name="search_compliance_requirements",
        input_data={"query": query, "standards": standards}
    )
    
    try:
        if not standards:
            standards = ["gdpr", "hipaa", "pci_dss"]
        
        query_lower = query.lower()
        results = []
        
        for standard_name in standards:
            standard_lower = standard_name.lower().replace("-", "_")
            data = get_standard(standard_lower)
            
            if not data:
                continue
            
            # Search in different structures
            if standard_lower == "gdpr":
                searchable_items = data.get("key_principles", [])
            elif standard_lower == "hipaa":
                searchable_items = data.get("key_rules", [])
            elif standard_lower == "pci_dss":
                searchable_items = data.get("requirements", [])
            else:
                searchable_items = []
            
            # Search in each item
            for item in searchable_items:
                item_str = json.dumps(item).lower()
                if query_lower in item_str:
                    results.append({
                        "standard": standard_name.upper(),
                        "item": item
                    })
        
        result = {
            "success": True,
            "query": query,
            "standards_searched": standards,
            "matches": results,
            "total_matches": len(results)
        }
        
        log_tool_call(
            tool_name="search_compliance_requirements",
            input_data={"query": query, "standards": standards},
            output_data={k: v for k, v in result.items() if k != "matches"},
            success=True
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="search_compliance_requirements",
            input_data={"query": query, "standards": standards},
            output_data=error_result,
            success=False
        )
        
        return error_result


def generate_compliance_report(
    standards: List[str],
    include_checklist: bool = True,
    include_penalties: bool = True,
    include_breach_info: bool = True
) -> Dict[str, Any]:
    """
    Generate a comprehensive compliance report for specified standards
    
    Args:
        standards: List of standards to include (gdpr, hipaa, pci_dss)
        include_checklist: Include compliance checklists
        include_penalties: Include penalty information
        include_breach_info: Include breach notification requirements
    
    Returns:
        dict: Comprehensive compliance report
    """
    log_tool_call(
        tool_name="generate_compliance_report",
        input_data={
            "standards": standards,
            "include_checklist": include_checklist,
            "include_penalties": include_penalties,
            "include_breach_info": include_breach_info
        }
    )
    
    try:
        report = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "standards": [],
            "summary": {
                "total_standards": len(standards),
                "total_requirements": 0,
                "total_checklist_items": 0
            }
        }
        
        for standard_name in standards:
            standard_lower = standard_name.lower().replace("-", "_")
            data = get_standard(standard_lower)
            
            if not data:
                continue
            
            standard_report = {
                "name": data.get("name"),
                "region": data.get("region"),
                "overview": data.get("overview"),
                "official_reference": data.get("official_reference")
            }
            
            # Add requirements
            if standard_lower == "gdpr":
                requirements = data.get("key_principles", [])
            elif standard_lower == "hipaa":
                requirements = data.get("key_rules", [])
            elif standard_lower == "pci_dss":
                requirements = data.get("requirements", [])
            else:
                requirements = []
            
            standard_report["requirements"] = requirements
            standard_report["requirement_count"] = len(requirements)
            report["summary"]["total_requirements"] += len(requirements)
            
            # Add checklist if requested
            if include_checklist:
                checklist = get_checklist(standard_lower)
                standard_report["checklist"] = checklist
                standard_report["checklist_count"] = len(checklist)
                report["summary"]["total_checklist_items"] += len(checklist)
            
            # Add penalties if requested
            if include_penalties:
                standard_report["penalties"] = data.get("penalties", {})
            
            # Add breach notification info if requested
            if include_breach_info:
                standard_report["breach_notification"] = data.get("breach_notification", {})
            
            report["standards"].append(standard_report)
        
        result = {
            "success": True,
            "report": report
        }
        
        log_tool_call(
            tool_name="generate_compliance_report",
            input_data={"standards": standards},
            output_data={"success": True, "summary": report["summary"]},
            success=True
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="generate_compliance_report",
            input_data={"standards": standards},
            output_data=error_result,
            success=False
        )
        
        return error_result


# Export all tool functions
__all__ = [
    "get_compliance_overview",
    "get_compliance_requirements",
    "get_compliance_checklist",
    "get_penalty_information",
    "get_breach_notification_requirements",
    "cross_reference_compliance_topic",
    "search_compliance_requirements",
    "generate_compliance_report"
]
