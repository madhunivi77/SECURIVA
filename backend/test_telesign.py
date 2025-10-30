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
    get_messaging_client
)

print("=" * 60)
print("TELESIGN ENTERPRISE SDK TEST")
print("=" * 60)

load_dotenv()

# ===== Test 1: Verify Credentials =====
def test_credentials():
    print("\n=== Test 1: Verify Credentials ===")
    try:
        client = get_messaging_client()
        print(f"✅ Messaging client created successfully")
        print(f"   Customer ID: {client.customer_id[:10]}...")
        return True
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False


# ===== Test 2: Phone Number Verification =====
def test_phone_verification():
    print("\n=== Test 2: Phone Number Verification ===")
    
    test_number = input("Enter a phone number to verify (E.164 format, e.g., +12345678900): ").strip()
    
    if not test_number:
        print("⚠️  Skipped")
        return
    
    try:
        result = verify_phone_number(test_number)
        print(f"✅ Verification Status: {result['status_code']}")
        print(f"   Phone Type: {result.get('phone_type', 'Unknown')}")
        print(f"   Carrier: {result.get('carrier', 'Unknown')}")
        print(f"   Country: {result.get('country', 'Unknown')}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")


# ===== Test 3: Send SMS =====
def test_send_sms():
    print("\n=== Test 3: Send SMS ===")
    
    phone = input("Enter phone number for SMS test (or press Enter to skip): ").strip()
    if not phone:
        print("⚠️  Skipped")
        return
    
    message = input("Enter message (or press Enter for default): ").strip()
    if not message:
        message = "Hello from Securiva! This is a test SMS."
    
    confirm = input(f"Send SMS to {phone}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Cancelled")
        return
    
    try:
        result = send_sms(phone, message)
        print(f"✅ SMS Sent!")
        print(f"   Status Code: {result['status_code']}")
        print(f"   Reference ID: {result['reference_id']}")
        print(f"   Status: {result['status']}")
        
        if result.get('errors'):
            print(f"   Errors: {result['errors']}")
        
        return result['reference_id']
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")
        return None


# ===== Test 4: Send WhatsApp Message =====
def test_send_whatsapp():
    print("\n=== Test 4: Send WhatsApp Message ===")
    
    phone = input("Enter phone number for WhatsApp test (or press Enter to skip): ").strip()
    if not phone:
        print("⚠️  Skipped")
        return
    
    message = input("Enter message (or press Enter for default): ").strip()
    if not message:
        message = "Hello from Securiva! This is a test WhatsApp message."
    
    confirm = input(f"Send WhatsApp message to {phone}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Cancelled")
        return
    
    try:
        result = send_whatsapp_message(phone, message)
        print(f"✅ WhatsApp Message Sent!")
        print(f"   Status Code: {result['status_code']}")
        print(f"   Reference ID: {result['reference_id']}")
        print(f"   Status: {result['status']}")
        
        if result.get('errors'):
            print(f"   Errors: {result['errors']}")
        
        return result['reference_id']
    except Exception as e:
        print(f"❌ Failed to send WhatsApp: {e}")
        import traceback
        traceback.print_exc()
        return None


# ===== Test 5: Check Message Status =====
def test_message_status(reference_id: str = None):
    print("\n=== Test 5: Check Message Status ===")
    
    if not reference_id:
        reference_id = input("Enter reference ID to check (or press Enter to skip): ").strip()
    
    if not reference_id:
        print("⚠️  Skipped")
        return
    
    try:
        result = get_message_status(reference_id)
        print(f"✅ Status Retrieved!")
        print(f"   Status Code: {result['status_code']}")
        print(f"   Status: {result['status']}")
    except Exception as e:
        print(f"❌ Failed to get status: {e}")


# ===== Main Test Runner =====
def main():
    print("\nRunning Telesign Enterprise SDK tests...\n")
    
    # Test 1: Verify credentials
    if not test_credentials():
        print("\n❌ Cannot proceed without valid credentials")
        input("\nPress Enter to exit...")
        return
    
    # Interactive test menu
    while True:
        print("\n" + "=" * 60)
        print("TELESIGN TEST MENU")
        print("=" * 60)
        print("1. Verify a phone number")
        print("2. Send SMS")
        print("3. Send WhatsApp message")
        print("4. Check message status")
        print("5. Run all tests")
        print("0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            test_phone_verification()
        elif choice == "2":
            ref_id = test_send_sms()
            if ref_id:
                check = input("\nCheck message status? (yes/no): ").strip().lower()
                if check == "yes":
                    test_message_status(ref_id)
        elif choice == "3":
            ref_id = test_send_whatsapp()
            if ref_id:
                check = input("\nCheck message status? (yes/no): ").strip().lower()
                if check == "yes":
                    test_message_status(ref_id)
        elif choice == "4":
            test_message_status()
        elif choice == "5":
            test_phone_verification()
            ref_id = test_send_sms()
            if ref_id:
                test_message_status(ref_id)
            ref_id = test_send_whatsapp()
            if ref_id:
                test_message_status(ref_id)
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()