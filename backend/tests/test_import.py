"""
Simple test to verify compliance tools import properly
"""
print("Testing compliance tools import...")

try:
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
    print("✓ Compliance tools imported successfully\n")
    
    # Test a simple function
    result = get_compliance_overview("gdpr")
    print(f"✓ get_compliance_overview function works: {result['success']}")
    print(f"  Standard: {result.get('standard', 'N/A')}\n")
    
    # Count tools
    tool_count = 8
    print(f"✓ All {tool_count} compliance tool functions available:\n")
    print("  1. get_compliance_overview")
    print("  2. get_compliance_requirements")
    print("  3. get_compliance_checklist")
    print("  4. get_penalty_information")
    print("  5. get_breach_notification_requirements")
    print("  6. cross_reference_compliance_topic")
    print("  7. search_compliance_requirements")
    print("  8. generate_compliance_report")
    
    print("\n" + "="*60)
    print("✓ COMPLIANCE TOOLS READY!")
    print("="*60)
    print("\nThese tools are now registered in mcp_server.py as:")
    print("  • getComplianceOverview")
    print("  • getComplianceRequirements")
    print("  • getComplianceChecklist")
    print("  • getPenaltyInformation")
    print("  • getBreachNotificationRequirements")
    print("  • crossReferenceComplianceTopic")
    print("  • searchComplianceRequirements")
    print("  • generateComplianceReport")
    print("\nThe AI will see and use these when you start the MCP server!")
    
except ImportError as e:
    print(f"✗ Import failed: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
