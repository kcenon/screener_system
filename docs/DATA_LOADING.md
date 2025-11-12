# Data Loading Guide

This guide explains how to load sample stock data into the Stock Screening Platform for development and testing purposes.

## Overview

The platform includes pre-built seed data generator that creates realistic Korean stock market data:
- **150 stocks**: 100 from KOSPI, 50 from KOSDAQ
- **27,000 daily prices**: ~252 trading days per stock
- **600 financial statements**: Last 4 quarters for each stock
- **150 calculated indicators**: All technical and fundamental indicators

## Quick Start

### Load Pre-generated Seed Data

The fastest way to get started with sample data:

```bash
# Load via Docker (from project root)
docker exec -i screener_postgres psql -U screener_user -d screener_db \
  < database/seeds/seed_data.sql

# Verify data loaded
docker exec screener_postgres psql -U screener_user -d screener_db \
  -c "SELECT COUNT(*) FROM stocks; SELECT COUNT(*) FROM daily_prices;"
```

**Expected Output:**
```
 count 
-------
   150
   
 count  
--------
  27000
```

### Generate Fresh Seed Data

To customize the seed data or generate fresh datasets:

```bash
# Generate with default settings
cd database/seeds
python3 generate_seed_data.py

# Custom configuration
python3 generate_seed_data.py --kospi 75 --kosdaq 25 --days 180 --output custom_seed.sql

# Load custom data
docker exec -i screener_postgres psql -U screener_user -d screener_db \
  < database/seeds/custom_seed.sql
```

## Data Structure

### Stocks Table (150 records)

Real Korean companies with realistic metadata:

```sql
-- Example: Samsung Electronics
code: '005930'
name: '삼성전자'
name_english: 'Samsung Electronics'
market: 'KOSPI'
sector: 'Technology'
industry: 'Semiconductors'
listing_date: '2019-09-02'
shares_outstanding: 4,865,717,272
```

**Distribution:**
- KOSPI: 100 stocks (large cap, major sectors)
- KOSDAQ: 50 stocks (mid/small cap, growth sectors)

### Daily Prices Table (27,000 records)

Historical OHLCV data for approximately 1 year (252 trading days):

```sql
stock_code: '005930'
trade_date: '2025-11-07'
open_price: 71,234
high_price: 73,456
low_price: 70,123
close_price: 72,345
volume: 12,345,678
trading_value: 893,456,789,012
```

**Features:**
- Realistic price movements (-3% to +3.5% daily)
- Volume proportional to market cap
- No weekends (simplified calendar)

### Financial Statements Table (600 records)

Quarterly financial data for the last 4 quarters per stock:

```sql
-- Example: Q3 2024
revenue: 79,107,000,000,000           # 79.1T KRW
operating_profit: 13,519,000,000,000  # 17% margin
net_profit: 10,062,000,000,000        # 12.7% margin
total_assets: 465,872,000,000,000
equity: 349,468,000,000,000
```

### Calculated Indicators Table (150 records)

All 60+ technical and fundamental indicators pre-calculated:

```sql
-- Valuation
per: 12.50              # Price-to-Earnings
pbr: 1.20               # Price-to-Book
dividend_yield: 2.50    # %

-- Profitability
roe: 15.20              # Return on Equity
roa: 9.80               # Return on Assets
operating_margin: 15.30 # %

-- Quality Scores
piotroski_f_score: 8    # 0-9 scale
overall_score: 80       # 0-100
```

## Validation Steps

After loading data, verify integrity:

### 1. Check Record Counts

```bash
docker exec screener_postgres psql -U screener_user -d screener_db -c "
SELECT 
  'Stocks' as table_name, COUNT(*) as count FROM stocks
UNION ALL
SELECT 'Daily Prices', COUNT(*) FROM daily_prices
UNION ALL
SELECT 'Financial Statements', COUNT(*) FROM financial_statements
UNION ALL
SELECT 'Calculated Indicators', COUNT(*) FROM calculated_indicators;
"
```

**Expected:**
```
      table_name       | count 
-----------------------+-------
 Calculated Indicators |   150
 Daily Prices          | 27000
 Financial Statements  |   600
 Stocks                |   150
```

### 2. Verify Market Distribution

```bash
docker exec screener_postgres psql -U screener_user -d screener_db -c "
SELECT market, COUNT(*) FROM stocks GROUP BY market;
"
```

**Expected:**
```
 market | count 
--------+-------
 KOSDAQ |    50
 KOSPI  |   100
```

### 3. Check Data Quality

```bash
docker exec screener_postgres psql -U screener_user -d screener_db -c "
-- No NULL values in required fields
SELECT 'NULL values' as check, COUNT(*) as issues
FROM stocks WHERE code IS NULL OR name IS NULL
UNION ALL
-- No duplicate codes
SELECT 'Duplicates', COUNT(*) FROM (
  SELECT code FROM stocks GROUP BY code HAVING COUNT(*) > 1
) dups
UNION ALL
-- All stocks have prices
SELECT 'Missing prices', COUNT(*) FROM stocks s
LEFT JOIN daily_prices dp ON s.code = dp.stock_code
WHERE dp.stock_code IS NULL
UNION ALL
-- No invalid price data
SELECT 'Invalid prices', COUNT(*) FROM daily_prices
WHERE open_price <= 0 OR close_price <= 0 OR volume < 0;
"
```

**Expected:** All checks should return 0 issues.

### 4. Test Screening Queries

```bash
docker exec screener_postgres psql -U screener_user -d screener_db -c "
SELECT s.code, s.name, dp.close_price, dp.volume
FROM stocks s
JOIN daily_prices dp ON s.code = dp.stock_code
WHERE dp.trade_date = (SELECT MAX(trade_date) FROM daily_prices)
AND dp.volume > 1000000
LIMIT 5;
"
```

Should return valid stock data with prices and volumes.

## Using with API

Once data is loaded, test the API endpoints:

```bash
# Get stock list
curl "http://localhost:8000/v1/stocks?limit=10"

# Get stock details
curl "http://localhost:8000/v1/stocks/005930"

# Run screening query
curl -X POST "http://localhost:8000/v1/screening" \
  -H "Content-Type: application/json" \
  -d '{"filters": {"per": {"min": 5, "max": 15}}}'
```

## Airflow DAG Testing

The seed data enables testing of Airflow DAGs:

### 1. Access Airflow UI

```bash
open http://localhost:8080
# Default credentials: admin / admin
```

### 2. Trigger Indicator Calculation DAG

```bash
# Via CLI
docker exec screener_airflow_scheduler \
  airflow dags unpause indicator_calculation

docker exec screener_airflow_scheduler \
  airflow dags trigger indicator_calculation

# Via UI
# Navigate to DAGs -> indicator_calculation -> Trigger DAG
```

### 3. Monitor Execution

```bash
# Check DAG status
docker exec screener_airflow_scheduler \
  airflow dags list-runs -d indicator_calculation --no-backfill

# View logs
docker logs -f screener_airflow_scheduler
```

## Regenerating Data

To clear and reload fresh data:

```bash
# Clear existing data
docker exec screener_postgres psql -U screener_user -d screener_db -c "
TRUNCATE TABLE calculated_indicators, financial_statements, daily_prices, stocks CASCADE;
"

# Generate new seed
cd database/seeds
python3 generate_seed_data.py

# Load new seed
docker exec -i screener_postgres psql -U screener_user -d screener_db \
  < seed_data.sql
```

## Data Characteristics

### Realism
- Real Korean company names for top 20 stocks
- Realistic Korean naming patterns for generated companies
- Market-appropriate price ranges (KOSPI: 10K-100K, KOSDAQ: 5K-50K)
- Sector-appropriate financial metrics

### Consistency
- Stock prices match market cap calculations
- Financial ratios calculated from actual statement data
- Indicator values consistent with price and fundamental data

### Completeness
- All required fields populated
- No NULL values in critical columns
- Foreign key relationships intact
- Idempotent (can run multiple times safely)

## Performance

Loading seed data typically takes:
- **Generation**: 10-15 seconds
- **SQL execution**: 30-60 seconds
- **Total size**: 2.7MB

## Troubleshooting

### "Cannot connect to database"

```bash
# Check PostgreSQL is running
docker ps | grep screener_postgres

# Check credentials
cat .env | grep DB_
```

### "Seed file not found"

```bash
# Generate seed data
cd database/seeds
python3 generate_seed_data.py
```

### "Duplicate key violation"

```bash
# Clear data and reload (seed script uses ON CONFLICT DO NOTHING)
docker exec screener_postgres psql -U screener_user -d screener_db -c "
TRUNCATE TABLE stocks CASCADE;
"
docker exec -i screener_postgres psql -U screener_user -d screener_db \
  < database/seeds/seed_data.sql
```

## Production Data

**Important:** This seed data is for **testing and development only**.

For production:
- Use real KRX API data via Airflow DAGs
- Load full stock universe (2,400+ stocks)
- Implement historical backfill as needed
- Set up daily updates via scheduled DAGs

See [Data Pipeline Documentation](data_pipeline/README.md) for production data setup.

## References

- **Seed Data Generator**: `database/seeds/generate_seed_data.py`
- **Seed Data README**: `database/seeds/README.md`
- **Database Schema**: `database/migrations/01_create_tables.sql`
- **Airflow DAGs**: `data_pipeline/dags/`

## Version History

- **v1.0** (2025-11-12): Initial data loading guide
  - Quick start instructions
  - Validation procedures
  - Airflow integration
  - Troubleshooting guide
