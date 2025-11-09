# Airflow Quick Start Guide

This guide will help you set up Apache Airflow for the Stock Screening Platform in **under 5 minutes**.

## Prerequisites

- Docker & Docker Compose installed
- PostgreSQL running (via `docker-compose up -d postgres`)
- `.env` file configured with database credentials

## Option 1: Automated Setup (Recommended)

### Step 1: Run Setup Script

```bash
# From project root
./scripts/setup_airflow.sh docker
```

This script will:
- Generate Fernet key for Airflow encryption
- Start Airflow webserver and scheduler
- Initialize Airflow database
- Create admin user
- Configure database connections

### Step 2: Access Airflow UI

Open your browser and navigate to:

```
http://localhost:8080
```

**Login credentials:**
- Username: `admin`
- Password: `admin` (or value from `.env`)

### Step 3: Verify Setup

1. Check that DAGs are visible:
   - `daily_price_ingestion`
   - `indicator_calculation`

2. Test database connection:
   - Go to Admin → Connections
   - Find `screener_db` connection
   - Click "Test" button → Should show green success

3. Trigger a test run:
   - Click on `daily_price_ingestion` DAG
   - Click "Trigger DAG" button
   - Monitor task execution in Graph view

✅ **Setup Complete!** Airflow is now ready to orchestrate data pipelines.

---

## Option 2: Manual Setup

If you prefer manual control or the automated script fails:

### Step 1: Generate Fernet Key

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the output to `.env`:
```bash
AIRFLOW_FERNET_KEY=<generated-key>
```

### Step 2: Start Airflow Services

```bash
# Start all services including Airflow
docker-compose --profile full up -d

# Or start only Airflow services
docker-compose up -d airflow_webserver airflow_scheduler
```

### Step 3: Wait for Initialization

Airflow will automatically:
- Initialize metadata database
- Create admin user (from `.env` variables)
- Start webserver and scheduler

Wait ~30 seconds for services to be healthy:

```bash
docker-compose ps
```

You should see:
- `screener_airflow_webserver` - healthy
- `screener_airflow_scheduler` - running

### Step 4: Configure Database Connection

```bash
# Execute connection setup script inside container
docker-compose exec airflow_webserver python /opt/airflow/dags/../config/setup_connections.py
```

### Step 5: Access UI

Open http://localhost:8080 and log in with credentials from `.env`

---

## Environment Variables

Required variables in `.env`:

```bash
# Airflow Configuration
AIRFLOW_PORT=8080
AIRFLOW_USER=admin
AIRFLOW_PASSWORD=admin
AIRFLOW_FERNET_KEY=<generated-key>
AIRFLOW_SECRET_KEY=<random-secret-key>

# Database for Airflow metadata
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://screener_user:password@postgres:5432/airflow

# Screener database (for DAGs to connect)
SCREENER_DB_HOST=postgres
SCREENER_DB_PORT=5432
SCREENER_DB_NAME=screener_db
SCREENER_DB_USER=screener_user
SCREENER_DB_PASSWORD=<your-password>
```

---

## Troubleshooting

### Webserver not starting

**Check logs:**
```bash
docker-compose logs airflow_webserver
```

**Common issue**: Database not ready
```bash
# Ensure PostgreSQL is running
docker-compose up -d postgres

# Wait for healthy status
docker-compose ps postgres
```

### DAGs not appearing in UI

**Cause**: DAG parsing errors

**Solution:**
```bash
# Check DAG import errors
docker-compose exec airflow_webserver airflow dags list-import-errors

# Validate DAG syntax
docker-compose exec airflow_webserver python /opt/airflow/dags/daily_price_ingestion_dag.py
```

### Connection test fails

**Check database is accessible:**
```bash
# From host machine
docker-compose exec postgres pg_isready

# Test connection manually
docker-compose exec postgres psql -U screener_user -d screener_db -c "SELECT version();"
```

**Update connection:**
```bash
# Re-run connection setup
docker-compose exec airflow_webserver python /opt/airflow/dags/../config/setup_connections.py
```

### Permission denied on volumes

**Issue**: Docker volume mount permissions

**Solution:**
```bash
# Fix ownership (Linux only)
sudo chown -R $USER:$USER data_pipeline/

# Or recreate volumes
docker-compose down -v
docker-compose up -d
```

---

## Next Steps

After setup is complete:

1. **Review DAG configuration**
   - Check DAG schedules match your requirements
   - Verify email alert configuration

2. **Configure API credentials**
   - Add KRX API key to Airflow Variables
   - Add F&Guide API key (for financial statements)

3. **Test data ingestion**
   - Manually trigger `daily_price_ingestion` DAG
   - Monitor execution and check logs
   - Verify data loaded into `daily_prices` table

4. **Set up monitoring**
   - Configure SMTP for email alerts
   - Set up Slack webhook (optional)
   - Review SLA settings

---

## Useful Commands

```bash
# View all DAGs
docker-compose exec airflow_webserver airflow dags list

# Trigger a DAG run
docker-compose exec airflow_webserver airflow dags trigger daily_price_ingestion

# Check DAG run status
docker-compose exec airflow_webserver airflow dags list-runs -d daily_price_ingestion

# View task logs
docker-compose exec airflow_webserver airflow tasks logs daily_price_ingestion fetch_krx_prices 2024-11-09

# Access Airflow shell
docker-compose exec airflow_webserver bash

# Stop Airflow
docker-compose --profile full stop

# Restart Airflow
docker-compose --profile full restart
```

---

## Resources

- [Full README](README.md) - Detailed documentation
- [Airflow Docs](https://airflow.apache.org/docs/apache-airflow/stable/)
- [DAG Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

---

**Setup Time**: ~3-5 minutes
**Last Updated**: 2025-11-09
