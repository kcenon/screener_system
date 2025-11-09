"""
Daily Price Data Ingestion DAG

This DAG runs every weekday after market close (18:00 KST) to collect:
- Daily stock prices (OHLCV) from KRX
- Market capitalization data
- Trading volume and value

Schedule: Mon-Fri at 18:00 KST (after KOSPI/KOSDAQ market closes at 15:30)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.task_group import TaskGroup

import logging
import os
import sys
import requests
import pandas as pd
from typing import List, Dict

# Add scripts directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from krx_api_client import create_client, PriceData

# Default arguments for the DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['data-alerts@screener.kr'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

# DAG definition
dag = DAG(
    'daily_price_ingestion',
    default_args=default_args,
    description='Ingest daily stock prices from KRX',
    schedule_interval='0 18 * * 1-5',  # Mon-Fri at 18:00 KST
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['daily', 'krx', 'prices', 'critical'],
)


# ============================================================================
# TASK FUNCTIONS
# ============================================================================

def fetch_krx_prices(**context):
    """
    Fetch daily price data from KRX API using KRX API client.

    The client can use either real API data or mock data for testing.
    Set KRX_USE_MOCK=true environment variable to use mock data.
    """
    logger = logging.getLogger(__name__)
    execution_date = context['ds']  # YYYY-MM-DD format

    logger.info(f"Fetching KRX prices for {execution_date}")

    try:
        # Create KRX API client (automatically uses environment configuration)
        with create_client() as client:
            # Fetch daily prices for execution date
            price_objects = client.fetch_daily_prices(date=execution_date)

            # Convert PriceData objects to dictionaries for XCom
            prices_data = [
                {
                    'stock_code': p.stock_code,
                    'trade_date': p.trade_date,
                    'open_price': p.open_price,
                    'high_price': p.high_price,
                    'low_price': p.low_price,
                    'close_price': p.close_price,
                    'volume': p.volume,
                    'trading_value': p.trading_value,
                    'market_cap': p.market_cap
                }
                for p in price_objects
            ]

            logger.info(f"Fetched {len(prices_data)} stock prices from KRX API")

    except Exception as e:
        logger.error(f"Failed to fetch KRX prices: {e}")
        raise

    # Push data to XCom for next task
    context['task_instance'].xcom_push(key='prices_data', value=prices_data)

    logger.info(f"Successfully processed {len(prices_data)} stock prices")
    return len(prices_data)


def validate_price_data(**context):
    """
    Validate fetched price data for quality and completeness.
    """
    logger = logging.getLogger(__name__)
    ti = context['task_instance']
    prices_data = ti.xcom_pull(task_ids='fetch_krx_prices', key='prices_data')

    if not prices_data:
        raise ValueError("No price data received")

    # Validation checks
    total_stocks = len(prices_data)
    invalid_records = []

    for record in prices_data:
        # Check required fields
        required_fields = ['stock_code', 'trade_date', 'close_price', 'volume']
        missing_fields = [f for f in required_fields if f not in record or record[f] is None]

        if missing_fields:
            invalid_records.append({
                'stock_code': record.get('stock_code', 'UNKNOWN'),
                'error': f"Missing fields: {missing_fields}"
            })
            continue

        # Validate price relationships: high >= low, close within [low, high]
        if record.get('high_price') and record.get('low_price'):
            if record['high_price'] < record['low_price']:
                invalid_records.append({
                    'stock_code': record['stock_code'],
                    'error': f"High price {record['high_price']} < Low price {record['low_price']}"
                })

        # Validate positive values
        if record['close_price'] <= 0 or record['volume'] < 0:
            invalid_records.append({
                'stock_code': record['stock_code'],
                'error': "Invalid price or volume (must be positive)"
            })

    # Log validation results
    valid_count = total_stocks - len(invalid_records)
    logger.info(f"Validation: {valid_count}/{total_stocks} records valid")

    if invalid_records:
        logger.warning(f"Invalid records: {invalid_records[:10]}")  # Log first 10

    # Fail if >5% of records are invalid
    if len(invalid_records) / total_stocks > 0.05:
        raise ValueError(f"Too many invalid records: {len(invalid_records)}/{total_stocks}")

    # Filter out invalid records and push to XCom
    valid_data = [r for r in prices_data if r['stock_code'] not in
                  [inv['stock_code'] for inv in invalid_records]]

    ti.xcom_push(key='valid_prices', value=valid_data)
    return valid_count


def load_prices_to_db(**context):
    """
    Load validated price data to PostgreSQL database.
    """
    logger = logging.getLogger(__name__)
    ti = context['task_instance']
    valid_prices = ti.xcom_pull(task_ids='validate_price_data', key='valid_prices')

    if not valid_prices:
        logger.warning("No valid price data to load")
        return 0

    # Get PostgreSQL connection
    pg_hook = PostgresHook(postgres_conn_id='screener_db')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    inserted_count = 0
    updated_count = 0

    try:
        for record in valid_prices:
            # Upsert (INSERT ... ON CONFLICT UPDATE)
            cursor.execute("""
                INSERT INTO daily_prices (
                    stock_code, trade_date, open_price, high_price, low_price,
                    close_price, volume, trading_value, market_cap
                ) VALUES (
                    %(stock_code)s, %(trade_date)s, %(open_price)s, %(high_price)s,
                    %(low_price)s, %(close_price)s, %(volume)s, %(trading_value)s,
                    %(market_cap)s
                )
                ON CONFLICT (stock_code, trade_date)
                DO UPDATE SET
                    open_price = EXCLUDED.open_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price,
                    close_price = EXCLUDED.close_price,
                    volume = EXCLUDED.volume,
                    trading_value = EXCLUDED.trading_value,
                    market_cap = EXCLUDED.market_cap
                RETURNING (xmax = 0) AS inserted
            """, record)

            result = cursor.fetchone()
            if result and result[0]:
                inserted_count += 1
            else:
                updated_count += 1

        conn.commit()

    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to load prices to database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

    logger.info(f"Loaded {inserted_count} new records, updated {updated_count} records")
    return inserted_count + updated_count


def check_data_completeness(**context):
    """
    Verify that all active stocks have price data for the execution date.
    """
    logger = logging.getLogger(__name__)
    execution_date = context['ds']

    pg_hook = PostgresHook(postgres_conn_id='screener_db')

    # Count active stocks (not delisted)
    active_stocks_count = pg_hook.get_first(
        "SELECT COUNT(*) FROM stocks WHERE delisting_date IS NULL"
    )[0]

    # Count stocks with prices for execution date
    prices_count = pg_hook.get_first(
        "SELECT COUNT(*) FROM daily_prices WHERE trade_date = %s",
        parameters=(execution_date,)
    )[0]

    missing_count = active_stocks_count - prices_count
    completeness_pct = (prices_count / active_stocks_count * 100) if active_stocks_count > 0 else 0

    logger.info(f"Data completeness: {prices_count}/{active_stocks_count} ({completeness_pct:.1f}%)")
    logger.info(f"Missing prices for {missing_count} stocks")

    # Alert if < 95% complete
    if completeness_pct < 95:
        logger.error(f"Data completeness below threshold: {completeness_pct:.1f}%")
        raise ValueError(f"Incomplete data: only {completeness_pct:.1f}% of stocks have prices")

    return completeness_pct


def log_ingestion_status(**context):
    """
    Log ingestion run status to data_ingestion_log table.
    """
    logger = logging.getLogger(__name__)
    ti = context['task_instance']
    execution_date = context['ds']

    # Collect metrics from previous tasks
    fetched_count = ti.xcom_pull(task_ids='fetch_krx_prices') or 0
    valid_count = ti.xcom_pull(task_ids='validate_price_data') or 0
    loaded_count = ti.xcom_pull(task_ids='load_prices_to_db') or 0
    completeness = ti.xcom_pull(task_ids='check_data_completeness') or 0

    pg_hook = PostgresHook(postgres_conn_id='screener_db')

    # Determine status
    status = 'success' if completeness >= 95 else 'partial'

    pg_hook.run("""
        INSERT INTO data_ingestion_log (
            source, data_type, records_processed, records_failed,
            status, started_at, completed_at
        ) VALUES (
            'krx', 'daily_prices', %s, %s, %s, %s, NOW()
        )
    """, parameters=(
        loaded_count,
        fetched_count - valid_count,
        status,
        context['execution_date']
    ))

    logger.info(f"Logged ingestion status: {status}")


# ============================================================================
# TASK DEFINITIONS
# ============================================================================

# Task 1: Fetch prices from KRX
fetch_prices = PythonOperator(
    task_id='fetch_krx_prices',
    python_callable=fetch_krx_prices,
    provide_context=True,
    dag=dag,
)

# Task 2: Validate data quality
validate_data = PythonOperator(
    task_id='validate_price_data',
    python_callable=validate_price_data,
    provide_context=True,
    dag=dag,
)

# Task 3: Load to database
load_to_db = PythonOperator(
    task_id='load_prices_to_db',
    python_callable=load_prices_to_db,
    provide_context=True,
    dag=dag,
)

# Task 4: Check completeness
check_completeness = PythonOperator(
    task_id='check_data_completeness',
    python_callable=check_data_completeness,
    provide_context=True,
    dag=dag,
)

# Task 5: Refresh TimescaleDB continuous aggregates
refresh_aggregates = PostgresOperator(
    task_id='refresh_timescale_aggregates',
    postgres_conn_id='screener_db',
    sql="""
        REFRESH MATERIALIZED VIEW CONCURRENTLY daily_prices_weekly;
        REFRESH MATERIALIZED VIEW CONCURRENTLY daily_prices_monthly;
    """,
    dag=dag,
)

# Task 6: Log status
log_status = PythonOperator(
    task_id='log_ingestion_status',
    python_callable=log_ingestion_status,
    provide_context=True,
    trigger_rule='all_done',  # Run even if previous tasks failed
    dag=dag,
)

# Task 7: Trigger indicator calculation DAG
trigger_indicator_calc = BashOperator(
    task_id='trigger_indicator_calculation',
    bash_command='airflow dags trigger indicator_calculation',
    dag=dag,
)

# ============================================================================
# TASK DEPENDENCIES
# ============================================================================

fetch_prices >> validate_data >> load_to_db >> check_completeness
check_completeness >> refresh_aggregates >> trigger_indicator_calc
[check_completeness, trigger_indicator_calc] >> log_status
