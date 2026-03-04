"""
Test script for Compliance Tools
Demonstrates how to use each compliance tool function
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from my_app.server.compliance_tools import (
    get_compliance_overview,
    get_compliance_requirements,
    get_compliance_checklist,
    get_penalty_information,
    get_breach_notification_requirements,
    cross_reference_compliance_topic,
    search_compliance_requirements,
    generate_compliance_report
)


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_compliance_overview():
    """Test get_compliance_overview function"""
    print_section("TEST: Compliance Overview")
    
    for standard in ["gdpr", "hipaa", "pci_dss"]:
        result = get_compliance_overview(standard)
        if result["success"]:
            print(f"✓ {result['standard']}")
            print(f"  Region: {result['region']}")
            print(f"  Effective: {result['effective_date']}")
            print(f"  Overview: {result['overview'][:100]}...")
            print()


def test_compliance_requirements():
    """Test get_compliance_requirements function"""
    print_section("TEST: Compliance Requirements")
    
    # Test GDPR - get all principles
    result = get_compliance_requirements("gdpr")
    if result["success"]:
        print(f"✓ GDPR has {result['total_count']} key principles:")
        for req in result["requirements"][:3]:  # Show first 3
            print(f"  - {req['name']} ({req['article']})")
    
    print()
    
    # Test PCI-DSS - get specific requirement
    result = get_compliance_requirements("pci_dss", requirement_id=3)
    if result["success"] and result["requirements"]:
        req = result["requirements"][0]
        print(f"✓ PCI-DSS Requirement {req['id']}: {req['name']}")
        print(f"  Description: {req['description']}")


def test_compliance_checklist():
    """Test get_compliance_checklist function"""
    print_section("TEST: Compliance Checklist")
    
    result = get_compliance_checklist("hipaa")
    if result["success"]:
        print(f"✓ HIPAA Checklist: {result['total_items']} items")
        print(f"\nCategories:")
        for category, items in result["categories"].items():
            print(f"  {category}: {len(items)} items")
        
        # Show sample items
        print(f"\nSample items:")
        for item in result["checklist"][:3]:
            print(f"  [{item['id']}] {item['requirement']}")


def test_penalty_information():
    """Test get_penalty_information function"""
    print_section("TEST: Penalty Information")
    
    for standard in ["gdpr", "hipaa"]:
        result = get_penalty_information(standard)
        if result["success"]:
            print(f"✓ {result['standard']} Penalties:")
            for tier, info in result["penalties"].items():
                print(f"  {tier}: {info.get('amount', info.get('description'))}")
            print()


def test_breach_notification():
    """Test get_breach_notification_requirements function"""
    print_section("TEST: Breach Notification Requirements")
    
    for standard in ["gdpr", "hipaa"]:
        result = get_breach_notification_requirements(standard)
        if result["success"]:
            print(f"✓ {result['standard']}:")
            breach_info = result["breach_notification"]
            if isinstance(breach_info, dict):
                for key, value in breach_info.items():
                    print(f"  {key}: {value}")
            print()


def test_cross_reference():
    """Test cross_reference_compliance_topic function"""
    print_section("TEST: Cross-Reference Topics")
    
    topics = ["data_encryption", "access_control", "audit_logging"]
    
    for topic in topics:
        result = cross_reference_compliance_topic(topic)
        if result["success"]:
            print(f"✓ Topic: {result['topic']}")
            for standard, refs in result["cross_references"].items():
                print(f"  {standard.upper()}:")
                for ref in refs:
                    print(f"    - {ref}")
            print()


def test_search_requirements():
    """Test search_compliance_requirements function"""
    print_section("TEST: Search Requirements")
    
    queries = ["encryption", "access control", "audit"]
    
    for query in queries:
        result = search_compliance_requirements(query, standards=["gdpr", "hipaa", "pci_dss"])
        if result["success"]:
            print(f"✓ Query: '{query}' - Found {result['total_matches']} matches")
            for match in result["matches"][:2]:  # Show first 2
                print(f"  {match['standard']}: {match['item'].get('name', 'N/A')}")
            print()


def test_generate_report():
    """Test generate_compliance_report function"""
    print_section("TEST: Generate Compliance Report")
    
    result = generate_compliance_report(
        standards=["gdpr", "hipaa"],
        include_checklist=True,
        include_penalties=True,
        include_breach_info=True
    )
    
    if result["success"]:
        report = result["report"]
        print(f"✓ Report Generated at: {report['generated_at']}")
        print(f"\nSummary:")
        print(f"  Standards: {report['summary']['total_standards']}")
        print(f"  Total Requirements: {report['summary']['total_requirements']}")
        print(f"  Total Checklist Items: {report['summary']['total_checklist_items']}")
        
        print(f"\nIncluded Standards:")
        for std in report["standards"]:
            print(f"  - {std['name']}")
            print(f"    Requirements: {std['requirement_count']}")
            if 'checklist_count' in std:
                print(f"    Checklist Items: {std['checklist_count']}")


def test_error_handling():
    """Test error handling"""
    print_section("TEST: Error Handling")
    
    # Test invalid standard
    result = get_compliance_overview("invalid_standard")
    if not result["success"]:
        print(f"✓ Invalid standard handled gracefully")
        print(f"  Error: {result['error']}")
        print(f"  Available: {result.get('available_standards', [])}")
    
    print()
    
    # Test invalid topic
    result = cross_reference_compliance_topic("invalid_topic")
    if not result["success"]:
        print(f"✓ Invalid topic handled gracefully")
        print(f"  Error: {result['error']}")
        print(f"  Available: {result.get('available_topics', [])}")


def run_all_tests():
    """Run all test functions"""
    print("\n" + "="*80)
    print("  COMPLIANCE TOOLS TEST SUITE")
    print("="*80)
    
    test_compliance_overview()
    test_compliance_requirements()
    test_compliance_checklist()
    test_penalty_information()
    test_breach_notification()
    test_cross_reference()
    test_search_requirements()
    test_generate_report()
    test_error_handling()
    
    print_section("ALL TESTS COMPLETED")
    print("Check backend/logs/tool_calls.json for detailed logs")


if __name__ == "__main__":
    run_all_tests()
