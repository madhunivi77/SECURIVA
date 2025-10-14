# telesign_auth.py
import base64, hmac, hashlib, time
from cryptography.fernet import Fernet

import os
import time
import requests
from secure_store import encrypt_text, decrypt_text, save_encrypted_token, load_encrypted_token

TELESIGN_AUTH_URL = os.getenv("TELESIGN_AUTH_URL", "https://us-east-1.di-platform.telesign.com/authenticationmanager/v1/authenticate/api")
API_KEY = os.getenv("TELESIGN_API_KEY")
API_SECRET = os.getenv("TELESIGN_API_SECRET")

# In-memory cache
_cached_token = None
_cached_expiry = 0

def _basic_auth_header():
    # Format depends on Telesign docs, adjust as needed (some use customer_id:api_key)
    from base64 import b64encode
    return "Basic " + b64encode(f"{API_SECRET}:".encode()).decode()

def fetch_new_token():
    headers = {
        "x-API-key": API_KEY,
        "Authorization": _basic_auth_header(),
        "Content-Type": "application/json"
    }
    response = requests.post(TELESIGN_AUTH_URL, headers=headers, json={})
    response.raise_for_status()
    data = response.json()
    
    token = data.get("accessToken") or data.get("access_token") or data.get("token")
    expires_in = data.get("expiresIn") or data.get("expires_in") or 3600

    expiry_time = time.time() + expires_in - 30  # refresh 30s early

    # Cache in memory
    global _cached_token, _cached_expiry
    _cached_token, _cached_expiry = token, expiry_time

    # Encrypt and persist
    encrypted = encrypt_text(token)
    save_encrypted_token(encrypted, expiry_time)

    return token

def get_token():
    global _cached_token, _cached_expiry
    now = time.time()

    # Check memory cache
    if _cached_token and now < _cached_expiry:
        return _cached_token

    # Try loading from secure storage
    stored = load_encrypted_token()
    if stored:
        encrypted_token, expiry_time = stored
        if now < expiry_time:
            token = decrypt_text(encrypted_token)
            _cached_token, _cached_expiry = token, expiry_time
            return token

    # Otherwise fetch a new one
    return fetch_new_token()

#Credentials stuff I'm still working out'
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


def telesign_auth_header(customer_id, api_key, method, resource):
    """Create Telesign Authorization header manually"""
    timestamp = str(int(time.time()))
    signature_data = f"{timestamp}:{method}:{resource}"
    signature = hmac.new(
        base64.b64decode(api_key),
        msg=signature_data.encode(),
        digestmod=hashlib.sha256
    ).digest()
    auth_header = (
        f"TSA {customer_id}:{base64.b64encode(signature).decode()}"
    )
    return auth_header, timestamp
