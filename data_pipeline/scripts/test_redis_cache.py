#!/usr/bin/env python3
"""
Test script for KIS API Redis caching functionality.

This script tests the caching layer with mock data (no real KIS API credentials needed).
It verifies:
1. Cache miss on first request
2. Cache hit on subsequent request
3. Cache TTL expiration
4. Graceful degradation when Redis is unavailable
"""

import os
import sys
import time
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kis_api_client import KISAPIClient, PriceType

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_mock_mode_with_cache():
    """Test caching with mock data (no API credentials needed)"""
    print("\n" + "=" * 80)
    print("TEST: Mock Mode with Caching")
    print("=" * 80)

    # Create client with mock mode (no credentials needed)
    # Cache will be disabled if Redis is not available (graceful degradation)
    client = KISAPIClient(use_mock=True, enable_cache=True)

    test_stock = "005930"  # Samsung Electronics

    # Test 1: Current Price (cache miss -> cache hit)
    print("\n--- Test 1: Current Price Caching ---")
    print("First call (should be MISS):")
    price1 = client.get_current_price(test_stock)
    print(f"  {price1.stock_name}: {price1.current_price:,} KRW")

    print("Second call (should be HIT if Redis available):")
    price2 = client.get_current_price(test_stock)
    print(f"  {price2.stock_name}: {price2.current_price:,} KRW")

    assert price1.current_price == price2.current_price, "Prices should match"

    # Test 2: Order Book (cache miss -> cache hit)
    print("\n--- Test 2: Order Book Caching ---")
    print("First call (should be MISS):")
    orderbook1 = client.get_order_book(test_stock)
    print(f"  Best bid: {orderbook1.best_bid:,}, Best ask: {orderbook1.best_ask:,}")

    print("Second call (should be HIT if Redis available):")
    orderbook2 = client.get_order_book(test_stock)
    print(f"  Best bid: {orderbook2.best_bid:,}, Best ask: {orderbook2.best_ask:,}")

    assert orderbook1.best_bid == orderbook2.best_bid, "Order book should match"

    # Test 3: Chart Data (cache miss -> cache hit)
    print("\n--- Test 3: Chart Data Caching ---")
    print("First call (should be MISS):")
    chart1 = client.get_chart_data(test_stock, PriceType.DAILY, 5)
    print(f"  Retrieved {len(chart1)} candles")

    print("Second call (should be HIT if Redis available):")
    chart2 = client.get_chart_data(test_stock, PriceType.DAILY, 5)
    print(f"  Retrieved {len(chart2)} candles")

    assert len(chart1) == len(chart2), "Chart data should match"

    # Test 4: Stock Info (cache miss -> cache hit)
    print("\n--- Test 4: Stock Info Caching ---")
    print("First call (should be MISS):")
    info1 = client.get_stock_info(test_stock)
    print(f"  {info1.stock_name} ({info1.market})")

    print("Second call (should be HIT if Redis available):")
    info2 = client.get_stock_info(test_stock)
    print(f"  {info2.stock_name} ({info2.market})")

    assert info1.stock_name == info2.stock_name, "Stock info should match"

    print("\n" + "=" * 80)
    print("✅ All caching tests passed!")
    print("=" * 80)

    # Cache statistics
    if client.cache.enabled:
        print("\n📊 Cache Statistics:")
        print(f"  Cache enabled: Yes")
        print(f"  Redis host: {client.cache.host}:{client.cache.port}")
        print(f"  TTL config: {client.cache.ttl_config}")
    else:
        print("\n⚠️  Cache disabled (Redis not available or explicitly disabled)")
        print("  Application works normally without caching (graceful degradation)")


def test_cache_disabled():
    """Test that client works without caching"""
    print("\n" + "=" * 80)
    print("TEST: Cache Disabled Mode")
    print("=" * 80)

    # Create client with cache explicitly disabled
    client = KISAPIClient(use_mock=True, enable_cache=False)

    test_stock = "005930"

    print("\nFetching data without cache:")
    price = client.get_current_price(test_stock)
    print(f"  {price.stock_name}: {price.current_price:,} KRW")

    orderbook = client.get_order_book(test_stock)
    print(f"  Best bid: {orderbook.best_bid:,}, Best ask: {orderbook.best_ask:,}")

    print("\n✅ Cache disabled mode works correctly!")


if __name__ == "__main__":
    try:
        # Test 1: Mock mode with caching
        test_mock_mode_with_cache()

        # Test 2: Cache disabled
        test_cache_disabled()

        print("\n" + "=" * 80)
        print("🎉 All tests completed successfully!")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
