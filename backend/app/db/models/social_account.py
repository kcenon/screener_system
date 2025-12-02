"""Social account database model for OAuth integration"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from app.db.base import BaseModel
from sqlalchemy import (CheckConstraint, Column, DateTime, ForeignKey, Index,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from app.db.models.user import User  # noqa: F401


class OAuthProvider(str, Enum):
    """Supported OAuth providers"""

    GOOGLE = "GOOGLE"
    KAKAO = "KAKAO"
    NAVER = "NAVER"


class SocialAccount(BaseModel):
    """
    Social account model for OAuth provider accounts linked to users.

    One user can have multiple social accounts (one per provider).
    Each social account is uniquely identified by provider + provider_user_id.
    """

    __tablename__ = "social_accounts"

    # Foreign key to user
    user_id = Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Provider information
    provider = Column(String(20), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255), nullable=True)
    provider_name = Column(String(255), nullable=True)
    provider_picture = Column(String(512), nullable=True)

    # OAuth tokens (should be encrypted in production)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="social_accounts")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "provider IN ('GOOGLE', 'KAKAO', 'NAVER')",
            name="valid_oauth_provider",
        ),
        UniqueConstraint("provider", "provider_user_id", name="unique_provider_user"),
        UniqueConstraint("user_id", "provider", name="unique_user_provider"),
        Index("idx_social_accounts_provider_email", "provider_email"),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<SocialAccount(id={self.id}, user_id={self.user_id}, "
            f"provider={self.provider}, email={self.provider_email})>"
        )

    @property
    def is_token_expired(self) -> bool:
        """Check if OAuth token has expired"""
        if not self.token_expires_at:
            return True
        from app.db.base import utc_now

        return self.token_expires_at < utc_now()

    def update_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        """Update OAuth tokens"""
        self.access_token = access_token
        if refresh_token:
            self.refresh_token = refresh_token
        if expires_at:
            self.token_expires_at = expires_at
