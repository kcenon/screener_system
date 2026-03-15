"""Unit tests for PortfolioService calculations"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.models import Transaction
from app.db.models.holding import Holding as HoldingModel
from app.services.portfolio_service import PortfolioService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_holding(
    stock_code: str = "005930",
    shares: int = 100,
    average_price: float = 70000.0,
    holding_id: int = 1,
    portfolio_id: int = 1,
) -> MagicMock:
    h = MagicMock(spec=HoldingModel)
    h.id = holding_id
    h.portfolio_id = portfolio_id
    h.stock_code = stock_code
    h.shares = shares
    h.average_price = average_price
    h.total_cost = Decimal(str(shares)) * Decimal(str(average_price))
    h.updated_at = datetime(2025, 1, 1)
    h.created_at = datetime(2025, 1, 1)
    return h


def _make_daily_price(close_price: int, trade_date=None) -> MagicMock:
    dp = MagicMock()
    dp.close_price = close_price
    dp.trade_date = trade_date
    return dp


def _make_stock(
    code: str = "005930",
    name: str = "Samsung Electronics",
    sector: str = "Technology",
    shares_outstanding: int = 5_969_782_550,
) -> MagicMock:
    s = MagicMock()
    s.code = code
    s.name = name
    s.sector = sector
    s.shares_outstanding = shares_outstanding
    s.get_market_cap = lambda price: shares_outstanding * price
    return s


def _make_transaction(
    stock_code: str,
    transaction_type: str,
    quantity: int,
    price: float,
    commission: float = 0.0,
    transaction_date: datetime = None,
    portfolio_id: int = 1,
) -> MagicMock:
    tx = MagicMock(spec=Transaction)
    tx.portfolio_id = portfolio_id
    tx.stock_code = stock_code
    tx.transaction_type = transaction_type
    tx.quantity = quantity
    tx.price = price
    tx.commission = commission
    tx.transaction_date = transaction_date or datetime(2025, 1, 1)
    return tx


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


# ---------------------------------------------------------------------------
# Tests for _calculate_realized_gain
# ---------------------------------------------------------------------------


class TestCalculateRealizedGain:
    """Tests for the average cost method realized gain calculation."""

    @pytest.fixture
    def service(self):
        session = AsyncMock()
        return PortfolioService(session=session)

    @pytest.mark.asyncio
    async def test_buy_only_no_realized_gain(self, service):
        """Holding without any sell → realized gain is zero."""
        buy_tx = _make_transaction("005930", "BUY", 100, 70000.0)
        service.session.execute = AsyncMock(return_value=_mock_scalars([buy_tx]))
        result = await service._calculate_realized_gain(portfolio_id=1)
        assert result == Decimal("0")

    @pytest.mark.asyncio
    async def test_simple_profit(self, service):
        """Buy 100 @ 70000, sell 50 @ 80000 → gain = (80000-70000)*50 = 500000."""
        buy_tx = _make_transaction("005930", "BUY", 100, 70000.0)
        sell_tx = _make_transaction("005930", "SELL", 50, 80000.0)
        service.session.execute = AsyncMock(
            return_value=_mock_scalars([buy_tx, sell_tx])
        )
        result = await service._calculate_realized_gain(portfolio_id=1)
        assert result == Decimal("500000")

    @pytest.mark.asyncio
    async def test_simple_loss(self, service):
        """Buy 100 @ 70000, sell 50 @ 60000 → gain = (60000-70000)*50 = -500000."""
        buy_tx = _make_transaction("005930", "BUY", 100, 70000.0)
        sell_tx = _make_transaction("005930", "SELL", 50, 60000.0)
        service.session.execute = AsyncMock(
            return_value=_mock_scalars([buy_tx, sell_tx])
        )
        result = await service._calculate_realized_gain(portfolio_id=1)
        assert result == Decimal("-500000")

    @pytest.mark.asyncio
    async def test_commission_deducted_from_gain(self, service):
        """Commission is subtracted from realized gain."""
        buy_tx = _make_transaction("005930", "BUY", 100, 70000.0)
        sell_tx = _make_transaction("005930", "SELL", 100, 80000.0, commission=5000.0)
        service.session.execute = AsyncMock(
            return_value=_mock_scalars([buy_tx, sell_tx])
        )
        # gain = (80000-70000)*100 - 5000 = 1000000 - 5000 = 995000
        result = await service._calculate_realized_gain(portfolio_id=1)
        assert result == Decimal("995000")

    @pytest.mark.asyncio
    async def test_weighted_average_cost_after_second_buy(self, service):
        """
        Buy 100 @ 70000, buy 100 @ 90000 → avg = 80000.
        Sell 100 @ 85000 → gain = (85000 - 80000) * 100 = 500000.
        """
        buy1 = _make_transaction(
            "005930", "BUY", 100, 70000.0, transaction_date=datetime(2025, 1, 1)
        )
        buy2 = _make_transaction(
            "005930", "BUY", 100, 90000.0, transaction_date=datetime(2025, 1, 2)
        )
        sell = _make_transaction(
            "005930", "SELL", 100, 85000.0, transaction_date=datetime(2025, 1, 3)
        )
        service.session.execute = AsyncMock(
            return_value=_mock_scalars([buy1, buy2, sell])
        )
        result = await service._calculate_realized_gain(portfolio_id=1)
        assert result == Decimal("500000")

    @pytest.mark.asyncio
    async def test_multiple_stocks(self, service):
        """Gains from two different stocks are summed."""
        buy_a = _make_transaction("005930", "BUY", 100, 70000.0)
        sell_a = _make_transaction("005930", "SELL", 100, 80000.0)
        buy_b = _make_transaction("000660", "BUY", 50, 100000.0)
        sell_b = _make_transaction("000660", "SELL", 50, 110000.0)
        service.session.execute = AsyncMock(
            return_value=_mock_scalars([buy_a, sell_a, buy_b, sell_b])
        )
        # gain_a = 10000*100 = 1000000, gain_b = 10000*50 = 500000
        result = await service._calculate_realized_gain(portfolio_id=1)
        assert result == Decimal("1500000")


# ---------------------------------------------------------------------------
# Tests for get_portfolio_performance day_change calculation
# ---------------------------------------------------------------------------


class TestDayChangeCalculation:
    """Tests for day_change in get_portfolio_performance."""

    @pytest.fixture
    def service(self):
        session = AsyncMock()
        svc = PortfolioService(session=session)
        svc.holding_repo = AsyncMock()
        svc.stock_repo = AsyncMock()
        svc.session.execute = AsyncMock(return_value=_mock_scalars([]))
        return svc

    @pytest.mark.asyncio
    async def test_day_change_positive(self, service):
        """When close price rose, day_change should be positive."""
        holding = _make_holding(stock_code="005930", shares=100, average_price=70000.0)
        service.holding_repo.get_portfolio_holdings = AsyncMock(return_value=[holding])
        service.stock_repo.get_by_code = AsyncMock(return_value=_make_stock("005930"))
        # today: 75000, yesterday: 70000 → day_change = +5000 * 100 = +500000
        service.stock_repo.get_price_history = AsyncMock(
            return_value=[
                _make_daily_price(75000),
                _make_daily_price(70000),
            ]
        )

        result = await service.get_portfolio_performance(portfolio_id=1)

        assert result is not None
        assert result.day_change == Decimal("500000")
        assert result.day_change_percent > Decimal("0")

    @pytest.mark.asyncio
    async def test_day_change_zero_when_single_price_record(self, service):
        """When only one price record exists, day_change contribution is zero."""
        holding = _make_holding(stock_code="005930", shares=100, average_price=70000.0)
        service.holding_repo.get_portfolio_holdings = AsyncMock(return_value=[holding])
        service.stock_repo.get_by_code = AsyncMock(return_value=_make_stock("005930"))
        service.stock_repo.get_price_history = AsyncMock(
            return_value=[_make_daily_price(75000)]  # Only one record
        )

        result = await service.get_portfolio_performance(portfolio_id=1)

        assert result is not None
        assert result.day_change == Decimal("0")
        assert result.day_change_percent == Decimal("0")


# ---------------------------------------------------------------------------
# Tests for Holding.total_cost property
# ---------------------------------------------------------------------------


class TestHoldingTotalCost:
    """Tests for the Holding.total_cost property."""

    def test_total_cost_calculation(self):
        holding = HoldingModel()
        holding.shares = 100
        holding.average_price = 73500.0
        assert holding.total_cost == Decimal("7350000.0")

    def test_total_cost_zero_shares(self):
        holding = HoldingModel()
        holding.shares = 0
        holding.average_price = 73500.0
        assert holding.total_cost == Decimal("0")


# ---------------------------------------------------------------------------
# Tests for market cap classification in get_portfolio_allocation
# ---------------------------------------------------------------------------


class TestMarketCapClassification:
    """Tests that market cap buckets are computed correctly."""

    @pytest.fixture
    def service(self):
        session = AsyncMock()
        svc = PortfolioService(session=session)
        svc.holding_repo = AsyncMock()
        svc.stock_repo = AsyncMock()
        return svc

    @pytest.mark.asyncio
    async def test_large_cap_stock(self, service):
        """A stock with market_cap >= 1 trillion goes into 'large'."""
        holding = _make_holding(stock_code="005930", shares=1, average_price=70000.0)
        service.holding_repo.get_portfolio_holdings = AsyncMock(return_value=[holding])

        # shares_outstanding * price >= 1 trillion
        stock = _make_stock(
            "005930", shares_outstanding=20_000_000_000  # 20B shares * 70000 = 1.4T
        )
        service.stock_repo.get_by_code = AsyncMock(return_value=stock)
        service.stock_repo.get_latest_price = AsyncMock(
            return_value=_make_daily_price(70000)
        )

        result = await service.get_portfolio_allocation(portfolio_id=1)

        assert result is not None
        assert result.by_market_cap["large"] == pytest.approx(100.0)
        assert result.by_market_cap["mid"] == pytest.approx(0.0)
        assert result.by_market_cap["small"] == pytest.approx(0.0)

    @pytest.mark.asyncio
    async def test_small_cap_stock(self, service):
        """A stock with market_cap < 100 billion goes into 'small'."""
        holding = _make_holding(stock_code="999999", shares=1, average_price=1000.0)
        service.holding_repo.get_portfolio_holdings = AsyncMock(return_value=[holding])

        # 100 shares * 1000 = 100,000 (tiny market cap)
        stock = _make_stock("999999", shares_outstanding=100)
        service.stock_repo.get_by_code = AsyncMock(return_value=stock)
        service.stock_repo.get_latest_price = AsyncMock(
            return_value=_make_daily_price(1000)
        )

        result = await service.get_portfolio_allocation(portfolio_id=1)

        assert result is not None
        assert result.by_market_cap["small"] == pytest.approx(100.0)
        assert result.by_market_cap["large"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _mock_scalars(items: list) -> MagicMock:
    """Return a mock that mimics SQLAlchemy .scalars().all() pattern."""
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = items
    mock_result.scalars.return_value = mock_scalars
    return mock_result
