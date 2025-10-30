"""uv 
Telesign authentication and messaging using the official Enterprise SDK
"""

import os
import base64
import hmac
import hashlib
from email.utils import formatdate
from telesignenterprise.messaging import MessagingClient
from dotenv import load_dotenv
import requests

load_dotenv()

# Load credentials from environment
CUSTOMER_ID = os.getenv("TELESIGN_CUSTOMER_ID")
API_KEY = os.getenv("TELESIGN_API_KEY")


def get_messaging_client() -> MessagingClient:
    """
    Get an authenticated Telesign Messaging client
    
    Returns:
        MessagingClient: Ready-to-use Telesign messaging client
    """
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    
    return MessagingClient(CUSTOMER_ID, API_KEY)


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
    
    return {
        "status_code": response.status_code,
        "reference_id": response.json.get("reference_id"),
        "status": response.json.get("status"),
        "errors": response.json.get("errors", []),
        "full_response": response.json
    }


def send_sms(phone_number: str, message: str) -> dict:
    """
    Send an SMS message using Telesign
    
    Args:
        phone_number: Target phone number in E.164 format
        message: SMS message text
    
    Returns:
        dict: Response from Telesign API
    """
    return send_whatsapp_message(phone_number, message, message_type="OTP")


def verify_phone_number(phone_number: str) -> dict:
    """
    Verify a phone number using Telesign PhoneID
    
    Args:
        phone_number: Phone number to verify in E.164 format
    
    Returns:
        dict: Verification result with phone number details
    """
    # Manual REST call with proper authentication
    timestamp = formatdate(timeval=None, localtime=False, usegmt=True)
    resource = f"/v1/phoneid/standard/{phone_number}"
    string_to_sign = f"GET\n\n\nx-ts-date:{timestamp}\n{resource}"
    
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        "Authorization": f"TSA {CUSTOMER_ID}:{signature}",
        "x-ts-date": timestamp
    }
    
    # Make the API call
    url = f"https://rest-api.telesign.com{resource}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        response_json = response.json()
        return {
            "status_code": response.status_code,
            "phone_type": response_json.get("phone_type", {}).get("description", "Unknown"),
            "carrier": response_json.get("numbering", {}).get("original", {}).get("carrier", {}).get("name", "Unknown"),
            "country": response_json.get("location", {}).get("country", {}).get("name", "Unknown"),
            "full_response": response_json
        }
    else:
        return {
            "status_code": response.status_code,
            "phone_type": "Error",
            "carrier": "N/A",
            "country": "N/A",
            "error": response.text,
            "full_response": {}
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
    Send a 2FA verification code
    
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
    Verify a user-entered code against Telesign's stored code
    
    Args:
        reference_id: From send_verification_code response
        user_code: Code entered by user
    
    Returns:
        dict: Verification result (valid/invalid)
    """
    timestamp = formatdate(timeval=None, localtime=False, usegmt=True)
    resource = f"/v1/verify/{reference_id}"
    
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode('utf-8'),
            f"GET\n\n\nx-ts-date:{timestamp}\n{resource}".encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        "Authorization": f"TSA {CUSTOMER_ID}:{signature}",
        "x-ts-date": timestamp
    }
    
    params = {"verify_code": user_code}
    response = requests.get(f"https://rest-api.telesign.com{resource}", headers=headers, params=params)
    response_json = response.json()
    
    return {
        "status_code": response.status_code,
        "valid": response_json.get("verify", {}).get("code_state") == "VALID",
        "full_response": response_json
    }

def assess_phone_risk(phone_number: str) -> dict:
    """
    Get fraud risk assessment for a phone number
    Useful for detecting suspicious registrations
    """
    timestamp = formatdate(timeval=None, localtime=False, usegmt=True)
    resource = f"/v1/phoneid/score/{phone_number}"
    
    signature = base64.b64encode(
        hmac.new(
            API_KEY.encode('utf-8'),
            f"GET\n\n\nx-ts-date:{timestamp}\n{resource}".encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    headers = {
        "Authorization": f"TSA {CUSTOMER_ID}:{signature}",
        "x-ts-date": timestamp
    }
    
    response = requests.get(f"https://rest-api.telesign.com{resource}", headers=headers)
    response_json = response.json()
    
    return {
        "status_code": response.status_code,
        "risk_level": response_json.get("risk", {}).get("level"),  # low/medium/high
        "risk_score": response_json.get("risk", {}).get("score"),  # 0-1000
        "recommendation": response_json.get("risk", {}).get("recommendation"),
        "full_response": response_json
    }