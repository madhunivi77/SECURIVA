-- backend/my_app/server/migrations/001_multitenant_credentials_schema.sql
-- Multi-tenant credential storage schema for SECURIVA
-- Supports: Google OAuth, Salesforce OAuth, Telesign API Keys

-- ============================================================================
-- ORGANIZATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS organizations (
    org_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_name VARCHAR(255) NOT NULL,
    org_slug VARCHAR(100) UNIQUE NOT NULL, -- For subdomain: acme.securiva.com
    plan_tier VARCHAR(50) DEFAULT 'free', -- free, pro, enterprise
    max_users INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}', -- Org-specific configurations
    CONSTRAINT valid_plan_tier CHECK (plan_tier IN ('free', 'pro', 'enterprise'))
);

-- Index for fast slug lookup (subdomain routing)
CREATE INDEX idx_orgs_slug ON organizations(org_slug) WHERE is_active = TRUE;
CREATE INDEX idx_orgs_active ON organizations(is_active);

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(org_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) DEFAULT 'member', -- owner, admin, member
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    metadata JSONB DEFAULT '{}', -- User preferences, profile data
    CONSTRAINT valid_role CHECK (role IN ('owner', 'admin', 'member', 'viewer'))
);

-- Indexes
CREATE INDEX idx_users_org ON users(org_id) WHERE is_active = TRUE;
CREATE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_org_email ON users(org_id, email);

-- ============================================================================
-- ORGANIZATION CREDENTIALS TABLE
-- Stores encrypted credentials for various services
-- ============================================================================
CREATE TABLE IF NOT EXISTS organization_credentials (
    credential_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL, -- NULL for org-level credentials
    
    -- Service identification
    service_name VARCHAR(50) NOT NULL, -- google, salesforce, telesign
    credential_type VARCHAR(50) NOT NULL, -- oauth, api_key, access_token
    
    -- Encrypted credential data
    encrypted_data BYTEA NOT NULL, -- Encrypted JSON containing all credential fields
    encryption_version VARCHAR(10) DEFAULT 'v1',
    
    -- Metadata
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    validated_at TIMESTAMP, -- Last time credentials were validated
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, expired, revoked
    
    -- Constraints
    CONSTRAINT valid_service CHECK (service_name IN ('google', 'salesforce', 'telesign', 'slack', 'zoom', 'custom')),
    CONSTRAINT valid_credential_type CHECK (credential_type IN ('oauth', 'api_key', 'access_token', 'refresh_token')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'expired', 'revoked')),
    
    -- Unique constraint: one credential per org+user+service+type
    -- For org-level credentials (user_id is NULL), unique per org+service+type
    UNIQUE NULLS NOT DISTINCT (org_id, user_id, service_name, credential_type)
);

-- Indexes for fast lookups
CREATE INDEX idx_creds_org ON organization_credentials(org_id) WHERE status = 'active';
CREATE INDEX idx_creds_user ON organization_credentials(user_id) WHERE status = 'active';
CREATE INDEX idx_creds_service ON organization_credentials(service_name, status);
CREATE INDEX idx_creds_org_service ON organization_credentials(org_id, service_name) WHERE status = 'active';

-- ============================================================================
-- CREDENTIAL AUDIT LOG
-- Track all credential access and modifications
-- ============================================================================
CREATE TABLE IF NOT EXISTS credential_audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    credential_id UUID REFERENCES organization_credentials(credential_id) ON DELETE SET NULL,
    
    -- Action details
    action VARCHAR(50) NOT NULL, -- created, accessed, updated, deleted, refreshed, validated
    performed_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Result
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_action CHECK (action IN ('created', 'accessed', 'updated', 'deleted', 'refreshed', 'validated', 'revoked'))
);

-- Indexes for audit queries
CREATE INDEX idx_audit_org_date ON credential_audit_log(org_id, created_at DESC);
CREATE INDEX idx_audit_cred ON credential_audit_log(credential_id, created_at DESC);
CREATE INDEX idx_audit_user ON credential_audit_log(performed_by, created_at DESC);

-- ============================================================================
-- USAGE TRACKING TABLE
-- Track API usage for billing and quota enforcement
-- ============================================================================
CREATE TABLE IF NOT EXISTS usage_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Usage details
    action_type VARCHAR(50) NOT NULL, -- api_call, email_sent, sms_sent, storage_gb
    service VARCHAR(50) NOT NULL, -- gmail, salesforce, openai, telesign
    resource_units INTEGER DEFAULT 1, -- Number of units consumed
    
    -- Metadata
    metadata JSONB DEFAULT '{}', -- Additional context (endpoint, duration, etc.)
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_action_type CHECK (action_type IN (
        'api_call', 'email_sent', 'sms_sent', 'storage_gb', 
        'ai_tokens', 'webhook_call', 'automation_run'
    ))
);

-- Indexes for usage queries and billing
CREATE INDEX idx_usage_org_date ON usage_logs(org_id, created_at DESC);
CREATE INDEX idx_usage_org_service_date ON usage_logs(org_id, service, created_at DESC);
CREATE INDEX idx_usage_service_date ON usage_logs(service, created_at DESC);

-- Partition by month for efficient queries (optional, for high volume)
-- CREATE TABLE usage_logs_2026_02 PARTITION OF usage_logs
--     FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- ============================================================================
-- API KEYS TABLE
-- Organization-level API keys for accessing SECURIVA APIs
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_keys (
    key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE, -- User who created the key
    
    -- Key data
    key_hash VARCHAR(64) NOT NULL UNIQUE, -- SHA-256 hash of the key
    key_prefix VARCHAR(20), -- First 12 chars for display (sk_live_abc...)
    key_name VARCHAR(100), -- User-friendly name ("Production API", "Dev Key")
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP,
    expires_at TIMESTAMP, -- NULL = never expires
    
    -- Permissions
    scopes TEXT[] DEFAULT ARRAY['read', 'write'], -- Permissions for this key
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Rate limiting (optional)
    rate_limit_per_minute INTEGER DEFAULT 60
);

-- Indexes
CREATE INDEX idx_api_keys_org ON api_keys(org_id) WHERE is_active = TRUE;
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash) WHERE is_active = TRUE;
CREATE INDEX idx_api_keys_user ON api_keys(user_id);

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS) POLICIES
-- Ensure organizations can only access their own data
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE credential_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own organization's data
CREATE POLICY org_isolation_users ON users
    USING (org_id = current_setting('app.current_org_id', true)::uuid);

CREATE POLICY org_isolation_credentials ON organization_credentials
    USING (org_id = current_setting('app.current_org_id', true)::uuid);

CREATE POLICY org_isolation_audit ON credential_audit_log
    USING (org_id = current_setting('app.current_org_id', true)::uuid);

CREATE POLICY org_isolation_usage ON usage_logs
    USING (org_id = current_setting('app.current_org_id', true)::uuid);

CREATE POLICY org_isolation_api_keys ON api_keys
    USING (org_id = current_setting('app.current_org_id', true)::uuid);

-- Organizations can see their own record
CREATE POLICY org_self_access ON organizations
    USING (org_id = current_setting('app.current_org_id', true)::uuid);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to set current org context for RLS
CREATE OR REPLACE FUNCTION set_org_context(p_org_id UUID)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_org_id', p_org_id::text, false);
END;
$$ LANGUAGE plpgsql;

-- Function to get credential count for an organization
CREATE OR REPLACE FUNCTION get_org_credential_count(p_org_id UUID)
RETURNS TABLE(service_name VARCHAR, count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        oc.service_name,
        COUNT(*) as count
    FROM organization_credentials oc
    WHERE oc.org_id = p_org_id
      AND oc.status = 'active'
    GROUP BY oc.service_name;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA (for development/testing)
-- ============================================================================

-- Create a sample organization
INSERT INTO organizations (org_id, org_name, org_slug, plan_tier, max_users)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'Demo Company', 'demo', 'pro', 25)
ON CONFLICT (org_id) DO NOTHING;

-- Create a sample user
INSERT INTO users (user_id, org_id, email, role)
VALUES 
    ('22222222-2222-2222-2222-222222222222', 
     '11111111-1111-1111-1111-111111111111', 
     'admin@demo.com', 
     'owner')
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================================
-- GRANTS (adjust based on your application user)
-- ============================================================================
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO securiva_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO securiva_app;
