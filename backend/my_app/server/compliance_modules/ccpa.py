"""
California Consumer Privacy Act (CCPA)
As amended by the California Privacy Rights Act (CPRA)
Effective: January 1, 2020 | CPRA Amendments: January 1, 2023
"""

STANDARD = {
    "name": "California Consumer Privacy Act (CCPA/CPRA)",
    "region": "California, United States",
    "effective_date": "2020-01-01",
    "version": "As Amended by CPRA 2023",
    "overview": "California law that grants consumers rights over their personal information and imposes obligations on businesses that collect consumer data. Applies to for-profit businesses doing business in California with gross revenues over $25M, buying/selling personal info of 50K+ consumers, or deriving 50%+ revenue from selling personal info.",
    
    "key_provisions": {
        "applicability": {
            "business_thresholds": [
                "Annual gross revenues exceed $25 million",
                "Buys, sells, or shares personal information of 100,000+ consumers/households annually",
                "Derives 50% or more of annual revenue from selling or sharing personal information"
            ],
            "geographic_scope": "Applies to businesses that collect personal information from California residents, regardless of business location"
        },
        
        "personal_information_definition": {
            "description": "Information that identifies, relates to, describes, or is capable of being associated with a particular consumer or household",
            "categories": [
                "Identifiers (name, email, IP address, device ID)",
                "Commercial information (purchase history, preferences)",
                "Biometric information",
                "Internet/network activity (browsing history, search history)",
                "Geolocation data",
                "Audio, electronic, visual, or similar information",
                "Professional or employment-related information",
                "Education information",
                "Inferences (profiles, preferences, behavior)"
            ],
            "sensitive_personal_information": [
                "Social Security number, driver's license, passport number",
                "Account login credentials",
                "Precise geolocation data",
                "Racial or ethnic origin",
                "Religious or philosophical beliefs",
                "Union membership",
                "Genetic data",
                "Biometric data for unique identification",
                "Health information",
                "Sex life or sexual orientation information"
            ]
        }
    },
    
    "consumer_rights": [
        {
            "id": "right_to_know",
            "name": "Right to Know",
            "description": "Consumers can request disclosure of what personal information a business collects, uses, discloses, and sells",
            "reference": "CCPA §1798.100",
            "requirements": [
                "Provide categories of personal information collected",
                "Provide specific pieces of personal information collected",
                "Disclose categories of sources",
                "Disclose business or commercial purpose",
                "Disclose categories of third parties with whom information is shared"
            ],
            "response_time": "45 days (extendable by 45 days with notice)",
            "format": "Must deliver information in a readily usable format (electronic preferred)",
            "implementation": [
                "Establish verified request process",
                "Maintain data inventory and mapping",
                "Create consumer-facing request portal",
                "Train staff on access request procedures"
            ]
        },
        {
            "id": "right_to_delete",
            "name": "Right to Delete",
            "description": "Consumers can request deletion of personal information collected from them",
            "reference": "CCPA §1798.105",
            "requirements": [
                "Delete consumer's personal information from records",
                "Direct service providers to delete the information",
                "Verify consumer identity before deletion"
            ],
            "exceptions": [
                "Complete the transaction for which information was collected",
                "Detect security incidents or protect against illegal activity",
                "Debug or repair errors",
                "Exercise free speech or ensure another's right to free speech",
                "Comply with California Electronic Communications Privacy Act",
                "Engage in public or peer-reviewed research",
                "Enable internal uses reasonably aligned with consumer expectations",
                "Comply with legal obligation",
                "Make other internal and lawful uses compatible with context"
            ],
            "response_time": "45 days (extendable by 45 days with notice)",
            "implementation": [
                "Implement secure deletion procedures",
                "Notify service providers of deletion requests",
                "Log deletion requests and actions taken",
                "Verify requester identity (2+ data points)"
            ]
        },
        {
            "id": "right_to_correct",
            "name": "Right to Correct",
            "reference": "CPRA §1798.106",
            "description": "Consumers can request correction of inaccurate personal information",
            "requirements": [
                "Correct inaccurate personal information",
                "Direct service providers to correct the information",
                "Maintain reasonable security procedures"
            ],
            "response_time": "45 days (extendable by 45 days with notice)",
            "implementation": [
                "Establish correction request process",
                "Verify accuracy of requested corrections",
                "Update data across all systems",
                "Notify third parties of corrections where feasible"
            ]
        },
        {
            "id": "right_to_opt_out",
            "name": "Right to Opt-Out of Sale/Sharing",
            "reference": "CCPA §1798.120",
            "description": "Consumers can opt-out of the sale or sharing of their personal information",
            "requirements": [
                "Provide clear 'Do Not Sell or Share My Personal Information' link on homepage",
                "Allow opt-out without requiring account creation",
                "Wait at least 12 months before asking to opt back in",
                "For consumers under 16, require opt-IN (not opt-out)"
            ],
            "implementation": [
                "Add prominent opt-out link on website homepage",
                "Implement opt-out signal processing (e.g., Global Privacy Control)",
                "Update internal systems to respect opt-out status",
                "Train sales/marketing teams on opt-out requirements"
            ]
        },
        {
            "id": "right_to_limit_sensitive_pi",
            "name": "Right to Limit Use of Sensitive Personal Information",
            "reference": "CPRA §1798.121",
            "description": "Consumers can limit business's use of sensitive personal information",
            "requirements": [
                "Provide 'Limit the Use of My Sensitive Personal Information' link if applicable",
                "Only use sensitive PI for authorized purposes after request",
                "Respond to limit requests within 15 days"
            ],
            "authorized_uses": [
                "Performing services reasonably expected",
                "Preventing, detecting, and investigating security incidents",
                "Resisting malicious, fraudulent, or illegal actions",
                "Ensuring physical safety",
                "Short-term, transient use",
                "Performing services on behalf of business (service provider context)",
                "Quality or safety verification"
            ],
            "implementation": [
                "Identify if you use sensitive personal information",
                "Add limit link to privacy policy if applicable",
                "Implement controls to restrict sensitive PI usage",
                "Update data processing procedures"
            ]
        },
        {
            "id": "right_to_non_discrimination",
            "name": "Right to Non-Discrimination",
            "reference": "CCPA §1798.125",
            "description": "Businesses cannot discriminate against consumers for exercising CCPA rights",
            "prohibited_actions": [
                "Denying goods or services",
                "Charging different prices or rates",
                "Providing different level or quality of goods/services",
                "Suggesting consumer will receive different price or quality"
            ],
            "permitted_differences": [
                "Offering financial incentive reasonably related to data value",
                "Charging different price if difference is reasonably related to value provided by consumer data"
            ],
            "implementation": [
                "Review pricing and service tiers for discrimination",
                "Ensure consistent treatment across all consumers",
                "Document any financial incentive programs",
                "Train customer service on non-discrimination requirements"
            ]
        }
    ],
    
    "business_obligations": [
        {
            "obligation": "Privacy Notice at Collection",
            "reference": "CCPA §1798.100(b)",
            "description": "Must inform consumers about data collection at or before collection",
            "required_disclosures": [
                "Categories of personal information collected",
                "Purposes for which information is used",
                "Whether information is sold or shared",
                "Length of time information is retained (or criteria to determine)"
            ]
        },
        {
            "obligation": "Privacy Policy",
            "reference": "CCPA §1798.130(a)(5)",
            "description": "Must maintain comprehensive privacy policy updated at least annually",
            "required_content": [
                "Categories of personal information collected",
                "Categories of sources",
                "Business or commercial purposes",
                "Categories of third parties with whom information is shared",
                "Consumer rights and how to exercise them",
                "Instructions for submitting requests"
            ]
        },
        {
            "obligation": "Respond to Consumer Requests",
            "description": "Must provide accessible means for consumers to submit requests and respond within required timeframes",
            "requirements": [
                "Provide 2+ methods for submitting requests (toll-free number and website)",
                "Respond substantively within 45 days (extendable by 45 days)",
                "Verify consumer identity for requests",
                "Free for consumers (up to 2 requests per 12-month period)"
            ]
        },
        {
            "obligation": "Data Security",
            "reference": "CCPA §1798.150",
            "description": "Implement reasonable security procedures and practices",
            "requirements": [
                "Protect against unauthorized access, destruction, use, modification, or disclosure",
                "Security measures appropriate to nature of personal information",
                "Maintain security incident response procedures"
            ]
        },
        {
            "obligation": "Service Provider Contracts",
            "reference": "CCPA §1798.140(w)",
            "description": "Contracts with service providers must include specific provisions",
            "required_contract_terms": [
                "Prohibit service provider from selling personal information",
                "Prohibit service provider from retaining, using, or disclosing personal information for any purpose other than performing services",
                "Require service provider to certify compliance with CCPA restrictions",
                "Grant business right to monitor compliance and take corrective action"
            ]
        },
        {
            "obligation": "Do Not Sell/Share Link",
            "reference": "CCPA §1798.135",
            "description": "If selling or sharing personal information, must provide clear opt-out mechanism",
            "requirements": [
                "Display 'Do Not Sell or Share My Personal Information' link on homepage",
                "Link must be clear and conspicuous",
                "Allow opt-out without account creation",
                "Respect Global Privacy Control signals"
            ]
        }
    ],
    
    "penalties": {
        "administrative": {
            "intentional_violation": {
                "amount": "$7,500 per violation",
                "issued_by": "California Attorney General"
            },
            "unintentional_violation": {
                "amount": "$2,500 per violation",
                "issued_by": "California Attorney General"
            },
            "cure_period": "30 days to cure after notice (if curable)"
        },
        "private_right_of_action": {
            "trigger": "Data breach resulting from business's violation of duty to implement reasonable security",
            "damages": "$100 to $750 per consumer per incident, or actual damages (whichever is greater)",
            "requirements": [
                "Provide 30 days written notice to business and Attorney General",
                "Business has 30 days to cure breach (if curable)",
                "Class action lawsuits permitted"
            ]
        },
        "cpra_enforcement_changes": {
            "agency": "California Privacy Protection Agency (CPPA) - new enforcement agency as of July 1, 2023",
            "increased_penalties": "Administrative penalties increased for violations involving minors"
        }
    },
    
    "breach_notification": {
        "trigger": "Unauthorized access, acquisition, or disclosure of personal information",
        "timeline": "Without unreasonable delay (specific timeline not mandated by CCPA, see Civil Code §1798.82)",
        "notification_requirements": [
            "Notify affected California residents",
            "Notify Attorney General if breach affects 500+ residents",
            "Include: Type of information compromised, contact info for business, toll-free numbers for credit bureaus"
        ],
        "related_law": "California Civil Code §1798.82 governs breach notification specifics"
    },
    
    "checklist": [
        {
            "category": "Assessment",
            "items": [
                "Determine if CCPA applies to your business (revenue, data volume thresholds)",
                "Identify all personal information collected, used, and disclosed",
                "Map data flows and third-party relationships",
                "Identify sensitive personal information processing"
            ]
        },
        {
            "category": "Privacy Notices",
            "items": [
                "Create/update privacy notice at collection",
                "Create/update comprehensive privacy policy",
                "Ensure policies are clear, accessible, and updated annually",
                "Add required disclosures about data sales/sharing"
            ]
        },
        {
            "category": "Consumer Rights Infrastructure",
            "items": [
                "Establish 2+ methods for submitting requests (website, toll-free number)",
                "Implement identity verification procedures",
                "Create processes for responding within 45-day window",
                "Set up deletion and correction workflows",
                "Implement opt-out mechanisms (sale, sharing, sensitive PI)"
            ]
        },
        {
            "category": "Website Updates",
            "items": [
                "Add 'Do Not Sell or Share My Personal Information' link to homepage (if applicable)",
                "Add 'Limit the Use of My Sensitive Personal Information' link (if applicable)",
                "Implement Global Privacy Control (GPC) signal recognition",
                "Ensure privacy policy is easily accessible"
            ]
        },
        {
            "category": "Contracts & Vendors",
            "items": [
                "Review and update service provider contracts with required CCPA provisions",
                "Review vendor data practices for CCPA compliance",
                "Ensure data processing addenda with third parties",
                "Document legitimate business purposes for data sharing"
            ]
        },
        {
            "category": "Data Security",
            "items": [
                "Implement reasonable security measures for personal information",
                "Encrypt sensitive data in transit and at rest",
                "Conduct regular security assessments",
                "Maintain incident response plan for data breaches"
            ]
        },
        {
            "category": "Training & Governance",
            "items": [
                "Train customer-facing staff on CCPA rights and request handling",
                "Train IT and security teams on data protection requirements",
                "Designate compliance owner/team",
                "Document compliance procedures and maintain records"
            ]
        },
        {
            "category": "Ongoing Compliance",
            "items": [
                "Review and update privacy notices annually",
                "Monitor for CPPA guidance and enforcement actions",
                "Audit third-party compliance with CCPA requirements",
                "Track and log consumer requests and responses",
                "Stay updated on CPRA amendments and new regulations"
            ]
        }
    ],
    
    "key_dates": {
        "ccpa_effective": "January 1, 2020",
        "ccpa_enforcement": "July 1, 2020",
        "cpra_passed": "November 3, 2020 (Proposition 24)",
        "cpra_effective": "January 1, 2023",
        "cppa_operational": "July 1, 2023 (California Privacy Protection Agency)"
    },
    
    "differences_from_gdpr": [
        "CCPA applies to for-profit businesses only (GDPR applies to all organizations)",
        "CCPA has revenue/data volume thresholds (GDPR applies to all who process EU data)",
        "CCPA uses opt-out for data sales (GDPR requires opt-in consent)",
        "CCPA has private right of action for data breaches (GDPR only regulatory enforcement)",
        "CCPA focuses on 'sale' concept (GDPR focuses on 'processing')",
        "CCPA has narrower geographic scope (California residents vs. EU residents globally)"
    ],
    
    "additional_resources": {
        "official_text": "https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?division=3.&part=4.&lawCode=CIV&title=1.81.5",
        "attorney_general": "https://oag.ca.gov/privacy/ccpa",
        "cppa": "https://cppa.ca.gov/"
    }
}
