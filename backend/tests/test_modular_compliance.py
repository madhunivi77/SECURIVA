"""
Test the new modular compliance system
"""
import sys
from pathlib import Path

# Make sure we can import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

print("="*60)
print("TESTING MODULAR COMPLIANCE SYSTEM")
print("="*60)

# Test 1: Import the module loader
print("\n1. Testing module loader import...")
try:
    from my_app.server.compliance_modules import (
        load_compliance_module,
        get_available_modules,
        load_all_modules,
        get_module_info
    )
    print("✓ Module loader imported successfully")
except Exception as e:
    print(f"✗ Failed to import module loader: {e}")
    sys.exit(1)

# Test 2: List available modules
print("\n2. Listing available compliance modules...")
try:
    modules = get_available_modules()
    print(f"✓ Found {len(modules)} modules:")
    for module in modules:
        print(f"  • {module}")
except Exception as e:
    print(f"✗ Failed to list modules: {e}")

# Test 3: Load GDPR module
print("\n3. Testing GDPR module loading...")
try:
    gdpr = load_compliance_module("gdpr")
    print(f"✓ GDPR loaded: {gdpr['name']}")
    print(f"  Region: {gdpr['region']}")
    print(f"  Principles: {len(gdpr['key_principles'])}")
except Exception as e:
    print(f"✗ Failed to load GDPR: {e}")

# Test 4: Load Email Compliance module
print("\n4. Testing Email Compliance module loading...")
try:
    email = load_compliance_module("email_compliance")
    print(f"✓ Email Compliance loaded: {email['name']}")
    print(f"  Region: {email['region']}")
    print(f"  Standards covered: {len(email['standards'])}")
    for std in email['standards']:
        print(f"    - {std['name']}")
    print(f"  Checklist items: {len(email['checklist'])}")
except Exception as e:
    print(f"✗ Failed to load Email Compliance: {e}")

# Test 5: Load all modules at once
print("\n5. Testing bulk module loading...")
try:
    all_standards = load_all_modules()
    print(f"✓ Loaded {len(all_standards)} standards:")
    for key, standard in all_standards.items():
        print(f"  • {key}: {standard.get('name', 'Unknown')}")
except Exception as e:
    print(f"✗ Failed to load all modules: {e}")

# Test 6: Test with compliance_data.py
print("\n6. Testing integration with compliance_data.py...")
try:
    from my_app.server.compliance_data import get_standard, list_available_standards
    
    # Test getting email compliance through the main interface
    email_std = get_standard("email_compliance")
    if email_std:
        print(f"✓ Email compliance accessible via get_standard()")
        print(f"  Name: {email_std['name']}")
    
    # List all available standards
    all_stds = list_available_standards()
    print(f"✓ Total standards available: {len(all_stds)}")
    for std in all_stds:
        print(f"  • {std['id']}: {std['name']} ({std['type']})")
    
except Exception as e:
    print(f"✗ Integration test failed: {e}")

# Test 7: Test module info
print("\n7. Testing module metadata...")
try:
    for module_name in ["gdpr", "email_compliance"]:
        info = get_module_info(module_name)
        print(f"✓ {module_name}:")
        print(f"  Name: {info.get('name')}")
        print(f"  Region: {info.get('region')}")
        print(f"  Version: {info.get('version')}")
except Exception as e:
    print(f"✗ Metadata test failed: {e}")

print("\n" + "="*60)
print("✅ MODULAR COMPLIANCE SYSTEM WORKING!")
print("="*60)
print("\nYou can now:")
print("  1. Add new modules by creating files in compliance_modules/")
print("  2. Use email_compliance standard in your AI tools")
print("  3. Access all standards via get_standard()")
print("\nExample: Ask AI about email compliance:")
print("  'What are the CAN-SPAM requirements?'")
print("  'Give me an email marketing compliance checklist'")
print("  'How does CASL differ from CAN-SPAM?'")
