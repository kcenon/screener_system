#!/usr/bin/env python3
"""
Test script for DAG integration with KIS API.

This script verifies:
1. DAG can be imported without errors
2. Data source abstraction layer works correctly
3. Data conversion functions work as expected
4. Mock data can be fetched through the new pipeline

Usage:
    python test_dag_integration.py
"""

import sys
import os
import logging
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test 1: Verify all imports work correctly"""
    logger.info("=" * 70)
    logger.info("TEST 1: Import Verification")
    logger.info("=" * 70)

    try:
        # Test data source imports
        from data_source import (
            DataSourceFactory,
            DataSourceType,
            AbstractDataSource,
            KISDataSource,
            MockDataSource
        )
        logger.info("✓ Data source module imported successfully")

        # Test KIS API client imports
        from kis_api_client import (
            KISAPIClient,
            CurrentPrice,
            OrderBook,
            ChartData,
            StockInfo,
            PriceType
        )
        logger.info("✓ KIS API client module imported successfully")

        # Test KRX client (for comparison)
        from krx_api_client import PriceData
        logger.info("✓ KRX client module imported successfully")

        logger.info("✅ All imports successful\n")
        return True

    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False


def test_data_source_factory():
    """Test 2: Verify DataSourceFactory works"""
    logger.info("=" * 70)
    logger.info("TEST 2: DataSourceFactory Functionality")
    logger.info("=" * 70)

    try:
        from data_source import DataSourceFactory, DataSourceType

        # Test mock data source creation
        with DataSourceFactory.create(DataSourceType.MOCK) as source:
            logger.info(f"✓ Created data source: {type(source).__name__}")

            # Test fetching data
            price = source.get_current_price("005930")
            logger.info(f"✓ Fetched current price: {price.stock_name} = {price.current_price:,} KRW")

            chart = source.get_chart_data("005930", count=3)
            logger.info(f"✓ Fetched {len(chart)} chart data points")

        logger.info("✅ DataSourceFactory works correctly\n")
        return True

    except Exception as e:
        logger.error(f"❌ DataSourceFactory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_conversion():
    """Test 3: Verify chart data to price data conversion"""
    logger.info("=" * 70)
    logger.info("TEST 3: Data Conversion Functions")
    logger.info("=" * 70)

    try:
        from data_source import DataSourceFactory, DataSourceType
        from kis_api_client import PriceType

        # Add DAG directory to path
        dag_path = os.path.join(os.path.dirname(__file__), '..', 'dags')
        sys.path.insert(0, dag_path)

        # Import conversion function
        from daily_price_ingestion_dag import convert_chart_data_to_price_data

        # Fetch mock chart data
        with DataSourceFactory.create(DataSourceType.MOCK) as source:
            chart_data = source.get_chart_data("005930", PriceType.DAILY, count=1)

            # Convert to price_data format
            prices_data = convert_chart_data_to_price_data(chart_data, "005930")

            logger.info(f"✓ Converted {len(chart_data)} chart records to {len(prices_data)} price records")

            # Verify structure
            if prices_data:
                record = prices_data[0]
                required_fields = ['stock_code', 'trade_date', 'close_price', 'volume']
                missing = [f for f in required_fields if f not in record]

                if not missing:
                    logger.info(f"✓ Price record structure is valid")
                    logger.info(f"  Stock: {record['stock_code']}")
                    logger.info(f"  Date: {record['trade_date']}")
                    logger.info(f"  Close: {record['close_price']:,}")
                    logger.info(f"  Volume: {record['volume']:,}")
                else:
                    logger.error(f"❌ Missing fields: {missing}")
                    return False

        logger.info("✅ Data conversion works correctly\n")
        return True

    except Exception as e:
        logger.error(f"❌ Data conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dag_import():
    """Test 4: Verify DAG can be imported (syntax check)"""
    logger.info("=" * 70)
    logger.info("TEST 4: DAG Import Verification")
    logger.info("=" * 70)

    try:
        # Note: This won't fully initialize Airflow, but will catch syntax errors
        dag_path = os.path.join(os.path.dirname(__file__), '..', 'dags')
        sys.path.insert(0, dag_path)

        logger.info("Attempting to import daily_price_ingestion_dag...")

        # This will fail if there are syntax errors or import issues
        import daily_price_ingestion_dag

        logger.info(f"✓ DAG imported successfully")
        logger.info(f"✓ DAG ID: {daily_price_ingestion_dag.dag.dag_id}")
        logger.info(f"✓ DAG tasks: {len(daily_price_ingestion_dag.dag.tasks)}")

        logger.info("✅ DAG import successful\n")
        return True

    except Exception as e:
        logger.error(f"❌ DAG import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_detection():
    """Test 5: Verify environment-based data source selection"""
    logger.info("=" * 70)
    logger.info("TEST 5: Environment Detection")
    logger.info("=" * 70)

    try:
        from data_source import DataSourceFactory

        # Test 1: No environment variables (should use mock)
        logger.info("Testing with no credentials (should use mock)...")
        with DataSourceFactory.create() as source:
            logger.info(f"✓ Auto-detected source: {type(source).__name__}")

        # Test 2: Check current DATA_SOURCE_TYPE
        data_source_type = os.getenv('DATA_SOURCE_TYPE', 'not set')
        logger.info(f"✓ Current DATA_SOURCE_TYPE: {data_source_type}")

        logger.info("✅ Environment detection works correctly\n")
        return True

    except Exception as e:
        logger.error(f"❌ Environment detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("\n" + "=" * 70)
    logger.info("KIS API DAG Integration Test Suite")
    logger.info("=" * 70 + "\n")

    tests = [
        ("Import Verification", test_imports),
        ("DataSourceFactory", test_data_source_factory),
        ("Data Conversion", test_data_conversion),
        ("DAG Import", test_dag_import),
        ("Environment Detection", test_environment_detection),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Unexpected error in {test_name}: {e}")
            results[test_name] = False

    # Print summary
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}  {test_name}")

    logger.info("=" * 70)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 70)

    # Return exit code
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
