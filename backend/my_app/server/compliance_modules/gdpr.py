"""
GDPR (General Data Protection Regulation) Compliance Module
"""

STANDARD = {
    "name": "General Data Protection Regulation (GDPR)",
    "region": "European Union",
    "effective_date": "2018-05-25",
    "version": "2016/679",
    "overview": "EU regulation on data protection and privacy for individuals within the EU and the European Economic Area.",
    "official_reference": "Regulation (EU) 2016/679",
    "authority": "European Data Protection Board (EDPB)",
    "website": "https://gdpr.eu/",
    
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

# Module metadata
MODULE_INFO = {
    "module_type": "compliance_standard",
    "last_updated": "2024-03-01",
    "maintainer": "Compliance Team",
    "tags": ["data_protection", "privacy", "eu", "gdpr"]
}
