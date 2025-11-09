# Airflow Setup Troubleshooting Guide

This document covers common issues encountered during Airflow setup and their solutions.

## Issue 1: ModuleNotFoundError: No module named 'cryptography'

### Symptom
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from cryptography.fernet import Fernet
ModuleNotFoundError: No module named 'cryptography'
```

### Root Cause
The `cryptography` Python module is not installed on the host system.

### Solution
The setup script now automatically falls back to using a Docker container to generate the Fernet key.

**Fixed in**: Commit `8bef842`

### Manual Workaround
If you need to generate the key manually:

```bash
# Option 1: Install cryptography module
pip3 install cryptography
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Option 2: Use Docker (no installation needed)
docker run --rm python:3.11-slim python -c "import subprocess; subprocess.check_call(['pip', 'install', '-q', 'cryptography']); from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Then add the generated key to `.env`:
```bash
AIRFLOW_FERNET_KEY=<generated-key>
```

---

## Issue 2: Database "airflow" does not exist

### Symptom
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
connection to server at "postgres" (172.18.0.3), port 5432 failed:
FATAL:  database "airflow" does not exist
```

### Root Cause
The PostgreSQL `airflow` database was not created before starting Airflow services.

### Solution
The setup script now automatically creates the `airflow` database if it doesn't exist.

**Fixed in**: Commit `52a8ad4`

### Manual Workaround
Create the database manually:

```bash
# Check if airflow database exists
docker-compose exec postgres psql -U screener_user -d postgres -c "\l" | grep airflow

# Create airflow database if it doesn't exist
docker-compose exec postgres psql -U screener_user -d postgres -c "CREATE DATABASE airflow OWNER screener_user;"

# Restart Airflow services
docker-compose restart airflow_webserver airflow_scheduler
```

### Automated Script
Use the provided script:

```bash
./database/scripts/init_airflow_db.sh
```

---

## Issue 3: Airflow webserver timeout (30 retries)

### Symptom
```
[ERROR] Airflow failed to start after 30 retries
[INFO] Check logs with: docker-compose logs airflow_webserver
```

### Root Cause
Usually caused by:
1. Missing `airflow` database
2. Database connection issues
3. Incorrect environment variables

### Diagnosis Steps

**Step 1**: Check webserver logs
```bash
docker-compose logs airflow_webserver --tail 50
```

**Step 2**: Verify database connection
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test database connection
docker-compose exec postgres psql -U screener_user -d postgres -c "SELECT version();"
```

**Step 3**: Check environment variables
```bash
# Verify Airflow configuration
docker-compose exec airflow_webserver env | grep AIRFLOW

# Check database URL
docker-compose exec airflow_webserver env | grep SQL_ALCHEMY_CONN
```

### Solutions

**If database is missing**: See Issue #2 above

**If connection fails**:
```bash
# Ensure PostgreSQL is healthy
docker-compose up -d postgres
docker-compose exec postgres pg_isready

# Restart Airflow
docker-compose restart airflow_webserver airflow_scheduler
```

**If configuration is wrong**:
```bash
# Update .env file
# Then restart services
docker-compose down
docker-compose --profile full up -d
```

---

## Issue 4: DAGs not appearing in UI

### Symptom
Airflow UI is accessible but no DAGs are shown.

### Diagnosis

**Check DAG folder mounting**:
```bash
# Verify volume mount
docker-compose exec airflow_webserver ls -la /opt/airflow/dags/
```

**Check for DAG parsing errors**:
```bash
docker-compose exec airflow_webserver airflow dags list-import-errors
```

**Validate DAG syntax**:
```bash
docker-compose exec airflow_webserver python /opt/airflow/dags/daily_price_ingestion_dag.py
```

### Solutions

**If DAGs not mounted**:
```bash
# Check docker-compose.yml volumes section
# Ensure: ./data_pipeline/dags:/opt/airflow/dags

# Restart with volume recreation
docker-compose down
docker-compose --profile full up -d
```

**If parsing errors**:
Fix the Python errors shown in the import errors list, then:
```bash
# Force DAG refresh
docker-compose exec airflow_webserver airflow dags reserialize
```

---

## Issue 5: Permission denied on airflow_logs volume

### Symptom
```
PermissionError: [Errno 13] Permission denied: '/opt/airflow/logs/...'
```

### Root Cause
Volume ownership mismatch between host and container.

### Solution

**On Linux**:
```bash
# Fix ownership
sudo chown -R $USER:$USER data_pipeline/

# Or use root user in docker-compose (not recommended)
```

**On macOS/Windows**:
Usually not an issue. If it occurs:
```bash
# Recreate volumes
docker-compose down -v
docker volume create screener_system_airflow_logs
docker-compose --profile full up -d
```

---

## Quick Diagnostic Checklist

Use this checklist to quickly diagnose Airflow issues:

- [ ] **PostgreSQL running**: `docker-compose ps postgres` → Healthy
- [ ] **airflow database exists**: `docker-compose exec postgres psql -U screener_user -d postgres -c "\l" | grep airflow`
- [ ] **Environment variables set**: Check `.env` for AIRFLOW_FERNET_KEY, AIRFLOW_SECRET_KEY
- [ ] **Webserver healthy**: `curl http://localhost:8080/health`
- [ ] **Scheduler running**: `docker-compose logs airflow_scheduler | grep "Starting the scheduler"`
- [ ] **DAGs folder mounted**: `docker-compose exec airflow_webserver ls /opt/airflow/dags/`
- [ ] **No import errors**: `docker-compose exec airflow_webserver airflow dags list-import-errors`

---

## Getting Help

If none of the above solutions work:

1. **Collect logs**:
   ```bash
   # Save all logs for debugging
   docker-compose logs airflow_webserver > webserver.log
   docker-compose logs airflow_scheduler > scheduler.log
   docker-compose logs postgres > postgres.log
   ```

2. **Check Airflow health**:
   ```bash
   curl http://localhost:8080/health | jq
   ```

3. **Review configuration**:
   ```bash
   docker-compose config | grep -A 20 airflow
   ```

4. **Restart everything**:
   ```bash
   # Nuclear option: complete restart
   docker-compose down
   docker volume prune -f
   docker-compose --profile full up -d
   ```

---

## Prevention

To avoid these issues in future setups:

1. **Use the automated setup script**:
   ```bash
   ./scripts/setup_airflow.sh docker
   ```

2. **Verify prerequisites**:
   - Docker and Docker Compose installed
   - PostgreSQL container running and healthy
   - `.env` file configured with all required variables

3. **Check logs immediately after setup**:
   ```bash
   docker-compose logs -f airflow_webserver
   ```

4. **Test health endpoints**:
   ```bash
   curl http://localhost:8080/health
   ```

---

**Last Updated**: 2025-11-09
**Version**: 1.0.0
