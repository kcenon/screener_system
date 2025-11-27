"""Tests for Redis Pub/Sub client"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.redis_pubsub import RedisPubSubClient, redis_pubsub


@pytest.fixture
def pubsub_client():
    """Create fresh RedisPubSubClient for each test"""
    client = RedisPubSubClient()
    yield client
    # Cleanup
    client._running = False


class TestRedisPubSubClientInit:
    """Test RedisPubSubClient initialization"""

    def test_init_default_values(self, pubsub_client: RedisPubSubClient):
        """Test initialization sets default values"""
        assert pubsub_client._redis is None
        assert pubsub_client._pubsub is None
        assert pubsub_client._subscribers == {}
        assert pubsub_client._listener_task is None
        assert pubsub_client._running is False

    def test_is_connected_false_initially(self, pubsub_client: RedisPubSubClient):
        """Test is_connected returns False when not connected"""
        assert pubsub_client.is_connected() is False

    def test_get_subscriber_count_zero_initially(self, pubsub_client: RedisPubSubClient):
        """Test subscriber count is zero initially"""
        assert pubsub_client.get_subscriber_count() == 0


class TestRedisPubSubConnect:
    """Test Redis connection functionality"""

    @pytest.mark.asyncio
    async def test_connect_success(self, pubsub_client: RedisPubSubClient):
        """Test successful Redis connection"""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.pubsub = MagicMock(return_value=AsyncMock())

        with patch("app.core.redis_pubsub.redis.from_url", return_value=mock_redis):
            await pubsub_client.connect()

            assert pubsub_client._redis is not None
            assert pubsub_client._pubsub is not None
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure_raises_exception(self, pubsub_client: RedisPubSubClient):
        """Test connection failure raises exception"""
        with patch(
            "app.core.redis_pubsub.redis.from_url",
            side_effect=Exception("Connection refused"),
        ):
            with pytest.raises(Exception, match="Connection refused"):
                await pubsub_client.connect()

    @pytest.mark.asyncio
    async def test_is_connected_true_after_connect(self, pubsub_client: RedisPubSubClient):
        """Test is_connected returns True after successful connection"""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_redis.pubsub = MagicMock(return_value=AsyncMock())

        with patch("app.core.redis_pubsub.redis.from_url", return_value=mock_redis):
            await pubsub_client.connect()
            assert pubsub_client.is_connected() is True


class TestRedisPubSubDisconnect:
    """Test Redis disconnection functionality"""

    @pytest.mark.asyncio
    async def test_disconnect_stops_running(self, pubsub_client: RedisPubSubClient):
        """Test disconnect sets _running to False"""
        pubsub_client._running = True
        pubsub_client._redis = None
        pubsub_client._pubsub = None

        await pubsub_client.disconnect()

        assert pubsub_client._running is False

    @pytest.mark.asyncio
    async def test_disconnect_cancels_listener_task(self, pubsub_client: RedisPubSubClient):
        """Test disconnect cancels listener task"""
        # Create a mock task that is both cancellable and awaitable
        # Real tasks raise CancelledError when awaited after cancel()
        class CancelledTaskMock:
            def __init__(self):
                self.cancel = MagicMock()

            def __await__(self):
                raise asyncio.CancelledError()
                yield  # pragma: no cover

        mock_task = CancelledTaskMock()

        pubsub_client._listener_task = mock_task
        pubsub_client._redis = None
        pubsub_client._pubsub = None

        await pubsub_client.disconnect()

        mock_task.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_unsubscribes_all(self, pubsub_client: RedisPubSubClient):
        """Test disconnect unsubscribes from all channels"""
        mock_pubsub = AsyncMock()
        mock_redis = AsyncMock()

        pubsub_client._pubsub = mock_pubsub
        pubsub_client._redis = mock_redis

        await pubsub_client.disconnect()

        mock_pubsub.unsubscribe.assert_called_once()
        mock_pubsub.close.assert_called_once()
        mock_redis.close.assert_called_once()


class TestRedisPubSubPublish:
    """Test Redis publish functionality"""

    @pytest.mark.asyncio
    async def test_publish_success(self, pubsub_client: RedisPubSubClient):
        """Test successful message publishing"""
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock(return_value=5)

        pubsub_client._redis = mock_redis

        message = {"stock_code": "005930", "price": 70000}
        receivers = await pubsub_client.publish("stock:005930:price", message)

        assert receivers == 5
        mock_redis.publish.assert_called_once_with(
            "stock:005930:price", json.dumps(message)
        )

    @pytest.mark.asyncio
    async def test_publish_without_connection_raises(self, pubsub_client: RedisPubSubClient):
        """Test publish raises error when not connected"""
        message = {"test": "data"}

        with pytest.raises(RuntimeError, match="Redis client not connected"):
            await pubsub_client.publish("test_channel", message)

    @pytest.mark.asyncio
    async def test_publish_error_propagates(self, pubsub_client: RedisPubSubClient):
        """Test publish error is propagated"""
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock(side_effect=Exception("Redis error"))

        pubsub_client._redis = mock_redis

        with pytest.raises(Exception, match="Redis error"):
            await pubsub_client.publish("test_channel", {"test": "data"})


class TestRedisPubSubSubscribe:
    """Test Redis subscribe functionality"""

    @pytest.mark.asyncio
    async def test_subscribe_exact_channel(self, pubsub_client: RedisPubSubClient):
        """Test subscribing to exact channel"""
        mock_pubsub = AsyncMock()
        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = False

        async def handler(channel, data):
            pass

        await pubsub_client.subscribe("stock:005930:price", handler)

        assert "stock:005930:price" in pubsub_client._subscribers
        assert handler in pubsub_client._subscribers["stock:005930:price"]
        mock_pubsub.subscribe.assert_called_once_with("stock:005930:price")

    @pytest.mark.asyncio
    async def test_subscribe_pattern_channel(self, pubsub_client: RedisPubSubClient):
        """Test subscribing to pattern channel with wildcard"""
        mock_pubsub = AsyncMock()
        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = False

        async def handler(channel, data):
            pass

        await pubsub_client.subscribe("stock:*:price", handler)

        mock_pubsub.psubscribe.assert_called_once_with("stock:*:price")

    @pytest.mark.asyncio
    async def test_subscribe_without_pubsub_raises(self, pubsub_client: RedisPubSubClient):
        """Test subscribe raises error when PubSub not initialized"""

        async def handler(channel, data):
            pass

        with pytest.raises(RuntimeError, match="PubSub not initialized"):
            await pubsub_client.subscribe("test_channel", handler)

    @pytest.mark.asyncio
    async def test_subscribe_starts_listener(self, pubsub_client: RedisPubSubClient):
        """Test subscribe starts listener task if not running"""
        mock_pubsub = AsyncMock()
        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = False

        async def handler(channel, data):
            pass

        with patch.object(pubsub_client, "_listen", new_callable=AsyncMock):
            await pubsub_client.subscribe("test_channel", handler)

            assert pubsub_client._running is True
            assert pubsub_client._listener_task is not None


class TestRedisPubSubUnsubscribe:
    """Test Redis unsubscribe functionality"""

    @pytest.mark.asyncio
    async def test_unsubscribe_exact_channel(self, pubsub_client: RedisPubSubClient):
        """Test unsubscribing from exact channel"""
        mock_pubsub = AsyncMock()
        pubsub_client._pubsub = mock_pubsub
        pubsub_client._subscribers["stock:005930:price"] = set()

        await pubsub_client.unsubscribe("stock:005930:price")

        assert "stock:005930:price" not in pubsub_client._subscribers
        mock_pubsub.unsubscribe.assert_called_once_with("stock:005930:price")

    @pytest.mark.asyncio
    async def test_unsubscribe_pattern_channel(self, pubsub_client: RedisPubSubClient):
        """Test unsubscribing from pattern channel"""
        mock_pubsub = AsyncMock()
        pubsub_client._pubsub = mock_pubsub
        pubsub_client._subscribers["stock:*:price"] = set()

        await pubsub_client.unsubscribe("stock:*:price")

        mock_pubsub.punsubscribe.assert_called_once_with("stock:*:price")

    @pytest.mark.asyncio
    async def test_unsubscribe_without_pubsub_returns(self, pubsub_client: RedisPubSubClient):
        """Test unsubscribe returns silently when PubSub not initialized"""
        await pubsub_client.unsubscribe("test_channel")  # Should not raise


class TestRedisPubSubListen:
    """Test Redis listener functionality"""

    @pytest.mark.asyncio
    async def test_listen_without_pubsub_returns(self, pubsub_client: RedisPubSubClient):
        """Test _listen returns when PubSub is None"""
        pubsub_client._pubsub = None
        await pubsub_client._listen()  # Should return without error

    @pytest.mark.asyncio
    async def test_listen_processes_message(self, pubsub_client: RedisPubSubClient):
        """Test _listen processes messages correctly"""
        received_data = []

        async def handler(channel, data):
            received_data.append((channel, data))

        mock_message = {
            "type": "message",
            "channel": "test_channel",
            "data": '{"test": "data"}',
        }

        async def mock_listen():
            yield mock_message
            pubsub_client._running = False

        mock_pubsub = AsyncMock()
        mock_pubsub.listen = mock_listen

        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = True
        pubsub_client._subscribers["test_channel"] = {handler}

        await pubsub_client._listen()

        assert len(received_data) == 1
        assert received_data[0] == ("test_channel", {"test": "data"})

    @pytest.mark.asyncio
    async def test_listen_skips_subscription_messages(self, pubsub_client: RedisPubSubClient):
        """Test _listen skips subscription confirmation messages"""
        received_data = []

        async def handler(channel, data):
            received_data.append((channel, data))

        async def mock_listen():
            yield {"type": "subscribe", "channel": "test_channel", "data": 1}
            pubsub_client._running = False

        mock_pubsub = AsyncMock()
        mock_pubsub.listen = mock_listen

        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = True
        pubsub_client._subscribers["test_channel"] = {handler}

        await pubsub_client._listen()

        assert len(received_data) == 0

    @pytest.mark.asyncio
    async def test_listen_handles_invalid_json(self, pubsub_client: RedisPubSubClient):
        """Test _listen handles invalid JSON gracefully"""
        received_data = []

        async def handler(channel, data):
            received_data.append((channel, data))

        async def mock_listen():
            yield {
                "type": "message",
                "channel": "test_channel",
                "data": "invalid json{",
            }
            pubsub_client._running = False

        mock_pubsub = AsyncMock()
        mock_pubsub.listen = mock_listen

        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = True
        pubsub_client._subscribers["test_channel"] = {handler}

        await pubsub_client._listen()

        assert len(received_data) == 0

    @pytest.mark.asyncio
    async def test_listen_handles_handler_exception(self, pubsub_client: RedisPubSubClient):
        """Test _listen handles handler exceptions gracefully"""

        async def failing_handler(channel, data):
            raise ValueError("Handler error")

        async def mock_listen():
            yield {
                "type": "message",
                "channel": "test_channel",
                "data": '{"test": "data"}',
            }
            pubsub_client._running = False

        mock_pubsub = AsyncMock()
        mock_pubsub.listen = mock_listen

        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = True
        pubsub_client._subscribers["test_channel"] = {failing_handler}

        # Should not raise
        await pubsub_client._listen()

    @pytest.mark.asyncio
    async def test_listen_handles_pattern_message(self, pubsub_client: RedisPubSubClient):
        """Test _listen handles pattern match messages"""
        received_data = []

        async def handler(channel, data):
            received_data.append((channel, data))

        async def mock_listen():
            yield {
                "type": "pmessage",
                "pattern": "stock:*:price",
                "channel": "stock:005930:price",
                "data": '{"price": 70000}',
            }
            pubsub_client._running = False

        mock_pubsub = AsyncMock()
        mock_pubsub.listen = mock_listen

        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = True
        pubsub_client._subscribers["stock:*:price"] = {handler}

        await pubsub_client._listen()

        assert len(received_data) == 1
        assert received_data[0] == ("stock:005930:price", {"price": 70000})

    @pytest.mark.asyncio
    async def test_listen_calls_sync_handler(self, pubsub_client: RedisPubSubClient):
        """Test _listen calls synchronous handlers correctly"""
        received_data = []

        def sync_handler(channel, data):
            received_data.append((channel, data))

        async def mock_listen():
            yield {
                "type": "message",
                "channel": "test_channel",
                "data": '{"test": "sync"}',
            }
            pubsub_client._running = False

        mock_pubsub = AsyncMock()
        mock_pubsub.listen = mock_listen

        pubsub_client._pubsub = mock_pubsub
        pubsub_client._running = True
        pubsub_client._subscribers["test_channel"] = {sync_handler}

        await pubsub_client._listen()

        assert len(received_data) == 1


class TestGlobalRedisPubSub:
    """Test global redis_pubsub instance"""

    def test_global_instance_exists(self):
        """Test global redis_pubsub instance is created"""
        assert redis_pubsub is not None
        assert isinstance(redis_pubsub, RedisPubSubClient)

    def test_global_instance_not_connected_initially(self):
        """Test global instance is not connected initially"""
        assert redis_pubsub.is_connected() is False
