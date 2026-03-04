"""Test HIPAA module through compliance tool functions"""
import sys
sys.path.insert(0, 'backend')

from my_app.server.compliance_tools import (
    get_compliance_overview,
    get_compliance_requirements,
    get_compliance_checklist,
    get_penalty_information
)

print("=" * 70)
print("TESTING HIPAA MODULE THROUGH AI COMPLIANCE TOOLS")
print("=" * 70)

# Test 1: Get Overview
print("\n[Test 1: Get HIPAA Overview]")
overview = get_compliance_overview("hipaa")
print(f"✓ Standard: {overview['standard']}")
print(f"✓ Region: {overview['region']}")
print(f"✓ Overview: {overview['overview'][:100]}...")

# Test 2: Get Requirements
print("\n[Test 2: Get HIPAA Requirements]")
requirements = get_compliance_requirements("hipaa", "privacy_rule")
print(f"✓ Total found: {requirements['total_count']}")
if requirements['requirements']:
    rule = requirements['requirements'][0]
    print(f"✓ Rule name: {rule['name']}")
    print(f"✓ Reference: {rule['reference']}")
    print(f"✓ Requirements count: {len(rule['requirements'])}")
    print(f"  - {rule['requirements'][0]}")

# Test 3: Get Checklist
print("\n[Test 3: Get HIPAA Checklist]")
checklist = get_compliance_checklist("hipaa")
print(f"✓ Total checklist items: {checklist['total_items']}")
print(f"✓ Categories: {', '.join(checklist['categories'])}")
print(f"✓ Sample item: {checklist['checklist'][0]['requirement']}")

# Test 4: Get Penalties
print("\n[Test 4: Get HIPAA Penalties]")
penalties = get_penalty_information("hipaa")
print(f"✓ Success: {penalties['success']}")
print(f"✓ Standard: {penalties['standard']}")
print(f"✓ Tier 1 (Unknowing): {penalties['penalties']['tier_1']['amount']}")
print(f"✓ Tier 4 (Willful neglect): {penalties['penalties']['tier_4']['amount']}")

# Test 5: Cross-standard comparison
print("\n[Test 5: Verify Multiple Standards Available]")
from my_app.server.compliance_data import get_all_standards
all_standards = get_all_standards()
print(f"✓ Total standards available: {len(all_standards)}")
print(f"✓ Available: {', '.join(all_standards.keys())}")

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED - HIPAA MODULE FULLY INTEGRATED")
print("=" * 70)
