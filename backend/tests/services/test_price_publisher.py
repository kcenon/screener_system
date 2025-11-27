"""Tests for PricePublisher service"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.price_publisher import PricePublisher, price_publisher


@pytest.fixture
def publisher():
    """Create fresh PricePublisher for each test"""
    pub = PricePublisher()
    yield pub
    # Cleanup
    pub._running = False
    if pub._publish_task:
        pub._publish_task.cancel()


class TestPricePublisherInit:
    """Test PricePublisher initialization"""

    def test_init_default_values(self, publisher: PricePublisher):
        """Test initialization sets default values"""
        assert publisher._running is False
        assert publisher._publish_task is None


class TestPublishPriceUpdate:
    """Test price update publishing"""

    @pytest.mark.asyncio
    async def test_publish_price_update_success(self, publisher: PricePublisher):
        """Test successful price update publishing"""
        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(return_value=1)

            await publisher.publish_price_update(
                stock_code="005930",
                price=70000.0,
                change=500.0,
                change_percent=0.72,
                volume=1000000,
            )

            mock_pubsub.publish.assert_called_once()
            call_args = mock_pubsub.publish.call_args

            assert call_args[0][0] == "stock:005930:price"
            message = call_args[0][1]
            assert message["stock_code"] == "005930"
            assert message["price"] == 70000.0
            assert message["change"] == 500.0
            assert message["change_percent"] == 0.72
            assert message["volume"] == 1000000

    @pytest.mark.asyncio
    async def test_publish_price_update_handles_exception(self, publisher: PricePublisher):
        """Test price update handles exception gracefully"""
        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(side_effect=Exception("Redis error"))

            # Should not raise
            await publisher.publish_price_update(
                stock_code="005930",
                price=70000.0,
                change=500.0,
                change_percent=0.72,
                volume=1000000,
            )


class TestPublishOrderbookUpdate:
    """Test order book update publishing"""

    @pytest.mark.asyncio
    async def test_publish_orderbook_update_success(self, publisher: PricePublisher):
        """Test successful order book update publishing"""
        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(return_value=1)

            bids = [
                {"price": 69900, "quantity": 1000, "orders": 5},
                {"price": 69800, "quantity": 2000, "orders": 10},
            ]
            asks = [
                {"price": 70000, "quantity": 800, "orders": 3},
                {"price": 70100, "quantity": 1500, "orders": 8},
            ]

            await publisher.publish_orderbook_update(
                stock_code="005930",
                bids=bids,
                asks=asks,
            )

            mock_pubsub.publish.assert_called_once()
            call_args = mock_pubsub.publish.call_args

            assert call_args[0][0] == "stock:005930:orderbook"
            message = call_args[0][1]
            assert message["stock_code"] == "005930"
            assert len(message["bids"]) == 2
            assert len(message["asks"]) == 2

    @pytest.mark.asyncio
    async def test_publish_orderbook_update_handles_exception(
        self, publisher: PricePublisher
    ):
        """Test order book update handles exception gracefully"""
        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(side_effect=Exception("Redis error"))

            # Should not raise
            await publisher.publish_orderbook_update(
                stock_code="005930",
                bids=[],
                asks=[],
            )


class TestPublishMarketStatus:
    """Test market status publishing"""

    @pytest.mark.asyncio
    async def test_publish_market_status_success(self, publisher: PricePublisher):
        """Test successful market status publishing"""
        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(return_value=1)

            await publisher.publish_market_status(
                market="KOSPI",
                status="open",
            )

            mock_pubsub.publish.assert_called_once()
            call_args = mock_pubsub.publish.call_args

            assert call_args[0][0] == "market:KOSPI:status"
            message = call_args[0][1]
            assert message["market"] == "KOSPI"
            assert message["status"] == "open"

    @pytest.mark.asyncio
    async def test_publish_market_status_different_markets(
        self, publisher: PricePublisher
    ):
        """Test market status publishing for different markets"""
        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(return_value=1)

            await publisher.publish_market_status(market="KOSDAQ", status="closed")

            call_args = mock_pubsub.publish.call_args
            assert call_args[0][0] == "market:KOSDAQ:status"

    @pytest.mark.asyncio
    async def test_publish_market_status_handles_exception(
        self, publisher: PricePublisher
    ):
        """Test market status handles exception gracefully"""
        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(side_effect=Exception("Redis error"))

            # Should not raise
            await publisher.publish_market_status(
                market="KOSPI",
                status="open",
            )


class TestPublishBulkPriceUpdates:
    """Test bulk price updates publishing"""

    @pytest.mark.asyncio
    async def test_publish_bulk_price_updates_success(self, publisher: PricePublisher):
        """Test successful bulk price updates publishing"""
        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(return_value=1)

            updates = [
                {
                    "stock_code": "005930",
                    "price": 70000.0,
                    "change": 500.0,
                    "change_percent": 0.72,
                    "volume": 1000000,
                },
                {
                    "stock_code": "000660",
                    "price": 150000.0,
                    "change": -1000.0,
                    "change_percent": -0.66,
                    "volume": 500000,
                },
            ]

            await publisher.publish_bulk_price_updates(updates)

            assert mock_pubsub.publish.call_count == 2

    @pytest.mark.asyncio
    async def test_publish_bulk_handles_partial_failures(
        self, publisher: PricePublisher
    ):
        """Test bulk publishing handles partial failures gracefully"""
        call_count = 0

        async def mock_publish(channel, message):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First publish failed")
            return 1

        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = mock_publish

            updates = [
                {
                    "stock_code": "005930",
                    "price": 70000.0,
                    "change": 500.0,
                    "change_percent": 0.72,
                    "volume": 1000000,
                },
                {
                    "stock_code": "000660",
                    "price": 150000.0,
                    "change": -1000.0,
                    "change_percent": -0.66,
                    "volume": 500000,
                },
            ]

            # Should not raise even if some fail
            await publisher.publish_bulk_price_updates(updates)


class TestMockPublisher:
    """Test mock price publisher functionality"""

    @pytest.mark.asyncio
    async def test_start_mock_publisher(self, publisher: PricePublisher):
        """Test starting mock publisher"""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        with patch.object(publisher, "_mock_publish_loop", new_callable=AsyncMock):
            await publisher.start_mock_publisher(mock_db, interval=1.0)

            assert publisher._running is True
            assert publisher._publish_task is not None

    @pytest.mark.asyncio
    async def test_start_mock_publisher_already_running(self, publisher: PricePublisher):
        """Test starting mock publisher when already running"""
        publisher._running = True

        mock_db = AsyncMock()

        await publisher.start_mock_publisher(mock_db)

        # Should not start another task
        assert publisher._publish_task is None

    @pytest.mark.asyncio
    async def test_stop_mock_publisher(self, publisher: PricePublisher):
        """Test stopping mock publisher"""
        # Create a mock task that is both cancellable and awaitable
        # Real tasks raise CancelledError when awaited after cancel()
        class CancelledTaskMock:
            def __init__(self):
                self.cancel = MagicMock()

            def __await__(self):
                raise asyncio.CancelledError()
                yield  # pragma: no cover

        mock_task = CancelledTaskMock()
        publisher._running = True
        publisher._publish_task = mock_task

        await publisher.stop_mock_publisher()

        assert publisher._running is False
        mock_task.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_mock_publisher_when_not_running(self, publisher: PricePublisher):
        """Test stopping mock publisher when not running"""
        publisher._running = False
        publisher._publish_task = None

        # Should not raise
        await publisher.stop_mock_publisher()

        assert publisher._running is False

    @pytest.mark.asyncio
    async def test_mock_publish_loop_no_stocks(self, publisher: PricePublisher):
        """Test mock publish loop with no stocks"""
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        publisher._running = True

        await publisher._mock_publish_loop(mock_db, interval=1.0)

        # Should return early when no stocks
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_mock_publish_loop_with_stocks(self, publisher: PricePublisher):
        """Test mock publish loop with stocks"""
        from unittest.mock import MagicMock

        mock_stock = MagicMock()
        mock_stock.stock_code = "005930"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_stock]
        mock_db.execute.return_value = mock_result

        iteration_count = 0

        async def mock_sleep(seconds):
            nonlocal iteration_count
            iteration_count += 1
            if iteration_count >= 1:
                publisher._running = False

        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(return_value=1)

            with patch("asyncio.sleep", mock_sleep):
                publisher._running = True
                await publisher._mock_publish_loop(mock_db, interval=1.0)

                # Should have published at least once
                assert mock_pubsub.publish.called

    @pytest.mark.asyncio
    async def test_mock_publish_loop_handles_cancel(self, publisher: PricePublisher):
        """Test mock publish loop handles cancellation"""
        mock_stock = MagicMock()
        mock_stock.stock_code = "005930"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_stock]
        mock_db.execute.return_value = mock_result

        async def raise_cancel(seconds):
            raise asyncio.CancelledError()

        with patch("app.services.price_publisher.redis_pubsub") as mock_pubsub:
            mock_pubsub.publish = AsyncMock(return_value=1)

            with patch("asyncio.sleep", raise_cancel):
                publisher._running = True

                with pytest.raises(asyncio.CancelledError):
                    await publisher._mock_publish_loop(mock_db, interval=1.0)


class TestGlobalPricePublisher:
    """Test global price_publisher instance"""

    def test_global_instance_exists(self):
        """Test global price_publisher instance is created"""
        assert price_publisher is not None
        assert isinstance(price_publisher, PricePublisher)

    def test_global_instance_not_running_initially(self):
        """Test global instance is not running initially"""
        assert price_publisher._running is False
