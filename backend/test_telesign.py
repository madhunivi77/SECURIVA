"""
Test file for Telesign WhatsApp functionality using the Enterprise SDK
"""

import os
from dotenv import load_dotenv
from my_app.server.telesign_auth import (
    send_whatsapp_message,
    send_sms,
    verify_phone_number,
    get_message_status,
    get_messaging_client,
    send_verification_code,
    verify_code,
    assess_phone_risk,
    send_whatsapp_template,
    send_whatsapp_media,
    send_whatsapp_buttons
)

print("=" * 60)
print("TELESIGN ENTERPRISE SDK TEST")
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
    print("  • Line type and status")
    
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


# ===== Test 4: Send WhatsApp Message =====
def test_send_whatsapp():
    print("\n" + "=" * 60)
    print("TEST 4: Send WhatsApp Message")
    print("=" * 60)
    print("This test sends a WhatsApp text message.")
    print("Note: The recipient must have WhatsApp installed.")
    
    phone = get_phone_input("Enter destination phone number for WhatsApp")
    
    if not phone:
        print("⚠️  Test skipped")
        return None
    
    print("\nEnter your WhatsApp message:")
    print("  (Press Enter for default message)")
    message = input("Message: ").strip()
    if not message:
        message = "Hello from Securiva! This is a test WhatsApp message."
        print(f"  → Using default: '{message}'")
    
    if not confirm_action(f"Send WhatsApp message to {phone}"):
        print("❌ Test cancelled")
        return None
    
    try:
        print("\n🔄 Sending WhatsApp message...")
        result = send_whatsapp_message(phone, message)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: WhatsApp message sent")
            print(f"   Reference ID: {result['reference_id']}")
            print(f"   Status: {result['status']}")
            return result['reference_id']
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   Errors: {result.get('errors', [])}")
            return None
    except Exception as e:
        print(f"❌ FAILED: Could not send WhatsApp message")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# ===== Test 5: Check Message Status =====
def test_message_status(reference_id: str = None):
    print("\n" + "=" * 60)
    print("TEST 5: Check Message Delivery Status")
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


# ===== Test 6: Send 2FA Verification Code =====
def test_send_verification_code():
    print("\n" + "=" * 60)
    print("TEST 6: Send 2FA Verification Code")
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
            print(f"   → The recipient should receive a code via SMS")
            print(f"   → Use Test 7 to verify the code they received")
            return result['reference_id']
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            return None
    except Exception as e:
        print(f"❌ FAILED: Could not send verification code")
        print(f"   Error: {e}")
        return None


# ===== Test 7: Verify 2FA Code =====
def test_verify_code(reference_id: str = None):
    print("\n" + "=" * 60)
    print("TEST 7: Verify 2FA Code")
    print("=" * 60)
    print("This test verifies a code entered by the user against Telesign's stored code.")
    
    if not reference_id:
        print("\nEnter the Reference ID from the verification code message:")
        print("  (Press Enter to skip)")
        reference_id = input("Reference ID: ").strip()
    
    if not reference_id:
        print("⚠️  Test skipped")
        return
    
    print("\nEnter the verification code received:")
    user_code = input("Code: ").strip()
    
    if not user_code:
        print("❌ Code is required")
        return
    
    try:
        print("\n🔄 Verifying code...")
        result = verify_code(reference_id, user_code)
        
        if result['status_code'] == 200:
            if result.get('valid'):
                print(f"✅ SUCCESS: Code is VALID")
            else:
                print(f"❌ FAILED: Code is INVALID")
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
    except Exception as e:
        print(f"❌ FAILED: Could not verify code")
        print(f"   Error: {e}")


# ===== Test 8: Assess Phone Risk =====
def test_assess_risk():
    print("\n" + "=" * 60)
    print("TEST 8: Assess Phone Number Risk")
    print("=" * 60)
    print("This test performs fraud risk assessment on a phone number.")
    print("Useful for detecting suspicious registrations or transactions.")
    
    phone = get_phone_input("Enter phone number to assess")
    
    if not phone:
        print("⚠️  Test skipped")
        return
    
    try:
        print("\n🔄 Assessing phone risk...")
        result = assess_phone_risk(phone)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: Risk assessment complete")
            print(f"   Risk Level: {result.get('risk_level', 'Unknown')}")
            print(f"   Risk Score: {result.get('risk_score', 'N/A')} (0-1000 scale)")
            print(f"   Recommendation: {result.get('recommendation', 'Unknown')}")
            
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


# ===== Test 9: Send WhatsApp Template =====
def test_send_template():
    print("\n" + "=" * 60)
    print("TEST 9: Send WhatsApp Template Message")
    print("=" * 60)
    print("This test sends a pre-approved WhatsApp template message.")
    print("Note: Templates must be created and approved in your WhatsApp Business account.")
    
    phone = get_phone_input("Enter destination phone number")
    
    if not phone:
        print("⚠️  Test skipped")
        return None
    
    print("\nEnter the WhatsApp template ID:")
    print("  (This is the name/ID from your approved templates)")
    template_id = input("Template ID: ").strip()
    
    if not template_id:
        print("❌ Template ID is required")
        return None
    
    print("\nEnter template parameters (comma-separated, or press Enter for none):")
    print("  Example: John,123456,30")
    params_input = input("Parameters: ").strip()
    parameters = [p.strip() for p in params_input.split(',')] if params_input else []
    
    if not confirm_action(f"Send template '{template_id}' to {phone}"):
        print("❌ Test cancelled")
        return None
    
    try:
        print("\n🔄 Sending template message...")
        result = send_whatsapp_template(phone, template_id, parameters)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: Template message sent")
            print(f"   Reference ID: {result['reference_id']}")
            return result['reference_id']
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   → Make sure the template is approved in your WhatsApp Business account")
            return None
    except Exception as e:
        print(f"❌ FAILED: Could not send template")
        print(f"   Error: {e}")
        return None


# ===== Test 10: Send WhatsApp Media =====
def test_send_media():
    print("\n" + "=" * 60)
    print("TEST 10: Send WhatsApp Media Message")
    print("=" * 60)
    print("This test sends a media file (image, video, document) via WhatsApp.")
    print("Note: The media must be hosted at a publicly accessible URL.")
    
    phone = get_phone_input("Enter destination phone number")
    
    if not phone:
        print("⚠️  Test skipped")
        return None
    
    print("\nEnter the public URL of the media file:")
    print("  Example: https://example.com/image.jpg")
    media_url = input("Media URL: ").strip()
    
    if not media_url:
        print("❌ Media URL is required")
        return None
    
    print("\nSelect media type:")
    print("  1. Image (jpg, png, gif)")
    print("  2. Video (mp4, 3gp)")
    print("  3. Document (pdf, doc, xls)")
    print("  4. Audio (mp3, ogg)")
    media_choice = input("Choice (1-4): ").strip()
    
    media_type_map = {'1': 'image', '2': 'video', '3': 'document', '4': 'audio'}
    media_type = media_type_map.get(media_choice, 'image')
    
    print(f"\nEnter optional caption (or press Enter to skip):")
    caption = input("Caption: ").strip()
    
    if not confirm_action(f"Send {media_type} to {phone}"):
        print("❌ Test cancelled")
        return None
    
    try:
        print("\n🔄 Sending media message...")
        result = send_whatsapp_media(phone, media_url, caption, media_type)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: Media message sent")
            print(f"   Reference ID: {result['reference_id']}")
            return result['reference_id']
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   → Ensure the URL is publicly accessible and the file format is supported")
            return None
    except Exception as e:
        print(f"❌ FAILED: Could not send media")
        print(f"   Error: {e}")
        return None


# ===== Test 11: Send WhatsApp Buttons =====
def test_send_buttons():
    print("\n" + "=" * 60)
    print("TEST 11: Send WhatsApp Interactive Buttons")
    print("=" * 60)
    print("This test sends a WhatsApp message with interactive button options.")
    
    phone = get_phone_input("Enter destination phone number")
    
    if not phone:
        print("⚠️  Test skipped")
        return None
    
    print("\nEnter the message text:")
    body_text = input("Message: ").strip()
    
    if not body_text:
        body_text = "Please choose an option:"
        print(f"  → Using default: '{body_text}'")
    
    # Create sample buttons
    print("\nCreating sample buttons (Yes/No)...")
    buttons = [
        {"id": "1", "title": "Yes"},
        {"id": "2", "title": "No"}
    ]
    print(f"  Buttons: {[b['title'] for b in buttons]}")
    
    if not confirm_action(f"Send button message to {phone}"):
        print("❌ Test cancelled")
        return None
    
    try:
        print("\n🔄 Sending button message...")
        result = send_whatsapp_buttons(phone, body_text, buttons)
        
        if result['status_code'] == 200:
            print(f"✅ SUCCESS: Button message sent")
            print(f"   Reference ID: {result['reference_id']}")
            return result['reference_id']
        else:
            print(f"⚠️  Status Code: {result['status_code']}")
            print(f"   → Interactive messages may require WhatsApp Business API approval")
            return None
    except Exception as e:
        print(f"❌ FAILED: Could not send buttons")
        print(f"   Error: {e}")
        return None


# ===== Main Test Runner =====
def main():
    print("\nWelcome to the Telesign Enterprise SDK Test Suite!")
    print("This interactive tool helps you test all Telesign/WhatsApp features.\n")
    
    # Test 1: Verify credentials (required)
    if not test_credentials():
        print("\n❌ CRITICAL: Cannot proceed without valid credentials")
        print("   → Please check your .env file")
        input("\nPress Enter to exit...")
        return
    
    # Interactive test menu
    while True:
        print("\n" + "=" * 60)
        print("TELESIGN TEST MENU")
        print("=" * 60)
        print("Basic Tests:")
        print("  1.  Verify phone number (PhoneID)")
        print("  2.  Send SMS")
        print("  3.  Send WhatsApp message")
        print("  4.  Check message status")
        print("\nAdvanced Tests:")
        print("  5.  Send 2FA verification code")
        print("  6.  Verify 2FA code")
        print("  7.  Assess phone fraud risk")
        print("  8.  Send WhatsApp template")
        print("  9.  Send WhatsApp media (image/video/doc)")
        print("  10. Send WhatsApp interactive buttons")
        print("\nBatch Tests:")
        print("  11. Run all basic tests")
        print("  12. Run all advanced tests")
        print("\n  0.  Exit")
        print("=" * 60)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            test_phone_verification()
        
        elif choice == "2":
            ref_id = test_send_sms()
            if ref_id and confirm_action("Check message status now"):
                test_message_status(ref_id)
        
        elif choice == "3":
            ref_id = test_send_whatsapp()
            if ref_id and confirm_action("Check message status now"):
                test_message_status(ref_id)
        
        elif choice == "4":
            test_message_status()
        
        elif choice == "5":
            ref_id = test_send_verification_code()
            if ref_id and confirm_action("Verify code now"):
                test_verify_code(ref_id)
        
        elif choice == "6":
            test_verify_code()
        
        elif choice == "7":
            test_assess_risk()
        
        elif choice == "8":
            ref_id = test_send_template()
            if ref_id and confirm_action("Check message status now"):
                test_message_status(ref_id)
        
        elif choice == "9":
            ref_id = test_send_media()
            if ref_id and confirm_action("Check message status now"):
                test_message_status(ref_id)
        
        elif choice == "10":
            ref_id = test_send_buttons()
            if ref_id and confirm_action("Check message status now"):
                test_message_status(ref_id)
        
        elif choice == "11":
            print("\n🔄 Running all basic tests...")
            test_phone_verification()
            ref_id = test_send_sms()
            if ref_id:
                test_message_status(ref_id)
            ref_id = test_send_whatsapp()
            if ref_id:
                test_message_status(ref_id)
        
        elif choice == "12":
            print("\n🔄 Running all advanced tests...")
            ref_id = test_send_verification_code()
            if ref_id:
                test_verify_code(ref_id)
            test_assess_risk()
            test_send_template()
        
        elif choice == "0":
            print("\n👋 Thank you for using Telesign Test Suite!")
            break
        
        else:
            print("❌ Invalid choice. Please enter a number from the menu.")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()