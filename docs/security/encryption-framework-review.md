# Encryption Framework Review

## Sensitive Data Inventory

| Data | Where used or stored | Current protection | Risk or question |
|---|---|---|---|
| Google OAuth client secret | Backend environment | Environment variable | Confirm production secret storage |
| Google OAuth tokens | To be investigated | Unknown | May be stored in plain text |
| JWT secret | Backend environment | Environment variable | Confirm strength and rotation |
| Voice-session JWT | Backend and VAPI flow | Signed, short-lived token | Confirm it is never logged |
| OpenAI/Groq API keys | Backend environment | Environment variable | Confirm not exposed to frontend |
| User email and ID | Backend/session storage | To be investigated | Confirm encryption and retention |
| Gmail and Calendar data | Backend integrations | To be investigated | Confirm storage and logs |
| Voice transcripts | Voice processing flow | To be investigated | Confirm storage and deletion |
## Environment and Secret Configuration Review

The backend expects sensitive values to be provided through environment variables rather than hard-coded directly in the application.

### Sensitive variables identified

- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `JWT_SECRET_KEY`
- `GOOGLE_CLIENT_SECRET`
- `SF_CLIENT_SECRET`
- `TELESIGN_API_KEY`
- `DEEPGRAM_API_KEY`

### Security-related configuration identified

- `ENVIRONMENT`
- `COOKIE_SECURE`
- `COOKIE_SAMESITE`
- `ENABLE_TOOL_LOGGING`
- `TELESIGN_USE_ENCRYPTED`
- `VAPI_SERVER_URL`

### Initial observations

- The example file uses placeholder values rather than real credentials.
- Secret values are expected to be loaded from the backend environment.
- Production secret storage still needs to be confirmed.
- Cookie security settings need to be checked in the application code.
- Tool logging needs review to confirm that tokens or user data are not written to logs.
## OAuth Credential Storage Review

### Current design identified

- The project currently references `oauth.json` as centralized credential storage.
- The migration script describes `oauth.json` as plaintext storage.
- A migration path exists to move credentials to encrypted DynamoDB storage.
- The encrypted storage requires a `MASTER_ENCRYPTION_KEY`.
- The migration supports a dry-run mode before writing changes.

### Security concern identified

The migration script prints sensitive information to the terminal, including:

- User email
- User ID
- Organization ID
- The first 20 characters of Salesforce access tokens
- The first 20 characters of Salesforce refresh tokens

OAuth access and refresh tokens should not be displayed in terminal output or application logs, even partially.

### Initial recommendation

- Remove or redact all token output.
- Avoid printing personal identifiers unless required.
- Confirm whether the DynamoDB migration has been completed in production.
- Confirm how `MASTER_ENCRYPTION_KEY` is stored and rotated.
- Confirm that plaintext `oauth.json` is securely deleted after successful migration.## DynamoDB Credential Encryption Review

### Confirmed behavior

- The DynamoDB credential manager uses a dedicated encryption service.
- Credential data is encrypted before it is written to DynamoDB.
- Encrypted bytes are Base64-encoded for storage.
- The stored field is named `encrypted_data`.
- Credential storage raises an error when the encryption service is unavailable, rather than storing plaintext.
- Optional credential expiration is supported through DynamoDB TTL.
- AWS region and credentials are loaded through environment variables.

### Items still requiring review

- Encryption algorithm and mode.
- How the master encryption key is generated.
- Where the master encryption key is stored in production.
- Whether every encrypted value uses a unique nonce or initialization vector.
- Whether encryption includes integrity/authentication protection.
- Key rotation and recovery procedures.
- Whether AWS credentials should rely on an IAM role instead of long-lived environment keys.## Encryption Service Review

### Confirmed protections

- Credentials are encrypted using AES-256-GCM.
- AES-GCM provides confidentiality and authentication protection.
- A fresh random 12-byte nonce is generated for each encryption operation.
- The authentication tag is verified during decryption.
- Decryption fails if the key is incorrect or the encrypted data has been modified.
- The encryption key is derived using PBKDF2 with SHA-256.
- PBKDF2 currently uses 100,000 iterations.
- A key-rotation method exists.
- The master key is loaded from `MASTER_ENCRYPTION_KEY`.

### Security concern identified

The encryption salt falls back to the hard-coded value:

`securiva-salt-v1`

Production should not silently use a predictable default salt.

### Recommendations

- Require `ENCRYPTION_SALT` to be explicitly configured in production.
- Store `MASTER_ENCRYPTION_KEY` and `ENCRYPTION_SALT` in an approved secret-management system.
- Confirm that production is not using the default salt.
- Document key rotation, backup, recovery, and emergency revocation procedures.
- Add automated tests for tampered ciphertext, wrong keys, unique nonces, and key rotation.
## Authentication Cookie and JWT Review

### Confirmed protections

- Authentication cookies use `HttpOnly`.
- Production cookies can be restricted to HTTPS through `COOKIE_SECURE`.
- SameSite protection is configurable.
- Cookies are scoped to the current host.

### Security concerns

- Session cookies currently allow a 30-day lifetime.
- The manual-login JWT includes `sub` and `iat`, but no `exp` expiration claim.
- User email addresses are included in redirect URLs and may appear in browser history or logs.
- JWT security depends on `JWT_SECRET_KEY` being securely configured.

### Recommendations

- Add an explicit JWT expiration claim.
- Consider a shorter session lifetime for sensitive accounts.
- Remove email addresses from redirect query strings.
- Require a strong `JWT_SECRET_KEY` at application startup.
- Add tests for expired and invalid JWTs.

## JWT Validation Review

### Confirmed protections

- `JWT_SECRET_KEY` is required before the token verifier starts.
- Tokens are verified using the `HS256` algorithm.
- Invalid signatures and malformed tokens are rejected.
- Expired tokens are rejected when an `exp` claim exists.

### Security concerns

- The manual-login JWT currently has no `exp` claim, so it may remain cryptographically valid after the browser cookie expires.
- Token-validation errors are printed directly to the terminal.
- The verifier returns an access token even when optional claims such as `client_id` are missing.

### Recommendations

- Add a required `exp` claim to every authentication JWT.
- Require important claims such as `sub`, `iat`, and `exp` during decoding.
- Replace direct `print()` statements with structured, redacted security logging.
- Add automated tests for expired, malformed, wrong-signature, and missing-claim tokens.

## Voice Session JWT Review

### Confirmed protections

- Voice-session tokens include `sub`, `type`, `iat`, and `exp`.
- Voice-session tokens expire after 5 minutes.
- Tokens are signed using `HS256`.
- The raw API key remains in an `HttpOnly` cookie and is exchanged for a short-lived voice token.
- Invalid or missing API keys are rejected before a voice token is issued.

### Remaining checks

- Confirm the production `JWT_SECRET_KEY` is strong and shared consistently between token creation and validation.
- Confirm the voice token reaches VAPI metadata and the backend webhook correctly.
- Confirm voice-session events do not log the token value.
## Activity Logging Review

### Confirmed behavior

- Activity events may be stored in DynamoDB or a local file.
- Entries include event type, timestamp, status, user email and user ID.
- Optional `details` and `error` values are stored with the event.
- Voice-session logging currently records the event and user ID, but not the voice token directly.

### Security concerns

- Arbitrary `details` are stored without visible redaction.
- Full error messages may contain credentials, tokens, personal information or internal system details.
- User email addresses and IDs are retained in activity logs.
- The retention period and access controls for these logs are not yet confirmed.

### Recommendations

- Add centralized redaction for tokens, API keys, passwords, cookies and authorization headers.
- Sanitize error messages before saving them.
- Minimize personal identifiers in logs.
- Define log retention and deletion requirements.
- Restrict access to activity logs.
- Add tests confirming sensitive values are never stored.
## Activity Log Storage and Retention Review

### Confirmed protections

- DynamoDB activity records include a TTL value.
- DynamoDB logs are designed to expire automatically after `LOG_TTL_DAYS`.
- A local file fallback prevents complete loss of audit records when DynamoDB is unavailable.

### Security concerns

- Local fallback logs do not show an automatic expiration or deletion mechanism.
- Local log entries are written as complete JSON records without visible encryption or redaction.
- Local files may contain user email, user ID, arbitrary details and full error messages.
- A DynamoDB failure may cause sensitive records to remain locally for an unlimited period.
- DynamoDB write errors are printed directly to the terminal.

### Recommendations

- Apply the same retention policy to local fallback logs.
- Redact sensitive values before both DynamoDB and file storage.
- Restrict local log-file permissions.
- Encrypt sensitive local logs or avoid storing sensitive fields.
- Rotate and delete local logs automatically.
- Replace direct error printing with sanitized structured logging.
## Logging Configuration Review

### Confirmed configuration

- DynamoDB logging is enabled through `USE_DYNAMO_LOGS`.
- The DynamoDB table is `SecuriVALogs`.
- The configured AWS region is `us-east-2`.
- DynamoDB activity logs use a 90-day TTL.
- Local fallback logs are written to `backend/logs/activity.json`.

### Security concerns

- `USE_DYNAMO_LOGS` defaults to `false`, which may cause local file logging unless production overrides it.
- Local fallback logs do not have an equivalent 90-day deletion policy.
- Local logs may contain personal identifiers, arbitrary details and full error messages.
- The DynamoDB table name and AWS region are hard-coded.
- No visible encryption or permission-hardening is applied to the local file.

### Recommendations

- Require explicit production logging configuration.
- Apply retention and rotation to `activity.json`.
- Redact sensitive values before all log writes.
- Restrict local log-file permissions.
- Make the table name, region and retention period configurable.
- Confirm DynamoDB encryption-at-rest and access-control settings in AWS.
## AI Request and Response Logging Review

### Confirmed behavior

- AI activity is written to `backend/my_app/server/ai_calls.log`.
- Each log entry includes:
  - user ID
  - selected model
  - complete AI messages
  - complete AI response
- Logging uses a rotating file handler.
- Each file is limited to approximately 5 MB.
- Up to five rotated backup files may be retained in addition to the active file.

### Positive control

- Log rotation limits uncontrolled file growth.

### High-priority security concerns

- Complete prompts and AI responses are written to a local plaintext log.
- Messages may include email, calendar, chat, customer or business information.
- No redaction or sensitive-data filtering is visible before logging.
- No encryption is visible for the AI log files.
- User IDs are stored alongside complete conversation content.
- Rotated backup files extend the period during which sensitive content remains accessible.
- No time-based retention or secure deletion policy is visible.

### Recommendations

- Do not log complete AI prompts or responses in production.
- Log only operational metadata such as request ID, model, duration, token count and success status.
- Add centralized redaction for credentials, tokens, email addresses and personal information.
- Disable detailed AI logging by default in production.
- Restrict file permissions for AI logs.
- Define a time-based retention and secure deletion policy.
- Add automated tests confirming that prompts, responses and secrets are not written to logs.
## Chat Endpoint Data-Logging Review

### Confirmed behavior

- The `/api/chat` endpoint accepts user-supplied messages, model and API values.
- It sends the complete message list to `execute_chat_with_tools`.
- After execution, `log_ai_call` stores the full message list and complete result.
- The activity logger separately stores the latest user message, truncated to 200 characters.
- Activity logs also store the selected model, API and tool-call count.

### High-priority security concerns

- User conversation content is duplicated across two logging systems.
- Complete prompts and AI responses are stored in the AI-call log.
- The activity log stores up to 200 characters of the latest user message.
- Tool-enabled results may include email, calendar, customer or other connected-account data.
- Truncating a message does not make it non-sensitive.
- There is no visible consent, redaction or production-only disablement before logging.
- Multiple copies of the same sensitive content increase exposure and retention risk.

### Recommendations

- Remove complete prompts and responses from production logs.
- Remove `user_message` content from activity logs.
- Store only non-content metadata such as request ID, model, status, duration and tool-call count.
- Add a production-safe logging flag that defaults to disabled for message content.
- Apply centralized secret and personal-data redaction before all logging.
- Add tests confirming that chat content and tool results are not written to log files.
## Git Protection Review

### Confirmed protections

- `backend/my_app/server/oauth.json` is explicitly excluded by `.gitignore`.
- `backend/local.db` is excluded.
- Credential and secret JSON filename patterns are excluded.
- Certificate and private-key file patterns are excluded.
- Several deployment-secret files are explicitly excluded.

### Security concerns

- `.gitignore` does not remove files that were committed previously.
- Repository history has not yet been checked for previously committed OAuth files or credentials.
- Filename-based rules may not protect secrets stored under unexpected names.

### Recommendations

- Confirm `oauth.json` is not currently tracked by Git.
- Review Git history for previously committed secrets.
- Use automated secret scanning in CI.
- Rotate any credential that may have entered repository history.
- Keep production credentials in a managed secret store rather than local files.

### Git history verification

- Confirmed: `backend/my_app/server/oauth.json` is not currently tracked by Git.
- Confirmed: no Git commit history was found for that exact file path.

## Google OAuth Callback Credential Storage Review

### Confirmed behavior

- After successful Google OAuth authentication, the application calls `credentials.to_json()`.
- The serialized Google credentials are stored under the user’s Google service record.
- The full user-data structure is written to the local `oauth.json` file using `json.dump`.
- A generated application API key is also passed to `store_api_key` with the same OAuth file path.
- The OAuth file is excluded from current Git tracking.

### Critical security concerns

- Google OAuth credentials are written to a local plaintext JSON file.
- The serialized credentials may include access tokens, refresh tokens, client configuration and expiry information.
- No encryption is visible before writing the file.
- No restrictive file permissions are applied in the visible code.
- The application API key may also be stored in the same plaintext file.
- A compromise of the local file could expose multiple users and connected Google accounts.
- The file is rewritten as one centralized credential store, increasing the impact of file exposure.

### Recommendations

- Stop storing production OAuth credentials in plaintext JSON.
- Store credentials only in the encrypted DynamoDB credential manager.
- Encrypt credentials before persistence using the existing encryption service.
- Use least-privilege AWS IAM permissions for the credential table.
- Remove plaintext credentials after a verified migration.
- Restrict any temporary local credential file to development only.
- Add tests confirming that access tokens, refresh tokens, client secrets and API keys are never written to plaintext files.

## Application API Key Storage Review

### Confirmed protections

- The generated application API key is not visibly stored in full.
- The code stores a hash of the API key using `hash_api_key`.
- A limited key prefix is stored for identification.
- Creation and last-used metadata are also retained.

### Remaining concerns

- The hashed API-key record is stored inside the same plaintext `oauth.json` file as Google OAuth credentials.
- The security of the stored hash depends on the implementation of `hash_api_key`, which still needs review.
- Local file permissions and retention controls remain unconfirmed.

### Recommendations

- Continue storing only a non-reversible API-key hash.
- Review the hash algorithm and comparison method.
- Use constant-time comparison when validating API keys.
- Move API-key metadata out of the shared plaintext OAuth file.
- Store production API-key records in a protected database with least-privilege access.
## API Key Hashing Review

### Confirmed behavior

- API keys are hashed using SHA-256 before storage.
- Only the hexadecimal hash is stored for validation.
- A 12-character prefix is retained for display and identification.

### Positive controls

- The complete API key is not stored in the visible persistence code.
- SHA-256 is a one-way cryptographic hash.
- Long randomly generated API keys are resistant to practical brute-force recovery.

### Security concerns

- The API-key hash is not protected with a server-side secret or pepper.
- Identical API keys produce identical hashes.
- `get_key_prefix` returns the complete key when the key is 12 characters or shorter.
- The validation comparison method still needs review.

### Recommendations

- Use an HMAC-based hash with a server-side secret for stored API-key fingerprints.
- Alternatively, retain SHA-256 only when keys are cryptographically random and sufficiently long.
- Never return or store an entire short API key as its prefix.
- Limit displayed prefixes to a safe number of characters.
- Use constant-time comparison during API-key validation.
## API Key Validation Review

### Confirmed behavior

- The supplied API key is hashed before comparison.
- The stored hash is compared using the normal `==` operator.
- A successful match returns the associated user ID.
- The user’s `last_used` timestamp is updated after successful validation.
- Development mode supports a bypass API key.
- The default development bypass value is `dev-bypass`.
- Authentication timing information is printed to the terminal.

### Security concerns

- Hash comparison does not use a constant-time comparison function.
- The default development bypass key is predictable.
- A development configuration accidentally used in production could permit unauthorized access.
- Authentication timing output may expose unnecessary internal diagnostic information.
- The OAuth file is loaded for every validation request, which also keeps plaintext credential storage in the authentication path.

### Recommendations

- Replace normal hash equality with `hmac.compare_digest`.
- Remove the hard-coded `dev-bypass` fallback.
- Require `DEV_API_KEY` to be explicitly configured when development bypass is enabled.
- Fail safely if a development bypass key is missing.
- Ensure development bypasses cannot run when `ENVIRONMENT=production`.
- Replace direct timing prints with sanitized debug logging disabled in production.
## API Key Generation Review

### Confirmed protections

- API keys are generated using Python’s cryptographically secure `secrets` module.
- Each key uses `secrets.token_urlsafe(32)`.
- The generated value contains approximately 256 bits of randomness before encoding.
- Keys use the `sk_live_` prefix.
- The plaintext key is intended to be shown to the user only once.
- Only a hash and limited prefix are stored afterward.

### Assessment

- The generation method is strong and appropriate for production API keys.
- The long random value makes brute-force recovery from a SHA-256 hash impractical.
- The remaining improvements are constant-time validation, safer prefix handling and removal of the predictable development bypass.
## Master Encryption Key Initialization Review

### Confirmed protections

- `MASTER_ENCRYPTION_KEY` is loaded from the environment.
- The encryption service raises an error when the master key is missing.
- The master key is not visibly printed or logged.
- The service derives a 256-bit key using PBKDF2 with SHA-256.
- PBKDF2 uses 100,000 iterations.
- The derived key is used with AES-GCM.

### Security concerns

- Missing-key validation occurs when `CredentialEncryptionService` is instantiated, not necessarily during application startup.
- Production startup may succeed without the master key if the encryption service is not initialized immediately.
- `ENCRYPTION_SALT` falls back to the hard-coded value `securiva-salt-v1`.
- Reusing the same master key and default salt across deployments would derive the same encryption key.

### Recommendations

- Validate `MASTER_ENCRYPTION_KEY` during production application startup.
- Require `ENCRYPTION_SALT` explicitly in production.
- Remove the hard-coded production salt fallback.
- Store the master key and salt in an approved managed secret store.
- Add startup tests confirming production cannot run without required encryption configuration.
## Encryption Service Initialization Review

### Confirmed behavior

- The encryption service uses a singleton instance.
- `_encryption_service` is initialized to `None`.
- `CredentialEncryptionService` is created only when `get_encryption_service()` is first called.
- The master encryption key is therefore validated lazily rather than during application startup.
- The service includes a credential key-rotation method.

### Security concerns

- Production may start successfully without `MASTER_ENCRYPTION_KEY`.
- A missing or invalid key may remain undetected until the first credential operation.
- Health checks may report the application as available even though encrypted credential operations will fail.
- Key rotation behavior depends on the old master key and requires automated verification.

### Recommendations

- Validate required encryption configuration during production startup.
- Add a startup readiness check for the master key and encryption salt.
- Do not expose the key values in readiness output or logs.
- Add automated tests for encryption, decryption, authentication failure and key rotation.
## Plaintext OAuth File Cleanup Review

### Confirmed finding

- No `Path.unlink()` cleanup was found for `backend/my_app/server/oauth.json`.
- The existing `unlink()` calls relate only to tests and TeleSign log cleanup.
- No verified automatic deletion of the plaintext OAuth credential file has been identified after DynamoDB migration.

### Security concern

- Plaintext OAuth credentials may remain on disk after encrypted migration.
- This conflicts with the policy requirement that OAuth tokens must not be stored in plaintext. :contentReference[oaicite:0]{index=0}

### Recommendation

- Delete the plaintext OAuth file only after every credential record has been encrypted, stored and verified successfully.
- Create a protected backup only when explicitly required for rollback.
- Abort cleanup if any migration record fails.
- Record a sanitized migration result without printing token values.

- A repository-wide search also found no `os.remove()` operation for deleting the plaintext OAuth credential file.

## Application Startup Secret Validation Review

### Confirmed behavior

- The top-level Starlette application uses a `lifespan` startup function.
- Startup initializes the MCP session manager and cleanup task.
- Shutdown closes MCP connections.
- No validation of `MASTER_ENCRYPTION_KEY`, `ENCRYPTION_SALT`, or `JWT_SECRET_KEY` is visible in the top-level lifespan function.
- The startup function does not initialize `CredentialEncryptionService`.

### Security concern

- The application may start successfully with missing encryption configuration.
- Health checks may report the service as available even though credential encryption or decryption will fail later.
- Configuration errors may remain undetected until a sensitive operation is attempted.

### Recommendation

- Add a production startup validation function.
- Require `MASTER_ENCRYPTION_KEY`, `ENCRYPTION_SALT`, and `JWT_SECRET_KEY` in production.
- Fail startup safely when required secrets are absent.
- Never print secret values in startup errors or logs.
- Add automated tests proving that production startup fails when required secrets are missing.

## Existing Encryption Test Coverage Review

### Confirmed finding

- A search for `CredentialEncryptionService` within `backend/tests` returned only one reference.
- The result appears to be a parameter description or type reference in `dynamodb_credential_manager.py`.
- No dedicated automated test for `CredentialEncryptionService` was identified through this search.

### Test coverage gaps

- Encryption and decryption round-trip testing
- Rejection of modified or corrupted ciphertext
- Missing master-key behavior
- Missing production salt behavior
- Key-rotation validation
- Prevention of plaintext credential persistence
- Logging redaction tests

### Recommendation

- Add focused automated security tests before treating the Encryption Framework as validated.
- Preserve terminal test results as implementation evidence.
### Encryption test search clarification

- Two calls to `encrypt_credentials()` were found in `backend/tests/dynamodb_credential_manager.py`.
- These results confirm that the credential manager uses the encryption service.
- The search results do not yet confirm that dedicated pytest test cases or security assertions exist.
- Test coverage for encryption round trips, ciphertext tampering, missing keys, production configuration, and key rotation remains to be verified.
### Final encryption test verification

- A search for `def test_` in `backend/tests/dynamodb_credential_manager.py` returned no results.
- The file uses the encryption service but does not contain identifiable pytest test functions.
- Dedicated automated tests for encryption, decryption, ciphertext integrity, key rotation, missing configuration, logging redaction and plaintext credential prevention still need to be created.

## Encryption Framework Requirement Gap Analysis

| Requirement | Current Status | Confirmed Gap | Required Action | Evidence Needed |
|---|---|---|---|---|
| AES-256-GCM credential encryption | Partially implemented | Encryption service exists, but configuration is validated only when first used | Add production startup validation and automated tests | Source-code review and passing encryption tests |
| Protect OAuth credentials at rest | Not compliant | Google OAuth tokens are written to plaintext `oauth.json` | Move production credentials to encrypted DynamoDB storage and remove plaintext persistence | Storage inspection and plaintext-secret test |
| Remove plaintext file after migration | Not implemented | No `unlink()` or `os.remove()` cleanup was found | Delete the plaintext file only after successful encrypted migration and verification | Migration test and file-system evidence |
| Secure AI logging | Not compliant | Full prompts and AI responses are stored in plaintext logs | Replace content logging with safe operational metadata and redaction | Sanitized log sample and automated test |
| Secure activity logging | Partially implemented | User-message previews, arbitrary details and errors may contain sensitive information | Remove unnecessary content and add centralized redaction | Activity-log test and sanitized sample |
| Local log retention | Not implemented | Local fallback logs have no confirmed rotation or deletion policy | Add rotation, retention and restricted permissions | Configuration evidence and cleanup test |
| API-key generation | Implemented | No major generation weakness found | Retain cryptographically secure generation | Unit test confirming length and uniqueness |
| API-key validation | Partially implemented | Normal equality is used instead of constant-time comparison | Replace comparison with `hmac.compare_digest` | Valid-key and invalid-key tests |
| Development bypass security | Not compliant | Predictable default value `dev-bypass` exists | Remove the default and block development bypass in production | Production configuration test |
| Production secret validation | Not implemented | Startup does not validate encryption key, salt or JWT secret | Add startup validation that fails safely without exposing secret values | Startup failure tests |
| Encryption security tests | Not implemented | No dedicated pytest tests were found | Add encryption, decryption, tampering, rotation and missing-key tests | Passing pytest output |
| Secure KMS or vault | Roadmap / not implemented | No confirmed managed KMS integration exists | Design and implement an isolated KMS-backed key provider | Architecture, IAM and KMS configuration evidence |
| Continuous key backup | Roadmap / not implemented | No confirmed immediate backup of new or rotated keys | Ensure key creation and rotation include immediate protected replication | Backup verification test |
| Two-hour key recovery | Roadmap / not tested | No tested recovery procedure exists | Document and test recovery against the 2-hour RTO | Timed recovery exercise |
| Two-person recovery authorization | Roadmap / governance control | No confirmed multi-party approval workflow exists | Define separate requester and approver roles for recovery | IAM policy and approval evidence |
| Recovery audit logging | Roadmap / not implemented | No confirmed immutable key-recovery audit trail exists | Record access, copy, restoration and deletion attempts in protected logs | Audit-log sample |
| Secure key restoration | Roadmap / not tested | Encrypted restoration and integrity verification are not confirmed | Use authenticated encrypted channels and verify restored-key integrity | Restoration and integrity test |
| AWS regional failover | Roadmap / not implemented | No confirmed KMS recovery in a secondary region | Define primary and recovery regions and regional recovery procedure | Failover architecture and tabletop evidence |

## Remediation Priorities
### Critical — address first

1. Stop storing Google OAuth credentials in plaintext `oauth.json`.
2. Stop logging complete AI prompts and responses.
3. Remove user-message content and sensitive errors from activity logs.
4. Validate `MASTER_ENCRYPTION_KEY`, `ENCRYPTION_SALT`, and `JWT_SECRET_KEY` during production startup.
5. Create dedicated encryption security tests.

### High

1. Replace API-key hash comparison with `hmac.compare_digest`.
2. Remove the default `dev-bypass` API key.
3. Add centralized sensitive-data redaction.
4. Add local log rotation, retention, and permission controls.
5. Delete plaintext OAuth storage only after encrypted migration is successfully verified.

### Medium

1. Improve API-key prefix handling.
2. Replace direct terminal printing with sanitized structured logging.
3. Make logging table name, AWS region, and retention settings configurable.
4. Document retention periods for credentials, logs, AI content, and backup files.

### Architecture and Disaster-Recovery Roadmap

1. Design an AWS KMS-backed key provider.
2. Define primary and recovery AWS regions.
3. Support immediate backup or replication of new and rotated keys.
4. Define two-person authorization for emergency key recovery.
5. Create immutable recovery audit logging.
6. Define secure restoration and automated integrity verification.
7. Test key restoration against the approved 2-hour RTO.