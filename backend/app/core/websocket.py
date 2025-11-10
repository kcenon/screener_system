"""WebSocket connection manager with Redis Pub/Sub support"""

import asyncio
import json
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.core.logging import logger
from app.schemas.websocket import (ConnectionInfo, ErrorMessage, MessageType,
                                   PongMessage, SubscriptionType,
                                   WebSocketMessage)


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.

    This class handles:
    - Connection lifecycle (connect, disconnect)
    - Message sending (unicast, multicast, broadcast)
    - Subscription management
    - Heartbeat/ping-pong mechanism
    """

    def __init__(self, enable_redis: bool = True):
        """
        Initialize connection manager.

        Args:
            enable_redis: Enable Redis Pub/Sub for multi-instance support
        """
        # Active connections: connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Connection metadata: connection_id -> ConnectionInfo
        self.connection_info: Dict[str, ConnectionInfo] = {}

        # Subscriptions: subscription_type -> target -> Set[connection_id]
        # Example: {"stock": {"005930": {"conn1", "conn2"}}}
        self.subscriptions: Dict[
            SubscriptionType, Dict[str, Set[str]]
        ] = defaultdict(lambda: defaultdict(set))

        # Reverse index: connection_id -> Dict[subscription_type, Set[targets]]
        # For fast unsubscribe on disconnect
        self.connection_subscriptions: Dict[
            str, Dict[SubscriptionType, Set[str]]
        ] = defaultdict(lambda: defaultdict(set))

        # Message sequence counter for ordering
        self._sequence_counter = 0
        self._sequence_lock = asyncio.Lock()

        # Heartbeat task
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._heartbeat_interval = 30  # seconds

        # Redis Pub/Sub integration
        self._enable_redis = enable_redis
        self._redis_initialized = False
        self._redis_channels: Set[str] = set()  # Track subscribed Redis channels

    async def initialize_redis(self):
        """Initialize Redis Pub/Sub connection"""
        if not self._enable_redis or self._redis_initialized:
            return

        try:
            from app.core.redis_pubsub import redis_pubsub

            # Connect to Redis
            await redis_pubsub.connect()
            self._redis_initialized = True

            logger.info("Redis Pub/Sub initialized for WebSocket")

        except Exception as e:
            logger.warning(f"Failed to initialize Redis Pub/Sub: {e}")
            logger.warning("WebSocket will run in single-instance mode")
            self._enable_redis = False

    async def _next_sequence(self) -> int:
        """Get next message sequence number (thread-safe)"""
        async with self._sequence_lock:
            self._sequence_counter += 1
            return self._sequence_counter

    async def _handle_redis_message(self, channel: str, data: Dict[str, Any]):
        """
        Handle incoming message from Redis Pub/Sub.

        This broadcasts Redis messages to subscribed WebSocket connections.

        Args:
            channel: Redis channel name (e.g., "stock:005930:price")
            data: Message data
        """
        try:
            # Parse channel to determine subscription type and target
            # Channel format: {type}:{target}:{subtype}
            # Examples:
            #   stock:005930:price -> type=stock, target=005930
            #   market:KOSPI:status -> type=market, target=KOSPI

            parts = channel.split(":")
            if len(parts) < 2:
                logger.warning(f"Invalid channel format: {channel}")
                return

            channel_type = parts[0]
            target = parts[1]

            # Map channel type to subscription type
            type_mapping = {
                "stock": SubscriptionType.STOCK,
                "market": SubscriptionType.MARKET,
                "sector": SubscriptionType.SECTOR,
                "watchlist": SubscriptionType.WATCHLIST,
            }

            subscription_type = type_mapping.get(channel_type)
            if not subscription_type:
                logger.warning(f"Unknown channel type: {channel_type}")
                return

            # Create WebSocket message from Redis data
            # Data should already have correct schema from publisher
            message = WebSocketMessage(**data)

            # Send to all subscribers
            await self.send_to_subscribers(
                subscription_type=subscription_type,
                target=target,
                message=message,
            )

            logger.debug(
                f"Forwarded Redis message from {channel} to "
                f"{len(self.get_subscribers(subscription_type, target))} subscribers"
            )

        except Exception as e:
            logger.error(f"Error handling Redis message from {channel}: {e}")

    async def connect(
        self, websocket: WebSocket, user_id: Optional[str] = None
    ) -> str:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
            user_id: Optional authenticated user ID

        Returns:
            connection_id: Unique connection identifier
        """
        await websocket.accept()

        # Generate unique connection ID
        connection_id = str(uuid.uuid4())

        # Register connection
        self.active_connections[connection_id] = websocket

        # Create connection info
        info = ConnectionInfo(
            connection_id=connection_id,
            user_id=user_id,
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        self.connection_info[connection_id] = info

        logger.info(
            f"WebSocket connected: {connection_id} "
            f"(user: {user_id or 'anonymous'}, "
            f"total: {len(self.active_connections)})"
        )

        # Start heartbeat if not running
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        return connection_id

    async def disconnect(self, connection_id: str):
        """
        Disconnect and clean up a WebSocket connection.

        Args:
            connection_id: Connection to disconnect
        """
        # Remove from active connections
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        # Clean up subscriptions
        if connection_id in self.connection_subscriptions:
            for sub_type, targets in self.connection_subscriptions[
                connection_id
            ].items():
                for target in targets:
                    self.subscriptions[sub_type][target].discard(connection_id)
                    # Clean up empty subscription sets to prevent memory leak
                    if not self.subscriptions[sub_type][target]:
                        del self.subscriptions[sub_type][target]

            del self.connection_subscriptions[connection_id]

        # Remove connection info
        info = self.connection_info.pop(connection_id, None)

        user_id = info.user_id if info else "unknown"
        logger.info(
            f"WebSocket disconnected: {connection_id} "
            f"(user: {user_id}, remaining: {len(self.active_connections)})"
        )

        # Stop heartbeat if no connections
        if not self.active_connections and self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

    async def send_message(
        self, connection_id: str, message: WebSocketMessage
    ) -> bool:
        """
        Send a message to a specific connection.

        Args:
            connection_id: Target connection
            message: Message to send

        Returns:
            True if sent successfully, False otherwise
        """
        websocket = self.active_connections.get(connection_id)
        if not websocket:
            return False

        try:
            # Add sequence number if not present
            if message.sequence is None:
                message.sequence = await self._next_sequence()

            # Send as JSON
            await websocket.send_json(message.model_dump(mode="json"))

            # Update activity timestamp
            if connection_id in self.connection_info:
                self.connection_info[connection_id].last_activity = (
                    datetime.utcnow()
                )
                self.connection_info[connection_id].message_count += 1

            return True

        except WebSocketDisconnect:
            logger.warning(f"Connection {connection_id} disconnected during send")
            await self.disconnect(connection_id)
            return False

        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            return False

    async def send_error(
        self, connection_id: str, code: str, message: str, details: Optional[Dict] = None
    ):
        """
        Send an error message to a connection.

        Args:
            connection_id: Target connection
            code: Error code
            message: Error message
            details: Optional error details
        """
        error_msg = ErrorMessage(code=code, message=message, details=details)
        await self.send_message(connection_id, error_msg)

    async def broadcast(self, message: WebSocketMessage, exclude: Optional[Set[str]] = None):
        """
        Broadcast a message to all connections.

        Args:
            message: Message to broadcast
            exclude: Set of connection IDs to exclude
        """
        exclude = exclude or set()

        # Send to all connections
        send_tasks = [
            self.send_message(conn_id, message)
            for conn_id in self.active_connections.keys()
            if conn_id not in exclude
        ]

        if send_tasks:
            await asyncio.gather(*send_tasks, return_exceptions=True)

    async def send_to_subscribers(
        self,
        subscription_type: SubscriptionType,
        target: str,
        message: WebSocketMessage,
    ):
        """
        Send a message to all subscribers of a specific target.

        Args:
            subscription_type: Type of subscription
            target: Subscription target (stock code, market, etc.)
            message: Message to send
        """
        subscribers = self.subscriptions[subscription_type].get(target, set())

        if not subscribers:
            return

        # Send to all subscribers
        send_tasks = [
            self.send_message(conn_id, message) for conn_id in subscribers
        ]

        await asyncio.gather(*send_tasks, return_exceptions=True)

    async def subscribe(
        self, connection_id: str, subscription_type: SubscriptionType, target: str
    ):
        """
        Subscribe a connection to updates.

        Also subscribes to Redis channel if enabled and not already subscribed.

        Args:
            connection_id: Connection to subscribe
            subscription_type: Type of subscription
            target: Subscription target
        """
        # Add to subscriptions
        self.subscriptions[subscription_type][target].add(connection_id)

        # Add to reverse index
        self.connection_subscriptions[connection_id][subscription_type].add(target)

        # Update connection info
        if connection_id in self.connection_info:
            info = self.connection_info[connection_id]
            if subscription_type not in info.subscriptions:
                info.subscriptions[subscription_type] = []
            if target not in info.subscriptions[subscription_type]:
                info.subscriptions[subscription_type].append(target)

        # Subscribe to Redis channel if this is the first subscriber
        if self._enable_redis and self._redis_initialized:
            await self._subscribe_redis_channel(subscription_type, target)

        logger.debug(
            f"Subscribed {connection_id} to {subscription_type.value}:{target}"
        )

    async def _subscribe_redis_channel(
        self, subscription_type: SubscriptionType, target: str
    ):
        """
        Subscribe to Redis channel for a subscription type and target.

        Only subscribes if not already subscribed to avoid duplicates.

        Args:
            subscription_type: Type of subscription
            target: Subscription target
        """
        try:
            from app.core.redis_pubsub import redis_pubsub

            # Map subscription type to Redis channel pattern
            channel_patterns = {
                SubscriptionType.STOCK: f"stock:{target}:*",
                SubscriptionType.MARKET: f"market:{target}:*",
                SubscriptionType.SECTOR: f"sector:{target}:*",
                SubscriptionType.WATCHLIST: f"watchlist:{target}:*",
            }

            channel_pattern = channel_patterns.get(subscription_type)
            if not channel_pattern:
                return

            # Check if already subscribed
            if channel_pattern in self._redis_channels:
                return

            # Subscribe to Redis channel
            await redis_pubsub.subscribe(
                channel_pattern,
                self._handle_redis_message,
            )

            self._redis_channels.add(channel_pattern)

            logger.debug(f"Subscribed to Redis channel: {channel_pattern}")

        except Exception as e:
            logger.error(f"Error subscribing to Redis channel: {e}")

    def unsubscribe(
        self, connection_id: str, subscription_type: SubscriptionType, target: str
    ):
        """
        Unsubscribe a connection from updates.

        Args:
            connection_id: Connection to unsubscribe
            subscription_type: Type of subscription
            target: Subscription target
        """
        # Remove from subscriptions
        self.subscriptions[subscription_type][target].discard(connection_id)
        # Clean up empty subscription sets to prevent memory leak
        if not self.subscriptions[subscription_type][target]:
            del self.subscriptions[subscription_type][target]

        # Remove from reverse index
        self.connection_subscriptions[connection_id][subscription_type].discard(
            target
        )

        # Update connection info
        if connection_id in self.connection_info:
            info = self.connection_info[connection_id]
            if (
                subscription_type in info.subscriptions
                and target in info.subscriptions[subscription_type]
            ):
                info.subscriptions[subscription_type].remove(target)

        logger.debug(
            f"Unsubscribed {connection_id} from {subscription_type.value}:{target}"
        )

    def get_subscribers(
        self, subscription_type: SubscriptionType, target: str
    ) -> Set[str]:
        """
        Get all subscribers for a specific target.

        Args:
            subscription_type: Type of subscription
            target: Subscription target

        Returns:
            Set of connection IDs
        """
        return self.subscriptions[subscription_type].get(target, set()).copy()

    def get_connection_info(self, connection_id: str) -> Optional[ConnectionInfo]:
        """
        Get connection information.

        Args:
            connection_id: Connection ID

        Returns:
            ConnectionInfo or None if not found
        """
        return self.connection_info.get(connection_id)

    async def _heartbeat_loop(self):
        """
        Periodic heartbeat to detect dead connections.

        Sends ping messages to all connections at regular intervals.
        """
        logger.info("Starting WebSocket heartbeat loop")

        try:
            while self.active_connections:
                await asyncio.sleep(self._heartbeat_interval)

                # Send ping to all connections
                dead_connections = []

                for conn_id, websocket in self.active_connections.items():
                    try:
                        ping_msg = PongMessage()
                        await websocket.send_json(
                            ping_msg.model_dump(mode="json")
                        )
                    except Exception as e:
                        logger.warning(
                            f"Heartbeat failed for {conn_id}: {e}"
                        )
                        dead_connections.append(conn_id)

                # Clean up dead connections
                for conn_id in dead_connections:
                    await self.disconnect(conn_id)

        except asyncio.CancelledError:
            logger.info("WebSocket heartbeat loop cancelled")

        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection manager statistics.

        Returns:
            Dictionary with statistics
        """
        total_subscriptions = sum(
            len(targets)
            for sub_type in self.subscriptions.values()
            for targets in sub_type.values()
        )

        return {
            "active_connections": len(self.active_connections),
            "total_subscriptions": total_subscriptions,
            "subscriptions_by_type": {
                sub_type.value: sum(
                    len(subs) for subs in targets.values()
                )
                for sub_type, targets in self.subscriptions.items()
            },
            "messages_sent": self._sequence_counter,
        }


# Global connection manager instance
connection_manager = ConnectionManager()
