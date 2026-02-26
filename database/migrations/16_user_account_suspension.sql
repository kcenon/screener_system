-- ============================================================================
-- Migration: 16_user_account_suspension.sql
-- Description: Add account suspension and admin flag columns to users table
-- Author: OPS-013
-- Created: 2026-02-26
-- ============================================================================

-- ============================================================================
-- ADD SUSPENSION COLUMNS
-- ============================================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS is_suspended BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS suspended_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS suspension_reason TEXT;

COMMENT ON COLUMN users.is_suspended IS 'Whether the user account is suspended';
COMMENT ON COLUMN users.suspended_at IS 'Timestamp when the account was suspended';
COMMENT ON COLUMN users.suspension_reason IS 'Reason for account suspension';

-- ============================================================================
-- ADD ADMIN FLAG
-- ============================================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;

COMMENT ON COLUMN users.is_admin IS 'Whether the user has admin privileges';

-- ============================================================================
-- INDEX FOR SUSPENDED USERS LOOKUP
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_users_is_suspended ON users(is_suspended) WHERE is_suspended = TRUE;
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin) WHERE is_admin = TRUE;
