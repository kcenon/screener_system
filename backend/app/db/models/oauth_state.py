"""OAuth state database model for CSRF protection"""

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (CheckConstraint, Column, DateTime, ForeignKey, Index,
                        String)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class OAuthState(Base):
    """
    OAuth state model for CSRF protection during OAuth flow.

    State tokens are short-lived (typically 10 minutes) and used to:
    1. Prevent CSRF attacks by validating the state parameter on callback
    2. Store flow metadata (redirect URL, user ID for linking)
    """

    __tablename__ = "oauth_states"

    # Primary key
    id = Column("id", primary_key=True, autoincrement=True)

    # State token (random string)
    state = Column(String(255), unique=True, nullable=False, index=True)

    # OAuth flow information
    provider = Column(String(20), nullable=False)
    redirect_url = Column(String(512), nullable=True)

    # Optional user ID for account linking flow
    user_id = Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Additional metadata
    metadata = Column(JSONB, default=dict, nullable=False)

    # Relationships
    user = relationship("User")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "provider IN ('GOOGLE', 'KAKAO', 'NAVER')",
            name="valid_oauth_state_provider",
        ),
        Index("idx_oauth_states_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<OAuthState(id={self.id}, provider={self.provider}, "
            f"expires_at={self.expires_at})>"
        )

    @property
    def is_expired(self) -> bool:
        """Check if state token has expired"""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if state token is valid (not expired)"""
        return not self.is_expired

    @classmethod
    def create_state(
        cls,
        state: str,
        provider: str,
        redirect_url: Optional[str] = None,
        user_id: Optional[int] = None,
        expiry_minutes: int = 10,
        metadata: Optional[dict] = None,
    ) -> "OAuthState":
        """
        Factory method to create a new OAuth state.

        Args:
            state: Random state token
            provider: OAuth provider (GOOGLE, KAKAO, NAVER)
            redirect_url: URL to redirect after OAuth
            user_id: User ID for account linking (None for login/signup)
            expiry_minutes: State token expiration in minutes
            metadata: Additional flow metadata

        Returns:
            New OAuthState instance
        """
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)

        return cls(
            state=state,
            provider=provider.upper(),
            redirect_url=redirect_url,
            user_id=user_id,
            expires_at=expires_at,
            metadata=metadata or {},
        )
