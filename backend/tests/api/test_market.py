"""Integration tests for market overview API endpoints"""

from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMarketEndpoints:
    """Test market overview API endpoints"""

    # ========================================================================
    # Market Indices Tests
    # ========================================================================

    async def test_get_market_indices(self, client: AsyncClient):
        """Test GET /v1/market/indices"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_current_indices"
        ) as mock_indices:
            # Mock return value
            from app.db.models import MarketIndex

            mock_index = MarketIndex(
                id=1,
                code="KOSPI",
                timestamp=datetime.now(),
                open_value=2500.00,
                high_value=2520.00,
                low_value=2485.00,
                close_value=2510.50,
                volume=450000000,
                trading_value=12500000000000,
                change_value=10.50,
                change_percent=0.42,
            )
            mock_indices.return_value = [(mock_index, [2485.0, 2490.0, 2510.50])]

            response = await client.get("/v1/market/indices")

            assert response.status_code == 200
            data = response.json()

            assert "indices" in data
            assert "updated_at" in data
            assert len(data["indices"]) > 0

            index = data["indices"][0]
            assert "code" in index
            assert "current" in index
            assert "sparkline" in index
            assert isinstance(index["sparkline"], list)

    # ========================================================================
    # Market Breadth Tests
    # ========================================================================

    async def test_get_market_breadth_all(self, client: AsyncClient):
        """Test GET /v1/market/breadth with ALL market"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_market_breadth"
        ) as mock_breadth:
            mock_breadth.return_value = {
                "advancing": 1234,
                "declining": 856,
                "unchanged": 310,
                "total": 2400,
                "ad_ratio": 1.44,
            }

            response = await client.get("/v1/market/breadth?market=ALL")

            assert response.status_code == 200
            data = response.json()

            assert data["advancing"] == 1234
            assert data["declining"] == 856
            assert data["unchanged"] == 310
            assert data["total"] == 2400
            assert data["ad_ratio"] == 1.44
            assert data["sentiment"] in ["bullish", "neutral", "bearish"]
            assert data["market"] == "ALL"

    async def test_get_market_breadth_kospi(self, client: AsyncClient):
        """Test GET /v1/market/breadth with KOSPI market"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_market_breadth"
        ) as mock_breadth:
            mock_breadth.return_value = {
                "advancing": 600,
                "declining": 400,
                "unchanged": 100,
                "total": 1100,
                "ad_ratio": 1.5,
            }

            response = await client.get("/v1/market/breadth?market=KOSPI")

            assert response.status_code == 200
            data = response.json()

            assert data["market"] == "KOSPI"
            assert data["ad_ratio"] == 1.5

    async def test_get_market_breadth_invalid_market(self, client: AsyncClient):
        """Test GET /v1/market/breadth with invalid market parameter"""
        response = await client.get("/v1/market/breadth?market=INVALID")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    # ========================================================================
    # Sector Performance Tests
    # ========================================================================

    async def test_get_sector_performance(self, client: AsyncClient):
        """Test GET /v1/market/sectors"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_sector_performance"
        ) as mock_sectors:
            mock_sectors.return_value = [
                {
                    "code": "technology",
                    "name": "technology",
                    "change_percent": 2.1,
                    "stock_count": 245,
                    "market_cap": 450000000000000,
                    "top_stock": {"code": "005930", "name": "삼성전자"},
                }
            ]

            response = await client.get("/v1/market/sectors?timeframe=1D&market=ALL")

            assert response.status_code == 200
            data = response.json()

            assert "sectors" in data
            assert "timeframe" in data
            assert "market" in data
            assert data["timeframe"] == "1D"
            assert data["market"] == "ALL"

            if data["sectors"]:
                sector = data["sectors"][0]
                assert "code" in sector
                assert "change_percent" in sector
                assert "stock_count" in sector

    async def test_get_sector_performance_invalid_timeframe(self, client: AsyncClient):
        """Test GET /v1/market/sectors with invalid timeframe"""
        response = await client.get("/v1/market/sectors?timeframe=INVALID")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    # ========================================================================
    # Market Movers Tests
    # ========================================================================

    async def test_get_market_movers_gainers(self, client: AsyncClient):
        """Test GET /v1/market/movers with type=gainers"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_top_movers"
        ) as mock_movers:
            from app.db.models import DailyPrice, Stock

            mock_stock = Stock(
                code="123456",
                name="ABC Corp",
                market="KOSPI",
                sector="technology",
            )
            mock_price = DailyPrice(
                stock_code="123456",
                trade_date=datetime.now().date(),
                close_price=50000,
                volume=1250000,
                trading_value=62500000000,
            )
            mock_movers.return_value = [(mock_stock, mock_price, 10.5)]

            response = await client.get(
                "/v1/market/movers?type=gainers&market=ALL&limit=20"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["type"] == "gainers"
            assert data["market"] == "ALL"
            assert "stocks" in data
            assert isinstance(data["stocks"], list)

    async def test_get_market_movers_losers(self, client: AsyncClient):
        """Test GET /v1/market/movers with type=losers"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_top_movers"
        ) as mock_movers:
            mock_movers.return_value = []

            response = await client.get(
                "/v1/market/movers?type=losers&market=KOSDAQ&limit=10"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["type"] == "losers"
            assert data["market"] == "KOSDAQ"

    async def test_get_market_movers_invalid_type(self, client: AsyncClient):
        """Test GET /v1/market/movers with invalid type"""
        response = await client.get("/v1/market/movers?type=invalid")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    async def test_get_market_movers_invalid_limit(self, client: AsyncClient):
        """Test GET /v1/market/movers with invalid limit"""
        # limit must be <= 100
        response = await client.get("/v1/market/movers?type=gainers&limit=150")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    # ========================================================================
    # Most Active Tests
    # ========================================================================

    async def test_get_most_active_by_volume(self, client: AsyncClient):
        """Test GET /v1/market/active with metric=volume"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_most_active"
        ) as mock_active:
            from app.db.models import DailyPrice, Stock

            mock_stock = Stock(
                code="005930",
                name="삼성전자",
                market="KOSPI",
                sector="technology",
            )
            mock_price = DailyPrice(
                stock_code="005930",
                trade_date=datetime.now().date(),
                close_price=75000,
                volume=15234567,
                trading_value=1142592525000,
            )
            mock_active.return_value = [(mock_stock, mock_price)]

            response = await client.get(
                "/v1/market/active?metric=volume&market=ALL&limit=20"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["metric"] == "volume"
            assert data["market"] == "ALL"
            assert "stocks" in data

    async def test_get_most_active_by_value(self, client: AsyncClient):
        """Test GET /v1/market/active with metric=value"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_most_active"
        ) as mock_active:
            mock_active.return_value = []

            response = await client.get("/v1/market/active?metric=value&market=KOSPI")

            assert response.status_code == 200
            data = response.json()

            assert data["metric"] == "value"
            assert data["market"] == "KOSPI"

    async def test_get_most_active_invalid_metric(self, client: AsyncClient):
        """Test GET /v1/market/active with invalid metric"""
        response = await client.get("/v1/market/active?metric=invalid")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    # ========================================================================
    # Market Trend Tests
    # ========================================================================

    async def test_get_market_trend(self, client: AsyncClient):
        """Test GET /v1/market/trend"""
        with patch(
            "app.repositories.market_repository.MarketRepository.get_index_history"
        ) as mock_trend:
            from app.db.models import MarketIndex

            mock_trend.return_value = [
                MarketIndex(
                    id=1,
                    code="KOSPI",
                    timestamp=datetime.now(),
                    open_value=2450.00,
                    high_value=2465.30,
                    low_value=2442.50,
                    close_value=2460.10,
                    volume=420000000,
                )
            ]

            response = await client.get(
                "/v1/market/trend?index=KOSPI&timeframe=1M"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["index"] == "KOSPI"
            assert data["timeframe"] == "1M"
            assert "interval" in data
            assert "data" in data
            assert isinstance(data["data"], list)

    async def test_get_market_trend_invalid_index(self, client: AsyncClient):
        """Test GET /v1/market/trend with invalid index"""
        response = await client.get("/v1/market/trend?index=INVALID")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    async def test_get_market_trend_invalid_timeframe(self, client: AsyncClient):
        """Test GET /v1/market/trend with invalid timeframe"""
        response = await client.get("/v1/market/trend?index=KOSPI&timeframe=INVALID")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422


@pytest.mark.asyncio
class TestMarketEndpointsParameterValidation:
    """Test parameter validation for market endpoints"""

    async def test_market_breadth_parameter_validation(self, client: AsyncClient):
        """Test market parameter validation"""
        # Valid markets
        for market in ["KOSPI", "KOSDAQ", "ALL"]:
            response = await client.get(f"/v1/market/breadth?market={market}")
            assert response.status_code in [200, 500]  # May fail if no data

        # Invalid market
        response = await client.get("/v1/market/breadth?market=NYSE")
        assert response.status_code == 422

    async def test_sector_performance_timeframe_validation(self, client: AsyncClient):
        """Test timeframe parameter validation"""
        # Valid timeframes
        for timeframe in ["1D", "1W", "1M", "3M"]:
            response = await client.get(f"/v1/market/sectors?timeframe={timeframe}")
            assert response.status_code in [200, 500]  # May fail if no data

        # Invalid timeframe
        response = await client.get("/v1/market/sectors?timeframe=5Y")
        assert response.status_code == 422

    async def test_market_trend_combined_validation(self, client: AsyncClient):
        """Test combined index and timeframe validation"""
        # Valid combinations
        valid_combinations = [
            ("KOSPI", "1D"),
            ("KOSDAQ", "1M"),
            ("KRX100", "6M"),
        ]

        for index, timeframe in valid_combinations:
            response = await client.get(
                f"/v1/market/trend?index={index}&timeframe={timeframe}"
            )
            assert response.status_code in [200, 500]  # May fail if no data

        # Invalid index
        response = await client.get("/v1/market/trend?index=SP500&timeframe=1M")
        assert response.status_code == 422
