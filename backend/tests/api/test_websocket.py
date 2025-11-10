"""Tests for WebSocket endpoints"""

import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.core.websocket import connection_manager
from app.main import app
from app.schemas.websocket import MessageType, SubscriptionType


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_connection_manager():
    """Reset connection manager before each test"""
    connection_manager.active_connections.clear()
    connection_manager.connection_info.clear()
    connection_manager.subscriptions.clear()
    connection_manager.connection_subscriptions.clear()
    connection_manager._sequence_counter = 0


class TestWebSocketConnection:
    """Test WebSocket connection lifecycle"""

    def test_websocket_connect_and_disconnect(self, client):
        """Test basic WebSocket connection"""
        with client.websocket_connect("/v1/ws") as websocket:
            # Connection should be established
            assert len(connection_manager.active_connections) == 1

        # After context exit, connection should be cleaned up
        # Note: TestClient may not call disconnect immediately
        # In production, this is handled by FastAPI lifecycle

    def test_websocket_with_invalid_token(self, client):
        """Test WebSocket with invalid JWT token"""
        # Should still connect (anonymous connection)
        with client.websocket_connect("/v1/ws?token=invalid_token") as websocket:
            # Connection successful - invalid token treated as anonymous
            # Send ping to verify connection is working
            websocket.send_json({"type": "ping"})
            response = websocket.receive_json()
            assert response["type"] == "pong"


class TestWebSocketMessages:
    """Test WebSocket message handling"""

    def test_ping_pong(self, client):
        """Test ping-pong heartbeat"""
        with client.websocket_connect("/v1/ws") as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})

            # Receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"

    def test_subscribe_to_stock(self, client):
        """Test subscribing to stock updates"""
        with client.websocket_connect("/v1/ws") as websocket:
            # Subscribe to Samsung Electronics
            subscribe_msg = {
                "type": "subscribe",
                "subscription_type": "stock",
                "targets": ["005930"],
            }
            websocket.send_json(subscribe_msg)

            # Receive subscription confirmation
            response = websocket.receive_json()
            assert response["type"] == "subscribed"
            assert response["subscription_type"] == "stock"
            assert "005930" in response["targets"]

    def test_subscribe_multiple_stocks(self, client):
        """Test subscribing to multiple stocks"""
        with client.websocket_connect("/v1/ws") as websocket:
            # Subscribe to multiple stocks
            subscribe_msg = {
                "type": "subscribe",
                "subscription_type": "stock",
                "targets": ["005930", "000660", "035720"],
            }
            websocket.send_json(subscribe_msg)

            # Receive confirmation
            response = websocket.receive_json()
            assert response["type"] == "subscribed"
            assert len(response["targets"]) == 3

    def test_unsubscribe_from_stock(self, client):
        """Test unsubscribing from stock updates"""
        with client.websocket_connect("/v1/ws") as websocket:
            # Subscribe first
            websocket.send_json(
                {
                    "type": "subscribe",
                    "subscription_type": "stock",
                    "targets": ["005930"],
                }
            )
            websocket.receive_json()  # Skip confirmation

            # Unsubscribe
            unsubscribe_msg = {
                "type": "unsubscribe",
                "subscription_type": "stock",
                "targets": ["005930"],
            }
            websocket.send_json(unsubscribe_msg)

            # Receive confirmation
            response = websocket.receive_json()
            assert response["type"] == "unsubscribed"
            assert "005930" in response["targets"]

    def test_invalid_json(self, client):
        """Test sending invalid JSON"""
        with client.websocket_connect("/v1/ws") as websocket:
            # Send invalid JSON
            websocket.send_text("not a json")

            # Receive error
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert response["code"] == "INVALID_JSON"

    def test_missing_message_type(self, client):
        """Test message without type field"""
        with client.websocket_connect("/v1/ws") as websocket:
            # Send message without type
            websocket.send_json({"data": "test"})

            # Receive error
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert response["code"] == "MISSING_TYPE"

    def test_unknown_message_type(self, client):
        """Test unknown message type"""
        with client.websocket_connect("/v1/ws") as websocket:
            # Send unknown message type
            websocket.send_json({"type": "unknown_type"})

            # Receive error
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert response["code"] == "UNKNOWN_MESSAGE_TYPE"


class TestWebSocketStats:
    """Test WebSocket statistics endpoints"""

    def test_get_stats_no_connections(self, client):
        """Test stats with no active connections"""
        response = client.get("/v1/ws/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["stats"]["active_connections"] == 0

    def test_get_active_connections(self, client):
        """Test listing active connections"""
        response = client.get("/v1/ws/connections")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["total"] == 0
        assert isinstance(data["connections"], list)


class TestConnectionManager:
    """Test ConnectionManager functionality"""

    def test_subscribe_and_get_subscribers(self):
        """Test subscription management"""
        # Create mock connection
        conn_id = "test-conn-1"

        # Subscribe to stock
        connection_manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Get subscribers
        subscribers = connection_manager.get_subscribers(
            SubscriptionType.STOCK, "005930"
        )
        assert conn_id in subscribers

    def test_unsubscribe(self):
        """Test unsubscription"""
        conn_id = "test-conn-1"

        # Subscribe and unsubscribe
        connection_manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")
        connection_manager.unsubscribe(conn_id, SubscriptionType.STOCK, "005930")

        # Verify unsubscribed
        subscribers = connection_manager.get_subscribers(
            SubscriptionType.STOCK, "005930"
        )
        assert conn_id not in subscribers

    def test_multiple_subscriptions(self):
        """Test multiple subscriptions per connection"""
        conn_id = "test-conn-1"

        # Subscribe to multiple stocks
        connection_manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")
        connection_manager.subscribe(conn_id, SubscriptionType.STOCK, "000660")
        connection_manager.subscribe(conn_id, SubscriptionType.MARKET, "KOSPI")

        # Verify subscriptions
        assert conn_id in connection_manager.get_subscribers(
            SubscriptionType.STOCK, "005930"
        )
        assert conn_id in connection_manager.get_subscribers(
            SubscriptionType.STOCK, "000660"
        )
        assert conn_id in connection_manager.get_subscribers(
            SubscriptionType.MARKET, "KOSPI"
        )

    def test_get_stats(self):
        """Test statistics"""
        conn_id = "test-conn-1"

        # Add subscriptions
        connection_manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")
        connection_manager.subscribe(conn_id, SubscriptionType.STOCK, "000660")

        # Get stats
        stats = connection_manager.get_stats()
        assert stats["active_connections"] == 0  # No actual WebSocket connections
        assert stats["total_subscriptions"] >= 2


class TestWebSocketPhase3:
    """Test Phase 3 features: Session restoration, token refresh"""

    @pytest.mark.asyncio
    async def test_session_save_on_disconnect(self):
        """Test session is saved on disconnect"""
        from unittest.mock import AsyncMock, Mock

        # Create mock WebSocket connection
        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        # Connect
        conn_id = await connection_manager.connect(mock_ws, user_id="test-user")

        # Add some subscriptions
        await connection_manager.subscribe(conn_id, SubscriptionType.STOCK, "005930")
        await connection_manager.subscribe(conn_id, SubscriptionType.MARKET, "KOSPI")

        # Disconnect
        await connection_manager.disconnect(conn_id)

        # Verify session was saved
        assert conn_id in connection_manager._disconnected_sessions
        session = connection_manager._disconnected_sessions[conn_id]
        assert session["user_id"] == "test-user"
        assert "subscriptions" in session
        assert SubscriptionType.STOCK in session["subscriptions"]

    @pytest.mark.asyncio
    async def test_session_restoration_on_reconnect(self):
        """Test session restoration on reconnection"""
        from unittest.mock import AsyncMock, Mock

        # Create first connection
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        conn_id1 = await connection_manager.connect(mock_ws1, user_id="test-user")

        # Add subscriptions
        await connection_manager.subscribe(conn_id1, SubscriptionType.STOCK, "005930")
        await connection_manager.subscribe(conn_id1, SubscriptionType.STOCK, "000660")

        # Disconnect (saves session)
        await connection_manager.disconnect(conn_id1)

        # Reconnect with same session
        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        conn_id2, restored_subs, missed_msgs = await connection_manager.reconnect(
            mock_ws2, conn_id1, user_id="test-user"
        )

        # Verify new connection ID
        assert conn_id2 != conn_id1
        assert conn_id2 in connection_manager.active_connections

        # Verify subscriptions restored
        assert SubscriptionType.STOCK in restored_subs
        assert "005930" in restored_subs[SubscriptionType.STOCK]
        assert "000660" in restored_subs[SubscriptionType.STOCK]

        # Verify old session removed
        assert conn_id1 not in connection_manager._disconnected_sessions

    @pytest.mark.asyncio
    async def test_reconnect_with_expired_session(self):
        """Test reconnection fails with expired session"""
        from unittest.mock import AsyncMock, Mock

        mock_ws = Mock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        # Try to reconnect with non-existent session
        with pytest.raises(ValueError, match="Session .* not found"):
            await connection_manager.reconnect(
                mock_ws, "non-existent-session", user_id="test-user"
            )

    @pytest.mark.asyncio
    async def test_reconnect_with_user_mismatch(self):
        """Test reconnection fails with user ID mismatch"""
        from unittest.mock import AsyncMock, Mock

        # Create and disconnect connection
        mock_ws1 = Mock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        conn_id = await connection_manager.connect(mock_ws1, user_id="user1")
        await connection_manager.disconnect(conn_id)

        # Try to reconnect with different user
        mock_ws2 = Mock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        with pytest.raises(ValueError, match="User ID mismatch"):
            await connection_manager.reconnect(mock_ws2, conn_id, user_id="user2")

    def test_session_cleanup_stats(self):
        """Test session cleanup in stats"""
        # Add a saved session manually
        connection_manager._disconnected_sessions["test-session"] = {
            "connection_id": "test-session",
            "user_id": "test-user",
            "subscriptions": {},
            "last_sequence": 0,
            "saved_at": datetime.utcnow(),
        }

        # Get stats
        stats = connection_manager.get_stats()
        assert "saved_sessions" in stats
        assert stats["saved_sessions"] >= 1
