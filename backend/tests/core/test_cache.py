"""Tests for Redis cache manager"""

import json
from unittest.mock import AsyncMock, patch

import pytest
from app.core.cache import CacheManager


class TestCacheManager:
    """Test suite for CacheManager"""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager instance"""
        return CacheManager()

    @pytest.mark.asyncio
    async def test_connect_success(self, cache_manager):
        """Test successful Redis connection"""
        mock_redis = AsyncMock()

        async def mock_from_url(*args, **kwargs):
            return mock_redis

        with patch("app.core.cache.aioredis.from_url", side_effect=mock_from_url):
            await cache_manager.connect()

            assert cache_manager.redis is mock_redis

    @pytest.mark.asyncio
    async def test_disconnect_with_active_connection(self, cache_manager):
        """Test disconnecting when Redis is connected"""
        mock_redis = AsyncMock()
        cache_manager.redis = mock_redis

        await cache_manager.disconnect()

        mock_redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_without_connection(self, cache_manager):
        """Test disconnecting when Redis is not connected"""
        cache_manager.redis = None

        # Should not raise an error
        await cache_manager.disconnect()

    @pytest.mark.asyncio
    async def test_get_with_json_value(self, cache_manager):
        """Test getting a JSON-serializable value"""
        mock_redis = AsyncMock()
        test_data = {"key": "value", "number": 123}
        mock_redis.get.return_value = json.dumps(test_data)
        cache_manager.redis = mock_redis

        result = await cache_manager.get("test_key")

        assert result == test_data
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_with_string_value(self, cache_manager):
        """Test getting a plain string value"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "plain_string"
        cache_manager.redis = mock_redis

        result = await cache_manager.get("test_key")

        # Should return the plain string if JSON decode fails
        assert result == "plain_string"

    @pytest.mark.asyncio
    async def test_get_with_none_value(self, cache_manager):
        """Test getting a non-existent key"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        cache_manager.redis = mock_redis

        result = await cache_manager.get("nonexistent_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_without_redis_connection(self, cache_manager):
        """Test getting value when Redis is not connected"""
        cache_manager.redis = None

        result = await cache_manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_with_json_serializable_value(self, cache_manager):
        """Test setting a JSON-serializable value"""
        mock_redis = AsyncMock()
        mock_redis.set.return_value = True
        cache_manager.redis = mock_redis

        test_data = {"key": "value", "list": [1, 2, 3]}
        result = await cache_manager.set("test_key", test_data)

        assert result is True
        mock_redis.set.assert_called_once_with("test_key", json.dumps(test_data))

    @pytest.mark.asyncio
    async def test_set_with_ttl(self, cache_manager):
        """Test setting a value with TTL"""
        mock_redis = AsyncMock()
        mock_redis.setex.return_value = True
        cache_manager.redis = mock_redis

        test_data = {"key": "value"}
        ttl = 300
        result = await cache_manager.set("test_key", test_data, ttl=ttl)

        assert result is True
        mock_redis.setex.assert_called_once_with("test_key", ttl, json.dumps(test_data))

    @pytest.mark.asyncio
    async def test_set_with_non_serializable_value(self, cache_manager):
        """Test setting a non-JSON-serializable value"""
        mock_redis = AsyncMock()
        mock_redis.set.return_value = True
        cache_manager.redis = mock_redis

        # Create a non-serializable object
        class CustomObject:
            pass

        test_obj = CustomObject()
        result = await cache_manager.set("test_key", test_obj)

        assert result is True
        # Should convert to string
        mock_redis.set.assert_called_once()
        called_args = mock_redis.set.call_args[0]
        assert called_args[0] == "test_key"
        assert isinstance(called_args[1], str)

    @pytest.mark.asyncio
    async def test_set_without_redis_connection(self, cache_manager):
        """Test setting value when Redis is not connected"""
        cache_manager.redis = None

        result = await cache_manager.set("test_key", "value")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_existing_key(self, cache_manager):
        """Test deleting an existing key"""
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 1  # Key was deleted
        cache_manager.redis = mock_redis

        result = await cache_manager.delete("test_key")

        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, cache_manager):
        """Test deleting a non-existent key"""
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 0  # Key did not exist
        cache_manager.redis = mock_redis

        result = await cache_manager.delete("nonexistent_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_without_redis_connection(self, cache_manager):
        """Test deleting when Redis is not connected"""
        cache_manager.redis = None

        result = await cache_manager.delete("test_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_true(self, cache_manager):
        """Test checking if key exists (exists)"""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 1
        cache_manager.redis = mock_redis

        result = await cache_manager.exists("test_key")

        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_exists_false(self, cache_manager):
        """Test checking if key exists (does not exist)"""
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0
        cache_manager.redis = mock_redis

        result = await cache_manager.exists("nonexistent_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_without_redis_connection(self, cache_manager):
        """Test exists check when Redis is not connected"""
        cache_manager.redis = None

        result = await cache_manager.exists("test_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_clear_with_pattern(self, cache_manager):
        """Test clearing cache with pattern"""
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = ["key1", "key2", "key3"]
        mock_redis.delete.return_value = 3
        cache_manager.redis = mock_redis

        result = await cache_manager.clear("test:*")

        assert result == 3
        mock_redis.keys.assert_called_once_with("test:*")
        mock_redis.delete.assert_called_once_with("key1", "key2", "key3")

    @pytest.mark.asyncio
    async def test_clear_with_default_pattern(self, cache_manager):
        """Test clearing all cache (default pattern)"""
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = ["key1", "key2"]
        mock_redis.delete.return_value = 2
        cache_manager.redis = mock_redis

        result = await cache_manager.clear()

        assert result == 2
        mock_redis.keys.assert_called_once_with("*")

    @pytest.mark.asyncio
    async def test_clear_with_no_matching_keys(self, cache_manager):
        """Test clearing when no keys match pattern"""
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = []
        cache_manager.redis = mock_redis

        result = await cache_manager.clear("nonexistent:*")

        assert result == 0
        mock_redis.keys.assert_called_once_with("nonexistent:*")
        mock_redis.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_clear_without_redis_connection(self, cache_manager):
        """Test clearing when Redis is not connected"""
        cache_manager.redis = None

        result = await cache_manager.clear()

        assert result == 0


class TestCacheManagerDependency:
    """Test cache manager dependency injection"""

    @pytest.mark.asyncio
    async def test_get_cache_returns_singleton(self):
        """Test that get_cache returns the same instance"""
        from app.core.cache import get_cache

        cache1 = await get_cache()
        cache2 = await get_cache()

        assert cache1 is cache2
