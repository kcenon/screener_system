"""Tests for MarketService"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.market_service import MarketService


@pytest.fixture
def mock_session():
    """Create mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_cache():
    """Create mock cache manager"""
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    return cache


@pytest.fixture
def market_service(mock_session, mock_cache):
    """Create MarketService with mocked dependencies"""
    return MarketService(mock_session, mock_cache)


class TestMarketServiceInit:
    """Test MarketService initialization"""

    def test_init_sets_attributes(self, mock_session, mock_cache):
        """Test initialization sets session and cache"""
        service = MarketService(mock_session, mock_cache)
        assert service.session == mock_session
        assert service.cache == mock_cache
        assert service.market_repo is not None


class TestGetMarketIndices:
    """Test get_market_indices method"""

    @pytest.mark.asyncio
    async def test_get_market_indices_from_cache(self, market_service, mock_cache):
        """Test returning cached market indices"""
        cached_data = {
            "indices": [{"code": "KOSPI", "name": "코스피", "current": 2500.0}],
            "updated_at": datetime.now().isoformat(),
        }
        mock_cache.get.return_value = cached_data

        result = await market_service.get_market_indices()

        assert result == cached_data
        mock_cache.get.assert_called_once_with("market:indices:current")

    @pytest.mark.asyncio
    async def test_get_market_indices_from_db(self, market_service, mock_cache):
        """Test fetching market indices from database"""
        mock_cache.get.return_value = None

        mock_index = MagicMock()
        mock_index.code = "KOSPI"
        mock_index.close_value = 2500.0
        mock_index.change_value = 25.0
        mock_index.change_percent = 1.0
        mock_index.high_value = 2550.0
        mock_index.low_value = 2450.0
        mock_index.volume = 1000000
        mock_index.trading_value = 5000000000
        mock_index.timestamp = datetime.now()

        with (
            patch.object(
                market_service.market_repo,
                "get_current_indices",
                new_callable=AsyncMock,
                return_value=[mock_index],
            ),
            patch.object(
                market_service.market_repo,
                "get_index_sparkline",
                new_callable=AsyncMock,
                return_value=[2490, 2500, 2510],
            ),
        ):
            result = await market_service.get_market_indices()

            assert "indices" in result
            assert "updated_at" in result
            assert len(result["indices"]) == 1
            assert result["indices"][0]["code"] == "KOSPI"
            assert result["indices"][0]["name"] == "코스피"
            mock_cache.set.assert_called_once()


class TestGetMarketTrend:
    """Test get_market_trend method"""

    @pytest.mark.asyncio
    async def test_get_market_trend_from_cache(self, market_service, mock_cache):
        """Test returning cached trend data"""
        cached_data = {
            "index": "KOSPI",
            "timeframe": "1M",
            "data": [{"timestamp": "2025-01-01", "close": 2500.0}],
        }
        mock_cache.get.return_value = cached_data

        result = await market_service.get_market_trend("KOSPI", "1M")

        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_market_trend_invalid_index_defaults_to_kospi(
        self, market_service, mock_cache
    ):
        """Test invalid index defaults to KOSPI"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_index_history",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await market_service.get_market_trend("INVALID", "1M")
            assert result["index"] == "KOSPI"

    @pytest.mark.asyncio
    async def test_get_market_trend_different_timeframes(
        self, market_service, mock_cache
    ):
        """Test different timeframes"""
        mock_cache.get.return_value = None

        mock_point = MagicMock()
        mock_point.timestamp = datetime.now()
        mock_point.open_value = 2490.0
        mock_point.high_value = 2520.0
        mock_point.low_value = 2480.0
        mock_point.close_value = 2500.0
        mock_point.volume = 1000000

        with patch.object(
            market_service.market_repo,
            "get_index_history",
            new_callable=AsyncMock,
            return_value=[mock_point],
        ):
            for timeframe in ["1D", "5D", "1M", "3M", "6M", "1Y"]:
                result = await market_service.get_market_trend("KOSPI", timeframe)
                assert result["timeframe"] == timeframe


class TestGetMarketBreadth:
    """Test get_market_breadth method"""

    @pytest.mark.asyncio
    async def test_get_market_breadth_from_cache(self, market_service, mock_cache):
        """Test returning cached breadth data"""
        cached_data = {
            "advancing": 500,
            "declining": 400,
            "unchanged": 100,
            "ad_ratio": 1.25,
            "sentiment": "bullish",
        }
        mock_cache.get.return_value = cached_data

        result = await market_service.get_market_breadth()
        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_market_breadth_from_db(self, market_service, mock_cache):
        """Test fetching breadth data from database"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_market_breadth",
            new_callable=AsyncMock,
            return_value={"advancing": 600, "declining": 400, "unchanged": 100},
        ):
            result = await market_service.get_market_breadth()

            assert result["advancing"] == 600
            assert result["declining"] == 400
            assert result["ad_ratio"] == 1.5
            assert result["sentiment"] == "bullish"

    @pytest.mark.asyncio
    async def test_get_market_breadth_bearish_sentiment(
        self, market_service, mock_cache
    ):
        """Test bearish sentiment calculation"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_market_breadth",
            new_callable=AsyncMock,
            return_value={"advancing": 300, "declining": 600, "unchanged": 100},
        ):
            result = await market_service.get_market_breadth()
            assert result["sentiment"] == "bearish"

    @pytest.mark.asyncio
    async def test_get_market_breadth_neutral_sentiment(
        self, market_service, mock_cache
    ):
        """Test neutral sentiment calculation"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_market_breadth",
            new_callable=AsyncMock,
            return_value={"advancing": 500, "declining": 500, "unchanged": 100},
        ):
            result = await market_service.get_market_breadth()
            assert result["sentiment"] == "neutral"

    @pytest.mark.asyncio
    async def test_get_market_breadth_zero_declining(self, market_service, mock_cache):
        """Test with zero declining stocks (avoid division by zero)"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_market_breadth",
            new_callable=AsyncMock,
            return_value={"advancing": 500, "declining": 0, "unchanged": 100},
        ):
            result = await market_service.get_market_breadth()
            assert result["ad_ratio"] == 0.0

    @pytest.mark.asyncio
    async def test_get_market_breadth_invalid_market(self, market_service, mock_cache):
        """Test invalid market defaults to ALL"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_market_breadth",
            new_callable=AsyncMock,
            return_value={"advancing": 500, "declining": 400, "unchanged": 100},
        ):
            result = await market_service.get_market_breadth("INVALID")
            assert result["market"] == "ALL"


class TestGetSectorPerformance:
    """Test get_sector_performance method"""

    @pytest.mark.asyncio
    async def test_get_sector_performance_from_cache(self, market_service, mock_cache):
        """Test returning cached sector data"""
        cached_data = {
            "sectors": [{"code": "technology", "name": "기술", "change_percent": 1.5}],
            "timeframe": "1D",
        }
        mock_cache.get.return_value = cached_data

        result = await market_service.get_sector_performance()
        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_sector_performance_from_db(self, market_service, mock_cache):
        """Test fetching sector performance from database"""
        mock_cache.get.return_value = None

        sector_data = [
            {
                "code": "technology",
                "change_percent": 1.5,
                "stock_count": 50,
                "market_cap": 1000000000000,
                "volume": 50000000,
            }
        ]

        with (
            patch.object(
                market_service.market_repo,
                "get_sector_performance",
                new_callable=AsyncMock,
                return_value=sector_data,
            ),
            patch.object(
                market_service.market_repo,
                "get_sector_top_stock",
                new_callable=AsyncMock,
                return_value=("005930", "삼성전자", 2.5),
            ),
        ):
            result = await market_service.get_sector_performance()

            assert len(result["sectors"]) == 1
            assert result["sectors"][0]["name"] == "기술"
            assert result["sectors"][0]["top_stock"]["code"] == "005930"

    @pytest.mark.asyncio
    async def test_get_sector_performance_no_top_stock(
        self, market_service, mock_cache
    ):
        """Test sector with no top stock"""
        mock_cache.get.return_value = None

        sector_data = [
            {
                "code": "technology",
                "change_percent": 1.5,
                "stock_count": 50,
                "market_cap": 1000000000000,
                "volume": 50000000,
            }
        ]

        with (
            patch.object(
                market_service.market_repo,
                "get_sector_performance",
                new_callable=AsyncMock,
                return_value=sector_data,
            ),
            patch.object(
                market_service.market_repo,
                "get_sector_top_stock",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            result = await market_service.get_sector_performance()
            assert result["sectors"][0]["top_stock"] is None


class TestGetMarketMovers:
    """Test get_market_movers method"""

    @pytest.mark.asyncio
    async def test_get_market_movers_from_cache(self, market_service, mock_cache):
        """Test returning cached movers data"""
        cached_data = {
            "type": "gainers",
            "stocks": [{"code": "005930", "change_percent": 5.0}],
        }
        mock_cache.get.return_value = cached_data

        result = await market_service.get_market_movers("gainers")
        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_market_movers_gainers(self, market_service, mock_cache):
        """Test fetching top gainers"""
        mock_cache.get.return_value = None

        stocks = [
            {"code": "005930", "name": "삼성전자", "change_percent": 5.0},
            {"code": "000660", "name": "SK하이닉스", "change_percent": 4.5},
        ]

        with patch.object(
            market_service.market_repo,
            "get_top_movers",
            new_callable=AsyncMock,
            return_value=stocks,
        ):
            result = await market_service.get_market_movers("gainers")
            assert result["type"] == "gainers"
            assert len(result["stocks"]) == 2

    @pytest.mark.asyncio
    async def test_get_market_movers_losers(self, market_service, mock_cache):
        """Test fetching top losers"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_top_movers",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await market_service.get_market_movers("losers")
            assert result["type"] == "losers"

    @pytest.mark.asyncio
    async def test_get_market_movers_invalid_type(self, market_service, mock_cache):
        """Test invalid move_type defaults to gainers"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_top_movers",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await market_service.get_market_movers("invalid")
            assert result["type"] == "gainers"

    @pytest.mark.asyncio
    async def test_get_market_movers_limit_bounds(self, market_service, mock_cache):
        """Test limit is bounded between 1 and 100"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_top_movers",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_get_movers:
            # Test upper bound
            await market_service.get_market_movers("gainers", limit=200)
            assert mock_get_movers.call_args[1]["limit"] == 100

            # Test lower bound
            await market_service.get_market_movers("gainers", limit=0)
            assert mock_get_movers.call_args[1]["limit"] == 1


class TestGetMostActive:
    """Test get_most_active method"""

    @pytest.mark.asyncio
    async def test_get_most_active_from_cache(self, market_service, mock_cache):
        """Test returning cached active stocks"""
        cached_data = {
            "metric": "volume",
            "stocks": [{"code": "005930", "volume": 50000000}],
        }
        mock_cache.get.return_value = cached_data

        result = await market_service.get_most_active()
        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_most_active_by_volume(self, market_service, mock_cache):
        """Test fetching most active by volume"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_most_active",
            new_callable=AsyncMock,
            return_value=[{"code": "005930", "volume": 50000000}],
        ):
            result = await market_service.get_most_active("volume")
            assert result["metric"] == "volume"

    @pytest.mark.asyncio
    async def test_get_most_active_by_value(self, market_service, mock_cache):
        """Test fetching most active by trading value"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_most_active",
            new_callable=AsyncMock,
            return_value=[{"code": "005930", "value": 5000000000000}],
        ):
            result = await market_service.get_most_active("value")
            assert result["metric"] == "value"

    @pytest.mark.asyncio
    async def test_get_most_active_invalid_metric(self, market_service, mock_cache):
        """Test invalid metric defaults to volume"""
        mock_cache.get.return_value = None

        with patch.object(
            market_service.market_repo,
            "get_most_active",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await market_service.get_most_active("invalid")
            assert result["metric"] == "volume"


class TestHelperMethods:
    """Test helper methods"""

    def test_calculate_sentiment_bullish(self, market_service):
        """Test bullish sentiment calculation"""
        assert market_service._calculate_sentiment(1.5) == "bullish"
        assert market_service._calculate_sentiment(1.21) == "bullish"

    def test_calculate_sentiment_bearish(self, market_service):
        """Test bearish sentiment calculation"""
        assert market_service._calculate_sentiment(0.5) == "bearish"
        assert market_service._calculate_sentiment(0.79) == "bearish"

    def test_calculate_sentiment_neutral(self, market_service):
        """Test neutral sentiment calculation"""
        assert market_service._calculate_sentiment(1.0) == "neutral"
        assert market_service._calculate_sentiment(0.8) == "neutral"
        assert market_service._calculate_sentiment(1.2) == "neutral"

    def test_get_index_name(self, market_service):
        """Test index name mapping"""
        assert market_service._get_index_name("KOSPI") == "코스피"
        assert market_service._get_index_name("KOSDAQ") == "코스닥"
        assert market_service._get_index_name("KRX100") == "KRX 100"
        assert market_service._get_index_name("UNKNOWN") == "UNKNOWN"

    def test_get_sector_name(self, market_service):
        """Test sector name mapping"""
        assert market_service._get_sector_name("technology") == "기술"
        assert market_service._get_sector_name("finance") == "금융"
        assert market_service._get_sector_name("unknown") == "unknown"
