-- ============================================================================
-- Migration: 13_oauth_social_login.sql
-- Description: Add OAuth social login support (Google, Kakao, Naver)
-- Author: FEATURE-005
-- Created: 2025-11-26
-- ============================================================================

-- ============================================================================
-- MODIFY USERS TABLE
-- Allow null password_hash for OAuth-only users
-- ============================================================================

ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

COMMENT ON COLUMN users.password_hash IS 'Hashed password (NULL for OAuth-only users)';

-- ============================================================================
-- SOCIAL ACCOUNTS TABLE
-- Store linked social provider accounts for users
-- ============================================================================

CREATE TABLE IF NOT EXISTS social_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Provider information
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('GOOGLE', 'KAKAO', 'NAVER')),
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    provider_name VARCHAR(255),
    provider_picture VARCHAR(512),

    -- OAuth tokens (encrypted in application layer)
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure unique provider account per provider
    CONSTRAINT unique_provider_user UNIQUE (provider, provider_user_id),
    -- Ensure user can only link one account per provider
    CONSTRAINT unique_user_provider UNIQUE (user_id, provider)
);

COMMENT ON TABLE social_accounts IS 'OAuth social accounts linked to user accounts';
COMMENT ON COLUMN social_accounts.provider IS 'OAuth provider: GOOGLE, KAKAO, or NAVER';
COMMENT ON COLUMN social_accounts.provider_user_id IS 'Unique user ID from the OAuth provider';
COMMENT ON COLUMN social_accounts.provider_email IS 'Email from OAuth provider (may differ from user email)';
COMMENT ON COLUMN social_accounts.access_token IS 'OAuth access token (encrypted)';
COMMENT ON COLUMN social_accounts.refresh_token IS 'OAuth refresh token for token renewal (encrypted)';

-- Indexes for social_accounts
CREATE INDEX idx_social_accounts_user_id ON social_accounts(user_id);
CREATE INDEX idx_social_accounts_provider_user ON social_accounts(provider, provider_user_id);
CREATE INDEX idx_social_accounts_provider_email ON social_accounts(provider_email);

-- ============================================================================
-- OAUTH STATES TABLE
-- Store temporary state tokens for CSRF protection during OAuth flow
-- ============================================================================

CREATE TABLE IF NOT EXISTS oauth_states (
    id SERIAL PRIMARY KEY,

    -- State token (random string for CSRF protection)
    state VARCHAR(255) NOT NULL UNIQUE,

    -- OAuth flow information
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('GOOGLE', 'KAKAO', 'NAVER')),
    redirect_url VARCHAR(512),

    -- Optional: link to existing user (for account linking flow)
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,

    -- Expiration (short-lived, typically 10 minutes)
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Additional metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

COMMENT ON TABLE oauth_states IS 'Temporary state tokens for OAuth CSRF protection';
COMMENT ON COLUMN oauth_states.state IS 'Random state token sent to OAuth provider and validated on callback';
COMMENT ON COLUMN oauth_states.redirect_url IS 'URL to redirect after successful OAuth';
COMMENT ON COLUMN oauth_states.user_id IS 'User ID for account linking flow (NULL for login/signup)';
COMMENT ON COLUMN oauth_states.expires_at IS 'State expiration time (typically 10 minutes)';
COMMENT ON COLUMN oauth_states.metadata IS 'Additional flow metadata as JSON';

-- Indexes for oauth_states
CREATE INDEX idx_oauth_states_state ON oauth_states(state);
CREATE INDEX idx_oauth_states_expires_at ON oauth_states(expires_at);

-- ============================================================================
-- CLEANUP FUNCTION FOR EXPIRED STATES
-- Automatically remove expired OAuth states
-- ============================================================================

CREATE OR REPLACE FUNCTION cleanup_expired_oauth_states()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM oauth_states
    WHERE expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_oauth_states() IS 'Remove expired OAuth state tokens';

-- ============================================================================
-- TRIGGER FOR UPDATED_AT ON SOCIAL_ACCOUNTS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_social_accounts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_social_accounts_updated_at
    BEFORE UPDATE ON social_accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_social_accounts_updated_at();

-- ============================================================================
-- MIGRATION VERIFICATION
-- ============================================================================

-- Verify tables created
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'social_accounts') THEN
        RAISE EXCEPTION 'social_accounts table was not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'oauth_states') THEN
        RAISE EXCEPTION 'oauth_states table was not created';
    END IF;

    RAISE NOTICE 'OAuth migration completed successfully';
END $$;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
