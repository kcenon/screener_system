# Database Schema Documentation

## Overview

This directory contains the complete database schema for the Stock Screening Platform.

**Database**: PostgreSQL 16+ with TimescaleDB extension

## Directory Structure

```
database/
├── migrations/          # Schema migration files (numbered sequence)
│   ├── 00_extensions.sql
│   ├── 01_create_tables.sql
│   ├── 02_timescaledb_setup.sql
│   ├── 03_indexes.sql
│   ├── 04_functions_triggers.sql
│   ├── 05_views.sql
│   ├── 06_add_calculated_indicators_updated_at.sql
│   └── 07_order_book.sql
├── seeds/              # Initial/test data
│   ├── dev_seed.sql
│   └── prod_seed.sql
├── scripts/            # Utility scripts
│   ├── backup.sh
│   ├── restore.sh
│   └── reset_dev.sh
└── README.md           # This file
```

## Setup Instructions

### 1. Install PostgreSQL 16+

**macOS (Homebrew)**:
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Ubuntu/Debian**:
```bash
sudo apt-get install postgresql-16
```

### 2. Install TimescaleDB Extension

**macOS**:
```bash
brew tap timescale/tap
brew install timescaledb
```

**Ubuntu/Debian**:
```bash
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt update
sudo apt install timescaledb-2-postgresql-16
```

### 3. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE screener_db;
CREATE USER screener_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE screener_db TO screener_user;

# Connect to new database
\c screener_db

# Grant schema privileges
GRANT ALL ON SCHEMA public TO screener_user;
```

### 4. Run Migrations

Execute migration files in order:

```bash
# From the database/ directory
psql -U screener_user -d screener_db -f migrations/00_extensions.sql
psql -U screener_user -d screener_db -f migrations/01_create_tables.sql
psql -U screener_user -d screener_db -f migrations/02_timescaledb_setup.sql
psql -U screener_user -d screener_db -f migrations/03_indexes.sql
psql -U screener_user -d screener_db -f migrations/04_functions_triggers.sql
psql -U screener_user -d screener_db -f migrations/05_views.sql
psql -U screener_user -d screener_db -f migrations/06_add_calculated_indicators_updated_at.sql
psql -U screener_user -d screener_db -f migrations/07_order_book.sql
```

Or use the automated script:
```bash
./scripts/run_migrations.sh
```

### 5. Seed Data (Optional)

**Development**:
```bash
psql -U screener_user -d screener_db -f seeds/dev_seed.sql
```

**Production**:
```bash
psql -U screener_user -d screener_db -f seeds/prod_seed.sql
```

## Schema Overview

### Core Tables

| Table | Purpose | Rows (Estimated) |
|-------|---------|------------------|
| `stocks` | Stock master data | ~2,400 |
| `daily_prices` | Daily OHLCV data (TimescaleDB) | ~2.4M (2,400 stocks × 1,000 days) |
| `financial_statements` | Quarterly/annual financials | ~50K |
| `calculated_indicators` | Pre-calculated 200+ indicators | ~2.4M |

### User Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts |
| `portfolios` | User portfolio containers |
| `portfolio_holdings` | Stock holdings in portfolios |
| `alerts` | Price/volume alert configurations |

### Audit Tables

| Table | Purpose |
|-------|---------|
| `user_activity_log` | User action tracking |
| `data_ingestion_log` | Data pipeline monitoring |

## Performance Considerations

### TimescaleDB Hypertables

`daily_prices` is converted to a TimescaleDB hypertable partitioned by `trade_date`:
- Automatic time-based partitioning (1-month chunks)
- Continuous aggregates for fast queries
- Compression for data older than 1 year (10x storage reduction)

### Indexes

Strategic indexes on:
- Foreign keys (automatic query optimization)
- Frequently filtered columns (e.g., `market`, `sector`)
- Search columns with trigram indexes for fuzzy matching

### Caching Strategy

- Application caching (Redis): Hot data, screening results
- PostgreSQL caching: `shared_buffers` set to 25% of RAM
- Materialized views: Pre-computed aggregations

## Maintenance

### Vacuum & Analyze

Run weekly:
```sql
VACUUM ANALYZE;
```

### TimescaleDB Compression

Automatically compresses data older than 1 year:
```sql
SELECT add_compression_policy('daily_prices', INTERVAL '365 days');
```

### Backup

Daily automated backups:
```bash
./scripts/backup.sh
```

Retention: 7 daily, 4 weekly, 12 monthly

## Monitoring

### Key Metrics

- Table sizes: `SELECT pg_size_pretty(pg_total_relation_size('table_name'));`
- Index usage: Check `pg_stat_user_indexes`
- Slow queries: Enable `log_min_duration_statement = 1000` (1 second)

### Useful Queries

**Table sizes**:
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Index usage**:
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Troubleshooting

### Connection Issues

Check PostgreSQL is running:
```bash
pg_isready -U screener_user -d screener_db
```

### Permission Errors

Grant all necessary privileges:
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO screener_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO screener_user;
```

### TimescaleDB Not Working

Verify extension is installed:
```sql
SELECT * FROM pg_extension WHERE extname = 'timescaledb';
```

If not installed, run:
```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

## References

- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

Last Updated: 2025-11-09
