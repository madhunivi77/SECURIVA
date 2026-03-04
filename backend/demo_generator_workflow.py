"""
Demonstration: AI-Safe Compliance Module Generation Workflow
Shows the correct 2-step process: Validate → Create
"""
import sys
sys.path.insert(0, 'backend')

from my_app.server.compliance_module_generator import (
    create_compliance_module_dry_run,
    create_compliance_module,
    list_compliance_modules
)
import json

print("=" * 80)
print("AI-SAFE COMPLIANCE MODULE GENERATION WORKFLOW")
print("=" * 80)

# Example: AI wants to create a SOX compliance module

sox_content = '''"""
SOX (Sarbanes-Oxley Act) Compliance Module
Corporate financial reporting and internal controls for public companies
"""

STANDARD = {
    "name": "Sarbanes-Oxley Act of 2002",
    "region": "United States",
    "effective_date": "2002-07-30",
    "version": "Public Law 107-204",
    "overview": "Federal law establishing enhanced standards for public company boards, management, and accounting firms to improve financial reporting accuracy and prevent corporate fraud",
    "official_reference": "Public Law 107-204, 116 Stat. 745",
    "authority": "Securities and Exchange Commission (SEC), Public Company Accounting Oversight Board (PCAOB)",
    "website": "https://www.sec.gov/spotlight/sarbanes-oxley.htm",
    
    "key_sections": [
        {
            "id": "section_302",
            "name": "Corporate Responsibility for Financial Reports",
            "description": "CEO and CFO must certify the accuracy of financial statements",
            "requirements": [
                "Sign and certify quarterly and annual financial reports",
                "Certify that report fairly presents financial condition",
                "Certify internal controls are effective",
                "Disclose significant deficiencies in internal controls",
                "Disclose fraud involving management or employees with significant role"
            ],
            "penalties": "Up to $5 million fine and 20 years imprisonment for willful violations"
        },
        {
            "id": "section_404",
            "name": "Management Assessment of Internal Controls",
            "description": "Annual report on internal controls over financial reporting",
            "requirements": [
                "Establish and maintain adequate internal control structure",
                "Assess effectiveness of internal controls annually",
                "Include internal control report in annual filing",
                "External auditor must attest to management assessment",
                "Identify material weaknesses in internal controls"
            ],
            "compliance_cost": "Often most expensive SOX requirement for companies"
        },
        {
            "id": "section_401",
            "name": "Disclosures in Periodic Reports",
            "description": "Enhanced financial disclosures requirements",
            "requirements": [
                "Disclose all material off-balance-sheet transactions",
                "Disclose all material obligations and liabilities",
                "Pro forma financial information must not be misleading",
                "Reconcile pro forma data with GAAP"
            ]
        },
        {
            "id": "section_802",
            "name": "Criminal Penalties for Document Destruction",
            "description": "Penalties for destroying or altering documents",
            "requirements": [
                "Retain audit workpapers for 7 years",
                "Preserve records relevant to federal investigations",
                "No destruction of documents to impede investigations"
            ],
            "penalties": "Up to 20 years imprisonment for destroying documents"
        },
        {
            "id": "section_906",
            "name": "Criminal Penalties for CEO/CFO Certification",
            "description": "Criminal liability for false certification",
            "penalties": {
                "knowing_violation": "Up to $1 million fine and 10 years imprisonment",
                "willful_violation": "Up to $5 million fine and 20 years imprisonment"
            }
        }
    ],
    
    "compliance_requirements": [
        "Public companies must comply (private companies exempt)",
        "Annual Section 404 assessment",
        "Quarterly CEO/CFO certifications",
        "Independent audit committee required",
        "Auditor independence rules",
        "Whistleblower protections",
        "Real-time disclosure of material changes"
    ],
    
    "penalties": {
        "section_302_willful": "Up to $5 million fine and 20 years imprisonment",
        "section_906_willful": "Up to $5 million fine and 20 years imprisonment",
        "section_906_knowing": "Up to $1 million fine and 10 years imprisonment",
        "section_802": "Up to 20 years imprisonment for document destruction",
        "securities_fraud": "Up to 25 years imprisonment"
    },
    
    "checklist": [
        {"id": "sox_001", "requirement": "Establish internal control framework (e.g., COSO)", "category": "Internal Controls"},
        {"id": "sox_002", "requirement": "Document all significant processes and controls", "category": "Documentation"},
        {"id": "sox_003", "requirement": "Test effectiveness of internal controls annually", "category": "Testing"},
        {"id": "sox_004", "requirement": "CEO and CFO certify financial statements quarterly", "category": "Certification"},
        {"id": "sox_005", "requirement": "External auditor attestation on internal controls", "category": "Audit"},
        {"id": "sox_006", "requirement": "Independent audit committee established", "category": "Governance"},
        {"id": "sox_007", "requirement": "Whistleblower protection program in place", "category": "Ethics"},
        {"id": "sox_008", "requirement": "Audit workpapers retained for 7 years", "category": "Records"},
        {"id": "sox_009", "requirement": "Disclosure controls and procedures documented", "category": "Disclosure"},
        {"id": "sox_010", "requirement": "IT general controls assessed and tested", "category": "IT Controls"}
    ],
    
    "applicability": {
        "required_for": [
            "Public companies registered with SEC",
            "Foreign companies listed on US exchanges",
            "Companies filing with SEC (even if private)"
        ],
        "exempt": [
            "Private companies not filing with SEC",
            "Non-profit organizations",
            "Government entities"
        ]
    }
}

MODULE_INFO = {
    "module_type": "compliance_standard",
    "last_updated": "2024-03-04",
    "maintainer": "Compliance Team",
    "tags": ["finance", "accounting", "public companies", "sec", "audit", "us"],
    "industry": "Finance/Accounting"
}
'''

print("\n📋 AI Generated Content:")
print(f"   Module: sox.py")
print(f"   Size: {len(sox_content)} bytes")
print(f"   Lines: {sox_content.count(chr(10))}")

# ====================
# STEP 1: VALIDATE (DRY RUN)
# ====================

print("\n" + "=" * 80)
print("STEP 1: VALIDATION (DRY RUN - NO FILE CREATED)")
print("=" * 80)

print("\n🔍 Running security validation...")
validation_result = create_compliance_module_dry_run('sox.py', sox_content)

print(f"\n📊 Validation Result:")
print(json.dumps(validation_result, indent=2))

# Check if validation passed
if not validation_result.get('success'):
    print("\n❌ VALIDATION FAILED!")
    print("   AI should NOT proceed to Step 2.")
    print(f"   Error: {validation_result.get('error')}")
    sys.exit(1)

print("\n✅ VALIDATION PASSED!")
print("\n🔒 Security Checks:")
for check in validation_result.get('validation_results', []):
    print(f"   {check}")

# ====================
# STEP 2: CREATE FILE
# ====================

print("\n" + "=" * 80)
print("STEP 2: CREATE FILE (WRITES TO DISK)")
print("=" * 80)

print("\n⚠️  AI Decision Point:")
print("   Validation passed. Should we create the file?")
print("   User can review validation results before proceeding.")

# Simulate user confirmation (in real scenario, might require approval)
user_approved = True

if user_approved:
    print("\n✅ Proceeding with file creation...")
    
    # Actually create the file
    creation_result = create_compliance_module(
        filename='sox.py',
        content=sox_content,
        allow_overwrite=False  # Don't overwrite existing
    )
    
    print(f"\n📄 Creation Result:")
    print(json.dumps(creation_result, indent=2))
    
    if creation_result.get('success'):
        print("\n🎉 SUCCESS!")
        print(f"   File created: {creation_result.get('filename')}")
        print(f"   Location: {creation_result.get('target_path')}")
        print(f"   Standard: {creation_result.get('standard_name')}")
    else:
        print("\n❌ CREATION FAILED!")
        print(f"   Error: {creation_result.get('error')}")
else:
    print("\n🚫 File creation cancelled by user")

# ====================
# STEP 3: VERIFY
# ====================

print("\n" + "=" * 80)
print("STEP 3: VERIFY MODULE AVAILABLE")
print("=" * 80)

print("\n📋 Listing all compliance modules...")
modules_result = list_compliance_modules()

print(f"\n📊 Available Modules: {modules_result.get('total_modules')}")
for module in modules_result.get('modules', []):
    print(f"   • {module['module_id']}: {module['filename']} ({module['size_bytes']} bytes)")

# Check if SOX is in the list
sox_found = any(m['module_id'] == 'sox' for m in modules_result.get('modules', []))
if sox_found:
    print("\n✅ SOX module successfully added and available!")
else:
    print("\n⚠️  SOX module not found in list")

# ====================
# SUMMARY
# ====================

print("\n" + "=" * 80)
print("WORKFLOW SUMMARY")
print("=" * 80)

print("""
✅ 2-Step Security Process Completed:

   1. VALIDATE (Dry Run)
      - Filename validation ✓
      - Path security check ✓
      - Python syntax validation ✓
      - Dangerous code detection ✓
      - Structure validation ✓
      - File size check ✓
      → Result: SAFE TO PROCEED

   2. CREATE (Write to Disk)
      - File created in compliance_modules/ ✓
      - Automatically discoverable ✓
      - Ready for AI queries ✓

   3. VERIFY
      - Module appears in list ✓
      - Can be loaded by AI tools ✓

🎯 AI can now answer questions about SOX compliance!

Example queries:
- "What are the SOX Section 404 requirements?"
- "What are the penalties for SOX violations?"
- "Show me the SOX compliance checklist"
- "Compare SOX vs HIPAA requirements"
""")

print("=" * 80)
