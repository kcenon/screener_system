"""Integration tests for stock API endpoints"""

from datetime import date, datetime, timedelta
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.daily_price import DailyPrice
from app.db.models.financial_statement import FinancialStatement
from app.db.models.stock import Stock


@pytest_asyncio.fixture
async def sample_stocks(db: AsyncSession) -> list[Stock]:
    """Create sample stocks for testing"""
    stocks = [
        Stock(
            code="005930",
            name="삼성전자",
            name_english="Samsung Electronics",
            market="KOSPI",
            sector="Technology",
            industry="Semiconductors",
            listing_date=date(1975, 6, 11),
            shares_outstanding=5969782550,
        ),
        Stock(
            code="000660",
            name="SK하이닉스",
            name_english="SK Hynix",
            market="KOSPI",
            sector="Technology",
            industry="Semiconductors",
            listing_date=date(1996, 12, 26),
            shares_outstanding=728002365,
        ),
        Stock(
            code="035420",
            name="NAVER",
            name_english="NAVER Corporation",
            market="KOSPI",
            sector="Technology",
            industry="Internet Software/Services",
            listing_date=date(2002, 10, 29),
            shares_outstanding=164263395,
        ),
        Stock(
            code="051910",
            name="LG화학",
            name_english="LG Chem",
            market="KOSPI",
            sector="Materials",
            industry="Chemicals",
            listing_date=date(2001, 4, 25),
            shares_outstanding=70592343,
        ),
        Stock(
            code="035720",
            name="카카오",
            name_english="Kakao Corp",
            market="KOSDAQ",
            sector="Technology",
            industry="Internet Software/Services",
            listing_date=date(2017, 7, 10),
            shares_outstanding=444871597,
        ),
    ]

    for stock in stocks:
        db.add(stock)
    await db.commit()

    # Refresh to get created_at/updated_at
    for stock in stocks:
        await db.refresh(stock)

    return stocks


@pytest_asyncio.fixture
async def sample_prices(
    db: AsyncSession, sample_stocks: list[Stock]
) -> list[DailyPrice]:
    """Create sample price data for testing"""
    prices = []
    base_date = date.today() - timedelta(days=365)

    # Create 1 year of daily prices for Samsung (005930)
    for i in range(365):
        trade_date = base_date + timedelta(days=i)
        base_price = 70000 + (i * 100)  # Trending upward

        price = DailyPrice(
            stock_code="005930",
            trade_date=trade_date,
            open_price=base_price - 500,
            high_price=base_price + 1000,
            low_price=base_price - 1000,
            close_price=base_price,
            volume=10000000 + (i * 1000),
            trading_value=(base_price * (10000000 + i * 1000)),
            market_cap=base_price * 5969782550,
        )
        prices.append(price)

    # Create 30 days of prices for other stocks
    for stock in sample_stocks[1:3]:  # SK Hynix, NAVER
        for i in range(30):
            trade_date = date.today() - timedelta(days=30 - i)
            base_price = 100000 if stock.code == "000660" else 200000

            price = DailyPrice(
                stock_code=stock.code,
                trade_date=trade_date,
                open_price=base_price - 1000,
                high_price=base_price + 2000,
                low_price=base_price - 2000,
                close_price=base_price,
                volume=5000000,
                trading_value=base_price * 5000000,
                market_cap=base_price * stock.shares_outstanding,
            )
            prices.append(price)

    for price in prices:
        db.add(price)
    await db.commit()

    return prices


@pytest_asyncio.fixture
async def sample_financials(
    db: AsyncSession, sample_stocks: list[Stock]
) -> list[FinancialStatement]:
    """Create sample financial statements for testing"""
    financials = []

    # Create 5 years of annual financials for Samsung
    for year in range(2019, 2024):
        financial = FinancialStatement(
            stock_code="005930",
            period_type="annual",
            fiscal_year=year,
            report_date=date(year, 12, 31),
            revenue=200000000000000 + (year - 2019) * 10000000000000,
            operating_profit=40000000000000 + (year - 2019) * 2000000000000,
            net_profit=30000000000000 + (year - 2019) * 1500000000000,
            total_assets=300000000000000 + (year - 2019) * 15000000000000,
            equity=200000000000000 + (year - 2019) * 10000000000000,
            eps=5000 + (year - 2019) * 500,
        )
        financials.append(financial)

    # Create 4 quarters of 2023 financials for Samsung
    for quarter in range(1, 5):
        financial = FinancialStatement(
            stock_code="005930",
            period_type="quarterly",
            fiscal_year=2023,
            fiscal_quarter=quarter,
            report_date=date(2023, quarter * 3, 1),
            revenue=50000000000000 + quarter * 1000000000000,
            operating_profit=10000000000000 + quarter * 200000000000,
            net_profit=7500000000000 + quarter * 150000000000,
            total_assets=315000000000000,
            equity=210000000000000,
            eps=1250 + quarter * 25,
        )
        financials.append(financial)

    for financial in financials:
        db.add(financial)
    await db.commit()

    return financials


# ============================================================================
# Stock List and Search Tests
# ============================================================================


@pytest.mark.asyncio
class TestStockListEndpoints:
    """Test stock listing and search endpoints"""

    async def test_list_stocks_default_params(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/ with default parameters"""
        response = await client.get("/v1/stocks")

        assert response.status_code == 200
        data = response.json()

        assert "stocks" in data
        assert "meta" in data

        # Should return all stocks with default pagination
        assert len(data["stocks"]) == len(sample_stocks)

        # Check meta information
        meta = data["meta"]
        assert meta["total"] == len(sample_stocks)
        assert meta["page"] == 1
        assert meta["per_page"] == 50

        # Verify stock data structure
        stock = data["stocks"][0]
        assert "code" in stock
        assert "name" in stock
        assert "market" in stock

    async def test_list_stocks_with_pagination(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/ with pagination parameters"""
        # Request page 1 with 2 items per page
        response = await client.get("/v1/stocks?page=1&per_page=2")

        assert response.status_code == 200
        data = response.json()

        assert len(data["stocks"]) == 2
        assert data["meta"]["page"] == 1
        assert data["meta"]["per_page"] == 2
        assert data["meta"]["total"] == len(sample_stocks)

        # Request page 2
        response = await client.get("/v1/stocks?page=2&per_page=2")

        assert response.status_code == 200
        data = response.json()

        assert len(data["stocks"]) == 2
        assert data["meta"]["page"] == 2

    async def test_list_stocks_with_market_filter(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/ with market filter"""
        # Filter by KOSPI
        response = await client.get("/v1/stocks?market=KOSPI")

        assert response.status_code == 200
        data = response.json()

        # Should only return KOSPI stocks
        kospi_stocks = [s for s in sample_stocks if s.market == "KOSPI"]
        assert len(data["stocks"]) == len(kospi_stocks)

        # Verify all returned stocks are KOSPI
        for stock in data["stocks"]:
            assert stock["market"] == "KOSPI"

        # Filter by KOSDAQ
        response = await client.get("/v1/stocks?market=KOSDAQ")

        assert response.status_code == 200
        data = response.json()

        # Should only return KOSDAQ stocks
        kosdaq_stocks = [s for s in sample_stocks if s.market == "KOSDAQ"]
        assert len(data["stocks"]) == len(kosdaq_stocks)

    async def test_list_stocks_with_sector_filter(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/ with sector filter"""
        response = await client.get("/v1/stocks?sector=Technology")

        assert response.status_code == 200
        data = response.json()

        # Should only return Technology sector stocks
        tech_stocks = [s for s in sample_stocks if s.sector == "Technology"]
        assert len(data["stocks"]) == len(tech_stocks)

        # Verify all returned stocks are in Technology sector
        for stock in data["stocks"]:
            assert stock["sector"] == "Technology"

    async def test_list_stocks_invalid_market(self, client: AsyncClient):
        """Test GET /stocks/ with invalid market parameter"""
        response = await client.get("/v1/stocks?market=INVALID")

        # Should return 422 Unprocessable Entity for invalid enum value
        assert response.status_code == 422

    async def test_list_stocks_invalid_pagination(self, client: AsyncClient):
        """Test GET /stocks/ with invalid pagination parameters"""
        # page must be >= 1
        response = await client.get("/v1/stocks?page=0")
        assert response.status_code == 422

        # per_page must be <= 100
        response = await client.get("/v1/stocks?per_page=101")
        assert response.status_code == 422

    async def test_search_stocks_by_name(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/search by stock name"""
        response = await client.get("/v1/stocks/search?q=삼성")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        # Should find Samsung Electronics
        assert any(stock["code"] == "005930" for stock in data["items"])

    async def test_search_stocks_by_code(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/search by stock code"""
        response = await client.get("/v1/stocks/search?q=005930")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) >= 1
        assert data["items"][0]["code"] == "005930"

    async def test_search_stocks_with_limit(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/search with limit parameter"""
        response = await client.get("/v1/stocks/search?q=Technology&limit=2")

        assert response.status_code == 200
        data = response.json()

        # Should respect limit parameter
        assert len(data["items"]) <= 2

    async def test_search_stocks_no_results(self, client: AsyncClient):
        """Test GET /stocks/search with no matching results"""
        response = await client.get("/v1/stocks/search?q=NonExistentStock")

        assert response.status_code == 200
        data = response.json()

        assert data["items"] == []


# ============================================================================
# Stock Detail Tests
# ============================================================================


@pytest.mark.asyncio
class TestStockDetailEndpoint:
    """Test stock detail endpoint"""

    async def test_get_stock_by_code(
        self, client: AsyncClient, sample_stocks: list[Stock], sample_prices: list[DailyPrice]
    ):
        """Test GET /stocks/{stock_code} returns stock details"""
        response = await client.get("/v1/stocks/005930")

        assert response.status_code == 200
        data = response.json()

        # Verify basic stock information
        assert data["code"] == "005930"
        assert data["name"] == "삼성전자"
        assert data["market"] == "KOSPI"
        assert data["sector"] == "Technology"

    async def test_get_stock_includes_all_fields(
        self, client: AsyncClient, sample_stocks: list[Stock], sample_prices: list[DailyPrice]
    ):
        """Test stock detail response includes all required fields"""
        response = await client.get("/v1/stocks/005930")

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        required_fields = [
            "code",
            "name",
            "market",
            "sector",
            "industry",
            "listing_date",
            "shares_outstanding",
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    async def test_get_stock_not_found(self, client: AsyncClient):
        """Test GET /stocks/{stock_code} with non-existent code"""
        response = await client.get("/v1/stocks/999999")

        # Should return 404 Not Found
        assert response.status_code == 404

    async def test_get_stock_invalid_code_format(self, client: AsyncClient):
        """Test GET /stocks/{stock_code} with invalid code format"""
        # Code must be 6 digits
        response = await client.get("/v1/stocks/123")

        # May return 404 or 422 depending on validation
        assert response.status_code in [404, 422]


# ============================================================================
# Price History Tests
# ============================================================================


@pytest.mark.asyncio
class TestPriceHistoryEndpoint:
    """Test price history endpoint"""

    async def test_get_stock_prices(
        self, client: AsyncClient, sample_stocks: list[Stock], sample_prices: list[DailyPrice]
    ):
        """Test GET /stocks/{stock_code}/prices returns price history"""
        response = await client.get("/v1/stocks/005930/prices")

        assert response.status_code == 200
        data = response.json()

        # Should return list of prices
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify price data structure
        price = data[0]
        required_fields = [
            "stock_code",
            "trade_date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
        ]

        for field in required_fields:
            assert field in price, f"Missing required field: {field}"

    async def test_get_stock_prices_date_range(
        self, client: AsyncClient, sample_stocks: list[Stock], sample_prices: list[DailyPrice]
    ):
        """Test GET /stocks/{stock_code}/prices with date range filter"""
        from_date = (date.today() - timedelta(days=30)).isoformat()
        to_date = date.today().isoformat()

        response = await client.get(
            f"/v1/stocks/005930/prices?from_date={from_date}&to_date={to_date}"
        )

        assert response.status_code == 200
        data = response.json()

        # Should return prices within date range
        assert len(data) > 0

        # Verify all prices are within range
        for price in data:
            price_date = datetime.fromisoformat(price["trade_date"]).date()
            assert price_date >= date.fromisoformat(from_date)
            assert price_date <= date.fromisoformat(to_date)

    async def test_get_stock_prices_with_limit(
        self, client: AsyncClient, sample_stocks: list[Stock], sample_prices: list[DailyPrice]
    ):
        """Test GET /stocks/{stock_code}/prices with limit parameter"""
        response = await client.get("/v1/stocks/005930/prices?limit=10")

        assert response.status_code == 200
        data = response.json()

        # Should respect limit parameter
        assert len(data) <= 10

    async def test_get_stock_prices_empty_range(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/{stock_code}/prices with no prices in range"""
        # Query for dates far in the future
        from_date = "2030-01-01"
        to_date = "2030-12-31"

        response = await client.get(
            f"/v1/stocks/005930/prices?from_date={from_date}&to_date={to_date}"
        )

        assert response.status_code == 200
        data = response.json()

        # Should return empty list
        assert data == []

    async def test_get_stock_prices_invalid_dates(self, client: AsyncClient):
        """Test GET /stocks/{stock_code}/prices with invalid date formats"""
        # Invalid date format
        response = await client.get("/v1/stocks/005930/prices?from_date=invalid-date")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    async def test_get_stock_prices_stock_not_found(self, client: AsyncClient):
        """Test GET /stocks/{stock_code}/prices for non-existent stock"""
        response = await client.get("/v1/stocks/999999/prices")

        # May return 404 or empty list depending on implementation
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert data == []


# ============================================================================
# Financial Data Tests
# ============================================================================


@pytest.mark.asyncio
class TestFinancialDataEndpoint:
    """Test financial data endpoint"""

    async def test_get_stock_financials(
        self,
        client: AsyncClient,
        sample_stocks: list[Stock],
        sample_financials: list[FinancialStatement],
    ):
        """Test GET /stocks/{stock_code}/financials returns financial data"""
        response = await client.get("/v1/stocks/005930/financials")

        assert response.status_code == 200
        data = response.json()

        # Should return list of financial statements
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify financial data structure
        financial = data[0]
        required_fields = [
            "stock_code",
            "period_type",
            "fiscal_year",
            "report_date",
        ]

        for field in required_fields:
            assert field in financial, f"Missing required field: {field}"

    async def test_get_stock_financials_includes_metrics(
        self,
        client: AsyncClient,
        sample_stocks: list[Stock],
        sample_financials: list[FinancialStatement],
    ):
        """Test financial response includes key financial metrics"""
        response = await client.get("/v1/stocks/005930/financials")

        assert response.status_code == 200
        data = response.json()

        financial = data[0]

        # Check for key financial metrics
        key_metrics = ["revenue", "operating_profit", "net_profit", "eps"]

        for metric in key_metrics:
            assert metric in financial

    async def test_get_stock_financials_period_type_filter(
        self,
        client: AsyncClient,
        sample_stocks: list[Stock],
        sample_financials: list[FinancialStatement],
    ):
        """Test GET /stocks/{stock_code}/financials with period_type filter"""
        # Test annual financials
        response = await client.get("/v1/stocks/005930/financials?period_type=annual")

        assert response.status_code == 200
        data = response.json()

        # All should be annual
        for financial in data:
            assert financial["period_type"] == "annual"

        # Test quarterly financials
        response = await client.get("/v1/stocks/005930/financials?period_type=quarterly")

        assert response.status_code == 200
        data = response.json()

        # All should be quarterly
        for financial in data:
            assert financial["period_type"] == "quarterly"

    async def test_get_stock_financials_years_parameter(
        self,
        client: AsyncClient,
        sample_stocks: list[Stock],
        sample_financials: list[FinancialStatement],
    ):
        """Test GET /stocks/{stock_code}/financials with years parameter"""
        response = await client.get("/v1/stocks/005930/financials?years=3")

        assert response.status_code == 200
        data = response.json()

        # Should limit results based on years parameter
        # The actual number depends on how the service implements this
        assert len(data) > 0

    async def test_get_stock_financials_not_available(
        self, client: AsyncClient, sample_stocks: list[Stock]
    ):
        """Test GET /stocks/{stock_code}/financials when data not available"""
        # Query for stock with no financial data (LG Chem - 051910)
        response = await client.get("/v1/stocks/051910/financials")

        assert response.status_code == 200
        data = response.json()

        # Should return empty list
        assert data == []

    async def test_get_stock_financials_stock_not_found(self, client: AsyncClient):
        """Test GET /stocks/{stock_code}/financials for non-existent stock"""
        response = await client.get("/v1/stocks/999999/financials")

        # May return 404 or empty list
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert data == []

    async def test_get_stock_financials_invalid_period_type(self, client: AsyncClient):
        """Test GET /stocks/{stock_code}/financials with invalid period_type"""
        response = await client.get("/v1/stocks/005930/financials?period_type=invalid")

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    async def test_get_stock_financials_invalid_years(self, client: AsyncClient):
        """Test GET /stocks/{stock_code}/financials with invalid years parameter"""
        # years must be >= 1 and <= 10
        response = await client.get("/v1/stocks/005930/financials?years=0")
        assert response.status_code == 422

        response = await client.get("/v1/stocks/005930/financials?years=11")
        assert response.status_code == 422
