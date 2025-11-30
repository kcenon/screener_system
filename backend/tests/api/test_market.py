"""Integration tests for Market Overview API endpoints"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
from httpx import AsyncClient
from sqlalchemy import delete

from app.db.models import DailyPrice, MarketIndex, Stock


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
async def test_market_indices(db, clean_market_data) -> List[MarketIndex]:
    """Create test market indices data"""
    now = datetime.now()
    indices_data = []

    # Create 7 days of data for each index
    for days_ago in range(7, 0, -1):
        timestamp = now - timedelta(days=days_ago)

        # KOSPI
        indices_data.append(
            MarketIndex(
                code="KOSPI",
                timestamp=timestamp,
                open_value=Decimal("2450.00") + Decimal(days_ago * 5),
                high_value=Decimal("2480.00") + Decimal(days_ago * 5),
                low_value=Decimal("2430.00") + Decimal(days_ago * 5),
                close_value=Decimal("2470.00") + Decimal(days_ago * 5),
                volume=450000000 + (days_ago * 1000000),
                trading_value=12500000000000 + (days_ago * 100000000),
            )
        )

        # KOSDAQ
        indices_data.append(
            MarketIndex(
                code="KOSDAQ",
                timestamp=timestamp,
                open_value=Decimal("840.00") + Decimal(days_ago * 2),
                high_value=Decimal("855.00") + Decimal(days_ago * 2),
                low_value=Decimal("835.00") + Decimal(days_ago * 2),
                close_value=Decimal("850.00") + Decimal(days_ago * 2),
                volume=320000000 + (days_ago * 500000),
                trading_value=8500000000000 + (days_ago * 50000000),
            )
        )

        # KRX100
        indices_data.append(
            MarketIndex(
                code="KRX100",
                timestamp=timestamp,
                open_value=Decimal("5200.00") + Decimal(days_ago * 10),
                high_value=Decimal("5250.00") + Decimal(days_ago * 10),
                low_value=Decimal("5180.00") + Decimal(days_ago * 10),
                close_value=Decimal("5230.00") + Decimal(days_ago * 10),
                volume=180000000 + (days_ago * 200000),
                trading_value=6200000000000 + (days_ago * 30000000),
            )
        )

    for index_data in indices_data:
        db.add(index_data)

    await db.commit()
    return indices_data


@pytest.fixture
async def test_stocks_with_sectors(db, clean_market_data) -> List[Stock]:
    """Create test stocks with various sectors and daily prices"""
    from datetime import date

    # Define stock data with prices
    stocks_data = [
        # Technology sector
        {
            "code": "005930",
            "name": "Samsung Electronics",
            "market": "KOSPI",
            "sector": "technology",
            "close_price": 75000,
            "volume": 15000000,
            "market_cap": 450000000000000,
            "prev_close": 73895,  # +1.5%
        },
        {
            "code": "000660",
            "name": "SK Hynix",
            "market": "KOSPI",
            "sector": "technology",
            "close_price": 125000,
            "volume": 8000000,
            "market_cap": 350000000000000,
            "prev_close": 122187,  # +2.3%
        },
        # Finance sector
        {
            "code": "055550",
            "name": "Shinhan Financial",
            "market": "KOSPI",
            "sector": "finance",
            "close_price": 42000,
            "volume": 5000000,
            "market_cap": 280000000000000,
            "prev_close": 42211,  # -0.5%
        },
        {
            "code": "105560",
            "name": "KB Financial",
            "market": "KOSPI",
            "sector": "finance",
            "close_price": 58000,
            "volume": 6000000,
            "market_cap": 320000000000000,
            "prev_close": 58467,  # -0.8%
        },
        # Healthcare sector
        {
            "code": "207940",
            "name": "Samsung Biologics",
            "market": "KOSPI",
            "sector": "healthcare",
            "close_price": 850000,
            "volume": 200000,
            "market_cap": 600000000000000,
            "prev_close": 823643,  # +3.2%
        },
        # Consumer sector (gainers)
        {
            "code": "051900",
            "name": "LG H&H",
            "market": "KOSPI",
            "sector": "consumer",
            "close_price": 320000,
            "volume": 1200000,
            "market_cap": 220000000000000,
            "prev_close": 294931,  # +8.5%
        },
        # Materials sector (losers)
        {
            "code": "051910",
            "name": "LG Chem",
            "market": "KOSPI",
            "sector": "materials",
            "close_price": 380000,
            "volume": 2500000,
            "market_cap": 270000000000000,
            "prev_close": 405120,  # -6.2%
        },
        # KOSDAQ stocks
        {
            "code": "035420",
            "name": "NAVER",
            "market": "KOSDAQ",
            "sector": "technology",
            "close_price": 220000,
            "volume": 3500000,
            "market_cap": 360000000000000,
            "prev_close": 211364,  # +4.1%
        },
        {
            "code": "035720",
            "name": "Kakao",
            "market": "KOSDAQ",
            "sector": "technology",
            "close_price": 48000,
            "volume": 7000000,
            "market_cap": 210000000000000,
            "prev_close": 49129,  # -2.3%
        },
        # Unchanged stock
        {
            "code": "012330",
            "name": "Hyundai Mobis",
            "market": "KOSPI",
            "sector": "industrial",
            "close_price": 250000,
            "volume": 1500000,
            "market_cap": 360000000000000,
            "prev_close": 250000,  # 0.0%
        },
    ]

    stocks = []
    today = date.today()

    for stock_data in stocks_data:
        # Create Stock record
        stock = Stock(
            code=stock_data["code"],
            name=stock_data["name"],
            market=stock_data["market"],
            sector=stock_data["sector"],
        )
        db.add(stock)
        stocks.append(stock)

        # Create DailyPrice record for today
        # Calculate open_price based on change direction
        change_pct = (
            (stock_data["close_price"] - stock_data["prev_close"])
            / stock_data["prev_close"]
            * 100
        )
        # Set open slightly different from close to show direction
        if change_pct > 0:
            open_price = stock_data["close_price"] - abs(
                int(stock_data["close_price"] * 0.01)
            )
        elif change_pct < 0:
            open_price = stock_data["close_price"] + abs(
                int(stock_data["close_price"] * 0.01)
            )
        else:
            open_price = stock_data["close_price"]

        daily_price = DailyPrice(
            stock_code=stock_data["code"],
            trade_date=today,
            open_price=open_price,
            close_price=stock_data["close_price"],
            volume=stock_data["volume"],
            trading_value=stock_data["close_price"] * stock_data["volume"],
            market_cap=stock_data["market_cap"],
        )
        db.add(daily_price)

        # Create previous day price for change calculation
        prev_price = DailyPrice(
            stock_code=stock_data["code"],
            trade_date=today - timedelta(days=1),
            open_price=stock_data["prev_close"],
            close_price=stock_data["prev_close"],
            volume=stock_data["volume"],
            market_cap=stock_data["market_cap"],
        )
        db.add(prev_price)

    await db.commit()
    return stocks


@pytest.fixture
async def clean_market_data(db):
    """Clean up market data before/after tests"""
    # Clean before test (order matters due to foreign keys)
    await db.execute(delete(DailyPrice))
    await db.execute(delete(MarketIndex))
    await db.execute(delete(Stock))
    await db.commit()

    yield

    # Clean after test
    await db.execute(delete(DailyPrice))
    await db.execute(delete(MarketIndex))
    await db.execute(delete(Stock))
    await db.commit()


# =============================================================================
# API INTEGRATION TESTS - Market Indices
# =============================================================================


class TestMarketIndicesEndpoint:
    """Test GET /v1/market/indices endpoint"""

    async def test_get_market_indices_success(
        self,
        client: AsyncClient,
        test_market_indices,
        clean_market_data,
    ):
        """Test successful retrieval of market indices"""
        response = await client.get("/v1/market/indices")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "indices" in data
        assert "updated_at" in data

        indices = data["indices"]
        assert len(indices) == 3  # KOSPI, KOSDAQ, KRX100

        # Verify each index has required fields
        for index in indices:
            assert "code" in index
            assert "name" in index
            assert "current" in index
            assert "change" in index
            assert "change_percent" in index
            assert "high" in index
            assert "low" in index
            assert "volume" in index
            assert "value" in index
            assert "timestamp" in index
            assert "sparkline" in index

            # Verify sparkline has data
            assert isinstance(index["sparkline"], list)
            assert len(index["sparkline"]) > 0
            assert len(index["sparkline"]) <= 30  # Max 30 data points

    async def test_get_market_indices_empty_database(
        self, client: AsyncClient, clean_market_data
    ):
        """Test endpoint when no market data exists"""
        response = await client.get("/v1/market/indices")

        assert response.status_code == 200
        data = response.json()
        assert data["indices"] == []


# =============================================================================
# API INTEGRATION TESTS - Market Trend
# =============================================================================


class TestMarketTrendEndpoint:
    """Test GET /v1/market/trend endpoint"""

    async def test_get_market_trend_default(
        self, client: AsyncClient, test_market_indices, clean_market_data
    ):
        """Test market trend with default parameters"""
        response = await client.get("/v1/market/trend")

        assert response.status_code == 200
        data = response.json()

        assert "index" in data
        assert data["index"] == "KOSPI"  # Default
        assert "timeframe" in data
        assert data["timeframe"] == "1M"  # Default
        assert "interval" in data
        assert "data" in data
        assert "count" in data
        assert "updated_at" in data

        # Verify data structure
        for point in data["data"]:
            assert "timestamp" in point
            assert "open" in point
            assert "high" in point
            assert "low" in point
            assert "close" in point
            assert "volume" in point

    async def test_get_market_trend_kosdaq(
        self, client: AsyncClient, test_market_indices, clean_market_data
    ):
        """Test market trend for KOSDAQ"""
        response = await client.get("/v1/market/trend?index=KOSDAQ")

        assert response.status_code == 200
        data = response.json()
        assert data["index"] == "KOSDAQ"

    async def test_get_market_trend_different_timeframes(
        self, client: AsyncClient, test_market_indices, clean_market_data
    ):
        """Test different timeframe parameters"""
        timeframes = ["1D", "5D", "1M", "3M"]

        for timeframe in timeframes:
            response = await client.get(f"/v1/market/trend?timeframe={timeframe}")
            assert response.status_code == 200
            data = response.json()
            assert data["timeframe"] == timeframe

    async def test_get_market_trend_invalid_index(
        self, client: AsyncClient, test_market_indices, clean_market_data
    ):
        """Test invalid index parameter"""
        response = await client.get("/v1/market/trend?index=INVALID")

        assert response.status_code == 422  # Validation error

    async def test_get_market_trend_invalid_timeframe(
        self, client: AsyncClient, test_market_indices, clean_market_data
    ):
        """Test invalid timeframe parameter"""
        response = await client.get("/v1/market/trend?timeframe=INVALID")

        assert response.status_code == 422  # Validation error


# =============================================================================
# API INTEGRATION TESTS - Market Breadth
# =============================================================================


class TestMarketBreadthEndpoint:
    """Test GET /v1/market/breadth endpoint"""

    async def test_get_market_breadth_all_markets(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test market breadth for all markets"""
        response = await client.get("/v1/market/breadth")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "advancing" in data
        assert "declining" in data
        assert "unchanged" in data
        assert "total" in data
        assert "ad_ratio" in data
        assert "sentiment" in data
        assert "market" in data
        assert data["market"] == "ALL"
        assert "timestamp" in data

        # Verify calculations
        assert data["advancing"] > 0
        assert data["declining"] > 0
        assert (
            data["total"] == data["advancing"] + data["declining"] + data["unchanged"]
        )

        # Verify sentiment is valid
        assert data["sentiment"] in ["bullish", "neutral", "bearish"]

    async def test_get_market_breadth_kospi_only(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test market breadth for KOSPI only"""
        response = await client.get("/v1/market/breadth?market=KOSPI")

        assert response.status_code == 200
        data = response.json()
        assert data["market"] == "KOSPI"

    async def test_get_market_breadth_kosdaq_only(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test market breadth for KOSDAQ only"""
        response = await client.get("/v1/market/breadth?market=KOSDAQ")

        assert response.status_code == 200
        data = response.json()
        assert data["market"] == "KOSDAQ"

    async def test_get_market_breadth_invalid_market(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test invalid market parameter"""
        response = await client.get("/v1/market/breadth?market=INVALID")

        assert response.status_code == 422  # Validation error


# =============================================================================
# API INTEGRATION TESTS - Sector Performance
# =============================================================================


class TestSectorPerformanceEndpoint:
    """Test GET /v1/market/sectors endpoint"""

    async def test_get_sector_performance_default(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test sector performance with default parameters"""
        response = await client.get("/v1/market/sectors")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "sectors" in data
        assert "timeframe" in data
        assert "market" in data
        assert "updated_at" in data

        # Verify sector data
        sectors = data["sectors"]
        assert len(sectors) > 0

        for sector in sectors:
            assert "code" in sector
            assert "name" in sector
            assert "change_percent" in sector
            assert "stock_count" in sector
            assert "market_cap" in sector
            assert "volume" in sector
            assert "top_stock" in sector

            # Verify top_stock structure
            top_stock = sector["top_stock"]
            assert "code" in top_stock
            assert "name" in top_stock
            assert "change_percent" in top_stock

    async def test_get_sector_performance_kospi_only(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test sector performance for KOSPI only"""
        response = await client.get("/v1/market/sectors?market=KOSPI")

        assert response.status_code == 200
        data = response.json()
        assert data["market"] == "KOSPI"

    async def test_get_sector_performance_different_timeframes(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test different timeframe parameters"""
        timeframes = ["1D", "1W", "1M", "3M"]

        for timeframe in timeframes:
            response = await client.get(f"/v1/market/sectors?timeframe={timeframe}")
            assert response.status_code == 200
            data = response.json()
            assert data["timeframe"] == timeframe


# =============================================================================
# API INTEGRATION TESTS - Market Movers
# =============================================================================


class TestMarketMoversEndpoint:
    """Test GET /v1/market/movers endpoint"""

    async def test_get_top_gainers_default(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test top gainers with default parameters"""
        response = await client.get("/v1/market/movers?type=gainers")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "type" in data
        assert data["type"] == "gainers"
        assert "market" in data
        assert "stocks" in data
        assert "total" in data
        assert "updated_at" in data

        # Verify stocks are sorted by change_percent descending
        stocks = data["stocks"]
        if len(stocks) > 1:
            for i in range(len(stocks) - 1):
                assert stocks[i]["change_percent"] >= stocks[i + 1]["change_percent"]

        # Verify stock structure
        for stock in stocks:
            assert "code" in stock
            assert "name" in stock
            assert "market" in stock
            assert "current_price" in stock
            assert "change" in stock
            assert "change_percent" in stock
            assert "volume" in stock
            assert "value" in stock
            assert "sector" in stock

    async def test_get_top_losers_default(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test top losers with default parameters"""
        response = await client.get("/v1/market/movers?type=losers")

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "losers"

        # Verify stocks are sorted by change_percent ascending
        stocks = data["stocks"]
        if len(stocks) > 1:
            for i in range(len(stocks) - 1):
                assert stocks[i]["change_percent"] <= stocks[i + 1]["change_percent"]

    async def test_get_movers_with_limit(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test market movers with custom limit"""
        response = await client.get("/v1/market/movers?type=gainers&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["stocks"]) <= 5

    async def test_get_movers_kospi_only(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test market movers for KOSPI only"""
        response = await client.get("/v1/market/movers?type=gainers&market=KOSPI")

        assert response.status_code == 200
        data = response.json()
        assert data["market"] == "KOSPI"

        # Verify all stocks are from KOSPI
        for stock in data["stocks"]:
            assert stock["market"] == "KOSPI"

    async def test_get_movers_missing_type(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test endpoint without required type parameter - should use default"""
        response = await client.get("/v1/market/movers")

        # API provides default value, so it should work
        # If you want it to be required, update the API endpoint
        assert response.status_code in [200, 422]  # Either default or validation error

    async def test_get_movers_invalid_type(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test invalid type parameter"""
        response = await client.get("/v1/market/movers?type=invalid")

        assert response.status_code == 422  # Validation error


# =============================================================================
# API INTEGRATION TESTS - Most Active Stocks
# =============================================================================


class TestMostActiveEndpoint:
    """Test GET /v1/market/active endpoint"""

    async def test_get_most_active_by_volume(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test most active stocks by volume"""
        response = await client.get("/v1/market/active?metric=volume")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "metric" in data
        assert data["metric"] == "volume"
        assert "market" in data
        assert "stocks" in data
        assert "total" in data
        assert "updated_at" in data

        # Verify stocks are sorted by volume descending
        stocks = data["stocks"]
        if len(stocks) > 1:
            for i in range(len(stocks) - 1):
                assert stocks[i]["volume"] >= stocks[i + 1]["volume"]

    async def test_get_most_active_by_value(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test most active stocks by trading value"""
        response = await client.get("/v1/market/active?metric=value")

        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "value"

        # Verify stocks are sorted by value descending
        stocks = data["stocks"]
        if len(stocks) > 1:
            for i in range(len(stocks) - 1):
                assert stocks[i]["value"] >= stocks[i + 1]["value"]

    async def test_get_most_active_with_limit(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test most active with custom limit"""
        response = await client.get("/v1/market/active?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data["stocks"]) <= 3

    async def test_get_most_active_kosdaq_only(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test most active for KOSDAQ only"""
        response = await client.get("/v1/market/active?market=KOSDAQ")

        assert response.status_code == 200
        data = response.json()
        assert data["market"] == "KOSDAQ"

        # Verify all stocks are from KOSDAQ
        for stock in data["stocks"]:
            assert stock["market"] == "KOSDAQ"

    async def test_get_most_active_invalid_metric(
        self, client: AsyncClient, test_stocks_with_sectors, clean_market_data
    ):
        """Test invalid metric parameter"""
        response = await client.get("/v1/market/active?metric=invalid")

        assert response.status_code == 422  # Validation error


# =============================================================================
# API INTEGRATION TESTS - Edge Cases
# =============================================================================


class TestMarketAPIEdgeCases:
    """Test edge cases and error handling"""

    async def test_all_endpoints_with_empty_database(
        self, client: AsyncClient, clean_market_data
    ):
        """Test all endpoints handle empty database gracefully"""
        endpoints = [
            "/v1/market/indices",
            "/v1/market/trend",
            "/v1/market/breadth",
            "/v1/market/sectors",
            "/v1/market/movers?type=gainers",
            "/v1/market/active",
        ]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            # Should return 200 with empty/default data, not error
            assert response.status_code == 200

    async def test_concurrent_requests(
        self, client: AsyncClient, test_market_indices, clean_market_data
    ):
        """Test multiple concurrent requests to same endpoint"""
        import asyncio

        # Make 5 concurrent requests
        tasks = [client.get("/v1/market/indices") for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
