"""
PCI-DSS (Payment Card Industry Data Security Standard) Compliance Module
Information security standard for organizations that handle branded credit cards
"""

STANDARD = {
    "name": "Payment Card Industry Data Security Standard (PCI-DSS)",
    "region": "Global",
    "current_version": "4.0",
    "effective_date": "2022-03-31",
    "transition_deadline": "2024-03-31",
    "overview": "Information security standard for organizations that handle branded credit cards from major card schemes",
    "official_reference": "PCI DSS v4.0",
    "authority": "PCI Security Standards Council",
    "website": "https://www.pcisecuritystandards.org/",
    "applicability": "All entities that store, process, or transmit cardholder data",
    
    "requirements": [
        {
            "id": 1,
            "name": "Install and Maintain Network Security Controls",
            "description": "Protect cardholder data with firewalls and network segmentation",
            "sub_requirements": [
                "1.1 Implement and maintain network security controls",
                "1.2 Configure network security controls to restrict connections between untrusted networks and system components",
                "1.3 Restrict network access to trusted environments",
                "1.4 Monitor and control all network traffic leaving trusted environments"
            ],
            "key_controls": [
                "Firewall and router configuration standards",
                "Network segmentation and DMZ",
                "Restrict inbound and outbound traffic",
                "Personal firewall software on mobile devices"
            ]
        },
        {
            "id": 2,
            "name": "Apply Secure Configurations to All System Components",
            "description": "Remove default credentials and unnecessary services",
            "sub_requirements": [
                "2.1 Configure and maintain secure systems and networks",
                "2.2 Configure system security parameters to prevent misuse",
                "2.3 Wireless environments are configured securely (if used)"
            ],
            "key_controls": [
                "Change all vendor-supplied defaults",
                "Remove unnecessary functionality",
                "Implement strong encryption for wireless networks",
                "Configure security parameters to prevent misuse"
            ]
        },
        {
            "id": 3,
            "name": "Protect Stored Account Data",
            "description": "Protect cardholder data through encryption, truncation, masking, and hashing",
            "sub_requirements": [
                "3.1 Keep cardholder data storage and retention to an absolute minimum",
                "3.2 Do not store sensitive authentication data after authorization",
                "3.3 Mask PAN when displayed (first six and last four digits max)",
                "3.4 Render PAN unreadable wherever it is stored",
                "3.5 Protect cryptographic keys used to encrypt cardholder data",
                "3.6 Fully document and implement all key-management processes",
                "3.7 Ensure security policies address cardholder data protection"
            ],
            "data_protection_requirements": {
                "primary_account_number": "Must be rendered unreadable (encryption, truncation, tokenization, hashing)",
                "cardholder_name": "Protect if stored with PAN",
                "expiration_date": "Protect if stored with PAN",
                "service_code": "Protect if stored with PAN"
            },
            "prohibited_storage": [
                "Full magnetic stripe data (track data)",
                "CAV2/CVC2/CVV2/CID (card verification code/value)",
                "PIN/PIN Block (personal identification number or PIN block)"
            ],
            "acceptable_methods": [
                "Strong cryptography with key management",
                "Truncation (hashing cannot be the sole method)",
                "Index tokens and pads",
                "Strong one-way hash functions (SHA-256 or stronger)"
            ]
        },
        {
            "id": 4,
            "name": "Protect Cardholder Data with Strong Cryptography During Transmission",
            "description": "Encrypt transmission of cardholder data across open, public networks",
            "sub_requirements": [
                "4.1 Strong cryptography and security protocols are used to safeguard PAN during transmission",
                "4.2 Never send unprotected PANs via end-user messaging technologies"
            ],
            "key_controls": [
                "TLS 1.2 or higher for transmission over public networks",
                "Never send unencrypted PANs via email, instant messaging, SMS, chat",
                "Ensure wireless networks transmitting cardholder data use strong encryption",
                "Maintain inventory of trusted keys and certificates"
            ],
            "required_protocols": [
                "TLS 1.2 or higher (TLS 1.3 recommended)",
                "SSH v2 or higher",
                "IPsec for VPN connections"
            ]
        },
        {
            "id": 5,
            "name": "Protect All Systems and Networks from Malicious Software",
            "description": "Deploy and maintain anti-malware solutions on all systems",
            "sub_requirements": [
                "5.1 Processes and mechanisms for protecting against malware are defined and understood",
                "5.2 Malicious software is prevented or detected and addressed",
                "5.3 Anti-malware mechanisms and processes are active, maintained, and monitored",
                "5.4 Anti-malware mechanisms cannot be disabled or altered by users"
            ],
            "key_controls": [
                "Anti-virus software on all systems commonly affected by malware",
                "Anti-malware software is kept current",
                "Automatic updates and periodic scans",
                "Audit logs for anti-malware activity"
            ]
        },
        {
            "id": 6,
            "name": "Develop and Maintain Secure Systems and Software",
            "description": "Identify security vulnerabilities and protect systems through patching and secure development",
            "sub_requirements": [
                "6.1 Processes to identify and address security vulnerabilities",
                "6.2 Bespoke and custom software is developed securely",
                "6.3 Security vulnerabilities are identified and addressed",
                "6.4 Public-facing web applications are protected against attacks",
                "6.5 Changes to all system components are managed securely"
            ],
            "key_controls": [
                "Install critical security patches within one month of release",
                "Establish software development processes",
                "Separate development, test, and production environments",
                "Web application firewall (WAF) for public-facing applications",
                "Secure coding training for developers",
                "Review custom code for vulnerabilities"
            ]
        },
        {
            "id": 7,
            "name": "Restrict Access to System Components and Cardholder Data by Business Need to Know",
            "description": "Limit access to cardholder data to only those individuals whose jobs require such access",
            "sub_requirements": [
                "7.1 Processes to limit access to system components and cardholder data",
                "7.2 Access to system components and data is appropriately defined and assigned",
                "7.3 Access to system components and data is managed via access control systems"
            ],
            "key_controls": [
                "Define access rights for each role",
                "Assign access based on job classification and function",
                "Default deny-all setting",
                "Documented approval by authorized parties",
                "Least privilege principle"
            ]
        },
        {
            "id": 8,
            "name": "Identify Users and Authenticate Access to System Components",
            "description": "Assign a unique ID to each person with computer access and authenticate with passwords or MFA",
            "sub_requirements": [
                "8.1 Processes to identify users and authenticate access",
                "8.2 User identification and authentication for non-consumer users and administrators",
                "8.3 Multi-factor authentication (MFA) for all access into the CDE",
                "8.4 MFA systems are configured to prevent misuse",
                "8.5 Passwords/passphrases meet defined requirements for strength"
            ],
            "key_controls": [
                "Assign unique ID to each user",
                "MFA for all access to cardholder data environment (CDE)",
                "MFA for all remote access",
                "Password complexity: minimum 12 characters (or 8 characters with complexity)",
                "Password/passphrase history: prevent reuse of last 4 passwords",
                "Account lockout after 6 failed login attempts",
                "Lockout duration minimum 30 minutes or until admin reset"
            ]
        },
        {
            "id": 9,
            "name": "Restrict Physical Access to Cardholder Data",
            "description": "Physical access to cardholder data or systems must be appropriately restricted",
            "sub_requirements": [
                "9.1 Processes to restrict physical access to cardholder data",
                "9.2 Physical access controls manage entry into facilities and systems",
                "9.3 Physical access for personnel and visitors is authorized and managed",
                "9.4 Media containing cardholder data is securely stored, accessed, and inventoried",
                "9.5 Point-of-interaction (POI) devices are protected from tampering and unauthorized substitution"
            ],
            "key_controls": [
                "Video cameras or access control mechanisms monitor entry/exit",
                "Visitor badges that expire and clearly distinguish visitors",
                "Physically secure all media containing cardholder data",
                "Maintain strict control over distribution of media",
                "Destroy cardholder data when no longer needed",
                "Maintain POI device inventory and inspect regularly"
            ]
        },
        {
            "id": 10,
            "name": "Log and Monitor All Access to System Components and Cardholder Data",
            "description": "Track and monitor all access to network resources and cardholder data",
            "sub_requirements": [
                "10.1 Processes to log and monitor all access to system components and cardholder data",
                "10.2 Audit logs are implemented to support anomaly detection",
                "10.3 Audit logs are protected from destruction and unauthorized modification",
                "10.4 Audit logs are reviewed to identify anomalies or suspicious activity",
                "10.5 Audit log history is retained and available for analysis",
                "10.6 Time-synchronization mechanisms support consistent logging",
                "10.7 Failures of critical security control systems are detected, reported, and responded to"
            ],
            "required_log_entries": [
                "User identification",
                "Type of event",
                "Date and time",
                "Success or failure indication",
                "Origination of event",
                "Identity or name of affected data, system component, resource, or service"
            ],
            "key_controls": [
                "Implement automated audit trails for all system components",
                "Review logs at least daily",
                "Retain audit log history for at least one year",
                "Use time-synchronization technology (e.g., NTP)",
                "Secure authentication and integrity of logs"
            ]
        },
        {
            "id": 11,
            "name": "Test Security of Systems and Networks Regularly",
            "description": "Regularly test security systems and processes to identify vulnerabilities",
            "sub_requirements": [
                "11.1 Processes to test security of systems and networks regularly",
                "11.2 Wireless access points are identified and monitored",
                "11.3 Vulnerabilities are identified via security testing",
                "11.4 External and internal penetration testing is performed",
                "11.5 Network intrusions and unexpected file changes are detected and responded to",
                "11.6 Unauthorized changes on payment pages are detected and responded to"
            ],
            "key_controls": [
                "Quarterly internal vulnerability scans",
                "Quarterly external vulnerability scans by Approved Scanning Vendor (ASV)",
                "Internal and external penetration testing at least annually",
                "Implement intrusion-detection/prevention systems (IDS/IPS)",
                "Deploy file integrity monitoring (FIM)",
                "Implement change detection for payment pages"
            ]
        },
        {
            "id": 12,
            "name": "Support Information Security with Organizational Policies and Programs",
            "description": "Maintain a policy that addresses information security for all personnel",
            "sub_requirements": [
                "12.1 Information security policy is established and published",
                "12.2 Acceptable use policies for end-user technologies",
                "12.3 Risks to the cardholder data environment are formally identified and managed",
                "12.4 PCI DSS compliance is managed",
                "12.5 PCI DSS scope is documented and validated",
                "12.6 Security awareness education is an ongoing activity",
                "12.7 Personnel are screened to reduce risks from insider threats",
                "12.8 Risk to information assets associated with third-party service providers (TPSPs) is managed"
            ],
            "key_controls": [
                "Annual information security policy review",
                "Security awareness training for all personnel upon hire and annually",
                "Formal risk assessment process at least annually",
                "Maintain and distribute security policy to all personnel",
                "Incident response plan in place and tested annually",
                "Background checks for personnel with access to cardholder data"
            ]
        }
    ],
    
    "merchant_levels": {
        "level_1": {
            "description": "Merchants processing over 6 million card transactions annually (all channels) or identified as Level 1 by any card brand",
            "validation_requirements": [
                "Annual Report on Compliance (ROC) by Qualified Security Assessor (QSA)",
                "Quarterly network scans by Approved Scanning Vendor (ASV)",
                "Attestation of Compliance"
            ]
        },
        "level_2": {
            "description": "Merchants processing 1-6 million card transactions annually (all channels)",
            "validation_requirements": [
                "Annual Self-Assessment Questionnaire (SAQ)",
                "Quarterly network scans by ASV",
                "Attestation of Compliance"
            ]
        },
        "level_3": {
            "description": "Merchants processing 20,000 to 1 million e-commerce transactions annually",
            "validation_requirements": [
                "Annual Self-Assessment Questionnaire (SAQ)",
                "Quarterly network scans by ASV",
                "Attestation of Compliance"
            ]
        },
        "level_4": {
            "description": "Merchants processing fewer than 20,000 e-commerce transactions annually or up to 1 million total transactions annually",
            "validation_requirements": [
                "Annual Self-Assessment Questionnaire (SAQ)",
                "Quarterly network scans by ASV (if applicable)",
                "Attestation of Compliance"
            ]
        }
    },
    
    "service_provider_levels": {
        "level_1": {
            "description": "Service providers processing over 300,000 transactions annually",
            "requirements": "Annual ROC by QSA"
        },
        "level_2": {
            "description": "Service providers processing fewer than 300,000 transactions annually",
            "requirements": "Annual SAQ"
        }
    },
    
    "validation_methods": [
        "Self-Assessment Questionnaire (SAQ) - 9 different types based on environment",
        "Attestation of Compliance (AOC) - Completed annually",
        "Report on Compliance (ROC) - Required for Level 1 merchants and service providers",
        "Quarterly Network Scans by Approved Scanning Vendor (ASV)"
    ],
    
    "saq_types": {
        "SAQ_A": "Card-not-present merchants using third-party payment processor (no storage, processing, or transmission)",
        "SAQ_A_EP": "E-commerce merchants with payment page hosted by third-party",
        "SAQ_B": "Merchants using imprint machines or standalone dial-out terminals",
        "SAQ_B_IP": "Merchants using standalone, PTS-approved payment terminals with IP connection",
        "SAQ_C": "Merchants with payment application systems connected to the Internet (no electronic storage)",
        "SAQ_C_VT": "Merchants using web-based virtual terminals (no electronic storage)",
        "SAQ_D_Merchant": "All other merchants not included in above categories",
        "SAQ_D_Service_Provider": "All service providers"
    },
    
    "penalties": {
        "non_compliance_fines": {
            "level_1": "$5,000 - $100,000 per month",
            "level_2": "$5,000 - $50,000 per month",
            "level_3_4": "$5,000 - $25,000 per month"
        },
        "breach_costs": {
            "card_reissuance": "$5 - $10 per card",
            "forensic_investigation": "$50,000 - $500,000+",
            "legal_fees": "Variable, potentially millions",
            "reputation_damage": "Immeasurable",
            "customer_notification": "$5 - $15 per customer"
        },
        "additional_consequences": [
            "Termination of ability to accept payment cards",
            "Increased transaction fees",
            "Required audits at merchant expense",
            "Legal liability for compromised data",
            "Loss of customer trust and business"
        ]
    },
    
    "breach_notification": {
        "immediate_actions": [
            "Contact acquiring bank immediately",
            "Engage PCI Forensic Investigator (PFI) if applicable",
            "Preserve evidence for forensic investigation",
            "Contain the breach and eliminate vulnerabilities",
            "Contact card brands' incident response teams"
        ],
        "timeline": "Immediate notification to acquiring bank upon suspicion of breach",
        "forensic_investigation": "Required for confirmed breaches; must be conducted by PCI Forensic Investigator (PFI)"
    },
    
    "checklist": [
        {"id": "pci_001", "requirement": "Firewall configuration standards document network security controls", "category": "Network Security", "requirement_ref": "Requirement 1"},
        {"id": "pci_002", "requirement": "All vendor-supplied defaults changed (passwords, SNMP strings, etc.)", "category": "Configuration", "requirement_ref": "Requirement 2"},
        {"id": "pci_003", "requirement": "Cardholder data storage minimized to business-justified need", "category": "Data Protection", "requirement_ref": "Requirement 3"},
        {"id": "pci_004", "requirement": "PAN rendered unreadable wherever stored (encrypted/tokenized/hashed)", "category": "Data Protection", "requirement_ref": "Requirement 3"},
        {"id": "pci_005", "requirement": "Transmission encryption (TLS 1.2+) for cardholder data over public networks", "category": "Transmission Security", "requirement_ref": "Requirement 4"},
        {"id": "pci_006", "requirement": "Anti-malware software installed, updated, and generating logs", "category": "Malware Protection", "requirement_ref": "Requirement 5"},
        {"id": "pci_007", "requirement": "Critical security patches applied within 30 days of release", "category": "Vulnerability Management", "requirement_ref": "Requirement 6"},
        {"id": "pci_008", "requirement": "Access controls restrict data access to need-to-know", "category": "Access Control", "requirement_ref": "Requirement 7"},
        {"id": "pci_009", "requirement": "Unique user IDs assigned; multi-factor authentication implemented", "category": "Authentication", "requirement_ref": "Requirement 8"},
        {"id": "pci_010", "requirement": "Physical access controls protect cardholder data environment", "category": "Physical Security", "requirement_ref": "Requirement 9"},
        {"id": "pci_011", "requirement": "Audit logs enabled, protected from tampering, reviewed daily", "category": "Monitoring", "requirement_ref": "Requirement 10"},
        {"id": "pci_012", "requirement": "Quarterly internal and external vulnerability scans completed", "category": "Testing", "requirement_ref": "Requirement 11"},
        {"id": "pci_013", "requirement": "Annual penetration testing (internal and external) performed", "category": "Testing", "requirement_ref": "Requirement 11"},
        {"id": "pci_014", "requirement": "Information security policy documented, reviewed annually, distributed", "category": "Policy", "requirement_ref": "Requirement 12"},
        {"id": "pci_015", "requirement": "Security awareness training provided to all personnel annually", "category": "Training", "requirement_ref": "Requirement 12"}
    ],
    
    "key_definitions": {
        "PAN": "Primary Account Number - Unique payment card number (typically 13-19 digits) that identifies the issuer and cardholder account",
        "CDE": "Cardholder Data Environment - Network segments, systems, and applications that store, process, or transmit cardholder data",
        "CHD": "Cardholder Data - At minimum, PAN. May also include cardholder name, expiration date, and/or service code",
        "SAD": "Sensitive Authentication Data - Security-related information (CAV2/CVV2/CVC2/CID, full track data, PIN/PIN block) used to authenticate cardholders",
        "QSA": "Qualified Security Assessor - Company certified by PCI SSC to conduct PCI DSS assessments",
        "ASV": "Approved Scanning Vendor - Company approved by PCI SSC to conduct external vulnerability scanning services",
        "SAQ": "Self-Assessment Questionnaire - Validation tool for merchants and service providers to self-evaluate PCI DSS compliance",
        "AOC": "Attestation of Compliance - Form to document results of PCI DSS assessment",
        "ROC": "Report on Compliance - Form used to document detailed compliance validation for entities undergoing on-site PCI DSS review"
    }
}

MODULE_INFO = {
    "module_type": "compliance_standard",
    "last_updated": "2024-03-04",
    "maintainer": "Compliance Team",
    "tags": ["payment", "finance", "credit cards", "security", "global", "retail", "e-commerce"],
    "industry": "Payment Processing / Retail / E-commerce",
    "related_standards": ["ISO 27001", "NIST Cybersecurity Framework"],
    "version_notes": "PCI DSS v4.0 became effective March 31, 2022 with transition deadline March 31, 2024"
}
