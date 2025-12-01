"""Redis Pub/Sub client for multi-instance WebSocket support"""

import asyncio
import json
from typing import Any, Callable, Dict, Optional, Set

import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import logger
from redis.asyncio.client import PubSub


class RedisPubSubClient:
    """
    Redis Pub/Sub client for broadcasting messages across multiple server instances.

    This enables:
    - Multi-instance WebSocket support with load balancing
    - Decoupled data publishing from WebSocket connections
    - Horizontal scalability

    Channel Naming Convention:
    - stock:{stock_code}:price - Price updates for specific stock
    - stock:{stock_code}:orderbook - Order book updates
    - market:{market}:status - Market status (KOSPI, KOSDAQ)
    - alerts:{user_id} - User-specific alerts
    """

    def __init__(self):
        """Initialize Redis Pub/Sub client"""
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[PubSub] = None
        self._subscribers: Dict[str, Set[Callable]] = {}
        self._listener_task: Optional[asyncio.Task] = None
        self._running = False

    async def connect(self):
        """Connect to Redis server"""
        try:
            # Parse Redis URL
            self._redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )

            # Test connection
            await self._redis.ping()

            # Create PubSub instance
            self._pubsub = self._redis.pubsub()

            logger.info(f"Connected to Redis Pub/Sub: {settings.REDIS_URL}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis server"""
        self._running = False

        # Cancel listener task
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        # Unsubscribe all channels
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()

        # Close Redis connection
        if self._redis:
            await self._redis.close()

        logger.info("Disconnected from Redis Pub/Sub")

    async def publish(
        self,
        channel: str,
        message: Dict[str, Any],
    ) -> int:
        """
        Publish a message to a Redis channel.

        Args:
            channel: Channel name
            message: Message data (will be JSON-serialized)

        Returns:
            Number of subscribers that received the message
        """
        if not self._redis:
            raise RuntimeError("Redis client not connected")

        try:
            # Serialize message to JSON
            message_str = json.dumps(message)

            # Publish to channel
            receivers = await self._redis.publish(channel, message_str)

            logger.debug(
                f"Published to {channel}: {len(message_str)} bytes "
                f"({receivers} receivers)"
            )

            return receivers

        except Exception as e:
            logger.error(f"Error publishing to {channel}: {e}")
            raise

    async def subscribe(
        self,
        channel: str,
        handler: Callable[[str, Dict[str, Any]], Any],
    ):
        """
        Subscribe to a Redis channel.

        Args:
            channel: Channel name (supports wildcards: stock:*:price)
            handler: Async callback function(channel, message)
        """
        if not self._pubsub:
            raise RuntimeError("PubSub not initialized")

        # Add handler to subscribers
        if channel not in self._subscribers:
            self._subscribers[channel] = set()
        self._subscribers[channel].add(handler)

        # Subscribe to channel
        if "*" in channel or "?" in channel:
            # Pattern subscription (wildcard)
            await self._pubsub.psubscribe(channel)
            logger.info(f"Subscribed to pattern: {channel}")
        else:
            # Exact channel subscription
            await self._pubsub.subscribe(channel)
            logger.info(f"Subscribed to channel: {channel}")

        # Start listener if not running
        if not self._running:
            self._running = True
            self._listener_task = asyncio.create_task(self._listen())

    async def unsubscribe(self, channel: str):
        """
        Unsubscribe from a Redis channel.

        Args:
            channel: Channel name
        """
        if not self._pubsub:
            return

        # Remove subscribers
        self._subscribers.pop(channel, None)

        # Unsubscribe from channel
        if "*" in channel or "?" in channel:
            await self._pubsub.punsubscribe(channel)
            logger.info(f"Unsubscribed from pattern: {channel}")
        else:
            await self._pubsub.unsubscribe(channel)
            logger.info(f"Unsubscribed from channel: {channel}")

    async def _listen(self):
        """
        Listen for messages from subscribed channels.

        This runs in a background task and dispatches messages to handlers.
        """
        if not self._pubsub:
            return

        logger.info("Starting Redis Pub/Sub listener")

        try:
            async for message in self._pubsub.listen():
                if not self._running:
                    break

                # Skip subscription confirmation messages
                if message["type"] not in ("message", "pmessage"):
                    continue

                try:
                    # Extract channel and data
                    if message["type"] == "pmessage":
                        # Pattern match
                        pattern = message["pattern"]
                        channel = message["channel"]
                    else:
                        # Exact match
                        pattern = None
                        channel = message["channel"]

                    data_str = message["data"]

                    # Parse JSON
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON from {channel}: {e}")
                        continue

                    # Find matching handlers
                    handlers = set()

                    # Add exact match handlers
                    if channel in self._subscribers:
                        handlers.update(self._subscribers[channel])

                    # Add pattern match handlers
                    if pattern:
                        if pattern in self._subscribers:
                            handlers.update(self._subscribers[pattern])

                    # Call all handlers
                    for handler in handlers:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(channel, data)
                            else:
                                handler(channel, data)
                        except Exception as e:
                            logger.error(f"Error in handler for {channel}: {e}")

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except asyncio.CancelledError:
            logger.info("Redis Pub/Sub listener cancelled")
            raise

        except Exception as e:
            logger.error(f"Error in Redis Pub/Sub listener: {e}")

        finally:
            logger.info("Redis Pub/Sub listener stopped")

    def is_connected(self) -> bool:
        """Check if connected to Redis"""
        return self._redis is not None

    def get_subscriber_count(self) -> int:
        """Get total number of subscribed channels"""
        return len(self._subscribers)


# Global Redis Pub/Sub instance
redis_pubsub = RedisPubSubClient()
