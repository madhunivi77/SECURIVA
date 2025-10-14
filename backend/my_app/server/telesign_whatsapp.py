# telesign_whatsapp.py
import requests
from telesign_auth import load_credentials, telesign_auth_header

customer_id, api_key = load_credentials()
auth_header, timestamp = telesign_auth_header(customer_id, api_key, "POST", "/v1/messaging")

headers = {
    "Authorization": auth_header,
    "Date": timestamp,
    "Content-Type": "application/json"
}

data = {
    "phone_number": "YOUR_PHONE_NUMBER",
    "message": "Hello from Telesign!",
    "message_type": "ARN"  # WhatsApp type
}

response = requests.post("https://rest-api.telesign.com/v1/messaging", json=data, headers=headers)
print(response.status_code, response.text)
