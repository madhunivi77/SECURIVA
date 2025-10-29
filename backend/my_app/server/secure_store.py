# secure_store.py
import os
import base64
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

STORAGE_PATH = "secure_token.json"  # Google OAuth has its own so uh, eventually this will be phased towards it
MASTER_KEY = os.getenv("MASTER_KEY")  # 32-byte key in base64

if not MASTER_KEY:
    raise RuntimeError("Missing MASTER_KEY env variable (base64-encoded 32 bytes).")

def encrypt_text(plaintext: str) -> str:
    key = base64.b64decode(MASTER_KEY)
    iv = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return base64.b64encode(iv + tag + ciphertext).decode()

def decrypt_text(b64_ciphertext: str) -> str:
    key = base64.b64decode(MASTER_KEY)
    raw = base64.b64decode(b64_ciphertext)
    iv, tag, ciphertext = raw[:12], raw[12:28], raw[28:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()

def save_encrypted_token(encrypted_token: str, expiry_time: float):
    data = {"token": encrypted_token, "expiry": expiry_time}
    with open(STORAGE_PATH, "w") as f:
        json.dump(data, f)

def load_encrypted_token():
    if not os.path.exists(STORAGE_PATH):
        return None
    with open(STORAGE_PATH, "r") as f:
        data = json.load(f)
    return data["token"], data["expiry"]
