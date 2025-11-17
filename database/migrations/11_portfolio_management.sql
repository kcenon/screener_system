-- ============================================================================
-- Migration: 11_portfolio_management.sql
-- Description: Create portfolio management tables (portfolios, holdings, transactions)
-- Author: Portfolio Team
-- Created: 2025-11-17
-- Ticket: FEATURE-002
-- ============================================================================

-- ============================================================================
-- PORTFOLIOS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

    CONSTRAINT uq_user_portfolio_name UNIQUE (user_id, name),
    CONSTRAINT valid_portfolio_name CHECK (LENGTH(TRIM(name)) >= 1)
);

COMMENT ON TABLE portfolios IS 'User portfolios for tracking stock holdings and performance';
COMMENT ON COLUMN portfolios.user_id IS 'Owner of the portfolio';
COMMENT ON COLUMN portfolios.name IS 'Portfolio name (unique per user)';
COMMENT ON COLUMN portfolios.description IS 'Optional description of portfolio strategy';
COMMENT ON COLUMN portfolios.is_default IS 'Whether this is the user''s default portfolio';

-- ============================================================================
-- HOLDINGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    shares DECIMAL(18, 8) NOT NULL,
    average_cost DECIMAL(18, 2) NOT NULL,
    first_purchase_date DATE,
    last_update_date TIMESTAMP DEFAULT NOW(),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol) ON DELETE RESTRICT,

    CONSTRAINT uq_portfolio_stock UNIQUE (portfolio_id, stock_symbol),
    CONSTRAINT valid_shares CHECK (shares >= 0),
    CONSTRAINT valid_average_cost CHECK (average_cost >= 0)
);

COMMENT ON TABLE holdings IS 'Stock holdings within portfolios with cost basis tracking';
COMMENT ON COLUMN holdings.portfolio_id IS 'Portfolio containing this holding';
COMMENT ON COLUMN holdings.stock_symbol IS 'Stock symbol (e.g., 005930 for Samsung)';
COMMENT ON COLUMN holdings.shares IS 'Number of shares owned (supports fractional shares)';
COMMENT ON COLUMN holdings.average_cost IS 'Weighted average cost per share';
COMMENT ON COLUMN holdings.first_purchase_date IS 'Date of first purchase (for performance tracking)';
COMMENT ON COLUMN holdings.last_update_date IS 'Last transaction affecting this holding';

-- ============================================================================
-- TRANSACTIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,
    shares DECIMAL(18, 8) NOT NULL,
    price DECIMAL(18, 2) NOT NULL,
    commission DECIMAL(18, 2) DEFAULT 0,
    transaction_date TIMESTAMP DEFAULT NOW(),
    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol) ON DELETE RESTRICT,

    CONSTRAINT valid_transaction_type CHECK (transaction_type IN ('BUY', 'SELL')),
    CONSTRAINT valid_shares CHECK (shares > 0),
    CONSTRAINT valid_price CHECK (price >= 0),
    CONSTRAINT valid_commission CHECK (commission >= 0)
);

COMMENT ON TABLE transactions IS 'Transaction history for portfolio buy/sell activities';
COMMENT ON COLUMN transactions.portfolio_id IS 'Portfolio where transaction occurred';
COMMENT ON COLUMN transactions.stock_symbol IS 'Stock symbol involved in transaction';
COMMENT ON COLUMN transactions.transaction_type IS 'Type: BUY or SELL';
COMMENT ON COLUMN transactions.shares IS 'Number of shares transacted';
COMMENT ON COLUMN transactions.price IS 'Price per share at time of transaction';
COMMENT ON COLUMN transactions.commission IS 'Trading commission/fees';
COMMENT ON COLUMN transactions.transaction_date IS 'When transaction occurred';
COMMENT ON COLUMN transactions.notes IS 'Optional user notes about transaction';

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Portfolios indexes
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_portfolios_created_at ON portfolios(created_at DESC);
CREATE INDEX idx_portfolios_updated_at ON portfolios(updated_at DESC);
CREATE INDEX idx_portfolios_is_default ON portfolios(user_id, is_default) WHERE is_default = TRUE;

-- Holdings indexes
CREATE INDEX idx_holdings_portfolio_id ON holdings(portfolio_id);
CREATE INDEX idx_holdings_stock_symbol ON holdings(stock_symbol);
CREATE INDEX idx_holdings_portfolio_stock ON holdings(portfolio_id, stock_symbol);
CREATE INDEX idx_holdings_updated_at ON holdings(updated_at DESC);

-- Transactions indexes
CREATE INDEX idx_transactions_portfolio_id ON transactions(portfolio_id);
CREATE INDEX idx_transactions_stock_symbol ON transactions(stock_symbol);
CREATE INDEX idx_transactions_date ON transactions(transaction_date DESC);
CREATE INDEX idx_transactions_portfolio_date ON transactions(portfolio_id, transaction_date DESC);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update portfolios.updated_at on holding changes
CREATE OR REPLACE FUNCTION update_portfolio_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE portfolios
    SET updated_at = NOW()
    WHERE id = COALESCE(NEW.portfolio_id, OLD.portfolio_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_portfolio_on_holding_change
AFTER INSERT OR UPDATE OR DELETE ON holdings
FOR EACH ROW
EXECUTE FUNCTION update_portfolio_timestamp();

CREATE TRIGGER trigger_update_portfolio_on_transaction
AFTER INSERT ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_portfolio_timestamp();

-- Auto-update holdings.updated_at
CREATE TRIGGER trigger_update_holdings_timestamp
BEFORE UPDATE ON holdings
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Auto-update portfolios.updated_at
CREATE TRIGGER trigger_update_portfolios_timestamp
BEFORE UPDATE ON portfolios
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Note: update_updated_at_column() function should exist from 04_functions_triggers.sql

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Get portfolio holding count
CREATE OR REPLACE FUNCTION get_portfolio_holding_count(p_portfolio_id INTEGER)
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER
    FROM holdings
    WHERE portfolio_id = p_portfolio_id AND shares > 0;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_portfolio_holding_count IS 'Count active holdings in a portfolio';

-- Get user portfolio count
CREATE OR REPLACE FUNCTION get_user_portfolio_count(p_user_id INTEGER)
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER
    FROM portfolios
    WHERE user_id = p_user_id;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_user_portfolio_count IS 'Count portfolios owned by user';

-- Get portfolio total cost
CREATE OR REPLACE FUNCTION get_portfolio_total_cost(p_portfolio_id INTEGER)
RETURNS DECIMAL AS $$
    SELECT COALESCE(SUM(shares * average_cost), 0)::DECIMAL(18, 2)
    FROM holdings
    WHERE portfolio_id = p_portfolio_id AND shares > 0;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_portfolio_total_cost IS 'Calculate total cost basis of portfolio';

-- Get holding current value (requires current price from daily_prices)
CREATE OR REPLACE FUNCTION get_holding_current_value(
    p_stock_symbol VARCHAR,
    p_shares DECIMAL
)
RETURNS DECIMAL AS $$
    SELECT (p_shares * COALESCE(close, 0))::DECIMAL(18, 2)
    FROM daily_prices
    WHERE symbol = p_stock_symbol
    ORDER BY date DESC
    LIMIT 1;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION get_holding_current_value IS 'Calculate current value of holding based on latest price';

-- Calculate realized gain/loss from transactions
CREATE OR REPLACE FUNCTION calculate_realized_gain(
    p_portfolio_id INTEGER,
    p_stock_symbol VARCHAR DEFAULT NULL
)
RETURNS DECIMAL AS $$
    WITH buys AS (
        SELECT SUM(shares * price + commission) AS total_cost
        FROM transactions
        WHERE portfolio_id = p_portfolio_id
          AND transaction_type = 'BUY'
          AND (p_stock_symbol IS NULL OR stock_symbol = p_stock_symbol)
    ),
    sells AS (
        SELECT SUM(shares * price - commission) AS total_proceeds
        FROM transactions
        WHERE portfolio_id = p_portfolio_id
          AND transaction_type = 'SELL'
          AND (p_stock_symbol IS NULL OR stock_symbol = p_stock_symbol)
    )
    SELECT (COALESCE(sells.total_proceeds, 0) - COALESCE(buys.total_cost, 0))::DECIMAL(18, 2)
    FROM buys FULL OUTER JOIN sells ON TRUE;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION calculate_realized_gain IS 'Calculate realized gain/loss from completed transactions';

-- Check if user can create portfolio (subscription tier limits)
CREATE OR REPLACE FUNCTION can_create_portfolio(p_user_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    v_tier VARCHAR;
    v_count INTEGER;
    v_limit INTEGER;
BEGIN
    -- Get user tier
    SELECT subscription_tier INTO v_tier
    FROM users
    WHERE id = p_user_id;

    -- Get current portfolio count
    v_count := get_user_portfolio_count(p_user_id);

    -- Determine limit based on tier
    v_limit := CASE v_tier
        WHEN 'free' THEN 0      -- No portfolios for free tier
        WHEN 'premium' THEN 3   -- 3 portfolios for premium
        WHEN 'pro' THEN 999     -- Unlimited for pro
        ELSE 0
    END;

    RETURN v_count < v_limit;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION can_create_portfolio IS 'Check if user can create portfolio based on subscription tier limits';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Portfolio summary view
CREATE OR REPLACE VIEW v_portfolio_summary AS
SELECT
    p.id,
    p.user_id,
    p.name,
    p.description,
    p.is_default,
    COUNT(h.id) AS holding_count,
    COALESCE(SUM(h.shares * h.average_cost), 0) AS total_cost,
    MAX(t.transaction_date) AS last_transaction_date,
    p.created_at,
    p.updated_at
FROM portfolios p
LEFT JOIN holdings h ON p.id = h.portfolio_id AND h.shares > 0
LEFT JOIN transactions t ON p.id = t.portfolio_id
GROUP BY p.id, p.user_id, p.name, p.description, p.is_default, p.created_at, p.updated_at;

COMMENT ON VIEW v_portfolio_summary IS 'Portfolio summary with holding counts and total cost';

-- Holding detail view with current performance
CREATE OR REPLACE VIEW v_holding_details AS
SELECT
    h.id,
    h.portfolio_id,
    h.stock_symbol,
    h.shares,
    h.average_cost,
    h.shares * h.average_cost AS total_cost,
    dp.close AS current_price,
    h.shares * dp.close AS current_value,
    (h.shares * dp.close) - (h.shares * h.average_cost) AS unrealized_gain,
    CASE
        WHEN h.average_cost > 0
        THEN ((dp.close - h.average_cost) / h.average_cost * 100)
        ELSE 0
    END AS return_percent,
    h.first_purchase_date,
    h.last_update_date,
    s.name AS stock_name,
    s.sector,
    s.market_cap
FROM holdings h
LEFT JOIN stocks s ON h.stock_symbol = s.symbol
LEFT JOIN LATERAL (
    SELECT close
    FROM daily_prices
    WHERE symbol = h.stock_symbol
    ORDER BY date DESC
    LIMIT 1
) dp ON TRUE
WHERE h.shares > 0;

COMMENT ON VIEW v_holding_details IS 'Detailed holding information with current prices and performance';

-- Transaction history view
CREATE OR REPLACE VIEW v_transaction_history AS
SELECT
    t.id,
    t.portfolio_id,
    p.name AS portfolio_name,
    t.stock_symbol,
    s.name AS stock_name,
    t.transaction_type,
    t.shares,
    t.price,
    t.shares * t.price AS transaction_value,
    t.commission,
    (t.shares * t.price) + CASE WHEN t.transaction_type = 'BUY' THEN t.commission ELSE -t.commission END AS total_amount,
    t.transaction_date,
    t.notes,
    t.created_at
FROM transactions t
LEFT JOIN portfolios p ON t.portfolio_id = p.id
LEFT JOIN stocks s ON t.stock_symbol = s.symbol
ORDER BY t.transaction_date DESC;

COMMENT ON VIEW v_transaction_history IS 'Transaction history with calculated totals';

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
WHERE tablename IN ('portfolios', 'holdings', 'transactions')
ORDER BY tablename;

-- Check indexes
SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE tablename IN ('portfolios', 'holdings', 'transactions')
ORDER BY tablename, indexname;

-- Check functions
SELECT
    proname AS function_name,
    pg_get_function_result(oid) AS return_type
FROM pg_proc
WHERE proname LIKE '%portfolio%' OR proname LIKE '%holding%'
ORDER BY proname;

-- Check views
SELECT
    viewname,
    schemaname
FROM pg_views
WHERE viewname LIKE 'v_%portfolio%' OR viewname LIKE 'v_%holding%' OR viewname LIKE 'v_%transaction%'
ORDER BY viewname;

-- Check triggers
SELECT
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers
WHERE event_object_table IN ('portfolios', 'holdings', 'transactions')
ORDER BY event_object_table, trigger_name;
*/

-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================
-- Run these commands to rollback this migration

/*
DROP VIEW IF EXISTS v_transaction_history CASCADE;
DROP VIEW IF EXISTS v_holding_details CASCADE;
DROP VIEW IF EXISTS v_portfolio_summary CASCADE;

DROP FUNCTION IF EXISTS can_create_portfolio(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS calculate_realized_gain(INTEGER, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_holding_current_value(VARCHAR, DECIMAL) CASCADE;
DROP FUNCTION IF EXISTS get_portfolio_total_cost(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS get_user_portfolio_count(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS get_portfolio_holding_count(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS update_portfolio_timestamp() CASCADE;

DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS holdings CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
*/
