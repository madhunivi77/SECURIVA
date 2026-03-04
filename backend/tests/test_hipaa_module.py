"""Quick test to verify HIPAA module loads correctly"""
from my_app.server.compliance_modules import get_available_modules, load_compliance_module

print('Available modules:', get_available_modules())

# Load HIPAA module
hipaa = load_compliance_module('hipaa')

print(f'\n✓ HIPAA module loaded successfully!')
print(f'  Name: {hipaa["name"]}')
print(f'  Region: {hipaa["region"]}')
print(f'  Effective Date: {hipaa["effective_date"]}')
print(f'  Key Rules: {len(hipaa["key_rules"])}')
print(f'  Checklist Items: {len(hipaa["checklist"])}')
print(f'  Penalty Tiers: {len(hipaa["penalties"])}')

# Test that we can access specific data
print(f'\n✓ Data Access Test:')
print(f'  Privacy Rule: {hipaa["key_rules"][0]["name"]}')
print(f'  Security Rule: {hipaa["key_rules"][1]["name"]}')
print(f'  Breach Notification: {hipaa["key_rules"][2]["name"]}')

print(f'\n✓ PHI Identifiers: {len(hipaa["phi_definition"]["identifiers"])} types')
print(f'\n✓ Module is ready for AI tool integration!')
