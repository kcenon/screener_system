"""WebSocket endpoints for real-time updates"""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from fastapi import Depends, status  # Unused
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import logger
from app.core.websocket import connection_manager
from app.schemas.websocket import (
    MessageType,
    PongMessage,
    SubscribeRequest,
    SubscriptionResponse,
    UnsubscribeRequest,
)
# from app.schemas.websocket import ErrorMessage  # Unused

router = APIRouter(tags=["websocket"])


async def verify_token(token: Optional[str]) -> Optional[str]:
    """
    Verify JWT token from WebSocket connection.

    Args:
        token: JWT token string

    Returns:
        user_id if valid, None if invalid or anonymous
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        return user_id
    except JWTError as e:
        logger.warning(f"Invalid WebSocket token: {e}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None,
    session_id: Optional[str] = None,  # Phase 3: For reconnection
):
    """
    Main WebSocket endpoint for real-time stock updates.

    Connection URL: ws://localhost:8000/v1/ws?token=<jwt_token>
    Reconnection URL:
    ws://localhost:8000/v1/ws?token=<jwt_token>&session_id=<old_connection_id>

    The WebSocket connection supports:
    - Real-time price updates
    - Order book updates
    - Market status notifications
    - Custom alerts
    - Subscription management
    - Token refresh (Phase 3)
    - Session restoration on reconnection (Phase 3)
    """
    # Verify authentication (optional, allows anonymous connections)
    user_id = await verify_token(token)

    # Phase 3: Handle reconnection if session_id provided
    connection_id = None
    restored_subscriptions = None
    missed_messages = 0

    if session_id:
        try:
            # Attempt to restore session
            connection_id, restored_subscriptions, missed_messages = (
                await connection_manager.reconnect(websocket, session_id, user_id)
            )

            # Send reconnection confirmation
            from app.schemas.websocket import ReconnectedMessage

            reconnect_msg = ReconnectedMessage(
                session_id=session_id,
                restored_subscriptions=restored_subscriptions or {},
                missed_messages_count=missed_messages,
            )
            await connection_manager.send_message(connection_id, reconnect_msg)

            logger.info(
                f"Client reconnected: {session_id} -> {connection_id} "
                f"(restored {sum(len(v) for v in restored_subscriptions.values())} "
                f"subscriptions)"
            )

        except ValueError as e:
            # Session restoration failed, connect normally
            logger.warning(f"Session restoration failed for {session_id}: {e}")
            connection_id = await connection_manager.connect(websocket, user_id)

            # Send error message about failed restoration
            await connection_manager.send_error(
                connection_id,
                code="SESSION_RESTORATION_FAILED",
                message=str(e),
            )
    else:
        # Normal connection
        connection_id = await connection_manager.connect(websocket, user_id)

    try:
        # Send welcome message
        logger.info(f"Client {connection_id} connected")

        # Message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()

                # Check message size (DoS protection)
                if len(data) > settings.WEBSOCKET_MAX_MESSAGE_SIZE:
                    logger.warning(
                        f"Message too large from {connection_id}: {len(data)} bytes"
                    )
                    await connection_manager.send_error(
                        connection_id,
                        code="MESSAGE_TOO_LARGE",
                        message=(
                            f"Message exceeds maximum size of "
                            f"{settings.WEBSOCKET_MAX_MESSAGE_SIZE} bytes"
                        ),
                    )
                    continue

                # Parse JSON
                try:
                    message = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from {connection_id}: {e}")
                    await connection_manager.send_error(
                        connection_id,
                        code="INVALID_JSON",
                        message="Invalid JSON format",
                        details={"error": str(e)},
                    )
                    continue

                # Get message type
                msg_type = message.get("type")

                if not msg_type:
                    await connection_manager.send_error(
                        connection_id,
                        code="MISSING_TYPE",
                        message="Message type is required",
                    )
                    continue

                # Handle different message types
                if msg_type == MessageType.SUBSCRIBE:
                    await handle_subscribe(connection_id, message)

                elif msg_type == MessageType.UNSUBSCRIBE:
                    await handle_unsubscribe(connection_id, message)

                elif msg_type == MessageType.PING:
                    # Respond with pong
                    pong = PongMessage()
                    await connection_manager.send_message(connection_id, pong)

                elif msg_type == MessageType.REFRESH_TOKEN:
                    # Phase 3: Token refresh
                    await handle_refresh_token(connection_id, message)

                elif msg_type == MessageType.RECONNECT:
                    # Phase 3: Reconnection - handled at connection time
                    await connection_manager.send_error(
                        connection_id,
                        code="RECONNECT_NOT_SUPPORTED_HERE",
                        message="Reconnection must be done at initial connection",
                    )

                else:
                    await connection_manager.send_error(
                        connection_id,
                        code="UNKNOWN_MESSAGE_TYPE",
                        message=f"Unknown message type: {msg_type}",
                    )

            except WebSocketDisconnect:
                logger.info(f"Client {connection_id} disconnected normally")
                break

            except Exception as e:
                logger.error(f"Error processing message from {connection_id}: {e}")
                await connection_manager.send_error(
                    connection_id,
                    code="PROCESSING_ERROR",
                    message="Error processing message",
                    details={"error": str(e)} if settings.DEBUG else None,
                )

    except WebSocketDisconnect:
        logger.info(f"Client {connection_id} disconnected")

    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")

    finally:
        # Clean up connection
        await connection_manager.disconnect(connection_id)


async def handle_subscribe(connection_id: str, message: dict):
    """
    Handle subscription request.

    Args:
        connection_id: Connection ID
        message: Subscription message
    """
    try:
        # Validate and parse request
        request = SubscribeRequest(**message)

        # Check targets per request limit (DoS protection)
        if len(request.targets) > settings.WEBSOCKET_MAX_TARGETS_PER_SUBSCRIPTION:
            await connection_manager.send_error(
                connection_id,
                code="TOO_MANY_TARGETS",
                message=(
                    f"Cannot subscribe to more than "
                    f"{settings.WEBSOCKET_MAX_TARGETS_PER_SUBSCRIPTION} targets at once"
                ),
            )
            return

        # Check total subscription limit (DoS protection)
        conn_info = connection_manager.get_connection_info(connection_id)
        if conn_info:
            current_subscriptions = sum(
                len(targets) for targets in conn_info.subscriptions.values()
            )
            if (
                current_subscriptions + len(request.targets)
                > settings.WEBSOCKET_MAX_SUBSCRIPTIONS_PER_CONNECTION
            ):
                await connection_manager.send_error(
                    connection_id,
                    code="SUBSCRIPTION_LIMIT_EXCEEDED",
                    message=(
                        f"Maximum {settings.WEBSOCKET_MAX_SUBSCRIPTIONS_PER_CONNECTION}"
                        " subscriptions per connection"
                    ),
                )
                return

        # Subscribe to each target
        for target in request.targets:
            await connection_manager.subscribe(
                connection_id, request.subscription_type, target
            )

        # Send confirmation
        response = SubscriptionResponse(
            type=MessageType.SUBSCRIBED,
            subscription_type=request.subscription_type,
            targets=request.targets,
        )
        await connection_manager.send_message(connection_id, response)

        logger.info(
            f"Subscribed {connection_id} to "
            f"{request.subscription_type.value}: {request.targets}"
        )

    except Exception as e:
        logger.error(f"Subscribe error for {connection_id}: {e}")
        await connection_manager.send_error(
            connection_id,
            code="SUBSCRIBE_ERROR",
            message="Failed to process subscription",
            details={"error": str(e)} if settings.DEBUG else None,
        )


async def handle_unsubscribe(connection_id: str, message: dict):
    """
    Handle unsubscribe request.

    Args:
        connection_id: Connection ID
        message: Unsubscribe message
    """
    try:
        # Validate and parse request
        request = UnsubscribeRequest(**message)

        # Unsubscribe from each target
        for target in request.targets:
            connection_manager.unsubscribe(
                connection_id, request.subscription_type, target
            )

        # Send confirmation
        response = SubscriptionResponse(
            type=MessageType.UNSUBSCRIBED,
            subscription_type=request.subscription_type,
            targets=request.targets,
        )
        await connection_manager.send_message(connection_id, response)

        logger.info(
            f"Unsubscribed {connection_id} from "
            f"{request.subscription_type.value}: {request.targets}"
        )

    except Exception as e:
        logger.error(f"Unsubscribe error for {connection_id}: {e}")
        await connection_manager.send_error(
            connection_id,
            code="UNSUBSCRIBE_ERROR",
            message="Failed to process unsubscription",
            details={"error": str(e)} if settings.DEBUG else None,
        )


async def handle_refresh_token(connection_id: str, message: dict):
    """
    Handle token refresh request (Phase 3).

    Args:
        connection_id: Connection ID
        message: Token refresh message
    """
    try:
        from app.schemas.websocket import RefreshTokenRequest, TokenRefreshedMessage

        # Validate request
        request = RefreshTokenRequest(**message)

        # Verify refresh token and generate new access token
        try:
            payload = jwt.decode(
                request.refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            # Check if this is a refresh token
            token_type = payload.get("type")
            if token_type != "refresh":
                await connection_manager.send_error(
                    connection_id,
                    code="INVALID_TOKEN_TYPE",
                    message="Not a refresh token",
                )
                return

            # Extract user info
            user_id = payload.get("sub")
            if not user_id:
                await connection_manager.send_error(
                    connection_id,
                    code="INVALID_TOKEN",
                    message="User ID not found in token",
                )
                return

            # Generate new access token
            from datetime import timedelta
            from jose import jwt as jose_jwt

            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            expires_in = int(expires_delta.total_seconds())

            new_payload = {
                "sub": user_id,
                "type": "access",
                "exp": datetime.utcnow() + expires_delta,
            }

            new_access_token = jose_jwt.encode(
                new_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
            )

            # Send new access token
            response = TokenRefreshedMessage(
                access_token=new_access_token,
                expires_in=expires_in,
            )
            await connection_manager.send_message(connection_id, response)

            logger.info(f"Token refreshed for {connection_id} (user: {user_id})")

        except JWTError as e:
            logger.warning(f"Invalid refresh token from {connection_id}: {e}")
            await connection_manager.send_error(
                connection_id,
                code="INVALID_REFRESH_TOKEN",
                message="Invalid or expired refresh token",
            )

    except Exception as e:
        logger.error(f"Token refresh error for {connection_id}: {e}")
        await connection_manager.send_error(
            connection_id,
            code="TOKEN_REFRESH_ERROR",
            message="Failed to refresh token",
            details={"error": str(e)} if settings.DEBUG else None,
        )


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.

    Returns connection and subscription statistics for monitoring.
    """
    stats = connection_manager.get_stats()
    return {
        "status": "ok",
        "stats": stats,
    }


@router.get("/ws/connections")
async def get_active_connections():
    """
    Get information about active WebSocket connections.

    Returns list of active connections with metadata.
    """
    connections = []

    for conn_id, info in connection_manager.connection_info.items():
        connections.append(
            {
                "connection_id": conn_id,
                "user_id": info.user_id,
                "connected_at": info.connected_at.isoformat(),
                "last_activity": info.last_activity.isoformat(),
                "message_count": info.message_count,
                "subscriptions": {
                    k.value: v for k, v in info.subscriptions.items()
                },
            }
        )

    return {
        "status": "ok",
        "total": len(connections),
        "connections": connections,
    }
