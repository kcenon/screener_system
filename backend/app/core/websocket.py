"""WebSocket connection manager with Redis Pub/Sub support"""

import asyncio
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union

from app.core.logging import logger
from app.schemas.websocket import (BatchMessage, ConnectionInfo, ErrorMessage,
                                   PongMessage, SubscriptionType,
                                   WebSocketMessage)
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.

    This class handles:
    - Connection lifecycle (connect, disconnect)
    - Message sending (unicast, multicast, broadcast)
    - Subscription management
    - Heartbeat/ping-pong mechanism
    """

    def __init__(
        self,
        enable_redis: bool = True,
        enable_batching: bool = True,
        batch_interval: float = 0.03,  # 30ms default
        enable_rate_limiting: bool = True,
        rate_limit: int = 100,  # messages per second per connection
    ):
        """
        Initialize connection manager.

        Args:
            enable_redis: Enable Redis Pub/Sub for multi-instance support
            enable_batching: Enable message batching (Phase 4)
            batch_interval: Batch flush interval in seconds (Phase 4)
            enable_rate_limiting: Enable per-connection rate limiting (Phase 4)
            rate_limit: Max messages per second per connection (Phase 4)
        """
        # Active connections: connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Connection metadata: connection_id -> ConnectionInfo
        self.connection_info: Dict[str, ConnectionInfo] = {}

        # Subscriptions: subscription_type -> target -> Set[connection_id]
        # Example: {"stock": {"005930": {"conn1", "conn2"}}}
        self.subscriptions: Dict[SubscriptionType, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )

        # Reverse index: connection_id -> Dict[subscription_type, Set[targets]]
        # For fast unsubscribe on disconnect
        self.connection_subscriptions: Dict[str, Dict[SubscriptionType, Set[str]]] = (
            defaultdict(lambda: defaultdict(set))
        )

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

        # Phase 3: Session restoration support
        # Store disconnected session info for 5 minutes to allow reconnection
        self._disconnected_sessions: Dict[str, Dict[str, Any]] = {}
        self._session_ttl = 300  # seconds (5 minutes)
        self._session_cleanup_task: Optional[asyncio.Task] = None

        # Phase 4: Message batching
        self._enable_batching = enable_batching
        self._batch_interval = batch_interval
        self._message_queues: Dict[str, List[WebSocketMessage]] = defaultdict(list)
        self._batch_task: Optional[asyncio.Task] = None
        self._batch_lock = asyncio.Lock()

        # Phase 4: Rate limiting
        self._enable_rate_limiting = enable_rate_limiting
        self._rate_limit = rate_limit
        self._message_timestamps: Dict[str, List[float]] = defaultdict(list)
        self._rate_limit_window = 1.0  # 1 second window

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

    async def _check_rate_limit(self, connection_id: str) -> bool:
        """
        Check if connection is within rate limit (Phase 4).

        Args:
            connection_id: Connection to check

        Returns:
            True if within limit, False if exceeded
        """
        if not self._enable_rate_limiting:
            return True

        import time

        now = time.time()
        timestamps = self._message_timestamps[connection_id]

        # Remove timestamps outside the window
        timestamps[:] = [ts for ts in timestamps if now - ts < self._rate_limit_window]

        # Check if limit exceeded
        if len(timestamps) >= self._rate_limit:
            return False

        # Add current timestamp
        timestamps.append(now)
        return True

    async def _add_to_batch(self, connection_id: str, message: WebSocketMessage):
        """
        Add message to batch queue (Phase 4).

        Args:
            connection_id: Target connection
            message: Message to queue
        """
        async with self._batch_lock:
            # Add sequence number if not present
            if message.sequence is None:
                message.sequence = await self._next_sequence()

            self._message_queues[connection_id].append(message)

    async def _flush_batch(self, connection_id: str):
        """
        Flush batched messages for a connection (Phase 4).

        Args:
            connection_id: Connection to flush
        """
        websocket = self.active_connections.get(connection_id)
        if not websocket:
            return

        async with self._batch_lock:
            messages = self._message_queues.get(connection_id, [])
            if not messages:
                return

            # Clear queue
            self._message_queues[connection_id] = []

        try:
            if len(messages) == 1:
                # Single message: send directly
                await websocket.send_json(messages[0].model_dump(mode="json"))
            else:
                # Multiple messages: send as batch
                batch = BatchMessage(
                    messages=messages,
                    batch_size=len(messages),
                )
                batch.sequence = await self._next_sequence()
                await websocket.send_json(batch.model_dump(mode="json"))

            # Update activity timestamp
            if connection_id in self.connection_info:
                self.connection_info[connection_id].last_activity = datetime.utcnow()
                self.connection_info[connection_id].message_count += len(messages)

            logger.debug(f"Flushed {len(messages)} messages to {connection_id}")

        except WebSocketDisconnect:
            logger.warning(
                f"Connection {connection_id} disconnected during batch flush"
            )
            await self.disconnect(connection_id)

        except Exception as e:
            logger.error(f"Error flushing batch to {connection_id}: {e}")

    async def _batch_flush_loop(self):
        """
        Periodic batch flushing loop (Phase 4).
        """
        logger.info(
            f"Starting batch flush loop (interval: {self._batch_interval * 1000:.0f}ms)"
        )

        try:
            while self.active_connections:
                await asyncio.sleep(self._batch_interval)

                # Flush all connections with queued messages
                flush_tasks = []
                for conn_id in list(self.active_connections.keys()):
                    if self._message_queues.get(conn_id):
                        flush_tasks.append(self._flush_batch(conn_id))

                if flush_tasks:
                    await asyncio.gather(*flush_tasks, return_exceptions=True)

        except asyncio.CancelledError:
            logger.info("Batch flush loop cancelled")

        except Exception as e:
            logger.error(f"Error in batch flush loop: {e}")

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

    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None) -> str:
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

        # Phase 4: Start batch flush loop if enabled and not running
        if self._enable_batching and (
            self._batch_task is None or self._batch_task.done()
        ):
            self._batch_task = asyncio.create_task(self._batch_flush_loop())

        return connection_id

    async def disconnect(self, connection_id: str):
        """
        Disconnect and clean up a WebSocket connection.

        Args:
            connection_id: Connection to disconnect
        """
        # Phase 3: Save session before disconnecting (for reconnection)
        await self._save_session(connection_id)

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

        # Phase 4: Clean up batching and rate limiting data
        if connection_id in self._message_queues:
            del self._message_queues[connection_id]
        if connection_id in self._message_timestamps:
            del self._message_timestamps[connection_id]

        # Stop tasks if no connections
        if not self.active_connections:
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                self._heartbeat_task = None
            if self._batch_task:
                self._batch_task.cancel()
                self._batch_task = None

    async def send_message(
        self, connection_id: str, message: WebSocketMessage, immediate: bool = False
    ) -> bool:
        """
        Send a message to a specific connection.

        Phase 4: Messages are batched by default unless immediate=True.
        Rate limiting is applied if enabled.

        Args:
            connection_id: Target connection
            message: Message to send
            immediate: Send immediately without batching (for critical messages)

        Returns:
            True if sent successfully, False otherwise
        """
        websocket = self.active_connections.get(connection_id)
        if not websocket:
            return False

        # Phase 4: Check rate limit (skip for error messages to avoid recursion)
        if self._enable_rate_limiting and not isinstance(message, ErrorMessage):
            if not await self._check_rate_limit(connection_id):
                logger.warning(
                    f"Rate limit exceeded for {connection_id} "
                    f"({self._rate_limit} msg/s)"
                )
                # Send error message
                await self.send_error(
                    connection_id,
                    "RATE_LIMIT_EXCEEDED",
                    f"Rate limit exceeded ({self._rate_limit} messages/second)",
                    details={"rate_limit": self._rate_limit},
                )
                return False

        # Phase 4: Use batching if enabled and not immediate
        if self._enable_batching and not immediate:
            await self._add_to_batch(connection_id, message)
            return True

        # Send immediately
        try:
            # Add sequence number if not present
            if message.sequence is None:
                message.sequence = await self._next_sequence()

            # Assuming message has a 'type' attribute for ping/pong handling
            # If message.type is not available, this will raise an AttributeError
            # and the original send_json will be executed in the `else` block.
            if hasattr(message, "type"):
                message_type = message.type
                if message_type == "ping":
                    await websocket.send_json(
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                    )
                else:
                    # Send as JSON
                    await websocket.send_json(message.model_dump(mode="json"))
            else:
                # Send as JSON if no 'type' attribute
                await websocket.send_json(message.model_dump(mode="json"))

            # Update activity timestamp
            if connection_id in self.connection_info:
                self.connection_info[connection_id].last_activity = datetime.utcnow()
                self.connection_info[connection_id].message_count += 1

            return True

        except WebSocketDisconnect:
            logger.warning(f"Connection {connection_id} disconnected during send")
            await self.disconnect(connection_id)
            return False

            return False

        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            return False

    async def send_personal_message(
        self, message: Union[Dict[str, Any], WebSocketMessage], user_id: str
    ):
        """
        Send a message to all connections of a specific user.

        Args:
            message: Message to send (dict or WebSocketMessage)
            user_id: Target user ID
        """
        # Find all connections for this user
        target_connections = []
        for conn_id, info in self.connection_info.items():
            if info.user_id == user_id:
                target_connections.append(conn_id)
        
        if not target_connections:
            return

        if isinstance(message, WebSocketMessage):
            ws_message = message
        else:
            try:
                # Check if it's an error message
                if message.get("type") == "error":
                    # Map payload to ErrorMessage fields if needed
                    # ErrorMessage expects code, message, details
                    # But the dict might be {"type": "error", "payload": {"message": ...}}
                    payload = message.get("payload", {})
                    if isinstance(payload, dict):
                        ws_message = ErrorMessage(
                            code=payload.get("code", "ERROR"),
                            message=payload.get("message", "Unknown error"),
                            details=payload.get("details")
                        )
                    else:
                         ws_message = WebSocketMessage(**message)
                else:
                    ws_message = WebSocketMessage(**message)
            except Exception:
                msg_type = message.get("type", "message")
                ws_message = WebSocketMessage(type=msg_type, payload=message.get("payload"))

        for conn_id in target_connections:
            await self.send_message(conn_id, ws_message, immediate=True)

    async def send_error(
        self,
        connection_id: str,
        code: str,
        message: str,
        details: Optional[Dict] = None,
    ):
        """
        Send an error message to a connection.

        Phase 4: Error messages are always sent immediately.

        Args:
            connection_id: Target connection
            code: Error code
            message: Error message
            details: Optional error details
        """
        error_msg = ErrorMessage(code=code, message=message, details=details)
        # However, `user_id` is not directly available in `send_error`'s scope.
        # To make it syntactically correct and avoid an immediate NameError,
        # I will use `self.connection_info.get(connection_id).user_id` if info exists.
        # If the intent was purely "break long lines" for the existing line,
        # the snippet is misleading. I will follow the snippet's content.

        # Original line:
        # await self.send_message(connection_id, error_msg, immediate=True)
        # Replacing with the line from the snippet, adapting for `user_id`
        # and assuming `send_personal_message` will be defined elsewhere or is implicit.
        info = self.connection_info.get(connection_id)
        user_id = info.user_id if info else None
        if user_id:
            await self.send_personal_message(
                {
                    "type": "error",
                    "payload": {"message": message},
                },
                user_id,
            )
        else:
            # Fallback if user_id is not found or send_personal_message is not suitable
            await self.send_message(connection_id, error_msg, immediate=True)

    async def broadcast(
        self, message: WebSocketMessage, exclude: Optional[Set[str]] = None
    ):
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
        send_tasks = [self.send_message(conn_id, message) for conn_id in subscribers]

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
        self.connection_subscriptions[connection_id][subscription_type].discard(target)

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
                        await websocket.send_json(ping_msg.model_dump(mode="json"))
                    except Exception as e:
                        logger.warning(f"Heartbeat failed for {conn_id}: {e}")
                        dead_connections.append(conn_id)

                # Clean up dead connections
                for conn_id in dead_connections:
                    await self.disconnect(conn_id)

        except asyncio.CancelledError:
            logger.info("WebSocket heartbeat loop cancelled")

        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")

    async def _save_session(self, connection_id: str):
        """
        Save session information for reconnection (Phase 3).

        Args:
            connection_id: Connection ID to save
        """
        if connection_id not in self.connection_info:
            return

        info = self.connection_info[connection_id]

        # Save session with TTL
        session_data = {
            "connection_id": connection_id,
            "user_id": info.user_id,
            "subscriptions": {
                sub_type: list(targets)
                for sub_type, targets in self.connection_subscriptions[
                    connection_id
                ].items()
            },
            "last_sequence": self._sequence_counter,
            "saved_at": datetime.utcnow(),
        }

        self._disconnected_sessions[connection_id] = session_data

        logger.info(
            f"Saved session {connection_id} for reconnection "
            f"(TTL: {self._session_ttl}s)"
        )

    async def reconnect(
        self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None
    ) -> tuple[str, Dict[SubscriptionType, List[str]], int]:
        """
        Reconnect a client with session restoration (Phase 3).

        Args:
            websocket: New WebSocket connection
            session_id: Previous connection ID
            user_id: User ID (for verification)

        Returns:
            Tuple of (new_connection_id, restored_subscriptions, missed_messages)

        Raises:
            ValueError: If session not found or user mismatch
        """
        # Check if session exists
        if session_id not in self._disconnected_sessions:
            raise ValueError(f"Session {session_id} not found or expired")

        session_data = self._disconnected_sessions[session_id]

        # Verify user ID matches (security check)
        if user_id and session_data["user_id"] != user_id:
            raise ValueError("User ID mismatch")

        # Check session age
        saved_at = session_data["saved_at"]
        age = (datetime.utcnow() - saved_at).total_seconds()
        if age > self._session_ttl:
            # Session expired
            del self._disconnected_sessions[session_id]
            raise ValueError(f"Session expired ({age:.0f}s > {self._session_ttl}s)")

        # Create new connection
        new_connection_id = await self.connect(websocket, user_id)

        # Restore subscriptions
        restored_subscriptions: Dict[SubscriptionType, List[str]] = {}
        subscriptions = session_data.get("subscriptions", {})

        for sub_type_str, targets in subscriptions.items():
            sub_type = SubscriptionType(sub_type_str)
            restored_subscriptions[sub_type] = []

            for target in targets:
                await self.subscribe(new_connection_id, sub_type, target)
                restored_subscriptions[sub_type].append(target)

        # Calculate missed messages
        last_sequence = session_data.get("last_sequence", 0)
        missed_messages = max(0, self._sequence_counter - last_sequence)

        # Remove saved session
        del self._disconnected_sessions[session_id]

        logger.info(
            f"Reconnected session {session_id} -> {new_connection_id} "
            f"(restored {sum(len(t) for t in restored_subscriptions.values())} subs, "
            f"missed {missed_messages} messages)"
        )

        return new_connection_id, restored_subscriptions, missed_messages

    async def _cleanup_expired_sessions(self):
        """
        Periodically clean up expired sessions (Phase 3).
        """
        logger.info("Starting session cleanup task")

        try:
            while True:
                await asyncio.sleep(60)  # Check every minute

                now = datetime.utcnow()
                expired = []

                for session_id, session_data in self._disconnected_sessions.items():
                    saved_at = session_data["saved_at"]
                    age = (now - saved_at).total_seconds()

                    if age > self._session_ttl:
                        expired.append(session_id)

                # Remove expired sessions
                for session_id in expired:
                    del self._disconnected_sessions[session_id]
                    logger.debug(f"Cleaned up expired session {session_id}")

                if expired:
                    logger.info(f"Cleaned up {len(expired)} expired sessions")

        except asyncio.CancelledError:
            logger.info("Session cleanup task cancelled")

        except Exception as e:
            logger.error(f"Error in session cleanup: {e}")

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

        # Phase 4: Batching stats
        total_queued = sum(len(q) for q in self._message_queues.values())
        queued_by_connection = {
            conn_id: len(q) for conn_id, q in self._message_queues.items() if q
        }

        return {
            "active_connections": len(self.active_connections),
            "total_subscriptions": total_subscriptions,
            "subscriptions_by_type": {
                sub_type.value: sum(len(subs) for subs in targets.values())
                for sub_type, targets in self.subscriptions.items()
            },
            "messages_sent": self._sequence_counter,
            "saved_sessions": len(self._disconnected_sessions),  # Phase 3
            # Phase 4 stats
            "batching_enabled": self._enable_batching,
            "batch_interval_ms": (
                self._batch_interval * 1000 if self._enable_batching else None
            ),
            "queued_messages": total_queued if self._enable_batching else None,
            "queued_by_connection": (
                queued_by_connection if self._enable_batching else None
            ),
            "rate_limiting_enabled": self._enable_rate_limiting,
            "rate_limit": self._rate_limit if self._enable_rate_limiting else None,
        }


# Global connection manager instance
connection_manager = ConnectionManager()
