-- ============================================================================
-- Migration: 03_indexes.sql
-- Description: Create indexes for query performance optimization
-- Author: Database Team
-- Created: 2025-11-09
-- ============================================================================

-- ============================================================================
-- STOCKS TABLE INDEXES
-- ============================================================================

-- Market classification (frequently filtered)
CREATE INDEX IF NOT EXISTS idx_stocks_market ON stocks(market);

-- Sector and industry (for grouping and filtering)
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector);
CREATE INDEX IF NOT EXISTS idx_stocks_industry ON stocks(industry);

-- Trigram index for fuzzy stock name search
CREATE INDEX IF NOT EXISTS idx_stocks_name_trgm ON stocks USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_stocks_name_english_trgm ON stocks USING gin (name_english gin_trgm_ops);

-- Listing status (active vs delisted)
CREATE INDEX IF NOT EXISTS idx_stocks_delisting ON stocks(delisting_date)
WHERE delisting_date IS NULL; -- Partial index for active stocks only

COMMENT ON INDEX idx_stocks_market IS 'Fast filtering by KOSPI/KOSDAQ';
COMMENT ON INDEX idx_stocks_name_trgm IS 'Fuzzy text search for stock names (supports LIKE queries)';

-- ============================================================================
-- DAILY_PRICES INDEXES (TimescaleDB hypertable)
-- ============================================================================

-- Note: TimescaleDB automatically creates indexes on partitioning key (trade_date)
-- Additional indexes for common query patterns:

-- Stock code (for single-stock queries) - TimescaleDB optimizes this automatically
-- CREATE INDEX IF NOT EXISTS idx_daily_prices_stock_date ON daily_prices(stock_code, trade_date DESC);
-- ^ Not needed - composite primary key already serves this

-- Volume-based queries (e.g., finding high volume days)
CREATE INDEX IF NOT EXISTS idx_daily_prices_volume ON daily_prices(trade_date, volume DESC)
WHERE volume > 0;

-- Market cap (for filtering by company size)
CREATE INDEX IF NOT EXISTS idx_daily_prices_market_cap ON daily_prices(trade_date, market_cap DESC)
WHERE market_cap IS NOT NULL;

COMMENT ON INDEX idx_daily_prices_volume IS 'Optimizes queries for high-volume stocks';

-- ============================================================================
-- FINANCIAL_STATEMENTS INDEXES
-- ============================================================================

-- Lookup by stock and period (most common query)
CREATE INDEX IF NOT EXISTS idx_financials_stock_period ON financial_statements(
    stock_code,
    period_type,
    fiscal_year DESC,
    fiscal_quarter DESC
);

-- Lookup by report date (for timeline queries)
CREATE INDEX IF NOT EXISTS idx_financials_report_date ON financial_statements(report_date DESC);

-- Filter by fiscal year (e.g., "show all FY2024 reports")
CREATE INDEX IF NOT EXISTS idx_financials_fiscal_year ON financial_statements(fiscal_year DESC);

COMMENT ON INDEX idx_financials_stock_period IS 'Optimizes retrieval of financial history for a stock';

-- ============================================================================
-- CALCULATED_INDICATORS INDEXES
-- ============================================================================

-- Calculation date (most recent indicators)
CREATE INDEX IF NOT EXISTS idx_indicators_date ON calculated_indicators(calculation_date DESC);

-- Composite index for stock + date
CREATE INDEX IF NOT EXISTS idx_indicators_stock_date ON calculated_indicators(stock_code, calculation_date DESC);

-- Valuation metrics (frequently filtered)
CREATE INDEX IF NOT EXISTS idx_indicators_per ON calculated_indicators(per)
WHERE per IS NOT NULL AND per > 0;

CREATE INDEX IF NOT EXISTS idx_indicators_pbr ON calculated_indicators(pbr)
WHERE pbr IS NOT NULL AND pbr > 0;

CREATE INDEX IF NOT EXISTS idx_indicators_psr ON calculated_indicators(psr)
WHERE psr IS NOT NULL AND psr > 0;

CREATE INDEX IF NOT EXISTS idx_indicators_dividend_yield ON calculated_indicators(dividend_yield DESC)
WHERE dividend_yield > 0;

-- Profitability metrics
CREATE INDEX IF NOT EXISTS idx_indicators_roe ON calculated_indicators(roe DESC)
WHERE roe IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_indicators_roa ON calculated_indicators(roa DESC)
WHERE roa IS NOT NULL;

-- Growth metrics
CREATE INDEX IF NOT EXISTS idx_indicators_revenue_growth ON calculated_indicators(revenue_growth_yoy DESC)
WHERE revenue_growth_yoy IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_indicators_profit_growth ON calculated_indicators(profit_growth_yoy DESC)
WHERE profit_growth_yoy IS NOT NULL;

-- Composite scores (for pre-built screens)
CREATE INDEX IF NOT EXISTS idx_indicators_quality_score ON calculated_indicators(quality_score DESC)
WHERE quality_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_indicators_value_score ON calculated_indicators(value_score DESC)
WHERE value_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_indicators_growth_score ON calculated_indicators(growth_score DESC)
WHERE growth_score IS NOT NULL;

-- Price momentum
CREATE INDEX IF NOT EXISTS idx_indicators_price_change_1m ON calculated_indicators(price_change_1m DESC);
CREATE INDEX IF NOT EXISTS idx_indicators_volume_surge ON calculated_indicators(volume_surge_pct DESC)
WHERE volume_surge_pct > 0;

COMMENT ON INDEX idx_indicators_per IS 'Partial index for valid PER values (screening optimization)';
COMMENT ON INDEX idx_indicators_quality_score IS 'Optimizes quality-based stock screening';

-- ============================================================================
-- USER MANAGEMENT INDEXES
-- ============================================================================

-- Email lookup (login)
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- ^ Not needed - UNIQUE constraint already creates an index

-- Subscription tier (for feature access checks)
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_tier);

-- Email verification status
CREATE INDEX IF NOT EXISTS idx_users_verification ON users(email_verified)
WHERE email_verified = FALSE;

-- Password reset tokens
CREATE INDEX IF NOT EXISTS idx_users_reset_token ON users(password_reset_token)
WHERE password_reset_token IS NOT NULL;

COMMENT ON INDEX idx_users_verification IS 'Find unverified users for reminder emails';

-- ============================================================================
-- PORTFOLIO INDEXES
-- ============================================================================

-- User's portfolios
CREATE INDEX IF NOT EXISTS idx_portfolios_user ON portfolios(user_id);

-- Holdings by portfolio
CREATE INDEX IF NOT EXISTS idx_holdings_portfolio ON portfolio_holdings(portfolio_id);

-- Holdings by stock (for "who owns this stock?" queries)
CREATE INDEX IF NOT EXISTS idx_holdings_stock ON portfolio_holdings(stock_code);

-- User + stock lookup (check if user owns a stock)
CREATE INDEX IF NOT EXISTS idx_holdings_user_stock ON portfolio_holdings(portfolio_id, stock_code);

-- ============================================================================
-- ALERTS INDEXES
-- ============================================================================

-- Active alerts by user
CREATE INDEX IF NOT EXISTS idx_alerts_user_active ON alerts(user_id, is_active)
WHERE is_active = TRUE;

-- Active alerts by stock (for checking on price updates)
CREATE INDEX IF NOT EXISTS idx_alerts_stock_active ON alerts(stock_code, is_active)
WHERE is_active = TRUE;

-- Alert type filtering
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type)
WHERE is_active = TRUE;

-- Recently triggered (for rate limiting)
CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered_at DESC)
WHERE triggered_at IS NOT NULL;

COMMENT ON INDEX idx_alerts_stock_active IS 'Optimizes alert checking on price updates';

-- ============================================================================
-- AUDIT LOG INDEXES
-- ============================================================================

-- User activity lookup
CREATE INDEX IF NOT EXISTS idx_activity_user_date ON user_activity_log(user_id, created_at DESC);

-- Action type analytics
CREATE INDEX IF NOT EXISTS idx_activity_action ON user_activity_log(action_type, created_at DESC);

-- Resource tracking
CREATE INDEX IF NOT EXISTS idx_activity_resource ON user_activity_log(resource_type, resource_id);

-- GIN index for JSONB metadata queries
CREATE INDEX IF NOT EXISTS idx_activity_metadata ON user_activity_log USING gin (metadata);

COMMENT ON INDEX idx_activity_metadata IS 'Enables fast queries on JSON metadata (e.g., filter criteria)';

-- ============================================================================
-- DATA INGESTION LOG INDEXES
-- ============================================================================

-- Source and date (for monitoring)
CREATE INDEX IF NOT EXISTS idx_ingestion_source_date ON data_ingestion_log(source, created_at DESC);

-- Status filtering (find failed jobs)
CREATE INDEX IF NOT EXISTS idx_ingestion_status ON data_ingestion_log(status, created_at DESC);

-- ============================================================================
-- SCREENING TEMPLATES INDEXES
-- ============================================================================

-- Public templates lookup
CREATE INDEX IF NOT EXISTS idx_templates_public ON screening_templates(is_public, category)
WHERE is_public = TRUE;

-- User-created templates
CREATE INDEX IF NOT EXISTS idx_templates_creator ON screening_templates(created_by)
WHERE created_by IS NOT NULL;

-- Popular templates (by usage)
CREATE INDEX IF NOT EXISTS idx_templates_usage ON screening_templates(usage_count DESC);

-- GIN index for filter config queries
CREATE INDEX IF NOT EXISTS idx_templates_filters ON screening_templates USING gin (filter_config);

-- ============================================================================
-- SAVED SCREENS INDEXES
-- ============================================================================

-- User's saved screens
CREATE INDEX IF NOT EXISTS idx_saved_screens_user ON saved_screens(user_id, updated_at DESC);

-- GIN index for filter config
CREATE INDEX IF NOT EXISTS idx_saved_screens_filters ON saved_screens USING gin (filter_config);

-- ============================================================================
-- WATCHLISTS INDEXES
-- ============================================================================

-- User's watchlists
CREATE INDEX IF NOT EXISTS idx_watchlists_user ON watchlists(user_id);

-- Watchlist items
CREATE INDEX IF NOT EXISTS idx_watchlist_items_list ON watchlist_items(watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_stock ON watchlist_items(stock_code);

-- ============================================================================
-- USER SESSIONS INDEXES
-- ============================================================================

-- Refresh token lookup
-- CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token ON user_sessions(refresh_token);
-- ^ Not needed - UNIQUE constraint creates index

-- User's active sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_active ON user_sessions(user_id, expires_at)
WHERE revoked = FALSE;

-- Expired sessions cleanup
CREATE INDEX IF NOT EXISTS idx_sessions_expired ON user_sessions(expires_at)
WHERE revoked = FALSE;

COMMENT ON INDEX idx_sessions_expired IS 'Optimizes cleanup job for expired sessions';

-- ============================================================================
-- INDEX USAGE MONITORING
-- ============================================================================

-- View to check index usage (run periodically to identify unused indexes)
CREATE OR REPLACE VIEW index_usage_stats AS
SELECT
    schemaname,
    relname AS tablename,
    indexrelname AS indexname,
    idx_scan AS scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    CASE
        WHEN idx_scan = 0 THEN 'UNUSED - Consider dropping'
        WHEN idx_scan < 100 THEN 'Low usage'
        ELSE 'Active'
    END AS usage_status
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC;

COMMENT ON VIEW index_usage_stats IS 'Monitor index usage to identify unused indexes';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- List all indexes created
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Total index size
SELECT
    pg_size_pretty(SUM(pg_relation_size(indexrelid))) AS total_index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public';

-- ============================================================================
-- INDEXES CREATED SUCCESSFULLY
-- ============================================================================

\echo 'All indexes created successfully!'
\echo ''
\echo 'Performance optimizations applied:'
\echo '  - Stock filtering: market, sector, industry'
\echo '  - Fuzzy search: trigram indexes on stock names'
\echo '  - Indicator screening: partial indexes on key metrics'
\echo '  - User queries: optimized lookups for portfolios, alerts, watchlists'
\echo '  - Audit logs: JSONB GIN indexes for metadata queries'
\echo ''
\echo 'Next steps:'
\echo '  1. Run 04_functions_triggers.sql to add business logic'
\echo '  2. Monitor index usage with: SELECT * FROM index_usage_stats;'
\echo '  3. Analyze query plans with: EXPLAIN ANALYZE <your_query>;'
