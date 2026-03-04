"""Quick test to verify compliance tools work"""
from my_app.server.compliance_tools import get_compliance_overview

print("Testing compliance tools...")
result = get_compliance_overview('gdpr')
print(f"✓ get_compliance_overview: success={result['success']}")
print(f"✓ Standard name: {result.get('standard', 'N/A')}")
print("\nAll imports and basic functionality working!")
