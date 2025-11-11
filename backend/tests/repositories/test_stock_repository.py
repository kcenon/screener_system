"""Unit and integration tests for stock repository"""

from datetime import date
from unittest.mock import AsyncMock, Mock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.stock_repository import StockRepository
from app.db.models import Stock, DailyPrice, CalculatedIndicator


class TestStockRepository:
    """Test StockRepository"""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        session = Mock(spec=AsyncSession)
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance with mock session"""
        return StockRepository(session=mock_session)

    @pytest.fixture
    def sample_stock(self):
        """Create sample stock object"""
        return Stock(
            code="005930",
            name="삼성전자",
            name_english="Samsung Electronics",
            market="KOSPI",
            sector="전기전자",
            industry="반도체",
            listing_date=date(1975, 6, 11),
            delisting_date=None,
        )

    @pytest.fixture
    def sample_price(self):
        """Create sample daily price object"""
        return DailyPrice(
            stock_code="005930",
            date=date(2025, 11, 11),
            open_price=70000,
            high_price=71000,
            low_price=69500,
            close_price=70500,
            volume=10000000,
            trading_value=705000000000,
        )

    @pytest.fixture
    def sample_indicators(self):
        """Create sample calculated indicators object"""
        return CalculatedIndicator(
            stock_code="005930",
            date=date(2025, 11, 11),
            per=15.5,
            pbr=1.2,
            roe=12.5,
        )

    # ========================================================================
    # Initialization Tests
    # ========================================================================

    def test_init(self, mock_session):
        """Test repository initialization"""
        repo = StockRepository(session=mock_session)
        assert repo.session == mock_session

    # ========================================================================
    # get_by_code Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_by_code_found(self, repository, mock_session, sample_stock):
        """Test get_by_code when stock exists"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_stock
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_by_code("005930")

        # Assert
        assert result == sample_stock
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_get_by_code_not_found(self, repository, mock_session):
        """Test get_by_code when stock does not exist"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_by_code("999999")

        # Assert
        assert result is None
        assert mock_session.execute.called

    # ========================================================================
    # get_by_code_with_latest Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_by_code_with_latest_found(
        self, repository, sample_stock, sample_price, sample_indicators
    ):
        """Test get_by_code_with_latest when stock exists"""
        # Mock the methods
        repository.get_by_code = AsyncMock(return_value=sample_stock)
        repository.get_latest_price = AsyncMock(return_value=sample_price)
        repository.get_latest_indicators = AsyncMock(return_value=sample_indicators)

        # Execute
        result = await repository.get_by_code_with_latest("005930")

        # Assert
        assert result is not None
        stock, price, indicators = result
        assert stock == sample_stock
        assert price == sample_price
        assert indicators == sample_indicators

    @pytest.mark.asyncio
    async def test_get_by_code_with_latest_stock_not_found(self, repository):
        """Test get_by_code_with_latest when stock does not exist"""
        # Mock the get_by_code to return None
        repository.get_by_code = AsyncMock(return_value=None)

        # Execute
        result = await repository.get_by_code_with_latest("999999")

        # Assert
        assert result is None

    # ========================================================================
    # list_stocks Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_list_stocks_no_filters(self, repository, mock_session, sample_stock):
        """Test list_stocks without filters"""
        # Setup mocks
        mock_stocks_result = Mock()
        mock_stocks_result.scalars.return_value.all.return_value = [sample_stock]

        mock_count_result = Mock()
        mock_count_result.scalar_one.return_value = 1

        # Configure execute to return different results based on call order
        mock_session.execute.side_effect = [mock_count_result, mock_stocks_result]

        # Execute
        stocks, total_count = await repository.list_stocks()

        # Assert
        assert len(stocks) == 1
        assert stocks[0] == sample_stock
        assert total_count == 1
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_list_stocks_with_market_filter(
        self, repository, mock_session, sample_stock
    ):
        """Test list_stocks with market filter"""
        # Setup mocks
        mock_stocks_result = Mock()
        mock_stocks_result.scalars.return_value.all.return_value = [sample_stock]

        mock_count_result = Mock()
        mock_count_result.scalar_one.return_value = 1

        mock_session.execute.side_effect = [mock_count_result, mock_stocks_result]

        # Execute
        stocks, total_count = await repository.list_stocks(market="KOSPI")

        # Assert
        assert len(stocks) == 1
        assert total_count == 1

    @pytest.mark.asyncio
    async def test_list_stocks_with_pagination(
        self, repository, mock_session, sample_stock
    ):
        """Test list_stocks with pagination"""
        # Setup mocks
        mock_stocks_result = Mock()
        mock_stocks_result.scalars.return_value.all.return_value = [sample_stock]

        mock_count_result = Mock()
        mock_count_result.scalar_one.return_value = 100

        mock_session.execute.side_effect = [mock_count_result, mock_stocks_result]

        # Execute
        stocks, total_count = await repository.list_stocks(offset=10, limit=10)

        # Assert
        assert len(stocks) == 1
        assert total_count == 100

    # ========================================================================
    # search_stocks Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_search_stocks_by_name(
        self, repository, mock_session, sample_stock
    ):
        """Test search_stocks by stock name"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_stock]
        mock_session.execute.return_value = mock_result

        # Execute
        results = await repository.search_stocks("삼성")

        # Assert
        assert len(results) == 1
        assert results[0] == sample_stock
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_search_stocks_by_code(
        self, repository, mock_session, sample_stock
    ):
        """Test search_stocks by stock code"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_stock]
        mock_session.execute.return_value = mock_result

        # Execute
        results = await repository.search_stocks("005930")

        # Assert
        assert len(results) == 1
        assert results[0] == sample_stock

    @pytest.mark.asyncio
    async def test_search_stocks_with_market_filter(
        self, repository, mock_session, sample_stock
    ):
        """Test search_stocks with market filter"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_stock]
        mock_session.execute.return_value = mock_result

        # Execute
        results = await repository.search_stocks("삼성", market="KOSPI")

        # Assert
        assert len(results) == 1
        assert results[0] == sample_stock

    @pytest.mark.asyncio
    async def test_search_stocks_no_results(self, repository, mock_session):
        """Test search_stocks with no matching results"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        # Execute
        results = await repository.search_stocks("없는회사")

        # Assert
        assert len(results) == 0

    # ========================================================================
    # get_latest_price Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_latest_price_found(
        self, repository, mock_session, sample_price
    ):
        """Test get_latest_price when price exists"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_price
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_latest_price("005930")

        # Assert
        assert result == sample_price
        assert mock_session.execute.called

    @pytest.mark.asyncio
    async def test_get_latest_price_not_found(self, repository, mock_session):
        """Test get_latest_price when no price data exists"""
        # Setup mock
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await repository.get_latest_price("999999")

        # Assert
        assert result is None
