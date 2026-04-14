"""
Email Compliance Standards Module
Covers CAN-SPAM, CASL, GDPR email requirements, and email marketing best practices
"""

STANDARD = {
    "name": "Email Marketing Compliance Standards",
    "region": "Global (US, Canada, EU)",
    "effective_date": "2003-12-16",  # CAN-SPAM effective date
    "version": "Consolidated 2024",
    "overview": "Comprehensive email marketing compliance covering CAN-SPAM (US), CASL (Canada), GDPR email requirements (EU), and international best practices for commercial electronic messages.",
    "official_reference": "CAN-SPAM Act 15 USC 7701, CASL S.C. 2010 c.23, GDPR Article 21",
    "authority": "FTC (US), CRTC (Canada), EDPB (EU)",
    
    "standards": [
        {
            "id": "can_spam",
            "name": "CAN-SPAM Act (US)",
            "region": "United States",
            "effective_date": "2004-01-01",
            "description": "Controls the Assault of Non-Solicited Pornography And Marketing Act",
            "requirements": [
                {
                    "id": "can_spam_1",
                    "name": "No False or Misleading Headers",
                    "description": "From, To, Reply-To, and routing information must be accurate and identify the sender",
                    "implementation": [
                        "Use accurate sender name and email address",
                        "Ensure routing information is legitimate",
                        "Don't use deceptive subject lines"
                    ]
                },
                {
                    "id": "can_spam_2",
                    "name": "Clear Subject Lines",
                    "description": "Subject line must accurately reflect the content of the message",
                    "implementation": [
                        "Subject must not be deceptive",
                        "Subject must relate to email content",
                        "Avoid clickbait or misleading titles"
                    ]
                },
                {
                    "id": "can_spam_3",
                    "name": "Identify Message as Advertisement",
                    "description": "Message must be clearly identified as an advertisement",
                    "implementation": [
                        "Disclose that message is an ad",
                        "Make disclosure clear and conspicuous",
                        "Can be in subject or body"
                    ]
                },
                {
                    "id": "can_spam_4",
                    "name": "Include Physical Address",
                    "description": "Include valid physical postal address",
                    "implementation": [
                        "Include street address OR P.O. box",
                        "Must be current and valid",
                        "Typically in footer"
                    ]
                },
                {
                    "id": "can_spam_5",
                    "name": "Provide Opt-Out Method",
                    "description": "Tell recipients how to opt out of future emails",
                    "implementation": [
                        "Clear and conspicuous opt-out notice",
                        "Easy-to-use unsubscribe mechanism",
                        "Free to opt-out (no fees)",
                        "Process within 10 business days"
                    ]
                },
                {
                    "id": "can_spam_6",
                    "name": "Honor Opt-Outs Promptly",
                    "description": "Honor opt-out requests within 10 business days",
                    "implementation": [
                        "Stop sending within 10 business days",
                        "Cannot sell/transfer opt-out addresses",
                        "Maintain suppression list"
                    ]
                },
                {
                    "id": "can_spam_7",
                    "name": "Monitor Third Parties",
                    "description": "Monitor what others are doing on your behalf",
                    "implementation": [
                        "Responsible for violations by hired marketers",
                        "Ensure vendors comply with CAN-SPAM",
                        "Written agreements with email service providers"
                    ]
                }
            ],
            "penalties": {
                "civil": "Up to $51,744 per violation (adjusted for inflation)",
                "criminal": "Up to 5 years imprisonment for aggravated violations",
                "notes": "Each separate email can be a separate violation"
            }
        },
        {
            "id": "casl",
            "name": "CASL - Canada's Anti-Spam Legislation",
            "region": "Canada",
            "effective_date": "2014-07-01",
            "description": "Canadian law governing commercial electronic messages",
            "requirements": [
                {
                    "id": "casl_1",
                    "name": "Express or Implied Consent Required",
                    "description": "Must have consent before sending commercial electronic messages",
                    "implementation": [
                        "Obtain express consent (opt-in)",
                        "Or rely on implied consent (existing business relationship)",
                        "Document consent with timestamp",
                        "Keep consent records for 3 years"
                    ]
                },
                {
                    "id": "casl_2",
                    "name": "Clear Identification",
                    "description": "Clearly identify sender and on whose behalf message is sent",
                    "implementation": [
                        "Include sender's name",
                        "Include company name if applicable",
                        "Identify on behalf of whom message is sent"
                    ]
                },
                {
                    "id": "casl_3",
                    "name": "Provide Contact Information",
                    "description": "Include sender's contact information",
                    "implementation": [
                        "Physical mailing address",
                        "Phone number, email, or web address",
                        "Must be valid and monitored"
                    ]
                },
                {
                    "id": "casl_4",
                    "name": "Unsubscribe Mechanism",
                    "description": "Provide clear and simple unsubscribe method",
                    "implementation": [
                        "One-click unsubscribe preferred",
                        "Process within 10 business days",
                        "Free of charge",
                        "Must work for at least 60 days after sending"
                    ]
                },
                {
                    "id": "casl_5",
                    "name": "Pre-Checked Boxes Prohibited",
                    "description": "Cannot use pre-checked consent boxes",
                    "implementation": [
                        "Consent checkboxes must be unchecked by default",
                        "User must actively opt-in",
                        "Bundled consent prohibited"
                    ]
                }
            ],
            "implied_consent_scenarios": [
                "Existing business relationship (purchase/inquiry within 2 years)",
                "Existing non-business relationship (membership, volunteer work within 2 years)",
                "Conspicuously published email (personal relationship exception)",
                "Business card exchange within 6 months"
            ],
            "penalties": {
                "administrative": "Up to CAD $10 million per violation",
                "individual_max": "Up to CAD $1 million per violation",
                "notes": "One of the strictest anti-spam laws globally"
            }
        },
        {
            "id": "gdpr_email",
            "name": "GDPR Email Marketing Requirements",
            "region": "European Union",
            "effective_date": "2018-05-25",
            "description": "GDPR requirements specific to email marketing",
            "requirements": [
                {
                    "id": "gdpr_email_1",
                    "name": "Lawful Basis for Processing",
                    "description": "Establish lawful basis (consent or legitimate interest) for email marketing",
                    "implementation": [
                        "Obtain explicit consent for marketing emails",
                        "OR demonstrate legitimate interest with balancing test",
                        "Document legal basis in privacy policy",
                        "Consent must be freely given, specific, informed"
                    ]
                },
                {
                    "id": "gdpr_email_2",
                    "name": "Right to Object (Article 21)",
                    "description": "Recipients can object to email marketing at any time",
                    "implementation": [
                        "Provide easy opt-out mechanism",
                        "Inform about right to object in privacy policy",
                        "Honor opt-outs immediately",
                        "Maintain suppression list"
                    ]
                },
                {
                    "id": "gdpr_email_3",
                    "name": "Transparency Requirements",
                    "description": "Provide clear information about data processing",
                    "implementation": [
                        "Link to privacy policy in emails",
                        "Explain how email address was obtained",
                        "Describe purpose of processing",
                        "Identity of data controller"
                    ]
                },
                {
                    "id": "gdpr_email_4",
                    "name": "Data Protection by Design",
                    "description": "Implement privacy safeguards in email systems",
                    "implementation": [
                        "Encrypt email databases",
                        "Implement access controls",
                        "Regular security audits",
                        "Data minimization (only collect necessary data)"
                    ]
                }
            ],
            "special_notes": [
                "B2B emails may have lighter requirements",
                "Soft opt-in allowed for existing customers (similar products)",
                "Third-party consent requires transparency about data sharing"
            ]
        }
    ],
    
    "best_practices": [
        {
            "category": "Double Opt-In",
            "description": "Send confirmation email before adding to list",
            "benefits": ["Higher engagement", "Better deliverability", "Legal protection", "Reduced complaints"]
        },
        {
            "category": "Preference Centers",
            "description": "Let subscribers choose email frequency and topics",
            "benefits": ["Reduced unsubscribes", "Better targeting", "Compliance with granular consent"]
        },
        {
            "category": "Email Authentication",
            "description": "Implement SPF, DKIM, and DMARC",
            "benefits": ["Improved deliverability", "Brand protection", "Reduced spoofing"]
        },
        {
            "category": "Suppression Lists",
            "description": "Maintain lists of unsubscribed and bounced addresses",
            "benefits": ["Compliance", "Better sender reputation", "Reduced costs"]
        },
        {
            "category": "Engagement Metrics",
            "description": "Monitor open rates, click rates, and complaints",
            "benefits": ["Identify disengaged users", "Improve content", "Maintain deliverability"]
        }
    ],
    
    "technical_requirements": {
        "unsubscribe_link": {
            "placement": "Footer of email (visible without scrolling preferred)",
            "format": "One-click preferred, max 2 clicks",
            "text": "Clear language (Unsubscribe, Opt-out, etc.)",
            "processing_time": "10 business days maximum (US/Canada), immediate preferred"
        },
        "list_unsubscribe_header": {
            "description": "RFC 8058 - One-Click Unsubscribe",
            "implementation": "List-Unsubscribe: <mailto:unsub@example.com>, <https://example.com/unsub>",
            "benefit": "Gmail/Yahoo bulk senders requirement (Feb 2024)"
        },
        "sender_authentication": {
            "spf": "Sender Policy Framework - Authorize sending IPs",
            "dkim": "DomainKeys Identified Mail - Cryptographic signature",
            "dmarc": "Domain-based Message Authentication - Policy and reporting"
        }
    },
    
    "common_violations": [
        {
            "violation": "Purchased email lists",
            "issue": "No consent from recipients",
            "penalty": "High spam complaints, legal fines"
        },
        {
            "violation": "Hidden unsubscribe links",
            "issue": "Not clear and conspicuous",
            "penalty": "CAN-SPAM violations, poor deliverability"
        },
        {
            "violation": "Ignoring opt-outs",
            "issue": "Continuing to email after unsubscribe",
            "penalty": "Legal violations, spam complaints"
        },
        {
            "violation": "Pre-checked consent boxes",
            "issue": "Not valid consent under GDPR/CASL",
            "penalty": "Invalid consent, regulatory fines"
        },
        {
            "violation": "Misleading subject lines",
            "issue": "Deceptive or clickbait subjects",
            "penalty": "CAN-SPAM violations, poor engagement"
        }
    ],
    
    "checklist": [
        {"id": "email_001", "requirement": "Obtain valid consent (opt-in) before sending", "standard": "CASL/GDPR"},
        {"id": "email_002", "requirement": "Use accurate From name and email address", "standard": "CAN-SPAM"},
        {"id": "email_003", "requirement": "Subject line accurately reflects content", "standard": "CAN-SPAM"},
        {"id": "email_004", "requirement": "Include valid physical address in footer", "standard": "CAN-SPAM"},
        {"id": "email_005", "requirement": "Provide clear unsubscribe link", "standard": "All"},
        {"id": "email_006", "requirement": "Process unsubscribes within 10 business days", "standard": "CAN-SPAM/CASL"},
        {"id": "email_007", "requirement": "Implement List-Unsubscribe header", "standard": "Best Practice"},
        {"id": "email_008", "requirement": "Link to privacy policy", "standard": "GDPR"},
        {"id": "email_009", "requirement": "Maintain suppression list", "standard": "All"},
        {"id": "email_010", "requirement": "Document consent with timestamps", "standard": "CASL/GDPR"},
        {"id": "email_011", "requirement": "Implement SPF, DKIM, DMARC", "standard": "Best Practice"},
        {"id": "email_012", "requirement": "Monitor engagement and clean lists", "standard": "Best Practice"}
    ]
}

# Module metadata
MODULE_INFO = {
    "module_type": "compliance_standard",
    "last_updated": "2024-03-01",
    "maintainer": "Compliance Team",
    "tags": ["email", "marketing", "can-spam", "casl", "gdpr", "privacy"],
    "related_modules": ["gdpr", "privacy_shield"]
}
