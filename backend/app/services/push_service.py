"""Web Push notification service using pywebpush with VAPID authentication."""

import json
import logging
from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.push_subscription import PushSubscription

logger = logging.getLogger(__name__)

# pywebpush is optional — graceful fallback when not installed
try:
    from pywebpush import WebPushException, webpush

    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    logger.info("pywebpush not installed. Web Push notifications disabled.")


class PushService:
    """Service for sending Web Push notifications via VAPID."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def is_configured() -> bool:
        """Check if VAPID keys are configured."""
        return bool(
            WEBPUSH_AVAILABLE
            and settings.VAPID_PRIVATE_KEY
            and settings.VAPID_PUBLIC_KEY
            and settings.VAPID_CLAIMS_EMAIL
        )

    async def subscribe(
        self,
        user_id: int,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
        user_agent: Optional[str] = None,
    ) -> PushSubscription:
        """Register a browser push subscription.

        If the endpoint already exists, update the keys (browser may
        regenerate keys on re-subscribe).
        """
        result = await self.session.execute(
            select(PushSubscription).where(PushSubscription.endpoint == endpoint)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.user_id = user_id
            existing.p256dh_key = p256dh_key
            existing.auth_key = auth_key
            existing.user_agent = user_agent
            await self.session.commit()
            await self.session.refresh(existing)
            logger.info(f"Updated push subscription {existing.id} for user {user_id}")
            return existing

        subscription = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh_key,
            auth_key=auth_key,
            user_agent=user_agent,
        )
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        logger.info(f"Created push subscription {subscription.id} for user {user_id}")
        return subscription

    async def unsubscribe(self, user_id: int, endpoint: str) -> bool:
        """Remove a push subscription by endpoint."""
        result = await self.session.execute(
            delete(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == endpoint,
            )
        )
        await self.session.commit()
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Removed push subscription for user {user_id}")
        return deleted

    async def get_user_subscriptions(self, user_id: int) -> List[PushSubscription]:
        """Get all push subscriptions for a user."""
        result = await self.session.execute(
            select(PushSubscription).where(PushSubscription.user_id == user_id)
        )
        return list(result.scalars().all())

    async def send_push(
        self,
        user_id: int,
        title: str,
        body: str,
        url: Optional[str] = None,
    ) -> int:
        """Send a Web Push notification to all user subscriptions.

        Returns the number of successfully delivered pushes.
        Automatically removes expired/invalid subscriptions.
        """
        if not self.is_configured():
            logger.debug("Web Push not configured, skipping push delivery")
            return 0

        subscriptions = await self.get_user_subscriptions(user_id)
        if not subscriptions:
            return 0

        payload = json.dumps({
            "title": title,
            "body": body,
            "url": url,
        })

        vapid_claims = {"sub": settings.VAPID_CLAIMS_EMAIL}
        success_count = 0
        expired_ids: list[int] = []

        for sub in subscriptions:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh_key,
                    "auth": sub.auth_key,
                },
            }

            try:
                webpush(
                    subscription_info=subscription_info,
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims=vapid_claims,
                )
                success_count += 1
            except WebPushException as e:
                status_code = getattr(e, "response", None)
                if status_code and hasattr(status_code, "status_code"):
                    code = status_code.status_code
                else:
                    code = None

                if code in (404, 410):
                    # Subscription expired or unsubscribed
                    expired_ids.append(sub.id)
                    logger.info(
                        f"Push subscription {sub.id} expired (HTTP {code}), removing"
                    )
                else:
                    logger.error(
                        f"Failed to send push to subscription {sub.id}: {e}"
                    )
            except Exception as e:
                logger.error(f"Unexpected error sending push to {sub.id}: {e}")

        # Clean up expired subscriptions
        if expired_ids:
            await self.session.execute(
                delete(PushSubscription).where(PushSubscription.id.in_(expired_ids))
            )
            await self.session.commit()

        logger.info(
            f"Push delivery to user {user_id}: "
            f"{success_count}/{len(subscriptions)} successful, "
            f"{len(expired_ids)} expired removed"
        )
        return success_count
