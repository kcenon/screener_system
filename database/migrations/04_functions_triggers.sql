-- ============================================================================
-- Migration: 04_functions_triggers.sql
-- Description: Create utility functions, triggers, and business logic
-- Author: Database Team
-- Created: 2025-11-09
-- ============================================================================

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column IS 'Automatically update updated_at timestamp on row modification';

-- ============================================================================
-- TRIGGERS FOR AUTO-UPDATING TIMESTAMPS
-- ============================================================================

-- Stocks
CREATE TRIGGER update_stocks_updated_at
    BEFORE UPDATE ON stocks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Portfolios
CREATE TRIGGER update_portfolios_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Portfolio Holdings
CREATE TRIGGER update_holdings_updated_at
    BEFORE UPDATE ON portfolio_holdings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Alerts
CREATE TRIGGER update_alerts_updated_at
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Screening Templates
CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON screening_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Saved Screens
CREATE TRIGGER update_saved_screens_updated_at
    BEFORE UPDATE ON saved_screens
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Watchlists
CREATE TRIGGER update_watchlists_updated_at
    BEFORE UPDATE ON watchlists
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- User Sessions
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PORTFOLIO VALUATION FUNCTIONS
-- ============================================================================

-- Calculate current portfolio value
CREATE OR REPLACE FUNCTION calculate_portfolio_value(p_portfolio_id INTEGER)
RETURNS TABLE (
    total_value NUMERIC,
    total_cost NUMERIC,
    total_gain NUMERIC,
    gain_percentage NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        SUM(ph.quantity * COALESCE(lp.close_price, 0))::NUMERIC AS total_value,
        SUM(ph.quantity * ph.avg_price)::NUMERIC AS total_cost,
        (SUM(ph.quantity * COALESCE(lp.close_price, 0)) - SUM(ph.quantity * ph.avg_price))::NUMERIC AS total_gain,
        CASE
            WHEN SUM(ph.quantity * ph.avg_price) > 0 THEN
                ROUND(((SUM(ph.quantity * COALESCE(lp.close_price, 0)) - SUM(ph.quantity * ph.avg_price)) / SUM(ph.quantity * ph.avg_price) * 100)::NUMERIC, 2)
            ELSE 0
        END AS gain_percentage
    FROM portfolio_holdings ph
    LEFT JOIN LATERAL (
        SELECT close_price
        FROM daily_prices
        WHERE stock_code = ph.stock_code
        ORDER BY trade_date DESC
        LIMIT 1
    ) lp ON TRUE
    WHERE ph.portfolio_id = p_portfolio_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_portfolio_value IS 'Calculate total value, cost, and gain for a portfolio';

-- Example usage:
-- SELECT * FROM calculate_portfolio_value(1);

-- ============================================================================
-- STOCK SCREENING HELPER FUNCTIONS
-- ============================================================================

-- Get latest indicators for a stock
CREATE OR REPLACE FUNCTION get_latest_indicators(p_stock_code VARCHAR(6))
RETURNS TABLE (
    stock_code VARCHAR(6),
    calculation_date DATE,
    per NUMERIC,
    pbr NUMERIC,
    roe NUMERIC,
    revenue_growth_yoy NUMERIC,
    quality_score INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ci.stock_code,
        ci.calculation_date,
        ci.per,
        ci.pbr,
        ci.roe,
        ci.revenue_growth_yoy,
        ci.quality_score
    FROM calculated_indicators ci
    WHERE ci.stock_code = p_stock_code
    ORDER BY ci.calculation_date DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_latest_indicators IS 'Retrieve most recent calculated indicators for a stock';

-- ============================================================================
-- ALERT CHECKING FUNCTIONS
-- ============================================================================

-- Check if alert should be triggered
CREATE OR REPLACE FUNCTION check_price_alerts()
RETURNS TABLE (
    alert_id INTEGER,
    user_id INTEGER,
    stock_code VARCHAR(6),
    current_price NUMERIC,
    threshold_value NUMERIC,
    condition VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.user_id,
        a.stock_code,
        lp.close_price::NUMERIC,
        a.threshold_value,
        a.condition
    FROM alerts a
    CROSS JOIN LATERAL (
        SELECT close_price
        FROM daily_prices
        WHERE stock_code = a.stock_code
        ORDER BY trade_date DESC
        LIMIT 1
    ) lp
    WHERE a.is_active = TRUE
      AND a.alert_type = 'price'
      AND (
          (a.condition = 'above' AND lp.close_price > a.threshold_value) OR
          (a.condition = 'below' AND lp.close_price < a.threshold_value) OR
          (a.condition = 'equals' AND lp.close_price = a.threshold_value)
      )
      AND (a.triggered_at IS NULL OR a.triggered_at < NOW() - INTERVAL '1 hour'); -- Rate limit: 1 hour
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_price_alerts IS 'Find all price alerts that should be triggered';

-- Example usage:
-- SELECT * FROM check_price_alerts();

-- ============================================================================
-- MARKET STATISTICS FUNCTIONS
-- ============================================================================

-- Calculate market overview (KOSPI/KOSDAQ indices)
CREATE OR REPLACE FUNCTION get_market_overview(p_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    market VARCHAR(10),
    total_stocks INTEGER,
    avg_price_change NUMERIC,
    total_volume BIGINT,
    advancers INTEGER,
    decliners INTEGER,
    unchanged INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH latest_prices AS (
        SELECT
            s.market,
            dp.stock_code,
            dp.close_price,
            LAG(dp.close_price) OVER (PARTITION BY dp.stock_code ORDER BY dp.trade_date) AS prev_close,
            dp.volume
        FROM daily_prices dp
        JOIN stocks s ON dp.stock_code = s.code
        WHERE dp.trade_date <= p_date
          AND s.delisting_date IS NULL
    ),
    price_changes AS (
        SELECT
            market,
            stock_code,
            CASE
                WHEN prev_close > 0 THEN ROUND(((close_price - prev_close) / prev_close * 100)::NUMERIC, 2)
                ELSE 0
            END AS price_change,
            volume
        FROM latest_prices
        WHERE prev_close IS NOT NULL
    )
    SELECT
        pc.market,
        COUNT(DISTINCT pc.stock_code)::INTEGER AS total_stocks,
        ROUND(AVG(pc.price_change), 2) AS avg_price_change,
        SUM(pc.volume)::BIGINT AS total_volume,
        COUNT(CASE WHEN pc.price_change > 0 THEN 1 END)::INTEGER AS advancers,
        COUNT(CASE WHEN pc.price_change < 0 THEN 1 END)::INTEGER AS decliners,
        COUNT(CASE WHEN pc.price_change = 0 THEN 1 END)::INTEGER AS unchanged
    FROM price_changes pc
    GROUP BY pc.market;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_market_overview IS 'Calculate market statistics for a given date';

-- Example usage:
-- SELECT * FROM get_market_overview(CURRENT_DATE);

-- ============================================================================
-- HOT STOCKS DETECTION
-- ============================================================================

-- Find stocks with volume surge
CREATE OR REPLACE FUNCTION get_hot_stocks(
    p_min_surge_pct NUMERIC DEFAULT 150,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    stock_code VARCHAR(6),
    stock_name VARCHAR(100),
    current_volume BIGINT,
    avg_volume BIGINT,
    volume_surge_pct NUMERIC,
    price_change_pct NUMERIC,
    current_price INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH volume_stats AS (
        SELECT
            dp.stock_code,
            dp.volume AS current_volume,
            AVG(dp.volume) OVER (
                PARTITION BY dp.stock_code
                ORDER BY dp.trade_date
                ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING
            ) AS avg_volume_20d,
            dp.close_price AS current_price,
            LAG(dp.close_price, 1) OVER (PARTITION BY dp.stock_code ORDER BY dp.trade_date) AS prev_close,
            ROW_NUMBER() OVER (PARTITION BY dp.stock_code ORDER BY dp.trade_date DESC) AS rn
        FROM daily_prices dp
    )
    SELECT
        vs.stock_code,
        s.name,
        vs.current_volume,
        vs.avg_volume_20d::BIGINT,
        ROUND(((vs.current_volume::NUMERIC / vs.avg_volume_20d - 1) * 100), 2) AS volume_surge_pct,
        ROUND(((vs.current_price - vs.prev_close)::NUMERIC / vs.prev_close * 100), 2) AS price_change_pct,
        vs.current_price
    FROM volume_stats vs
    JOIN stocks s ON vs.stock_code = s.code
    WHERE vs.rn = 1
      AND vs.avg_volume_20d > 0
      AND (vs.current_volume::NUMERIC / vs.avg_volume_20d * 100) >= p_min_surge_pct
      AND s.delisting_date IS NULL
    ORDER BY volume_surge_pct DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_hot_stocks IS 'Detect stocks with significant volume surge (default: 150%+)';

-- Example usage:
-- SELECT * FROM get_hot_stocks(150, 20);

-- ============================================================================
-- STOCK PERFORMANCE RANKINGS
-- ============================================================================

-- Get top performers by price change
CREATE OR REPLACE FUNCTION get_top_movers(
    p_mover_type VARCHAR(10) DEFAULT 'gainers', -- 'gainers' or 'losers'
    p_period VARCHAR(10) DEFAULT '1d', -- '1d', '1w', '1m', '3m', '6m', '1y'
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    rank INTEGER,
    stock_code VARCHAR(6),
    stock_name VARCHAR(100),
    market VARCHAR(10),
    price_change_pct NUMERIC,
    current_price INTEGER,
    volume BIGINT
) AS $$
DECLARE
    period_interval INTERVAL;
BEGIN
    -- Map period to interval
    period_interval := CASE p_period
        WHEN '1d' THEN INTERVAL '1 day'
        WHEN '1w' THEN INTERVAL '1 week'
        WHEN '1m' THEN INTERVAL '1 month'
        WHEN '3m' THEN INTERVAL '3 months'
        WHEN '6m' THEN INTERVAL '6 months'
        WHEN '1y' THEN INTERVAL '1 year'
        ELSE INTERVAL '1 day'
    END;

    RETURN QUERY
    WITH price_changes AS (
        SELECT
            dp.stock_code,
            s.name,
            s.market,
            dp.close_price AS current_price,
            dp.volume,
            first_value(dp.close_price) OVER (
                PARTITION BY dp.stock_code
                ORDER BY dp.trade_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) AS period_start_price,
            ROW_NUMBER() OVER (PARTITION BY dp.stock_code ORDER BY dp.trade_date DESC) AS rn
        FROM daily_prices dp
        JOIN stocks s ON dp.stock_code = s.code
        WHERE dp.trade_date >= CURRENT_DATE - period_interval
          AND s.delisting_date IS NULL
    ),
    ranked_changes AS (
        SELECT
            ROW_NUMBER() OVER (ORDER BY
                ((pc.current_price - pc.period_start_price)::NUMERIC / pc.period_start_price) *
                CASE WHEN p_mover_type = 'gainers' THEN -1 ELSE 1 END
            )::INTEGER AS rank,
            pc.stock_code,
            pc.name,
            pc.market,
            ROUND(((pc.current_price - pc.period_start_price)::NUMERIC / pc.period_start_price * 100), 2) AS price_change_pct,
            pc.current_price,
            pc.volume
        FROM price_changes pc
        WHERE pc.rn = 1 AND pc.period_start_price > 0
    )
    SELECT * FROM ranked_changes
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_top_movers IS 'Get top gainers or losers for a specified period';

-- Example usage:
-- SELECT * FROM get_top_movers('gainers', '1d', 20);
-- SELECT * FROM get_top_movers('losers', '1w', 20);

-- ============================================================================
-- DATA QUALITY FUNCTIONS
-- ============================================================================

-- Check for missing data
CREATE OR REPLACE FUNCTION check_data_completeness(p_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    check_name VARCHAR(100),
    status VARCHAR(20),
    details TEXT
) AS $$
DECLARE
    expected_stocks INTEGER;
    actual_prices INTEGER;
    missing_stocks INTEGER;
BEGIN
    -- Count active stocks
    SELECT COUNT(*) INTO expected_stocks
    FROM stocks
    WHERE delisting_date IS NULL;

    -- Count stocks with prices on given date
    SELECT COUNT(DISTINCT stock_code) INTO actual_prices
    FROM daily_prices
    WHERE trade_date = p_date;

    missing_stocks := expected_stocks - actual_prices;

    RETURN QUERY
    SELECT
        'Daily Prices'::VARCHAR(100),
        CASE
            WHEN missing_stocks = 0 THEN 'OK'::VARCHAR(20)
            WHEN missing_stocks < expected_stocks * 0.05 THEN 'WARNING'::VARCHAR(20)
            ELSE 'ERROR'::VARCHAR(20)
        END,
        FORMAT('%s/%s stocks have prices (%s missing)',
               actual_prices, expected_stocks, missing_stocks)::TEXT;

    -- Add more checks as needed
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_data_completeness IS 'Verify data quality and completeness for a given date';

-- Example usage:
-- SELECT * FROM check_data_completeness(CURRENT_DATE);

-- ============================================================================
-- SESSION CLEANUP FUNCTION
-- ============================================================================

-- Clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_sessions
    WHERE expires_at < NOW() AND revoked = FALSE;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_sessions IS 'Remove expired user sessions (should be run by cron job)';

-- Example usage:
-- SELECT cleanup_expired_sessions();

-- ============================================================================
-- USER ACTIVITY LOGGING HELPER
-- ============================================================================

-- Log user action
CREATE OR REPLACE FUNCTION log_user_activity(
    p_user_id INTEGER,
    p_action_type VARCHAR(50),
    p_resource_type VARCHAR(50) DEFAULT NULL,
    p_resource_id VARCHAR(100) DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    log_id BIGINT;
BEGIN
    INSERT INTO user_activity_log (
        user_id, action_type, resource_type, resource_id,
        metadata, ip_address, user_agent
    ) VALUES (
        p_user_id, p_action_type, p_resource_type, p_resource_id,
        p_metadata, p_ip_address, p_user_agent
    )
    RETURNING id INTO log_id;

    RETURN log_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION log_user_activity IS 'Convenience function to log user actions';

-- Example usage:
-- SELECT log_user_activity(
--     1, 'screen', 'screening_template', '5',
--     '{"filters": {"per": {"max": 15}}}'::jsonb,
--     '192.168.1.1'::inet,
--     'Mozilla/5.0...'
-- );

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- List all functions
SELECT
    n.nspname AS schema,
    p.proname AS function_name,
    pg_get_function_arguments(p.oid) AS arguments,
    d.description
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
LEFT JOIN pg_description d ON p.oid = d.objoid
WHERE n.nspname = 'public'
  AND p.prokind = 'f'
ORDER BY p.proname;

-- List all triggers
SELECT
    trigger_name,
    event_object_table AS table_name,
    action_timing,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS CREATED SUCCESSFULLY
-- ============================================================================

\echo 'All functions and triggers created successfully!'
\echo ''
\echo 'Utility functions:'
\echo '  - update_updated_at_column() - Auto-update timestamps'
\echo '  - calculate_portfolio_value() - Portfolio valuation'
\echo '  - get_latest_indicators() - Latest stock indicators'
\echo '  - check_price_alerts() - Alert detection'
\echo '  - get_market_overview() - Market statistics'
\echo '  - get_hot_stocks() - Volume surge detection'
\echo '  - get_top_movers() - Top gainers/losers'
\echo '  - check_data_completeness() - Data quality checks'
\echo '  - cleanup_expired_sessions() - Session maintenance'
\echo '  - log_user_activity() - Activity logging helper'
\echo ''
\echo 'Next steps:'
\echo '  1. Run 05_views.sql to create materialized views'
\echo '  2. Test functions with sample data'
\echo '  3. Schedule cleanup_expired_sessions() as a cron job'
