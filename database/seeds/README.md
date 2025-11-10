# Seed Data

This directory contains seed data for development and testing of the Stock Screening Platform.

## Overview

The seed data includes:
- **150 stocks**: 100 from KOSPI, 50 from KOSDAQ
- **27,000 daily prices**: 252 trading days (1 year) per stock
- **600 financial statements**: Last 4 quarters for each stock
- **150 calculated indicators**: All 60+ technical and fundamental indicators

## Files

- `generate_seed_data.py`: Python script to generate realistic seed data
- `seed_data.sql`: Auto-generated SQL file with seed data (2.7MB)
- `load_seed_data.sh`: Bash script to load seed data into database
- `dev_seed.sql`: Small development seed (10 stocks, 30 days) - legacy

## Quick Start

### 1. Generate Seed Data

```bash
# Generate with default settings (100 KOSPI + 50 KOSDAQ, 252 days)
python3 generate_seed_data.py

# Custom configuration
python3 generate_seed_data.py --kospi 150 --kosdaq 75 --days 365 --output custom_seed.sql
```

**Options:**
- `--kospi`: Number of KOSPI stocks (default: 100)
- `--kosdaq`: Number of KOSDAQ stocks (default: 50)
- `--days`: Number of trading days for price history (default: 252)
- `--output`: Output SQL file path (default: seeds/seed_data.sql)

### 2. Load Seed Data

```bash
# Load to default database (screener_db)
./load_seed_data.sh

# Load to test database
./load_seed_data.sh screener_test

# Load from custom file
./load_seed_data.sh screener_db custom_seed.sql
```

### 3. Load via Docker

```bash
# From project root
docker exec screener_postgres psql -U screener_user -d screener_db -f /docker-entrypoint-initdb.d/seeds/seed_data.sql

# Or use the convenience script
docker exec screener_postgres bash -c "cd /docker-entrypoint-initdb.d && ./seeds/load_seed_data.sh"
```

## Seed Data Structure

### Stocks (150 rows)

Real Korean companies with realistic data:

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

**KOSPI Stocks (100):**
- Large cap: Market cap 1T-500T KRW
- Major sectors: Technology, Financial, Consumer, Industrial
- Includes top 20 real Korean companies (삼성전자, SK하이닉스, NAVER, etc.)

**KOSDAQ Stocks (50):**
- Mid/small cap: Market cap 100B-10T KRW
- Growth sectors: Biotech, IT, Gaming

### Daily Prices (27,000 rows)

Historical OHLCV data for 252 trading days (approx. 1 year):

```sql
stock_code: '005930'
trade_date: '2025-11-10'
open_price: 71,234
high_price: 73,456
low_price: 70,123
close_price: 72,345
adjusted_close: 72,345
volume: 12,345,678
trading_value: 893,456,789,012
market_cap: 352,123,456,789,000
```

**Features:**
- Realistic price movements (-3% to +3.5% daily change)
- Random walk with slight upward bias
- Volume proportional to market cap
- Excludes weekends (simplified - no holiday calendar)

### Financial Statements (600 rows)

Quarterly financial data for last 4 quarters per stock:

```sql
-- Example: Q3 2024
revenue: 79,107,000,000,000           # 79.1T KRW
gross_profit: 23,732,100,000,000      # 30% margin
operating_profit: 13,519,000,000,000  # 17% margin
net_profit: 10,062,000,000,000        # 12.7% margin
total_assets: 465,872,000,000,000
total_liabilities: 116,404,000,000,000
equity: 349,468,000,000,000
operating_cash_flow: 23,000,000,000,000
free_cash_flow: 15,000,000,000,000
```

**Metrics:**
- Revenue: Proportional to market cap
- Profit margins: 20-50% gross, 5-25% operating, 3-20% net
- Balance sheet: Realistic debt-to-equity ratios (15-60%)
- Cash flows: Consistent with profitability

### Calculated Indicators (150 rows)

All 60+ technical and fundamental indicators:

```sql
-- Valuation
per: 12.50                  # Price-to-Earnings
pbr: 1.20                   # Price-to-Book
psr: 1.80                   # Price-to-Sales
dividend_yield: 2.50        # %

-- Profitability
roe: 15.20                  # Return on Equity (%)
roa: 9.80                   # Return on Assets (%)
gross_margin: 38.50         # %
operating_margin: 15.30     # %
net_margin: 12.70           # %

-- Growth
revenue_growth_yoy: 8.50    # Year-over-Year (%)
profit_growth_yoy: 15.30    # %

-- Stability
debt_to_equity: 33.30       # %
current_ratio: 2.10

-- Quality Scores
piotroski_f_score: 8        # 0-9 scale
quality_score: 85           # 0-100
value_score: 75             # 0-100
growth_score: 70            # 0-100
overall_score: 80           # 0-100
```

## Regenerating Seed Data

The seed data is **idempotent** - you can run it multiple times safely using `ON CONFLICT DO NOTHING`.

To regenerate with fresh data:

```bash
# Clear existing data
docker exec screener_postgres psql -U screener_user -d screener_db -c "
TRUNCATE TABLE calculated_indicators, financial_statements, daily_prices, stocks CASCADE;
"

# Generate new seed
python3 generate_seed_data.py

# Load new seed
./load_seed_data.sh
```

## Using for Testing

### Unit Tests

```python
# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def test_db():
    """Load seed data for testing"""
    # Load seed_data.sql to screener_test
    subprocess.run([
        "psql", "-U", "screener_user", "-d", "screener_test",
        "-f", "database/seeds/seed_data.sql"
    ])
    yield
```

### Integration Tests

```bash
# Load test data
./load_seed_data.sh screener_test

# Run tests
pytest backend/tests/integration/

# Verify data via API
curl "http://localhost:8000/v1/stocks?limit=10"
```

## Data Quality

The seed data maintains realistic relationships:

✅ **Consistency**
- Stock prices match market cap calculations
- Financial ratios calculated from actual statement data
- Indicator values consistent with price and fundamental data

✅ **Realism**
- Real Korean company names and stock codes for top 20
- Realistic Korean naming patterns for generated companies
- Market-appropriate price ranges (KOSPI: 10K-100K, KOSDAQ: 5K-50K)
- Sector-appropriate metrics (tech has higher P/E, banks have higher D/E)

✅ **Completeness**
- All required fields populated
- No NULL values in critical columns
- Foreign key relationships intact

## Performance

Loading seed data typically takes:
- **Generation**: 10-15 seconds
- **SQL execution**: 30-60 seconds
- **Total size**: 2.7MB (well under 10MB limit)

For faster testing, use `dev_seed.sql` (10 stocks, 30 days, <100KB).

## Customization

### Add More Real Stocks

Edit `generate_seed_data.py`:

```python
KOSPI_STOCKS = [
    ('005930', '삼성전자', 'Samsung Electronics', 'Technology', 'Semiconductors'),
    ('000660', 'SK하이닉스', 'SK Hynix', 'Technology', 'Semiconductors'),
    # Add your stocks here
    ('123456', '새로운회사', 'New Company', 'Sector', 'Industry'),
]
```

### Adjust Data Ranges

```python
# More volatile prices
daily_change = random.uniform(-0.10, 0.10)  # ±10% daily

# Higher market caps
base_price = random.randint(50000, 500000)  # 50K-500K KRW

# Longer history
args.days = 504  # 2 years
```

## Troubleshooting

### "Cannot connect to database"

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check credentials in .env
cat .env | grep POSTGRES_
```

### "Seed file not found"

```bash
# Generate seed data first
python3 seeds/generate_seed_data.py
```

### "Duplicate key violation"

The seed script uses `ON CONFLICT DO NOTHING`, so this shouldn't happen. If it does:

```bash
# Clear data and reload
psql -U screener_user -d screener_db -c "TRUNCATE TABLE stocks CASCADE;"
./load_seed_data.sh
```

### "Out of memory"

For large datasets (>500 stocks):

```bash
# Generate in smaller batches
python3 generate_seed_data.py --kospi 50 --kosdaq 25 --output batch1.sql
python3 generate_seed_data.py --kospi 50 --kosdaq 25 --output batch2.sql

# Load separately
./load_seed_data.sh screener_db batch1.sql
./load_seed_data.sh screener_db batch2.sql
```

## References

- **Faker**: https://github.com/joke2k/faker
- **FinanceDataReader**: https://github.com/FinanceData/FinanceDataReader (for real data)
- **Database Schema**: `/database/migrations/01_create_tables.sql`

## Version History

- **v1.0** (2025-11-10): Initial seed data generator
  - 150 stocks (100 KOSPI + 50 KOSDAQ)
  - 252 days price history
  - 4 quarters financial statements
  - 60+ calculated indicators
  - Realistic Korean company names
  - Idempotent SQL script

## License

Same as project license. Seed data is for development/testing only.
