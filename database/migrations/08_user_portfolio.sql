-- ============================================================================
-- Migration: 08_user_portfolio.sql
-- Description: Create user portfolio tables (watchlists, activity tracking)
-- Author: Database Team
-- Created: 2025-11-14
-- Ticket: BE-007
-- ============================================================================

-- ============================================================================
-- WATCHLISTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    CONSTRAINT uq_user_watchlist_name UNIQUE (user_id, name),
    CONSTRAINT valid_watchlist_name CHECK (LENGTH(TRIM(name)) >= 1)
);

COMMENT ON TABLE watchlists IS 'User watchlists for organizing favorite stocks';
COMMENT ON COLUMN watchlists.user_id IS 'Owner of the watchlist';
COMMENT ON COLUMN watchlists.name IS 'Watchlist name (unique per user)';
COMMENT ON COLUMN watchlists.description IS 'Optional description of watchlist purpose';

-- ============================================================================
-- WATCHLIST STOCKS (Junction Table)
-- ============================================================================

CREATE TABLE IF NOT EXISTS watchlist_stocks (
    watchlist_id UUID NOT NULL,
    stock_code VARCHAR(6) NOT NULL,
    added_at TIMESTAMP DEFAULT NOW(),

    notes TEXT,

    PRIMARY KEY (watchlist_id, stock_code),
    FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE
);

COMMENT ON TABLE watchlist_stocks IS 'Junction table linking watchlists to stocks';
COMMENT ON COLUMN watchlist_stocks.added_at IS 'When stock was added to watchlist';
COMMENT ON COLUMN watchlist_stocks.notes IS 'Optional user notes about this stock';

-- ============================================================================
-- USER ACTIVITIES (Activity Log)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    activity_metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    CONSTRAINT valid_activity_type CHECK (
        activity_type IN (
            'screening',
            'watchlist_create',
            'watchlist_update',
            'watchlist_delete',
            'stock_add',
            'stock_remove',
            'stock_view',
            'login',
            'logout'
        )
    )
);

COMMENT ON TABLE user_activities IS 'Audit log of user activities for recent history';
COMMENT ON COLUMN user_activities.activity_type IS 'Type of activity performed';
COMMENT ON COLUMN user_activities.description IS 'Human-readable description of activity';
COMMENT ON COLUMN user_activities.activity_metadata IS 'Additional structured data (screening filters, etc.)';

-- ============================================================================
-- USER PREFERENCES (Dashboard Settings)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY,
    default_watchlist_id UUID,
    screening_quota_used INTEGER DEFAULT 0,
    screening_quota_reset_at TIMESTAMP DEFAULT NOW() + INTERVAL '1 month',

    dashboard_layout JSONB,
    notification_settings JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (default_watchlist_id) REFERENCES watchlists(id) ON DELETE SET NULL,

    CONSTRAINT valid_quota CHECK (screening_quota_used >= 0)
);

COMMENT ON TABLE user_preferences IS 'User-specific preferences and settings';
COMMENT ON COLUMN user_preferences.default_watchlist_id IS 'Watchlist to show by default on dashboard';
COMMENT ON COLUMN user_preferences.screening_quota_used IS 'Number of screening queries used this period';
COMMENT ON COLUMN user_preferences.dashboard_layout IS 'Custom dashboard widget layout (JSON)';

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Watchlists indexes
CREATE INDEX idx_watchlists_user_id ON watchlists(user_id);
CREATE INDEX idx_watchlists_created_at ON watchlists(created_at DESC);
CREATE INDEX idx_watchlists_updated_at ON watchlists(updated_at DESC);

-- Watchlist stocks indexes
CREATE INDEX idx_watchlist_stocks_watchlist_id ON watchlist_stocks(watchlist_id);
CREATE INDEX idx_watchlist_stocks_stock_code ON watchlist_stocks(stock_code);
CREATE INDEX idx_watchlist_stocks_added_at ON watchlist_stocks(added_at DESC);

-- User activities indexes
CREATE INDEX idx_user_activities_user_id ON user_activities(user_id);
CREATE INDEX idx_user_activities_type ON user_activities(activity_type);
CREATE INDEX idx_user_activities_created_at ON user_activities(created_at DESC);
CREATE INDEX idx_user_activities_user_created ON user_activities(user_id, created_at DESC);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update watchlists.updated_at on stock changes
CREATE OR REPLACE FUNCTION update_watchlist_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE watchlists
    SET updated_at = NOW()
    WHERE id = COALESCE(NEW.watchlist_id, OLD.watchlist_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_watchlist_timestamp
AFTER INSERT OR DELETE ON watchlist_stocks
FOR EACH ROW
EXECUTE FUNCTION update_watchlist_timestamp();

-- Auto-update user_preferences.updated_at
CREATE TRIGGER trigger_update_user_preferences_timestamp
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
-- Note: update_updated_at_column() function should exist from 04_functions_triggers.sql

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Get watchlist stock count
CREATE OR REPLACE FUNCTION get_watchlist_stock_count(p_watchlist_id UUID)
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER
    FROM watchlist_stocks
    WHERE watchlist_id = p_watchlist_id;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_watchlist_stock_count IS 'Count stocks in a watchlist';

-- Get user watchlist count
CREATE OR REPLACE FUNCTION get_user_watchlist_count(p_user_id UUID)
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER
    FROM watchlists
    WHERE user_id = p_user_id;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_user_watchlist_count IS 'Count watchlists owned by user';

-- Check if user can create watchlist (limit: 10)
CREATE OR REPLACE FUNCTION can_create_watchlist(p_user_id UUID)
RETURNS BOOLEAN AS $$
    SELECT get_user_watchlist_count(p_user_id) < 10;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION can_create_watchlist IS 'Check if user has not reached watchlist limit (max 10)';

-- Get user activity count
CREATE OR REPLACE FUNCTION get_user_activity_count(
    p_user_id UUID,
    p_activity_type VARCHAR DEFAULT NULL
)
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER
    FROM user_activities
    WHERE user_id = p_user_id
        AND (p_activity_type IS NULL OR activity_type = p_activity_type);
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_user_activity_count IS 'Count user activities, optionally filtered by type';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Watchlist summary view
CREATE OR REPLACE VIEW v_watchlist_summary AS
SELECT
    w.id,
    w.user_id,
    w.name,
    w.description,
    COUNT(ws.stock_code) AS stock_count,
    MAX(ws.added_at) AS last_stock_added,
    w.created_at,
    w.updated_at
FROM watchlists w
LEFT JOIN watchlist_stocks ws ON w.id = ws.watchlist_id
GROUP BY w.id, w.user_id, w.name, w.description, w.created_at, w.updated_at;

COMMENT ON VIEW v_watchlist_summary IS 'Watchlist summary with stock counts and last update';

-- User dashboard summary view
CREATE OR REPLACE VIEW v_user_dashboard_summary AS
SELECT
    u.id AS user_id,
    u.email,
    u.tier,
    COUNT(DISTINCT w.id) AS watchlist_count,
    COUNT(DISTINCT ws.stock_code) AS total_stocks_watched,
    COUNT(DISTINCT CASE WHEN ua.activity_type = 'screening' THEN ua.id END) AS screening_count,
    MAX(ua.created_at) AS last_activity_at,
    COALESCE(up.screening_quota_used, 0) AS screening_quota_used,
    COALESCE(
        CASE u.tier
            WHEN 'free' THEN 100
            WHEN 'premium' THEN 500
            WHEN 'enterprise' THEN 2000
            ELSE 10
        END,
        10
    ) AS screening_quota_limit
FROM users u
LEFT JOIN watchlists w ON u.id = w.user_id
LEFT JOIN watchlist_stocks ws ON w.id = ws.watchlist_id
LEFT JOIN user_activities ua ON u.id = ua.user_id
    AND ua.created_at >= NOW() - INTERVAL '30 days'
LEFT JOIN user_preferences up ON u.id = up.user_id
GROUP BY u.id, u.email, u.tier, up.screening_quota_used;

COMMENT ON VIEW v_user_dashboard_summary IS 'User dashboard summary with activity metrics';

-- ============================================================================
-- SAMPLE DATA (Development Only)
-- ============================================================================
-- Uncomment for local development testing

/*
-- Create sample watchlist for first user
DO $$
DECLARE
    v_user_id UUID;
    v_watchlist_id UUID;
BEGIN
    -- Get first user
    SELECT id INTO v_user_id FROM users LIMIT 1;

    IF v_user_id IS NOT NULL THEN
        -- Create watchlist
        INSERT INTO watchlists (user_id, name, description)
        VALUES (v_user_id, 'Tech Stocks', 'High-growth technology companies')
        RETURNING id INTO v_watchlist_id;

        -- Add sample stocks
        INSERT INTO watchlist_stocks (watchlist_id, stock_code)
        SELECT v_watchlist_id, code
        FROM stocks
        WHERE sector = 'Technology'
        LIMIT 5;

        -- Create preferences
        INSERT INTO user_preferences (user_id, default_watchlist_id)
        VALUES (v_user_id, v_watchlist_id)
        ON CONFLICT (user_id) DO NOTHING;
    END IF;
END $$;
*/

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify migration success

/*
-- Check table creation
SELECT
    tablename,
    schemaname
FROM pg_tables
WHERE tablename IN ('watchlists', 'watchlist_stocks', 'user_activities', 'user_preferences')
ORDER BY tablename;

-- Check indexes
SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE tablename IN ('watchlists', 'watchlist_stocks', 'user_activities')
ORDER BY tablename, indexname;

-- Check functions
SELECT
    proname AS function_name,
    pg_get_function_result(oid) AS return_type
FROM pg_proc
WHERE proname LIKE '%watchlist%' OR proname LIKE '%activity%'
ORDER BY proname;

-- Check views
SELECT
    viewname,
    schemaname
FROM pg_views
WHERE viewname LIKE 'v_%dashboard%' OR viewname LIKE 'v_%watchlist%'
ORDER BY viewname;
*/

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================
-- Run these commands to rollback this migration

/*
DROP VIEW IF EXISTS v_user_dashboard_summary CASCADE;
DROP VIEW IF EXISTS v_watchlist_summary CASCADE;

DROP FUNCTION IF EXISTS get_user_activity_count(UUID, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS can_create_watchlist(UUID) CASCADE;
DROP FUNCTION IF EXISTS get_user_watchlist_count(UUID) CASCADE;
DROP FUNCTION IF EXISTS get_watchlist_stock_count(UUID) CASCADE;
DROP FUNCTION IF EXISTS update_watchlist_timestamp() CASCADE;

DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS user_activities CASCADE;
DROP TABLE IF EXISTS watchlist_stocks CASCADE;
DROP TABLE IF EXISTS watchlists CASCADE;
*/
