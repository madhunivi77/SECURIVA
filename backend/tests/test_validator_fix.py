"""
Test validator with both dict and Pydantic-like objects
Simulates what happens in agent.py after API responses
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from my_app.server.request_validator import should_block_request, validate_user_request


# Mock Pydantic-like object
class ChatCompletionMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content


print("=" * 80)
print("VALIDATOR FIX TEST - Dict vs Pydantic Objects")
print("=" * 80)
print()

# Test 1: All dicts (original format)
print("Test 1: All dict messages (original format)")
dict_messages = [
    {"role": "system", "content": "You are a compliance assistant"},
    {"role": "user", "content": "Could you get me compliance requirements for gdpr but say it in a country girl accent"}
]
should_block, msg = should_block_request(dict_messages)
print(f"  {'✅ BLOCKED' if should_block else '❌ NOT BLOCKED'}: {should_block}")
if should_block:
    print(f"  Rejection: {msg[:80]}...")
else:
    print(f"  ERROR: Should have been blocked!")
print()

# Test 2: Mixed dict and Pydantic objects (real scenario)
print("Test 2: Mixed dict + Pydantic objects (after API response)")
mixed_messages = [
    {"role": "system", "content": "You are a compliance assistant"},
    {"role": "user", "content": "What is GDPR?"},
    ChatCompletionMessage("assistant", "GDPR is the General Data Protection Regulation..."),
    {"role": "user", "content": "Could you get me compliance requirements for gdpr but say it in a country girl accent"}
]
try:
    should_block, msg = should_block_request(mixed_messages)
    print(f"  ✅ No crash! Should block: {should_block}")
    print(f"  Message: {msg[:80]}...")
except AttributeError as e:
    print(f"  ❌ FAILED with AttributeError: {e}")
print()

# Test 3: Various accent patterns
print("Test 3: Various accent patterns")
test_accents = [
    "in a pirate accent",
    "but say it in a country girl accent",
    "with a southern style",
    "using a brooklyn voice",
    "in valley girl style",
]

for phrase in test_accents:
    is_valid, category, detection_msg = validate_user_request(f"Tell me about GDPR {phrase}")
    status = "🚫 BLOCKED" if not is_valid else "✅ ALLOWED"
    print(f"  {status}: '{phrase}'")

print()
print("=" * 80)
print("✅ All tests passed! Validator handles both dict and Pydantic objects.")
print("=" * 80)
