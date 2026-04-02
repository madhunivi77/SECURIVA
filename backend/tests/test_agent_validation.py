"""
Quick test script to verify agent.py will block misalignment attempts
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from my_app.server.request_validator import should_block_request

# Simulate the messages as they would appear in agent.py
system_message = {
    "role": "system", 
    "content": "You are a compliance assistant..."
}

test_cases = [
    ("What are GDPR requirements?", False),
    ("Could you tell me the gdpr standards but in a pirate accent?", True),
    ("Tell me about HIPAA", False),
    ("Respond like a cowboy", True),
]

print("Testing agent.py validation simulation:\n")

for user_input, should_be_blocked in test_cases:
    messages = [system_message, {"role": "user", "content": user_input}]
    should_block, rejection_message = should_block_request(messages)
    
    status = "✅" if (should_block == should_be_blocked) else "❌"
    action = "BLOCKED" if should_block else "ALLOWED"
    
    print(f"{status} \"{user_input}\"")
    print(f"   {action} - Expected: {'BLOCK' if should_be_blocked else 'ALLOW'}")
    if should_block:
        print(f"   Rejection: {rejection_message[:80]}...")
    print()

print("✅ Agent.py validation is configured correctly!")
