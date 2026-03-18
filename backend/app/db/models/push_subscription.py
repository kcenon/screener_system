"""Push subscription model for Web Push API notifications."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import BaseModel, utc_now


class PushSubscription(BaseModel):
    """Browser push notification subscription (Web Push API).

    Stores the subscription information provided by the browser's
    PushManager.subscribe() method. Each user can have multiple
    subscriptions (one per browser/device).

    Attributes:
        user_id: Owner of the subscription.
        endpoint: Push service URL provided by the browser.
        p256dh_key: Public key for message encryption (base64url).
        auth_key: Authentication secret (base64url).
        user_agent: Browser user-agent string for identification.
        subscribed_at: When the subscription was created.
    """

    __tablename__ = "push_subscriptions"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    endpoint = Column(String(2048), nullable=False)
    p256dh_key = Column(String(256), nullable=False)
    auth_key = Column(String(256), nullable=False)
    user_agent = Column(String(512), nullable=True)
    subscribed_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="push_subscriptions")

    __table_args__ = (
        UniqueConstraint("endpoint", name="uq_push_subscriptions_endpoint"),
    )

    def __repr__(self) -> str:
        return (
            f"<PushSubscription(id={self.id}, user_id={self.user_id}, "
            f"endpoint={self.endpoint[:50]}...)>"
        )
