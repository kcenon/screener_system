"""Notification management endpoints for viewing and managing notifications.

This module provides REST API endpoints for managing user notifications including
listing, marking as read, and managing notification preferences.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.models import Notification, NotificationPreference, User
from app.db.session import get_db
from app.schemas.notification import (NotificationDeleteResponse,
                                      NotificationListResponse,
                                      NotificationMarkAllReadResponse,
                                      NotificationMarkReadResponse,
                                      NotificationPreferenceResponse,
                                      NotificationPreferenceUpdate,
                                      NotificationResponse,
                                      NotificationUnreadCountResponse)
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ============================================================================
# Notification Management Endpoints
# ============================================================================


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user notifications",
    description="""
    Get paginated list of notifications for the authenticated user.

    **Filters:**
    - `notification_type`: Filter by type (ALERT, MARKET_EVENT, SYSTEM, PORTFOLIO)
    - `is_read`: Filter by read status
    - `priority`: Filter by priority (LOW, NORMAL, HIGH, URGENT)

    **Sorting:**
    - Default: Most recent first (created_at DESC)

    **Pagination:**
    - Default page size: 20
    - Maximum page size: 100
    """,
)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    notification_type: Optional[str] = Query(
        None,
        description="Filter by notification type",
    ),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
) -> NotificationListResponse:
    """Get paginated list of user notifications."""
    # Build query
    query = select(Notification).where(Notification.user_id == current_user.id)

    # Apply filters
    if notification_type:
        query = query.where(Notification.notification_type == notification_type)
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)
    if priority:
        query = query.where(Notification.priority == priority)

    # Get total count
    count_query = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id
    )
    if notification_type:
        count_query = count_query.where(
            Notification.notification_type == notification_type
        )
    if is_read is not None:
        count_query = count_query.where(Notification.is_read == is_read)
    if priority:
        count_query = count_query.where(Notification.priority == priority)

    result = await db.execute(count_query)
    total = result.scalar_one()

    # Get unread count
    unread_query = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False,  # noqa: E712
    )
    result = await db.execute(unread_query)
    unread_count = result.scalar_one()

    # Get paginated results
    query = query.order_by(Notification.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    notifications = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return NotificationListResponse(
        items=[
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/unread",
    response_model=NotificationUnreadCountResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unread notification count",
    description="""
    Get count of unread notifications for the authenticated user.

    This is useful for displaying notification badges in the UI.
    """,
)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationUnreadCountResponse:
    """Get count of unread notifications."""
    service = NotificationService(db)
    unread_count = await service.get_unread_count(current_user.id)

    return NotificationUnreadCountResponse(unread_count=unread_count)


@router.post(
    "/{notification_id}/read",
    response_model=NotificationMarkReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
    description="Mark a specific notification as read.",
)
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationMarkReadResponse:
    """Mark notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found",
        )

    if notification.is_read:
        # Already read, return current state
        return NotificationMarkReadResponse(
            id=notification.id,
            is_read=True,
            read_at=notification.read_at,
            message="Notification already marked as read",
        )

    # Mark as read
    notification.mark_as_read()
    await db.commit()
    await db.refresh(notification)

    logger.info(
        f"Notification {notification.id} marked as read for user {current_user.id}"
    )

    return NotificationMarkReadResponse(
        id=notification.id,
        is_read=True,
        read_at=notification.read_at,
        message="Notification marked as read successfully",
    )


@router.post(
    "/read-all",
    response_model=NotificationMarkAllReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read",
    description="""
    Mark all unread notifications as read for the authenticated user.

    This is useful for "mark all as read" functionality in the UI.
    """,
)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationMarkAllReadResponse:
    """Mark all notifications as read."""
    service = NotificationService(db)
    marked_count = await service.mark_all_as_read(current_user.id)

    logger.info(
        f"Marked {marked_count} notifications as read for user {current_user.id}"
    )

    return NotificationMarkAllReadResponse(
        marked_count=marked_count,
        message=f"Marked {marked_count} notifications as read",
    )


@router.delete(
    "/{notification_id}",
    response_model=NotificationDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete notification",
    description="""
    Delete a notification. This action cannot be undone.

    **Note:** Deleting a notification does not delete the associated alert.
    """,
)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationDeleteResponse:
    """Delete a notification."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found",
        )

    await db.delete(notification)
    await db.commit()

    logger.info(f"Notification {notification.id} deleted for user {current_user.id}")

    return NotificationDeleteResponse(
        id=notification_id,
        message="Notification deleted successfully",
    )


# ============================================================================
# Notification Preferences Endpoints
# ============================================================================


@router.get(
    "/preferences",
    response_model=NotificationPreferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get notification preferences",
    description="""
    Get notification preferences for the authenticated user.

    If preferences don't exist, default preferences will be created automatically.
    """,
)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferenceResponse:
    """Get user notification preferences."""
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    preferences = result.scalar_one_or_none()

    # Create default preferences if none exist
    if not preferences:
        preferences = NotificationPreference.create_default(current_user.id)
        db.add(preferences)
        await db.commit()
        await db.refresh(preferences)

        logger.info(
            f"Created default notification preferences for user {current_user.id}"
        )

    return NotificationPreferenceResponse.model_validate(preferences)


@router.put(
    "/preferences",
    response_model=NotificationPreferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update notification preferences",
    description="""
    Update notification preferences for the authenticated user.

    **Preferences:**
    - **Channels**: Enable/disable email, push, in-app notifications
    - **Type-specific**: Control emails for each notification type
    - **Digests**: Enable daily or weekly digest emails
    - **Quiet hours**: Set time range to pause notifications

    **Examples:**
    ```json
    {
      "email_enabled": true,
      "push_enabled": false,
      "alert_email": true,
      "quiet_hours_start": "22:00",
      "quiet_hours_end": "07:00",
      "quiet_hours_timezone": "Asia/Seoul"
    }
    ```
    """,
)
async def update_preferences(
    preference_data: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferenceResponse:
    """Update user notification preferences."""
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    preferences = result.scalar_one_or_none()

    # Create default preferences if none exist
    if not preferences:
        preferences = NotificationPreference.create_default(current_user.id)
        db.add(preferences)
        await db.flush()

    # Update fields
    update_data = preference_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)

    await db.commit()
    await db.refresh(preferences)

    logger.info(f"Updated notification preferences for user {current_user.id}")

    return NotificationPreferenceResponse.model_validate(preferences)
