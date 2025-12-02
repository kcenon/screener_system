"""Unit tests for stock service"""

from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheManager
from app.core.exceptions import NotFoundException
from app.services.stock_service import StockService
from app.db.models import Stock, DailyPrice, CalculatedIndicator
from app.schemas import StockListResponse, StockDetail, StockSearchResponse


class TestStockService:
    """Test StockService"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        return Mock(spec=AsyncSession)

    @pytest.fixture
    def mock_cache(self):
        """Create mock cache manager"""
        cache = Mock(spec=CacheManager)
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        cache.delete = AsyncMock()
        return cache

    @pytest.fixture
    def service(self, mock_session, mock_cache):
        """Create service instance with mocks"""
        return StockService(session=mock_session, cache=mock_cache)

    @pytest.fixture
    def sample_stock(self):
        """Create sample stock object"""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        return Stock(
            code="005930",
            name="삼성전자",
            name_english="Samsung Electronics",
            market="KOSPI",
            sector="전기전자",
            industry="반도체",
            listing_date=date(1975, 6, 11),
            shares_outstanding=5969782550,
            created_at=now,
            updated_at=now,
        )

    @pytest.fixture
    def sample_price(self):
        """Create sample daily price object"""
        return DailyPrice(
            stock_code="005930",
            trade_date=date(2025, 11, 11),
            open_price=70000,
            high_price=71000,
            low_price=69500,
            close_price=70500,
            volume=10000000,
            market_cap=420000000000000,
        )

    @pytest.fixture
    def sample_indicators(self):
        """Create sample calculated indicators object"""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        return CalculatedIndicator(
            stock_code="005930",
            calculation_date=date(2025, 11, 11),
            per=15.5,
            pbr=1.2,
            roe=12.5,
            price_change_1d=1.5,
            created_at=now,
            updated_at=now,
        )

    # ========================================================================
    # list_stocks Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_list_stocks_cache_hit(self, service, mock_cache):
        """Test list_stocks returns cached result if available"""
        # Setup cached response
        cached_response = {
            "items": [],
            "meta": {"total": 0, "page": 1, "per_page": 50, "total_pages": 0},
        }
        mock_cache.get.return_value = cached_response

        # Mock repository to verify it's not called
        service.stock_repo.list_stocks_with_latest_price = AsyncMock()

        # Execute
        result = await service.list_stocks()

        # Assert
        assert isinstance(result, StockListResponse)
        mock_cache.get.assert_called_once()
        # Repository should not be called if cache hit
        service.stock_repo.list_stocks_with_latest_price.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_stocks_cache_miss(
        self, service, mock_cache, sample_stock, sample_price, sample_indicators
    ):
        """Test list_stocks fetches from repository on cache miss"""
        # Setup cache miss
        mock_cache.get.return_value = None

        # Mock repository response
        service.stock_repo.list_stocks_with_latest_price = AsyncMock(
            return_value=([(sample_stock, sample_price, sample_indicators)], 1)
        )

        # Execute
        result = await service.list_stocks()

        # Assert
        assert isinstance(result, StockListResponse)
        assert len(result.items) == 1
        assert result.items[0].code == "005930"
        assert result.meta.total == 1
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_stocks_with_market_filter(
        self, service, mock_cache, sample_stock, sample_price, sample_indicators
    ):
        """Test list_stocks with market filter"""
        # Setup
        mock_cache.get.return_value = None
        service.stock_repo.list_stocks_with_latest_price = AsyncMock(
            return_value=([(sample_stock, sample_price, sample_indicators)], 1)
        )

        # Execute
        result = await service.list_stocks(market="KOSPI")

        # Assert
        assert len(result.items) == 1
        service.stock_repo.list_stocks_with_latest_price.assert_called_once()
        call_args = service.stock_repo.list_stocks_with_latest_price.call_args
        assert call_args.kwargs["market"] == "KOSPI"

    @pytest.mark.asyncio
    async def test_list_stocks_pagination_validation(
        self, service, mock_cache, sample_stock, sample_price, sample_indicators
    ):
        """Test list_stocks validates pagination parameters"""
        # Setup
        mock_cache.get.return_value = None
        service.stock_repo.list_stocks_with_latest_price = AsyncMock(
            return_value=([(sample_stock, sample_price, sample_indicators)], 100)
        )

        # Execute with invalid page (should be clamped to 1)
        result = await service.list_stocks(page=0, per_page=200)

        # Assert
        assert result.meta.page == 1
        assert result.meta.per_page == 100  # Clamped to max 100

    # ========================================================================
    # get_stock_by_code Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_stock_by_code_cache_hit(self, service, mock_cache):
        """Test get_stock_by_code returns cached result if available"""
        # Setup cached response
        cached_detail = {
            "code": "005930",
            "name": "삼성전자",
            "name_english": "Samsung Electronics",
            "market": "KOSPI",
            "sector": "전기전자",
            "industry": "반도체",
            "listing_date": "1975-06-11",
            "delisting_date": None,
            "shares_outstanding": 5969782550,
            "latest_price": None,
            "latest_indicators": None,
            "created_at": "2025-11-11T00:00:00",
            "updated_at": "2025-11-11T00:00:00",
        }
        mock_cache.get.return_value = cached_detail

        # Mock repository to verify it's not called
        service.stock_repo.get_by_code_with_latest = AsyncMock()

        # Execute
        result = await service.get_stock_by_code("005930")

        # Assert
        assert isinstance(result, StockDetail)
        assert result.code == "005930"
        mock_cache.get.assert_called_once()
        service.stock_repo.get_by_code_with_latest.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_stock_by_code_cache_miss(
        self, service, mock_cache, sample_stock, sample_price, sample_indicators
    ):
        """Test get_stock_by_code fetches from repository on cache miss"""
        # Setup cache miss
        mock_cache.get.return_value = None

        # Mock repository response
        service.stock_repo.get_by_code_with_latest = AsyncMock(
            return_value=(sample_stock, sample_price, sample_indicators)
        )

        # Execute
        result = await service.get_stock_by_code("005930")

        # Assert
        assert isinstance(result, StockDetail)
        assert result.code == "005930"
        assert result.name == "삼성전자"
        assert result.latest_price is not None
        assert result.latest_indicators is not None
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_stock_by_code_not_found(self, service, mock_cache):
        """Test get_stock_by_code raises NotFoundException when stock not found"""
        # Setup
        mock_cache.get.return_value = None
        service.stock_repo.get_by_code_with_latest = AsyncMock(return_value=None)

        # Execute and assert
        with pytest.raises(NotFoundException) as exc_info:
            await service.get_stock_by_code("999999")

        assert "Stock 999999 not found" in str(exc_info.value)

    # ========================================================================
    # search_stocks Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_stocks_cache_hit(self, service, mock_cache):
        """Test search_stocks returns cached result if available"""
        # Setup cached response
        cached_search = {"items": [], "total": 0, "query": "삼성"}
        mock_cache.get.return_value = cached_search

        # Mock repository to verify it's not called
        service.stock_repo.search_stocks = AsyncMock()

        # Execute
        result = await service.search_stocks("삼성")

        # Assert
        assert isinstance(result, StockSearchResponse)
        mock_cache.get.assert_called_once()
        service.stock_repo.search_stocks.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_stocks_cache_miss(self, service, mock_cache, sample_stock):
        """Test search_stocks fetches from repository on cache miss"""
        # Setup cache miss
        mock_cache.get.return_value = None

        # Mock repository response
        service.stock_repo.search_stocks = AsyncMock(return_value=[sample_stock])

        # Execute
        result = await service.search_stocks("삼성")

        # Assert
        assert isinstance(result, StockSearchResponse)
        assert len(result.items) == 1
        assert result.items[0].code == "005930"
        assert result.items[0].name == "삼성전자"
        assert result.total == 1
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_stocks_with_market_filter(
        self, service, mock_cache, sample_stock
    ):
        """Test search_stocks with market filter"""
        # Setup
        mock_cache.get.return_value = None
        service.stock_repo.search_stocks = AsyncMock(return_value=[sample_stock])

        # Execute
        result = await service.search_stocks("삼성", market="KOSPI")

        # Assert
        assert len(result.items) == 1
        service.stock_repo.search_stocks.assert_called_once()
        call_args = service.stock_repo.search_stocks.call_args
        assert call_args.args[1] == "KOSPI"

    @pytest.mark.asyncio
    async def test_search_stocks_limit_validation(
        self, service, mock_cache, sample_stock
    ):
        """Test search_stocks validates limit parameter"""
        # Setup
        mock_cache.get.return_value = None
        service.stock_repo.search_stocks = AsyncMock(return_value=[sample_stock])

        # Execute
        await service.search_stocks("삼성", limit=100)

        # Assert
        call_args = service.stock_repo.search_stocks.call_args
        assert call_args.args[2] == 50  # Clamped to max 50

    @pytest.mark.asyncio
    async def test_search_stocks_no_results(self, service, mock_cache):
        """Test search_stocks with no matching results"""
        # Setup
        mock_cache.get.return_value = None
        service.stock_repo.search_stocks = AsyncMock(return_value=[])

        # Execute
        result = await service.search_stocks("없는회사")

        # Assert
        assert isinstance(result, StockSearchResponse)
        assert len(result.items) == 0
        assert result.total == 0

    # ========================================================================
    # Cache Integration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_service_uses_correct_cache_keys(self, service, mock_cache):
        """Test that service uses correct cache key patterns"""
        # Setup
        mock_cache.get.return_value = None
        service.stock_repo.list_stocks_with_latest_price = AsyncMock(
            return_value=([], 0)
        )

        # Execute
        await service.list_stocks(market="KOSPI", sector="IT", page=2, per_page=25)

        # Assert - verify cache key format
        mock_cache.get.assert_called_once()
        cache_key = mock_cache.get.call_args[0][0]
        assert cache_key == "stocks:list:KOSPI:IT:2:25"

    @pytest.mark.asyncio
    async def test_service_caches_with_correct_ttl(
        self, service, mock_cache, sample_stock, sample_price, sample_indicators
    ):
        """Test that service caches data with correct TTL"""
        # Setup
        mock_cache.get.return_value = None
        service.stock_repo.get_by_code_with_latest = AsyncMock(
            return_value=(sample_stock, sample_price, sample_indicators)
        )

        # Execute
        await service.get_stock_by_code("005930")

        # Assert - verify TTL is set correctly
        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args
        assert call_args.kwargs["ttl"] == StockService.STOCK_DETAIL_TTL
