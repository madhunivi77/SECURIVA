"""
HIPAA (Health Insurance Portability and Accountability Act) Compliance Module
Healthcare data privacy and security standard for the United States
"""

STANDARD = {
    "name": "Health Insurance Portability and Accountability Act (HIPAA)",
    "region": "United States",
    "effective_date": "1996-08-21",
    "version": "Public Law 104-191",
    "overview": "US legislation providing data privacy and security provisions for safeguarding medical information.",
    "official_reference": "Public Law 104-191",
    "authority": "Department of Health and Human Services (HHS), Office for Civil Rights (OCR)",
    "website": "https://www.hhs.gov/hipaa/index.html",
    
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
            "covered_entities": [
                "Healthcare providers",
                "Health plans",
                "Healthcare clearinghouses"
            ],
            "patient_rights": [
                "Right to access medical records",
                "Right to request corrections",
                "Right to receive notice of privacy practices",
                "Right to request restrictions on PHI use",
                "Right to request confidential communications",
                "Right to receive accounting of disclosures"
            ]
        },
        {
            "id": "security_rule",
            "name": "Security Rule",
            "reference": "45 CFR Part 160 and Part 164, Subparts A and C",
            "description": "National standards to protect electronic PHI (ePHI)",
            "safeguards": [
                {
                    "type": "Administrative",
                    "description": "Policies and procedures to manage security measures",
                    "requirements": [
                        "Security management process (risk analysis, risk management, sanction policy, information system activity review)",
                        "Security personnel designation (security official)",
                        "Workforce security (authorization, supervision, termination, access management)",
                        "Information access management (authorization and access establishment)",
                        "Security awareness and training",
                        "Security incident procedures",
                        "Contingency plan (data backup, disaster recovery, emergency mode)",
                        "Business associate contracts"
                    ]
                },
                {
                    "type": "Physical",
                    "description": "Physical measures to protect electronic systems and buildings",
                    "requirements": [
                        "Facility access controls (contingency operations, facility security plan, access control/validation)",
                        "Workstation use policies (proper functions and physical attributes)",
                        "Workstation security (restrict physical access)",
                        "Device and media controls (disposal, media re-use, accountability, data backup/storage)"
                    ]
                },
                {
                    "type": "Technical",
                    "description": "Technology and policy to protect ePHI and control access",
                    "requirements": [
                        "Access controls (unique user IDs, emergency access procedure, automatic logoff, encryption/decryption)",
                        "Audit controls and logging (hardware, software, procedural mechanisms)",
                        "Integrity controls (mechanisms to authenticate ePHI is not altered/destroyed)",
                        "Person or entity authentication (verify identity)",
                        "Transmission security (encryption, integrity controls for ePHI transmission)"
                    ]
                }
            ],
            "implementation_specifications": {
                "required": [
                    "Unique User Identification",
                    "Emergency Access Procedure",
                    "Automatic Logoff",
                    "Audit Controls",
                    "Integrity",
                    "Person or Entity Authentication"
                ],
                "addressable": [
                    "Encryption and Decryption",
                    "Mechanism to Authenticate ePHI",
                    "Integrity Controls (transmission)"
                ]
            }
        },
        {
            "id": "breach_notification",
            "name": "Breach Notification Rule",
            "reference": "45 CFR §§ 164.400-414",
            "description": "Requirements for notifying affected individuals, HHS, and media of breaches",
            "requirements": [
                "Notify affected individuals within 60 days",
                "Notify HHS of breaches affecting 500+ individuals without unreasonable delay (within 60 days)",
                "Notify media for breaches affecting 500+ individuals in a state or jurisdiction",
                "Maintain breach log for incidents affecting <500 individuals (annual reporting to HHS)"
            ],
            "breach_definition": "Unauthorized acquisition, access, use, or disclosure of PHI that compromises the security or privacy of the information",
            "exceptions": [
                "Unintentional acquisition/access by workforce acting in good faith",
                "Inadvertent disclosure within covered entity",
                "Disclosure where information cannot reasonably be retained"
            ],
            "risk_assessment_factors": [
                "Nature and extent of PHI involved",
                "Unauthorized person who used/received the PHI",
                "Whether PHI was actually acquired or viewed",
                "Extent to which risk has been mitigated"
            ]
        },
        {
            "id": "omnibus_rule",
            "name": "HITECH Omnibus Rule",
            "reference": "45 CFR Parts 160 and 164",
            "effective_date": "2013-09-23",
            "description": "Strengthened privacy and security protections under HITECH Act",
            "key_changes": [
                "Business associates directly liable for compliance",
                "Breach notification requirements expanded",
                "Increased penalties for violations",
                "Prohibition on sale of PHI without authorization",
                "Marketing restrictions strengthened",
                "Genetic information restrictions"
            ]
        }
    ],
    
    "phi_definition": {
        "description": "Protected Health Information - any health information that can identify an individual",
        "scope": "Information created, received, maintained, or transmitted by covered entities and business associates",
        "identifiers": [
            "Names",
            "Dates (birth, admission, discharge, death)",
            "Telephone/fax numbers",
            "Email addresses",
            "Social Security numbers",
            "Medical record numbers",
            "Health plan numbers",
            "Account numbers",
            "Certificate/license numbers",
            "Vehicle identifiers and serial numbers",
            "Device identifiers and serial numbers",
            "Web URLs",
            "IP addresses",
            "Biometric identifiers (fingerprints, voiceprints)",
            "Full-face photos and comparable images",
            "Any other unique identifying number, characteristic, or code"
        ],
        "de_identification_methods": [
            "Expert determination (statistical analysis)",
            "Safe harbor method (remove 18 identifiers)"
        ]
    },
    
    "penalties": {
        "tier_1": {
            "amount": "$100 - $50,000 per violation",
            "description": "Unknowing violation",
            "annual_max": "$25,000 per violation type per year"
        },
        "tier_2": {
            "amount": "$1,000 - $50,000 per violation",
            "description": "Reasonable cause (should have known but couldn't avoid)",
            "annual_max": "$100,000 per violation type per year"
        },
        "tier_3": {
            "amount": "$10,000 - $50,000 per violation",
            "description": "Willful neglect that was corrected within 30 days",
            "annual_max": "$250,000 per violation type per year"
        },
        "tier_4": {
            "amount": "$50,000 per violation",
            "description": "Willful neglect not corrected within 30 days",
            "annual_max": "$1.5 million per violation type per year"
        },
        "criminal_penalties": {
            "tier_1": "Up to $50,000 and 1 year in prison (reasonable cause or no knowledge)",
            "tier_2": "Up to $100,000 and 5 years in prison (obtained under false pretenses)",
            "tier_3": "Up to $250,000 and 10 years in prison (intent to sell, transfer, or misuse)"
        }
    },
    
    "breach_notification": {
        "individual_notification": "Within 60 days of discovery",
        "hhs_notification": {
            "large_breach": "Within 60 days (500+ individuals)",
            "small_breach": "Annual log submission (fewer than 500 individuals)"
        },
        "media_notification": "Prominent media outlet serving state/jurisdiction (500+ individuals in area)",
        "notification_content": [
            "Description of what happened and when",
            "Types of PHI involved",
            "Steps individuals should take to protect themselves",
            "What the entity is doing to investigate and mitigate",
            "Contact information for questions"
        ]
    },
    
    "business_associate_requirements": {
        "baa_required": True,
        "description": "Written agreement between covered entity and business associate",
        "must_include": [
            "Permitted uses and disclosures of PHI",
            "Requirement to implement safeguards",
            "Requirement to report security incidents",
            "Requirement to ensure subcontractors comply",
            "Requirement to return or destroy PHI at contract termination",
            "Authorization for covered entity to take action if breach occurs"
        ],
        "examples_of_business_associates": [
            "IT service providers",
            "Billing companies",
            "Claims processors",
            "Medical transcription services",
            "Cloud storage providers",
            "Shredding companies",
            "Consultants with access to PHI"
        ]
    },
    
    "checklist": [
        {"id": "hipaa_001", "requirement": "Risk analysis completed and documented", "category": "Administrative", "rule": "Security Rule"},
        {"id": "hipaa_002", "requirement": "Risk management plan implemented", "category": "Administrative", "rule": "Security Rule"},
        {"id": "hipaa_003", "requirement": "Workforce security training completed annually", "category": "Administrative", "rule": "Security Rule"},
        {"id": "hipaa_004", "requirement": "Business Associate Agreements (BAA) signed with all vendors", "category": "Administrative", "rule": "Privacy Rule"},
        {"id": "hipaa_005", "requirement": "Privacy Officer and Security Officer designated", "category": "Administrative", "rule": "Privacy & Security Rule"},
        {"id": "hipaa_006", "requirement": "Notice of Privacy Practices (NPP) provided to patients", "category": "Administrative", "rule": "Privacy Rule"},
        {"id": "hipaa_007", "requirement": "Facility access controls implemented and monitored", "category": "Physical", "rule": "Security Rule"},
        {"id": "hipaa_008", "requirement": "Workstation security policies enforced", "category": "Physical", "rule": "Security Rule"},
        {"id": "hipaa_009", "requirement": "Unique user identification assigned to all users", "category": "Technical", "rule": "Security Rule"},
        {"id": "hipaa_010", "requirement": "Encryption of ePHI at rest and in transit", "category": "Technical", "rule": "Security Rule"},
        {"id": "hipaa_011", "requirement": "Audit logging and monitoring enabled on all systems", "category": "Technical", "rule": "Security Rule"},
        {"id": "hipaa_012", "requirement": "Automatic logoff after period of inactivity", "category": "Technical", "rule": "Security Rule"},
        {"id": "hipaa_013", "requirement": "Data backup and disaster recovery plan in place", "category": "Contingency", "rule": "Security Rule"},
        {"id": "hipaa_014", "requirement": "Breach notification procedures documented and tested", "category": "Incident Response", "rule": "Breach Notification Rule"},
        {"id": "hipaa_015", "requirement": "Patient rights request procedures established", "category": "Privacy", "rule": "Privacy Rule"}
    ],
    
    "common_violations": [
        {
            "violation": "Unauthorized access to PHI",
            "example": "Employee accessing records without legitimate reason",
            "prevention": "Role-based access controls, audit logs, training"
        },
        {
            "violation": "Lack of encryption",
            "example": "Unencrypted laptops, mobile devices, or transmissions",
            "prevention": "Implement full-disk encryption and TLS for transmissions"
        },
        {
            "violation": "Missing Business Associate Agreement",
            "example": "Working with vendors without signed BAA",
            "prevention": "Inventory all vendors with PHI access and obtain BAAs"
        },
        {
            "violation": "Inadequate risk analysis",
            "example": "No documented risk analysis or outdated assessment",
            "prevention": "Conduct annual comprehensive risk analysis"
        },
        {
            "violation": "Delayed breach notification",
            "example": "Notifying individuals beyond 60-day deadline",
            "prevention": "Establish incident response plan with clear timelines"
        }
    ]
}

# Module metadata
MODULE_INFO = {
    "module_type": "compliance_standard",
    "last_updated": "2024-03-04",
    "maintainer": "Compliance Team",
    "tags": ["healthcare", "privacy", "security", "phi", "us", "medical"],
    "related_modules": ["gdpr"],
    "industry": "Healthcare"
}
