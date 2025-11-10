"""Unit tests for screening schemas"""

import pytest
from pydantic import ValidationError

from app.schemas.screening import (FilterRange, ScreenedStock,
                                   ScreeningFilters, ScreeningMetadata,
                                   ScreeningRequest, ScreeningResponse,
                                   ScreeningTemplate, ScreeningTemplateList)


class TestFilterRange:
    """Test FilterRange schema"""

    def test_valid_range(self):
        """Test creating valid range filter"""
        filter_range = FilterRange(min=10.0, max=20.0)
        assert filter_range.min == 10.0
        assert filter_range.max == 20.0

    def test_only_min(self):
        """Test range with only minimum value"""
        filter_range = FilterRange(min=10.0)
        assert filter_range.min == 10.0
        assert filter_range.max is None

    def test_only_max(self):
        """Test range with only maximum value"""
        filter_range = FilterRange(max=20.0)
        assert filter_range.min is None
        assert filter_range.max == 20.0

    def test_negative_value_allowed_for_minus_one(self):
        """Test that -1 is allowed as special case"""
        filter_range = FilterRange(min=-1.0, max=10.0)
        assert filter_range.min == -1.0

    def test_negative_value_disallowed(self):
        """Test that negative values (except -1) are disallowed"""
        with pytest.raises(ValidationError) as exc_info:
            FilterRange(min=-5.0)
        assert "must be non-negative or -1" in str(exc_info.value)

    def test_min_greater_than_max_raises_error(self):
        """Test that min > max raises validation error"""
        filter_range = FilterRange(min=20.0, max=10.0)
        with pytest.raises(ValueError) as exc_info:
            filter_range.validate_range()
        assert "min must be less than or equal to max" in str(exc_info.value)

    def test_min_equal_max_allowed(self):
        """Test that min == max is allowed"""
        filter_range = FilterRange(min=15.0, max=15.0)
        filter_range.validate_range()  # Should not raise


class TestScreeningFilters:
    """Test ScreeningFilters schema"""

    def test_empty_filters(self):
        """Test creating empty filters"""
        filters = ScreeningFilters()
        assert filters.market == "ALL"
        assert filters.sector is None
        assert filters.per is None

    def test_market_filter(self):
        """Test market filter validation"""
        filters = ScreeningFilters(market="KOSPI")
        assert filters.market == "KOSPI"

        filters = ScreeningFilters(market="KOSDAQ")
        assert filters.market == "KOSDAQ"

    def test_invalid_market_raises_error(self):
        """Test that invalid market raises validation error"""
        with pytest.raises(ValidationError):
            ScreeningFilters(market="INVALID")

    def test_valuation_filters(self):
        """Test valuation filter fields"""
        filters = ScreeningFilters(
            per={"min": 5.0, "max": 15.0},
            pbr={"min": 0.5, "max": 1.5},
            dividend_yield={"min": 3.0},
        )
        assert filters.per.min == 5.0
        assert filters.per.max == 15.0
        assert filters.pbr.min == 0.5
        assert filters.dividend_yield.max is None

    def test_profitability_filters(self):
        """Test profitability filter fields"""
        filters = ScreeningFilters(
            roe={"min": 10.0},
            roa={"min": 5.0},
            operating_margin={"min": 15.0},
        )
        assert filters.roe.min == 10.0
        assert filters.roa.min == 5.0
        assert filters.operating_margin.min == 15.0

    def test_growth_filters(self):
        """Test growth filter fields"""
        filters = ScreeningFilters(
            revenue_growth_yoy={"min": 20.0},
            profit_growth_yoy={"min": 10.0},
            eps_growth_yoy={"min": 15.0},
        )
        assert filters.revenue_growth_yoy.min == 20.0
        assert filters.profit_growth_yoy.min == 10.0
        assert filters.eps_growth_yoy.min == 15.0

    def test_score_filters(self):
        """Test composite score filters"""
        filters = ScreeningFilters(
            quality_score={"min": 70.0},
            value_score={"min": 60.0},
            overall_score={"min": 75.0},
        )
        assert filters.quality_score.min == 70.0
        assert filters.value_score.min == 60.0
        assert filters.overall_score.min == 75.0

    def test_string_filters(self):
        """Test string filter fields"""
        filters = ScreeningFilters(
            sector="Technology",
            industry="Software",
        )
        assert filters.sector == "Technology"
        assert filters.industry == "Software"

    def test_filter_range_validation_on_creation(self):
        """Test that invalid ranges are caught during creation"""
        with pytest.raises(ValidationError) as exc_info:
            ScreeningFilters(per={"min": 20.0, "max": 10.0})  # min > max
        assert "min must be less than or equal to max" in str(exc_info.value)


class TestScreeningRequest:
    """Test ScreeningRequest schema"""

    def test_minimal_request(self):
        """Test creating request with defaults"""
        request = ScreeningRequest()
        assert request.filters.market == "ALL"
        assert request.sort_by == "market_cap"
        assert request.order == "desc"
        assert request.page == 1
        assert request.per_page == 50

    def test_custom_sorting(self):
        """Test custom sorting parameters"""
        request = ScreeningRequest(
            sort_by="per",
            order="asc",
        )
        assert request.sort_by == "per"
        assert request.order == "asc"

    def test_custom_pagination(self):
        """Test custom pagination parameters"""
        request = ScreeningRequest(
            page=2,
            per_page=100,
        )
        assert request.page == 2
        assert request.per_page == 100

    def test_invalid_sort_field_raises_error(self):
        """Test that invalid sort field raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            ScreeningRequest(sort_by="invalid_field")
        assert "Invalid sort field" in str(exc_info.value)

    def test_invalid_order_raises_error(self):
        """Test that invalid order raises validation error"""
        with pytest.raises(ValidationError):
            ScreeningRequest(order="invalid")

    def test_page_must_be_positive(self):
        """Test that page must be >= 1"""
        with pytest.raises(ValidationError):
            ScreeningRequest(page=0)

    def test_per_page_limits(self):
        """Test per_page boundaries"""
        # Test minimum
        with pytest.raises(ValidationError):
            ScreeningRequest(per_page=0)

        # Test maximum
        with pytest.raises(ValidationError):
            ScreeningRequest(per_page=201)

        # Test valid boundaries
        request = ScreeningRequest(per_page=1)
        assert request.per_page == 1

        request = ScreeningRequest(per_page=200)
        assert request.per_page == 200

    def test_with_filters(self):
        """Test request with screening filters"""
        request = ScreeningRequest(
            filters=ScreeningFilters(
                market="KOSPI",
                per={"min": 5.0, "max": 15.0},
                roe={"min": 10.0},
            ),
            sort_by="quality_score",
            order="desc",
        )
        assert request.filters.market == "KOSPI"
        assert request.filters.per.min == 5.0
        assert request.filters.roe.min == 10.0
        assert request.sort_by == "quality_score"


class TestScreenedStock:
    """Test ScreenedStock schema"""

    def test_minimal_stock(self):
        """Test creating stock with minimal required fields"""
        stock = ScreenedStock(
            code="005930",
            name="삼성전자",
            market="KOSPI",
        )
        assert stock.code == "005930"
        assert stock.name == "삼성전자"
        assert stock.market == "KOSPI"
        assert stock.name_english is None

    def test_full_stock_data(self):
        """Test creating stock with all fields"""
        from datetime import date
        from decimal import Decimal

        stock = ScreenedStock(
            code="005930",
            name="삼성전자",
            name_english="Samsung Electronics",
            market="KOSPI",
            sector="Technology",
            industry="Semiconductors",
            current_price=70000,
            market_cap=400000000,
            per=Decimal("12.5"),
            pbr=Decimal("1.2"),
            roe=Decimal("8.5"),
            quality_score=Decimal("85.0"),
            last_trade_date=date(2025, 11, 10),
        )
        assert stock.code == "005930"
        assert stock.name_english == "Samsung Electronics"
        assert stock.current_price == 70000
        assert stock.per == Decimal("12.5")
        assert stock.quality_score == Decimal("85.0")

    def test_from_attributes_config(self):
        """Test that from_attributes is enabled for ORM models"""
        assert ScreenedStock.model_config["from_attributes"] is True


class TestScreeningMetadata:
    """Test ScreeningMetadata schema"""

    def test_valid_metadata(self):
        """Test creating valid metadata"""
        metadata = ScreeningMetadata(
            total=150,
            page=2,
            per_page=50,
            total_pages=3,
        )
        assert metadata.total == 150
        assert metadata.page == 2
        assert metadata.per_page == 50
        assert metadata.total_pages == 3

    def test_total_must_be_non_negative(self):
        """Test that total must be >= 0"""
        with pytest.raises(ValidationError):
            ScreeningMetadata(
                total=-1,
                page=1,
                per_page=50,
                total_pages=0,
            )

    def test_page_must_be_positive(self):
        """Test that page must be >= 1"""
        with pytest.raises(ValidationError):
            ScreeningMetadata(
                total=100,
                page=0,
                per_page=50,
                total_pages=2,
            )


class TestScreeningResponse:
    """Test ScreeningResponse schema"""

    def test_valid_response(self):
        """Test creating valid screening response"""
        stocks = [
            ScreenedStock(
                code="005930",
                name="삼성전자",
                market="KOSPI",
            ),
        ]
        metadata = ScreeningMetadata(
            total=1,
            page=1,
            per_page=50,
            total_pages=1,
        )
        response = ScreeningResponse(
            stocks=stocks,
            meta=metadata,
            query_time_ms=125.5,
            filters_applied={"market": "KOSPI"},
        )
        assert len(response.stocks) == 1
        assert response.meta.total == 1
        assert response.query_time_ms == 125.5
        assert response.filters_applied["market"] == "KOSPI"

    def test_empty_results(self):
        """Test response with no results"""
        metadata = ScreeningMetadata(
            total=0,
            page=1,
            per_page=50,
            total_pages=0,
        )
        response = ScreeningResponse(
            stocks=[],
            meta=metadata,
            query_time_ms=50.0,
            filters_applied={},
        )
        assert len(response.stocks) == 0
        assert response.meta.total == 0


class TestScreeningTemplate:
    """Test ScreeningTemplate schema"""

    def test_valid_template(self):
        """Test creating valid screening template"""
        template = ScreeningTemplate(
            id="dividend_stocks",
            name="고배당주",
            description="배당수익률이 높은 우량주 종목",
            filters=ScreeningFilters(
                dividend_yield={"min": 3.0},
                quality_score={"min": 70.0},
            ),
            sort_by="dividend_yield",
            order="desc",
        )
        assert template.id == "dividend_stocks"
        assert template.name == "고배당주"
        assert template.filters.dividend_yield.min == 3.0
        assert template.sort_by == "dividend_yield"

    def test_invalid_template_id(self):
        """Test that template ID must match pattern"""
        with pytest.raises(ValidationError):
            ScreeningTemplate(
                id="Invalid-ID!",  # Contains invalid characters
                name="Test",
                description="Test template",
                filters=ScreeningFilters(),
            )


class TestScreeningTemplateList:
    """Test ScreeningTemplateList schema"""

    def test_template_list(self):
        """Test creating template list"""
        templates = [
            ScreeningTemplate(
                id="dividend_stocks",
                name="고배당주",
                description="배당수익률이 높은 우량주",
                filters=ScreeningFilters(dividend_yield={"min": 3.0}),
            ),
            ScreeningTemplate(
                id="value_stocks",
                name="가치주",
                description="저평가된 우량주",
                filters=ScreeningFilters(per={"max": 15.0}),
            ),
        ]
        template_list = ScreeningTemplateList(templates=templates)
        assert len(template_list.templates) == 2
        assert template_list.templates[0].id == "dividend_stocks"
        assert template_list.templates[1].id == "value_stocks"
