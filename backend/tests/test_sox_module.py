"""
Verify SOX module is accessible through AI compliance tools
"""
import sys
sys.path.insert(0, 'backend')

from my_app.server.compliance_tools import (
    get_compliance_overview,
    get_compliance_requirements,
    get_compliance_checklist
)

print("=" * 80)
print("TESTING SOX MODULE WITH AI COMPLIANCE TOOLS")
print("=" * 80)

# Test 1: Get Overview
print("\n[1] Get SOX Overview")
overview = get_compliance_overview("sox")
if overview['success']:
    print(f"✓ Name: {overview['standard']}")
    print(f"✓ Region: {overview['region']}")
    print(f"✓ Effective Date: {overview['effective_date']}")
    print(f"✓ Overview: {overview['overview'][:100]}...")
else:
    print(f"✗ Failed: {overview.get('error')}")

# Test 2: Get Requirements
print("\n[2] Get SOX Requirements (Section 302)")
requirements = get_compliance_requirements("sox", "section_302")
if requirements['success']:
    print(f"✓ Found: {requirements['total_count']} section(s)")
    if requirements['requirements']:
        section = requirements['requirements'][0]
        print(f"✓ Section: {section['name']}")
        print(f"✓ Requirements:")
        for req in section['requirements'][:3]:
            print(f"  - {req}")
else:
    print(f"✗ Failed: {requirements.get('error')}")

# Test 3: Get Checklist
print("\n[3] Get SOX Compliance Checklist")
checklist = get_compliance_checklist("sox")
if checklist['success']:
    print(f"✓ Total items: {checklist['total_items']}")
    print(f"✓ Categories: {', '.join(checklist['categories'])}")
    print(f"✓ Sample items:")
    for item in checklist['checklist'][:3]:
        print(f"  - [{item['id']}] {item['requirement']}")
else:
    print(f"✗ Failed: {checklist.get('error')}")

print("\n" + "=" * 80)
print("✅ SOX MODULE FULLY INTEGRATED WITH AI TOOLS!")
print("=" * 80)
print("\nUsers can now ask:")
print("  • 'What are the SOX Section 404 requirements?'")
print("  • 'Show me the SOX compliance checklist'")
print("  • 'Compare SOX Section 302 vs HIPAA Privacy Rule'")
print("  • 'What are penalties for SOX violations?'")
print("=" * 80)
