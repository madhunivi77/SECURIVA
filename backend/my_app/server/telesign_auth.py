"""uv 
Telesign authentication and messaging using the official Enterprise SDK
"""

import os
import base64
import hmac
import hashlib
import json
import random
from email.utils import formatdate
from telesignenterprise.messaging import MessagingClient
from telesignenterprise.phoneid import PhoneIdClient
from telesignenterprise.verify import VerifyClient  #no access without full client yet
from dotenv import load_dotenv
import requests
from .telesign_logging import log_transaction #newly added

load_dotenv()

# Load credentials from environment
CUSTOMER_ID = os.getenv("TELESIGN_CUSTOMER_ID")
API_KEY = os.getenv("TELESIGN_API_KEY")


def random_with_n_digits(n: int) -> str:
    """
    Generate a random number with n digits
    
    Args:
        n: Number of digits
    
    Returns:
        str: Random number as string with exactly n digits
    """
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return str(random.randint(range_start, range_end))


def get_messaging_client() -> MessagingClient:
    """
    Get an authenticated Telesign Messaging client
    
    Returns:
        MessagingClient: Ready-to-use Telesign messaging client
    """
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    
    return MessagingClient(CUSTOMER_ID, API_KEY)


def get_verify_client() -> VerifyClient:
    """
    Get an authenticated Telesign Verify client
    
    Returns:
        VerifyClient: Ready-to-use Telesign verify client
    """
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    
    return VerifyClient(CUSTOMER_ID, API_KEY)


def send_otp_sms(phone_number: str, code_length: int = 5, sender_id: str = None) -> dict:
    """
    Send a one-time passcode (OTP) via SMS using Telesign VerifyClient
    This generates and sends a custom OTP code
    
    Args:
        phone_number: Target phone number (without + prefix for trial accounts)
        code_length: Length of OTP code (default: 5 digits)
        sender_id: Optional sender ID for SMS
    
    Returns:
        dict: Contains reference_id, verify_code, and response details
    
    Example:
        >>> result = send_otp_sms("16027395506", code_length=6)
        >>> print(f"OTP sent! Reference: {result['reference_id']}")
        >>> print(f"Code (for testing): {result['verify_code']}")
    """
    # Generate one-time passcode (OTP) for verification
    verify_code = random_with_n_digits(code_length)
    
    # Instantiate a verification client object
    verify_client = get_verify_client()
    
    # Create the parameters dictionary
    params = {
        'verify_code': verify_code
    }
    
    # Add optional sender ID if provided
    if sender_id:
        params['sender_id'] = sender_id
    
    # Make the request and capture the response
    response = verify_client.sms(phone_number, **params)
    
    # Parse response body
    try:
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
    except (json.JSONDecodeError, AttributeError):
        response_data = {}
    
    # Debug output
    print(f"\nOTP SMS Response:")
    print(f"  HTTP Status: {response.status_code}")
    print(f"  Response Body: {response.body}")
    print(f"  Generated OTP: {verify_code} (DO NOT expose in production!)")
    
    return {
        "status_code": response.status_code,
        "reference_id": response_data.get("reference_id"),
        "verify_code": verify_code,  # Include for testing (remove in production)
        "status": response_data.get("status"),
        "full_response": response_data
    }


def verify_otp_code(original_code: str, user_entered_code: str) -> dict:
    """
    Verify a user-entered OTP code against the original code
    This is a local comparison (not an API call)
    
    Args:
        original_code: The original OTP code that was generated
        user_entered_code: The code entered by the user
    
    Returns:
        dict: Verification result with 'valid' boolean
    
    Example:
        >>> result = verify_otp_code("12345", "12345")
        >>> if result['valid']:
        ...     print("Access granted!")
    """
    is_valid = original_code == user_entered_code.strip()
    
    return {
        "valid": is_valid,
        "message": "Code is correct" if is_valid else "Code is incorrect"
    }


def send_whatsapp_message(phone_number: str, message: str, message_type: str = "ARN") -> dict:
    """
    Send a WhatsApp message using Telesign Enterprise SDK
    
    Args:
        phone_number: Target phone number in E.164 format (e.g., +12345678900)
        message: Message text to send
        message_type: Message type ("ARN" for WhatsApp, "OTP" for SMS, etc.)
    
    Returns:
        dict: Response from Telesign API containing status and reference_id
    
    Example:
        >>> response = send_whatsapp_message("+12345678900", "Hello from Securiva!")
        >>> print(response.json)
        {
            "reference_id": "ABCD1234567890",
            "status": {
                "code": 290,
                "description": "Message in progress"
            }
        }
    """
    client = get_messaging_client()
    
    # The SDK handles all authentication automatically
    response = client.message(
        phone_number=phone_number,
        message=message,
        message_type=message_type
    )
    
    result = {
        "status_code": response.status_code,
        "reference_id": response.json.get("reference_id"),
        "status": response.json.get("status"),
        "errors": response.json.get("errors", []),
        "full_response": response.json
    }
    
    # Log the transaction
    log_transaction(
        transaction_type="WhatsApp" if message_type == "ARN" else "SMS",
        phone_number=phone_number,
        status_code=result['status_code'],
        reference_id=result.get('reference_id'),
        message=message,
        response_data=result.get('full_response'),
        error=result.get('errors')
    )
    
    return result


def send_sms(phone_number: str, message: str) -> dict:
    """
    Send an SMS message using Telesign
    
    Args:
        phone_number: Target phone number in E.164 format
        message: SMS message text
    
    Returns:
        dict: Response from Telesign API
    """
    result = send_whatsapp_message(phone_number, message, message_type="OTP")
    
    # Log the transaction
    log_transaction(
        transaction_type="SMS",
        phone_number=phone_number,
        status_code=result['status_code'],
        reference_id=result.get('reference_id'),
        message=message,
        response_data=result.get('full_response'),
        error=result.get('errors')
    )
    
    return result


def verify_phone_number(phone_number: str) -> dict:
    """
    Verify a phone number using Telesign PhoneID SDK
    Following Telesign's official example pattern
    
    Args:
        phone_number: Phone number to verify in E.164 format (e.g., +16027395506)
    
    Returns:
        dict: Verification result with phone number details
    """
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    
    # Instantiate a Phone ID client object
    client = PhoneIdClient(CUSTOMER_ID, API_KEY)
    
    # Add the payload (matching Telesign's example)
    payload = {  
        "addons": {
            "contact": {}
        },
        "phone_number": phone_number
    }
    
    # Make the request and capture the response
    response = client.phoneid(**payload)
    
    # Debug output (matching Telesign's example)
    print(f"\nPhoneID Response:\n{response.body}\n")
    
    # Parse response - response.body might be string or dict
    try:
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
    except (json.JSONDecodeError, AttributeError):
        response_data = {}
    
    if response.status_code == 200:
        return {
            "status_code": response.status_code,
            "phone_type": response_data.get("phone_type", {}).get("description", "Unknown"),
            "carrier": response_data.get("numbering", {}).get("original", {}).get("carrier", {}).get("name", "Unknown"),
            "country": response_data.get("location", {}).get("country", {}).get("name", "Unknown"),
            "full_response": response_data
        }
    else:
        return {
            "status_code": response.status_code,
            "phone_type": "Error",
            "carrier": "N/A",
            "country": "N/A",
            "error": response.body,
            "full_response": response_data
        }


def get_message_status(reference_id: str) -> dict:
    """
    Check the delivery status of a sent message
    
    Args:
        reference_id: Reference ID returned when message was sent
    
    Returns:
        dict: Current status of the message
    """
    client = get_messaging_client()
    response = client.status(reference_id)
    
    return {
        "status_code": response.status_code,
        "status": response.json.get("status"),
        "full_response": response.json
    }


# Alias for backward compatibility
def load_credentials() -> tuple[str, str]:
    """
    Load Telesign credentials (legacy function for compatibility)
    
    Returns:
        tuple: (customer_id, api_key)
    """
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return CUSTOMER_ID, API_KEY


def send_verification_code(phone_number: str, code_length: int = 6) -> dict:
    """
    Send a 2FA verification code (legacy method using REST API)
    
    Note: Consider using send_otp_sms() instead for better OTP handling
    
    Returns:
        dict: Contains reference_id for later verification
    """
    timestamp = formatdate(timeval=None, localtime=False, usegmt=True)
    resource = "/v1/verify/sms"
    
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode('utf-8'),
            f"POST\napplication/json\n\nx-ts-date:{timestamp}\n{resource}".encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        "Authorization": f"TSA {CUSTOMER_ID}:{signature}",
        "x-ts-date": timestamp,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone_number": phone_number,
        "verify_code": None,  # Telesign generates it
        "template": f"Your Securiva verification code is: $$CODE$$"
    }
    
    response = requests.post(f"https://rest-api.telesign.com{resource}", json=payload, headers=headers)
    response_json = response.json()
    
    return {
        "status_code": response.status_code,
        "reference_id": response_json.get("reference_id"),
        "verify_code": response_json.get("verify", {}).get("code_state"),  # Don't expose actual code
        "full_response": response_json
    }


def verify_code(reference_id: str, user_code: str) -> dict:
    """
    Verify a user-entered code against Telesign's stored code (legacy method)
    
    Args:
        reference_id: From send_verification_code response
        user_code: Code entered by user
    
    Returns:
        dict: Verification result (valid/invalid)
    """
    timestamp = formatdate(timeval=None, localtime=False, usegmt=True)
    resource = f"/v1/verify/{reference_id}"
    
    # FIXED: Use POST instead of GET
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode('utf-8'),
            f"POST\napplication/json\n\nx-ts-date:{timestamp}\n{resource}".encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        "Authorization": f"TSA {CUSTOMER_ID}:{signature}",
        "x-ts-date": timestamp,
        "Content-Type": "application/json"
    }
    
    # Send code in request body, not query params
    payload = {"verify_code": user_code}
    
    # FIXED: Use POST request
    response = requests.post(
        f"https://rest-api.telesign.com{resource}", 
        json=payload, 
        headers=headers
    )
    response_json = response.json()
    
    return {
        "status_code": response.status_code,
        "valid": response_json.get("verify", {}).get("code_state") == "VALID",
        "full_response": response_json
    }


def assess_phone_risk(phone_number: str) -> dict:
    """
    Get fraud risk assessment for a phone number using PhoneID Score
    Useful for detecting suspicious registrations
    
    Args:
        phone_number: Phone number to assess in E.164 format
    
    Returns:
        dict: Risk assessment details
    """
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    
    client = PhoneIdClient(CUSTOMER_ID, API_KEY)
    
    # Use SDK method for PhoneID Score
    payload = {
        "phone_number": phone_number,
        "account_lifecycle_event": "create"  # Options: create, sign-in, transact, update, delete
    }
    
    try:
        response = client.score(**payload)
        
        # Parse response body
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
        
        print(f"\nPhoneID Score Response:\n{response.body}\n")
        
        if response.status_code == 200:
            return {
                "status_code": response.status_code,
                "risk_level": response_data.get("risk", {}).get("level"),  # low/medium/high
                "risk_score": response_data.get("risk", {}).get("score"),  # 0-1000
                "recommendation": response_data.get("risk", {}).get("recommendation"),  # allow/flag/block
                "full_response": response_data
            }
        else:
            return {
                "status_code": response.status_code,
                "risk_level": "Error",
                "risk_score": None,
                "recommendation": "Error",
                "error": response.body,
                "full_response": response_data
            }
    except Exception as e:
        return {
            "status_code": 500,
            "risk_level": "Error",
            "risk_score": None,
            "recommendation": "Error",
            "error": str(e),
            "full_response": {}
        }


def send_whatsapp_template(phone_number: str, template_id: str, parameters: list = None) -> dict:
    """
    Send a pre-approved WhatsApp template message
    
    Args:
        phone_number: Target phone number in E.164 format
        template_id: WhatsApp Business template ID
        parameters: List of parameter values for template placeholders
    
    Returns:
        dict: Response from Telesign API
    """
    timestamp = formatdate(timeval=None, localtime=False, usegmt=True)
    resource = "/v1/messaging"
    
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode('utf-8'),
            f"POST\napplication/json\n\nx-ts-date:{timestamp}\n{resource}".encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        "Authorization": f"TSA {CUSTOMER_ID}:{signature}",
        "x-ts-date": timestamp,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone_number": phone_number,
        "message_type": "ARN",
        "template": template_id,
        "template_params": parameters or []
    }
    
    response = requests.post(f"https://rest-api.telesign.com{resource}", json=payload, headers=headers)
    response_json = response.json()
    
    return {
        "status_code": response.status_code,
        "reference_id": response_json.get("reference_id"),
        "status": response_json.get("status"),
        "full_response": response_json
    }


def send_whatsapp_media(phone_number: str, media_url: str, caption: str = "", media_type: str = "image") -> dict:
    """
    Send WhatsApp media message (image, video, document)
    
    Args:
        phone_number: Target phone number in E.164 format
        media_url: Public URL of the media file
        caption: Optional caption for the media
        media_type: Type of media (image, video, document, audio)
    
    Returns:
        dict: Response from Telesign API
    """
    timestamp = formatdate(timeval=None, localtime=False, usegmt=True)
    resource = "/v1/messaging"
    
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode('utf-8'),
            f"POST\napplication/json\n\nx-ts-date:{timestamp}\n{resource}".encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        "Authorization": f"TSA {CUSTOMER_ID}:{signature}",
        "x-ts-date": timestamp,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone_number": phone_number,
        "message_type": "ARN",
        "media": {
            "type": media_type,
            "url": media_url,
            "caption": caption
        }
    }
    
    response = requests.post(f"https://rest-api.telesign.com{resource}", json=payload, headers=headers)
    response_json = response.json()
    
    return {
        "status_code": response.status_code,
        "reference_id": response_json.get("reference_id"),
        "status": response_json.get("status"),
        "full_response": response_json
    }


def send_whatsapp_buttons(phone_number: str, body_text: str, buttons: list[dict]) -> dict:
    """
    Send WhatsApp interactive button message
    
    Args:
        phone_number: Target phone number in E.164 format
        body_text: Main message text
        buttons: List of button objects [{"id": "1", "title": "Option 1"}, ...]
    
    Returns:
        dict: Response from Telesign API
    """
    timestamp = formatdate(timeval=None, localtime=False, usegmt=True)
    resource = "/v1/messaging"
    
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode('utf-8'),
            f"POST\napplication/json\n\nx-ts-date:{timestamp}\n{resource}".encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        "Authorization": f"TSA {CUSTOMER_ID}:{signature}",
        "x-ts-date": timestamp,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone_number": phone_number,
        "message_type": "ARN",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": buttons}
        }
    }
    
    response = requests.post(f"https://rest-api.telesign.com{resource}", json=payload, headers=headers)
    response_json = response.json()
    
    return {
        "status_code": response.status_code,
        "reference_id": response_json.get("reference_id"),
        "status": response_json.get("status"),
        "full_response": response_json
    }