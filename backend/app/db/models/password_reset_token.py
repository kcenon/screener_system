"""Password reset token database model"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class PasswordResetToken(BaseModel):
    """Password reset token model for account recovery"""

    __tablename__ = "password_reset_tokens"

    # Foreign key
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", backref="reset_tokens", lazy="select")

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, "
            f"used={'Yes' if self.used_at else 'No'})>"
        )

    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)"""
        from app.db.base import utc_now

        now = utc_now()
        return not self.is_used and self.expires_at > now

    @property
    def is_used(self) -> bool:
        """Check if token has been used"""
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        """Check if token has expired"""
        from app.db.base import utc_now

        return self.expires_at <= utc_now()

    def mark_as_used(self, timestamp: Optional[datetime] = None) -> None:
        """Mark token as used"""
        from app.db.base import utc_now

        self.used_at = timestamp or utc_now()

    @staticmethod
    def calculate_expiry(hours: int = 1) -> datetime:
        """Calculate token expiration time (default: 1 hour)"""
        from app.db.base import utc_now

        return utc_now() + timedelta(hours=hours)
