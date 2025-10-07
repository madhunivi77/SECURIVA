#Haven't added credentials to the .gitignore yet, this is just code for code's sake

import os
from telesign.whatsapp import WhatsAppClient

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

customer_id = os.environ.get("TELESIGN_CUSTOMER_ID")
api_key = os.environ.get("TELESIGN_API_KEY")

whatsapp_client = WhatsAppClient(customer_id, api_key)

#Phone Number template section:
phone_number = "12345678900" # Replace with recipient's phone number
# Pre-approved template components
template = {
    "name": "your_approved_template_name",
    "language": {
        "code": "en_US"
    },
    "components": [
        {
            "type": "body",
            "parameters": [
                {
                    "type": "text",
                    "text": "dynamic_value_1"
                },
                {
                    "type": "text",
                    "text": "dynamic_value_2"
                }
            ]
        }
    ]
}

try:
    response = whatsapp_client.message(phone_number, template)
    print("WhatsApp message sent successfully.")
    print(response.json)
except Exception as e:
    print(f"Error sending WhatsApp message: {e}")
