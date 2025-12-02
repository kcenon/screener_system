"""Stripe webhook event database model"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.db.base import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, String, Text

# from sqlalchemy.dialects.postgresql import JSONB


class StripeWebhookEvent(BaseModel):
    """Stripe webhook event model for idempotency and audit trail"""

    __tablename__ = "stripe_webhook_events"

    # Event identification
    stripe_event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)

    # Processing status
    processed = Column(Boolean, default=False, index=True)
    processing_error = Column(Text)
    processed_at = Column(DateTime(timezone=True))

    # Event payload
    payload = Column(JSON, nullable=False)

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<StripeWebhookEvent(id={self.id}, type={self.event_type}, "
            f"processed={self.processed})>"
        )

    @property
    def is_processed(self) -> bool:
        """Check if event has been processed"""
        return self.processed

    @property
    def has_error(self) -> bool:
        """Check if event processing had an error"""
        return self.processing_error is not None

    def mark_as_processed(self) -> None:
        """Mark event as successfully processed"""
        self.processed = True
        self.processed_at = datetime.now(timezone.utc)
        self.processing_error = None

    def mark_as_failed(self, error: str) -> None:
        """Mark event as failed with error message"""
        self.processed = True
        self.processed_at = datetime.now(timezone.utc)
        self.processing_error = error

    def get_payload_data(self) -> Dict[str, Any]:
        """Get payload as dictionary"""
        return dict(self.payload) if self.payload else {}

    def get_object(self) -> Optional[Dict[str, Any]]:
        """Get the Stripe object from the event payload"""
        payload = self.get_payload_data()
        data = payload.get("data", {})
        return data.get("object")

    @classmethod
    def event_type_prefix(cls, event_type: str) -> str:
        """
        Extract the prefix from an event type (e.g., 'invoice' from 'invoice.paid')
        """
        return event_type.split(".")[0] if "." in event_type else event_type
