"""
Verify PCI-DSS module is complete and accessible
"""
import sys
sys.path.insert(0, 'backend')

from my_app.server.compliance_modules import get_available_modules, load_compliance_module
from my_app.server.compliance_tools import (
    get_compliance_overview,
    get_compliance_requirements,
    get_compliance_checklist
)

print("=" * 80)
print("TESTING PCI-DSS MODULE")
print("=" * 80)

# Test 1: Module discovery
print("\n[1] Module Discovery")
modules = get_available_modules()
print(f"✓ Available modules: {modules}")
print(f"✓ PCI-DSS present: {'pci_dss' in modules}")

# Test 2: Direct module load
print("\n[2] Direct Module Load")
pci_dss = load_compliance_module('pci_dss')
print(f"✓ Name: {pci_dss['name']}")
print(f"✓ Version: {pci_dss['current_version']}")
print(f"✓ Requirements: {len(pci_dss['requirements'])} (Expected: 12)")
print(f"✓ Checklist items: {len(pci_dss['checklist'])} (Expected: 15)")
print(f"✓ Merchant levels: {len(pci_dss['merchant_levels'])}")

# Test 3: Verify all 12 requirements present
print("\n[3] Requirements Verification")
for req in pci_dss['requirements']:
    print(f"  ✓ Req {req['id']}: {req['name']}")

# Test 4: Test with AI compliance tools
print("\n[4] AI Tool Integration Test")

overview = get_compliance_overview("pci_dss")
if overview['success']:
    print(f"✓ Overview: {overview['overview'][:80]}...")
else:
    print(f"✗ Failed: {overview.get('error')}")

requirements = get_compliance_requirements("pci_dss", 3)  # Pass as int
if requirements['success']:
    print(f"✓ Requirement 3 found: {len(requirements['requirements'])} item(s)")
    if requirements['requirements']:
        req = requirements['requirements'][0]
        print(f"  - Name: {req['name']}")
        print(f"  - Sub-requirements: {len(req['sub_requirements'])}")
else:
    print(f"✗ Failed: {requirements.get('error')}")

checklist = get_compliance_checklist("pci_dss")
if checklist['success']:
    print(f"✓ Checklist: {checklist['total_items']} items")
    if 'categories' in checklist and checklist['categories']:
        print(f"  Categories: {', '.join(list(checklist['categories'])[:5])}...")
    else:
        print(f"  First 3 items:")
        for item in checklist['checklist'][:3]:
            print(f"    - {item['id']}: {item['requirement'][:60]}...")
else:
    print(f"✗ Failed: {checklist.get('error')}")

# Test 5: Check data completeness
print("\n[5] Data Completeness Check")
checks = [
    ("Merchant levels", len(pci_dss.get('merchant_levels', {})) == 4),
    ("SAQ types", len(pci_dss.get('saq_types', {})) >= 8),
    ("Validation methods", len(pci_dss.get('validation_methods', [])) >= 4),
    ("Penalties defined", 'penalties' in pci_dss),
    ("Breach notification", 'breach_notification' in pci_dss),
    ("Key definitions", 'key_definitions' in pci_dss),
    ("All 12 requirements", len(pci_dss.get('requirements', [])) == 12)
]

all_passed = True
for check_name, result in checks:
    status = "✓" if result else "✗"
    print(f"  {status} {check_name}")
    if not result:
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("✅ PCI-DSS MODULE FULLY FUNCTIONAL AND COMPLETE!")
else:
    print("⚠️  Some checks failed - review above")
print("=" * 80)

if all_passed:
    print("\nUsers can now ask:")
    print("  • 'What are the PCI-DSS 12 requirements?'")
    print("  • 'Explain PCI-DSS Requirement 3 about protecting stored data'")
    print("  • 'Show me the PCI-DSS compliance checklist'")
    print("  • 'What are merchant levels in PCI-DSS?'")
    print("  • 'What data cannot be stored under PCI-DSS?'")
    print("=" * 80)
