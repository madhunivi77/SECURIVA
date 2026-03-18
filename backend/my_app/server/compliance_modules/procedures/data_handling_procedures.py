"""
Step-by-step procedures for handling client data in compliance with regulations
These procedures provide actionable guidance with real examples
"""

PROCEDURES = {
    "data_collection": {
        "title": "Collecting Client Data",
        "description": "Procedures for collecting personal information from users/clients",
        "applicable_regulations": ["GDPR", "CCPA", "HIPAA"],
        "steps": [
            {
                "step": 1,
                "action": "Identify legal basis for collection",
                "details": "Before collecting any personal data, determine your legal justification",
                "regulation_references": {
                    "gdpr": "Article 6 - Lawful basis required: Consent, Contract, Legal obligation, Vital interests, Public task, or Legitimate interests",
                    "ccpa": "Business/Commercial purpose must be disclosed",
                    "hipaa": "Minimum necessary standard applies"
                },
                "examples": {
                    "compliant": [
                        "Collecting email address to create user account (contract basis)",
                        "Collecting payment info to process purchase (contract basis)",
                        "Collecting health data with explicit consent for treatment (HIPAA)"
                    ],
                    "non_compliant": [
                        "Collecting Social Security Number without legitimate reason",
                        "Requiring phone number when not necessary for service",
                        "Collecting children's data without parental consent"
                    ]
                },
                "implementation_checklist": [
                    "Document business purpose for each data field",
                    "Review if data is truly necessary",
                    "Obtain appropriate consent where required",
                    "Implement data minimization (collect only what you need)"
                ]
            },
            {
                "step": 2,
                "action": "Provide clear privacy notice before or at collection",
                "details": "Users must be informed about data collection before or at the point of collection",
                "regulation_references": {
                    "gdpr": "Article 13 - Information to be provided when personal data are collected from the data subject",
                    "ccpa": "§1798.100(b) - Notice at collection required",
                    "hipaa": "Notice of Privacy Practices (NPP) required"
                },
                "required_disclosures": [
                    "What data is being collected (categories and specific items)",
                    "Why it's being collected (purpose)",
                    "How long it will be retained",
                    "Who it will be shared with (third parties)",
                    "User's rights (access, deletion, portability, etc.)",
                    "How to exercise those rights"
                ],
                "examples": {
                    "compliant": [
                        "Displaying privacy policy link BEFORE user enters data",
                        "Pop-up: 'We collect your email to send order confirmations. See Privacy Policy'",
                        "Checkbox: 'I agree to Terms and Privacy Policy' (unchecked by default) with links"
                    ],
                    "non_compliant": [
                        "Privacy policy link buried in footer after data entered",
                        "Pre-checked consent boxes (not valid consent)",
                        "Vague notice: 'We may use your data for business purposes'",
                        "Notice only in terms that user hasn't seen"
                    ]
                },
                "implementation_checklist": [
                    "Add privacy notice at all data collection points (forms, signup)",
                    "Make privacy policy easily accessible (clear link)",
                    "Use plain language (avoid legalese)",
                    "Update notice whenever data practices change"
                ]
            },
            {
                "step": 3,
                "action": "Obtain explicit consent where required",
                "details": "For certain data types or uses, explicit opt-in consent is mandatory",
                "when_required": [
                    "Processing sensitive personal data (health, race, biometrics) - GDPR",
                    "Marketing communications - GDPR, CAN-SPAM",
                    "Selling personal information to third parties - CCPA",
                    "Collecting data from children under 13 (COPPA) or 16 (CCPA)",
                    "Using cookies for tracking - GDPR, ePrivacy"
                ],
                "regulation_references": {
                    "gdpr": "Article 7 - Conditions for consent (must be freely given, specific, informed, unambiguous)",
                    "ccpa": "§1798.120(d) - Opt-in required for minors under 16"
                },
                "examples": {
                    "compliant": [
                        "Unchecked checkbox: 'I want to receive marketing emails'",
                        "Separate consent for sensitive data: 'I consent to sharing my health data with doctors'",
                        "Age verification: 'Are you 16 or older?' before data collection",
                        "Granular consent: Separate boxes for 'account emails' vs 'marketing emails'"
                    ],
                    "non_compliant": [
                        "Pre-checked boxes (consent must be opt-in, not opt-out)",
                        "Bundled consent: 'I agree to Terms, Privacy Policy, and Marketing' in one box",
                        "Making consent required for service that doesn't need that data",
                        "Assuming consent from inaction (silence is not consent)"
                    ]
                },
                "implementation_checklist": [
                    "Use clear, affirmative action (checkboxes, buttons)",
                    "Never pre-check consent boxes",
                    "Keep consent records (who, when, what, how)",
                    "Make it as easy to withdraw consent as to give it"
                ]
            },
            {
                "step": 4,
                "action": "Implement data minimization",
                "details": "Collect only the data that is necessary for the stated purpose",
                "regulation_references": {
                    "gdpr": "Article 5(1)(c) - Data minimisation principle",
                    "hipaa": "Minimum necessary standard",
                    "ccpa": "Reasonable security standards"
                },
                "examples": {
                    "compliant": [
                        "Collecting only email and password for account creation",
                        "Asking for billing address only at checkout (not during signup)",
                        "Storing last 4 digits of credit card, not full number"
                    ],
                    "non_compliant": [
                        "Requiring phone number, address, birthdate for a free newsletter",
                        "Collecting Social Security Number for general account",
                        "Storing full credit card numbers when not needed"
                    ]
                },
                "implementation_checklist": [
                    "Review each form field - is this truly necessary?",
                    "Make optional fields clearly marked as optional",
                    "Don't collect 'just in case' data",
                    "Regularly audit and purge unnecessary data"
                ]
            },
            {
                "step": 5,
                "action": "Secure data immediately upon collection",
                "details": "Protect data from the moment it enters your systems",
                "technical_requirements": [
                    "Use HTTPS (TLS 1.2+) for data transmission",
                    "Encrypt sensitive data at rest (AES-256)",
                    "Hash passwords (bcrypt, Argon2)",
                    "Implement access controls (least privilege)",
                    "Enable audit logging for data access"
                ],
                "regulation_references": {
                    "gdpr": "Article 32 - Security of processing",
                    "hipaa": "Technical Safeguards (§164.312)",
                    "ccpa": "§1798.150 - Reasonable security procedures required"
                },
                "examples": {
                    "compliant": [
                        "Form data sent via HTTPS POST",
                        "Passwords hashed with bcrypt before database storage",
                        "Credit card numbers tokenized via payment processor",
                        "Database encrypted with managed keys (AWS KMS, Azure Key Vault)"
                    ],
                    "non_compliant": [
                        "HTTP form submission (data visible in transit)",
                        "Passwords stored in plaintext or MD5 (easily cracked)",
                        "Sensitive data in unencrypted database",
                        "API keys hardcoded in source code"
                    ]
                },
                "implementation_checklist": [
                    "Enable HTTPS across entire site/app",
                    "Use encryption libraries (don't roll your own crypto)",
                    "Store encryption keys separately from data",
                    "Implement rate limiting to prevent brute force attacks"
                ]
            }
        ]
    },
    
    "data_storage": {
        "title": "Storing Client Data Securely",
        "description": "Procedures for secure, compliant data storage and retention",
        "applicable_regulations": ["GDPR", "CCPA", "HIPAA", "SOX"],
        "steps": [
            {
                "step": 1,
                "action": "Encrypt data at rest",
                "details": "All stored personal data must be encrypted",
                "technical_requirements": [
                    "Use AES-256 encryption minimum",
                    "Store encryption keys in secure key management system",
                    "Rotate encryption keys annually or per policy",
                    "Separate key storage from data storage"
                ],
                "regulation_references": {
                    "gdpr": "Article 32(1)(a) - Pseudonymisation and encryption",
                    "hipaa": "§164.312(a)(2)(iv) - Encryption and decryption",
                    "ccpa": "Reasonable security measures required"
                },
                "examples": {
                    "compliant": [
                        "Database: Transparent Data Encryption (TDE) enabled",
                        "Files: Encrypted file system (EFS, Azure encryption)",
                        "Backups: Encrypted with separate keys",
                        "Keys: Stored in AWS KMS, Azure Key Vault, or HashiCorp Vault"
                    ],
                    "non_compliant": [
                        "Plaintext database (anyone with DB access sees data)",
                        "Unencrypted backups stored on removable media",
                        "Encryption keys stored in same database as data",
                        "Using weak encryption (DES, 3DES, RC4)"
                    ]
                },
                "implementation_checklist": [
                    "Enable database encryption (TDE)",
                    "Enable disk encryption for servers",
                    "Use cloud provider encryption services",
                    "Document encryption methods and key locations"
                ]
            },
            {
                "step": 2,
                "action": "Implement access controls",
                "details": "Restrict data access to authorized personnel only (least privilege principle)",
                "technical_requirements": [
                    "Role-based access control (RBAC)",
                    "Multi-factor authentication (MFA) for privileged access",
                    "Regular access reviews and audits",
                    "Immediately revoke access for departing employees"
                ],
                "regulation_references": {
                    "gdpr": "Article 32(1)(b) - Ability to ensure confidentiality",
                    "hipaa": "§164.308(a)(4) - Information Access Management",
                    "sox": "Section 404 - Internal controls over financial reporting"
                },
                "examples": {
                    "compliant": [
                        "Customer service: Read-only access to customer names/emails only",
                        "Developers: Access to dev/test databases, not production",
                        "DBAs: MFA required for production database access",
                        "Automated systems: Service accounts with minimal permissions"
                    ],
                    "non_compliant": [
                        "Everyone has admin access 'just in case'",
                        "Shared passwords for production systems",
                        "No distinction between dev and production access",
                        "Former employee accounts still active after 90 days"
                    ]
                },
                "implementation_checklist": [
                    "Define roles and minimum required permissions",
                    "Implement MFA for all system access",
                    "Review access logs monthly",
                    "Automate access revocation on termination"
                ]
            },
            {
                "step": 3,
                "action": "Define and enforce retention periods",
                "details": "Determine how long to retain data, then delete when no longer needed",
                "regulation_references": {
                    "gdpr": "Article 5(1)(e) - Storage limitation principle",
                    "ccpa": "Length of retention must be disclosed to consumers",
                    "hipaa": "Minimum 6 years for medical records",
                    "sox": "7 years for audit-related records"
                },
                "retention_guidelines": {
                    "active_accounts": "While account is active + grace period",
                    "closed_accounts": "30-90 days after closure (unless legal requirement)",
                    "marketing_data": "Until consent withdrawn or inactivity (e.g., 2 years)",
                    "financial_records": "7 years (tax/SOX requirements)",
                    "medical_records": "6+ years (HIPAA minimum)",
                    "logs_and_backups": "90 days to 1 year (unless needed for audit)"
                },
                "examples": {
                    "compliant": [
                        "User closes account → Data deleted after 30 days (GDPR right to erasure)",
                        "Marketing emails: Auto-purge inactive subscribers after 2 years",
                        "Job applicant data: Deleted 6 months after hiring decision",
                        "Automated deletion: Cron job purges old data monthly"
                    ],
                    "non_compliant": [
                        "Keeping all data forever 'just in case'",
                        "Retaining marketing data after unsubscribe",
                        "No defined retention policy",
                        "Manual deletion only (never happens in practice)"
                    ]
                },
                "implementation_checklist": [
                    "Document retention periods for each data type",
                    "Implement automated deletion where possible",
                    "Balance retention needs with privacy principles",
                    "Consider legal hold requirements for litigation"
                ]
            },
            {
                "step": 4,
                "action": "Enable audit logging",
                "details": "Log all access and changes to personal data for accountability",
                "what_to_log": [
                    "Who accessed data (user ID, IP address)",
                    "When (timestamp)",
                    "What action (create, read, update, delete)",
                    "What data (which records, which fields)",
                    "Why (business purpose, if captured)",
                    "Result (success or failure)"
                ],
                "regulation_references": {
                    "gdpr": "Article 5(2) - Accountability principle",
                    "hipaa": "§164.312(b) - Audit controls",
                    "sox": "Audit trail for financial data required"
                },
                "examples": {
                    "compliant": [
                        "Log: 'User admin@company.com accessed customer ID 12345 on 2024-03-18 14:32 UTC for support ticket #789'",
                        "Database audit: Track all SELECT statements on customer table",
                        "API logs: Log all requests with user, endpoint, timestamp",
                        "Retention: Keep audit logs for 1-2 years"
                    ],
                    "non_compliant": [
                        "No logging at all",
                        "Logging only errors, not access",
                        "Logs include full data (log 'user accessed SSN' not 'user accessed SSN: 123-45-6789')",
                        "Logs accessible to everyone (not secured)"
                    ]
                },
                "implementation_checklist": [
                    "Enable database audit logging",
                    "Log application-level data access",
                    "Centralize logs (SIEM, CloudWatch, Splunk)",
                    "Alert on suspicious patterns (e.g., bulk exports)"
                ]
            },
            {
                "step": 5,
                "action": "Secure backups",
                "details": "Backups contain copies of personal data and must be equally protected",
                "technical_requirements": [
                    "Encrypt all backups (separate keys from primary data)",
                    "Store backups in separate location/region",
                    "Test restore procedures regularly",
                    "Apply same retention rules to backups"
                ],
                "examples": {
                    "compliant": [
                        "Automated daily backups to separate AWS region, encrypted with KMS",
                        "Off-site tape backups encrypted and stored in secure facility",
                        "Backup retention: 30 days, then automated deletion",
                        "Quarterly restore tests to verify backup integrity"
                    ],
                    "non_compliant": [
                        "Unencrypted backups on USB drives",
                        "Backups in same datacenter as primary data (disaster risk)",
                        "Never tested restore (backups may be corrupted)",
                        "Backups retained indefinitely (retention violation)"
                    ]
                },
                "implementation_checklist": [
                    "Automate backup process",
                    "Encrypt backups with separate keys",
                    "Store backups geographically separated",
                    "Test restore quarterly"
                ]
            }
        ]
    },
    
    "data_sharing": {
        "title": "Sharing Client Data with Third Parties",
        "description": "Procedures for sharing personal data with vendors, partners, or other third parties",
        "applicable_regulations": ["GDPR", "CCPA", "HIPAA"],
        "decision_tree_reference": "See decision_trees.json → data_sharing_decision",
        "steps": [
            {
                "step": 1,
                "action": "Identify the legal basis and necessity",
                "details": "Determine why sharing is needed and whether it's lawful",
                "questions_to_ask": [
                    "Is sharing necessary to provide our service?",
                    "Did the user consent to this sharing?",
                    "Is there a legal obligation to share?",
                    "Is the recipient a service provider/processor or third party?",
                    "Is this a 'sale' or 'sharing' under CCPA?"
                ],
                "regulation_references": {
                    "gdpr": "Article 6 - Lawful basis must apply to sharing as well",
                    "ccpa": "§1798.140(t) - 'Sale' and 'sharing' definitions",
                    "hipaa": "§164.502 - Uses and disclosures of protected health information"
                },
                "examples": {
                    "compliant": [
                        "Sharing with payment processor (Stripe) to process payments (necessary for service)",
                        "Sharing with email service (SendGrid) to send transactional emails (service provider)",
                        "Sharing with analytics service (Google Analytics) after cookie consent",
                        "Sharing with doctor's office after patient authorization (HIPAA)"
                    ],
                    "non_compliant": [
                        "Selling email list to marketing company without consent",
                        "Sharing customer data with partner for their own marketing",
                        "Giving vendor access to entire database when they only need subset",
                        "Sharing medical records without patient authorization"
                    ]
                },
                "implementation_checklist": [
                    "Document business purpose for each sharing relationship",
                    "Classify recipients (service provider vs. third party)",
                    "Obtain consent where required",
                    "Disclose sharing in privacy policy"
                ]
            },
            {
                "step": 2,
                "action": "Execute appropriate contract (DPA/BAA)",
                "details": "Before sharing, must have written agreement with required privacy terms",
                "required_agreements": {
                    "gdpr": "Data Processing Agreement (DPA) with Article 28 provisions",
                    "ccpa": "Service Provider contract with §1798.140(w) provisions",
                    "hipaa": "Business Associate Agreement (BAA) with §164.504(e) provisions"
                },
                "required_contract_terms": [
                    "Purpose: Specify exact purposes for which data can be used",
                    "Restrictions: Prohibit use for processor's own purposes",
                    "Security: Require appropriate security measures",
                    "Subprocessors: Require approval for further subcontracting",
                    "Breach notification: Require immediate breach notification",
                    "Audit rights: Allow data controller to audit compliance",
                    "Data return/deletion: Return or delete data after contract ends",
                    "Compliance: Certify compliance with applicable laws"
                ],
                "examples": {
                    "compliant": [
                        "DPA with Salesforce before using their CRM for customer data",
                        "BAA with AWS before storing PHI in cloud",
                        "Service provider contract with email vendor including CCPA terms",
                        "Addendum to master agreement specifying data processing terms"
                    ],
                    "non_compliant": [
                        "Sharing data with no contract in place",
                        "Generic NDA without data processing provisions",
                        "Verbal agreement without written terms",
                        "Contract without breach notification clause"
                    ]
                },
                "implementation_checklist": [
                    "Use standard DPA/BAA templates (don't reinvent)",
                    "Execute before sharing any data",
                    "Maintain registry of all data processing agreements",
                    "Review and renew agreements annually"
                ]
            },
            {
                "step": 3,
                "action": "Apply data minimization to sharing",
                "details": "Share only the minimum data necessary, not entire databases",
                "examples": {
                    "compliant": [
                        "Share: Customer name + email with support ticketing system",
                        "Share: Transaction ID + amount with fraud detection service",
                        "Share: Anonymized usage data with analytics platform",
                        "Share: Specific medical records needed for consultation (HIPAA minimum necessary)"
                    ],
                    "non_compliant": [
                        "Share: Entire customer database dump with marketing vendor",
                        "Share: Full credit card numbers when payment processor only needs token",
                        "Share: Social Security Numbers with vendor who doesn't need them",
                        "Share: All medical records when only allergy info needed"
                    ]
                },
                "implementation_checklist": [
                    "Create limited data extracts (don't give full database access)",
                    "Use APIs with field-level permissions (not broad SELECT *)",
                    "Anonymize or pseudonymize data where possible",
                    "Review shared data scope quarterly"
                ]
            },
            {
                "step": 4,
                "action": "Use secure transfer methods",
                "details": "Protect data in transit during sharing",
                "approved_methods": [
                    "API over HTTPS (TLS 1.2+)",
                    "SFTP (SSH File Transfer Protocol)",
                    "Encrypted email (S/MIME, PGP)",
                    "Secure file transfer portal with encryption",
                    "Direct database connection over VPN or private network",
                    "Encrypted cloud storage (AWS S3 with SSE, Azure Blob)"
                ],
                "rejected_methods": [
                    "Unencrypted email attachments",
                    "HTTP (without TLS)",
                    "FTP (File Transfer Protocol without encryption)",
                    "Public file sharing links (Dropbox, Google Drive without access controls)",
                    "USB drives or physical media without encryption",
                    "SMS/text messages for sensitive data"
                ],
                "examples": {
                    "compliant": [
                        "Transfer via REST API over HTTPS with API key authentication",
                        "Upload to vendor's SFTP server with SSH keys",
                        "Send PGP-encrypted email with signed agreement attached",
                        "Share via secure portal with password + 2FA"
                    ],
                    "non_compliant": [
                        "Email spreadsheet with customer data as plain attachment",
                        "Upload to public Google Drive and share link",
                        "FTP without encryption",
                        "Text message with login credentials"
                    ]
                },
                "implementation_checklist": [
                    "Never use unencrypted email for personal data",
                    "Require HTTPS for all API integrations",
                    "Use short-lived access credentials (expire after 24-48 hours)",
                    "Enable download limits and expiration on shared files"
                ]
            },
            {
                "step": 5,
                "action": "Log and monitor sharing activities",
                "details": "Track what data was shared, when, with whom, and why",
                "what_to_log": [
                    "Recipient (company name, contact)",
                    "Date and time of sharing",
                    "Data categories/records shared",
                    "Purpose of sharing",
                    "Legal basis (contract, consent, etc.)",
                    "Who authorized sharing (employee, department)"
                ],
                "examples": {
                    "compliant": [
                        "Log: 'Shared 1,000 customer emails with Mailchimp on 2024-03-18 for newsletter campaign (consent obtained)'",
                        "API logs: Track all data exports with timestamp and user",
                        "Quarterly review: DPO reviews all sharing activities",
                        "Alert: Automated alert if data export exceeds normal threshold"
                    ],
                    "non_compliant": [
                        "No record of what data was shared",
                        "Can't answer 'Who did we share data with last quarter?'",
                        "No approval process for new sharing relationships",
                        "Discovery of unauthorized sharing only during audit"
                    ]
                },
                "implementation_checklist": [
                    "Maintain data sharing inventory",
                    "Log all API data transfers",
                    "Require approval workflow for new sharing",
                    "Review sharing activities monthly"
                ]
            }
        ]
    },
    
    "data_deletion": {
        "title": "Deleting Client Data (Right to Erasure / Right to Delete)",
        "description": "Procedures for handling data deletion requests from users",
        "applicable_regulations": ["GDPR Article 17", "CCPA §1798.105"],
        "response_deadline": {
            "gdpr": "1 month (extendable by 2 more months if complex)",
            "ccpa": "45 days (extendable by 45 more days with notice)"
        },
        "steps": [
            {
                "step": 1,
                "action": "Verify requester identity",
                "details": "Confirm the person requesting deletion is actually the data subject",
                "verification_methods": [
                    "Email confirmation to registered email address",
                    "Account login (user submits request while logged in)",
                    "Match 2-3 data points (name + birthdate + last 4 of SSN)",
                    "Government ID verification for CCPA requests"
                ],
                "regulation_references": {
                    "gdpr": "Recital 64 - Verification should be reasonable and not excessive",
                    "ccpa": "§1798.140(q) - Reasonable verification methods"
                },
                "examples": {
                    "compliant": [
                        "Send verification email: 'Click this link to confirm deletion request'",
                        "Request login: 'Please log in to your account to submit deletion request'",
                        "For CCPA: 'Please provide name, email, and last 4 of phone number to verify'",
                        "For high-risk: 'Please upload copy of government ID'"
                    ],
                    "non_compliant": [
                        "Delete data based on email request alone (no verification)",
                        "Require excessive verification (utility bill + passport for simple request)",
                        "Make verification so difficult users give up",
                        "Refuse to delete because 'we can't verify' without trying reasonable methods"
                    ]
                },
                "implementation_checklist": [
                    "Define verification requirements by data sensitivity",
                    "Use automated email verification where possible",
                    "Document verification method used for each request",
                    "Balance security (prevent unauthorized deletion) with accessibility"
                ]
            },
            {
                "step": 2,
                "action": "Check for legal retention exceptions",
                "details": "Determine if any legal obligation prevents immediate deletion",
                "valid_exceptions": {
                    "gdpr_article_17_3": [
                        "Exercise of freedom of expression and information",
                        "Compliance with legal obligation",
                        "Public interest (public health, archiving, research)",
                        "Establishment, exercise or defense of legal claims"
                    ],
                    "ccpa_1798_105_d": [
                        "Complete transaction for which data was collected",
                        "Detect security incidents or protect against illegal activity",
                        "Debug or repair errors",
                        "Exercise free speech",
                        "Comply with California Electronic Communications Privacy Act",
                        "Engage in public or peer-reviewed research",
                        "Legal obligation compliance",
                        "Internal lawful uses compatible with context"
                    ],
                    "common_retention_requirements": [
                        "Tax records: 7 years (IRS)",
                        "Financial records: 7 years (SOX)",
                        "Medical records: 6+ years (HIPAA)",
                        "Employment records: 3-7 years (varies by state)",
                        "Litigation hold: Until dispute resolved"
                    ]
                },
                "examples": {
                    "compliant": [
                        "Response: 'We must retain your tax records for 5 more years per IRS requirement, but have deleted all marketing data'",
                        "Response: 'Your account data is deleted, but we must keep transaction history for ongoing fraud investigation'",
                        "Partial deletion: Delete preferences/activity, keep anonymized transaction total for financial reporting"
                    ],
                    "non_compliant": [
                        "Response: 'We're keeping all your data indefinitely for our records'",
                        "Claiming retention exception without specific legal basis",
                        "Keeping data 'just in case' for potential future legal issues",
                        "Refusing deletion because it's 'too difficult'"
                    ]
                },
                "implementation_checklist": [
                    "Document legal retention requirements by data type",
                    "Implement partial deletion (delete what you can)",
                    "Clearly communicate exceptions to users",
                    "Review retention exceptions annually"
                ]
            },
            {
                "step": 3,
                "action": "Delete data from all systems",
                "details": "Remove data not just from primary database, but all locations",
                "systems_to_check": [
                    "Primary production database",
                    "Data warehouse / analytics database",
                    "Backup systems (or document deletion date to purge from backups)",
                    "Log files (application logs, API logs, audit logs)",
                    "Cached data (Redis, Memcached, CDN)",
                    "Development/test databases (if they contain production data)",
                    "Third-party systems (notify service providers to delete)",
                    "Archives and offline storage"
                ],
                "examples": {
                    "compliant": [
                        "Automated deletion: Script deletes from all databases + notifies service providers",
                        "Backup handling: Mark data for deletion + purge from next backup cycle",
                        "Third-party: Send deletion requests to Salesforce, Mailchimp, analytics providers",
                        "Log handling: Delete or anonymize logs older than 90 days"
                    ],
                    "non_compliant": [
                        "Only delete from primary database, forget data warehouse",
                        "Delete from database but not backups (data persists for years)",
                        "Forget to notify third-party processors to delete",
                        "Keep data in test environment or developer laptop"
                    ]
                },
                "implementation_checklist": [
                    "Create deletion checklist for all systems",
                    "Automate deletion where possible (database triggers, scripts)",
                    "Maintain list of all third-party processors",
                    "Test deletion thoroughly (verify data is actually gone)"
                ]
            },
            {
                "step": 4,
                "action": "Notify third parties and service providers",
                "details": "If you've shared data with others, they must delete too",
                "who_to_notify": [
                    "Service providers (processors) - required by GDPR Art. 17(2) and CCPA §1798.105(c)",
                    "Third parties to whom data was sold/shared",
                    "Partners with whom data was shared"
                ],
                "regulation_references": {
                    "gdpr": "Article 17(2) - Controller must inform other controllers of erasure request",
                    "ccpa": "§1798.105(c) - Direct service providers to delete"
                },
                "examples": {
                    "compliant": [
                        "Email to service providers: 'Please delete user ID 12345's data from your systems per deletion request'",
                        "API call: DELETE /users/12345 to partner systems",
                        "Maintain log of notifications sent",
                        "Follow up to confirm deletion completed"
                    ],
                    "non_compliant": [
                        "Only delete from your systems, ignore third parties",
                        "Assume service providers will figure it out",
                        "No record of who was notified",
                        "Never verify deletion was completed"
                    ]
                },
                "implementation_checklist": [
                    "Maintain registry of all data recipients",
                    "Include deletion notification in service provider contracts",
                    "Implement automated notification where possible",
                    "Track and follow up on deletion confirmations"
                ]
            },
            {
                "step": 5,
                "action": "Respond to user and log the request",
                "details": "Confirm completion and document the deletion",
                "response_content": [
                    "Confirm data has been deleted",
                    "Specify what was deleted and what (if anything) was retained",
                    "Explain any retention exceptions",
                    "Provide effective date of deletion"
                ],
                "what_to_log": [
                    "Requester identity (user ID, email)",
                    "Date request received",
                    "Verification method used",
                    "Data deleted (categories or specifics)",
                    "Exceptions/data retained (if any)",
                    "Date deletion completed",
                    "Employee who processed request"
                ],
                "examples": {
                    "compliant": [
                        "Response: 'Your deletion request has been processed. We deleted your profile, preferences, and activity history on 2024-03-20. Transaction history from 2023-2024 is retained for 7 years per tax law.'",
                        "Log entry: 'User 12345 deletion request received 2024-03-18, verified via email, deleted all data except financial records (7yr retention), completed 2024-03-20'",
                        "Confirmation email sent within 45 days"
                    ],
                    "non_compliant": [
                        "No response to user (radio silence)",
                        "Response: 'We'll get to it eventually'",
                        "No log of deletion request or actions taken",
                        "Exceeding response deadline without communication"
                    ]
                },
                "implementation_checklist": [
                    "Send confirmation emaail to user",
                    "Log all deletion requests in compliance system",
                    "Meet response deadline (30 days GDPR / 45 days CCPA)",
                    "If extension needed, notify user and explain why"
                ]
            }
        ]
    },
    
    "breach_response": {
        "title": "Responding to a Data Breach",
        "description": "Step-by-step procedures when personal data is compromised",
        "applicable_regulations": ["GDPR Article 33-34", "CCPA §1798.150", "HIPAA §164.408"],
        "critical_timelines": {
            "gdpr": "72 hours to notify regulator, without undue delay to individuals",
            "hipaa": "60 days to notify HHS and affected individuals",
            "state_laws": "Varies (often 'without unreasonable delay', some specify days)"
        },
        "steps": [
            {
                "step": 1,
                "action": "Contain the breach immediately",
                "details": "Stop the breach and secure systems to prevent further damage",
                "immediate_actions": [
                    "Isolate affected systems (disconnect from network if needed)",
                    "Change passwords and revoke compromised credentials",
                    "Patch vulnerabilities that caused the breach",
                    "Preserve evidence (don't delete logs)",
                    "Activate incident response team"
                ],
                "examples": {
                    "compliant": [
                        "Discovered unauthorized access → Immediately disable compromised admin account",
                        "Ransomware detected → Isolate affected servers from network",
                        "SQL injection exploit → Take vulnerable endpoint offline, patch immediately",
                        "Lost laptop → Remotely wipe device"
                    ],
                    "non_compliant": [
                        "Waiting until Monday to address Friday breach",
                        "Trying to cover up or hide the breach",
                        "Deleting logs to hide evidence",
                        "Continuing business as usual while breach is active"
                    ]
                }
            },
            {
                "step": 2,
                "action": "Assess the scope and severity",
                "details": "Determine what data was compromised and risk to individuals",
                "questions_to_answer": [
                    "What data was accessed/stolen? (names, emails, SSNs, health data, etc.)",
                    "How many individuals are affected?",
                    "Was data encrypted? (encrypted data may have lower risk)",
                    "Who accessed it? (insider vs. external attacker)",
                    "How did breach occur? (what vulnerability)",
                    "Has data been misused? (fraud, identity theft)",
                    "Can breach be remediated? (e.g., stolen data recovered)"
                ],
                "severity_factors": {
                    "high_risk": [
                        "Social Security Numbers or financial data exposed",
                        "Health/medical data exposed (HIPAA)",
                        "Large number of individuals (>500)",
                        "Data unencrypted and plaintext",
                        "Evidence of malicious use"
                    ],
                    "lower_risk": [
                        "Encrypted data stolen (attacker can't decrypt)",
                        "Names and emails only (no sensitive data)",
                        "Small number of individuals",
                        "Accidental disclosure (not malicious attack)",
                        "Data recovered before misuse"
                    ]
                },
                "regulation_requirements": {
                    "gdpr": "Article 33(3) - Must describe: nature of breach, categories and number of individuals, likely consequences, measures taken",
                    "hipaa": "Must assess whether breach poses risk to PHI",
                    "ccpa": "Private right of action only if 'reasonable security' was lacking"
                }
            },
            {
                "step": 3,
                "action": "Notify regulatory authorities",
                "details": "Report breach to relevant data protection authorities within required timeframes",
                "notification_requirements": {
                    "gdpr": {
                        "authority": "Lead supervisory authority (Data Protection Authority)",
                        "deadline": "72 hours of becoming aware",
                        "required_information": [
                            "Nature of personal data breach",
                            "Categories and approximate number of data subjects",
                            "Name and contact of Data Protection Officer",
                            "Likely consequences of breach",
                            "Measures taken or proposed to address breach"
                        ]
                    },
                    "hipaa": {
                        "authority": "HHS Office for Civil Rights",
                        "deadline": "60 days from discovery",
                        "large_breaches": "If affecting 500+ individuals, notify HHS within 60 days AND notify media",
                        "small_breaches": "If affecting <500 individuals, annual notification log"
                    },
                    "state_laws": {
                        "varies": "Check state-specific requirements (California, New York, etc.)",
                        "california": "If 500+ California residents, notify Attorney General"
                    }
                },
                "examples": {
                    "compliant": [
                        "GDPR: Breach discovered Monday 9am → Notify DPA by Wednesday 9am (72 hours)",
                        "HIPAA: 1,000 records exposed → Notify HHS and media within 60 days",
                        "Multi-jurisdictional: Notify GDPR authority + HHS + California AG (all applicable)",
                        "Cannot meet 72hrs → Notify with explanation of delay"
                    ],
                    "non_compliant": [
                        "Waiting weeks or months to notify",
                        "Not notifying because breach is 'embarrassing'",
                        "Downplaying severity to avoid reporting",
                        "Only notifying one jurisdiction when multiple apply"
                    ]
                }
            },
            {
                "step": 4,
                "action": "Notify affected individuals",
                "details": "Inform people whose data was compromised",
                "when_required": {
                    "gdpr": "Article 34 - When breach likely to result in high risk to rights and freedoms",
                    "ccpa": "If breach results from violation of reasonable security duty",
                    "hipaa": "Always required if PHI is breached",
                    "state_laws": "Most states require notification without unreasonable delay"
                },
                "notification_content": [
                    "Description of the breach (what happened)",
                    "Types of personal data involved",
                    "Likely consequences and potential risks",
                    "Measures taken to address breach",
                    "Recommendations for individuals (change passwords, monitor credit)",
                    "Contact point for questions",
                    "FREE credit monitoring or identity theft protection (if appropriate)"
                 ],
                "notification_methods": [
                    "Email to affected individuals (preferred)",
                    "Letter to last known address",
                    "Prominent website notice (if email/address unavailable)",
                    "Media notice (if >500 HIPAA records or cannot contact individuals)"
                ],
                "examples": {
                    "compliant": [
                        "Email: 'We experienced a data breach on March 14. Your name, email, and billing address may have been accessed. We have secured our systems and are offering 1 year of free credit monitoring. Please change your password and monitor your accounts. Contact security@company.com with questions.'",
                        "Include FREE credit monitoring service (Experian, TransUnion)",
                        "Set up dedicated breach response phone line and FAQ page",
                        "Send notification without undue delay (within days/weeks)"
                    ],
                    "non_compliant": [
                        "Not notifying individuals at all",
                        "Vague notice: 'We may have had a security incident'",
                        "Blaming individuals: 'You should have used better passwords'",
                        "Waiting months to notify (without valid reason)",
                        "Charging for credit monitoring"
                    ]
                }
            },
            {
                "step": 5,
                "action": "Document everything and learn from the breach",
                "details": "Maintain comprehensive records and prevent future breaches",
                "documentation_required": [
                    "Incident timeline (discovery, containment, notification)",
                    "Scope assessment (data affected, individuals impacted)",
                    "Root cause analysis (how breach occurred)",
                    "Notifications sent (when, to whom)",
                    "Remediation steps taken",
                    "Lessons learned and preventive measures"
                ],
                "post-breach_actions": [
                    "Conduct security audit to identify other vulnerabilities",
                    "Implement additional security controls",
                    "Update incident response plan based on lessons learned",
                    "Re-train employees on security practices",
                    "Consider cyber insurance claim if applicable",
                    "Prepare for potential regulatory investigations"
                ],
                "examples": {
                    "compliant": [
                        "Incident report: 'Breach occurred due to unpatched server. 10,000 users affected. Regulatory notifications sent within 72hrs. Implemented automated patching and vulnerability scanning.'",
                        "Follow-up security improvements: Deployed MFA, encrypted additional data, hired security consultant",
                        "Annual breach drill to test incident response"
                    ],
                    "non_compliant": [
                        "No documentation at all",
                        "Forgetting about breach after immediate crisis",
                        "Not implementing preventive measures",
                        "Repeating same breach type years later"
                    ]
                },
                "regulatory_accountability": {
                    "gdpr": "Article 33(5) - Must document all breaches, even if not reported (internal record)",
                    "hipaa": "Must maintain breach logs and policies",
                    "penalties": "Failure to notify can result in larger fines than breach itself"
                }
            }
        ]
    }
}
