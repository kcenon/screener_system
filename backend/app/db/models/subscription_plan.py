"""Subscription plan database model"""

from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class SubscriptionPlan(BaseModel):
    """Subscription plan model defining available plans and their features"""

    __tablename__ = "subscription_plans"

    # Plan identification
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)

    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=False, default=0.00)
    price_yearly = Column(Numeric(10, 2), nullable=False, default=0.00)

    # Features and limits stored as JSON
    features = Column(JSONB, nullable=False, default=dict)
    limits = Column(JSONB, nullable=False, default=dict)

    # Status
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    # Relationships
    subscriptions = relationship(
        "UserSubscription",
        back_populates="plan",
        lazy="select",
    )

    def __repr__(self) -> str:
        """String representation"""
        return f"<SubscriptionPlan(name={self.name}, price_monthly={self.price_monthly})>"

    @property
    def yearly_discount_percent(self) -> float:
        """Calculate yearly discount percentage compared to monthly"""
        if self.price_monthly == 0:
            return 0.0
        yearly_equivalent = float(self.price_monthly) * 12
        yearly_price = float(self.price_yearly)
        if yearly_equivalent == 0:
            return 0.0
        return round((1 - yearly_price / yearly_equivalent) * 100, 1)

    def has_feature(self, feature_name: str) -> bool:
        """Check if plan has a specific feature"""
        return self.features.get(feature_name, False) if self.features else False

    def get_limit(self, limit_name: str) -> int:
        """
        Get limit value for a resource.

        Returns:
            -1 for unlimited, 0 for not available, positive int for actual limit
        """
        if not self.limits:
            return 0
        return self.limits.get(limit_name, 0)

    def get_all_features(self) -> Dict[str, bool]:
        """Get all features as a dictionary"""
        return dict(self.features) if self.features else {}

    def get_all_limits(self) -> Dict[str, int]:
        """Get all limits as a dictionary"""
        return dict(self.limits) if self.limits else {}

    def to_pricing_dict(self) -> Dict[str, Any]:
        """Convert to pricing display dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "price_monthly": float(self.price_monthly),
            "price_yearly": float(self.price_yearly),
            "yearly_discount_percent": self.yearly_discount_percent,
            "features": self.get_all_features(),
            "limits": self.get_all_limits(),
        }
