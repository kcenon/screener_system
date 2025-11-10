"""WebSocket endpoints for real-time updates"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import logger
from app.core.websocket import connection_manager
from app.schemas.websocket import (ErrorMessage, MessageType, PingMessage,
                                   PongMessage, SubscribeRequest,
                                   SubscriptionResponse, SubscriptionType,
                                   UnsubscribeRequest)

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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        return user_id
    except JWTError as e:
        logger.warning(f"Invalid WebSocket token: {e}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None,
):
    """
    Main WebSocket endpoint for real-time stock updates.

    Connection URL: ws://localhost:8000/v1/ws?token=<jwt_token>

    The WebSocket connection supports:
    - Real-time price updates
    - Order book updates
    - Market status notifications
    - Custom alerts
    - Subscription management

    Message Format (Client -> Server):
    ```json
    {
        "type": "subscribe",
        "subscription_type": "stock",
        "targets": ["005930", "000660"]
    }
    ```

    Message Format (Server -> Client):
    ```json
    {
        "type": "price_update",
        "stock_code": "005930",
        "price": 72500.0,
        "change": 500.0,
        "change_percent": 0.69,
        "volume": 15234567,
        "timestamp": "2025-11-10T12:00:00Z",
        "sequence": 1234
    }
    ```
    """
    # Verify authentication (optional, allows anonymous connections)
    user_id = await verify_token(token)

    # Connect to WebSocket
    connection_id = await connection_manager.connect(websocket, user_id)

    try:
        # Send welcome message
        logger.info(f"Client {connection_id} connected")

        # Message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()

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
                    details={"error": str(e)},
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

        # Subscribe to each target
        for target in request.targets:
            connection_manager.subscribe(
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
            details={"error": str(e)},
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
            details={"error": str(e)},
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
