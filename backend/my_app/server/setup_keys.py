# setup_keys.py
from cryptography.fernet import Fernet

# 🔐 Generate your own master key (keep this safe, e.g., in environment variable)
MASTER_KEY = Fernet.generate_key()
print("MASTER KEY:", MASTER_KEY.decode())

cipher = Fernet(MASTER_KEY)

# Replace with your real credentials from Telesign
customer_id = "YOUR_TELESIGN_CUSTOMER_ID"
api_key = "YOUR_TELESIGN_API_KEY"

# Encrypt credentials
encrypted_customer_id = cipher.encrypt(customer_id.encode())
encrypted_api_key = cipher.encrypt(api_key.encode())

# Save encrypted values somewhere safe (local file, database, etc.)
with open("secure_creds.txt", "wb") as f:
    f.write(encrypted_customer_id + b"\n" + encrypted_api_key)

print("✅ Encrypted credentials saved to secure_creds.txt")
