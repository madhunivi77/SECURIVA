"""
Real-world examples of compliant vs non-compliant actions
Use these as training materials and reference for employees
"""

EXAMPLES = {
    "email_scenarios": [
        {
            "scenario": "Customer requests copy of their data (GDPR Article 15 / CCPA Right to Know)",
            "situation": "Customer emails: 'I want to know what personal data you have about me'",
            "applicable_regulations": ["GDPR", "CCPA"],
            "compliant_response": {
                "action": "Verify identity via email confirmation, provide data within 30 days in machine-readable format (JSON/CSV)",
                "steps": [
                    "Send verification email: 'Please click this link to confirm your data access request'",
                    "After verification: Export user's data (profile, order history, preferences, logs)",
                    "Provide in downloadable format (JSON, CSV, or PDF)",
                    "Send within 30 days (GDPR) or 45 days (CCPA)",
                    "Include explanation of data categories and sources"
                ],
                "why_compliant": "Responds within legal timeframe, verifies identity, provides data in portable/readable format",
                "legal_basis": "GDPR Article 15 - Right of access by data subject. CCPA §1798.100 - Right to know"
            },
            "non_compliant_response": {
                "action": "Ignore request or respond after 90 days or refuse to provide data",
                "examples": [
                    "No response at all",
                    "Response: 'We'll get to it eventually'",
                    "Providing only summary instead of actual data",
                    "Asking customer to pay for the data export"
                ],
                "why_non_compliant": "Exceeds 30-day GDPR / 45-day CCPA deadline, denies legal right to access",
                "consequence": "GDPR: Up to €20M or 4% global annual revenue. CCPA: $2,500-$7,500 per violation"
            }
        },
        {
            "scenario": "Marketing wants to email newsletter to all users",
            "situation": "Marketing team asks you to export all customer emails for monthly newsletter",
            "applicable_regulations": ["GDPR", "CCPA", "CAN-SPAM"],
            "compliant_response": {
                "action": "Only email users who explicitly opted in; include unsubscribe link; honor opt-outs within 10 days",
                "steps": [
                    "Export ONLY emails where marketing_consent=TRUE (explicit opt-in)",
                    "Verify consent timestamp (when did they consent?)",
                    "Ensure each email has working unsubscribe link",
                    "Honor unsubscribe requests within 10 business days (CAN-SPAM)",
                    "Include physical mailing address in email footer (CAN-SPAM requirement)"
                ],
                "checklist": [
                    "✓ Users explicitly checked 'I want to receive marketing emails' (not pre-checked box)",
                    "✓ Unsubscribe link in every marketing email",
                    "✓ Automated opt-out processing (no manual intervention required)",
                    "✓ Clear identification: Email clearly states it's from [Your Company]"
                ],
                "why_compliant": "GDPR requires explicit opt-in consent for marketing. CAN-SPAM requires unsubscribe mechanism.",
                "legal_basis": "GDPR Article 7 - Consent. CAN-SPAM Act 15 U.S.C. §7701"
            },
            "non_compliant_response": {
                "action": "Email all users assuming implied consent, no unsubscribe link",
                "examples": [
                    "Export entire customer database and send blast email",
                    "Assume consent from previous purchase (not valid for marketing)",
                    "Use pre-checked boxes at signup (not explicit consent)",
                    "Make unsubscribe difficult (must email support, no automated process)",
                    "Continue emailing after unsubscribe"
                ],
                "why_non_compliant": "GDPR requires explicit opt-in (pre-checked boxes don't count). CAN-SPAM requires easy opt-out.",
                "consequence": "GDPR: Up to €10M or 2% global revenue. CAN-SPAM: Up to $46,517 per violation (FTC)"
            }
        },
        {
            "scenario": "Third-party vendor requests access to customer database",
            "situation": "Salesforce rep asks for database credentials to set up CRM integration",
            "applicable_regulations": ["GDPR", "CCPA", "HIPAA"],
            "compliant_response": {
                "action": "Execute Data Processing Agreement (DPA) first, grant minimum necessary access via secure API, audit vendor compliance",
                "steps": [
                    "Before sharing ANY data: Execute DPA with Salesforce (ensure GDPR Art. 28 provisions)",
                    "Never give direct database credentials - use Salesforce API instead",
                    "Configure API: Read-write access to ONLY necessary fields (name, email, company - not SSN, passwords)",
                    "Enable audit logging: Track all data accessed by Salesforce API",
                    "Set data retention terms: Data must be deleted when contract ends",
                    "Schedule annual vendor compliance review"
                ],
                "required_dpa_terms": [
                    "Vendor processes data only per your instructions (not their own purposes)",
                    "Vendor maintains appropriate security measures (encryption, access controls)",
                    "Data returned or deleted after contract ends",
                    "Vendor notifies you of breaches within 24-72 hours",
                    "You have right to audit vendor's data practices"
                ],
                "why_compliant": "DPA establishes controller-processor relationship, limits vendor's use, provides breach notification, enforces security standards",
                "legal_basis": "GDPR Article 28 - Processor requirements. CCPA §1798.140(w) - Service provider definition"
            },
            "non_compliant_response": {
                "action": "Give vendor database credentials without DPA, full admin access, no limitations",
                "examples": [
                    "Provide master database username/password via email",
                    "Give full read-write access to all tables (including passwords, SSNs)",
                    "No contract or only generic NDA (no data processing terms)",
                    "No audit logging to track vendor's data access",
                    "Never review what vendor is doing with the data"
                ],
                "why_non_compliant": "No contractual safeguards; violates controller-processor requirements; excessive access (not data minimization); no audit trail",
                "consequence": "Data controller (YOU) remains fully liable for vendor's violations, breaches, or misuse. Could face same fines as if you committed violation yourself."
            }
        },
        {
            "scenario": "Customer requests deletion of account and data (Right to Erasure)",
            "situation": "Customer closes account and emails: 'Delete all my data per GDPR'",
            "applicable_regulations": ["GDPR Article 17", "CCPA §1798.105"],
            "compliant_response": {
                "action": "Verify identity, delete all data except legally required retention, respond within 30 days",
                "steps": [
                    "Send verification email to confirm deletion request",
                    "Check retention obligations: Must keep transaction records 7 years for tax law",
                    "Delete: Profile, preferences, activity logs, marketing data, cached data",
                    "Retain ONLY: Financial transaction history (anonymize if possible)",
                    "Notify third parties: Email CRM/email service providers to delete their copies",
                    "Mark data for deletion in backups (will purge when backups expire)",
                    "Respond within 30 days explaining what was deleted and what was retained (with legal justification)",
                    "Log the deletion request and actions taken"
                ],
                "sample_response": "Your deletion request has been completed. We've permanently deleted your profile, activity history, preferences, and marketing data. We are required to retain transaction records from 2023-2024 for 5 more years to comply with IRS tax retention requirements (7 years). These will be automatically deleted in 2029.",
                "why_compliant": "Verifies identity, deletes all non-essential data, clearly explains retention exceptions with legal basis, meets 30-day deadline",
                "legal_basis": "GDPR Article 17 - Right to erasure. CCPA §1798.105 - Right to delete. Retention exceptions: GDPR Art. 17(3)(b) - Legal obligation"
            },
            "non_compliant_response": {
                "action": "Ignore request or refuse deletion without valid reason or keep all data indefinitely",
                "examples": [
                    "No response (hope customer forgets)",
                    "'We can't delete because it's technically difficult'",
                    "'We need your data for our records' (not specific legal basis)",
                    "Delete from production but not backups (data persists for years)",
                    "Don't notify third-party processors to delete",
                    "Respond after 90 days (missed deadline)"
                ],
                "why_non_compliant": "Erasure is a right, not a request. Technical difficulty is not a valid exception. Must delete unless specific legal retention requirement applies.",
                "consequence": "GDPR: €20M or 4% global revenue for ignoring right to erasure. CCPA: $2,500-$7,500 per violation"
            }
        },
        {
            "scenario": "Employee receives phishing email requesting customer data",
            "situation": "Email from 'CEO' (ceo@gmail.com): 'Urgent! Send me list of all customers with credit card info ASAP!'",
            "applicable_regulations": ["GDPR", "CCPA", "HIPAA", "PCI-DSS"],
            "compliant_response": {
                "action": "Recognize phishing, do not respond, report to security team immediately",
                "steps": [
                    "DO NOT click any links or attachments",
                    "DO NOT reply or provide any information",
                    "Red flags: Gmail address claiming to be CEO, urgent language, requesting sensitive data via email",
                    "Forward email to security@company.com or IT Help Desk",
                    "Delete original email",
                    "Alert colleagues if they might receive similar emails",
                    "If you already clicked/provided data: Report immediately (time-critical for breach response)"
                ],
                "why_compliant": "Prevents data breach by recognizing and reporting phishing attempt. Quick reporting enables security team to block attack.",
                "training_point": "Real CEOs/managers don't ask for sensitive data via Gmail. Always verify through separate channel (call the person on known phone number)."
            },
            "non_compliant_response": {
                "action": "Send customer list with credit card numbers via email attachment",
                "examples": [
                    "Export from database and attach to email reply",
                    "Don't verify sender identity (assume Gmail email is legit)",
                    "Think: 'CEO said urgent, so I better comply'",
                    "Don't report because 'I don't want to bother security team'"
                ],
                "why_non_compliant": "Falls for phishing attack, exposes customer data to criminals, violates multiple regulations (GDPR, PCI-DSS, etc.)",
                "consequence": "Data breach affecting potentially thousands of customers. GDPR fines + CCPA private right of action + PCI-DSS penalties + reputational damage + potential criminal liability"
            }
        }
    ],
    
    "technical_scenarios": [
        {
            "scenario": "Storing user passwords",
            "situation": "Developerimplementing user authentication system",
            "applicable_regulations": ["GDPR Article 32", "CCPA", "NIST guidelines"],
            "compliant": {
                "method": "Hash passwords using bcrypt, Argon2, or PBKDF2 with salt",
                "code_example": """
# ✅ COMPLIANT - Using bcrypt
import bcrypt

def hash_password(password):
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12) # 12 rounds is good balance
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Store 'hashed' in database, never plain password
                """,
                "why": "Bcrypt is designed for password hashing (slow, resistant to brute-force). Even if database is breached, passwords can't be easily cracked.",
                "implementation_notes": [
                    "Use bcrypt rounds=10-12 (higher = slower but more secure)",
                    "Never store plaintext passwords",
                    "Never use reversible encryption (you shouldn't be able to decrypt passwords)",
                    "Each password gets unique salt (bcrypt handles automatically)"
                ]
            },
            "non_compliant": {
                "method": "Store passwords in plaintext or use weak hashing (MD5, SHA1)",
                "code_example": """
# ❌ NON-COMPLIANT - Storing plaintext
db.insert({'username': 'john', 'password': 'MyPassword123'})  # NEVER DO THIS

# ❌ NON-COMPLIANT - Using MD5
import hashlib
password_md5 = hashlib.md5(password.encode()).hexdigest()  # NEVER DO THIS
# MD5 is not designed for passwords, easily cracked with rainbow tables

# ❌ NON-COMPLIANT - Reversible encryption
from cryptography.fernet import Fernet
cipher = Fernet(key)
encrypted_pass = cipher.encrypt(password.encode())  # NEVER DO THIS
# If encryption key is stolen, all passwords exposed
                """,
                "why": "Plaintext passwords fully exposed in breach. MD5/SHA1 can be cracked in seconds with modern GPUs. Reversible encryption means one key compromises all passwords.",
                "consequence": "GDPR: Failure to implement appropriate security (Art failure to implement appropriate security (Art. 32) - fines up to €10M or 2%. Also: massive reputational damage, users' accounts on other sites compromised (password reuse)."
            }
        },
        {
            "scenario": "Logging user activity",
            "situation": "Developer adding logging to track user actions for debugging/analytics",
            "applicable_regulations": ["GDPR Article 5(1)(f)", "CCPA", "HIPAA"],
            "compliant": {
                "method": "Log actions without PII; use user IDs, not names/emails; anonymize logs",
                "code_example": """
# ✅ COMPLIANT - Using user IDs, minimal data
import logging

logger = logging.getLogger(__name__)

def log_user_action(user, action, resource_id):
    # Log using user_id (pseudonymization), not email/name
    logger.info(f'User {user.id} performed {action} on resource {resource_id}')
    # Example output: "User 12345 performed UPDATE on resource 789"
    
# ✅ COMPLIANT - Structured logging with minimal PII
logger.info('user_action', extra={
    'user_id': user.id,
    'action': 'login',
    'ip_address': request.remote_addr,  # OK for security
    'timestamp': datetime.utcnow()
})
# No email, no name, no other PII in logs
                """,
                "why": "User ID is sufficient for debugging. If attacker gets log files, they can't identify specific individuals without also breaching user database.",
                "implementation_notes": [
                    "Avoid logging: emails, names, SSNs, credit cards, health data",
                    "Use pseudonymous IDs: user_id, session_id, transaction_id",
                    "IP addresses: OK for security purposes, but consider truncation (last octet to .0)",
                    "Log retention: Delete logs after 90 days unless needed for audit/compliance",
                    "Encrypt log files if they contain any sensitive data"
                ]
            },
            "non_compliant": {
                "method": "Log full user data including emails, names, sensitive fields",
                "code_example": """
# ❌ NON-COMPLIANT - Logging PII
logger.info(f'User {user.email} (SSN: {user.ssn}) logged in from {ip}')
# Example output: "User john@email.com (SSN: 123-45-6789) logged in from 192.168.1.1"
# NEVER LOG THIS - Logs may not be encrypted, may persist for years

# ❌ NON-COMPLIANT - Logging full objects
logger.debug(f'User object: {user}')  # May dump all user fields including passwords
# Example: "User object: User(id=1, email=john@email.com, password_hash=..., ssn=123-45-6789)"

# ❌ NON-COMPLIANT - Logging API request/response with PII
logger.info(f'API request: {json.dumps(request.json())}')  # May contain credit card, SSN, etc.
                """,
                "why": "Logs may not be encrypted, may be stored for years, may be accessible to many developers/ops teams. Creates unnecessary exposure of PII.",
                "consequence": "GDPR: Violates data minimization (Art. 5(1)(c)) and confidentiality (Art. 5(1)(f)). If logs are breached, now personal data is exposed. Fines based on scope of exposure."
            }
        },
        {
            "scenario": "Implementing API authentication",
            "situation": "Developer building REST API that accesses user data",
            "applicable_regulations": ["GDPR Article 32", "CCPA", "OWASP Top 10"],
            "compliant": {
                "method": "Use OAuth 2.0 or JWT with HTTPS; implement rate limiting; validate tokens server-side",
                "code_example": """
# ✅ COMPLIANT - JWT authentication with FastAPI
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

app = FastAPI()
security = HTTPBearer()
SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # From environment, not hardcoded

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail='Invalid token')
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

@app.get('/api/user/data')
async def get_user_data(user_id: str = Depends(verify_token)):
    # user_id from validated JWT
    # Fetch ONLY this user's data (prevent unauthorized access)
    return get_data_for_user(user_id)
    
# ✅ Enable HTTPS (TLS 1.2+)
# ✅ Rate limiting: Limit to 100requests/minute per user
# ✅ Token expiration: JWT expires after 1 hour
                """,
                "why": "Tokens validated server-side, HTTPS prevents interception, rate limiting prevents abuse, tokens expire (limited damage if leaked)",
                "security_checklist": [
                    "✓ HTTPS/TLS 1.2+ required for all API endpoints",
                    "✓ Tokens validated on every request (don't trust client)",
                    "✓ Tokens expire (1 hour for access token, 30 days for refresh)",
                    "✓ Rate limiting (prevent brute force)",
                    "✓ Authorization: Check user can access requested resource"
                ]
            },
            "non_compliant": {
                "method": "No authentication, API keys in URL, no HTTPS, no rate limiting",
                "code_example": """
# ❌ NON-COMPLIANT - No authentication
@app.get('/api/user/{user_id}/data')
async def get_user_data(user_id: str):
    return get_data_for_user(user_id)  # Anyone can access anyone's data!

# ❌ NON-COMPLIANT - API key in URL query parameter
@app.get('/api/data?api_key=secret123')  # API key visible in logs, browser history
async def get_data(api_key: str):
    if api_key == 'secret123': # Hardcoded, never changes, shared by all users
        return data

# ❌ NON-COMPLIANT - HTTP (not HTTPS)
# Data transmitted in plaintext, interceptable by anyone on network

# ❌ NON-COMPLIANT - No rate limiting
# Attacker can brute-force API keys with unlimited requests
                """,
                "why": "No authentication = anyone can access any user's data. API keys in URL = visible in logs/history. HTTP = data intercepted. No rate limiting = easy to abuse.",
                "consequence": "GDPR: Failure to implement appropriate security (Art. 32). Likely data breach if discovered. Also: CCPA private right of action, reputational damage, customer loss."
            }
        },
        {
            "scenario": "Database encryption at rest",
            "situation": "DevOps engineer setting up production database",
            "applicable_regulations": ["GDPR Article 32", "HIPAA §164.312(a)(2)(iv)", "PCI-DSS Requirement 3.4"],
            "compliant": {
                "method": "Enable Transparent Data Encryption (TDE) or volume encryption with managed keys",
                "implementation": {
                    "aws_rds": """
# ✅ COMPLIANT - AWS RDS with encryption
aws rds create-db-instance \\
    --db-instance-identifier my-db \\
    --engine postgres \\
    --storage-encrypted \\
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/abcd1234
    # Encryption at rest enabled with AWS KMS managed key
                    """,
                    "azure_sql": """
# ✅ COMPLIANT - Azure SQL with TDE
# TDE is enabled by default on Azure SQL Database
# Managed by Azure Key Vault
# Automatic key rotation
                    """,
                    "postgresql": """
# ✅ COMPLIANT - PostgreSQL with pgcrypto for column-level encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    ssn BYTEA, -- Encrypted column
    credit_card BYTEA -- Encrypted column
);

-- Encrypt on insert
INSERT INTO users (email, ssn, credit_card) VALUES (
    'user@example.com',
    pgp_sym_encrypt('123-45-6789', 'encryption_key_from_vault'),
    pgp_sym_encrypt('4111111111111111', 'encryption_key_from_vault')
);

-- Decrypt on select (only by authorized app)
SELECT email, pgp_sym_decrypt(ssn, 'encryption_key_from_vault') AS ssn
FROM users WHERE user_id = 123;
                    """
                },
                "why": "If database files are stolen or backup tapes lost, data remains encrypted and unreadable without encryption keys",
                "key_management": [
                    "Store encryption keys separately from data (AWS KMS, Azure Key Vault, HashiCorp Vault)",
                    "Rotate keys annually or per security policy",
                    "Use managed key services (don't store keys in database or code)",
                    "Implement key access auditing (who accessed which keys when)"
                ]
            },
            "non_compliant": {
                "method": "Plaintext database with no encryption",
                "implementation": """
# ❌ NON-COMPLIANT - No encryption
aws rds create-db-instance \\
    --db-instance-identifier my-db \\
    --engine postgres
    # --storage-encrypted NOT specified = data stored in plaintext

# ❌ NON-COMPLIANT - Database on unencrypted disk
# EC2 instance with PostgreSQL, EBS volume not encrypted
# Anyone with disk access (stolen laptop, decommissioned server) can read data

# ❌ NON-COMPLIANT - Encryption key stored in database
CREATE TABLE encryption_keys (
    key_name VARCHAR(255),
    key_value TEXT -- ❌ Storing encryption key IN the encrypted database!
);
# If attacker gets database, they get encryption keys too
                """,
                "why": "Plaintext database = full data exposure if disk/backups stolen. Keys in database = defeats purpose of encryption.",
                "consequence": "GDPR: Art. 32 violation (failure to encrypt). If breached: Art. 33 notification required, potential max fines. HIPAA: Breach notification required if unencrypted PHI exposed. PCI-DSS: Immediate failure of compliance, loss of payment processing ability."
            }
        }
    ],
    
    "process_scenarios": [
        {
            "scenario": "Onboarding new employee - granting data access",
            "situation": "New customer support representative needs access to customer records",
            "applicable_regulations": ["GDPR Article 32", "HIPAA", "SOX"],
            "compliant": {
                "process": "Grant minimum necessary access based on job role, enable MFA, provide training before access",
                "steps": [
                    "1. Define role: Customer Support Rep needs to view customer profiles and order history",
                    "2. Grant minimum access: Read-only access to customer support portal (not direct database)",
                    "3. Specific permissions: Can view name, email, order history | Cannot view: passwords, credit cards, SSNs",
                    "4. Enable MFA: Require multi-factor authentication for portal access",
                    "5. Training: Complete data privacy training BEFORE granting access",
                    "6. Document: Log who approved access, what level, effective date",
                    "7. Review: Schedule 90-day access review (still needed?)"
                ],
                "why": "Least privilege principle - employee can do their job but cannot access unnecessary data. MFA prevents unauthorized access if password compromised.",
                "access_matrix_example": {
                    "customer_support": {
                        "can_access": ["customer_name", "email", "order_history", "support_tickets"],
                        "cannot_access": ["passwords", "ssn", "credit_cards", "full_database"],
                        "permission_level": "read-only"
                    }
                }
            },
            "non_compliant": {
                "process": "Grant full admin access to all systems, no training, shared password",
                "examples": [
                    "Give database admin credentials shared by entire team",
                    "No MFA (just password)",
                    "Access granted before training completed",
                    "No documentation of who has access to what",
                    "Never review whether access is still needed",
                    "Same access level for all employees regardless of role"
                ],
                "why": "Excessive access violates data minimization. Shared passwords = can't audit who accessed what. No training = employee doesn't know compliance requirements.",
                "consequence": "Insider threat risk (malicious or accidental). If breach occurs, can't determine who was responsible. Regulatory violations for excessive access."
            }
        },
        {
            "scenario": "Employee termination - data access revocation",
            "situation": "Employee resigns or is terminated",
            "applicable_regulations": ["GDPR", "HIPAA", "SOX", "Industry best practices"],
            "compliant": {
                "process": "Immediate access revocation on termination date, return devices, audit access logs",
                "steps": [
                    "On termination date (or immediately if involuntary termination):",
                    "1. Disable all user accounts (email, systems, applications) - within 1 hour",
                    "2. Revoke VPN/remote access immediately",
                    "3. Collect all company devices (laptop, phone, badge, keys)",
                    "4. Wipe remote devices if not returned",
                    "5. Change any shared passwords the employee knew",
                    "6. Audit logs: Review employee's last 30 days of data access (anything suspicious?)",
                    "7. Document: Log termination date, access revocation time, devices returned",
                    "8. Follow-up: 30-day post-termination audit to ensure all access removed"
                ],
                "why": "Terminated employees (especially involuntary) may have motive to steal or sabotage data. Immediate revocation prevents data exfiltration.",
                "timeline": {
                    "critical_systems": "0-1 hour (email, VPN, production access)",
                    "standard_systems": "Same day (internal tools, apps)",
                    "audit_review": "Within 7 days (review access logs)"
                }
            },
            "non_compliant": {
                "process": "Leave access active for days/weeks, don't collect devices, no audit",
                "examples": [
                    "Employee terminates Friday, access not revoked until following Monday",
                    "Never collect laptop (employee keeps company data)",
                    "Don't wipe remote devices",
                    "Don't review what employee accessed before leaving",
                    "Shared passwords not changed (ex-employee still knows them)",
                    "Discover ex-employee still logging in months later"
                ],
                "why": "Gives ex-employee opportunity to download customer lists, steal trade secrets, or sabotage systems. Major data breach risk.",
                "consequence": "Data theft by ex-employee = data breach requiring notification. GDPR fines for failure to secure data. Also: trade secret theft, competitive harm."
            }
        },
        {
            "scenario": "Responding to user consent withdrawal",
            "situation": "User clicks 'Unsubscribe' or withdraws consent for data processing",
            "applicable_regulations": ["GDPR Article 7(3)", "CCPA", "CAN-SPAM"],
            "compliant": {
                "process": "Honor opt-out immediately, make it as easy to withdraw as to give consent",
                "steps": [
                    "1. Provide easy unsubscribe link in every marketing email",
                    "2. On click: Immediate opt-out (no confirmation required, no login required)",
                    "3. Update database: Set marketing_consent=FALSE immediately",
                    "4. Stop processing: Exclude from all future marketing campaigns within 10 days",
                    "5. Confirmation: Show message 'You have been unsubscribed' + send confirmation email (one-time)",
                    "6. Suppression list: Keep email on 'do not contact' list to prevent re-addition",
                    "7. Respect indefinitely: Don't re-ask for consent for at least 12 months (CCPA)",
                    "8. Optional: Ask for feedback 'Why are you unsubscribing?' but don't require answer"
                ],
                "why": "Consent must be freely given and easy to withdraw (GDPR). Making it difficult = coercive = invalid consent in first place.",
                "unsubscribe_page_example": """
✅ COMPLIANT Unsubscribe Page:
'You have been unsubscribed from marketing emails. You will no longer receive promotional content.'
[Button: Confirm]
No login required, no question why, immediate effect.
                """
            },
            "non_compliant": {
                "process": "Make unsubscribe difficult, require login, continue emailing, ask to reconsider",
                "examples": [
                    "Unsubscribe requires login (many users don't remember passwords)",
                    "No unsubscribe link (must email support and wait days)",
                    "Multiple confirmation steps: 'Are you sure? Really sure? We'll miss you!'",
                    "Unsubscribe only from one type of email, still send others",
                    "Continue sending emails for weeks after unsubscribe",
                    "Hide unsubscribe link in tiny font or same color as background",
                    "Re-subscribe user months later automatically"
                ],
                "why": "Making withdrawal difficult = coercive consent = invaliddoes not comply with GDPR Art. 7(3) 'as easy to withdraw as to give'. CAN-SPAM violation.",
                "consequence": "GDPR: Invalid consent = all processing based on that consent is unlawful. Fines up to €10M or 2%. CAN-SPAM: Up to $46,517 per violation."
            }
        }
    ],
    
    "data_breach_scenarios": [
        {
            "scenario": "Discovering a data breach",
            "situation": "Security team discovers unauthorized access to customer database on Friday afternoon",
            "applicable_regulations": ["GDPR Article 33-34", "HIPAA §164.408", "State breach notification laws"],
            "compliant": {
                "process": "Immediate containment, assess scope, notify authorities within 72 hours, notify individuals without undue delay",
                "immediate_actions_friday_evening": [
                    "Hour 0: Discover breach - terminate unauthorized access immediately",
                    "Hour 1: Activate incident response team (don't wait until Monday)",
                    "Hour 2: Contain breach - isolate affected systems, change credentials",
                    "Hour 3-6: Begin scope assessment - what data was accessed?",
                    "Hour 8: Preserve evidence - logs, access records (don't delete)",
                    "Hour 12: Notify Data Protection Officer and legal team"
                ],
                "within_72_hours_gdpr": [
                    "Assess: Nature of breach (unauthorized access, data theft, ransomware)",
                    "Quantify: Number of individuals affected (approximate OK if exact unknown)",
                    "Identify: Categories of personal data compromised (names, emails, SSNs, etc.)",
                    "Notify regulator: Submit breach notification to lead Data Protection Authority",
                    "Document: Consequences likely to result from breach, measures taken to address"
                ],
                "notify_individuals_promptly": [
                    "Determine: Does breach pose high risk to individuals? (If yes, must notify)",
                    "Draft notification: Clear explanation of what happened, what data affected, steps taken, recommendations",
                    "Send notifications: Email to affected individuals (or letter if no email)",
                    "Provide support: Free credit monitoring if financial data compromised",
                    "Set up hotline: Dedicated support for questions"
                ],
                "why": "Fast response limits damage. 72-hour GDPR deadline is strict. Individual notification protects them (can change passwords, watch for fraud).",
                "sample_timeline": {
                    "hour_0": "Discover breach",
                    "hour_12": "Breach contained",
                    "hour_48": "Scope assessment complete",
                    "hour_72": "Regulator notified (GDPR deadline)",
                    "day_7": "Individual notifications sent",
                    "day_30": "Final incident report, preventive measures implemented"
                }
            },
            "non_compliant": {
                "process": "Delayed response, try to cover up, miss notification deadlines, don't notify individuals",
                "examples": [
                    "Friday discovery → 'We'll deal with it Monday' (breach active all weekend)",
                    "Try to fix quietly without notifying anyone (hope no one finds out)",
                    "Downplay severity to avoid reporting ('Only a few records, no big deal')",
                    "Miss 72-hour GDPR deadline (notify regulator 2 weeks later)",
                    "Don't notify individuals ('They'll just panic, better not tell them')",
                    "Delete logs to hide extent of breach",
                    "Blame vendor but don't take responsibility"
                ],
                "why": "Delayed containment = more data stolen. Cover-up = worse penalties when discovered. Not notifying = individuals can't protect themselves.",
                "consequence": "GDPR: Failure to notify within 72 hours = separate violation with fines up to €10M or 2%. Cover-up discovered = max penalties (€20M or 4%). Also: criminal liability possible, shareholder lawsuits, permanent reputation damage."
            }
        }
    ]
}
