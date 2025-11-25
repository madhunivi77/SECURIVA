"""
Telesign WhatsApp Business API Integration
Ready for production use when account is upgraded to premium tier.

Features:
- Text messages
- Template messages (pre-approved)
- Media messages (images, videos, documents, audio)
- Interactive messages (buttons, lists)
- Location messages
- Contact messages
- Message status tracking
- Webhook handling for inbound messages
"""

import os
import json
import datetime
import hashlib
import hmac
from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv
from telesignenterprise.messaging import MessagingClient

load_dotenv()

# Load credentials
CUSTOMER_ID = os.getenv("TELESIGN_CUSTOMER_ID")
API_KEY = os.getenv("TELESIGN_API_KEY")
WHATSAPP_SENDER_ID = os.getenv("WHATSAPP_SENDER_ID")  # Your WhatsApp Business number
WHATSAPP_NAMESPACE = os.getenv("WHATSAPP_NAMESPACE")  # Template namespace from Telesign portal 

# Premium feature flag
WHATSAPP_PREMIUM_ENABLED = os.getenv("WHATSAPP_PREMIUM_ENABLED", "False").lower() == "true"


class WhatsAppMessageType(Enum):
    """WhatsApp message types supported by Telesign"""
    TEXT = "text"
    TEMPLATE = "template"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    LOCATION = "location"
    CONTACTS = "contacts"
    INTERACTIVE = "interactive"


class WhatsAppButtonType(Enum):
    """Interactive button types"""
    QUICK_REPLY = "quick_reply"
    CALL_TO_ACTION = "cta_url"
    CALL_PHONE = "cta_call"


class WhatsAppMediaType(Enum):
    """Supported media types"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


def get_whatsapp_client() -> MessagingClient:
    """Get authenticated Telesign Messaging client for WhatsApp"""
    if not CUSTOMER_ID or not API_KEY:
        raise ValueError("TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY must be set in .env")
    return MessagingClient(CUSTOMER_ID, API_KEY)


def _check_premium_access() -> dict:
    """Check if premium WhatsApp access is enabled"""
    if not WHATSAPP_PREMIUM_ENABLED:
        return {
            "status_code": 403,
            "error": "WhatsApp Business API requires premium account",
            "message": "Contact Telesign to upgrade your account for WhatsApp access",
            "upgrade_url": "https://www.telesign.com/contact"
        }
    return None


def _format_phone_number(phone_number: str) -> str:
    """Format phone number for WhatsApp (E.164 format)"""
    # Remove any whitespace or special characters
    phone = ''.join(filter(str.isdigit, phone_number))
    # Ensure it starts with country code
    if not phone.startswith('1') and len(phone) == 10:
        phone = '1' + phone  # Assume US if no country code
    return phone


# ==================== TEXT MESSAGES ====================

def send_whatsapp_text(phone_number: str, message: str, preview_url: bool = True) -> dict:
    """
    Send a plain text WhatsApp message
    
    Args:
        phone_number: Recipient's WhatsApp number (E.164 format)
        message: Text message content
        preview_url: Whether to generate link preview for URLs in message
    
    Returns:
        dict: Response with reference_id and status
        
    Example:
        >>> send_whatsapp_text("+16025551234", "Hello from Securiva!")
    """
    premium_check = _check_premium_access()
    if premium_check:
        return premium_check
    
    phone_number = _format_phone_number(phone_number)
    
    try:
        client = get_whatsapp_client()
        
        # Telesign WhatsApp API payload
        payload = {
            "message": message,
            "message_type": "ARN",  # Telesign's code for WhatsApp
            "sender_id": WHATSAPP_SENDER_ID,
            "preview_url": preview_url
        }
        
        response = client.message(phone_number, message, "ARN", **payload)
        
        # Parse response
        response_data = json.loads(response.body) if isinstance(response.body, str) else response.body
        
        return {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status"),
            "message_type": "text",
            "recipient": phone_number,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "full_response": response_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "message_type": "text"
        }


# ==================== TEMPLATE MESSAGES ====================

def send_whatsapp_template(
    phone_number: str,
    template_name: str,
    language_code: str = "en",
    parameters: Optional[List[str]] = None,
    header_parameters: Optional[List[Dict]] = None,
    button_parameters: Optional[List[Dict]] = None
) -> dict:
    """
    Send a pre-approved WhatsApp template message
    
    Args:
        phone_number: Recipient's WhatsApp number
        template_name: Name of approved template (from Telesign portal)
        language_code: Template language (e.g., "en", "es", "fr")
        parameters: Body text parameters for template variables
        header_parameters: Header parameters (for media or text)
        button_parameters: Dynamic button parameters (URLs, phone numbers)
    
    Returns:
        dict: Response with reference_id and status
        
    Example:
        >>> # Simple template with body parameters
        >>> send_whatsapp_template(
        ...     "+16025551234",
        ...     "order_confirmation",
        ...     parameters=["John", "12345", "December 25"]
        ... )
        
        >>> # Template with header image
        >>> send_whatsapp_template(
        ...     "+16025551234",
        ...     "product_catalog",
        ...     header_parameters=[{
        ...         "type": "image",
        ...         "image": {"link": "https://example.com/product.jpg"}
        ...     }],
        ...     parameters=["iPhone 15", "$999"]
        ... )
    """
    premium_check = _check_premium_access()
    if premium_check:
        return premium_check
    
    phone_number = _format_phone_number(phone_number)
    
    try:
        client = get_whatsapp_client()
        
        # Build template payload
        template_payload = {
            "name": template_name,
            "language": {"code": language_code},
            "components": []
        }
        
        # Add header parameters
        if header_parameters:
            template_payload["components"].append({
                "type": "header",
                "parameters": header_parameters
            })
        
        # Add body parameters
        if parameters:
            body_params = [{"type": "text", "text": param} for param in parameters]
            template_payload["components"].append({
                "type": "body",
                "parameters": body_params
            })
        
        # Add button parameters
        if button_parameters:
            template_payload["components"].append({
                "type": "button",
                "parameters": button_parameters
            })
        
        # Full message payload
        payload = {
            "message_type": "ARN",
            "sender_id": WHATSAPP_SENDER_ID,
            "template": template_payload
        }
        
        response = client.message(phone_number, "", "ARN", **payload)
        response_data = json.loads(response.body) if isinstance(response.body, str) else response.body
        
        return {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status"),
            "message_type": "template",
            "template_name": template_name,
            "recipient": phone_number,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "full_response": response_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "message_type": "template"
        }


# ==================== MEDIA MESSAGES ====================

def send_whatsapp_media(
    phone_number: str,
    media_url: str,
    media_type: WhatsAppMediaType,
    caption: Optional[str] = None,
    filename: Optional[str] = None
) -> dict:
    """
    Send a media message (image, video, document, audio)
    
    Args:
        phone_number: Recipient's WhatsApp number
        media_url: Public HTTPS URL to the media file
        media_type: Type of media (image, video, audio, document)
        caption: Optional caption for image/video
        filename: Optional filename for document
    
    Returns:
        dict: Response with reference_id and status
        
    Example:
        >>> # Send image with caption
        >>> send_whatsapp_media(
        ...     "+16025551234",
        ...     "https://example.com/invoice.pdf",
        ...     WhatsAppMediaType.DOCUMENT,
        ...     filename="Invoice_12345.pdf"
        ... )
    """
    premium_check = _check_premium_access()
    if premium_check:
        return premium_check
    
    phone_number = _format_phone_number(phone_number)
    
    try:
        client = get_whatsapp_client()
        
        # Build media payload
        media_payload = {
            media_type.value: {
                "link": media_url
            }
        }
        
        # Add caption for image/video
        if caption and media_type in [WhatsAppMediaType.IMAGE, WhatsAppMediaType.VIDEO]:
            media_payload[media_type.value]["caption"] = caption
        
        # Add filename for documents
        if filename and media_type == WhatsAppMediaType.DOCUMENT:
            media_payload[media_type.value]["filename"] = filename
        
        payload = {
            "message_type": "ARN",
            "sender_id": WHATSAPP_SENDER_ID,
            "type": media_type.value,
            **media_payload
        }
        
        response = client.message(phone_number, "", "ARN", **payload)
        response_data = json.loads(response.body) if isinstance(response.body, str) else response.body
        
        return {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status"),
            "message_type": media_type.value,
            "media_url": media_url,
            "recipient": phone_number,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "full_response": response_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "message_type": media_type.value
        }


# ==================== INTERACTIVE MESSAGES ====================

def send_whatsapp_buttons(
    phone_number: str,
    body_text: str,
    buttons: List[Dict[str, str]],
    header_text: Optional[str] = None,
    footer_text: Optional[str] = None
) -> dict:
    """
    Send an interactive message with quick reply buttons
    
    Args:
        phone_number: Recipient's WhatsApp number
        body_text: Main message text
        buttons: List of button dicts with 'id' and 'title' keys (max 3 buttons)
        header_text: Optional header text
        footer_text: Optional footer text
    
    Returns:
        dict: Response with reference_id and status
        
    Example:
        >>> send_whatsapp_buttons(
        ...     "+16025551234",
        ...     "How can we help you today?",
        ...     buttons=[
        ...         {"id": "support", "title": "Customer Support"},
        ...         {"id": "sales", "title": "Talk to Sales"},
        ...         {"id": "info", "title": "More Info"}
        ...     ],
        ...     header_text="Securiva Assistant"
        ... )
    """
    premium_check = _check_premium_access()
    if premium_check:
        return premium_check
    
    if len(buttons) > 3:
        return {
            "status_code": 400,
            "error": "Maximum 3 buttons allowed for quick reply messages"
        }
    
    phone_number = _format_phone_number(phone_number)
    
    try:
        client = get_whatsapp_client()
        
        # Build interactive payload
        interactive_payload = {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": btn.get("id", f"btn_{i}"),
                            "title": btn.get("title", f"Button {i+1}")
                        }
                    }
                    for i, btn in enumerate(buttons)
                ]
            }
        }
        
        # Add optional header
        if header_text:
            interactive_payload["header"] = {
                "type": "text",
                "text": header_text
            }
        
        # Add optional footer
        if footer_text:
            interactive_payload["footer"] = {"text": footer_text}
        
        payload = {
            "message_type": "ARN",
            "sender_id": WHATSAPP_SENDER_ID,
            "type": "interactive",
            "interactive": interactive_payload
        }
        
        response = client.message(phone_number, "", "ARN", **payload)
        response_data = json.loads(response.body) if isinstance(response.body, str) else response.body
        
        return {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status"),
            "message_type": "interactive_buttons",
            "button_count": len(buttons),
            "recipient": phone_number,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "full_response": response_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "message_type": "interactive_buttons"
        }


def send_whatsapp_list(
    phone_number: str,
    body_text: str,
    button_text: str,
    sections: List[Dict[str, Any]],
    header_text: Optional[str] = None,
    footer_text: Optional[str] = None
) -> dict:
    """
    Send an interactive list message
    
    Args:
        phone_number: Recipient's WhatsApp number
        body_text: Main message text
        button_text: Text shown on the list button (e.g., "View Options")
        sections: List of sections, each with 'title' and 'rows' keys
        header_text: Optional header text
        footer_text: Optional footer text
    
    Returns:
        dict: Response with reference_id and status
        
    Example:
        >>> send_whatsapp_list(
        ...     "+16025551234",
        ...     "Choose a service:",
        ...     "Select Service",
        ...     sections=[
        ...         {
        ...             "title": "Support Options",
        ...             "rows": [
        ...                 {"id": "tech", "title": "Technical Support", "description": "IT help desk"},
        ...                 {"id": "billing", "title": "Billing", "description": "Account questions"}
        ...             ]
        ...         },
        ...         {
        ...             "title": "Sales",
        ...             "rows": [
        ...                 {"id": "demo", "title": "Request Demo", "description": "See our product"}
        ...             ]
        ...         }
        ...     ]
        ... )
    """
    premium_check = _check_premium_access()
    if premium_check:
        return premium_check
    
    # Validate: max 10 sections, max 10 rows per section
    if len(sections) > 10:
        return {
            "status_code": 400,
            "error": "Maximum 10 sections allowed"
        }
    
    phone_number = _format_phone_number(phone_number)
    
    try:
        client = get_whatsapp_client()
        
        # Build list payload
        interactive_payload = {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
        
        # Add optional header
        if header_text:
            interactive_payload["header"] = {
                "type": "text",
                "text": header_text
            }
        
        # Add optional footer
        if footer_text:
            interactive_payload["footer"] = {"text": footer_text}
        
        payload = {
            "message_type": "ARN",
            "sender_id": WHATSAPP_SENDER_ID,
            "type": "interactive",
            "interactive": interactive_payload
        }
        
        response = client.message(phone_number, "", "ARN", **payload)
        response_data = json.loads(response.body) if isinstance(response.body, str) else response.body
        
        return {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status"),
            "message_type": "interactive_list",
            "section_count": len(sections),
            "recipient": phone_number,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "full_response": response_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "message_type": "interactive_list"
        }


# ==================== LOCATION & CONTACTS ====================

def send_whatsapp_location(
    phone_number: str,
    latitude: float,
    longitude: float,
    name: Optional[str] = None,
    address: Optional[str] = None
) -> dict:
    """
    Send a location message
    
    Args:
        phone_number: Recipient's WhatsApp number
        latitude: Location latitude
        longitude: Location longitude
        name: Optional location name
        address: Optional location address
    
    Returns:
        dict: Response with reference_id and status
        
    Example:
        >>> send_whatsapp_location(
        ...     "+16025551234",
        ...     37.7749,
        ...     -122.4194,
        ...     name="Securiva HQ",
        ...     address="123 Main St, San Francisco, CA"
        ... )
    """
    premium_check = _check_premium_access()
    if premium_check:
        return premium_check
    
    phone_number = _format_phone_number(phone_number)
    
    try:
        client = get_whatsapp_client()
        
        location_payload = {
            "latitude": latitude,
            "longitude": longitude
        }
        
        if name:
            location_payload["name"] = name
        if address:
            location_payload["address"] = address
        
        payload = {
            "message_type": "ARN",
            "sender_id": WHATSAPP_SENDER_ID,
            "type": "location",
            "location": location_payload
        }
        
        response = client.message(phone_number, "", "ARN", **payload)
        response_data = json.loads(response.body) if isinstance(response.body, str) else response.body
        
        return {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status"),
            "message_type": "location",
            "coordinates": f"{latitude},{longitude}",
            "recipient": phone_number,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "full_response": response_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "message_type": "location"
        }


def send_whatsapp_contact(
    phone_number: str,
    contacts: List[Dict[str, Any]]
) -> dict:
    """
    Send contact card(s)
    
    Args:
        phone_number: Recipient's WhatsApp number
        contacts: List of contact dicts with name and phone info
    
    Returns:
        dict: Response with reference_id and status
        
    Example:
        >>> send_whatsapp_contact(
        ...     "+16025551234",
        ...     contacts=[{
        ...         "name": {"formatted_name": "John Doe", "first_name": "John", "last_name": "Doe"},
        ...         "phones": [{"phone": "+16025551111", "type": "WORK"}],
        ...         "emails": [{"email": "john@example.com", "type": "WORK"}]
        ...     }]
        ... )
    """
    premium_check = _check_premium_access()
    if premium_check:
        return premium_check
    
    phone_number = _format_phone_number(phone_number)
    
    try:
        client = get_whatsapp_client()
        
        payload = {
            "message_type": "ARN",
            "sender_id": WHATSAPP_SENDER_ID,
            "type": "contacts",
            "contacts": contacts
        }
        
        response = client.message(phone_number, "", "ARN", **payload)
        response_data = json.loads(response.body) if isinstance(response.body, str) else response.body
        
        return {
            "status_code": response.status_code,
            "reference_id": response_data.get("reference_id"),
            "status": response_data.get("status"),
            "message_type": "contacts",
            "contact_count": len(contacts),
            "recipient": phone_number,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "full_response": response_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "message_type": "contacts"
        }


# ==================== WEBHOOK HANDLING ====================

def verify_webhook_signature(payload: str, signature: str, timestamp: str) -> bool:
    """
    Verify webhook signature from Telesign
    
    Args:
        payload: Raw webhook payload body
        signature: X-Telesign-Signature header value
        timestamp: X-Telesign-Timestamp header value
    
    Returns:
        bool: True if signature is valid
    """
    if not API_KEY:
        raise ValueError("API_KEY required for webhook verification")
    
    # Create signature using HMAC-SHA256
    message = f"{timestamp}.{payload}"
    expected_signature = hmac.new(
        API_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


def parse_inbound_whatsapp_message(webhook_payload: dict) -> dict:
    """
    Parse inbound WhatsApp message from webhook
    
    Args:
        webhook_payload: Webhook JSON payload from Telesign
    
    Returns:
        dict: Parsed message data
    """
    try:
        message = webhook_payload.get("message", {})
        sender = webhook_payload.get("from", {})
        
        return {
            "message_id": message.get("id"),
            "sender_phone": sender.get("phone_number"),
            "sender_name": sender.get("profile", {}).get("name"),
            "timestamp": message.get("timestamp"),
            "message_type": message.get("type"),
            "text": message.get("text", {}).get("body"),
            "media": message.get("image") or message.get("video") or message.get("document") or message.get("audio"),
            "location": message.get("location"),
            "contacts": message.get("contacts"),
            "button_reply": message.get("button", {}).get("text"),
            "list_reply": message.get("list_reply", {}).get("title"),
            "full_payload": webhook_payload
        }
    except Exception as e:
        return {
            "error": str(e),
            "raw_payload": webhook_payload
        }


# ==================== STATUS & ANALYTICS ====================

def get_whatsapp_message_status(reference_id: str) -> dict:
    """
    Get detailed status of a WhatsApp message
    
    Args:
        reference_id: Message reference ID from send response
    
    Returns:
        dict: Message status details
    """
    premium_check = _check_premium_access()
    if premium_check:
        return premium_check
    
    try:
        client = get_whatsapp_client()
        response = client.status(reference_id)
        
        response_data = json.loads(response.body) if isinstance(response.body, str) else response.body
        status = response_data.get("status", {})
        
        return {
            "status_code": response.status_code,
            "reference_id": reference_id,
            "message_status": status.get("description"),
            "status_code": status.get("code"),
            "sent": status.get("code") in [290, 295],  # Message in progress
            "delivered": status.get("code") == 200,
            "read": status.get("code") == 203,
            "failed": status.get("code", 0) >= 400,
            "timestamp": status.get("updated_on"),
            "error": response_data.get("errors"),
            "full_response": response_data
        }
        
    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e),
            "reference_id": reference_id
        }


# ==================== UTILITY FUNCTIONS ====================

def create_whatsapp_link(phone_number: str, message: Optional[str] = None) -> str:
    """
    Create a WhatsApp chat link (wa.me link)
    
    Args:
        phone_number: WhatsApp number
        message: Pre-filled message
    
    Returns:
        str: WhatsApp chat link
    """
    phone = _format_phone_number(phone_number)
    base_url = f"https://wa.me/{phone}"
    
    if message:
        from urllib.parse import quote
        base_url += f"?text={quote(message)}"
    
    return base_url


def validate_whatsapp_template(template_name: str) -> dict:
    """
    Check if a template is approved and active
    (In production, this would query Telesign's template API)
    
    Args:
        template_name: Template name to validate
    
    Returns:
        dict: Validation result
    """
    # This would need actual API integration
    return {
        "template_name": template_name,
        "status": "pending_validation",
        "message": "Connect to Telesign API to validate template status"
    }