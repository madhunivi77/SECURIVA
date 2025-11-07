"""
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
from telesignenterprise.verify import VerifyClient
from telesign.score import ScoreClient
from telesign.util import random_with_n_digits
from dotenv import load_dotenv
import requests

load_dotenv()

# Load credentials from environment
CUSTOMER_ID = os.getenv("TELESIGN_CUSTOMER_ID")
API_KEY = os.getenv("TELESIGN_API_KEY")
SENDER_ID = os.getenv("TELESIGN_SENDER_ID", "2623984079")


def get_messaging_client() -> MessagingClient:
    """Get an authenticated Telesign Messaging client"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return MessagingClient(CUSTOMER_ID, API_KEY)


def get_verify_client() -> VerifyClient:
    """Get an authenticated Telesign Verify client"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return VerifyClient(CUSTOMER_ID, API_KEY)


def get_score_client() -> ScoreClient:
    """Get an authenticated Telesign Score (Intelligence) client"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return ScoreClient(CUSTOMER_ID, API_KEY)


def send_sms(phone_number: str, message: str) -> dict:
    """
    Send an SMS message using Telesign - FOLLOWING TELESIGN'S EXAMPLE
    
    Args:
        phone_number: Target phone number (without + prefix for trial)
        message: SMS message text
    
    Returns:
        dict: Response from Telesign API
    """
    # Set message type and sender ID (from Telesign example)
    message_type = "OTP"
    #sender_id = SENDER_ID
    
    # Instantiate a messaging client object (from Telesign example)
    messaging = get_messaging_client()
    
    # Make the request and capture the response (from Telesign example)
    response = messaging.message(phone_number, message, message_type)
    
    # Display the response body in the console for debugging purposes
    print(f"\nResponse:\n{response.body}\n")
    
    # Parse response
    try:
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
    except (json.JSONDecodeError, AttributeError):
        response_data = {}
    
    return {
        "status_code": response.status_code,
        "reference_id": response_data.get("reference_id"),
        "status": response_data.get("status"),
        "errors": response_data.get("errors", []),
        "full_response": response_data
    }


def send_whatsapp_message(phone_number: str, message: str) -> dict:
    """
    Send a WhatsApp message (when account is upgraded)
    """
    message_type = "ARN"  # ARN for WhatsApp
    sender_id = SENDER_ID
    
    messaging = get_messaging_client()
    response = messaging.message(phone_number, message, message_type, **{"sender_id": sender_id})
    
    print(f"\nResponse:\n{response.body}\n")
    
    try:
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
    except (json.JSONDecodeError, AttributeError):
        response_data = {}
    
    return {
        "status_code": response.status_code,
        "reference_id": response_data.get("reference_id"),
        "status": response_data.get("status"),
        "errors": response_data.get("errors", []),
        "full_response": response_data
    }


def verify_phone_number(phone_number: str) -> dict:
    """Verify a phone number using Telesign PhoneID SDK"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    
    client = PhoneIdClient(CUSTOMER_ID, API_KEY)
    
    payload = {  
        "addons": {"contact": {}},
        "phone_number": phone_number
    }
    
    response = client.phoneid(**payload)
    print(f"\nPhoneID Response:\n{response.body}\n")
    
    try:
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
    except (json.JSONDecodeError, AttributeError):
        response_data = {}
    
    if response.status_code == 200:
        # Extract detailed information from the response
        location = response_data.get("location", {})
        numbering = response_data.get("numbering", {})
        contact = response_data.get("contact", {})
        
        return {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "phone_type": response_data.get("phone_type", {}).get("description", "Unknown"),
            "carrier": response_data.get("carrier", {}).get("name", "Unknown"),
            "country": location.get("country", {}).get("name", "Unknown"),
            "country_code": location.get("country", {}).get("iso2", ""),
            "state": location.get("state", ""),
            "city": location.get("city", ""),
            "zip": location.get("zip", ""),
            "time_zone": location.get("time_zone", {}).get("name", ""),
            "formatted_number": numbering.get("original", {}).get("complete_phone_number", ""),
            "blocked": response_data.get("blocklisting", {}).get("blocked", False),
            "contact_info": {
                "first_name": contact.get("first_name", ""),
                "last_name": contact.get("last_name", ""),
                "email": contact.get("email_address", ""),
                "address": contact.get("address1", ""),
                "city": contact.get("city", ""),
                "state": contact.get("state_province", ""),
                "zip": contact.get("zip_postal_code", "")
            },
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
    """Check the delivery status of a sent message"""
    client = get_messaging_client()
    response = client.status(reference_id)
    
    return {
        "status_code": response.status_code,
        "status": response.json.get("status"),
        "full_response": response.json
    }


def send_verification_code(phone_number: str, code_length: int = 5) -> dict:
    """
    Send a 2FA verification code using Telesign Verify SDK
    
    Args:
        phone_number: Target phone number (without + prefix for trial)
        code_length: Length of verification code (default: 5)
    
    Returns:
        dict: Response with reference_id and generated code (for testing)
    """
    # Generate one-time passcode (OTP) for verification
    verify_code = random_with_n_digits(code_length)
    
    # Instantiate a verification client object
    verify = get_verify_client()
    
    # Create the parameters dictionary
    params = {
        'verify_code': verify_code,
        'sender_id': SENDER_ID
    }
    
    # Make the request and capture the response
    response = verify.sms(phone_number, **params)
    
    # Display the response in the console for debugging purposes
    print(f"Response HTTP status: {response.status_code}")
    print(f"Response body: {response.body}")
    
    # Parse response
    try:
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
    except (json.JSONDecodeError, AttributeError):
        response_data = {}
    
    return {
        "status_code": response.status_code,
        "reference_id": response_data.get("reference_id"),
        "verify_code": verify_code,  # Include for testing purposes
        "status": response_data.get("status"),
        "errors": response_data.get("errors", []),
        "full_response": response_data
    }


def verify_code(reference_id: str, user_code: str, original_code: str = None) -> dict:
    """
    Verify a user-entered code
    
    Args:
        reference_id: Reference ID from send_verification_code
        user_code: Code entered by user
        original_code: Original generated code (for local verification)
    
    Returns:
        dict: Verification result
    """
    # Strip whitespace from user input
    user_code = user_code.strip()
    
    # Determine if the codes match
    if original_code:
        is_valid = (original_code == user_code)
        
        return {
            "status_code": 200,
            "valid": is_valid,
            "message": "Your code is correct." if is_valid else "Your code is incorrect.",
            "reference_id": reference_id
        }
    else:
        return {
            "status_code": 400,
            "valid": False,
            "message": "Original verification code not provided",
            "reference_id": reference_id
        }


def assess_phone_risk(phone_number: str, account_lifecycle_event: str = "create") -> dict:
    """
    Get fraud risk assessment for a phone number using Telesign Intelligence (Score API)
    
    Args:
        phone_number: Phone number to assess
        account_lifecycle_event: Stage of account lifecycle (create, sign-in, transact, update)
    
    Returns:
        dict: Risk assessment results
    """
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    
    # Instantiate an Intelligence client object
    intelligence = get_score_client()
    
    try:
        # Make the request and capture the response
        # The request_risk_insights flag is needed to use the latest version of Intelligence
        response = intelligence.score(phone_number, account_lifecycle_event, request_risk_insights="true")
        
        # Display the response body in the console for debugging purposes
        print(f"\nResponse:\n{response.body}\n")
        
        # Parse response
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
        
        if response.status_code == 200:
            # Extract risk information
            risk_data = response_data.get("risk", {})
            phone_type_data = response_data.get("phone_type", {})
            numbering_data = response_data.get("numbering", {})
            
            return {
                "status_code": response.status_code,
                "reference_id": response_data.get("reference_id"),
                "risk_level": risk_data.get("level"),
                "risk_score": risk_data.get("score"),
                "recommendation": risk_data.get("recommendation"),
                "phone_type": phone_type_data.get("description", "Unknown"),
                "carrier": numbering_data.get("original", {}).get("carrier", {}).get("name", "Unknown"),
                "account_lifecycle_event": account_lifecycle_event,
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


# Placeholder functions for WhatsApp features (require upgraded account)
def send_whatsapp_template(phone_number: str, template_id: str, parameters: list = None) -> dict:
    """Send WhatsApp template message (requires WhatsApp Business API)"""
    return {
        "status_code": 501,
        "error": "WhatsApp templates require WhatsApp Business API access. Contact Telesign to upgrade."
    }


def send_whatsapp_media(phone_number: str, media_url: str, caption: str = "", media_type: str = "image") -> dict:
    """Send WhatsApp media message (requires WhatsApp Business API)"""
    return {
        "status_code": 501,
        "error": "WhatsApp media requires WhatsApp Business API access. Contact Telesign to upgrade."
    }


def send_whatsapp_buttons(phone_number: str, body_text: str, buttons: list) -> dict:
    """Send WhatsApp interactive buttons (requires WhatsApp Business API)"""
    return {
        "status_code": 501,
        "error": "WhatsApp buttons require WhatsApp Business API access. Contact Telesign to upgrade."
    }


# Keep backward compatibility
def load_credentials() -> tuple[str, str]:
    """Load Telesign credentials"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return CUSTOMER_ID, API_KEY