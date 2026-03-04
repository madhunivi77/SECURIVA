"""
Compliance Standards Data Repository
Contains structured information about GDPR, HIPAA, and PCI-DSS compliance standards
"""

from typing import Dict, List, Any
from datetime import datetime

# GDPR Compliance Standards
GDPR_STANDARDS = {
    "name": "General Data Protection Regulation (GDPR)",
    "region": "European Union",
    "effective_date": "2018-05-25",
    "overview": "EU regulation on data protection and privacy for individuals within the EU and the European Economic Area.",
    "official_reference": "Regulation (EU) 2016/679",
    "key_principles": [
        {
            "id": "lawfulness",
            "name": "Lawfulness, Fairness, and Transparency",
            "description": "Personal data must be processed lawfully, fairly, and transparently.",
            "article": "Article 5(1)(a)",
            "requirements": [
                "Obtain valid legal basis for processing",
                "Provide clear information about data processing",
                "Ensure transparency in all data operations"
            ]
        },
        {
            "id": "purpose_limitation",
            "name": "Purpose Limitation",
            "description": "Data must be collected for specified, explicit, and legitimate purposes.",
            "article": "Article 5(1)(b)",
            "requirements": [
                "Define clear purposes before collection",
                "Document purpose of data processing",
                "Avoid using data for incompatible purposes"
            ]
        },
        {
            "id": "data_minimization",
            "name": "Data Minimization",
            "description": "Only collect data that is adequate, relevant, and necessary.",
            "article": "Article 5(1)(c)",
            "requirements": [
                "Collect only necessary data",
                "Regularly review data collection practices",
                "Remove unnecessary data fields"
            ]
        },
        {
            "id": "accuracy",
            "name": "Accuracy",
            "description": "Personal data must be accurate and kept up to date.",
            "article": "Article 5(1)(d)",
            "requirements": [
                "Implement data validation",
                "Provide mechanisms for data correction",
                "Regularly verify data accuracy"
            ]
        },
        {
            "id": "storage_limitation",
            "name": "Storage Limitation",
            "description": "Data should be kept only as long as necessary.",
            "article": "Article 5(1)(e)",
            "requirements": [
                "Define retention periods",
                "Implement automatic deletion policies",
                "Document data retention schedules"
            ]
        },
        {
            "id": "integrity_confidentiality",
            "name": "Integrity and Confidentiality",
            "description": "Ensure appropriate security of personal data.",
            "article": "Article 5(1)(f)",
            "requirements": [
                "Implement encryption at rest and in transit",
                "Use access controls and authentication",
                "Regular security audits and testing"
            ]
        }
    ],
    "key_rights": [
        {
            "name": "Right to Access",
            "article": "Article 15",
            "description": "Individuals can request access to their personal data"
        },
        {
            "name": "Right to Rectification",
            "article": "Article 16",
            "description": "Individuals can request correction of inaccurate data"
        },
        {
            "name": "Right to Erasure",
            "article": "Article 17",
            "description": "Right to be forgotten - deletion of personal data"
        },
        {
            "name": "Right to Data Portability",
            "article": "Article 20",
            "description": "Receive personal data in a structured, machine-readable format"
        },
        {
            "name": "Right to Object",
            "article": "Article 21",
            "description": "Object to processing of personal data"
        }
    ],
    "penalties": {
        "tier_1": {
            "amount": "Up to €10 million or 2% of annual global turnover",
            "violations": ["Inadequate data processing records", "Failure to notify breaches"]
        },
        "tier_2": {
            "amount": "Up to €20 million or 4% of annual global turnover",
            "violations": ["Violating core principles", "Violating data subject rights"]
        }
    },
    "breach_notification": {
        "authority_notification": "Within 72 hours of becoming aware",
        "individual_notification": "Without undue delay if high risk to rights and freedoms"
    }
}

# HIPAA Compliance Standards
HIPAA_STANDARDS = {
    "name": "Health Insurance Portability and Accountability Act (HIPAA)",
    "region": "United States",
    "effective_date": "1996-08-21",
    "overview": "US legislation providing data privacy and security provisions for safeguarding medical information.",
    "official_reference": "Public Law 104-191",
    "key_rules": [
        {
            "id": "privacy_rule",
            "name": "Privacy Rule",
            "reference": "45 CFR Part 160 and Part 164, Subparts A and E",
            "description": "Standards for protecting individually identifiable health information (PHI)",
            "requirements": [
                "Limit use and disclosure of PHI",
                "Give patients rights over their health information",
                "Set boundaries on medical record use",
                "Establish safeguards for health information"
            ],
            "covered_entities": ["Healthcare providers", "Health plans", "Healthcare clearinghouses"]
        },
        {
            "id": "security_rule",
            "name": "Security Rule",
            "reference": "45 CFR Part 160 and Part 164, Subparts A and C",
            "description": "National standards to protect electronic PHI (ePHI)",
            "safeguards": [
                {
                    "type": "Administrative",
                    "requirements": [
                        "Security management process",
                        "Security personnel designation",
                        "Workforce training and management",
                        "Risk analysis and management"
                    ]
                },
                {
                    "type": "Physical",
                    "requirements": [
                        "Facility access controls",
                        "Workstation use policies",
                        "Device and media controls"
                    ]
                },
                {
                    "type": "Technical",
                    "requirements": [
                        "Access controls (unique user IDs)",
                        "Audit controls and logging",
                        "Integrity controls",
                        "Transmission security (encryption)"
                    ]
                }
            ]
        },
        {
            "id": "breach_notification",
            "name": "Breach Notification Rule",
            "reference": "45 CFR §§ 164.400-414",
            "description": "Requirements for notifying affected individuals, HHS, and media of breaches",
            "requirements": [
                "Notify affected individuals within 60 days",
                "Notify HHS of breaches affecting 500+ individuals",
                "Notify media for breaches affecting 500+ individuals in a state",
                "Maintain breach log for incidents affecting <500 individuals"
            ]
        }
    ],
    "phi_definition": {
        "description": "Protected Health Information - any health information that can identify an individual",
        "identifiers": [
            "Names", "Dates (birth, admission, discharge, death)",
            "Telephone/fax numbers", "Email addresses",
            "Social Security numbers", "Medical record numbers",
            "Health plan numbers", "Account numbers",
            "IP addresses", "Biometric identifiers",
            "Full-face photos", "Any unique identifying number"
        ]
    },
    "penalties": {
        "tier_1": {
            "amount": "$100 - $50,000 per violation",
            "description": "Unknowing violation"
        },
        "tier_2": {
            "amount": "$1,000 - $50,000 per violation",
            "description": "Reasonable cause"
        },
        "tier_3": {
            "amount": "$10,000 - $50,000 per violation",
            "description": "Willful neglect (corrected)"
        },
        "tier_4": {
            "amount": "$50,000 per violation",
            "description": "Willful neglect (not corrected)",
            "annual_max": "$1.5 million"
        }
    }
}

# PCI-DSS Compliance Standards
PCI_DSS_STANDARDS = {
    "name": "Payment Card Industry Data Security Standard (PCI-DSS)",
    "region": "Global",
    "current_version": "4.0",
    "effective_date": "2022-03-31",
    "transition_deadline": "2024-03-31",
    "overview": "Information security standard for organizations that handle branded credit cards",
    "managed_by": "PCI Security Standards Council",
    "requirements": [
        {
            "id": 1,
            "name": "Install and Maintain Network Security Controls",
            "description": "Protect cardholder data with firewalls and network segmentation",
            "sub_requirements": [
                "1.1 Implement and maintain network security controls",
                "1.2 Configure network security controls",
                "1.3 Restrict network access to trusted environments",
                "1.4 Monitor network traffic leaving trusted environments"
            ]
        },
        {
            "id": 2,
            "name": "Apply Secure Configurations",
            "description": "Remove default credentials and unnecessary services",
            "sub_requirements": [
                "2.1 Configure and maintain secure systems",
                "2.2 Configure system security parameters",
                "2.3 Wireless environments are configured securely"
            ]
        },
        {
            "id": 3,
            "name": "Protect Stored Account Data",
            "description": "Protect cardholder data through encryption and truncation",
            "sub_requirements": [
                "3.1 Keep cardholder data storage to a minimum",
                "3.2 Secure storage of cardholder data",
                "3.3 Secure sensitive authentication data",
                "3.4 Access to displays of full PAN is restricted",
                "3.5 Cardholder data is secured when stored on removable media",
                "3.6 Cryptographic keys used to protect stored account data"
            ],
            "data_protection": {
                "primary_account_number": "Render unreadable (encryption, truncation, hashing)",
                "cardholder_name": "Protect if stored with PAN",
                "expiration_date": "Protect if stored with PAN",
                "service_code": "Protect if stored with PAN"
            },
            "prohibited_storage": [
                "Full magnetic stripe data",
                "CAV2/CVC2/CVV2/CID",
                "PIN/PIN Block"
            ]
        },
        {
            "id": 4,
            "name": "Protect Cardholder Data with Strong Cryptography",
            "description": "Encrypt transmission of cardholder data across open, public networks",
            "sub_requirements": [
                "4.1 Strong cryptography and security protocols",
                "4.2 Secure PANs when transmitted via end-user messaging"
            ]
        },
        {
            "id": 5,
            "name": "Protect Systems Against Malware",
            "description": "Deploy anti-malware solutions",
            "sub_requirements": [
                "5.1 Malware risks are defined and addressed",
                "5.2 Anti-malware solutions are deployed and maintained",
                "5.3 Anti-malware mechanisms are kept current and active"
            ]
        },
        {
            "id": 6,
            "name": "Develop and Maintain Secure Systems",
            "description": "Patch systems and develop secure software",
            "sub_requirements": [
                "6.1 Security vulnerabilities are identified and addressed",
                "6.2 Bespoke and custom software is developed securely",
                "6.3 Security vulnerabilities in applications are addressed",
                "6.4 Public-facing web applications are protected",
                "6.5 Changes to all system components are managed securely"
            ]
        },
        {
            "id": 7,
            "name": "Restrict Access to System Components",
            "description": "Limit access to cardholder data by business need-to-know",
            "sub_requirements": [
                "7.1 Limit access to authorized personnel",
                "7.2 User access to system components is assigned",
                "7.3 User access privileges are managed"
            ]
        },
        {
            "id": 8,
            "name": "Identify Users and Authenticate Access",
            "description": "Assign unique ID to each person with computer access",
            "sub_requirements": [
                "8.1 Unique user IDs for all users",
                "8.2 Strong authentication for users",
                "8.3 Multi-factor authentication (MFA)",
                "8.4 MFA systems are configured to prevent misuse",
                "8.5 Passwords/passphrases meet minimum standards"
            ]
        },
        {
            "id": 9,
            "name": "Restrict Physical Access",
            "description": "Restrict physical access to cardholder data",
            "sub_requirements": [
                "9.1 Processes and mechanisms restrict physical access",
                "9.2 Physical access controls manage entry",
                "9.3 Physical access for personnel and visitors is managed",
                "9.4 Media with cardholder data is securely stored"
            ]
        },
        {
            "id": 10,
            "name": "Log and Monitor All Access",
            "description": "Track and monitor all access to network resources and cardholder data",
            "sub_requirements": [
                "10.1 Processes to log and monitor user activities",
                "10.2 Audit logs record appropriate details",
                "10.3 Audit logs are protected from destruction",
                "10.4 Audit logs are reviewed regularly",
                "10.5 Audit log history is retained",
                "10.6 Time-synchronization mechanisms support logging",
                "10.7 Failures of critical security control systems are detected"
            ]
        },
        {
            "id": 11,
            "name": "Test Security Systems Regularly",
            "description": "Regularly test security systems and processes",
            "sub_requirements": [
                "11.1 Processes to test security controls",
                "11.2 Wireless access points are identified and monitored",
                "11.3 External and internal vulnerabilities are scanned",
                "11.4 Internal and external penetration testing",
                "11.5 Network intrusions and unexpected file changes detected",
                "11.6 Unauthorized changes to payment pages are detected"
            ]
        },
        {
            "id": 12,
            "name": "Support Information Security with Policies",
            "description": "Maintain a policy that addresses information security for all personnel",
            "sub_requirements": [
                "12.1 Information security policy established and published",
                "12.2 Acceptable use policies for technology",
                "12.3 Risks to cardholder data are formally identified",
                "12.4 PCI DSS compliance is managed",
                "12.5 PCI DSS scope is documented and validated",
                "12.6 Security awareness education for personnel",
                "12.7 Personnel screening procedures",
                "12.8 Risk to information assets from third-party providers"
            ]
        }
    ],
    "merchant_levels": {
        "level_1": {
            "description": "Merchants processing over 6 million transactions annually",
            "requirements": ["Annual onsite assessment", "Quarterly network scans"]
        },
        "level_2": {
            "description": "Merchants processing 1-6 million transactions annually",
            "requirements": ["Annual self-assessment questionnaire", "Quarterly network scans"]
        },
        "level_3": {
            "description": "Merchants processing 20,000-1 million e-commerce transactions annually",
            "requirements": ["Annual self-assessment questionnaire", "Quarterly network scans"]
        },
        "level_4": {
            "description": "Merchants processing fewer than 20,000 e-commerce transactions annually",
            "requirements": ["Annual self-assessment questionnaire", "Quarterly network scans"]
        }
    },
    "validation_methods": [
        "Self-Assessment Questionnaire (SAQ)",
        "Attestation of Compliance (AOC)",
        "Report on Compliance (ROC)",
        "Quarterly Network Scans by Approved Scanning Vendor (ASV)"
    ]
}

# Compliance checklist templates
COMPLIANCE_CHECKLISTS = {
    "gdpr": [
        {"id": "gdpr_001", "requirement": "Lawful basis for data processing documented", "category": "Legal Basis"},
        {"id": "gdpr_002", "requirement": "Privacy policy published and accessible", "category": "Transparency"},
        {"id": "gdpr_003", "requirement": "Cookie consent mechanism implemented", "category": "Consent"},
        {"id": "gdpr_004", "requirement": "Data subject rights request process established", "category": "Rights"},
        {"id": "gdpr_005", "requirement": "Data retention policies defined and implemented", "category": "Storage Limitation"},
        {"id": "gdpr_006", "requirement": "Encryption at rest and in transit enabled", "category": "Security"},
        {"id": "gdpr_007", "requirement": "Access controls and authentication implemented", "category": "Security"},
        {"id": "gdpr_008", "requirement": "Data Processing Agreement (DPA) with vendors", "category": "Third Parties"},
        {"id": "gdpr_009", "requirement": "Data Protection Impact Assessment (DPIA) completed", "category": "Risk Assessment"},
        {"id": "gdpr_010", "requirement": "Breach notification procedures documented", "category": "Incident Response"}
    ],
    "hipaa": [
        {"id": "hipaa_001", "requirement": "Risk analysis completed", "category": "Administrative"},
        {"id": "hipaa_002", "requirement": "Risk management plan implemented", "category": "Administrative"},
        {"id": "hipaa_003", "requirement": "Workforce security training completed", "category": "Administrative"},
        {"id": "hipaa_004", "requirement": "Business Associate Agreements (BAA) signed", "category": "Administrative"},
        {"id": "hipaa_005", "requirement": "Facility access controls implemented", "category": "Physical"},
        {"id": "hipaa_006", "requirement": "Workstation security policies enforced", "category": "Physical"},
        {"id": "hipaa_007", "requirement": "Unique user identification assigned", "category": "Technical"},
        {"id": "hipaa_008", "requirement": "Encryption of ePHI at rest and in transit", "category": "Technical"},
        {"id": "hipaa_009", "requirement": "Audit logging and monitoring enabled", "category": "Technical"},
        {"id": "hipaa_010", "requirement": "Breach notification procedures documented", "category": "Incident Response"}
    ],
    "pci_dss": [
        {"id": "pci_001", "requirement": "Firewall configuration protects cardholder data", "category": "Network Security"},
        {"id": "pci_002", "requirement": "Default vendor passwords changed", "category": "Configuration"},
        {"id": "pci_003", "requirement": "Cardholder data storage minimized", "category": "Data Protection"},
        {"id": "pci_004", "requirement": "Cardholder data encrypted in storage", "category": "Data Protection"},
        {"id": "pci_005", "requirement": "Transmission encryption (TLS 1.2+)", "category": "Transmission Security"},
        {"id": "pci_006", "requirement": "Anti-malware software installed and updated", "category": "Malware Protection"},
        {"id": "pci_007", "requirement": "Security patches applied within defined timeframes", "category": "Vulnerability Management"},
        {"id": "pci_008", "requirement": "Access controls limit data access to authorized personnel", "category": "Access Control"},
        {"id": "pci_009", "requirement": "Multi-factor authentication implemented", "category": "Authentication"},
        {"id": "pci_010", "requirement": "Audit logs enabled and reviewed", "category": "Monitoring"},
        {"id": "pci_011", "requirement": "Quarterly vulnerability scans completed", "category": "Testing"},
        {"id": "pci_012", "requirement": "Information security policy documented", "category": "Policy"}
    ]
}

# Cross-reference mapping
COMPLIANCE_CROSS_REFERENCE = {
    "data_encryption": {
        "gdpr": ["Article 5(1)(f) - Integrity and Confidentiality", "Article 32 - Security of Processing"],
        "hipaa": ["Security Rule - Technical Safeguards", "§164.312(a)(2)(iv) Encryption"],
        "pci_dss": ["Requirement 3 - Protect Stored Account Data", "Requirement 4 - Encrypt Transmission"]
    },
    "access_control": {
        "gdpr": ["Article 32(1)(b) - Access Controls"],
        "hipaa": ["§164.312(a)(1) Access Control", "§164.308(a)(4) Information Access Management"],
        "pci_dss": ["Requirement 7 - Restrict Access", "Requirement 8 - Identify Users"]
    },
    "audit_logging": {
        "gdpr": ["Article 32(1)(d) - Security Monitoring"],
        "hipaa": ["§164.312(b) Audit Controls"],
        "pci_dss": ["Requirement 10 - Log and Monitor"]
    },
    "breach_notification": {
        "gdpr": ["Article 33 - Notification to Authority", "Article 34 - Notification to Data Subject"],
        "hipaa": ["§164.404 - Notification to Individuals", "§164.406 - Notification to HHS"],
        "pci_dss": ["Report to payment brands and acquiring bank per brand requirements"]
    },
    "data_retention": {
        "gdpr": ["Article 5(1)(e) - Storage Limitation"],
        "hipaa": ["§164.316(b)(2) - Retention of Documentation (6 years)"],
        "pci_dss": ["Requirement 3.1 - Keep cardholder data storage to minimum"]
    }
}


def get_all_standards() -> Dict[str, Any]:
    """Get all compliance standards"""
    return {
        "gdpr": GDPR_STANDARDS,
        "hipaa": HIPAA_STANDARDS,
        "pci_dss": PCI_DSS_STANDARDS
    }


def get_standard(standard_name: str) -> Dict[str, Any]:
    """Get a specific compliance standard"""
    standards = {
        "gdpr": GDPR_STANDARDS,
        "hipaa": HIPAA_STANDARDS,
        "pci_dss": PCI_DSS_STANDARDS
    }
    return standards.get(standard_name.lower())


def get_checklist(standard_name: str) -> List[Dict[str, str]]:
    """Get compliance checklist for a standard"""
    return COMPLIANCE_CHECKLISTS.get(standard_name.lower(), [])


def get_cross_reference(topic: str) -> Dict[str, List[str]]:
    """Get cross-references for a specific compliance topic"""
    return COMPLIANCE_CROSS_REFERENCE.get(topic.lower(), {})
