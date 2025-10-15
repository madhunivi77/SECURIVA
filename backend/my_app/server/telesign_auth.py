# telesign_auth.py
import base64, hmac, hashlib, time, os
from cryptography.fernet import Fernet

# --------------------------------------------------------------------
# Load encrypted credentials securely
# --------------------------------------------------------------------
def load_credentials(master_key_path="MASTER_KEY.txt", creds_path="secure_creds.txt"):
    """Decrypt and return Customer ID and API Key"""
    with open(master_key_path, "rb") as key_file:
        master_key = key_file.read().strip()
    cipher = Fernet(master_key)
    with open(creds_path, "rb") as f:
        lines = f.readlines()
    customer_id = cipher.decrypt(lines[0].strip()).decode()
    api_key = cipher.decrypt(lines[1].strip()).decode()
    return customer_id, api_key


# --------------------------------------------------------------------
# Generate Telesign-style HMAC authorization header
# --------------------------------------------------------------------
def telesign_auth_header(customer_id, api_key, method, resource, body=""):
    """
    Generates the Telesign 'Authorization' header for REST requests.

    :param customer_id: Your Telesign Customer ID (UUID)
    :param api_key: Your Telesign API Key (base64 string)
    :param method: HTTP method (e.g., "POST", "GET")
    :param resource: Resource path (e.g., "/v1/messaging")
    :param body: Optional request body as string
    :return: Tuple (headers, timestamp)
    """
    timestamp = str(int(time.time()))
    nonce = base64.b64encode(os.urandom(12)).decode()  # random per-request salt

    # Following Telesign signature format (simplified)
    content = f"{method}\n{resource}\n{timestamp}\n{nonce}\n{body}"
    signature = hmac.new(
        base64.b64decode(api_key),
        msg=content.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    signature_b64 = base64.b64encode(signature).decode()

    auth_header = f"TSA {customer_id}:{signature_b64}"

    headers = {
        "Authorization": auth_header,
        "x-ts-date": timestamp,
        "x-ts-nonce": nonce,
        "Content-Type": "application/json"
    }
    return headers, timestamp
