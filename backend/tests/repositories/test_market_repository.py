"""Tests for MarketRepository"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.market_repository import MarketRepository


@pytest.fixture
def mock_session():
    """Create mock database session"""
    session = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def market_repo(mock_session):
    """Create MarketRepository with mocked session"""
    return MarketRepository(mock_session)


class TestMarketRepositoryInit:
    """Test MarketRepository initialization"""

    def test_init_sets_session(self, mock_session):
        """Test initialization sets session"""
        repo = MarketRepository(mock_session)
        assert repo.session == mock_session


class TestGetCurrentIndices:
    """Test get_current_indices method"""

    @pytest.mark.asyncio
    async def test_get_current_indices_empty(self, market_repo, mock_session):
        """Test get_current_indices with no data"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_current_indices()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_current_indices_returns_list(self, market_repo, mock_session):
        """Test get_current_indices returns list of indices"""
        mock_index = MagicMock()
        mock_index.code = "KOSPI"
        mock_index.close_value = Decimal("2500.50")

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_index]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_current_indices()

        assert len(result) == 1
        assert result[0].code == "KOSPI"


class TestGetIndexSparkline:
    """Test get_index_sparkline method"""

    @pytest.mark.asyncio
    async def test_get_index_sparkline_returns_floats(self, market_repo, mock_session):
        """Test get_index_sparkline returns list of floats"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Decimal("2510.0"),
            Decimal("2505.0"),
            Decimal("2500.0"),
        ]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_index_sparkline("KOSPI", data_points=3)

        # Should be reversed (oldest to newest)
        assert result == [2500.0, 2505.0, 2510.0]

    @pytest.mark.asyncio
    async def test_get_index_sparkline_empty(self, market_repo, mock_session):
        """Test get_index_sparkline with no data"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_index_sparkline("KOSPI")

        assert result == []


class TestGetIndexHistory:
    """Test get_index_history method"""

    @pytest.mark.asyncio
    async def test_get_index_history(self, market_repo, mock_session):
        """Test get_index_history returns list of indices"""
        mock_index = MagicMock()
        mock_index.code = "KOSPI"
        mock_index.timestamp = datetime.now()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_index]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_index_history(
            code="KOSPI",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
        )

        assert len(result) == 1
        assert result[0].code == "KOSPI"


class TestGetMarketBreadth:
    """Test get_market_breadth method"""

    @pytest.mark.asyncio
    async def test_get_market_breadth(self, market_repo, mock_session):
        """Test get_market_breadth returns dictionary"""
        mock_row = MagicMock()
        mock_row.advancing = 500
        mock_row.declining = 400
        mock_row.unchanged = 100

        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_market_breadth()

        assert result["advancing"] == 500
        assert result["declining"] == 400
        assert result["unchanged"] == 100

    @pytest.mark.asyncio
    async def test_get_market_breadth_with_null_values(self, market_repo, mock_session):
        """Test get_market_breadth handles null values"""
        mock_row = MagicMock()
        mock_row.advancing = None
        mock_row.declining = None
        mock_row.unchanged = None

        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_market_breadth()

        assert result["advancing"] == 0
        assert result["declining"] == 0
        assert result["unchanged"] == 0

    @pytest.mark.asyncio
    async def test_get_market_breadth_with_market_filter(self, market_repo, mock_session):
        """Test get_market_breadth with market filter"""
        mock_row = MagicMock()
        mock_row.advancing = 300
        mock_row.declining = 200
        mock_row.unchanged = 50

        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_market_breadth(market="KOSPI")

        assert result["advancing"] == 300


class TestGetSectorPerformance:
    """Test get_sector_performance method"""

    @pytest.mark.asyncio
    async def test_get_sector_performance(self, market_repo, mock_session):
        """Test get_sector_performance returns list"""
        mock_row = MagicMock()
        mock_row.sector = "technology"
        mock_row.stock_count = 50
        mock_row.market_cap = 1000000000000
        mock_row.total_volume = 50000000
        mock_row.avg_change_percent = 1.5

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_sector_performance()

        assert len(result) == 1
        assert result[0]["code"] == "technology"
        assert result[0]["stock_count"] == 50
        assert result[0]["change_percent"] == 1.5

    @pytest.mark.asyncio
    async def test_get_sector_performance_handles_null_values(
        self, market_repo, mock_session
    ):
        """Test get_sector_performance handles null values"""
        mock_row = MagicMock()
        mock_row.sector = "technology"
        mock_row.stock_count = 50
        mock_row.market_cap = None
        mock_row.total_volume = None
        mock_row.avg_change_percent = None

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_sector_performance()

        assert result[0]["market_cap"] == 0
        assert result[0]["volume"] == 0
        assert result[0]["change_percent"] == 0.0


class TestGetSectorTopStock:
    """Test get_sector_top_stock method"""

    @pytest.mark.asyncio
    async def test_get_sector_top_stock(self, market_repo, mock_session):
        """Test get_sector_top_stock returns tuple"""
        mock_row = MagicMock()
        mock_row.code = "005930"
        mock_row.name = "삼성전자"
        mock_row.change_percent = 2.5

        mock_result = MagicMock()
        mock_result.one_or_none.return_value = mock_row
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_sector_top_stock("technology")

        assert result == ("005930", "삼성전자", 2.5)

    @pytest.mark.asyncio
    async def test_get_sector_top_stock_none(self, market_repo, mock_session):
        """Test get_sector_top_stock returns None when no data"""
        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_sector_top_stock("unknown")

        assert result is None


class TestGetTopMovers:
    """Test get_top_movers method"""

    @pytest.mark.asyncio
    async def test_get_top_movers_gainers(self, market_repo, mock_session):
        """Test get_top_movers for gainers"""
        mock_row = MagicMock()
        mock_row.code = "005930"
        mock_row.name = "삼성전자"
        mock_row.market = "KOSPI"
        mock_row.sector = "technology"
        mock_row.close_price = 70000
        mock_row.change = 1000
        mock_row.change_percent = 1.45
        mock_row.volume = 10000000
        mock_row.trading_value = 700000000000

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_top_movers("gainers")

        assert len(result) == 1
        assert result[0]["code"] == "005930"
        assert result[0]["change_percent"] == 1.45

    @pytest.mark.asyncio
    async def test_get_top_movers_losers(self, market_repo, mock_session):
        """Test get_top_movers for losers"""
        mock_row = MagicMock()
        mock_row.code = "000660"
        mock_row.name = "SK하이닉스"
        mock_row.market = "KOSPI"
        mock_row.sector = "technology"
        mock_row.close_price = 150000
        mock_row.change = -2000
        mock_row.change_percent = -1.32
        mock_row.volume = 5000000
        mock_row.trading_value = 750000000000

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_top_movers("losers")

        assert len(result) == 1
        assert result[0]["change_percent"] == -1.32


class TestGetMostActive:
    """Test get_most_active method"""

    @pytest.mark.asyncio
    async def test_get_most_active_by_volume(self, market_repo, mock_session):
        """Test get_most_active sorted by volume"""
        mock_row = MagicMock()
        mock_row.code = "005930"
        mock_row.name = "삼성전자"
        mock_row.market = "KOSPI"
        mock_row.sector = "technology"
        mock_row.close_price = 70000
        mock_row.change_percent = 1.5
        mock_row.volume = 50000000
        mock_row.trading_value = 3500000000000

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_most_active("volume")

        assert len(result) == 1
        assert result[0]["volume"] == 50000000

    @pytest.mark.asyncio
    async def test_get_most_active_by_value(self, market_repo, mock_session):
        """Test get_most_active sorted by trading value"""
        mock_row = MagicMock()
        mock_row.code = "005930"
        mock_row.name = "삼성전자"
        mock_row.market = "KOSPI"
        mock_row.sector = "technology"
        mock_row.close_price = 70000
        mock_row.change_percent = 1.5
        mock_row.volume = 50000000
        mock_row.trading_value = 3500000000000

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_most_active("value")

        assert len(result) == 1
        assert result[0]["value"] == 3500000000000

    @pytest.mark.asyncio
    async def test_get_most_active_handles_null_change_percent(
        self, market_repo, mock_session
    ):
        """Test get_most_active handles null change_percent"""
        mock_row = MagicMock()
        mock_row.code = "005930"
        mock_row.name = "삼성전자"
        mock_row.market = "KOSPI"
        mock_row.sector = "technology"
        mock_row.close_price = 70000
        mock_row.change_percent = None
        mock_row.volume = 50000000
        mock_row.trading_value = 3500000000000

        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute.return_value = mock_result

        result = await market_repo.get_most_active("volume")

        assert result[0]["change_percent"] == 0.0
