-- ============================================================================
-- Migration: 09_market_indices.sql
-- Description: Create market_indices table for KOSPI/KOSDAQ/KRX100 data
-- Author: Backend Team
-- Created: 2025-11-14
-- Purpose: Support market overview API (BE-009) with historical index data
-- ============================================================================

-- ============================================================================
-- MARKET INDICES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS market_indices (
    id SERIAL,
    code VARCHAR(20) NOT NULL,  -- 'KOSPI', 'KOSDAQ', 'KRX100'
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,

    -- OHLC Data
    open_value NUMERIC(10, 2),
    high_value NUMERIC(10, 2),
    low_value NUMERIC(10, 2),
    close_value NUMERIC(10, 2) NOT NULL,

    -- Volume & Value
    volume BIGINT,
    trading_value BIGINT,

    -- Additional Metrics
    change_value NUMERIC(10, 2),
    change_percent NUMERIC(10, 4),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT valid_index_code CHECK (code IN ('KOSPI', 'KOSDAQ', 'KRX100')),
    CONSTRAINT valid_index_values CHECK (
        open_value > 0 AND
        high_value >= low_value AND
        close_value > 0
    ),
    CONSTRAINT valid_index_volume CHECK (volume IS NULL OR volume >= 0),
    CONSTRAINT unique_index_timestamp UNIQUE (code, timestamp)
);

COMMENT ON TABLE market_indices IS 'Historical data for market indices (KOSPI, KOSDAQ, KRX100)';
COMMENT ON COLUMN market_indices.code IS 'Index identifier: KOSPI, KOSDAQ, or KRX100';
COMMENT ON COLUMN market_indices.timestamp IS 'Timestamp of the index value (intraday or end-of-day)';
COMMENT ON COLUMN market_indices.close_value IS 'Closing value of the index';
COMMENT ON COLUMN market_indices.volume IS 'Total trading volume across all constituent stocks';
COMMENT ON COLUMN market_indices.trading_value IS 'Total trading value in KRW';

-- ============================================================================
-- CONVERT TO TIMESCALEDB HYPERTABLE
-- ============================================================================

-- Convert market_indices to TimescaleDB hypertable (time-series optimization)
SELECT create_hypertable(
    'market_indices',
    'timestamp',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

COMMENT ON TABLE market_indices IS
    'TimescaleDB hypertable for market indices. ' ||
    'Chunked by 7-day intervals for efficient time-series queries.';

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Index for fast lookup by code and timestamp (descending for latest-first queries)
CREATE INDEX IF NOT EXISTS idx_market_indices_code_timestamp
    ON market_indices (code, timestamp DESC);

-- Index for timestamp range queries
CREATE INDEX IF NOT EXISTS idx_market_indices_timestamp
    ON market_indices (timestamp DESC);

-- Index for recent data queries (last 30 days)
CREATE INDEX IF NOT EXISTS idx_market_indices_recent
    ON market_indices (code, timestamp DESC)
    WHERE timestamp >= NOW() - INTERVAL '30 days';

COMMENT ON INDEX idx_market_indices_code_timestamp IS
    'Composite index for querying specific index over time ranges';

-- ============================================================================
-- CONTINUOUS AGGREGATES (Optional - for performance optimization)
-- ============================================================================

-- Daily aggregates for fast dashboard queries
CREATE MATERIALIZED VIEW IF NOT EXISTS market_indices_daily
WITH (timescaledb.continuous) AS
SELECT
    code,
    time_bucket('1 day', timestamp) AS bucket,
    first(open_value, timestamp) AS open_value,
    max(high_value) AS high_value,
    min(low_value) AS low_value,
    last(close_value, timestamp) AS close_value,
    sum(volume) AS total_volume,
    sum(trading_value) AS total_value,
    count(*) AS data_points
FROM market_indices
GROUP BY code, bucket;

COMMENT ON MATERIALIZED VIEW market_indices_daily IS
    'Continuous aggregate: daily market index data for fast queries';

-- Add index on the materialized view
CREATE INDEX IF NOT EXISTS idx_market_indices_daily_code_bucket
    ON market_indices_daily (code, bucket DESC);

-- Refresh policy: Update every hour
SELECT add_continuous_aggregate_policy('market_indices_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

-- ============================================================================
-- DATA RETENTION POLICY (Optional)
-- ============================================================================

-- Keep detailed intraday data for 90 days, then compress
SELECT add_retention_policy('market_indices',
    INTERVAL '2 years',
    if_not_exists => TRUE
);

COMMENT ON TABLE market_indices IS
    COMMENT ON TABLE market_indices ||
    ' Retention: 2 years. Older data automatically dropped.';

-- ============================================================================
-- SEED DATA (Sample)
-- ============================================================================

-- Insert sample data for testing (last 7 days of KOSPI)
-- This will be replaced by real data from KIS API or calculation
DO $$
DECLARE
    i INT := 0;
    base_date TIMESTAMP := NOW() - INTERVAL '7 days';
    base_value NUMERIC := 2500.0;
BEGIN
    FOR i IN 0..6 LOOP
        INSERT INTO market_indices (
            code,
            timestamp,
            open_value,
            high_value,
            low_value,
            close_value,
            volume,
            trading_value,
            change_value,
            change_percent
        ) VALUES (
            'KOSPI',
            base_date + (i || ' days')::INTERVAL,
            base_value + (random() * 20 - 10),
            base_value + (random() * 30),
            base_value - (random() * 30),
            base_value + (random() * 20 - 10),
            (400000000 + random() * 100000000)::BIGINT,
            (10000000000000 + random() * 5000000000000)::BIGINT,
            (random() * 40 - 20),
            (random() * 2 - 1)
        );

        -- KOSDAQ sample
        INSERT INTO market_indices (
            code,
            timestamp,
            open_value,
            high_value,
            low_value,
            close_value,
            volume,
            trading_value,
            change_value,
            change_percent
        ) VALUES (
            'KOSDAQ',
            base_date + (i || ' days')::INTERVAL,
            850.0 + (random() * 10 - 5),
            850.0 + (random() * 15),
            850.0 - (random() * 15),
            850.0 + (random() * 10 - 5),
            (300000000 + random() * 80000000)::BIGINT,
            (3000000000000 + random() * 2000000000000)::BIGINT,
            (random() * 20 - 10),
            (random() * 1.5 - 0.75)
        );

        -- KRX100 sample
        INSERT INTO market_indices (
            code,
            timestamp,
            open_value,
            high_value,
            low_value,
            close_value,
            volume,
            change_value,
            change_percent
        ) VALUES (
            'KRX100',
            base_date + (i || ' days')::INTERVAL,
            5200.0 + (random() * 50 - 25),
            5200.0 + (random() * 70),
            5200.0 - (random() * 70),
            5200.0 + (random() * 50 - 25),
            (200000000 + random() * 50000000)::BIGINT,
            (random() * 80 - 40),
            (random() * 1.8 - 0.9)
        );
    END LOOP;
END $$;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table creation
SELECT
    'market_indices' AS table_name,
    COUNT(*) AS row_count,
    MIN(timestamp) AS earliest_data,
    MAX(timestamp) AS latest_data
FROM market_indices;

-- Verify hypertable conversion
SELECT * FROM timescaledb_information.hypertables
WHERE hypertable_name = 'market_indices';

-- Verify continuous aggregate
SELECT * FROM timescaledb_information.continuous_aggregates
WHERE view_name = 'market_indices_daily';
