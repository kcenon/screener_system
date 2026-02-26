"""Redis cache manager"""

import json
from typing import Any, Optional

from redis import asyncio as aioredis

from app.core.config import settings


class CacheManager:
    """Async Redis cache manager"""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.redis:
            return None

        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful
        """
        if not self.redis:
            return False

        try:
            serialized = json.dumps(value)
        except (TypeError, ValueError):
            serialized = str(value)

        if ttl:
            return await self.redis.setex(key, ttl, serialized)
        return await self.redis.set(key, serialized)

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if key was deleted
        """
        if not self.redis:
            return False

        result = await self.redis.delete(key)
        return bool(result)

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        if not self.redis:
            return False

        return bool(await self.redis.exists(key))

    async def clear(self, pattern: str = "*") -> int:
        """
        Clear cache by pattern

        Args:
            pattern: Key pattern (default: all keys)

        Returns:
            Number of keys deleted
        """
        if not self.redis:
            return 0

        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0


# Global cache manager instance
cache_manager = CacheManager()


async def get_cache() -> CacheManager:
    """Dependency to get cache manager"""
    return cache_manager
