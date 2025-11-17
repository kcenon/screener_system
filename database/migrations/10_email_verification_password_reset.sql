-- Migration: 10_email_verification_password_reset.sql
-- Description: Add email verification and password reset functionality
-- Created: 2025-11-17
-- Ticket: FEATURE-004

-- Add email_verified_at column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ;

-- Create email_verification_tokens table
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMPTZ,
    CONSTRAINT valid_expiration CHECK (expires_at > created_at)
);

-- Create password_reset_tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMPTZ,
    CONSTRAINT valid_reset_expiration CHECK (expires_at > created_at)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token
    ON email_verification_tokens(token) WHERE used_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id
    ON email_verification_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_expires_at
    ON email_verification_tokens(expires_at) WHERE used_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token
    ON password_reset_tokens(token) WHERE used_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id
    ON password_reset_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at
    ON password_reset_tokens(expires_at) WHERE used_at IS NULL;

-- Add comments for documentation
COMMENT ON TABLE email_verification_tokens IS 'Stores email verification tokens for user registration';
COMMENT ON COLUMN email_verification_tokens.token IS 'Unique verification token (hashed)';
COMMENT ON COLUMN email_verification_tokens.expires_at IS 'Token expiration time (24 hours from creation)';
COMMENT ON COLUMN email_verification_tokens.used_at IS 'Timestamp when token was used';

COMMENT ON TABLE password_reset_tokens IS 'Stores password reset tokens for account recovery';
COMMENT ON COLUMN password_reset_tokens.token IS 'Unique reset token (hashed)';
COMMENT ON COLUMN password_reset_tokens.expires_at IS 'Token expiration time (1 hour from creation)';
COMMENT ON COLUMN password_reset_tokens.used_at IS 'Timestamp when token was used';

-- Create function to clean up expired tokens (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete expired email verification tokens
    DELETE FROM email_verification_tokens
    WHERE expires_at < CURRENT_TIMESTAMP
    AND used_at IS NULL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Delete expired password reset tokens
    DELETE FROM password_reset_tokens
    WHERE expires_at < CURRENT_TIMESTAMP
    AND used_at IS NULL;

    GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_tokens() IS 'Removes expired verification and reset tokens';

-- Create trigger to update user email_verified_at
CREATE OR REPLACE FUNCTION update_user_email_verified()
RETURNS TRIGGER AS $$
BEGIN
    -- When a verification token is used, update the user's email_verified_at
    IF NEW.used_at IS NOT NULL AND OLD.used_at IS NULL THEN
        UPDATE users
        SET email_verified = TRUE,
            email_verified_at = NEW.used_at,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_email_verified
AFTER UPDATE OF used_at ON email_verification_tokens
FOR EACH ROW
EXECUTE FUNCTION update_user_email_verified();

COMMENT ON TRIGGER trigger_update_email_verified ON email_verification_tokens IS
'Automatically updates user email_verified status when token is used';
