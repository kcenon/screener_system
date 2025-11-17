"""User database model"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, String
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class User(BaseModel):
    """User account model"""

    __tablename__ = "users"

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))

    # Subscription
    subscription_tier = Column(
        String(20),
        nullable=False,
        default="free",
        server_default="free",
    )
    subscription_starts_at = Column(DateTime(timezone=True))
    subscription_expires_at = Column(DateTime(timezone=True))

    # Email verification
    email_verified = Column(Boolean, default=False, server_default="false")
    email_verification_token = Column(String(255))

    # Password reset
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime(timezone=True))

    # Activity tracking
    last_login_at = Column(DateTime(timezone=True))

    # Relationships
    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    watchlists = relationship(
        "Watchlist",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    portfolios = relationship(
        "Portfolio",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    activities = relationship(
        "UserActivity",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="select",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "subscription_tier IN ('free', 'basic', 'pro')",
            name="valid_subscription_tier",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<User(id={self.id}, email={self.email}, tier={self.subscription_tier})>"
        )

    @property
    def is_active(self) -> bool:
        """Check if user account is active"""
        # Could add more conditions like email_verified, account suspension, etc.
        return True

    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_tier in ("basic", "pro")

    @property
    def is_pro(self) -> bool:
        """Check if user has pro subscription"""
        return self.subscription_tier == "pro"

    def update_last_login(self, timestamp: Optional[datetime] = None) -> None:
        """Update last login timestamp"""
        from app.db.base import utc_now

        self.last_login_at = timestamp or utc_now()
