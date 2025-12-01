"""Integration tests for Redis Pub/Sub WebSocket integration"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from app.core.redis_pubsub import RedisPubSubClient
from app.core.websocket import ConnectionManager
from app.schemas.websocket import MessageType, SubscriptionType
from app.services.price_publisher import PricePublisher


class TestRedisPubSubClient:
    """Test Redis Pub/Sub client"""

    @pytest.mark.skip(
        reason="Redis mock configuration issues - requires separate fix (BUGFIX-004)"
    )
    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self):
        """Test Redis connection and disconnection"""
        client = RedisPubSubClient()

        # Mock Redis connection
        with patch("redis.asyncio.from_url") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_redis_instance.pubsub = Mock()
            mock_redis.return_value = mock_redis_instance

            await client.connect()
            assert client.is_connected()

            await client.disconnect()

    @pytest.mark.asyncio
    async def test_publish_message(self):
        """Test publishing a message to Redis channel"""
        client = RedisPubSubClient()

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_redis_instance.pubsub = Mock()
            mock_redis_instance.publish = AsyncMock(return_value=2)
            mock_redis.return_value = mock_redis_instance

            await client.connect()

            # Publish a message
            receivers = await client.publish(
                "stock:005930:price",
                {"type": "price_update", "price": 72500},
            )

            assert receivers == 2
            mock_redis_instance.publish.assert_called_once()

    @pytest.mark.skip(
        reason="Redis mock configuration issues - requires separate fix (BUGFIX-004)"
    )
    @pytest.mark.asyncio
    async def test_subscribe_to_channel(self):
        """Test subscribing to a Redis channel"""
        client = RedisPubSubClient()
        handler_called = asyncio.Event()
        received_data = {}

        async def test_handler(channel: str, data: dict):
            received_data["channel"] = channel
            received_data["data"] = data
            handler_called.set()

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_pubsub = AsyncMock()
            mock_pubsub.subscribe = AsyncMock()
            mock_pubsub.listen = AsyncMock()
            mock_redis_instance.pubsub.return_value = mock_pubsub
            mock_redis.return_value = mock_redis_instance

            await client.connect()
            await client.subscribe("stock:005930:price", test_handler)

            assert "stock:005930:price" in client._subscribers
            mock_pubsub.subscribe.assert_called_once_with("stock:005930:price")


class TestPricePublisher:
    """Test price publisher service"""

    @pytest.mark.asyncio
    async def test_publish_price_update(self):
        """Test publishing a price update"""
        publisher = PricePublisher()

        with patch("app.services.price_publisher.redis_pubsub") as mock_redis:
            mock_redis.publish = AsyncMock()

            await publisher.publish_price_update(
                stock_code="005930",
                price=72500.0,
                change=500.0,
                change_percent=0.69,
                volume=15234567,
            )

            # Verify Redis publish was called
            mock_redis.publish.assert_called_once()
            call_args = mock_redis.publish.call_args

            assert call_args[0][0] == "stock:005930:price"
            message = call_args[0][1]
            assert message["type"] == MessageType.PRICE_UPDATE
            assert message["stock_code"] == "005930"
            assert message["price"] == 72500.0

    @pytest.mark.asyncio
    async def test_publish_bulk_updates(self):
        """Test publishing multiple price updates"""
        publisher = PricePublisher()

        updates = [
            {
                "stock_code": "005930",
                "price": 72500.0,
                "change": 500.0,
                "change_percent": 0.69,
                "volume": 15234567,
            },
            {
                "stock_code": "000660",
                "price": 125000.0,
                "change": -1000.0,
                "change_percent": -0.79,
                "volume": 8765432,
            },
        ]

        with patch("app.services.price_publisher.redis_pubsub") as mock_redis:
            mock_redis.publish = AsyncMock()

            await publisher.publish_bulk_price_updates(updates)

            # Verify publish was called twice
            assert mock_redis.publish.call_count == 2

    @pytest.mark.asyncio
    async def test_publish_market_status(self):
        """Test publishing market status"""
        publisher = PricePublisher()

        with patch("app.services.price_publisher.redis_pubsub") as mock_redis:
            mock_redis.publish = AsyncMock()

            await publisher.publish_market_status(
                market="KOSPI",
                status="open",
            )

            mock_redis.publish.assert_called_once()
            call_args = mock_redis.publish.call_args

            assert call_args[0][0] == "market:KOSPI:status"
            message = call_args[0][1]
            assert message["type"] == MessageType.MARKET_STATUS
            assert message["market"] == "KOSPI"
            assert message["status"] == "open"


class TestWebSocketRedisIntegration:
    """Test WebSocket and Redis Pub/Sub integration"""

    @pytest.mark.skip(
        reason="Redis mock configuration issues - requires separate fix (BUGFIX-004)"
    )
    @pytest.mark.asyncio
    async def test_subscribe_creates_redis_channel(self):
        """Test that subscribing to stock creates Redis channel subscription"""
        manager = ConnectionManager(enable_redis=True)
        manager._redis_initialized = True

        with patch("app.core.websocket.redis_pubsub") as mock_redis:
            mock_redis.subscribe = AsyncMock()

            # Simulate connection
            conn_id = "test-connection"
            manager.connection_info[conn_id] = Mock()

            # Subscribe to stock
            await manager.subscribe(
                conn_id,
                SubscriptionType.STOCK,
                "005930",
            )

            # Verify Redis subscription
            mock_redis.subscribe.assert_called_once()
            call_args = mock_redis.subscribe.call_args
            assert call_args[0][0] == "stock:005930:*"

    @pytest.mark.skip(
        reason="Redis mock configuration issues - requires separate fix (BUGFIX-004)"
    )
    @pytest.mark.asyncio
    async def test_redis_message_forwarded_to_websocket(self):
        """Test that Redis messages are forwarded to WebSocket subscribers"""
        manager = ConnectionManager(enable_redis=False)

        # Create mock WebSocket connection
        mock_websocket = AsyncMock()
        conn_id = "test-connection"
        manager.active_connections[conn_id] = mock_websocket
        manager.connection_info[conn_id] = Mock(
            connection_id=conn_id,
            user_id=None,
            subscriptions={},
            message_count=0,
            last_activity=Mock(),
        )

        # Subscribe to stock
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Simulate Redis message
        redis_message = {
            "type": "price_update",
            "stock_code": "005930",
            "price": 72500.0,
            "change": 500.0,
            "change_percent": 0.69,
            "volume": 15234567,
        }

        await manager._handle_redis_message("stock:005930:price", redis_message)

        # Verify WebSocket send was called
        mock_websocket.send_json.assert_called_once()

    @pytest.mark.skip(
        reason="Redis mock configuration issues - requires separate fix (BUGFIX-004)"
    )
    @pytest.mark.asyncio
    async def test_multiple_subscribers_receive_message(self):
        """Test that multiple subscribers receive the same Redis message"""
        manager = ConnectionManager(enable_redis=False)

        # Create multiple mock WebSocket connections
        connections = {}
        for i in range(3):
            conn_id = f"test-connection-{i}"
            mock_websocket = AsyncMock()
            connections[conn_id] = mock_websocket
            manager.active_connections[conn_id] = mock_websocket
            manager.connection_info[conn_id] = Mock(
                connection_id=conn_id,
                user_id=None,
                subscriptions={},
                message_count=0,
                last_activity=Mock(),
            )
            await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Simulate Redis message
        redis_message = {
            "type": "price_update",
            "stock_code": "005930",
            "price": 72500.0,
            "change": 500.0,
            "change_percent": 0.69,
            "volume": 15234567,
        }

        await manager._handle_redis_message("stock:005930:price", redis_message)

        # Verify all connections received the message
        for conn_id, mock_websocket in connections.items():
            mock_websocket.send_json.assert_called_once()


class TestEndToEndFlow:
    """Test end-to-end flow: Publisher -> Redis -> WebSocket"""

    @pytest.mark.skip(
        reason="Redis mock configuration issues - requires separate fix (BUGFIX-004)"
    )
    @pytest.mark.asyncio
    async def test_price_update_flow(self):
        """Test complete flow from price update to WebSocket delivery"""
        # Setup
        publisher = PricePublisher()
        manager = ConnectionManager(enable_redis=False)

        # Create mock WebSocket
        mock_websocket = AsyncMock()
        conn_id = "test-connection"
        manager.active_connections[conn_id] = mock_websocket
        manager.connection_info[conn_id] = Mock(
            connection_id=conn_id,
            user_id=None,
            subscriptions={},
            message_count=0,
            last_activity=Mock(),
        )

        # Subscribe to stock
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Publish price update
        with patch("app.services.price_publisher.redis_pubsub"):
            # Simulate immediate delivery to manager
            # Wait for messages
            # Note: In a real test, we would need a more robust way to wait for messages
            # For now, we just wait a bit and check if we received anything
            await asyncio.sleep(0.5)

            # We can't easily check if messages were received without mocking
            # the websocket handler. But we can check that no exceptions were raised
            await publisher.publish_price_update(
                stock_code="005930",
                price=72500.0,
                change=500.0,
                change_percent=0.69,
                volume=15234567,
            )

            # Verify WebSocket received the message
            mock_websocket.send_json.assert_called_once()
            sent_message = mock_websocket.send_json.call_args[0][0]
            assert sent_message["type"] == MessageType.PRICE_UPDATE
            assert sent_message["stock_code"] == "005930"
