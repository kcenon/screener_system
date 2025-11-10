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

# Import both KRX client and data source abstraction layer
from krx_api_client import create_client as create_krx_client, PriceData
from data_source import DataSourceFactory, DataSourceType, ChartData
from kis_api_client import PriceType

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
# HELPER FUNCTIONS
# ============================================================================

def convert_chart_data_to_price_data(
    chart_data_list: List[ChartData],
    stock_code: str
) -> List[Dict]:
    """
    Convert KIS ChartData objects to price_data format.

    Args:
        chart_data_list: List of ChartData from KIS API
        stock_code: 6-digit stock code

    Returns:
        List of price dictionaries compatible with DAG pipeline
    """
    prices_data = []

    for chart in chart_data_list:
        prices_data.append({
            'stock_code': stock_code,
            'trade_date': chart.date,
            'open_price': chart.open_price,
            'high_price': chart.high_price,
            'low_price': chart.low_price,
            'close_price': chart.close_price,
            'volume': chart.volume,
            'trading_value': chart.trading_value if hasattr(chart, 'trading_value') else None,
            'market_cap': None  # KIS API doesn't provide market cap in chart data
        })

    return prices_data


def get_all_stock_codes(**context) -> List[str]:
    """
    Fetch list of all active stock codes from database.

    Returns:
        List of stock codes (6-digit strings)
    """
    logger = logging.getLogger(__name__)
    pg_hook = PostgresHook(postgres_conn_id='screener_db')

    # Query active stocks (not delisted)
    result = pg_hook.get_records(
        "SELECT stock_code FROM stocks WHERE delisting_date IS NULL ORDER BY stock_code"
    )

    stock_codes = [row[0] for row in result]
    logger.info(f"Found {len(stock_codes)} active stocks")

    return stock_codes


# ============================================================================
# TASK FUNCTIONS
# ============================================================================

def fetch_stock_prices(**context):
    """
    Fetch daily price data using configured data source.

    Supports multiple data sources via DataSourceFactory:
    - KIS API: Korea Investment & Securities (production)
    - KRX API: Korea Exchange (fallback)
    - Mock: Test data for development

    Data source selection:
    1. Environment variable DATA_SOURCE_TYPE (kis/krx/mock)
    2. Auto-detection based on available credentials
    3. Default: mock data
    """
    logger = logging.getLogger(__name__)
    execution_date = context['ds']  # YYYY-MM-DD format

    # Determine data source type
    source_type_str = os.getenv('DATA_SOURCE_TYPE', '').lower()
    source_type = None

    if source_type_str == 'kis':
        source_type = DataSourceType.KIS
        logger.info("Using KIS API data source")
    elif source_type_str == 'krx':
        source_type = DataSourceType.KRX
        logger.info("Using KRX API data source")
    elif source_type_str == 'mock':
        source_type = DataSourceType.MOCK
        logger.info("Using Mock data source")
    else:
        logger.info("Auto-detecting data source from environment")

    try:
        # Use DataSourceFactory if using KIS or Mock
        if source_type in [DataSourceType.KIS, DataSourceType.MOCK, None]:
            prices_data = fetch_prices_with_data_source(
                execution_date, source_type, context
            )
        else:  # KRX (legacy path)
            prices_data = fetch_prices_with_krx(execution_date, context)

        # Push data to XCom for next task
        context['task_instance'].xcom_push(key='prices_data', value=prices_data)

        logger.info(f"Successfully fetched {len(prices_data)} stock prices")
        return len(prices_data)

    except Exception as e:
        logger.error(f"Failed to fetch stock prices: {e}")
        raise


def fetch_prices_with_data_source(
    execution_date: str,
    source_type: Optional[DataSourceType],
    context: Dict
) -> List[Dict]:
    """
    Fetch prices using DataSourceFactory (KIS or Mock).

    Args:
        execution_date: Trade date in YYYY-MM-DD format
        source_type: Type of data source (None = auto-detect)
        context: Airflow context

    Returns:
        List of price dictionaries
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching prices for {execution_date} using data source abstraction")

    # Get list of all stock codes
    stock_codes = get_all_stock_codes(**context)

    if not stock_codes:
        logger.warning("No active stock codes found")
        return []

    all_prices = []
    failed_stocks = []

    with DataSourceFactory.create(source_type) as data_source:
        logger.info(f"Created data source: {type(data_source).__name__}")

        # Fetch historical data for each stock
        # Note: KIS API doesn't support batch queries, so we fetch one by one
        for idx, stock_code in enumerate(stock_codes):
            try:
                # Fetch daily chart data (last 1 day)
                chart_data = data_source.get_chart_data(
                    stock_code=stock_code,
                    period=PriceType.DAILY,
                    count=1  # Just today's data
                )

                if not chart_data:
                    logger.warning(f"No data for {stock_code}")
                    continue

                # Convert to price_data format
                prices = convert_chart_data_to_price_data(chart_data, stock_code)
                all_prices.extend(prices)

                # Log progress every 100 stocks
                if (idx + 1) % 100 == 0:
                    logger.info(f"Progress: {idx + 1}/{len(stock_codes)} stocks")

            except Exception as e:
                logger.warning(f"Failed to fetch data for {stock_code}: {e}")
                failed_stocks.append(stock_code)
                continue

    # Log summary
    logger.info(f"Fetched {len(all_prices)} price records for {len(stock_codes) - len(failed_stocks)} stocks")

    if failed_stocks:
        logger.warning(f"Failed to fetch {len(failed_stocks)} stocks: {failed_stocks[:10]}")

    return all_prices


def fetch_prices_with_krx(execution_date: str, context: Dict) -> List[Dict]:
    """
    Fetch prices using KRX API client (legacy path).

    Args:
        execution_date: Trade date in YYYY-MM-DD format
        context: Airflow context

    Returns:
        List of price dictionaries
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching KRX prices for {execution_date}")

    # Create KRX API client (automatically uses environment configuration)
    with create_krx_client() as client:
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
        return prices_data


def fetch_krx_prices(**context):
    """
    [DEPRECATED] Legacy function for KRX API.

    Use fetch_stock_prices() instead, which supports multiple data sources.
    This function is kept for backward compatibility.
    """
    logger = logging.getLogger(__name__)
    logger.warning("fetch_krx_prices is deprecated. Use fetch_stock_prices instead.")

    # Delegate to new implementation
    return fetch_stock_prices(**context)


def validate_price_data(**context):
    """
    Validate fetched price data for quality and completeness.

    Enhanced validation with:
    - Data source detection and logging
    - Comprehensive validation rules
    - Detailed error categorization
    - Performance metrics tracking
    """
    logger = logging.getLogger(__name__)
    ti = context['task_instance']
    execution_date = context['ds']

    # Get data from XCom
    prices_data = ti.xcom_pull(task_ids='fetch_krx_prices', key='prices_data')

    if not prices_data:
        raise ValueError("No price data received from fetch task")

    # Log data source information
    data_source_type = os.getenv('DATA_SOURCE_TYPE', 'auto-detect')
    logger.info(f"Validating price data from source: {data_source_type}")
    logger.info(f"Execution date: {execution_date}")

    # Start validation
    start_time = time.time()
    total_stocks = len(prices_data)
    invalid_records = []
    validation_warnings = []

    # Categorize errors
    error_categories = {
        'missing_fields': [],
        'invalid_price_relationship': [],
        'negative_values': [],
        'missing_market_cap': [],
        'data_quality': []
    }

    for record in prices_data:
        stock_code = record.get('stock_code', 'UNKNOWN')

        # Check required fields
        required_fields = ['stock_code', 'trade_date', 'close_price', 'volume']
        missing_fields = [f for f in required_fields if f not in record or record[f] is None]

        if missing_fields:
            error_categories['missing_fields'].append(stock_code)
            invalid_records.append({
                'stock_code': stock_code,
                'error': f"Missing fields: {missing_fields}"
            })
            continue

        # Validate price relationships: high >= low
        if record.get('high_price') and record.get('low_price'):
            if record['high_price'] < record['low_price']:
                error_categories['invalid_price_relationship'].append(stock_code)
                invalid_records.append({
                    'stock_code': stock_code,
                    'error': f"High price {record['high_price']} < Low price {record['low_price']}"
                })

        # Validate positive values
        if record.get('close_price') and (record['close_price'] <= 0 or record['volume'] < 0):
            error_categories['negative_values'].append(stock_code)
            invalid_records.append({
                'stock_code': stock_code,
                'error': "Invalid price or volume (must be positive)"
            })

        # Warning: missing market cap (non-critical for KIS data)
        if record.get('market_cap') is None:
            error_categories['missing_market_cap'].append(stock_code)
            # This is just a warning, not an error

    # Calculate validation metrics
    validation_time = time.time() - start_time
    valid_count = total_stocks - len(invalid_records)
    validity_rate = (valid_count / total_stocks * 100) if total_stocks > 0 else 0

    # Log validation results
    logger.info("=" * 70)
    logger.info(f"Validation Summary (completed in {validation_time:.2f}s)")
    logger.info("=" * 70)
    logger.info(f"Total records: {total_stocks}")
    logger.info(f"Valid records: {valid_count} ({validity_rate:.2f}%)")
    logger.info(f"Invalid records: {len(invalid_records)}")

    # Log error categories
    if error_categories['missing_fields']:
        logger.warning(f"Missing fields: {len(error_categories['missing_fields'])} stocks")
    if error_categories['invalid_price_relationship']:
        logger.warning(f"Invalid price relationships: {len(error_categories['invalid_price_relationship'])} stocks")
    if error_categories['negative_values']:
        logger.error(f"Negative values: {len(error_categories['negative_values'])} stocks")
    if error_categories['missing_market_cap']:
        logger.info(f"Missing market cap: {len(error_categories['missing_market_cap'])} stocks (expected for KIS data)")

    # Log specific invalid records (first 10)
    if invalid_records:
        logger.warning("Sample invalid records:")
        for inv_record in invalid_records[:10]:
            logger.warning(f"  {inv_record['stock_code']}: {inv_record['error']}")
        if len(invalid_records) > 10:
            logger.warning(f"  ... and {len(invalid_records) - 10} more")

    # Fail if >5% of records are invalid
    if len(invalid_records) / total_stocks > 0.05:
        logger.error(f"VALIDATION FAILED: Too many invalid records ({validity_rate:.2f}% valid)")
        raise ValueError(f"Too many invalid records: {len(invalid_records)}/{total_stocks} ({100-validity_rate:.2f}% invalid)")

    # Filter out invalid records
    invalid_stock_codes = {inv['stock_code'] for inv in invalid_records}
    valid_data = [r for r in prices_data if r['stock_code'] not in invalid_stock_codes]

    # Push to XCom
    ti.xcom_push(key='valid_prices', value=valid_data)

    # Log metrics for monitoring
    logger.info("=" * 70)
    logger.info("Validation Metrics:")
    logger.info(f"  Processing time: {validation_time:.2f}s")
    logger.info(f"  Records/second: {total_stocks / validation_time:.0f}")
    logger.info(f"  Validity rate: {validity_rate:.2f}%")
    logger.info("=" * 70)

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
