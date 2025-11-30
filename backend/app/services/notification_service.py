"""Notification service for delivering notifications across multiple channels.

This module provides the NotificationService class that handles notification
delivery via email, push, and in-app channels while respecting user preferences.

The service integrates with:
    - Email service (SMTP)
    - Push notification service (Firebase/APNs)
    - WebSocket for real-time in-app notifications

Example:
    Send a notification to a user::

        from app.services import NotificationService
        from app.db import get_session

        async with get_session() as session:
            service = NotificationService(session)
            await service.send_notification(
                user_id=123,
                notification_id=456,
            )
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import Notification, NotificationPreference
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notification delivery across multiple channels.

    This class handles the delivery of notifications to users via email, push,
    and in-app channels while respecting user preferences and quiet hours.

    Attributes:
        MAX_RETRIES: Maximum number of delivery retries (3).
        NOTIFICATION_TTL: Time-to-live for notifications in days (90).
    """

    MAX_RETRIES = 3
    NOTIFICATION_TTL = 90  # days

    def __init__(
        self,
        session: AsyncSession,
        email_service: Optional[EmailService] = None,
    ):
        """Initialize the notification service.

        Args:
            session: Database session for queries.
            email_service: Service for sending emails.
                If None, will be created automatically.
        """
        self.session = session
        self.email_service = email_service or EmailService()

    async def send_notification(
        self,
        user_id: int,
        notification_id: int,
    ) -> bool:
        """Send notification via all enabled channels.

        This is the main entry point for sending notifications. It checks user
        preferences and sends the notification via appropriate channels.

        Args:
            user_id: User ID to send notification to.
            notification_id: Notification ID to send.

        Returns:
            True if notification was sent successfully via at least one channel.
        """
        # Get notification with related data
        result = await self.session.execute(
            select(Notification)
            .options(joinedload(Notification.user))
            .where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False

        # Get user preferences
        preferences = await self._get_user_preferences(user_id)

        if not preferences:
            logger.warning(
                f"No notification preferences found for user {user_id}. "
                "Using defaults."
            )
            # Create default preferences if none exist
            preferences = NotificationPreference.create_default(user_id)
            self.session.add(preferences)
            await self.session.flush()

        # Check quiet hours
        if preferences.is_in_quiet_hours():
            logger.info(
                f"User {user_id} is in quiet hours. "
                "Notification will be queued for later."
            )
            # TODO: Implement notification queuing for quiet hours
            return False

        sent_via_any_channel = False

        # Send via in-app (always enabled for new notifications)
        if preferences.should_send_in_app():
            await self._send_in_app_notification(notification)
            sent_via_any_channel = True

        # Send via email
        if preferences.should_send_email(notification.notification_type):
            success = await self._send_email_notification(notification)
            sent_via_any_channel = sent_via_any_channel or success

        # Send via push (if enabled)
        if preferences.should_send_push():
            success = await self._send_push_notification(notification)
            sent_via_any_channel = sent_via_any_channel or success

        if sent_via_any_channel:
            logger.info(
                f"Notification {notification_id} sent successfully to user {user_id}"
            )
        else:
            logger.warning(
                f"Notification {notification_id} was not sent via any channel "
                f"for user {user_id}"
            )

        return sent_via_any_channel

    async def _get_user_preferences(
        self,
        user_id: int,
    ) -> Optional[NotificationPreference]:
        """Get notification preferences for a user.

        Args:
            user_id: User ID.

        Returns:
            User's notification preferences or None if not found.
        """
        result = await self.session.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def _send_in_app_notification(
        self,
        notification: Notification,
    ) -> bool:
        """Send in-app notification via WebSocket.

        Args:
            notification: Notification to send.

        Returns:
            True if notification was sent successfully.
        """
        try:
            # TODO: Integrate with WebSocket connection manager
            # For now, just log that notification is available in-app
            logger.info(
                f"In-app notification {notification.id} available for "
                f"user {notification.user_id}"
            )

            # The notification is already in the database, so it will be
            # visible when the user refreshes or polls for notifications

            return True
        except Exception as e:
            logger.error(
                f"Error sending in-app notification {notification.id}: {str(e)}",
                exc_info=True,
            )
            return False

    async def _send_email_notification(
        self,
        notification: Notification,
    ) -> bool:
        """Send email notification.

        Args:
            notification: Notification to send.

        Returns:
            True if email was sent successfully.
        """
        try:
            # Get user email
            user = notification.user
            if not user or not user.email:
                logger.warning(
                    f"No email address for user {notification.user_id}. "
                    "Skipping email notification."
                )
                return False

            # Send email
            success = await self.email_service.send_notification_email(
                to_email=user.email,
                subject=notification.title,
                body=notification.message,
                notification_type=notification.notification_type,
                priority=notification.priority,
            )

            if success:
                logger.info(
                    f"Email notification {notification.id} sent to {user.email}"
                )
            else:
                logger.error(
                    f"Failed to send email notification {notification.id} "
                    f"to {user.email}"
                )

            return success
        except Exception as e:
            logger.error(
                f"Error sending email notification {notification.id}: {str(e)}",
                exc_info=True,
            )
            return False

    async def _send_push_notification(
        self,
        notification: Notification,
    ) -> bool:
        """Send push notification (placeholder).

        This is a placeholder for future push notification integration
        (Firebase Cloud Messaging, Apple Push Notification Service, etc.).

        Args:
            notification: Notification to send.

        Returns:
            True if push notification was sent successfully.
        """
        # TODO: Implement push notification service
        logger.debug(
            f"Push notification for notification {notification.id} "
            "(not yet implemented)"
        )
        return False

    async def mark_as_read(
        self,
        notification_id: int,
        user_id: int,
    ) -> bool:
        """Mark a notification as read.

        Args:
            notification_id: Notification ID to mark as read.
            user_id: User ID (for security check).

        Returns:
            True if notification was marked as read.
        """
        result = await self.session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            logger.warning(
                f"Notification {notification_id} not found for user {user_id}"
            )
            return False

        notification.mark_as_read()
        await self.session.commit()

        logger.info(f"Notification {notification_id} marked as read")
        return True

    async def mark_all_as_read(
        self,
        user_id: int,
    ) -> int:
        """Mark all unread notifications as read for a user.

        Args:
            user_id: User ID.

        Returns:
            Number of notifications marked as read.
        """
        result = await self.session.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
        )
        notifications = result.scalars().all()

        count = 0
        for notification in notifications:
            notification.mark_as_read()
            count += 1

        await self.session.commit()

        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count

    async def delete_notification(
        self,
        notification_id: int,
        user_id: int,
    ) -> bool:
        """Delete a notification.

        Args:
            notification_id: Notification ID to delete.
            user_id: User ID (for security check).

        Returns:
            True if notification was deleted.
        """
        result = await self.session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            logger.warning(
                f"Notification {notification_id} not found for user {user_id}"
            )
            return False

        await self.session.delete(notification)
        await self.session.commit()

        logger.info(f"Notification {notification_id} deleted")
        return True

    async def get_unread_count(
        self,
        user_id: int,
    ) -> int:
        """Get count of unread notifications for a user.

        Args:
            user_id: User ID.

        Returns:
            Number of unread notifications.
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
        )
        count = result.scalar_one()

        return count

    async def cleanup_old_notifications(
        self,
        days: int = 90,
    ) -> int:
        """Clean up old read notifications.

        This should be called periodically (e.g., daily) to remove old
        notifications and free up database space.

        Args:
            days: Delete notifications older than this many days (default: 90).

        Returns:
            Number of notifications deleted.
        """
        from datetime import timedelta

        from sqlalchemy import delete

        from app.db.base import utc_now

        cutoff_date = utc_now() - timedelta(days=days)

        result = await self.session.execute(
            delete(Notification).where(
                Notification.created_at < cutoff_date,
                Notification.is_read == True,  # noqa: E712
            )
        )

        deleted_count = result.rowcount
        await self.session.commit()

        logger.info(
            f"Cleaned up {deleted_count} old notifications "
            f"(older than {days} days)"
        )

        return deleted_count
