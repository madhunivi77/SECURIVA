# setup_keys.py (SAFE)
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

# Generate master key
MASTER_KEY = Fernet.generate_key()
print("MASTER KEY:", MASTER_KEY.decode())
print("⚠️  Save this master key to your .env file as MASTER_KEY")

cipher = Fernet(MASTER_KEY)

# Get credentials from environment variables (NOT hardcoded)
customer_id = os.getenv("TELESIGN_CUSTOMER_ID")
api_key = os.getenv("TELESIGN_API_KEY")

if not customer_id or not api_key:
    print("❌ Error: Set TELESIGN_CUSTOMER_ID and TELESIGN_API_KEY in .env file first!")
    exit(1)

# Encrypt credentials
encrypted_customer_id = cipher.encrypt(customer_id.encode())
encrypted_api_key = cipher.encrypt(api_key.encode())

# Save encrypted values
with open("secure_creds.txt", "wb") as f:
    f.write(encrypted_customer_id + b"\n" + encrypted_api_key)

print("✅ Encrypted credentials saved to secure_creds.txt")