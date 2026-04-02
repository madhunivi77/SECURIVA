"""
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
