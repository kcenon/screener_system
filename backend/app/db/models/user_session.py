"""User session database model for refresh token management"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship

from app.db.base import Base, utc_now


class UserSession(Base):
    """User session model with refresh token"""

    __tablename__ = "user_sessions"

    # Primary key (UUID)
    id = Column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Foreign key to users table
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Refresh token (unique)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)

    # Session metadata
    ip_address = Column(INET)
    user_agent = Column(Text)

    # Token expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Revocation flag (for logout)
    revoked = Column(Boolean, default=False, server_default="false")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    last_accessed_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        """String representation"""
        status = "revoked" if self.revoked else "active"
        return f"<UserSession(id={self.id}, user_id={self.user_id}, status={status})>"

    @property
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return utc_now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if session is valid (not revoked and not expired)"""
        return not self.revoked and not self.is_expired

    def revoke(self) -> None:
        """Revoke this session"""
        self.revoked = True

    def update_last_accessed(self, timestamp: Optional[datetime] = None) -> None:
        """Update last accessed timestamp"""
        self.last_accessed_at = timestamp or utc_now()
