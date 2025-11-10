-- ============================================================================
-- Migration: 07_order_book.sql
-- Description: Create order book (호가) schema with TimescaleDB for high-frequency data
-- Author: Database Team
-- Created: 2025-11-11
-- Ticket: DB-005
-- ============================================================================

-- ============================================================================
-- ORDER BOOK TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS order_book (
    stock_code VARCHAR(6) NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- Ask levels (매도호가) - 10 levels from lowest (best) to highest
    ask_price_1 INTEGER,
    ask_price_2 INTEGER,
    ask_price_3 INTEGER,
    ask_price_4 INTEGER,
    ask_price_5 INTEGER,
    ask_price_6 INTEGER,
    ask_price_7 INTEGER,
    ask_price_8 INTEGER,
    ask_price_9 INTEGER,
    ask_price_10 INTEGER,

    ask_volume_1 BIGINT,
    ask_volume_2 BIGINT,
    ask_volume_3 BIGINT,
    ask_volume_4 BIGINT,
    ask_volume_5 BIGINT,
    ask_volume_6 BIGINT,
    ask_volume_7 BIGINT,
    ask_volume_8 BIGINT,
    ask_volume_9 BIGINT,
    ask_volume_10 BIGINT,

    -- Bid levels (매수호가) - 10 levels from highest (best) to lowest
    bid_price_1 INTEGER,
    bid_price_2 INTEGER,
    bid_price_3 INTEGER,
    bid_price_4 INTEGER,
    bid_price_5 INTEGER,
    bid_price_6 INTEGER,
    bid_price_7 INTEGER,
    bid_price_8 INTEGER,
    bid_price_9 INTEGER,
    bid_price_10 INTEGER,

    bid_volume_1 BIGINT,
    bid_volume_2 BIGINT,
    bid_volume_3 BIGINT,
    bid_volume_4 BIGINT,
    bid_volume_5 BIGINT,
    bid_volume_6 BIGINT,
    bid_volume_7 BIGINT,
    bid_volume_8 BIGINT,
    bid_volume_9 BIGINT,
    bid_volume_10 BIGINT,

    -- Aggregated metrics
    total_ask_volume BIGINT,
    total_bid_volume BIGINT,
    spread INTEGER,
    mid_price NUMERIC(10, 2),
    order_imbalance NUMERIC(5, 2), -- (bid_volume - ask_volume) / (bid_volume + ask_volume) * 100

    PRIMARY KEY (stock_code, timestamp),
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE,

    -- Constraints
    CONSTRAINT valid_ask_prices CHECK (
        ask_price_1 > 0 AND
        (ask_price_2 IS NULL OR ask_price_2 >= ask_price_1) AND
        (ask_price_3 IS NULL OR ask_price_3 >= ask_price_2) AND
        (ask_price_4 IS NULL OR ask_price_4 >= ask_price_3) AND
        (ask_price_5 IS NULL OR ask_price_5 >= ask_price_4) AND
        (ask_price_6 IS NULL OR ask_price_6 >= ask_price_5) AND
        (ask_price_7 IS NULL OR ask_price_7 >= ask_price_6) AND
        (ask_price_8 IS NULL OR ask_price_8 >= ask_price_7) AND
        (ask_price_9 IS NULL OR ask_price_9 >= ask_price_8) AND
        (ask_price_10 IS NULL OR ask_price_10 >= ask_price_9)
    ),
    CONSTRAINT valid_bid_prices CHECK (
        bid_price_1 > 0 AND
        (bid_price_2 IS NULL OR bid_price_2 <= bid_price_1) AND
        (bid_price_3 IS NULL OR bid_price_3 <= bid_price_2) AND
        (bid_price_4 IS NULL OR bid_price_4 <= bid_price_3) AND
        (bid_price_5 IS NULL OR bid_price_5 <= bid_price_4) AND
        (bid_price_6 IS NULL OR bid_price_6 <= bid_price_5) AND
        (bid_price_7 IS NULL OR bid_price_7 <= bid_price_6) AND
        (bid_price_8 IS NULL OR bid_price_8 <= bid_price_7) AND
        (bid_price_9 IS NULL OR bid_price_9 <= bid_price_8) AND
        (bid_price_10 IS NULL OR bid_price_10 <= bid_price_9)
    ),
    CONSTRAINT valid_volumes CHECK (
        (ask_volume_1 IS NULL OR ask_volume_1 >= 0) AND
        (ask_volume_2 IS NULL OR ask_volume_2 >= 0) AND
        (ask_volume_3 IS NULL OR ask_volume_3 >= 0) AND
        (ask_volume_4 IS NULL OR ask_volume_4 >= 0) AND
        (ask_volume_5 IS NULL OR ask_volume_5 >= 0) AND
        (ask_volume_6 IS NULL OR ask_volume_6 >= 0) AND
        (ask_volume_7 IS NULL OR ask_volume_7 >= 0) AND
        (ask_volume_8 IS NULL OR ask_volume_8 >= 0) AND
        (ask_volume_9 IS NULL OR ask_volume_9 >= 0) AND
        (ask_volume_10 IS NULL OR ask_volume_10 >= 0) AND
        (bid_volume_1 IS NULL OR bid_volume_1 >= 0) AND
        (bid_volume_2 IS NULL OR bid_volume_2 >= 0) AND
        (bid_volume_3 IS NULL OR bid_volume_3 >= 0) AND
        (bid_volume_4 IS NULL OR bid_volume_4 >= 0) AND
        (bid_volume_5 IS NULL OR bid_volume_5 >= 0) AND
        (bid_volume_6 IS NULL OR bid_volume_6 >= 0) AND
        (bid_volume_7 IS NULL OR bid_volume_7 >= 0) AND
        (bid_volume_8 IS NULL OR bid_volume_8 >= 0) AND
        (bid_volume_9 IS NULL OR bid_volume_9 >= 0) AND
        (bid_volume_10 IS NULL OR bid_volume_10 >= 0)
    ),
    CONSTRAINT valid_spread CHECK (spread >= 0),
    CONSTRAINT valid_ask_bid_relationship CHECK (ask_price_1 >= bid_price_1)
);

COMMENT ON TABLE order_book IS 'Order book (호가) data with 10-level bid/ask prices';
COMMENT ON COLUMN order_book.stock_code IS '6-digit stock code';
COMMENT ON COLUMN order_book.timestamp IS 'Timestamp of order book snapshot (millisecond precision)';
COMMENT ON COLUMN order_book.ask_price_1 IS 'Best ask price (lowest sell price)';
COMMENT ON COLUMN order_book.bid_price_1 IS 'Best bid price (highest buy price)';
COMMENT ON COLUMN order_book.spread IS 'Spread = ask_price_1 - bid_price_1';
COMMENT ON COLUMN order_book.mid_price IS 'Mid price = (ask_price_1 + bid_price_1) / 2';
COMMENT ON COLUMN order_book.order_imbalance IS 'Order imbalance ratio (positive = more buying pressure)';

-- ============================================================================
-- TIMESCALEDB HYPERTABLE CONVERSION
-- ============================================================================

-- Convert to hypertable with 1-day chunks (high-frequency data)
SELECT create_hypertable(
    'order_book',
    'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

COMMENT ON TABLE order_book IS 'TimescaleDB hypertable for order book data (partitioned by timestamp)';

-- ============================================================================
-- COMPRESSION POLICY
-- ============================================================================

-- Enable compression for order book data older than 7 days
ALTER TABLE order_book SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'stock_code',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- Automatically compress chunks older than 7 days
SELECT add_compression_policy(
    'order_book',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

COMMENT ON TABLE order_book IS 'TimescaleDB hypertable with automatic compression for data > 7 days old';

-- ============================================================================
-- RETENTION POLICY
-- ============================================================================

-- Automatically drop order book data older than 90 days
SELECT add_retention_policy(
    'order_book',
    INTERVAL '90 days',
    if_not_exists => TRUE
);

COMMENT ON TABLE order_book IS 'Order book data retained for 90 days, compressed after 7 days';

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Primary composite index on (stock_code, timestamp DESC) already created by PRIMARY KEY

-- Index for recent order book queries (last 7 days)
CREATE INDEX IF NOT EXISTS idx_order_book_recent
ON order_book (stock_code, timestamp DESC)
WHERE timestamp >= NOW() - INTERVAL '7 days';

COMMENT ON INDEX idx_order_book_recent IS 'Partial index for recent order book data (last 7 days)';

-- Index for spread analysis
CREATE INDEX IF NOT EXISTS idx_order_book_spread
ON order_book (stock_code, spread)
WHERE spread IS NOT NULL;

COMMENT ON INDEX idx_order_book_spread IS 'Index for spread analysis queries';

-- ============================================================================
-- MATERIALIZED VIEWS
-- ============================================================================

-- Latest order book for each stock
CREATE MATERIALIZED VIEW IF NOT EXISTS order_book_latest AS
SELECT DISTINCT ON (stock_code)
    stock_code,
    timestamp,
    ask_price_1,
    ask_volume_1,
    bid_price_1,
    bid_volume_1,
    spread,
    mid_price,
    order_imbalance,
    total_ask_volume,
    total_bid_volume
FROM order_book
ORDER BY stock_code, timestamp DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_order_book_latest_stock_code
ON order_book_latest (stock_code);

COMMENT ON MATERIALIZED VIEW order_book_latest IS 'Latest order book snapshot for each stock';

-- Spread history (hourly aggregates)
CREATE MATERIALIZED VIEW IF NOT EXISTS order_book_spread_history
WITH (timescaledb.continuous) AS
SELECT
    stock_code,
    time_bucket('1 hour', timestamp) AS hour,
    avg(spread) AS avg_spread,
    min(spread) AS min_spread,
    max(spread) AS max_spread,
    avg(mid_price) AS avg_mid_price,
    avg(order_imbalance) AS avg_order_imbalance,
    count(*) AS snapshot_count
FROM order_book
GROUP BY stock_code, hour
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW order_book_spread_history IS 'Hourly spread and order imbalance aggregates';

-- Refresh policy for spread history (refresh every hour)
SELECT add_continuous_aggregate_policy(
    'order_book_spread_history',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- Volume summary (hourly aggregates)
CREATE MATERIALIZED VIEW IF NOT EXISTS order_book_volume_summary
WITH (timescaledb.continuous) AS
SELECT
    stock_code,
    time_bucket('1 hour', timestamp) AS hour,
    avg(total_ask_volume) AS avg_total_ask_volume,
    avg(total_bid_volume) AS avg_total_bid_volume,
    avg(total_ask_volume + total_bid_volume) AS avg_total_volume,
    max(total_ask_volume + total_bid_volume) AS max_total_volume,
    count(*) AS snapshot_count
FROM order_book
GROUP BY stock_code, hour
WITH NO DATA;

COMMENT ON MATERIALIZED VIEW order_book_volume_summary IS 'Hourly volume aggregates for order book';

-- Refresh policy for volume summary (refresh every hour)
SELECT add_continuous_aggregate_policy(
    'order_book_volume_summary',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- ============================================================================
-- DATABASE FUNCTIONS
-- ============================================================================

-- Function: Get latest order book for a stock
CREATE OR REPLACE FUNCTION get_latest_order_book(p_stock_code VARCHAR(6))
RETURNS TABLE (
    stock_code VARCHAR(6),
    timestamp TIMESTAMP,
    ask_price_1 INTEGER,
    ask_volume_1 BIGINT,
    ask_price_2 INTEGER,
    ask_volume_2 BIGINT,
    ask_price_3 INTEGER,
    ask_volume_3 BIGINT,
    ask_price_4 INTEGER,
    ask_volume_4 BIGINT,
    ask_price_5 INTEGER,
    ask_volume_5 BIGINT,
    bid_price_1 INTEGER,
    bid_volume_1 BIGINT,
    bid_price_2 INTEGER,
    bid_volume_2 BIGINT,
    bid_price_3 INTEGER,
    bid_volume_3 BIGINT,
    bid_price_4 INTEGER,
    bid_volume_4 BIGINT,
    bid_price_5 INTEGER,
    bid_volume_5 BIGINT,
    spread INTEGER,
    mid_price NUMERIC(10, 2),
    order_imbalance NUMERIC(5, 2)
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        ob.stock_code,
        ob.timestamp,
        ob.ask_price_1, ob.ask_volume_1,
        ob.ask_price_2, ob.ask_volume_2,
        ob.ask_price_3, ob.ask_volume_3,
        ob.ask_price_4, ob.ask_volume_4,
        ob.ask_price_5, ob.ask_volume_5,
        ob.bid_price_1, ob.bid_volume_1,
        ob.bid_price_2, ob.bid_volume_2,
        ob.bid_price_3, ob.bid_volume_3,
        ob.bid_price_4, ob.bid_volume_4,
        ob.bid_price_5, ob.bid_volume_5,
        ob.spread,
        ob.mid_price,
        ob.order_imbalance
    FROM order_book ob
    WHERE ob.stock_code = p_stock_code
    ORDER BY ob.timestamp DESC
    LIMIT 1;
$$;

COMMENT ON FUNCTION get_latest_order_book IS 'Get the most recent order book snapshot for a stock';

-- Function: Calculate order imbalance
CREATE OR REPLACE FUNCTION calculate_order_imbalance(p_stock_code VARCHAR(6))
RETURNS NUMERIC(5, 2)
LANGUAGE SQL
STABLE
AS $$
    SELECT order_imbalance
    FROM order_book
    WHERE stock_code = p_stock_code
    ORDER BY timestamp DESC
    LIMIT 1;
$$;

COMMENT ON FUNCTION calculate_order_imbalance IS 'Get current order imbalance for a stock';

-- Function: Get spread history
CREATE OR REPLACE FUNCTION get_spread_history(
    p_stock_code VARCHAR(6),
    p_from_time TIMESTAMP,
    p_to_time TIMESTAMP
)
RETURNS TABLE (
    timestamp TIMESTAMP,
    spread INTEGER,
    mid_price NUMERIC(10, 2),
    order_imbalance NUMERIC(5, 2)
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        ob.timestamp,
        ob.spread,
        ob.mid_price,
        ob.order_imbalance
    FROM order_book ob
    WHERE ob.stock_code = p_stock_code
      AND ob.timestamp >= p_from_time
      AND ob.timestamp <= p_to_time
    ORDER BY ob.timestamp ASC;
$$;

COMMENT ON FUNCTION get_spread_history IS 'Get order book spread history for a time range';

-- ============================================================================
-- TRIGGER: Auto-calculate aggregated metrics
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_order_book_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate total ask volume
    NEW.total_ask_volume := COALESCE(NEW.ask_volume_1, 0) +
                            COALESCE(NEW.ask_volume_2, 0) +
                            COALESCE(NEW.ask_volume_3, 0) +
                            COALESCE(NEW.ask_volume_4, 0) +
                            COALESCE(NEW.ask_volume_5, 0) +
                            COALESCE(NEW.ask_volume_6, 0) +
                            COALESCE(NEW.ask_volume_7, 0) +
                            COALESCE(NEW.ask_volume_8, 0) +
                            COALESCE(NEW.ask_volume_9, 0) +
                            COALESCE(NEW.ask_volume_10, 0);

    -- Calculate total bid volume
    NEW.total_bid_volume := COALESCE(NEW.bid_volume_1, 0) +
                            COALESCE(NEW.bid_volume_2, 0) +
                            COALESCE(NEW.bid_volume_3, 0) +
                            COALESCE(NEW.bid_volume_4, 0) +
                            COALESCE(NEW.bid_volume_5, 0) +
                            COALESCE(NEW.bid_volume_6, 0) +
                            COALESCE(NEW.bid_volume_7, 0) +
                            COALESCE(NEW.bid_volume_8, 0) +
                            COALESCE(NEW.bid_volume_9, 0) +
                            COALESCE(NEW.bid_volume_10, 0);

    -- Calculate spread
    IF NEW.ask_price_1 IS NOT NULL AND NEW.bid_price_1 IS NOT NULL THEN
        NEW.spread := NEW.ask_price_1 - NEW.bid_price_1;
        NEW.mid_price := (NEW.ask_price_1 + NEW.bid_price_1) / 2.0;
    END IF;

    -- Calculate order imbalance
    IF NEW.total_bid_volume + NEW.total_ask_volume > 0 THEN
        NEW.order_imbalance := ROUND(
            ((NEW.total_bid_volume - NEW.total_ask_volume)::NUMERIC /
             (NEW.total_bid_volume + NEW.total_ask_volume)::NUMERIC * 100)::NUMERIC,
            2
        );
    ELSE
        NEW.order_imbalance := 0;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_order_book_metrics
    BEFORE INSERT OR UPDATE ON order_book
    FOR EACH ROW
    EXECUTE FUNCTION calculate_order_book_metrics();

COMMENT ON FUNCTION calculate_order_book_metrics IS 'Auto-calculate order book aggregated metrics on insert/update';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- View hypertable information
SELECT * FROM timescaledb_information.hypertables
WHERE hypertable_name = 'order_book';

-- View compression settings
SELECT * FROM timescaledb_information.compression_settings
WHERE hypertable_name = 'order_book';

-- View retention policy
SELECT * FROM timescaledb_information.data_retention
WHERE hypertable_name = 'order_book';

-- ============================================================================
-- SAMPLE DATA FOR TESTING (Optional - Uncomment to insert test data)
-- ============================================================================

-- INSERT INTO order_book (stock_code, timestamp,
--     ask_price_1, ask_volume_1, ask_price_2, ask_volume_2,
--     bid_price_1, bid_volume_1, bid_price_2, bid_volume_2)
-- VALUES
--     ('005930', NOW(), 70000, 1000, 70100, 2000, 69900, 1500, 69800, 3000),
--     ('000660', NOW(), 150000, 500, 150500, 1000, 149500, 800, 149000, 1200);

-- -- Test queries
-- SELECT * FROM get_latest_order_book('005930');
-- SELECT calculate_order_imbalance('005930');
-- SELECT * FROM get_spread_history('005930', NOW() - INTERVAL '1 hour', NOW());

-- ============================================================================
-- ORDER BOOK SCHEMA SETUP COMPLETE
-- ============================================================================

\echo 'Order book schema setup completed successfully!'
\echo 'Hypertable created: order_book (1-day chunks)'
\echo 'Compression enabled: Data older than 7 days will be compressed'
\echo 'Retention policy: Data older than 90 days will be dropped'
\echo 'Materialized views: order_book_latest, order_book_spread_history, order_book_volume_summary'
\echo 'Functions: get_latest_order_book(), calculate_order_imbalance(), get_spread_history()'
\echo ''
\echo 'Next steps:'
\echo '  1. Integrate with KIS API for real-time order book data (DP-004)'
\echo '  2. Implement WebSocket streaming (BE-006)'
\echo '  3. Create order book visualization component (FE-005)'
\echo '  4. Monitor compression with: SELECT * FROM timescaledb_information.chunks;'
