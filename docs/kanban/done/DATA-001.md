# DATA-001: Load Sample Stock Data for Testing and Validation

**Status**: DONE
**Priority**: High
**Assignee**: kcenon
**Estimated Time**: 4 hours
**Sprint**: Post-MVP Data Loading
**Tags**: data, database, testing, airflow, validation

## Description

The database schema is complete but tables are empty. Sample stock data must be loaded to enable Airflow DAG testing, end-to-end validation, and realistic performance testing. This ticket covers loading a minimal dataset for testing purposes.

## Current State

**Database Status**:
- ✅ Schema created (DB-002)
- ✅ Tables exist (stocks, daily_prices, stock_indicators, etc.)
- ✅ Stock data: 150 records (100 KOSPI + 50 KOSDAQ)
- ✅ Price data: 27,000 records (~252 trading days per stock)
- ✅ Indicator data: 150 records (all indicators calculated)
- ✅ Financial statements: 600 records (4 quarters per stock)

**Impact Resolution**:
- ✅ Can test Airflow DAG execution
- ✅ Can validate data pipeline
- ✅ Performance tests with realistic data
- ✅ End-to-end testing unblocked

## Root Cause

**Data Loading Not Completed**:
- Seed scripts exist but not executed
- DAG execution requires existing stock list
- No sample data in repository
- Data population deferred during MVP development

## Subtasks

### 1. Prepare Sample Stock Data

- [ ] Define sample dataset scope
  - **Recommended**: 50-100 stocks for testing
  - Include mix of markets (KOSPI + KOSDAQ)
  - Include various sectors
  - Include different market caps

- [ ] Create stock seed data
  ```sql
  -- File: database/seeds/sample_stocks.sql
  INSERT INTO stocks (code, name, market, sector, industry) VALUES
  ('005930', 'Samsung Electronics', 'KOSPI', 'Technology', 'Semiconductors'),
  ('000660', 'SK Hynix', 'KOSPI', 'Technology', 'Semiconductors'),
  ('035420', 'NAVER', 'KOSPI', 'Technology', 'Internet'),
  -- ... 47 more stocks
  ```

- [ ] Include metadata
  - Market cap ranges
  - Volume ranges
  - Various sectors
  - Active/delisted status

### 2. Load Stock Master Data

- [ ] Execute stock seed script
  ```bash
  docker exec screener_postgres psql \
    -U screener_user \
    -d screener_db \
    -f /docker-entrypoint-initdb.d/sample_stocks.sql
  ```

- [ ] Verify stock data loaded
  ```sql
  SELECT COUNT(*) FROM stocks;
  -- Expected: 50-100

  SELECT market, COUNT(*) FROM stocks GROUP BY market;
  -- Expected: Mix of KOSPI/KOSDAQ
  ```

- [ ] Validate data quality
  ```sql
  -- Check for nulls
  SELECT * FROM stocks WHERE code IS NULL OR name IS NULL;
  -- Expected: 0 rows

  -- Check for duplicates
  SELECT code, COUNT(*) FROM stocks GROUP BY code HAVING COUNT(*) > 1;
  -- Expected: 0 rows
  ```

### 3. Generate Sample Price Data

- [ ] Create price data generator script
  ```python
  # scripts/data/generate_sample_prices.py
  import random
  from datetime import datetime, timedelta

  def generate_prices(stock_codes, days=30):
      """Generate realistic sample price data"""
      for code in stock_codes:
          base_price = random.randint(5000, 100000)
          for day in range(days):
              date = datetime.now() - timedelta(days=day)
              # Generate OHLCV with realistic variance
              yield {
                  'stock_code': code,
                  'trade_date': date,
                  'open': base_price * random.uniform(0.98, 1.02),
                  # ... etc
              }
  ```

- [ ] Execute price generation
  ```bash
  python scripts/data/generate_sample_prices.py \
    --stocks 50 \
    --days 30 \
    --output database/seeds/sample_prices.sql
  ```

- [ ] Load price data
  ```bash
  docker exec screener_postgres psql \
    -U screener_user \
    -d screener_db \
    -f /docker-entrypoint-initdb.d/sample_prices.sql
  ```

### 4. Validate Data Loading

- [ ] Check record counts
  ```sql
  -- Stocks
  SELECT COUNT(*) FROM stocks;
  -- Expected: 50-100

  -- Prices (30 days * 50 stocks)
  SELECT COUNT(*) FROM daily_prices;
  -- Expected: ~1,500

  -- Date range
  SELECT MIN(trade_date), MAX(trade_date) FROM daily_prices;
  -- Expected: Last 30 days
  ```

- [ ] Verify data integrity
  ```sql
  -- All stocks have prices
  SELECT s.code, s.name
  FROM stocks s
  LEFT JOIN daily_prices dp ON s.code = dp.stock_code
  WHERE s.is_active = true
  AND dp.stock_code IS NULL;
  -- Expected: 0 rows

  -- Price data validity
  SELECT COUNT(*) FROM daily_prices
  WHERE open <= 0 OR close <= 0 OR volume < 0;
  -- Expected: 0 rows
  ```

- [ ] Test queries
  ```sql
  -- Sample screening query
  SELECT s.code, s.name, dp.close, dp.volume
  FROM stocks s
  JOIN daily_prices dp ON s.code = dp.stock_code
  WHERE dp.trade_date = (SELECT MAX(trade_date) FROM daily_prices)
  AND dp.volume > 100000
  LIMIT 10;
  -- Expected: Results returned
  ```

### 5. Enable Airflow DAG Testing

- [ ] Verify Airflow sees stock data
  ```sql
  -- In Airflow DAG context
  SELECT COUNT(*) FROM stocks WHERE is_active = true;
  -- Should return > 0
  ```

- [ ] Test indicator calculation DAG
  - Navigate to http://localhost:8080
  - Unpause `indicator_calculation` DAG
  - Trigger manual run
  - Monitor task execution
  - Verify indicators calculated

- [ ] Check indicator results
  ```sql
  SELECT COUNT(*) FROM stock_indicators;
  -- Expected: Records for all stocks

  SELECT * FROM stock_indicators LIMIT 5;
  -- Verify: PER, PBR, ROE, RSI, MACD populated
  ```

### 6. Create Data Loading Documentation

- [ ] Document data loading procedure
  ```markdown
  # File: docs/DATA_LOADING.md

  ## Sample Data Loading

  ### Quick Start
  1. Load stock master data
  2. Generate price data
  3. Run indicator calculation DAG

  ### Scripts
  - `database/seeds/sample_stocks.sql`
  - `scripts/data/generate_sample_prices.py`

  ### Validation
  - Check record counts
  - Verify data quality
  - Test screening queries
  ```

- [ ] Add to README
  - Link to data loading docs
  - Note sample data is for testing
  - Production data requires KRX API

## Acceptance Criteria

### Stock Data Loaded
- [ ] 50-100 sample stocks in database
- [ ] Mix of KOSPI and KOSDAQ markets
- [ ] Multiple sectors represented
- [ ] All required fields populated
- [ ] No duplicate stock codes

### Price Data Generated
- [ ] 30 days of price data for each stock
- [ ] OHLCV data complete
- [ ] Realistic price movements
- [ ] No invalid data (negative prices, etc.)
- [ ] ~1,500 total price records

### Data Quality Validated
- [ ] No NULL values in required fields
- [ ] No duplicate records
- [ ] All stocks have price data
- [ ] Date ranges correct
- [ ] Price ranges realistic

### Airflow DAG Testable
- [ ] indicator_calculation DAG runs successfully
- [ ] Indicators calculated for all stocks
- [ ] Results stored in stock_indicators table
- [ ] No errors in DAG execution
- [ ] Task logs show successful processing

### Screening Queries Work
- [ ] Can filter by market
- [ ] Can filter by price range
- [ ] Can filter by volume
- [ ] Results returned correctly
- [ ] Performance acceptable (<200ms)

### Documentation Complete
- [ ] Data loading procedure documented
- [ ] Scripts documented
- [ ] Validation steps documented
- [ ] README updated

## Testing Steps

### Step 1: Load Stock Data
```bash
# Create seed data (if not exists)
cat > database/seeds/sample_stocks.sql << 'EOF'
INSERT INTO stocks (code, name, market, sector) VALUES
('005930', 'Samsung Electronics', 'KOSPI', 'Technology'),
-- ... more stocks
EOF

# Load data
docker exec -i screener_postgres psql -U screener_user -d screener_db \
  < database/seeds/sample_stocks.sql

# Verify
docker exec screener_postgres psql -U screener_user -d screener_db \
  -c "SELECT COUNT(*) FROM stocks;"
```

### Step 2: Generate and Load Price Data
```bash
# Generate prices
python scripts/data/generate_sample_prices.py

# Load prices
docker exec -i screener_postgres psql -U screener_user -d screener_db \
  < database/seeds/sample_prices.sql

# Verify
docker exec screener_postgres psql -U screener_user -d screener_db \
  -c "SELECT COUNT(*) FROM daily_prices;"
```

### Step 3: Test Airflow DAG
```bash
# Access Airflow UI
open http://localhost:8080

# Trigger indicator_calculation DAG
# Monitor execution in UI

# Verify results
docker exec screener_postgres psql -U screener_user -d screener_db \
  -c "SELECT COUNT(*) FROM stock_indicators;"
```

## Dependencies

- [x] Database schema created (DB-002)
- [x] Airflow configured (DP-001)
- [ ] PostgreSQL container running
- [ ] Python environment for data generation

## Blocks

- Airflow DAG execution testing (BUGFIX-010 completion)
- End-to-end validation
- Realistic performance testing
- User acceptance testing

## References

- Database Schema: `database/schema.sql`
- Seed Scripts: `database/seeds/`
- Airflow DAGs: `data_pipeline/dags/`
- BUGFIX-010: Airflow validation report

## Progress

- **Current**: 100%
- **Updated**: 2025-11-12
- **Completed**: All subtasks completed, data loaded and validated

## Notes

**Sample Data Scope**:
- This is TEST data only
- Not for production use
- Minimal viable dataset (50-100 stocks)
- 30 days of history sufficient

**Production Data**:
- Use KRX API for real data
- Load full stock universe (2,400+)
- Historical backfill as needed
- Daily updates via Airflow

**Data Generation Tips**:
- Use realistic price ranges
- Apply proper volatility
- Ensure business days only
- Include various market caps

**Troubleshooting**:
- If load fails: Check PostgreSQL logs
- If data invalid: Review generator script
- If DAG fails: Check Airflow logs and data quality

---

**Created**: 2024-11-11
**Last Updated**: 2024-11-11
**Ticket Type**: Data Loading - Sample Dataset
**Related Tickets**: DB-002, DP-001, DP-002, DP-003, BUGFIX-010
