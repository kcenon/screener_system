"""Unit and integration tests for screening repository"""

from unittest.mock import AsyncMock, Mock

import pytest
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
        """Test adding range filter with minimum value only (parameterized)"""
        conditions = []
        params = {}
        filter_range = FilterRange(min=10.0)

        repository._add_range_filter(conditions, params, "per", filter_range)

        assert len(conditions) == 1
        assert conditions[0] == "per >= :per_min"
        assert params["per_min"] == 10.0

    def test_add_range_filter_with_max_only(self, repository):
        """Test adding range filter with maximum value only (parameterized)"""
        conditions = []
        params = {}
        filter_range = FilterRange(max=20.0)

        repository._add_range_filter(conditions, params, "pbr", filter_range)

        assert len(conditions) == 1
        assert conditions[0] == "pbr <= :pbr_max"
        assert params["pbr_max"] == 20.0

    def test_add_range_filter_with_both_min_and_max(self, repository):
        """Test adding range filter with both min and max (parameterized)"""
        conditions = []
        params = {}
        filter_range = FilterRange(min=5.0, max=15.0)

        repository._add_range_filter(conditions, params, "roe", filter_range)

        assert len(conditions) == 2
        assert "roe >= :roe_min" in conditions
        assert "roe <= :roe_max" in conditions
        assert params["roe_min"] == 5.0
        assert params["roe_max"] == 15.0

    def test_add_range_filter_with_none(self, repository):
        """Test that None filter_range adds nothing"""
        conditions = []
        params = {}

        repository._add_range_filter(conditions, params, "per", None)

        assert len(conditions) == 0
        assert len(params) == 0

    def test_add_range_filter_with_empty_range(self, repository):
        """Test that empty FilterRange adds nothing"""
        conditions = []
        params = {}
        filter_range = FilterRange()  # Both min and max are None

        repository._add_range_filter(conditions, params, "per", filter_range)

        assert len(conditions) == 0
        assert len(params) == 0

    def test_build_where_conditions_empty_filters(self, repository):
        """Test building WHERE conditions with empty filters"""
        filters = ScreeningFilters()

        conditions, params = repository._build_where_conditions(filters)

        # Should have no conditions or parameters
        assert len(conditions) == 0
        assert len(params) == 0

    def test_build_where_conditions_market_filter(self, repository):
        """Test building WHERE conditions with market filter (parameterized)"""
        filters = ScreeningFilters(market="KOSPI")

        conditions, params = repository._build_where_conditions(filters)

        assert "market = :market" in conditions
        assert params["market"] == "KOSPI"

    def test_build_where_conditions_market_all_skipped(self, repository):
        """Test that market='ALL' does not add condition"""
        filters = ScreeningFilters(market="ALL")

        conditions, params = repository._build_where_conditions(filters)

        # No market condition should be added for "ALL"
        market_conditions = [c for c in conditions if "market" in c]
        assert len(market_conditions) == 0

    def test_build_where_conditions_sector_filter(self, repository):
        """Test building WHERE conditions with sector filter (parameterized)"""
        filters = ScreeningFilters(sector="Technology")

        conditions, params = repository._build_where_conditions(filters)

        assert "sector = :sector" in conditions
        assert params["sector"] == "Technology"

    def test_build_where_conditions_sector_parameterized_safe(self, repository):
        """Test that parameterized queries handle special chars safely"""
        # Previously this test checked for manual escaping
        # Now with parameterized queries, the value is passed as-is
        filters = ScreeningFilters(sector="Tech'nology")

        conditions, params = repository._build_where_conditions(filters)

        # Condition uses parameter placeholder
        assert "sector = :sector" in conditions
        # Parameter value contains the single quote (SQLAlchemy will handle escaping)
        assert params["sector"] == "Tech'nology"

    def test_build_where_conditions_industry_filter(self, repository):
        """Test building WHERE conditions with industry filter (parameterized)"""
        filters = ScreeningFilters(industry="Software")

        conditions, params = repository._build_where_conditions(filters)

        assert "industry = :industry" in conditions
        assert params["industry"] == "Software"

    def test_build_where_conditions_valuation_filters(self, repository):
        """Test building WHERE conditions with valuation filters (parameterized)"""
        filters = ScreeningFilters(
            per=FilterRange(min=5.0, max=15.0),
            pbr=FilterRange(max=1.5),
            dividend_yield=FilterRange(min=3.0),
        )

        conditions, params = repository._build_where_conditions(filters)

        assert "per >= :per_min" in conditions
        assert "per <= :per_max" in conditions
        assert "pbr <= :pbr_max" in conditions
        assert "dividend_yield >= :dividend_yield_min" in conditions
        assert params["per_min"] == 5.0
        assert params["per_max"] == 15.0
        assert params["pbr_max"] == 1.5
        assert params["dividend_yield_min"] == 3.0

    def test_build_where_conditions_profitability_filters(self, repository):
        """Test building WHERE conditions with profitability filters (parameterized)"""
        filters = ScreeningFilters(
            roe=FilterRange(min=10.0),
            roa=FilterRange(min=5.0),
            operating_margin=FilterRange(min=15.0),
        )

        conditions, params = repository._build_where_conditions(filters)

        assert "roe >= :roe_min" in conditions
        assert "roa >= :roa_min" in conditions
        assert "operating_margin >= :operating_margin_min" in conditions
        assert params["roe_min"] == 10.0
        assert params["roa_min"] == 5.0
        assert params["operating_margin_min"] == 15.0

    def test_build_where_conditions_growth_filters(self, repository):
        """Test building WHERE conditions with growth filters (parameterized)"""
        filters = ScreeningFilters(
            revenue_growth_yoy=FilterRange(min=20.0),
            profit_growth_yoy=FilterRange(min=10.0),
        )

        conditions, params = repository._build_where_conditions(filters)

        assert "revenue_growth_yoy >= :revenue_growth_yoy_min" in conditions
        assert "profit_growth_yoy >= :profit_growth_yoy_min" in conditions
        assert params["revenue_growth_yoy_min"] == 20.0
        assert params["profit_growth_yoy_min"] == 10.0

    def test_build_where_conditions_stability_filters(self, repository):
        """Test building WHERE conditions with stability filters (parameterized)"""
        filters = ScreeningFilters(
            debt_to_equity=FilterRange(max=1.0),
            current_ratio=FilterRange(min=1.5),
            piotroski_f_score=FilterRange(min=7.0),
        )

        conditions, params = repository._build_where_conditions(filters)

        assert "debt_to_equity <= :debt_to_equity_max" in conditions
        assert "current_ratio >= :current_ratio_min" in conditions
        assert "piotroski_f_score >= :piotroski_f_score_min" in conditions
        assert params["debt_to_equity_max"] == 1.0
        assert params["current_ratio_min"] == 1.5
        assert params["piotroski_f_score_min"] == 7.0

    def test_build_where_conditions_momentum_filters(self, repository):
        """Test building WHERE conditions with price momentum filters (parameterized)"""
        filters = ScreeningFilters(
            price_change_1m=FilterRange(min=10.0),
            price_change_3m=FilterRange(min=20.0),
        )

        conditions, params = repository._build_where_conditions(filters)

        assert "price_change_1m >= :price_change_1m_min" in conditions
        assert "price_change_3m >= :price_change_3m_min" in conditions
        assert params["price_change_1m_min"] == 10.0
        assert params["price_change_3m_min"] == 20.0

    def test_build_where_conditions_score_filters(self, repository):
        """Test building WHERE conditions with composite score filters (parameterized)"""
        filters = ScreeningFilters(
            quality_score=FilterRange(min=70.0),
            value_score=FilterRange(min=60.0),
            overall_score=FilterRange(min=75.0),
        )

        conditions, params = repository._build_where_conditions(filters)

        assert "quality_score >= :quality_score_min" in conditions
        assert "value_score >= :value_score_min" in conditions
        assert "overall_score >= :overall_score_min" in conditions
        assert params["quality_score_min"] == 70.0
        assert params["value_score_min"] == 60.0
        assert params["overall_score_min"] == 75.0

    def test_build_where_conditions_price_and_market_cap_filters(self, repository):
        """Test building WHERE conditions with price and market cap filters (parameterized)"""
        filters = ScreeningFilters(
            current_price=FilterRange(min=10000, max=100000),
            market_cap=FilterRange(min=1000000),
        )

        conditions, params = repository._build_where_conditions(filters)

        assert "current_price >= :current_price_min" in conditions
        assert "current_price <= :current_price_max" in conditions
        assert "market_cap >= :market_cap_min" in conditions
        assert params["current_price_min"] == 10000.0
        assert params["current_price_max"] == 100000.0
        assert params["market_cap_min"] == 1000000.0

    def test_build_where_conditions_multiple_filters_combined(self, repository):
        """Test building WHERE conditions with multiple filter types (parameterized)"""
        filters = ScreeningFilters(
            market="KOSPI",
            sector="Technology",
            per=FilterRange(min=5.0, max=15.0),
            roe=FilterRange(min=10.0),
            quality_score=FilterRange(min=70.0),
        )

        conditions, params = repository._build_where_conditions(filters)

        # Should have all conditions
        assert "market = :market" in conditions
        assert "sector = :sector" in conditions
        assert "per >= :per_min" in conditions
        assert "per <= :per_max" in conditions
        assert "roe >= :roe_min" in conditions
        assert "quality_score >= :quality_score_min" in conditions
        assert len(conditions) >= 6
        # Check parameters
        assert params["market"] == "KOSPI"
        assert params["sector"] == "Technology"
        assert params["per_min"] == 5.0
        assert params["per_max"] == 15.0
        assert params["roe_min"] == 10.0
        assert params["quality_score_min"] == 70.0

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


@pytest.mark.asyncio
class TestSQLInjectionPrevention:
    """Test SQL injection attack prevention

    These tests verify that the repository properly defends against
    SQL injection attacks using allowlist and parameterized queries.
    """

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

    async def test_sort_by_sql_injection_blocked(self, repository):
        """Test that SQL injection in sort_by parameter is blocked"""
        malicious_sort = "1; DROP TABLE stocks; --"
        filters = ScreeningFilters()

        with pytest.raises(ValueError, match="Invalid sort field"):
            await repository.screen_stocks(
                filters=filters,
                sort_by=malicious_sort,
                order="desc",
                offset=0,
                limit=50,
            )

    async def test_sort_by_union_attack_blocked(self, repository):
        """Test that UNION-based SQL injection is blocked"""
        malicious_sort = "market_cap UNION SELECT password FROM users --"
        filters = ScreeningFilters()

        with pytest.raises(ValueError, match="Invalid sort field"):
            await repository.screen_stocks(
                filters=filters,
                sort_by=malicious_sort,
                order="desc",
                offset=0,
                limit=50,
            )

    async def test_sort_by_comment_injection_blocked(self, repository):
        """Test that comment-based SQL injection is blocked"""
        malicious_sort = "market_cap; --"
        filters = ScreeningFilters()

        with pytest.raises(ValueError, match="Invalid sort field"):
            await repository.screen_stocks(
                filters=filters,
                sort_by=malicious_sort,
                order="desc",
                offset=0,
                limit=50,
            )

    def test_market_filter_sql_injection_safe(self, repository):
        """Test that SQL injection in market filter is safely handled

        Parameterized queries should safely handle malicious input without
        executing it as SQL code.
        """
        malicious_market = "'; DROP TABLE stocks; --"
        filters = ScreeningFilters(market=malicious_market)

        conditions, params = repository._build_where_conditions(filters)

        # Should use parameter placeholder
        assert "market = :market" in conditions
        # Parameter value contains the malicious string (will be escaped by SQLAlchemy)
        assert params["market"] == malicious_market

    def test_sector_filter_sql_injection_safe(self, repository):
        """Test that SQL injection in sector filter is safely handled"""
        malicious_sector = "' OR '1'='1"
        filters = ScreeningFilters(sector=malicious_sector)

        conditions, params = repository._build_where_conditions(filters)

        # Should use parameter placeholder
        assert "sector = :sector" in conditions
        # Parameter value contains the malicious string
        assert params["sector"] == malicious_sector

    def test_industry_filter_sql_injection_safe(self, repository):
        """Test that SQL injection in industry filter is safely handled"""
        malicious_industry = "Software' AND (SELECT COUNT(*) FROM users) > 0 --"
        filters = ScreeningFilters(industry=malicious_industry)

        conditions, params = repository._build_where_conditions(filters)

        # Should use parameter placeholder
        assert "industry = :industry" in conditions
        # Parameter value contains the malicious string
        assert params["industry"] == malicious_industry

    def test_numeric_filter_sql_injection_safe(self, repository):
        """Test that numeric filters use parameterized queries

        Even though numeric values are less vulnerable, we still use
        parameterized queries for consistency and defense in depth.
        """
        filters = ScreeningFilters(per=FilterRange(min=5.0, max=15.0))

        conditions, params = repository._build_where_conditions(filters)

        # Should use parameter placeholders
        assert "per >= :per_min" in conditions
        assert "per <= :per_max" in conditions
        # Parameters should be numeric values
        assert params["per_min"] == 5.0
        assert params["per_max"] == 15.0

    def test_allowed_sort_fields_completeness(self, repository):
        """Test that ALLOWED_SORT_FIELDS includes all necessary fields"""
        expected_fields = {
            "code",
            "name",
            "market",
            "current_price",
            "market_cap",
            "per",
            "pbr",
            "pcr",
            "psr",
            "roe",
            "roa",
            "roic",
            "net_margin",
            "operating_margin",
            "gross_margin",
            "revenue_growth_yoy",
            "profit_growth_yoy",
            "eps_growth_yoy",
            "debt_to_equity",
            "current_ratio",
            "altman_z_score",
            "piotroski_f_score",
            "dividend_yield",
            "price_change_1d",
            "price_change_1w",
            "price_change_1m",
            "price_change_3m",
            "price_change_6m",
            "price_change_1y",
            "volume_surge_pct",
            "quality_score",
            "value_score",
            "growth_score",
            "momentum_score",
            "overall_score",
        }

        assert repository.ALLOWED_SORT_FIELDS == expected_fields

    async def test_valid_sort_fields_accepted(self, repository, mock_session):
        """Test that all valid sort fields are accepted"""
        filters = ScreeningFilters()

        # Mock the database execute to return dummy results
        mock_result = Mock()
        mock_result.scalar_one.return_value = 0
        mock_result.mappings.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        # Test a few valid fields
        valid_fields = ["market_cap", "per", "quality_score", "roe"]

        for field in valid_fields:
            # Should not raise any exception
            await repository.screen_stocks(
                filters=filters, sort_by=field, order="desc", offset=0, limit=50
            )

    def test_parameterized_queries_prevent_type_confusion(self, repository):
        """Test that parameterized queries prevent type confusion attacks"""
        # Try to inject SQL through what looks like a numeric value
        filters = ScreeningFilters(
            # FilterRange expects numeric, but let's verify parameter handling
            per=FilterRange(min=5.0, max=15.0)
        )

        conditions, params = repository._build_where_conditions(filters)

        # All parameters should be properly typed
        assert isinstance(params["per_min"], (int, float))
        assert isinstance(params["per_max"], (int, float))
        # And use placeholders in SQL
        assert ":per_min" in str(conditions)
        assert ":per_max" in str(conditions)
