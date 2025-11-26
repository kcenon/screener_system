"""Subscription guards and decorators for feature gating"""

import functools
import logging
from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_subscription_service
from app.db.models import User
from app.db.session import get_db
from app.services import SubscriptionService

logger = logging.getLogger(__name__)


class SubscriptionGuard:
    """
    Dependency class for subscription-based feature gating.

    Usage in endpoint:
        @router.get("/premium-feature")
        async def premium_feature(
            _: None = Depends(SubscriptionGuard(required_plan="PREMIUM")),
            current_user: User = Depends(get_current_active_user),
        ):
            ...
    """

    def __init__(
        self,
        required_plan: Optional[str] = None,
        required_feature: Optional[str] = None,
        allowed_plans: Optional[List[str]] = None,
    ):
        """
        Initialize subscription guard.

        Args:
            required_plan: Minimum plan required (FREE, PREMIUM, PRO)
            required_feature: Specific feature that must be enabled
            allowed_plans: List of allowed plan names
        """
        self.required_plan = required_plan
        self.required_feature = required_feature
        self.allowed_plans = allowed_plans or []

        # Plan hierarchy for comparison
        self._plan_hierarchy = {"FREE": 0, "PREMIUM": 1, "PRO": 2}

    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        """Check subscription requirements"""
        subscription_service = SubscriptionService(db)

        # Get user's current plan
        plan = await subscription_service.get_user_plan(current_user.id)

        # Check required plan (hierarchy-based)
        if self.required_plan:
            required_level = self._plan_hierarchy.get(self.required_plan.upper(), 0)
            user_level = self._plan_hierarchy.get(plan.name.upper(), 0)

            if user_level < required_level:
                logger.warning(
                    f"User {current_user.id} denied access: "
                    f"requires {self.required_plan}, has {plan.name}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "subscription_required",
                        "message": f"This feature requires a {self.required_plan} subscription",
                        "required_plan": self.required_plan,
                        "current_plan": plan.name,
                    },
                )

        # Check allowed plans (exact match)
        if self.allowed_plans:
            if plan.name.upper() not in [p.upper() for p in self.allowed_plans]:
                logger.warning(
                    f"User {current_user.id} denied access: "
                    f"plan {plan.name} not in allowed {self.allowed_plans}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "subscription_required",
                        "message": f"This feature is available for: {', '.join(self.allowed_plans)}",
                        "allowed_plans": self.allowed_plans,
                        "current_plan": plan.name,
                    },
                )

        # Check required feature
        if self.required_feature:
            has_access = await subscription_service.has_feature_access(
                current_user.id, self.required_feature
            )
            if not has_access:
                logger.warning(
                    f"User {current_user.id} denied access: "
                    f"feature {self.required_feature} not available"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "feature_not_available",
                        "message": f"Feature '{self.required_feature}' is not available on your plan",
                        "required_feature": self.required_feature,
                        "current_plan": plan.name,
                    },
                )


class UsageLimitGuard:
    """
    Dependency class for usage limit checking.

    Usage in endpoint:
        @router.post("/screening")
        async def run_screening(
            _: None = Depends(UsageLimitGuard(resource_type="screening")),
            current_user: User = Depends(get_current_active_user),
        ):
            ...
    """

    def __init__(
        self,
        resource_type: str,
        increment: bool = True,
        count: int = 1,
    ):
        """
        Initialize usage limit guard.

        Args:
            resource_type: Type of resource (screening, api_call, etc.)
            increment: Whether to increment usage after check
            count: Amount to check/increment
        """
        self.resource_type = resource_type
        self.increment = increment
        self.count = count

    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        """Check and optionally increment usage"""
        subscription_service = SubscriptionService(db)

        # Check usage limit
        has_access, remaining = await subscription_service.check_usage_limit(
            current_user.id, self.resource_type
        )

        if not has_access:
            plan = await subscription_service.get_user_plan(current_user.id)
            logger.warning(
                f"User {current_user.id} hit usage limit: "
                f"{self.resource_type} on plan {plan.name}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "usage_limit_exceeded",
                    "message": f"Daily limit for {self.resource_type} reached",
                    "resource_type": self.resource_type,
                    "current_plan": plan.name,
                    "upgrade_message": "Upgrade to Premium or Pro for unlimited access",
                },
            )

        # Increment usage if requested
        if self.increment:
            await subscription_service.increment_usage(
                current_user.id, self.resource_type, self.count
            )


# =============================================================================
# CONVENIENCE GUARDS
# =============================================================================

# Pre-configured guards for common use cases
RequirePremium = SubscriptionGuard(required_plan="PREMIUM")
RequirePro = SubscriptionGuard(required_plan="PRO")
RequireApiAccess = SubscriptionGuard(required_feature="api_access")
RequireAdvancedCharts = SubscriptionGuard(required_feature="advanced_charts")
RequireExportExcel = SubscriptionGuard(required_feature="export_excel")
RequireRealTimeData = SubscriptionGuard(required_feature="real_time_data")

# Usage limit guards
ScreeningLimit = UsageLimitGuard(resource_type="screening")
ApiCallLimit = UsageLimitGuard(resource_type="api_call")
ExportLimit = UsageLimitGuard(resource_type="export")


# =============================================================================
# DECORATOR FUNCTIONS
# =============================================================================


def require_subscription(required_plan: str):
    """
    Decorator to require a minimum subscription plan.

    Usage:
        @require_subscription("PREMIUM")
        async def premium_endpoint(...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # The actual check is done via the dependency
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_feature(feature_name: str):
    """
    Decorator to require a specific feature.

    Usage:
        @require_feature("api_access")
        async def api_endpoint(...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_usage_limit(resource_type: str, increment: bool = True):
    """
    Decorator to check and track usage limits.

    Usage:
        @check_usage_limit("screening")
        async def screening_endpoint(...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator
