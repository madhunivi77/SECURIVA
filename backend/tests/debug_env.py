from pathlib import Path
from dotenv import load_dotenv, dotenv_values
import os

# Get the .env file path
env_path = Path(__file__).parent.parent / ".env"

print(f"Looking for .env at: {env_path.absolute()}")
print(f"File exists: {env_path.exists()}")
print(f"File size: {env_path.stat().st_size if env_path.exists() else 0} bytes")
print()

# Try loading with dotenv_values to see what's actually parsed
print("=== Parsing .env file ===")
env_vars = dotenv_values(env_path)
print(f"Found {len(env_vars)} variables")
print(f"AWS variables found: {[k for k in env_vars.keys() if 'AWS' in k]}")
print()

# Now load into environment
print("=== Loading into environment ===")
result = load_dotenv(env_path, override=True)
print(f"load_dotenv() returned: {result}")
print()

# Check what's in os.environ
print("=== Checking os.environ ===")
aws_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')

print(f"AWS_ACCESS_KEY_ID: {aws_key if aws_key else 'NOT FOUND'}")
print(f"AWS_SECRET_ACCESS_KEY: {'Found (length=' + str(len(aws_secret)) + ')' if aws_secret else 'NOT FOUND'}")
print(f"AWS_REGION: {aws_region if aws_region else 'NOT FOUND'}")
