# [BUGFIX-005] Add Seed Data for Development and Testing

## Metadata
- **Status**: TODO
- **Priority**: Medium
- **Assignee**: AI Assistant
- **Estimated Time**: 4 hours
- **Sprint**: Sprint 3
- **Tags**: #data #testing #development #database
- **Created**: 2025-11-10

## Description
The database tables are empty, preventing frontend and API integration testing. Add seed data with realistic Korean stock market data for development and testing.

## Current State
- stocks table: 0 rows
- daily_prices table: 0 rows
- calculated_indicators table: 0 rows
- All other tables: 0 rows

## Subtasks
- [ ] Create seed data SQL script
  - [ ] 100 stocks from KOSPI (삼성전자, SK하이닉스, etc.)
  - [ ] 50 stocks from KOSDAQ (카카오, 네이버, etc.)
  - [ ] Historical daily_prices (last 252 trading days)
  - [ ] Calculated indicators for all stocks
  - [ ] Financial statements (last 4 quarters + 3 years)
- [ ] Create seed data generation script
  - [ ] Python script to generate realistic data
  - [ ] Use faker-korean for Korean company names
  - [ ] Realistic price movements (random walk)
  - [ ] Consistent indicator calculations
- [ ] Add seed data to database
  - [ ] Run seed script on screener_db
  - [ ] Run seed script on screener_test
  - [ ] Verify data integrity
- [ ] Update docker-compose.yml
  - [ ] Add seed data volume mount
  - [ ] Auto-run seed on first startup
- [ ] Document seed data structure
  - [ ] Add README in database/seeds/
  - [ ] Document how to regenerate seed data

## Acceptance Criteria
- [ ] Database has 150 stocks (100 KOSPI + 50 KOSDAQ)
- [ ] Each stock has price history (252 days)
- [ ] Each stock has calculated indicators
- [ ] Financial statements for major stocks
- [ ] Stock listing endpoint returns data
- [ ] Screening endpoint returns results
- [ ] Frontend screener page shows results
- [ ] Seed data script is idempotent (can run multiple times)

## Seed Data Structure
### stocks (150 rows)
- 100 KOSPI stocks (market_cap: 1T-500T KRW)
- 50 KOSDAQ stocks (market_cap: 100B-10T KRW)
- Realistic Korean company names
- Various sectors (Technology, Finance, Healthcare, etc.)

### daily_prices (37,800 rows = 150 * 252)
- Last 252 trading days (1 year)
- Realistic OHLCV data
- Price movements: -3% to +3% daily
- Volume: Proportional to market cap

### calculated_indicators (150 rows)
- All 60+ indicators calculated
- Consistent with price/financial data
- Reasonable ranges (PER: 5-50, PBR: 0.5-10, etc.)

### financial_statements (600 rows = 150 * 4 quarters)
- Last 4 quarters per stock
- Revenue, operating profit, net profit
- Assets, liabilities, equity
- Cash flow data

## Implementation Guide
```python
# database/seeds/generate_seed_data.py

import random
from datetime import datetime, timedelta
from faker import Faker

fake_kr = Faker('ko_KR')

def generate_stock(code, name, market, sector):
    return {
        'code': code,
        'name': name,
        'market': market,
        'sector': sector,
        'industry': f'{sector} Industry',
        'listing_date': fake_kr.date_between(start_date='-10y', end_date='-1y'),
        'shares_outstanding': random.randint(100_000_000, 1_000_000_000),
    }

def generate_price_history(stock_code, days=252):
    prices = []
    price = random.uniform(10000, 100000)

    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        change = random.uniform(-0.03, 0.03)
        price = price * (1 + change)

        prices.append({
            'stock_code': stock_code,
            'date': date.date(),
            'open': price * 0.99,
            'high': price * 1.01,
            'low': price * 0.98,
            'close': price,
            'volume': random.randint(100000, 10000000),
        })

    return prices

# ... (similar functions for indicators and financials)
```

## Dependencies
- **Depends on**: DB-002 (schema migrations)
- **Blocks**: FE-003, FE-004 (frontend development)

## Testing Plan
```bash
# Run seed script
python database/seeds/generate_seed_data.py

# Verify data
docker exec screener_postgres psql -U screener_user -d screener_db -c \
  "SELECT COUNT(*) FROM stocks; SELECT COUNT(*) FROM daily_prices;"

# Test APIs
curl "http://localhost:8000/v1/stocks?limit=10"
curl -X POST http://localhost:8000/v1/screen \
  -H "Content-Type: application/json" \
  -d '{"filters":{"market":"KOSPI"},"page":1,"per_page":50}'
```

## References
- **faker-korean**: https://github.com/cho2/faker_korean
- **FinanceDataReader**: https://github.com/FinanceData/FinanceDataReader
- **Database Schema**: `database/migrations/`

## Progress
- **0%** - Not started

## Notes
- Use realistic Korean stock tickers (005930 for Samsung, etc.)
- Keep seed data small enough for quick testing (<10MB)
- Provide both SQL and Python generation methods
- Consider using FinanceDataReader for real data (optional)
- Seed data should be version controlled
