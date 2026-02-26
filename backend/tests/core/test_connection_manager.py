"""Unit tests for WebSocket ConnectionManager"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.websocket import ConnectionManager
from app.schemas.websocket import (MessageType, PongMessage, PriceUpdate,
                                   SubscriptionType)


@pytest.fixture
def manager():
    """Create a ConnectionManager instance for testing"""
    # Disable Redis and batching for simpler unit tests
    return ConnectionManager(
        enable_redis=False,
        enable_batching=False,
        enable_rate_limiting=False,
    )


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket"""
    ws = Mock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    ws.receive_json = AsyncMock()
    return ws


class TestConnectionLifecycle:
    """Test connection lifecycle methods"""

    @pytest.mark.asyncio
    async def test_connect_new_client(self, manager, mock_websocket):
        """Test adding new WebSocket connection"""
        # Connect
        conn_id = await manager.connect(mock_websocket, user_id="test-user")

        # Verify connection
        assert conn_id in manager.active_connections
        assert manager.active_connections[conn_id] == mock_websocket
        assert conn_id in manager.connection_info
        assert manager.connection_info[conn_id].user_id == "test-user"
        assert len(manager.active_connections) == 1

        # Verify WebSocket accept was called
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_multiple_clients(self, manager):
        """Test multiple connections"""
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        # Connect two clients
        conn_id1 = await manager.connect(mock_ws1, user_id="user1")
        conn_id2 = await manager.connect(mock_ws2, user_id="user2")

        # Verify both connected
        assert len(manager.active_connections) == 2
        assert conn_id1 != conn_id2
        assert manager.connection_info[conn_id1].user_id == "user1"
        assert manager.connection_info[conn_id2].user_id == "user2"

    @pytest.mark.asyncio
    async def test_disconnect_existing_client(self, manager, mock_websocket):
        """Test removing WebSocket connection"""
        # Connect first
        conn_id = await manager.connect(mock_websocket, user_id="test-user")
        assert len(manager.active_connections) == 1

        # Disconnect
        await manager.disconnect(conn_id)

        # Verify disconnection
        assert conn_id not in manager.active_connections
        assert conn_id not in manager.connection_info
        assert len(manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_client(self, manager):
        """Test disconnecting client that doesn't exist"""
        # Should not raise an error
        await manager.disconnect("nonexistent-connection-id")

        # Verify no connections
        assert len(manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_multiple_connections_same_user(self, manager):
        """Test same user connecting from multiple devices"""
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        # Same user, two connections
        conn_id1 = await manager.connect(mock_ws1, user_id="same-user")
        conn_id2 = await manager.connect(mock_ws2, user_id="same-user")

        # Both connections should exist independently
        assert len(manager.active_connections) == 2
        assert conn_id1 != conn_id2
        assert manager.connection_info[conn_id1].user_id == "same-user"
        assert manager.connection_info[conn_id2].user_id == "same-user"

    @pytest.mark.asyncio
    async def test_connection_count(self, manager):
        """Test active connection count tracking"""
        assert len(manager.active_connections) == 0

        # Add connections
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        mock_ws3 = Mock()
        mock_ws3.accept = AsyncMock()
        mock_ws3.send_json = AsyncMock()

        conn_id1 = await manager.connect(mock_ws1)
        assert len(manager.active_connections) == 1

        conn_id2 = await manager.connect(mock_ws2)
        assert len(manager.active_connections) == 2

        conn_id3 = await manager.connect(mock_ws3)
        assert len(manager.active_connections) == 3

        # Remove one
        await manager.disconnect(conn_id2)
        assert len(manager.active_connections) == 2

        # Remove all
        await manager.disconnect(conn_id1)
        await manager.disconnect(conn_id3)
        assert len(manager.active_connections) == 0


class TestMessageBroadcasting:
    """Test message broadcasting methods"""

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, manager):
        """Test broadcasting message to all connected clients"""
        # Create 3 connections
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        mock_ws3 = Mock()
        mock_ws3.accept = AsyncMock()
        mock_ws3.send_json = AsyncMock()

        await manager.connect(mock_ws1)
        await manager.connect(mock_ws2)
        await manager.connect(mock_ws3)

        # Broadcast message
        message = PongMessage()
        await manager.broadcast(message)

        # Verify all received
        mock_ws1.send_json.assert_called()
        mock_ws2.send_json.assert_called()
        mock_ws3.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_broadcast_with_exclude(self, manager):
        """Test broadcasting with exclusion list"""
        # Create 3 connections
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        mock_ws3 = Mock()
        mock_ws3.accept = AsyncMock()
        mock_ws3.send_json = AsyncMock()

        await manager.connect(mock_ws1)
        conn_id2 = await manager.connect(mock_ws2)
        await manager.connect(mock_ws3)

        # Broadcast excluding conn_id2
        message = PongMessage()
        await manager.broadcast(message, exclude={conn_id2})

        # Verify only conn_id1 and conn_id3 received
        mock_ws1.send_json.assert_called()
        mock_ws2.send_json.assert_not_called()
        mock_ws3.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_send_to_user(self, manager, mock_websocket):
        """Test sending message to specific user (via connection_id)"""
        # Connect
        conn_id = await manager.connect(mock_websocket, user_id="test-user")

        # Send message
        message = PriceUpdate(
            stock_code="005930",
            price=70000,
            change=1000,
            change_percent=1.5,
            volume=1000000,
        )
        result = await manager.send_message(conn_id, message, immediate=True)

        # Verify sent
        assert result is True
        mock_websocket.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_subscribers(self, manager):
        """Test sending message to user group/subscribers"""
        # Create 3 connections
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        mock_ws3 = Mock()
        mock_ws3.accept = AsyncMock()
        mock_ws3.send_json = AsyncMock()

        conn_id1 = await manager.connect(mock_ws1)
        await manager.connect(mock_ws2)
        conn_id3 = await manager.connect(mock_ws3)

        # Subscribe conn_id1 and conn_id3 to Samsung Electronics
        await manager.subscribe(conn_id1, SubscriptionType.STOCK, "005930")
        await manager.subscribe(conn_id3, SubscriptionType.STOCK, "005930")

        # Send to subscribers
        message = PriceUpdate(
            stock_code="005930",
            price=70000,
            change=1000,
            change_percent=1.5,
            volume=1000000,
        )
        await manager.send_to_subscribers(SubscriptionType.STOCK, "005930", message)

        # Verify only subscribers received
        mock_ws1.send_json.assert_called()
        mock_ws2.send_json.assert_not_called()
        mock_ws3.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_broadcast_price_update(self, manager):
        """Test broadcasting price update format"""
        # Create connection
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        conn_id = await manager.connect(mock_ws)
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Broadcast price update
        message = PriceUpdate(
            stock_code="005930",
            price=70000,
            change=1000,
            change_percent=1.5,
            volume=1000000,
        )
        await manager.send_to_subscribers(SubscriptionType.STOCK, "005930", message)

        # Verify message format
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == MessageType.PRICE_UPDATE
        assert call_args["stock_code"] == "005930"
        assert call_args["price"] == 70000

    @pytest.mark.asyncio
    async def test_broadcast_empty_connections(self, manager):
        """Test broadcasting when no clients connected"""
        # No connections
        assert len(manager.active_connections) == 0

        # Broadcast should not raise error
        message = PongMessage()
        await manager.broadcast(message)

        # No errors raised


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_handle_connection_error(self, manager):
        """Test handling WebSocket connection errors"""
        # Create mock that raises on send
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock(side_effect=Exception("Connection error"))

        conn_id = await manager.connect(mock_ws)

        # Try to send message
        message = PongMessage()
        result = await manager.send_message(conn_id, message, immediate=True)

        # Should return False on error
        assert result is False

    @pytest.mark.asyncio
    async def test_handle_send_error(self, manager):
        """Test handling message send failures"""
        from fastapi import WebSocketDisconnect

        # Create mock that raises WebSocketDisconnect
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock(side_effect=WebSocketDisconnect())

        conn_id = await manager.connect(mock_ws)

        # Try to send message
        message = PongMessage()
        result = await manager.send_message(conn_id, message, immediate=True)

        # Should return False and auto-disconnect
        assert result is False
        assert conn_id not in manager.active_connections

    @pytest.mark.asyncio
    async def test_cleanup_stale_connections(self, manager):
        """Test removing disconnected clients"""
        # Connect
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        conn_id = await manager.connect(mock_ws, user_id="test-user")

        # Add subscription
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Disconnect
        await manager.disconnect(conn_id)

        # Verify cleanup
        assert conn_id not in manager.active_connections
        assert conn_id not in manager.connection_info
        assert conn_id not in manager.connection_subscriptions
        # Verify subscription cleaned up
        subscribers = manager.get_subscribers(SubscriptionType.STOCK, "005930")
        assert conn_id not in subscribers

    @pytest.mark.asyncio
    async def test_connection_timeout_heartbeat(self, manager):
        """Test connection timeout handling via heartbeat"""
        from fastapi import WebSocketDisconnect

        # Create mock that fails on heartbeat
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock(side_effect=WebSocketDisconnect())

        conn_id = await manager.connect(mock_ws)

        # Manually trigger heartbeat
        dead_connections = []
        try:
            ping_msg = PongMessage()
            await mock_ws.send_json(ping_msg.model_dump(mode="json"))
        except Exception:
            dead_connections.append(conn_id)

        # Clean up dead connection
        for dead_conn_id in dead_connections:
            await manager.disconnect(dead_conn_id)

        # Verify cleaned up
        assert conn_id not in manager.active_connections


class TestConcurrencySafety:
    """Test concurrency and thread safety"""

    @pytest.mark.asyncio
    async def test_concurrent_connects(self, manager):
        """Test multiple simultaneous connections"""

        async def connect_client(index):
            mock_ws = Mock()
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            return await manager.connect(mock_ws, user_id=f"user-{index}")

        # Connect 10 clients concurrently
        tasks = [connect_client(i) for i in range(10)]
        conn_ids = await asyncio.gather(*tasks)

        # Verify all connected
        assert len(manager.active_connections) == 10
        assert len(set(conn_ids)) == 10  # All unique IDs

    @pytest.mark.asyncio
    async def test_concurrent_disconnects(self, manager):
        """Test multiple simultaneous disconnections"""
        # Create 10 connections
        conn_ids = []
        for i in range(10):
            mock_ws = Mock()
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            conn_id = await manager.connect(mock_ws)
            conn_ids.append(conn_id)

        # Disconnect all concurrently
        disconnect_tasks = [manager.disconnect(conn_id) for conn_id in conn_ids]
        await asyncio.gather(*disconnect_tasks)

        # Verify all disconnected
        assert len(manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_concurrent_broadcasts(self, manager):
        """Test concurrent message broadcasts"""
        # Create 5 connections
        for i in range(5):
            mock_ws = Mock()
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            await manager.connect(mock_ws)

        # Broadcast 10 messages concurrently
        async def broadcast_message(index):
            message = PongMessage()
            await manager.broadcast(message)

        broadcast_tasks = [broadcast_message(i) for i in range(10)]
        await asyncio.gather(*broadcast_tasks)

        # Should complete without errors
        # Verify all connections still active
        assert len(manager.active_connections) == 5

    @pytest.mark.asyncio
    async def test_thread_safety_sequence_counter(self, manager):
        """Test ConnectionManager sequence counter is thread-safe"""

        async def get_next_sequence():
            return await manager._next_sequence()

        # Get 100 sequences concurrently
        tasks = [get_next_sequence() for _ in range(100)]
        sequences = await asyncio.gather(*tasks)

        # Verify all unique and sequential
        assert len(set(sequences)) == 100
        assert sorted(sequences) == list(range(1, 101))


class TestSubscriptionManagement:
    """Test subscription functionality"""

    @pytest.mark.asyncio
    async def test_subscribe_and_get_subscribers(self, manager):
        """Test subscription management"""
        # Create connection
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        conn_id = await manager.connect(mock_ws)

        # Subscribe to stock
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Get subscribers
        subscribers = manager.get_subscribers(SubscriptionType.STOCK, "005930")
        assert conn_id in subscribers

    @pytest.mark.asyncio
    async def test_unsubscribe(self, manager):
        """Test unsubscription"""
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        conn_id = await manager.connect(mock_ws)

        # Subscribe and unsubscribe
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")
        manager.unsubscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Verify unsubscribed
        subscribers = manager.get_subscribers(SubscriptionType.STOCK, "005930")
        assert conn_id not in subscribers

    @pytest.mark.asyncio
    async def test_multiple_subscriptions(self, manager):
        """Test multiple subscriptions per connection"""
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        conn_id = await manager.connect(mock_ws)

        # Subscribe to multiple targets
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "000660")
        await manager.subscribe(conn_id, SubscriptionType.MARKET, "KOSPI")

        # Verify all subscriptions
        assert conn_id in manager.get_subscribers(SubscriptionType.STOCK, "005930")
        assert conn_id in manager.get_subscribers(SubscriptionType.STOCK, "000660")
        assert conn_id in manager.get_subscribers(SubscriptionType.MARKET, "KOSPI")


class TestStatistics:
    """Test statistics functionality"""

    @pytest.mark.asyncio
    async def test_get_stats(self, manager):
        """Test statistics"""
        # Initial stats
        stats = manager.get_stats()
        assert stats["active_connections"] == 0
        assert stats["total_subscriptions"] == 0

        # Add connections and subscriptions
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        conn_id = await manager.connect(mock_ws)
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "000660")

        # Get updated stats
        stats = manager.get_stats()
        assert stats["active_connections"] == 1
        assert stats["total_subscriptions"] >= 2
        assert stats["messages_sent"] >= 0

    @pytest.mark.asyncio
    async def test_connection_info(self, manager):
        """Test connection info retrieval"""
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        conn_id = await manager.connect(mock_ws, user_id="test-user")

        # Get connection info
        info = manager.get_connection_info(conn_id)
        assert info is not None
        assert info.connection_id == conn_id
        assert info.user_id == "test-user"
        assert info.message_count == 0

        # Send message and verify count updates
        message = PongMessage()
        await manager.send_message(conn_id, message, immediate=True)

        info = manager.get_connection_info(conn_id)
        assert info.message_count == 1


class TestSessionRestoration:
    """Test Phase 3 session restoration features"""

    @pytest.mark.asyncio
    async def test_session_save_on_disconnect(self, manager):
        """Test session is saved on disconnect"""
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        # Connect
        conn_id = await manager.connect(mock_ws, user_id="test-user")

        # Add some subscriptions
        await manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")
        await manager.subscribe(conn_id, SubscriptionType.MARKET, "KOSPI")

        # Disconnect
        await manager.disconnect(conn_id)

        # Verify session was saved
        assert conn_id in manager._disconnected_sessions
        session = manager._disconnected_sessions[conn_id]
        assert session["user_id"] == "test-user"
        assert "subscriptions" in session

    @pytest.mark.asyncio
    async def test_session_restoration_on_reconnect(self, manager):
        """Test session restoration on reconnection"""
        # Create first connection
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        conn_id1 = await manager.connect(mock_ws1, user_id="test-user")

        # Add subscriptions
        await manager.subscribe(conn_id1, SubscriptionType.STOCK, "005930")
        await manager.subscribe(conn_id1, SubscriptionType.STOCK, "000660")

        # Disconnect (saves session)
        await manager.disconnect(conn_id1)

        # Reconnect with same session
        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        conn_id2, restored_subs, missed_msgs = await manager.reconnect(
            mock_ws2, conn_id1, user_id="test-user"
        )

        # Verify new connection ID
        assert conn_id2 != conn_id1
        assert conn_id2 in manager.active_connections

        # Verify subscriptions restored
        assert SubscriptionType.STOCK in restored_subs
        assert "005930" in restored_subs[SubscriptionType.STOCK]
        assert "000660" in restored_subs[SubscriptionType.STOCK]

        # Verify old session removed
        assert conn_id1 not in manager._disconnected_sessions

    @pytest.mark.asyncio
    async def test_reconnect_with_expired_session(self, manager):
        """Test reconnection fails with expired session"""
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        # Try to reconnect with non-existent session
        with pytest.raises(ValueError, match="Session .* not found"):
            await manager.reconnect(
                mock_ws, "non-existent-session", user_id="test-user"
            )

    @pytest.mark.asyncio
    async def test_reconnect_with_user_mismatch(self, manager):
        """Test reconnection fails with user ID mismatch"""
        # Create and disconnect connection
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        conn_id = await manager.connect(mock_ws1, user_id="user1")
        await manager.disconnect(conn_id)

        # Try to reconnect with different user
        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        with pytest.raises(ValueError, match="User ID mismatch"):
            await manager.reconnect(mock_ws2, conn_id, user_id="user2")
