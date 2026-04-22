"""
TeleSign authentication and messaging using the Self-Service SDK
Supports SMS, Voice, PhoneID, Verify, and Intelligence (Score) APIs

Self-Service Account Documentation:
https://developer.telesign.com/enterprise/docs/messaging-api
"""

import os
import base64
import hmac
import hashlib
import json
import random
import time
from email.utils import formatdate
from typing import Optional, Dict, List, Any
from pathlib import Path

# Use standard TeleSign SDK for messaging, voice, phoneid, score
from telesign.messaging import MessagingClient
from telesign.phoneid import PhoneIdClient
from telesign.score import ScoreClient
from telesign.voice import VoiceClient
from telesign.util import random_with_n_digits

# Use Enterprise SDK for VerifyClient (cheaper verification tokens)
from telesignenterprise.verify import VerifyClient

from dotenv import load_dotenv

# Import logging utility
from .tool_logger import log_tool_call

load_dotenv()

# Load credentials from environment
CUSTOMER_ID = os.getenv("TELESIGN_CUSTOMER_ID")
API_KEY = os.getenv("TELESIGN_API_KEY")
SENDER_ID = os.getenv("TELESIGN_SENDER_ID", "")
ACCOUNT_TYPE = "self-service"  # Set to "self-service" for standard accounts


def get_messaging_client() -> MessagingClient:
    """Get an authenticated TeleSign Messaging client for self-service account"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return MessagingClient(CUSTOMER_ID, API_KEY)


def get_voice_client() -> VoiceClient:
    """Get an authenticated TeleSign Voice client"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return VoiceClient(CUSTOMER_ID, API_KEY)


def get_verify_client() -> VerifyClient:
    """Get an authenticated TeleSign Verify client (Enterprise SDK - cheaper verification tokens)"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return VerifyClient(CUSTOMER_ID, API_KEY)


def get_phoneid_client() -> PhoneIdClient:
    """Get an authenticated TeleSign PhoneID client"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return PhoneIdClient(CUSTOMER_ID, API_KEY)


def get_score_client() -> ScoreClient:
    """Get an authenticated TeleSign Score (Intelligence) client"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return ScoreClient(CUSTOMER_ID, API_KEY)



def send_sms(phone_number: str, message: str, message_type: str = "OTP") -> dict:
    """
    Send an SMS message using TeleSign (Self-Service Account)
    
    Args:
        phone_number: Target phone number (with or without + prefix)
        message: SMS message text
        message_type: Message type (OTP, ARN, MKT) - defaults to OTP
    
    Returns:
        dict: Response from TeleSign API with status, reference_id, etc.
    """
    # Clean phone number
    phone_number = phone_number.lstrip('+').strip()
    
    # Log the attempt
    log_tool_call(
        tool_name="send_sms",
        input_data={"phone_number": phone_number, "message_type": message_type, "message_length": len(message)},
        metadata={"account_type": ACCOUNT_TYPE}
    )
    
    try:
        # Get messaging client
        messaging = get_messaging_client()
        
        # Make the request
        response = messaging.message(phone_number, message, message_type)
        
        # Parse response
        try:
            if isinstance(response.body, str):
                response_data = json.loads(response.body)
            else:
                response_data = response.body
        except (json.JSONDecodeError, AttributeError):
            response_data = {}
        
        # Log the result
        result = {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status", {}),
            "errors": response_data.get("errors", []),
            "success": response.status_code in [200, 201, 202, 203, 290, 291, 295]
        }
        
        log_tool_call(
            tool_name="send_sms",
            input_data={"phone_number": phone_number},
            output_data=result,
            success=result["success"],
            metadata={"reference_id": result.get("reference_id")}
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "status_code": 500,
            "success": False,
            "error": str(e),
            "errors": [{"message": str(e)}]
        }
        
        log_tool_call(
            tool_name="send_sms",
            input_data={"phone_number": phone_number},
            output_data=error_result,
            success=False,
            metadata={"error": str(e)}
        )
        
        return error_result


def send_voice_call(phone_number: str, message: str, voice_name: str = "female") -> dict:
    """
    Send a voice call with text-to-speech message
    
    Args:
        phone_number: Target phone number
        message: Message to speak (text-to-speech)
        voice_name: Voice type (female, male)
    
    Returns:
        dict: Response from TeleSign API
    """
    phone_number = phone_number.lstrip('+').strip()
    
    log_tool_call(
        tool_name="send_voice_call",
        input_data={"phone_number": phone_number, "voice_name": voice_name},
        metadata={"message_length": len(message)}
    )
    
    try:
        voice = get_voice_client()
        response = voice.call(phone_number, message, voice_name)
        
        try:
            if isinstance(response.body, str):
                response_data = json.loads(response.body)
            else:
                response_data = response.body
        except (json.JSONDecodeError, AttributeError):
            response_data = {}
        
        result = {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status", {}),
            "errors": response_data.get("errors", []),
            "success": response.status_code in [200, 201, 202, 203]
        }
        
        log_tool_call(
            tool_name="send_voice_call",
            input_data={"phone_number": phone_number},
            output_data=result,
            success=result["success"],
            metadata={"reference_id": result.get("reference_id")}
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "status_code": 500,
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="send_voice_call",
            input_data={"phone_number": phone_number},
            output_data=error_result,
            success=False
        )
        
        return error_result


def verify_phone_number(phone_number: str) -> dict:
    """Verify a phone number using TeleSign PhoneID SDK"""
    phone_number = phone_number.lstrip('+').strip()
    
    log_tool_call(
        tool_name="verify_phone_number",
        input_data={"phone_number": phone_number},
        metadata={"account_type": ACCOUNT_TYPE}
    )
    
    client = get_phoneid_client()
    
    payload = {  
        "addons": {"contact": {}},
        "phone_number": phone_number
    }
    
    response = client.phoneid(**payload)
    
    try:
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
    except (json.JSONDecodeError, AttributeError):
        response_data = {}
    
    try:
        if response.status_code == 200:
            # Extract detailed information from the response
            location = response_data.get("location", {})
            numbering = response_data.get("numbering", {})
            contact = response_data.get("contact", {})
            
            result = {
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
                "success": True,
                "full_response": response_data
            }
            
            log_tool_call(
                tool_name="verify_phone_number",
                input_data={"phone_number": phone_number},
                output_data=result,
                success=True,
                metadata={"reference_id": result.get("reference_id")}
            )
            
            return result
            
        else:
            error_result = {
                "status_code": response.status_code,
                "phone_type": "Error",
                "carrier": "N/A",
                "country": "N/A",
                "success": False,
                "error": response.body,
                "full_response": response_data
            }
            
            log_tool_call(
                tool_name="verify_phone_number",
                input_data={"phone_number": phone_number},
                output_data=error_result,
                success=False
            )
            
            return error_result
            
    except Exception as e:
        error_result = {
            "status_code": 500,
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="verify_phone_number",
            input_data={"phone_number": phone_number},
            output_data=error_result,
            success=False
        )
        
        return error_result


def get_message_status(reference_id: str) -> dict:
    """Check the delivery status of a sent message"""
    log_tool_call(
        tool_name="get_message_status",
        input_data={"reference_id": reference_id}
    )
    
    try:
        client = get_messaging_client()
        response = client.status(reference_id)
        
        try:
            if isinstance(response.body, str):
                response_data = json.loads(response.body)
            else:
                response_data = response.body
        except (json.JSONDecodeError, AttributeError):
            response_data = {}
        
        result = {
            "status_code": response.status_code,
            "status": response_data.get("status", {}),
            "success": response.status_code == 200,
            "full_response": response_data
        }
        
        log_tool_call(
            tool_name="get_message_status",
            input_data={"reference_id": reference_id},
            output_data=result,
            success=result["success"]
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "status_code": 500,
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="get_message_status",
            input_data={"reference_id": reference_id},
            output_data=error_result,
            success=False
        )
        
        return error_result


def send_verification_code(phone_number: str, code_length: int = 5) -> dict:
    """
    Send a 2FA verification code using TeleSign Verify API (Enterprise SDK - cheaper tokens)
    
    Args:
        phone_number: Target phone number
        code_length: Length of verification code (default: 5)
    
    Returns:
        dict: Response with reference_id and generated code
    """
    phone_number = phone_number.lstrip('+').strip()
    
    log_tool_call(
        tool_name="send_verification_code",
        input_data={"phone_number": phone_number, "code_length": code_length}
    )
    
    try:
        # Generate one-time passcode (OTP)
        verify_code = random_with_n_digits(code_length)
        
        # Get verify client
        verify = get_verify_client()
        
        # Send verification code using Verify API
        response = verify.sms(phone_number, verify_code=verify_code)
        
        # Parse response
        try:
            if isinstance(response.body, str):
                response_data = json.loads(response.body)
            else:
                response_data = response.body
        except (json.JSONDecodeError, AttributeError):
            response_data = {}
        
        result = {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "verify_code": verify_code,  # Include for testing
            "status": response_data.get("status", {}),
            "errors": response_data.get("errors", []),
            "success": response.status_code in [200, 201, 202, 203, 290, 291]
        }
        
        log_tool_call(
            tool_name="send_verification_code",
            input_data={"phone_number": phone_number},
            output_data={k: v for k, v in result.items() if k != "verify_code"},  # Don't log code
            success=result["success"],
            metadata={"reference_id": result.get("reference_id")}
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "status_code": 500,
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="send_verification_code",
            input_data={"phone_number": phone_number},
            output_data=error_result,
            success=False
        )
        
        return error_result


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
    Get fraud risk assessment for a phone number using TeleSign Intelligence (Score API)
    
    Args:
        phone_number: Phone number to assess
        account_lifecycle_event: Stage of account lifecycle (create, sign-in, transact, update)
    
    Returns:
        dict: Risk assessment results
    """
    phone_number = phone_number.lstrip('+').strip()
    
    log_tool_call(
        tool_name="assess_phone_risk",
        input_data={"phone_number": phone_number, "event": account_lifecycle_event}
    )
    
    try:
        # Get intelligence client
        intelligence = get_score_client()
        
        # Make the request
        response = intelligence.score(phone_number, account_lifecycle_event)
        
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
            
            result = {
                "status_code": response.status_code,
                "reference_id": response_data.get("reference_id"),
                "risk_level": risk_data.get("level"),
                "risk_score": risk_data.get("score"),
                "recommendation": risk_data.get("recommendation"),
                "phone_type": phone_type_data.get("description", "Unknown"),
                "carrier": numbering_data.get("original", {}).get("carrier", {}).get("name", "Unknown"),
                "account_lifecycle_event": account_lifecycle_event,
                "success": True,
                "full_response": response_data
            }
        else:
            result = {
                "status_code": response.status_code,
                "risk_level": "Error",
                "risk_score": None,
                "recommendation": "Error",
                "success": False,
                "error": response.body,
                "full_response": response_data
            }
        
        log_tool_call(
            tool_name="assess_phone_risk",
            input_data={"phone_number": phone_number},
            output_data=result,
            success=result.get("success", False),
            metadata={"reference_id": result.get("reference_id")}
        )
        
        return result
        
    except Exception as e:
        error_result = {
            "status_code": 500,
            "risk_level": "Error",
            "risk_score": None,
            "recommendation": "Error",
            "success": False,
            "error": str(e)
        }
        
        log_tool_call(
            tool_name="assess_phone_risk",
            input_data={"phone_number": phone_number},
            output_data=error_result,
            success=False
        )
        
        return error_result


# ==================== WHATSAPP FUNCTIONS (ENTERPRISE ACCOUNT REQUIRED) ====================
# Note: WhatsApp features require TeleSign Enterprise/Full-Service account upgrade
# These are stub implementations ready for when account is upgraded

def send_whatsapp_message(phone_number: str, message: str, whatsapp_account_id: str = None) -> dict:
    """
    Send a WhatsApp message (requires Enterprise/Full-Service account)
    
    Args:
        phone_number: Target phone number
        message: Message text to send
        whatsapp_account_id: Optional WhatsApp Business Account ID
    
    Returns:
        dict: Response with error about account upgrade needed
        
    Note: This function is ready for when you upgrade to Full-Service account.
          Until then, it returns an informative error message.
    """
    log_tool_call(
        tool_name="send_whatsapp_message",
        input_data={"phone_number": phone_number, "message_length": len(message)},
        metadata={"whatsapp_enabled": False}
    )
    
    # Return informative message about upgrade requirement
    result = {
        "success": False,
        "status_code": 403,
        "error": "WhatsApp messaging requires TeleSign Enterprise/Full-Service account",
        "message": "Please upgrade your TeleSign account to use WhatsApp features",
        "upgrade_info": "Contact TeleSign sales to upgrade from self-service to full-service account",
        "phone_number": phone_number
    }
    
    log_tool_call(
        tool_name="send_whatsapp_message",
        input_data={"phone_number": phone_number},
        output_data=result,
        success=False,
        metadata={"requires_upgrade": True}
    )
    
    return result
    
    # TODO: When upgraded to Full-Service, uncomment and configure:
    # """
    # from telesignenterprise.messaging import MessagingClient
    # 
    # phone_number = phone_number.lstrip('+').strip()
    # 
    # try:
    #     messaging = get_messaging_client()
    #     
    #     # WhatsApp message parameters
    #     params = {
    #         "message": message,
    #         "message_type": "OTP"  # or "ARN", "MKT"
    #     }
    #     
    #     if whatsapp_account_id:
    #         params["sender_id"] = whatsapp_account_id
    #     
    #     response = messaging.message(phone_number, message, "ARN", **params)
    #     
    #     if isinstance(response.body, str):
    #         response_data = json.loads(response.body)
    #     else:
    #         response_data = response.body
    #     
    #     return {
    #         "status_code": response.status_code,
    #         "reference_id": response_data.get("reference_id"),
    #         "status": response_data.get("status", {}),
    #         "success": response.status_code in [200, 201, 290, 291]
    #     }
    # except Exception as e:
    #     return {
    #         "status_code": 500,
    #         "success": False,
    #         "error": str(e)
    #     }
    # """


def send_whatsapp_template(phone_number: str, template_id: str, parameters: dict = None) -> dict:
    """
    Send a WhatsApp template message (requires Enterprise/Full-Service account)
    
    Args:
        phone_number: Target phone number
        template_id: WhatsApp template ID
        parameters: Template parameters
    
    Returns:
        dict: Response with error about account upgrade needed
    """
    return {
        "success": False,
        "status_code": 403,
        "error": "WhatsApp messaging requires TeleSign Enterprise/Full-Service account",
        "message": "Please upgrade your TeleSign account to use WhatsApp features",
        "phone_number": phone_number,
        "template_id": template_id
    }


def send_whatsapp_media(phone_number: str, media_url: str, caption: str = "", media_type: str = "image") -> dict:
    """
    Send WhatsApp media message (image, video, document) (requires Enterprise/Full-Service account)
    
    Args:
        phone_number: Target phone number
        media_url: Public URL of the media file
        caption: Optional caption for the media
        media_type: Type of media - "image", "video", "document", "audio"
    
    Returns:
        dict: Response with error about account upgrade needed
    """
    return {
        "success": False,
        "status_code": 403,
        "error": "WhatsApp messaging requires TeleSign Enterprise/Full-Service account",
        "message": "Please upgrade your TeleSign account to use WhatsApp features",
        "phone_number": phone_number,
        "media_type": media_type
    }


def send_whatsapp_buttons(phone_number: str, body_text: str, buttons: list[dict]) -> dict:
    """
    Send WhatsApp interactive button message (requires Enterprise/Full-Service account)
    
    Args:
        phone_number: Target phone number
        body_text: Main message text
        buttons: List of button dicts with 'id' and 'title' keys
                 Example: [{"id": "1", "title": "Yes"}, {"id": "2", "title": "No"}]
    
    Returns:
        dict: Response with error about account upgrade needed
    """
    return {
        "success": False,
        "status_code": 403,
        "error": "WhatsApp messaging requires TeleSign Enterprise/Full-Service account",
        "message": "Please upgrade your TeleSign account to use WhatsApp features",
        "phone_number": phone_number,
        "button_count": len(buttons) if buttons else 0
    }


def get_whatsapp_message_status(reference_id: str) -> dict:
    """
    Get WhatsApp message delivery status (requires Enterprise/Full-Service account)
    
    Args:
        reference_id: Message reference ID
    
    Returns:
        dict: Response with error about account upgrade needed
    """
    return {
        "success": False,
        "status_code": 403,
        "error": "WhatsApp messaging requires TeleSign Enterprise/Full-Service account",
        "message": "Please upgrade your TeleSign account to use WhatsApp features",
        "reference_id": reference_id
    }


# ==================== END WHATSAPP FUNCTIONS ====================


def get_detailed_message_status(reference_id: str) -> dict:
    """
    Get detailed message status including delivery timestamps and carrier info
    
    Returns:
        dict: Detailed status including timestamps, errors, and carrier feedback
    """
    client = get_messaging_client()
    response = client.status(reference_id)
    
    try:
        if isinstance(response.body, str):
            response_data = json.loads(response.body)
        else:
            response_data = response.body
    except (json.JSONDecodeError, AttributeError):
        response_data = {}
    
    status = response_data.get('status', {})
    
    return {
        "status_code": response.status_code,
        "reference_id": reference_id,
        "message_status_code": status.get('code'),  # Renamed to avoid conflict
        "status_description": status.get('description'),
        "updated_on": status.get('updated_on'),
        "completed_on": response_data.get('completed_on'),
        "submitted_at": response_data.get('submitted_at'),
        "errors": response_data.get('errors', []),
        "recipient": response_data.get('recipient'),
        "price": response_data.get('price'),
        "currency": response_data.get('currency'),
        "full_response": response_data
    }


def poll_message_until_complete(reference_id: str, max_attempts: int = 10, delay_seconds: int = 2) -> dict:
    """
    Poll message status until delivered or failed
    
    Args:
        reference_id: Message reference ID
        max_attempts: Maximum polling attempts
        delay_seconds: Delay between polls
    
    Returns:
        dict: Final message status
    """
    import time
    
    for attempt in range(max_attempts):
        status = get_detailed_message_status(reference_id)
        
        status_code = status.get('message_status_code')  # Updated key name
        
        # Check if message is in final state
        if status_code in [200, 203, 207, 220, 221, 222, 290, 295]:  # Delivered
            return {**status, "polling_complete": True, "attempts": attempt + 1}
        elif status_code and status_code >= 400:  # Failed
            return {**status, "polling_complete": True, "attempts": attempt + 1, "failed": True}
        
        # Continue polling
        if attempt < max_attempts - 1:
            time.sleep(delay_seconds)
    
    return {**status, "polling_complete": False, "attempts": max_attempts, "timeout": True}


def batch_verify_phones(phone_numbers: list[str]) -> list[dict]:
    """
    Verify multiple phone numbers in batch
    
    Args:
        phone_numbers: List of phone numbers to verify
    
    Returns:
        list[dict]: Verification results for each number
    """
    results = []
    
    for phone in phone_numbers:
        try:
            result = verify_phone_number(phone)
            results.append({
                "phone_number": phone,
                "success": result.get('status_code') == 200,
                "data": result
            })
        except Exception as e:
            results.append({
                "phone_number": phone,
                "success": False,
                "error": str(e)
            })
    
    return results


def batch_send_sms(recipients: list[dict]) -> list[dict]:
    """
    Send SMS to multiple recipients
    
    Args:
        recipients: List of dicts with 'phone_number' and 'message' keys
    
    Returns:
        list[dict]: Send results for each recipient
    """
    results = []
    
    for recipient in recipients:
        phone = recipient.get('phone_number')
        message = recipient.get('message')
        
        try:
            result = send_sms(phone, message)
            results.append({
                "phone_number": phone,
                "success": result.get('status_code') == 200,
                "reference_id": result.get('reference_id'),
                "data": result
            })
        except Exception as e:
            results.append({
                "phone_number": phone,
                "success": False,
                "error": str(e)
            })
    
    return results


# Keep backward compatibility
def load_credentials() -> tuple[str, str]:
    """Load Telesign credentials"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return CUSTOMER_ID, API_KEY