"""Integration tests for screening API endpoints"""

from decimal import Decimal
from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestScreeningEndpoints:
    """Test screening API endpoints"""

    async def test_screen_stocks_minimal_request(self, client: AsyncClient):
        """Test POST /v1/screen with minimal request (defaults)"""
        # Mock the repository to avoid database dependency
        with patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            mock_screen.return_value = (
                [
                    {
                        "code": "005930",
                        "name": "삼성전자",
                        "market": "KOSPI",
                        "current_price": 70000,
                        "market_cap": 400000000,
                    }
                ],
                1,
            )

            response = await client.post("/v1/screen", json={})

            assert response.status_code == 200
            data = response.json()

            assert "stocks" in data
            assert "meta" in data
            assert "query_time_ms" in data
            assert "filters_applied" in data

            assert len(data["stocks"]) == 1
            assert data["stocks"][0]["code"] == "005930"
            assert data["meta"]["total"] == 1
            assert data["meta"]["page"] == 1
            assert data["meta"]["per_page"] == 50

    async def test_screen_stocks_with_filters(self, client: AsyncClient):
        """Test POST /v1/screen with specific filters"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            mock_screen.return_value = ([], 0)

            request_data = {
                "filters": {
                    "market": "KOSPI",
                    "per": {"min": 5.0, "max": 15.0},
                    "roe": {"min": 10.0},
                },
                "sort_by": "quality_score",
                "order": "desc",
                "page": 1,
                "per_page": 50,
            }

            response = await client.post("/v1/screen", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # Verify filters were applied
            filters_applied = data["filters_applied"]
            assert filters_applied["market"] == "KOSPI"
            assert "per" in filters_applied
            assert "roe" in filters_applied

    async def test_screen_stocks_invalid_sort_field(self, client: AsyncClient):
        """Test POST /v1/screen with invalid sort field"""
        request_data = {
            "sort_by": "invalid_field",
        }

        response = await client.post("/v1/screen", json=request_data)

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    async def test_screen_stocks_invalid_pagination(self, client: AsyncClient):
        """Test POST /v1/screen with invalid pagination"""
        # page must be >= 1
        request_data = {"page": 0}
        response = await client.post("/v1/screen", json=request_data)
        assert response.status_code == 422

        # per_page must be <= 200
        request_data = {"per_page": 300}
        response = await client.post("/v1/screen", json=request_data)
        assert response.status_code == 422

    async def test_screen_stocks_custom_pagination(self, client: AsyncClient):
        """Test POST /v1/screen with custom pagination"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            mock_screen.return_value = ([], 150)

            request_data = {
                "page": 2,
                "per_page": 100,
            }

            response = await client.post("/v1/screen", json=request_data)

            assert response.status_code == 200
            data = response.json()

            assert data["meta"]["page"] == 2
            assert data["meta"]["per_page"] == 100
            assert data["meta"]["total"] == 150
            assert data["meta"]["total_pages"] == 2

    async def test_screen_stocks_sorting(self, client: AsyncClient):
        """Test POST /v1/screen with different sorting"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            mock_screen.return_value = ([], 0)

            request_data = {
                "sort_by": "per",
                "order": "asc",
            }

            response = await client.post("/v1/screen", json=request_data)

            assert response.status_code == 200

            # Verify repository was called with correct params
            call_kwargs = mock_screen.call_args.kwargs
            assert call_kwargs["sort_by"] == "per"
            assert call_kwargs["order"] == "asc"

    async def test_screen_stocks_range_filter_validation(self, client: AsyncClient):
        """Test POST /v1/screen with invalid range (min > max)"""
        request_data = {"filters": {"per": {"min": 20.0, "max": 10.0}}}  # min > max

        response = await client.post("/v1/screen", json=request_data)

        # Should return validation error
        assert response.status_code == 422

    async def test_get_screening_templates(self, client: AsyncClient):
        """Test GET /v1/screen/templates"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository"
            ".get_screening_templates"
        ) as mock_templates:
            mock_templates.return_value = [
                {
                    "id": "dividend_stocks",
                    "name": "고배당주",
                    "description": "High dividend stocks",
                    "filters": {"dividend_yield": {"min": 3.0}},
                    "sort_by": "dividend_yield",
                    "order": "desc",
                }
            ]

            response = await client.get("/v1/screen/templates")

            assert response.status_code == 200
            data = response.json()

            assert "templates" in data
            assert len(data["templates"]) == 1
            assert data["templates"][0]["id"] == "dividend_stocks"

    async def test_apply_screening_template(self, client: AsyncClient):
        """Test POST /v1/screen/templates/{template_id}"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository"
            ".get_screening_templates"
        ) as mock_templates, patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            # Mock templates
            mock_templates.return_value = [
                {
                    "id": "dividend_stocks",
                    "name": "고배당주",
                    "description": "High dividend stocks",
                    "filters": {
                        "dividend_yield": {"min": 3.0},
                        "quality_score": {"min": 70.0},
                    },
                    "sort_by": "dividend_yield",
                    "order": "desc",
                }
            ]

            # Mock screening results
            mock_screen.return_value = (
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

            response = await client.post("/v1/screen/templates/dividend_stocks")

            assert response.status_code == 200
            data = response.json()

            assert len(data["stocks"]) == 1
            assert data["stocks"][0]["code"] == "005930"

            # Verify template filters were applied
            call_kwargs = mock_screen.call_args.kwargs
            assert call_kwargs["filters"].dividend_yield.min == 3.0
            assert call_kwargs["filters"].quality_score.min == 70.0
            assert call_kwargs["sort_by"] == "dividend_yield"

    async def test_apply_screening_template_not_found(self, client: AsyncClient):
        """Test POST /v1/screen/templates/{template_id} with non-existent template"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository"
            ".get_screening_templates"
        ) as mock_templates:
            mock_templates.return_value = []

            response = await client.post("/v1/screen/templates/non_existent")

            # Should return 404 Not Found
            assert response.status_code == 404

    async def test_apply_screening_template_custom_pagination(
        self, client: AsyncClient
    ):
        """Test POST /v1/screen/templates/{template_id} with custom pagination"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository"
            ".get_screening_templates"
        ) as mock_templates, patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            mock_templates.return_value = [
                {
                    "id": "value_stocks",
                    "name": "가치주",
                    "description": "Value stocks",
                    "filters": {"per": {"max": 15.0}},
                    "sort_by": "value_score",
                    "order": "desc",
                }
            ]

            mock_screen.return_value = ([], 200)

            response = await client.post(
                "/v1/screen/templates/value_stocks?page=3&per_page=50"
            )

            assert response.status_code == 200
            data = response.json()

            # Verify custom pagination was used
            assert data["meta"]["page"] == 3
            assert data["meta"]["per_page"] == 50

    async def test_screen_stocks_empty_results(self, client: AsyncClient):
        """Test POST /v1/screen returning no results"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            mock_screen.return_value = ([], 0)

            response = await client.post("/v1/screen", json={})

            assert response.status_code == 200
            data = response.json()

            assert len(data["stocks"]) == 0
            assert data["meta"]["total"] == 0
            assert data["meta"]["total_pages"] == 0

    async def test_screen_stocks_all_filter_types(self, client: AsyncClient):
        """Test POST /v1/screen with all types of filters"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            mock_screen.return_value = ([], 0)

            request_data = {
                "filters": {
                    # Market filters
                    "market": "KOSDAQ",
                    "sector": "Technology",
                    "industry": "Software",
                    # Valuation filters
                    "per": {"min": 5.0, "max": 15.0},
                    "pbr": {"max": 1.5},
                    "dividend_yield": {"min": 3.0},
                    # Profitability filters
                    "roe": {"min": 10.0},
                    "roa": {"min": 5.0},
                    # Growth filters
                    "revenue_growth_yoy": {"min": 20.0},
                    # Stability filters
                    "debt_to_equity": {"max": 1.0},
                    "piotroski_f_score": {"min": 7.0},
                    # Momentum filters
                    "price_change_1m": {"min": 10.0},
                    # Score filters
                    "quality_score": {"min": 70.0},
                }
            }

            response = await client.post("/v1/screen", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # Verify all filters were counted
            assert data["filters_applied"]["_count"] >= 10

    async def test_screen_stocks_response_structure(self, client: AsyncClient):
        """Test that response has correct structure and types"""
        with patch(
            "app.repositories.screening_repository.ScreeningRepository.screen_stocks"
        ) as mock_screen:
            from datetime import date

            mock_screen.return_value = (
                [
                    {
                        "code": "005930",
                        "name": "삼성전자",
                        "name_english": "Samsung Electronics",
                        "market": "KOSPI",
                        "sector": "Technology",
                        "industry": "Semiconductors",
                        "last_trade_date": date(2025, 11, 10),
                        "current_price": 70000,
                        "market_cap": 400000000,
                        "per": Decimal("12.5"),
                        "pbr": Decimal("1.2"),
                        "roe": Decimal("8.5"),
                        "quality_score": Decimal("85.0"),
                    }
                ],
                1,
            )

            response = await client.post("/v1/screen", json={})

            assert response.status_code == 200
            data = response.json()

            # Check stocks structure
            stock = data["stocks"][0]
            assert "code" in stock
            assert "name" in stock
            assert "market" in stock
            assert "current_price" in stock

            # Check meta structure
            meta = data["meta"]
            assert "total" in meta
            assert "page" in meta
            assert "per_page" in meta
            assert "total_pages" in meta

            # Check top-level fields
            assert isinstance(data["query_time_ms"], float)
            assert isinstance(data["filters_applied"], dict)
