"""Unit tests for screening service"""

from decimal import Decimal
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.exceptions import NotFoundException
from app.schemas.screening import (FilterRange, ScreeningFilters,
                                   ScreeningRequest)
from app.services.screening_service import ScreeningService


class TestScreeningService:
    """Test ScreeningService"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        return Mock()

    @pytest.fixture
    def mock_cache(self):
        """Create mock cache manager"""
        cache = Mock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        return cache

    @pytest.fixture
    def mock_repository(self):
        """Create mock screening repository"""
        repo = Mock()
        repo.screen_stocks = AsyncMock()
        repo.get_screening_templates = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_session, mock_cache):
        """Create service instance with mocks"""
        return ScreeningService(session=mock_session, cache=mock_cache)

    def test_init(self, mock_session, mock_cache):
        """Test service initialization"""
        service = ScreeningService(session=mock_session, cache=mock_cache)
        assert service.session == mock_session
        assert service.cache == mock_cache
        assert service.screening_repo is not None

    def test_build_cache_key(self, service):
        """Test cache key generation with SHA-256 and API version"""
        request = ScreeningRequest(
            filters=ScreeningFilters(
                market="KOSPI",
                per=FilterRange(min=5.0, max=15.0),
            ),
            sort_by="per",
            order="asc",
            page=1,
            per_page=50,
        )

        cache_key = service._build_cache_key(request)

        # Should contain API version, filter hash (16 chars), and pagination params
        assert cache_key.startswith("screening:v1:")
        parts = cache_key.split(":")
        assert len(parts) == 7  # screening:v1:hash:sort:order:page:per_page
        assert len(parts[2]) == 16  # SHA-256 truncated to 16 chars
        assert ":per:asc:1:50" in cache_key

    def test_build_cache_key_deterministic(self, service):
        """Test that same filters produce same cache key"""
        request1 = ScreeningRequest(
            filters=ScreeningFilters(per=FilterRange(min=10.0)),
            sort_by="market_cap",
            page=1,
            per_page=50,
        )

        request2 = ScreeningRequest(
            filters=ScreeningFilters(per=FilterRange(min=10.0)),
            sort_by="market_cap",
            page=1,
            per_page=50,
        )

        key1 = service._build_cache_key(request1)
        key2 = service._build_cache_key(request2)

        assert key1 == key2

    def test_build_cache_key_different_filters(self, service):
        """Test that different filters produce different cache keys"""
        request1 = ScreeningRequest(
            filters=ScreeningFilters(per=FilterRange(min=10.0)),
        )

        request2 = ScreeningRequest(
            filters=ScreeningFilters(per=FilterRange(min=15.0)),
        )

        key1 = service._build_cache_key(request1)
        key2 = service._build_cache_key(request2)

        assert key1 != key2

    def test_build_cache_key_different_pagination(self, service):
        """Test that different pagination produces different cache keys"""
        request1 = ScreeningRequest(page=1, per_page=50)
        request2 = ScreeningRequest(page=2, per_page=50)

        key1 = service._build_cache_key(request1)
        key2 = service._build_cache_key(request2)

        assert key1 != key2

    def test_build_filters_summary_empty(self, service):
        """Test filters summary with no filters"""
        filters = ScreeningFilters()
        summary = service._build_filters_summary(filters)

        assert summary["_count"] == 0

    def test_build_filters_summary_market_all_not_counted(self, service):
        """Test that market='ALL' is not counted as active filter"""
        filters = ScreeningFilters(market="ALL")
        summary = service._build_filters_summary(filters)

        # market="ALL" should not increment count
        assert summary.get("market") == "ALL"
        assert summary["_count"] == 0

    def test_build_filters_summary_market_specific(self, service):
        """Test filters summary with specific market"""
        filters = ScreeningFilters(market="KOSPI")
        summary = service._build_filters_summary(filters)

        assert summary["market"] == "KOSPI"
        assert summary["_count"] == 1

    def test_build_filters_summary_string_filters(self, service):
        """Test filters summary with string filters"""
        filters = ScreeningFilters(
            sector="Technology",
            industry="Software",
        )
        summary = service._build_filters_summary(filters)

        assert summary["sector"] == "Technology"
        assert summary["industry"] == "Software"
        assert summary["_count"] == 2

    def test_build_filters_summary_range_filters(self, service):
        """Test filters summary with range filters"""
        filters = ScreeningFilters(
            per=FilterRange(min=5.0, max=15.0),
            roe=FilterRange(min=10.0),
        )
        summary = service._build_filters_summary(filters)

        assert "per" in summary
        assert summary["per"]["min"] == 5.0
        assert summary["per"]["max"] == 15.0
        assert "roe" in summary
        assert summary["roe"]["min"] == 10.0
        assert summary["_count"] == 2

    def test_build_filters_summary_mixed_filters(self, service):
        """Test filters summary with mixed filter types"""
        filters = ScreeningFilters(
            market="KOSDAQ",
            sector="Healthcare",
            per=FilterRange(min=5.0, max=15.0),
            dividend_yield=FilterRange(min=3.0),
        )
        summary = service._build_filters_summary(filters)

        assert summary["market"] == "KOSDAQ"
        assert summary["sector"] == "Healthcare"
        assert "per" in summary
        assert "dividend_yield" in summary
        assert summary["_count"] == 4

    @pytest.mark.asyncio
    async def test_execute_screening_no_cache(self, service, mock_repository):
        """Test executing screening without cache hit"""
        # Setup mocks
        service.screening_repo = mock_repository
        mock_repository.screen_stocks.return_value = (
            [
                {
                    "code": "005930",
                    "name": "삼성전자",
                    "market": "KOSPI",
                    "current_price": 70000,
                    "per": Decimal("12.5"),
                }
            ],
            1,  # total count
        )

        request = ScreeningRequest(
            filters=ScreeningFilters(market="KOSPI"),
            page=1,
            per_page=50,
        )

        response = await service.execute_screening(request)

        # Verify response
        assert len(response.stocks) == 1
        assert response.stocks[0].code == "005930"
        assert response.meta.total == 1
        assert response.meta.page == 1
        assert response.meta.per_page == 50
        assert response.query_time_ms >= 0

        # Verify cache was set
        service.cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_screening_with_cache_hit(self, service):
        """Test executing screening with cache hit"""
        # Setup cache to return cached response
        cached_data = {
            "stocks": [
                {
                    "code": "005930",
                    "name": "삼성전자",
                    "market": "KOSPI",
                    "current_price": 70000,
                }
            ],
            "meta": {
                "total": 1,
                "page": 1,
                "per_page": 50,
                "total_pages": 1,
            },
            "query_time_ms": 50.0,
            "filters_applied": {},
        }
        service.cache.get = AsyncMock(return_value=cached_data)

        request = ScreeningRequest()

        response = await service.execute_screening(request)

        # Verify response from cache
        assert len(response.stocks) == 1
        assert response.stocks[0].code == "005930"

        # Verify cache.get was called
        service.cache.get.assert_called_once()

        # Cache.set should not be called when cache hit
        service.cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_screening_pagination(self, service, mock_repository):
        """Test screening with pagination"""
        service.screening_repo = mock_repository
        mock_repository.screen_stocks.return_value = ([], 150)

        request = ScreeningRequest(page=2, per_page=50)

        response = await service.execute_screening(request)

        # Verify pagination metadata
        assert response.meta.total == 150
        assert response.meta.page == 2
        assert response.meta.per_page == 50
        assert response.meta.total_pages == 3

        # Verify correct offset was passed to repository
        call_kwargs = mock_repository.screen_stocks.call_args.kwargs
        assert call_kwargs["offset"] == 50  # (page - 1) * per_page
        assert call_kwargs["limit"] == 50

    @pytest.mark.asyncio
    async def test_get_templates_no_cache(self, service, mock_repository):
        """Test getting templates without cache hit"""
        service.screening_repo = mock_repository
        mock_repository.get_screening_templates.return_value = [
            {
                "id": "dividend_stocks",
                "name": "고배당주",
                "description": "High dividend stocks",
                "filters": {"dividend_yield": {"min": 3.0}},
                "sort_by": "dividend_yield",
                "order": "desc",
            }
        ]

        response = await service.get_templates()

        # Verify response
        assert len(response.templates) == 1
        assert response.templates[0].id == "dividend_stocks"
        assert response.templates[0].filters.dividend_yield.min == 3.0

        # Verify cache was set
        service.cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_templates_with_cache_hit(self, service):
        """Test getting templates with cache hit"""
        cached_data = {
            "templates": [
                {
                    "id": "value_stocks",
                    "name": "가치주",
                    "description": "Value stocks",
                    "filters": {"per": {"max": 15.0}},
                    "sort_by": "value_score",
                    "order": "desc",
                }
            ]
        }
        service.cache.get = AsyncMock(return_value=cached_data)

        response = await service.get_templates()

        # Verify response from cache
        assert len(response.templates) == 1
        assert response.templates[0].id == "value_stocks"

        # Cache.set should not be called
        service.cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_apply_template_success(self, service, mock_repository):
        """Test applying a valid template"""
        service.screening_repo = mock_repository

        # Mock get_templates
        mock_repository.get_screening_templates.return_value = [
            {
                "id": "dividend_stocks",
                "name": "고배당주",
                "description": "High dividend stocks",
                "filters": {"dividend_yield": {"min": 3.0}},
                "sort_by": "dividend_yield",
                "order": "desc",
            }
        ]

        # Mock screen_stocks
        mock_repository.screen_stocks.return_value = (
            [
                {
                    "code": "005930",
                    "name": "삼성전자",
                    "market": "KOSPI",
                    "dividend_yield": Decimal("3.5"),
                }
            ],
            1,
        )

        response = await service.apply_template("dividend_stocks", page=1, per_page=50)

        # Verify response
        assert len(response.stocks) == 1
        assert response.stocks[0].code == "005930"

        # Verify screening was called with template filters
        call_kwargs = mock_repository.screen_stocks.call_args.kwargs
        assert call_kwargs["filters"].dividend_yield.min == 3.0
        assert call_kwargs["sort_by"] == "dividend_yield"
        assert call_kwargs["order"] == "desc"

    @pytest.mark.asyncio
    async def test_apply_template_not_found(self, service, mock_repository):
        """Test applying a non-existent template"""
        service.screening_repo = mock_repository
        mock_repository.get_screening_templates.return_value = []

        with pytest.raises(NotFoundException) as exc_info:
            await service.apply_template("non_existent_template")

        assert "Template not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_apply_template_custom_pagination(self, service, mock_repository):
        """Test applying template with custom pagination"""
        service.screening_repo = mock_repository

        mock_repository.get_screening_templates.return_value = [
            {
                "id": "value_stocks",
                "name": "가치주",
                "description": "Value stocks",
                "filters": {"per": {"max": 15.0}},
                "sort_by": "value_score",
                "order": "desc",
            }
        ]

        mock_repository.screen_stocks.return_value = ([], 0)

        response = await service.apply_template("value_stocks", page=2, per_page=100)

        # Verify custom pagination was used
        assert response.meta.page == 2
        assert response.meta.per_page == 100

    @pytest.mark.asyncio
    async def test_invalidate_screening_cache_no_redis(self, service):
        """Test cache invalidation when Redis is not connected"""
        # Redis not connected
        service.cache.redis = None
        deleted = await service.invalidate_screening_cache()
        assert deleted == 0

    @pytest.mark.asyncio
    async def test_invalidate_screening_cache_with_redis(self, service):
        """Test cache invalidation deletes all screening keys"""
        # Mock Redis with SCAN and DELETE
        mock_redis = Mock()
        mock_redis.scan = AsyncMock()
        mock_redis.delete = AsyncMock()

        # Simulate SCAN iterations
        # First iteration: returns cursor=1 and some keys
        # Second iteration: returns cursor=0 (done) and more keys
        mock_redis.scan.side_effect = [
            (1, ["screening:v1:abc123:field:asc:1:50", "screening:v1:def456:field:desc:2:50"]),
            (0, ["screening:v1:ghi789:field:asc:1:100"]),
        ]

        # DELETE returns number of keys deleted
        mock_redis.delete.side_effect = [2, 1]

        service.cache.redis = mock_redis

        deleted = await service.invalidate_screening_cache()

        # Should have deleted 3 keys total (2 + 1)
        assert deleted == 3

        # Verify SCAN was called with correct pattern
        assert mock_redis.scan.call_count == 2
        scan_calls = mock_redis.scan.call_args_list
        assert scan_calls[0][0] == (0,)  # First call with cursor 0
        assert scan_calls[0][1]["match"] == "screening:v1:*"
        assert scan_calls[1][0] == (1,)  # Second call with cursor 1

        # Verify DELETE was called twice
        assert mock_redis.delete.call_count == 2

    @pytest.mark.asyncio
    async def test_invalidate_screening_cache_empty(self, service):
        """Test cache invalidation when no keys match"""
        mock_redis = Mock()
        mock_redis.scan = AsyncMock(return_value=(0, []))
        service.cache.redis = mock_redis

        deleted = await service.invalidate_screening_cache()

        assert deleted == 0
        mock_redis.scan.assert_called_once()
