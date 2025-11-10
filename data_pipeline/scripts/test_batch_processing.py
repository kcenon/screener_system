#!/usr/bin/env python3
"""
Test script for batch processing functionality.

This script tests the new batch processing methods with mock data
to ensure they work correctly before production deployment.
"""

import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kis_api_client import create_client, PriceType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_batch_price_fetching():
    """Test get_current_prices_batch() method"""
    print("\n" + "=" * 80)
    print("TEST 1: Batch Price Fetching")
    print("=" * 80)

    # Test with small batch
    test_codes = ['005930', '000660', '035420', '051910', '035720']

    def progress_callback(completed, total, stock_code):
        print(f"  Progress: {completed}/{total} - {stock_code}")

    with create_client(use_mock=True) as client:
        result = client.get_current_prices_batch(
            stock_codes=test_codes,
            max_workers=3,
            progress_callback=progress_callback
        )

        print(f"\nResults:")
        print(f"  Total: {result['stats']['total']}")
        print(f"  Succeeded: {result['stats']['succeeded']}")
        print(f"  Failed: {result['stats']['failed']}")
        print(f"  Duration: {result['stats']['duration_seconds']}s")
        print(f"  Speed: {result['stats']['stocks_per_second']} stocks/sec")

        # Show sample results
        print(f"\nSample prices:")
        for code, price in list(result['success'].items())[:3]:
            print(f"  {code}: {price.current_price:,.0f} KRW ({price.change_rate:+.2f}%)")

        assert result['stats']['succeeded'] == len(test_codes), "All stocks should succeed with mock data"
        print("\n✓ Batch price fetching test PASSED")


def test_batch_chart_fetching():
    """Test get_chart_data_batch() method"""
    print("\n" + "=" * 80)
    print("TEST 2: Batch Chart Data Fetching")
    print("=" * 80)

    test_codes = ['005930', '000660', '035420']

    with create_client(use_mock=True) as client:
        result = client.get_chart_data_batch(
            stock_codes=test_codes,
            period=PriceType.DAILY,
            count=30,
            max_workers=3
        )

        print(f"\nResults:")
        print(f"  Total: {result['stats']['total']}")
        print(f"  Succeeded: {result['stats']['succeeded']}")
        print(f"  Failed: {result['stats']['failed']}")
        print(f"  Duration: {result['stats']['duration_seconds']}s")
        print(f"  Speed: {result['stats']['stocks_per_second']} stocks/sec")

        # Show sample results
        print(f"\nSample chart data:")
        for code, chart_data in list(result['success'].items())[:2]:
            print(f"  {code}: {len(chart_data)} candles")
            if chart_data:
                latest = chart_data[0]
                print(f"    Latest: {latest.date} - Close={latest.close_price:,.0f} KRW")

        assert result['stats']['succeeded'] == len(test_codes), "All stocks should succeed with mock data"
        print("\n✓ Batch chart fetching test PASSED")


def test_cache_warming():
    """Test warm_cache() method"""
    print("\n" + "=" * 80)
    print("TEST 3: Cache Warming")
    print("=" * 80)

    test_codes = ['005930', '000660']

    with create_client(use_mock=True) as client:
        result = client.warm_cache(
            stock_codes=test_codes,
            data_types=['price', 'chart'],
            max_workers=2
        )

        print(f"\nResults:")
        print(f"  Price data: {result['price']['succeeded']} succeeded, {result['price']['failed']} failed")
        print(f"  Chart data: {result['chart']['succeeded']} succeeded, {result['chart']['failed']} failed")
        print(f"  Total duration: {result['total_duration_seconds']}s")

        assert result['price']['succeeded'] == len(test_codes), "All price warming should succeed"
        assert result['chart']['succeeded'] == len(test_codes), "All chart warming should succeed"
        print("\n✓ Cache warming test PASSED")


def test_large_batch():
    """Test with larger batch to simulate production load"""
    print("\n" + "=" * 80)
    print("TEST 4: Large Batch Processing (100 stocks)")
    print("=" * 80)

    # Generate 100 test stock codes
    test_codes = [f"{str(i).zfill(6)}" for i in range(1, 101)]

    with create_client(use_mock=True) as client:
        result = client.get_current_prices_batch(
            stock_codes=test_codes,
            max_workers=10
        )

        print(f"\nResults:")
        print(f"  Total: {result['stats']['total']}")
        print(f"  Succeeded: {result['stats']['succeeded']}")
        print(f"  Failed: {result['stats']['failed']}")
        print(f"  Duration: {result['stats']['duration_seconds']}s")
        print(f"  Speed: {result['stats']['stocks_per_second']} stocks/sec")

        # Calculate expected performance for 2,400 stocks
        if result['stats']['stocks_per_second'] > 0:
            estimated_2400 = 2400 / result['stats']['stocks_per_second']
            print(f"\nProjected performance for 2,400 stocks:")
            print(f"  Estimated time: {estimated_2400:.1f}s ({estimated_2400/60:.1f} minutes)")

        assert result['stats']['succeeded'] == len(test_codes), "All stocks should succeed with mock data"
        print("\n✓ Large batch test PASSED")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("KIS API Client - Batch Processing Test Suite")
    print("=" * 80)
    print("Testing new batch processing and cache warming features")
    print("Using mock data (no API credentials required)")
    print("=" * 80)

    try:
        test_batch_price_fetching()
        test_batch_chart_fetching()
        test_cache_warming()
        test_large_batch()

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        print("\nBatch processing features are ready for production!")
        print("Key capabilities:")
        print("  ✓ Concurrent batch price fetching")
        print("  ✓ Concurrent batch chart data fetching")
        print("  ✓ Cache warming for frequently accessed stocks")
        print("  ✓ Progress tracking and error handling")
        print("  ✓ Performance metrics and monitoring")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
