"""
Test file for Telesign SMS functionality using the Enterprise SDK
"""

import os
from dotenv import load_dotenv
from my_app.server.telesign_auth import (
    send_sms,
    verify_phone_number,
    get_message_status,
    get_messaging_client,
    send_verification_code,
    verify_code,
    assess_phone_risk  
)

print("=" * 60)
print("TELESIGN SMS TEST SUITE")
print("=" * 60)

load_dotenv()

# Helper function to format phone numbers
def format_phone_number(phone: str) -> str:
    """
    Format phone number by removing + prefix for trial accounts
    
    Args:
        phone: Phone number with or without + prefix
    
    Returns:
        str: Phone number without + prefix
    """
    return phone.lstrip('+')


def get_phone_input(prompt: str = "Enter phone number", allow_skip: bool = True) -> str | None:
    """
    Get phone number input with validation and helpful instructions
    
    Args:
        prompt: Custom prompt text
        allow_skip: Whether to allow skipping by pressing Enter
    
    Returns:
        str: Formatted phone number or None if skipped
    """
    print(f"\n{prompt}")
    print("  Format: E.164 format (e.g., +16027395506 or 16027395506)")
    print("  Note: The + prefix will be automatically removed for trial accounts")
    if allow_skip:
        print("  Press Enter to skip this test")
    
    phone = input("Phone number: ").strip()
    
    if not phone and allow_skip:
        return None
    
    if not phone:
        print("❌ Phone number is required!")
        return get_phone_input(prompt, allow_skip)
    
    # Format the phone number
    formatted = format_phone_number(phone)
    print(f"  → Using: {formatted}")
    return formatted


def confirm_action(action: str) -> bool:
    """
    Ask user to confirm an action
    
    Args:
        action: Description of the action to confirm
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    response = input(f"\n{action}? (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def get_lifecycle_event() -> str:
    """
    Get account lifecycle event selection from user
    
    Returns:
        str: Selected lifecycle event
    """
    print("\nSelect account lifecycle stage:")
    print("  1. create - New account registration")
    print("  2. sign-in - User login/authentication")
    print("  3. transact - Financial transaction")
    print("  4. update - Account information update")
    print("  Press Enter for default (create)")
    
    choice = input("Choice (1-4): ").strip()
    
    lifecycle_map = {
        "1": "create",
        "2": "sign-in",
        "3": "transact",
        "4": "update",
        "": "create"
    }
    
    event = lifecycle_map.get(choice, "create")
    print(f"  → Using lifecycle event: {event}")
    return event


# ===== Test 1: Verify Credentials =====
def test_credentials():
    print("\n" + "=" * 60)
    print("TEST 1: Verify Credentials")
    print("=" * 60)
    print("This test checks if your Telesign API credentials are valid.")
    
    try:
        client = get_messaging_client()
        print(f"✅ SUCCESS: Messaging client created")
        print(f"   Customer ID: {client.customer_id[:10]}...")
        return True
    except Exception as e:
        print(f"❌ FAILED: Could not create client")
        print(f"   Error: {e}")
        print(f"   → Check your .env file for TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY")
        return False


# ===== Test 2: Phone Number Verification =====
def test_phone_verification():
    print("\n" + "=" * 60)
    print("TEST 2: Phone Number Verification (PhoneID)")
    print("=" * 60)
    print("This test retrieves detailed information about a phone number:")
    print("  • Phone type (mobile, landline, VoIP, etc.)")
    print("  • Carrier/operator name")
    print("  • Country information")
    
    phone = get_phone_input("Enter phone number to verify")
    
    if not phone:
        print("⚠️  Test skipped")
        return
    
    try:
        print("\n🔄 Verifying phone number...")
        result = verify_phone_number(phone)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: Phone verification complete")
            print(f"   Phone Type: {result.get('phone_type', 'Unknown')}")
            print(f"   Carrier: {result.get('carrier', 'Unknown')}")
            print(f"   Country: {result.get('country', 'Unknown')}")
            print(f"   State: {result.get('state', 'Unknown')}")
            print(f"   City: {result.get('city', 'Unknown')}")
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            if 'trial account' in str(result.get('error', '')).lower():
                print(f"   → Add this number to your Telesign test numbers list")
    except Exception as e:
        print(f"❌ FAILED: Verification error")
        print(f"   Error: {e}")


# ===== Test 3: Send SMS =====
def test_send_sms():
    print("\n" + "=" * 60)
    print("TEST 3: Send SMS Message")
    print("=" * 60)
    print("This test sends a standard SMS text message.")
    
    phone = get_phone_input("Enter destination phone number for SMS")
    
    if not phone:
        print("⚠️  Test skipped")
        return None
    
    print("\nEnter your SMS message:")
    print("  (Press Enter for default message)")
    message = input("Message: ").strip()
    if not message:
        message = "Hello from Securiva! This is a test SMS message."
        print(f"  → Using default: '{message}'")
    
    if not confirm_action(f"Send SMS to {phone}"):
        print("❌ Test cancelled")
        return None
    
    try:
        print("\n🔄 Sending SMS...")
        result = send_sms(phone, message)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: SMS sent")
            print(f"   Reference ID: {result['reference_id']}")
            print(f"   Status: {result['status']}")
            print(f"   → Save this Reference ID to check delivery status later")
            return result['reference_id']
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   Errors: {result.get('errors', [])}")
            return None
    except Exception as e:
        print(f"❌ FAILED: Could not send SMS")
        print(f"   Error: {e}")
        return None


# ===== Test 4: Check Message Status =====
def test_message_status(reference_id: str = None):
    print("\n" + "=" * 60)
    print("TEST 4: Check Message Delivery Status")
    print("=" * 60)
    print("This test checks the delivery status of a previously sent message.")
    
    if not reference_id:
        print("\nEnter the Reference ID from a previous message:")
        print("  (Press Enter to skip)")
        reference_id = input("Reference ID: ").strip()
    
    if not reference_id:
        print("⚠️  Test skipped")
        return
    
    try:
        print("\n🔄 Checking message status...")
        result = get_message_status(reference_id)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: Status retrieved")
            print(f"   Status: {result['status']}")
            status_code = result['status'].get('code') if isinstance(result['status'], dict) else None
            if status_code:
                print(f"   Status Code: {status_code}")
                if status_code == 290:
                    print(f"   → Message in progress")
                elif status_code == 200:
                    print(f"   → Message delivered")
                elif status_code >= 400:
                    print(f"   → Message failed")
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
    except Exception as e:
        print(f"❌ FAILED: Could not retrieve status")
        print(f"   Error: {e}")


# ===== Test 5: Send 2FA Verification Code =====
def test_send_verification_code():
    print("\n" + "=" * 60)
    print("TEST 5: Send 2FA Verification Code")
    print("=" * 60)
    print("This test sends a verification code for two-factor authentication.")
    print("Telesign will automatically generate and send the code.")
    
    phone = get_phone_input("Enter phone number to receive verification code")
    
    if not phone:
        print("⚠️  Test skipped")
        return None
    
    if not confirm_action(f"Send verification code to {phone}"):
        print("❌ Test cancelled")
        return None
    
    try:
        print("\n🔄 Sending verification code...")
        result = send_verification_code(phone)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: Verification code sent")
            print(f"   Reference ID: {result['reference_id']}")
            print(f"   Generated Code: {result['verify_code']} (for testing)")
            print(f"   → The recipient should receive this code via SMS")
            print(f"   → Use Test 6 to verify the code they received")
            return {
                'reference_id': result['reference_id'],
                'verify_code': result['verify_code']
            }
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   Errors: {result.get('errors', [])}")
            return None
    except Exception as e:
        print(f"❌ FAILED: Could not send verification code")
        print(f"   Error: {e}")
        return None


# ===== Test 6: Verify 2FA Code =====
def test_verify_code(verification_data: dict = None):
    print("\n" + "=" * 60)
    print("TEST 6: Verify 2FA Code")
    print("=" * 60)
    print("This test verifies a code entered by the user.")
    
    reference_id = None
    original_code = None
    
    if verification_data:
        reference_id = verification_data.get('reference_id')
        original_code = verification_data.get('verify_code')
        print(f"\nUsing Reference ID: {reference_id}")
        print(f"Expected Code: {original_code} (hidden from user in production)")
    else:
        print("\nEnter the Reference ID from the verification code message:")
        print("  (Press Enter to skip)")
        reference_id = input("Reference ID: ").strip()
        
        if not reference_id:
            print("⚠️  Test skipped")
            return
        
        print("\nEnter the original verification code (for testing):")
        original_code = input("Original Code: ").strip()
    
    print("\nEnter the verification code received:")
    user_code = input("Code: ").strip()
    
    if not user_code:
        print("❌ Code is required")
        return
    
    try:
        print("\n🔄 Verifying code...")
        result = verify_code(reference_id, user_code, original_code)
        
        if result['status_code'] == 200:
            if result.get('valid'):
                print(f"✅ SUCCESS: {result.get('message', 'Code is VALID')}")
            else:
                print(f"❌ FAILED: {result.get('message', 'Code is INVALID')}")
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   Message: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"❌ FAILED: Could not verify code")
        print(f"   Error: {e}")


# ===== Test 7: Assess Phone Risk =====
def test_assess_risk():
    print("\n" + "=" * 60)
    print("TEST 7: Assess Phone Number Risk (Intelligence/Score API)")
    print("=" * 60)
    print("This test performs fraud risk assessment using Telesign Intelligence.")
    print("Useful for detecting suspicious registrations or transactions.")
    
    phone = get_phone_input("Enter phone number to assess")
    
    if not phone:
        print("⚠️  Test skipped")
        return
    
    # Get lifecycle event
    lifecycle_event = get_lifecycle_event()
    
    try:
        print(f"\n🔄 Assessing phone risk (lifecycle: {lifecycle_event})...")
        result = assess_phone_risk(phone, lifecycle_event)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: Risk assessment complete")
            print(f"   Reference ID: {result.get('reference_id', 'N/A')}")
            print(f"   Risk Level: {result.get('risk_level', 'Unknown')}")
            print(f"   Risk Score: {result.get('risk_score', 'N/A')} (0-1000 scale)")
            print(f"   Recommendation: {result.get('recommendation', 'Unknown')}")
            print(f"   Phone Type: {result.get('phone_type', 'Unknown')}")
            print(f"   Carrier: {result.get('carrier', 'Unknown')}")
            print(f"   Lifecycle Event: {result.get('account_lifecycle_event', 'N/A')}")
            
            # Explain recommendation
            recommendation = result.get('recommendation', '').lower()
            if recommendation == 'allow':
                print(f"   → Low risk - safe to proceed")
            elif recommendation == 'flag':
                print(f"   → Medium risk - additional verification recommended")
            elif recommendation == 'block':
                print(f"   → High risk - consider blocking")
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            if 'trial account' in str(result.get('error', '')).lower():
                print(f"   → Risk assessment may require a production account")
    except Exception as e:
        print(f"❌ FAILED: Risk assessment error")
        print(f"   Error: {e}")


# ===== Main Test Runner =====
def main():
    print("\nWelcome to the Telesign SMS Test Suite!")
    print("This interactive tool helps you test Telesign SMS features.\n")
    print("⚠️  Note: WhatsApp features require WhatsApp Business API access.")
    print("   Contact Telesign to upgrade your account for WhatsApp functionality.\n")
    
    # Test 1: Verify credentials (required)
    if not test_credentials():
        print("\n❌ CRITICAL: Cannot proceed without valid credentials")
        print("   → Please check your .env file")
        input("\nPress Enter to exit...")
        return
    
    # Interactive test menu
    while True:
        print("\n" + "=" * 60)
        print("TELESIGN SMS TEST MENU")
        print("=" * 60)
        print("Available Tests:")
        print("  1. Verify phone number (PhoneID)")
        print("  2. Send SMS message")
        print("  3. Check message delivery status")
        print("  4. Send 2FA verification code")
        print("  5. Verify 2FA code")
        print("  6. Assess phone fraud risk (Intelligence)")
        print("\nBatch Tests:")
        print("  7. Run all SMS tests")
        print("  8. Run complete 2FA workflow")
        print("\n  0. Exit")
        print("=" * 60)
        print("\n💡 TIP: Test 8 demonstrates a complete 2FA implementation!")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            test_phone_verification()
        
        elif choice == "2":
            ref_id = test_send_sms()
            if ref_id and confirm_action("Check message status now"):
                test_message_status(ref_id)
        
        elif choice == "3":
            test_message_status()
        
        elif choice == "4":
            verification_data = test_send_verification_code()
            if verification_data and confirm_action("Verify code now"):
                test_verify_code(verification_data)
        
        elif choice == "5":
            test_verify_code()
        
        elif choice == "6":
            test_assess_risk()
        
        elif choice == "7":
            print("\n🔄 Running all SMS tests...")
            test_phone_verification()
            ref_id = test_send_sms()
            if ref_id:
                test_message_status(ref_id)
            test_assess_risk()
        
        elif choice == "8":
            print("\n🔄 Running complete 2FA workflow...")
            print("This simulates a real 2FA authentication flow:")
            print("  1. Send verification code to user's phone")
            print("  2. User enters the code they received")
            print("  3. Verify the code matches\n")
            
            verification_data = test_send_verification_code()
            if verification_data:
                test_verify_code(verification_data)
        
        elif choice == "0":
            print("\n👋 Thank you for using Telesign SMS Test Suite!")
            print("\n💡 Want WhatsApp? Contact Telesign to upgrade your account:")
            print("   https://portal.telesign.com")
            break
        
        else:
            print("❌ Invalid choice. Please enter a number from the menu.")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()