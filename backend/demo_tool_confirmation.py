"""
Demo script for Tool Confirmation System

This script demonstrates how the tool confirmation system works
with various scenarios.
"""

from my_app.server.tool_confirmation_handler import get_confirmation_handler
from my_app.server.tool_confirmation_config import (
    requires_confirmation,
    format_confirmation_message,
    get_confirmation_rule
)


def print_separator():
    print("\n" + "=" * 80 + "\n")


def demo_basic_confirmation():
    """Demonstrate basic confirmation workflow."""
    print("📋 DEMO 1: Basic Confirmation Workflow")
    print_separator()
    
    handler = get_confirmation_handler()
    
    # Simulate user requesting to send SMS
    print("User: 'Send SMS to +1234567890 saying Meeting at 3pm'")
    print()
    
    # Check if tool requires confirmation
    tool_name = "sendSMS"
    if requires_confirmation(tool_name):
        print(f"✓ Tool '{tool_name}' requires confirmation")
        print()
        
        # Create confirmation request
        tool_args = {
            "phone_number": "+1234567890",
            "message": "Meeting at 3pm"
        }
        
        conf_id, message = handler.create_confirmation_request(
            tool_name=tool_name,
            tool_args=tool_args,
            session_id="demo-session-1"
        )
        
        print("System Response:")
        print(message)
        print()
        
        # User approves
        print("User: 'yes'")
        print()
        
        response_type, tool_info = handler.process_user_response(
            "yes",
            session_id="demo-session-1"
        )
        
        if response_type == "approved":
            tool_name, args = tool_info
            print(f"✅ Confirmation approved!")
            print(f"   Tool to execute: {tool_name}")
            print(f"   Arguments: {args}")


def demo_denial():
    """Demonstrate denial workflow."""
    print("📋 DEMO 2: User Denies Action")
    print_separator()
    
    handler = get_confirmation_handler()
    
    print("User: 'Create a Salesforce contact for Jane Doe'")
    print()
    
    tool_args = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com"
    }
    
    conf_id, message = handler.create_confirmation_request(
        tool_name="createSalesforceContact",
        tool_args=tool_args,
        session_id="demo-session-2"
    )
    
    print(message)
    print()
    
    print("User: 'no, cancel that'")
    print()
    
    response_type, _ = handler.process_user_response(
        "no",
        session_id="demo-session-2"
    )
    
    if response_type == "denied":
        print("❌ Action cancelled per user request")


def demo_multiple_confirmations():
    """Demonstrate handling multiple confirmations."""
    print("📋 DEMO 3: Multiple Confirmations")
    print_separator()
    
    handler = get_confirmation_handler()
    
    # First confirmation
    print("User Request 1: 'Send SMS to +1111111111'")
    conf_id_1, msg_1 = handler.create_confirmation_request(
        tool_name="sendSMS",
        tool_args={"phone_number": "+1111111111", "message": "Test 1"},
        session_id="demo-session-3a"
    )
    print(f"Confirmation ID: {conf_id_1[:8]}...")
    print()
    
    # Second confirmation (different session)
    print("User Request 2: 'Create calendar event'")
    conf_id_2, msg_2 = handler.create_confirmation_request(
        tool_name="addCalendarEvent",
        tool_args={"summary": "Team Meeting", "startTime": "2026-04-08 14:00"},
        session_id="demo-session-3b"
    )
    print(f"Confirmation ID: {conf_id_2[:8]}...")
    print()
    
    # Get all active confirmations
    confirmations_3a = handler.get_session_confirmations("demo-session-3a")
    confirmations_3b = handler.get_session_confirmations("demo-session-3b")
    
    print(f"Active confirmations for session 3a: {len(confirmations_3a)}")
    print(f"Active confirmations for session 3b: {len(confirmations_3b)}")


def demo_expiration():
    """Demonstrate confirmation expiration."""
    print("📋 DEMO 4: Confirmation Expiration")
    print_separator()
    
    from my_app.server.tool_confirmation_handler import ToolConfirmationHandler
    
    # Create handler with very short timeout
    handler = ToolConfirmationHandler(confirmation_timeout_seconds=1)
    
    print("Creating confirmation with 1-second timeout...")
    conf_id, message = handler.create_confirmation_request(
        tool_name="sendSMS",
        tool_args={"phone_number": "+1234567890", "message": "Test"},
        session_id="demo-session-4"
    )
    
    print("Waiting for expiration...")
    import time
    time.sleep(1.5)
    
    response_type, _ = handler.process_user_response(
        "yes",
        session_id="demo-session-4"
    )
    
    if response_type == "expired":
        print("⏱️ Confirmation has expired!")


def demo_tool_list():
    """Show all tools requiring confirmation."""
    print("📋 DEMO 5: Tools Requiring Confirmation")
    print_separator()
    
    from my_app.server.tool_confirmation_config import TOOLS_REQUIRING_CONFIRMATION
    
    # Group by risk level
    high_risk = []
    medium_risk = []
    low_risk = []
    
    for tool_name, rule in TOOLS_REQUIRING_CONFIRMATION.items():
        if rule.risk_level == "high":
            high_risk.append(tool_name)
        elif rule.risk_level == "medium":
            medium_risk.append(tool_name)
        else:
            low_risk.append(tool_name)
    
    print("🔴 HIGH RISK TOOLS:")
    for tool in high_risk:
        print(f"  • {tool}")
    
    print("\n🟡 MEDIUM RISK TOOLS:")
    for tool in medium_risk:
        print(f"  • {tool}")
    
    print("\n🟢 LOW RISK TOOLS:")
    for tool in low_risk:
        print(f"  • {tool}")
    
    print(f"\nTotal tools requiring confirmation: {len(TOOLS_REQUIRING_CONFIRMATION)}")


def demo_custom_confirmation():
    """Demonstrate adding a custom confirmation rule."""
    print("📋 DEMO 6: Adding Custom Confirmation Rule")
    print_separator()
    
    from my_app.server.tool_confirmation_config import (
        add_confirmation_requirement,
        remove_confirmation_requirement,
        ToolConfirmationRule
    )
    
    print("Adding custom tool: 'deleteAllData'")
    
    custom_rule = ToolConfirmationRule(
        tool_name="deleteAllData",
        confirmation_message_template="⚠️ **DANGER**\\n\\nDelete all data from:\\n- **Database**: {database_name}\\n\\n⚠️ This action cannot be undone!\\n\\nProceed?",
        risk_level="high"
    )
    
    add_confirmation_requirement(custom_rule)
    
    print(f"✓ Added 'deleteAllData' to confirmation list")
    print()
    
    # Test it
    if requires_confirmation("deleteAllData"):
        print("✓ Confirmation check works!")
        
        message = format_confirmation_message(
            "deleteAllData",
            {"database_name": "production_db"}
        )
        
        print("\nGenerated confirmation message:")
        print(message)
    
    # Cleanup
    remove_confirmation_requirement("deleteAllData")
    print("\n✓ Removed custom rule")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print(" " * 20 + "TOOL CONFIRMATION SYSTEM DEMO")
    print("=" * 80)
    
    try:
        demo_basic_confirmation()
        print_separator()
        
        demo_denial()
        print_separator()
        
        demo_multiple_confirmations()
        print_separator()
        
        demo_expiration()
        print_separator()
        
        demo_tool_list()
        print_separator()
        
        demo_custom_confirmation()
        print_separator()
        
        print("\n✅ All demos completed successfully!")
        print("\nFor more information, see: backend/docs/TOOL_CONFIRMATION_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
