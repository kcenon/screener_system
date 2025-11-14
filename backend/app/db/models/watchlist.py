"""Watchlist database models"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.stock import Stock
    from app.db.models.user import User


class Watchlist(Base, TimestampMixin):
    """User watchlist model"""

    __tablename__ = "watchlists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="watchlists")
    stocks = relationship(
        "WatchlistStock",
        back_populates="watchlist",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "LENGTH(TRIM(name)) >= 1",
            name="valid_watchlist_name",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return f"<Watchlist(id={self.id}, name='{self.name}', user_id={self.user_id})>"

    @property
    def stock_count(self) -> int:
        """Get number of stocks in watchlist"""
        return len(self.stocks) if self.stocks else 0


class WatchlistStock(Base):
    """Junction table for watchlist stocks"""

    __tablename__ = "watchlist_stocks"

    watchlist_id = Column(
        UUID(as_uuid=True),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        primary_key=True,
    )
    stock_code = Column(
        String(6),
        ForeignKey("stocks.code", ondelete="CASCADE"),
        primary_key=True,
    )
    added_at = Column(
        DateTime(timezone=True),
        default=datetime.now,
        nullable=False,
        index=True,
    )
    notes = Column(Text, nullable=True)

    # Relationships
    watchlist = relationship("Watchlist", back_populates="stocks")
    stock = relationship("Stock")

    def __repr__(self) -> str:
        """String representation"""
        return f"<WatchlistStock(watchlist_id={self.watchlist_id}, stock_code={self.stock_code})>"


class UserActivity(Base):
    """User activity log model"""

    __tablename__ = "user_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now,
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("User", back_populates="activities")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "activity_type IN ('screening', 'watchlist_create', 'watchlist_update', "
            "'watchlist_delete', 'stock_add', 'stock_remove', 'stock_view', 'login', 'logout')",
            name="valid_activity_type",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return f"<UserActivity(id={self.id}, type='{self.activity_type}', user_id={self.user_id})>"


class UserPreferences(Base, TimestampMixin):
    """User preferences model"""

    __tablename__ = "user_preferences"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    default_watchlist_id = Column(
        UUID(as_uuid=True),
        ForeignKey("watchlists.id", ondelete="SET NULL"),
        nullable=True,
    )
    screening_quota_used = Column(
        "screening_quota_used",  # Explicit column name
        type_=Integer,
        default=0,
        nullable=False,
    )
    screening_quota_reset_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    dashboard_layout = Column(JSONB, nullable=True)
    notification_settings = Column(JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="preferences")
    default_watchlist = relationship("Watchlist", foreign_keys=[default_watchlist_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "screening_quota_used >= 0",
            name="valid_quota",
        ),
    )

    def __repr__(self) -> str:
        """String representation"""
        return f"<UserPreferences(user_id={self.user_id}, quota_used={self.screening_quota_used})>"
