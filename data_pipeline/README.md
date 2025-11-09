# Data Pipeline - Apache Airflow

## Quick Start

**New to Airflow?** See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

**TL;DR:**
```bash
# Automated setup (recommended)
./scripts/setup_airflow.sh docker

# Access UI at http://localhost:8080 (admin/admin)
```

## Overview

This directory contains Apache Airflow DAGs for the Stock Screening Platform's data ingestion and processing pipelines.

**Pipelines**:
1. **Daily Price Ingestion**: Fetch daily OHLCV data from KRX
2. **Indicator Calculation**: Calculate 200+ technical and fundamental indicators
3. **Financial Statement Updates**: Quarterly/annual financial data ingestion
4. **Data Quality Monitoring**: Validate data completeness and accuracy

## Directory Structure

```
data_pipeline/
├── dags/                      # Airflow DAG definitions
│   ├── daily_price_ingestion_dag.py
│   ├── indicator_calculation_dag.py
│   ├── financial_statements_dag.py
│   └── data_quality_monitoring_dag.py
├── plugins/                   # Custom Airflow plugins
│   ├── operators/
│   ├── sensors/
│   └── hooks/
├── config/                    # Configuration files
│   ├── airflow.cfg
│   └── connections.json
├── scripts/                   # Utility scripts
│   ├── krx_api_client.py
│   └── fguide_api_client.py
└── README.md                  # This file
```

## DAG Schedule

| DAG | Schedule | Duration | Description |
|-----|----------|----------|-------------|
| `daily_price_ingestion` | Mon-Fri 18:00 KST | ~5 min | Fetch daily prices from KRX |
| `indicator_calculation` | Triggered | ~20 min | Calculate 200+ indicators |
| `financial_statements` | Quarterly | ~10 min | Update financial data (F&Guide) |
| `data_quality_monitoring` | Daily 19:00 KST | ~2 min | Validate data quality |

## Prerequisites

### 1. Install Apache Airflow

```bash
# Create virtual environment
python3 -m venv airflow_venv
source airflow_venv/bin/activate

# Install Airflow (adjust version as needed)
pip install "apache-airflow[postgres,celery]==2.8.0" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.0/constraints-3.9.txt"

# Install additional providers
pip install apache-airflow-providers-postgres
```

### 2. Initialize Airflow Database

```bash
# Set Airflow home
export AIRFLOW_HOME=$(pwd)

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 3. Configure Connections

**PostgreSQL Connection (screener_db)**:

```bash
airflow connections add 'screener_db' \
    --conn-type 'postgres' \
    --conn-host 'localhost' \
    --conn-schema 'screener_db' \
    --conn-login 'screener_user' \
    --conn-password 'your_password' \
    --conn-port 5432
```

Or via Airflow UI:
- Go to Admin → Connections
- Add new connection:
  - Conn Id: `screener_db`
  - Conn Type: `Postgres`
  - Host: `localhost`
  - Schema: `screener_db`
  - Login: `screener_user`
  - Password: `your_password`
  - Port: `5432`

## Running the Pipeline

### Start Airflow

```bash
# Terminal 1: Start webserver
airflow webserver --port 8080

# Terminal 2: Start scheduler
airflow scheduler
```

Access Airflow UI at http://localhost:8080

### Trigger DAGs Manually

```bash
# Trigger price ingestion
airflow dags trigger daily_price_ingestion

# Trigger indicator calculation
airflow dags trigger indicator_calculation

# Check DAG run status
airflow dags list-runs -d daily_price_ingestion
```

### Monitor DAG Execution

```bash
# View task logs
airflow tasks logs daily_price_ingestion fetch_krx_prices 2024-11-09

# List all task instances
airflow tasks list daily_price_ingestion

# Check task state
airflow tasks state daily_price_ingestion fetch_krx_prices 2024-11-09
```

## DAG Details

### 1. Daily Price Ingestion DAG

**File**: `dags/daily_price_ingestion_dag.py`

**Flow**:
```
fetch_krx_prices
  ↓
validate_price_data
  ↓
load_prices_to_db
  ↓
check_data_completeness
  ↓
refresh_timescale_aggregates
  ↓
trigger_indicator_calculation
  ↓
log_ingestion_status
```

**Tasks**:
- `fetch_krx_prices`: Fetch OHLCV data from KRX API
- `validate_price_data`: Quality checks (price relationships, non-negative values)
- `load_prices_to_db`: Upsert to `daily_prices` table
- `check_data_completeness`: Ensure ≥95% stocks have data
- `refresh_timescale_aggregates`: Update continuous aggregates
- `trigger_indicator_calculation`: Trigger next DAG
- `log_ingestion_status`: Log run metrics

**Error Handling**:
- Retries: 3 times with 5-minute intervals
- Email alerts on failure
- Partial success if ≥95% data complete

### 2. Indicator Calculation DAG

**File**: `dags/indicator_calculation_dag.py`

**Flow**:
```
calculate_indicators
  ↓
refresh_materialized_views
  ↓
log_calculation_status
```

**Calculations**:
- **Valuation**: PER, PBR, PSR, dividend yield, etc. (15 metrics)
- **Profitability**: ROE, ROA, margins (20 metrics)
- **Growth**: YoY/QoQ growth rates, CAGR (25 metrics)
- **Stability**: Debt ratios, current ratio, F-Score (20 metrics)
- **Technical**: Price momentum, volume surge, MA (30 metrics)
- **Composite**: Quality/Value/Growth scores (10 metrics)

**Performance**:
- Processes ~2,400 stocks in ~20 minutes
- Batch commits every 100 stocks
- Execution timeout: 30 minutes

## Configuration

### Environment Variables

Create `.env` file:

```bash
# Airflow
AIRFLOW__CORE__DAGS_FOLDER=/path/to/dags
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://user:pass@localhost:5432/airflow

# Database
SCREENER_DB_HOST=localhost
SCREENER_DB_PORT=5432
SCREENER_DB_NAME=screener_db
SCREENER_DB_USER=screener_user
SCREENER_DB_PASSWORD=your_password

# API Keys
KRX_API_KEY=your_krx_api_key
FGUIDE_API_KEY=your_fguide_api_key
```

### Airflow Configuration

Key settings in `airflow.cfg`:

```ini
[core]
executor = LocalExecutor
parallelism = 32
max_active_runs_per_dag = 1
load_examples = False

[scheduler]
dag_dir_list_interval = 300
catchup_by_default = False

[webserver]
web_server_port = 8080
secret_key = your_secret_key

[smtp]
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = alerts@screener.kr
smtp_password = your_app_password
smtp_port = 587
smtp_mail_from = alerts@screener.kr
```

## Monitoring & Alerting

### Email Alerts

Configure in each DAG's `default_args`:

```python
default_args = {
    'email': ['data-alerts@screener.kr'],
    'email_on_failure': True,
    'email_on_retry': False,
}
```

### Slack Integration (Optional)

```bash
# Install Slack provider
pip install apache-airflow-providers-slack

# Add Slack connection
airflow connections add 'slack_alerts' \
    --conn-type 'slack' \
    --conn-password 'your_webhook_url'
```

Use in DAG:
```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

send_slack_alert = SlackWebhookOperator(
    task_id='send_slack_alert',
    slack_webhook_conn_id='slack_alerts',
    message='Price ingestion completed: {{ ti.xcom_pull(task_ids="load_prices_to_db") }} records loaded',
)
```

### Metrics

View in Airflow UI:
- DAG run duration
- Task success/failure rates
- SLA misses
- XCom data volumes

## Troubleshooting

### Common Issues

**1. DAG not appearing in UI**

```bash
# Check DAG parsing errors
airflow dags list-import-errors

# Validate DAG syntax
python dags/daily_price_ingestion_dag.py
```

**2. Database connection errors**

```bash
# Test connection
airflow connections test screener_db

# Check PostgreSQL is running
pg_isready -h localhost -p 5432
```

**3. Task stuck in "running" state**

```bash
# Kill zombie tasks
airflow tasks clear daily_price_ingestion -s 2024-11-09 -e 2024-11-09

# Restart scheduler
pkill -f "airflow scheduler"
airflow scheduler
```

**4. Out of memory errors**

- Reduce `parallelism` in airflow.cfg
- Increase system memory allocation
- Use CeleryExecutor with worker pools

### Logs

```bash
# DAG logs
tail -f $AIRFLOW_HOME/logs/scheduler/latest/*.log

# Task logs
tail -f $AIRFLOW_HOME/logs/daily_price_ingestion/fetch_krx_prices/2024-11-09/*.log
```

## Scaling

### Production Deployment

**Use CeleryExecutor for parallel task execution**:

```bash
# Install Celery
pip install "apache-airflow[celery,redis]"

# Start components
airflow webserver
airflow scheduler
airflow celery worker
airflow celery flower  # Monitoring UI
```

**Use Kubernetes for auto-scaling**:

```bash
# Install Kubernetes provider
pip install "apache-airflow[kubernetes]"

# Deploy Airflow on Kubernetes
helm install airflow apache-airflow/airflow -f values.yaml
```

## Best Practices

1. **Idempotency**: All tasks should be idempotent (safe to re-run)
2. **Incremental Processing**: Process only new/changed data
3. **Retry Logic**: Configure appropriate retries and timeouts
4. **Logging**: Use structured logging with context
5. **Testing**: Test DAGs before deploying to production
6. **Documentation**: Keep DAG docstrings updated
7. **Monitoring**: Set up alerts for critical failures
8. **Backfilling**: Use `catchup=False` unless historical runs needed

## Development

### Testing DAGs

```bash
# Unit test individual tasks
python -m pytest tests/dags/test_daily_price_ingestion.py

# Test entire DAG
airflow dags test daily_price_ingestion 2024-11-09
```

### Adding New DAGs

1. Create DAG file in `dags/` directory
2. Test syntax: `python dags/new_dag.py`
3. Trigger test run: `airflow dags test new_dag 2024-11-09`
4. Monitor in UI
5. Enable for production schedule

## References

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [Airflow Providers](https://airflow.apache.org/docs/apache-airflow-providers/)

---

Last Updated: 2025-11-09
