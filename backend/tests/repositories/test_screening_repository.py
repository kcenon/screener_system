"""Unit and integration tests for screening repository"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.screening_repository import ScreeningRepository
from app.schemas.screening import FilterRange, ScreeningFilters


class TestScreeningRepository:
    """Test ScreeningRepository"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        session = Mock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance with mock session"""
        return ScreeningRepository(session=mock_session)

    def test_init(self, mock_session):
        """Test repository initialization"""
        repo = ScreeningRepository(session=mock_session)
        assert repo.session == mock_session

    def test_add_range_filter_with_min_only(self, repository):
        """Test adding range filter with minimum value only"""
        conditions = []
        filter_range = FilterRange(min=10.0)

        repository._add_range_filter(conditions, "per", filter_range)

        assert len(conditions) == 1
        assert conditions[0] == "per >= 10.0"

    def test_add_range_filter_with_max_only(self, repository):
        """Test adding range filter with maximum value only"""
        conditions = []
        filter_range = FilterRange(max=20.0)

        repository._add_range_filter(conditions, "pbr", filter_range)

        assert len(conditions) == 1
        assert conditions[0] == "pbr <= 20.0"

    def test_add_range_filter_with_both_min_and_max(self, repository):
        """Test adding range filter with both min and max"""
        conditions = []
        filter_range = FilterRange(min=5.0, max=15.0)

        repository._add_range_filter(conditions, "roe", filter_range)

        assert len(conditions) == 2
        assert "roe >= 5.0" in conditions
        assert "roe <= 15.0" in conditions

    def test_add_range_filter_with_none(self, repository):
        """Test that None filter_range adds nothing"""
        conditions = []

        repository._add_range_filter(conditions, "per", None)

        assert len(conditions) == 0

    def test_add_range_filter_with_empty_range(self, repository):
        """Test that empty FilterRange adds nothing"""
        conditions = []
        filter_range = FilterRange()  # Both min and max are None

        repository._add_range_filter(conditions, "per", filter_range)

        assert len(conditions) == 0

    def test_build_where_conditions_empty_filters(self, repository):
        """Test building WHERE conditions with empty filters"""
        filters = ScreeningFilters()

        conditions = repository._build_where_conditions(filters)

        # Should have at least market filter (default "ALL" should not add condition)
        assert len(conditions) == 0

    def test_build_where_conditions_market_filter(self, repository):
        """Test building WHERE conditions with market filter"""
        filters = ScreeningFilters(market="KOSPI")

        conditions = repository._build_where_conditions(filters)

        assert "market = 'KOSPI'" in conditions

    def test_build_where_conditions_market_all_skipped(self, repository):
        """Test that market='ALL' does not add condition"""
        filters = ScreeningFilters(market="ALL")

        conditions = repository._build_where_conditions(filters)

        # No market condition should be added for "ALL"
        market_conditions = [c for c in conditions if "market" in c]
        assert len(market_conditions) == 0

    def test_build_where_conditions_sector_filter(self, repository):
        """Test building WHERE conditions with sector filter"""
        filters = ScreeningFilters(sector="Technology")

        conditions = repository._build_where_conditions(filters)

        assert "sector = 'Technology'" in conditions

    def test_build_where_conditions_sector_sql_injection_prevention(self, repository):
        """Test that single quotes in sector are escaped"""
        filters = ScreeningFilters(sector="Tech'nology")

        conditions = repository._build_where_conditions(filters)

        # Single quote should be escaped to ''
        assert "sector = 'Tech''nology'" in conditions

    def test_build_where_conditions_industry_filter(self, repository):
        """Test building WHERE conditions with industry filter"""
        filters = ScreeningFilters(industry="Software")

        conditions = repository._build_where_conditions(filters)

        assert "industry = 'Software'" in conditions

    def test_build_where_conditions_valuation_filters(self, repository):
        """Test building WHERE conditions with valuation filters"""
        filters = ScreeningFilters(
            per=FilterRange(min=5.0, max=15.0),
            pbr=FilterRange(max=1.5),
            dividend_yield=FilterRange(min=3.0),
        )

        conditions = repository._build_where_conditions(filters)

        assert "per >= 5.0" in conditions
        assert "per <= 15.0" in conditions
        assert "pbr <= 1.5" in conditions
        assert "dividend_yield >= 3.0" in conditions

    def test_build_where_conditions_profitability_filters(self, repository):
        """Test building WHERE conditions with profitability filters"""
        filters = ScreeningFilters(
            roe=FilterRange(min=10.0),
            roa=FilterRange(min=5.0),
            operating_margin=FilterRange(min=15.0),
        )

        conditions = repository._build_where_conditions(filters)

        assert "roe >= 10.0" in conditions
        assert "roa >= 5.0" in conditions
        assert "operating_margin >= 15.0" in conditions

    def test_build_where_conditions_growth_filters(self, repository):
        """Test building WHERE conditions with growth filters"""
        filters = ScreeningFilters(
            revenue_growth_yoy=FilterRange(min=20.0),
            profit_growth_yoy=FilterRange(min=10.0),
        )

        conditions = repository._build_where_conditions(filters)

        assert "revenue_growth_yoy >= 20.0" in conditions
        assert "profit_growth_yoy >= 10.0" in conditions

    def test_build_where_conditions_stability_filters(self, repository):
        """Test building WHERE conditions with stability filters"""
        filters = ScreeningFilters(
            debt_to_equity=FilterRange(max=1.0),
            current_ratio=FilterRange(min=1.5),
            piotroski_f_score=FilterRange(min=7.0),
        )

        conditions = repository._build_where_conditions(filters)

        assert "debt_to_equity <= 1.0" in conditions
        assert "current_ratio >= 1.5" in conditions
        assert "piotroski_f_score >= 7.0" in conditions

    def test_build_where_conditions_momentum_filters(self, repository):
        """Test building WHERE conditions with price momentum filters"""
        filters = ScreeningFilters(
            price_change_1m=FilterRange(min=10.0),
            price_change_3m=FilterRange(min=20.0),
        )

        conditions = repository._build_where_conditions(filters)

        assert "price_change_1m >= 10.0" in conditions
        assert "price_change_3m >= 20.0" in conditions

    def test_build_where_conditions_score_filters(self, repository):
        """Test building WHERE conditions with composite score filters"""
        filters = ScreeningFilters(
            quality_score=FilterRange(min=70.0),
            value_score=FilterRange(min=60.0),
            overall_score=FilterRange(min=75.0),
        )

        conditions = repository._build_where_conditions(filters)

        assert "quality_score >= 70.0" in conditions
        assert "value_score >= 60.0" in conditions
        assert "overall_score >= 75.0" in conditions

    def test_build_where_conditions_price_and_market_cap_filters(self, repository):
        """Test building WHERE conditions with price and market cap filters"""
        filters = ScreeningFilters(
            current_price=FilterRange(min=10000, max=100000),
            market_cap=FilterRange(min=1000000),
        )

        conditions = repository._build_where_conditions(filters)

        assert "current_price >= 10000.0" in conditions
        assert "current_price <= 100000.0" in conditions
        assert "market_cap >= 1000000.0" in conditions

    def test_build_where_conditions_multiple_filters_combined(self, repository):
        """Test building WHERE conditions with multiple filter types"""
        filters = ScreeningFilters(
            market="KOSPI",
            sector="Technology",
            per=FilterRange(min=5.0, max=15.0),
            roe=FilterRange(min=10.0),
            quality_score=FilterRange(min=70.0),
        )

        conditions = repository._build_where_conditions(filters)

        # Should have all conditions
        assert "market = 'KOSPI'" in conditions
        assert "sector = 'Technology'" in conditions
        assert "per >= 5.0" in conditions
        assert "per <= 15.0" in conditions
        assert "roe >= 10.0" in conditions
        assert "quality_score >= 70.0" in conditions
        assert len(conditions) >= 6

    @pytest.mark.asyncio
    async def test_get_screening_templates(self, repository):
        """Test getting predefined screening templates"""
        templates = await repository.get_screening_templates()

        # Should have 5 predefined templates
        assert len(templates) == 5

        # Check template IDs
        template_ids = [t["id"] for t in templates]
        assert "dividend_stocks" in template_ids
        assert "value_stocks" in template_ids
        assert "growth_stocks" in template_ids
        assert "quality_stocks" in template_ids
        assert "momentum_stocks" in template_ids

    @pytest.mark.asyncio
    async def test_get_screening_templates_structure(self, repository):
        """Test that templates have correct structure"""
        templates = await repository.get_screening_templates()

        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "description" in template
            assert "filters" in template
            assert "sort_by" in template
            assert "order" in template

    @pytest.mark.asyncio
    async def test_get_screening_templates_dividend_stocks(self, repository):
        """Test dividend stocks template content"""
        templates = await repository.get_screening_templates()

        dividend_template = next(t for t in templates if t["id"] == "dividend_stocks")

        assert dividend_template["name"] == "고배당주 (High Dividend)"
        assert dividend_template["filters"]["dividend_yield"]["min"] == 3.0
        assert dividend_template["filters"]["quality_score"]["min"] == 70.0
        assert dividend_template["sort_by"] == "dividend_yield"
        assert dividend_template["order"] == "desc"

    @pytest.mark.asyncio
    async def test_get_screening_templates_value_stocks(self, repository):
        """Test value stocks template content"""
        templates = await repository.get_screening_templates()

        value_template = next(t for t in templates if t["id"] == "value_stocks")

        assert "가치주" in value_template["name"]
        assert value_template["filters"]["per"]["max"] == 15.0
        assert value_template["filters"]["pbr"]["max"] == 1.5
        assert value_template["filters"]["roe"]["min"] == 5.0
        assert value_template["sort_by"] == "value_score"

    @pytest.mark.asyncio
    async def test_get_screening_templates_growth_stocks(self, repository):
        """Test growth stocks template content"""
        templates = await repository.get_screening_templates()

        growth_template = next(t for t in templates if t["id"] == "growth_stocks")

        assert "성장주" in growth_template["name"]
        assert growth_template["filters"]["revenue_growth_yoy"]["min"] == 20.0
        assert growth_template["filters"]["profit_growth_yoy"]["min"] == 10.0
        assert growth_template["sort_by"] == "growth_score"

    @pytest.mark.asyncio
    async def test_get_screening_templates_quality_stocks(self, repository):
        """Test quality stocks template content"""
        templates = await repository.get_screening_templates()

        quality_template = next(t for t in templates if t["id"] == "quality_stocks")

        assert "우량주" in quality_template["name"]
        assert quality_template["filters"]["piotroski_f_score"]["min"] == 7.0
        assert quality_template["filters"]["quality_score"]["min"] == 80.0
        assert quality_template["sort_by"] == "quality_score"

    @pytest.mark.asyncio
    async def test_get_screening_templates_momentum_stocks(self, repository):
        """Test momentum stocks template content"""
        templates = await repository.get_screening_templates()

        momentum_template = next(t for t in templates if t["id"] == "momentum_stocks")

        assert "모멘텀주" in momentum_template["name"]
        assert momentum_template["filters"]["price_change_1m"]["min"] == 10.0
        assert momentum_template["filters"]["price_change_3m"]["min"] == 20.0
        assert momentum_template["sort_by"] == "momentum_score"
