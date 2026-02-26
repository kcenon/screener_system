"""Subscription service for managing subscriptions and usage tracking"""

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.db.models import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    SubscriptionPlan,
    UsageTracking,
    User,
    UserSubscription,
)
from app.services.stripe_service import StripeService

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing subscriptions and feature access"""

    def __init__(self, session: AsyncSession):
        """Initialize subscription service"""
        self.session = session
        self.stripe_service = StripeService(session)

    # =========================================================================
    # PLAN MANAGEMENT
    # =========================================================================

    async def get_all_plans(self, active_only: bool = True) -> List[SubscriptionPlan]:
        """Get all subscription plans"""
        query = select(SubscriptionPlan)
        if active_only:
            query = query.where(SubscriptionPlan.is_active.is_(True))
        query = query.order_by(SubscriptionPlan.sort_order)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_plan_by_name(self, name: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by name"""
        result = await self.session.execute(
            select(SubscriptionPlan).where(
                func.upper(SubscriptionPlan.name) == name.upper()
            )
        )
        return result.scalar_one_or_none()

    async def get_plan_by_id(self, plan_id: int) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID"""
        result = await self.session.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
        )
        return result.scalar_one_or_none()

    # =========================================================================
    # USER SUBSCRIPTION MANAGEMENT
    # =========================================================================

    async def get_user_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """Get active subscription for user"""
        result = await self.session.execute(
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.status.in_(["active", "trial"]),
            )
            .order_by(UserSubscription.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_user_plan(self, user_id: int) -> SubscriptionPlan:
        """
        Get current plan for user (returns FREE if no active subscription).

        Args:
            user_id: User ID

        Returns:
            User's current subscription plan
        """
        subscription = await self.get_user_subscription(user_id)

        if subscription and subscription.is_active:
            plan = await self.get_plan_by_id(subscription.plan_id)
            if plan:
                return plan

        # Return free plan as default
        free_plan = await self.get_plan_by_name("FREE")
        if not free_plan:
            raise NotFoundException("Free plan not found")
        return free_plan

    async def subscribe(
        self,
        user: User,
        plan_name: str,
        billing_cycle: str,
        payment_method_id: Optional[str] = None,
    ) -> Tuple[UserSubscription, Optional[str]]:
        """
        Subscribe user to a plan.

        Args:
            user: User to subscribe
            plan_name: Plan name (PREMIUM or PRO)
            billing_cycle: 'monthly' or 'yearly'
            payment_method_id: Stripe payment method ID

        Returns:
            Tuple of (subscription, client_secret_if_needed)
        """
        plan = await self.get_plan_by_name(plan_name)
        if not plan:
            raise NotFoundException(f"Plan '{plan_name}' not found")

        if plan.name == "FREE":
            raise BadRequestException("Cannot subscribe to free plan")

        # Check for existing active subscription
        existing = await self.get_user_subscription(user.id)
        if existing and existing.is_active:
            raise BadRequestException(
                "Already have an active subscription. Please cancel or upgrade instead."
            )

        # Determine if trial is available
        trial_days = None
        if not await self._has_used_trial(user.id):
            trial_days = settings.TRIAL_PERIOD_DAYS

        return await self.stripe_service.create_subscription(
            user=user,
            plan=plan,
            billing_cycle=billing_cycle,
            payment_method_id=payment_method_id,
            trial_days=trial_days,
        )

    async def cancel_subscription(
        self,
        user: User,
        immediate: bool = False,
        reason: Optional[str] = None,
    ) -> UserSubscription:
        """Cancel user's subscription"""
        subscription = await self.get_user_subscription(user.id)
        if not subscription:
            raise NotFoundException("No active subscription found")

        if subscription.is_canceled:
            raise BadRequestException("Subscription is already canceled")

        # Store cancellation reason in metadata
        if reason:
            metadata = subscription.metadata or {}
            metadata["cancellation_reason"] = reason
            subscription.metadata = metadata

        return await self.stripe_service.cancel_subscription(subscription, immediate)

    async def upgrade_subscription(
        self,
        user: User,
        new_plan_name: str,
        prorate: bool = True,
    ) -> UserSubscription:
        """Upgrade or downgrade subscription to a new plan"""
        subscription = await self.get_user_subscription(user.id)
        if not subscription:
            raise NotFoundException("No active subscription found")

        new_plan = await self.get_plan_by_name(new_plan_name)
        if not new_plan:
            raise NotFoundException(f"Plan '{new_plan_name}' not found")

        if subscription.plan_id == new_plan.id:
            raise BadRequestException("Already on this plan")

        return await self.stripe_service.update_subscription(
            subscription, new_plan, prorate
        )

    async def _has_used_trial(self, user_id: int) -> bool:
        """Check if user has already used a trial"""
        result = await self.session.execute(
            select(UserSubscription).where(
                UserSubscription.user_id == user_id,
                UserSubscription.trial_start.isnot(None),
            )
        )
        return result.scalar_one_or_none() is not None

    # =========================================================================
    # FEATURE ACCESS
    # =========================================================================

    async def has_feature_access(self, user_id: int, feature: str) -> bool:
        """
        Check if user has access to a specific feature.

        Args:
            user_id: User ID
            feature: Feature name (e.g., 'api_access', 'advanced_charts')

        Returns:
            True if user has access
        """
        plan = await self.get_user_plan(user_id)
        return plan.has_feature(feature)

    async def get_feature_access_list(self, user_id: int) -> Dict[str, Any]:
        """Get all feature access for user"""
        plan = await self.get_user_plan(user_id)
        return {
            "plan_name": plan.name,
            "features": plan.get_all_features(),
            "limits": plan.get_all_limits(),
        }

    async def check_feature_access(
        self,
        user_id: int,
        feature: str,
        required_plan: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check feature access and return detailed status.

        Args:
            user_id: User ID
            feature: Feature name
            required_plan: Minimum plan required for feature

        Returns:
            Dict with access status and details
        """
        plan = await self.get_user_plan(user_id)
        has_access = plan.has_feature(feature)

        return {
            "feature_name": feature,
            "has_access": has_access,
            "required_plan": required_plan,
            "message": (
                None
                if has_access
                else f"Upgrade to {required_plan or 'Premium'} to access this feature"
            ),
        }

    # =========================================================================
    # USAGE TRACKING
    # =========================================================================

    async def check_usage_limit(
        self,
        user_id: int,
        resource_type: str,
        period_type: str = "daily",
    ) -> Tuple[bool, int]:
        """
        Check if user has reached usage limit.

        Args:
            user_id: User ID
            resource_type: Resource type (screening, api_call, etc.)
            period_type: Period type (daily, monthly)

        Returns:
            Tuple of (has_access, remaining_count)
        """
        plan = await self.get_user_plan(user_id)

        # Map resource type to limit name
        limit_map = {
            "screening": "searches_per_day",
            "api_call": "api_calls_per_day",
            "alert": "alerts",
            "portfolio": "portfolios",
            "export": "exports_per_day",
        }
        limit_name = limit_map.get(resource_type, resource_type)
        limit_value = plan.get_limit(limit_name)

        # -1 means unlimited
        if limit_value == -1:
            return True, -1

        # Get current usage
        current_usage = await self._get_current_usage(
            user_id, resource_type, period_type
        )

        has_access = current_usage < limit_value
        remaining = max(0, limit_value - current_usage)

        return has_access, remaining

    async def increment_usage(
        self,
        user_id: int,
        resource_type: str,
        count: int = 1,
        period_type: str = "daily",
    ) -> int:
        """
        Increment usage counter.

        Args:
            user_id: User ID
            resource_type: Resource type
            count: Amount to increment
            period_type: Period type

        Returns:
            New usage count
        """
        period_start = self._get_period_start(period_type)

        # Try to update existing record
        result = await self.session.execute(
            select(UsageTracking).where(
                UsageTracking.user_id == user_id,
                UsageTracking.resource_type == resource_type,
                UsageTracking.period_start == period_start,
                UsageTracking.period_type == period_type,
            )
        )
        usage = result.scalar_one_or_none()

        if usage:
            usage.count += count
        else:
            usage = UsageTracking(
                user_id=user_id,
                resource_type=resource_type,
                count=count,
                period_start=period_start,
                period_type=period_type,
            )
            self.session.add(usage)

        await self.session.flush()
        return usage.count

    async def get_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """Get usage statistics for user"""
        plan = await self.get_user_plan(user_id)
        today = date.today()

        # Get today's usage
        result = await self.session.execute(
            select(UsageTracking).where(
                UsageTracking.user_id == user_id,
                UsageTracking.period_start == today,
                UsageTracking.period_type == "daily",
            )
        )
        daily_usage = {u.resource_type: u.count for u in result.scalars().all()}

        # Build usage stats
        limits = plan.get_all_limits()
        usage_list = []

        for resource_type in ["screening", "api_call", "alert", "portfolio", "export"]:
            limit_map = {
                "screening": "searches_per_day",
                "api_call": "api_calls_per_day",
                "alert": "alerts",
                "portfolio": "portfolios",
                "export": "exports_per_day",
            }
            limit_name = limit_map.get(resource_type, resource_type)
            limit_value = limits.get(limit_name, 0)
            current = daily_usage.get(resource_type, 0)

            usage_list.append(
                {
                    "resource_type": resource_type,
                    "current_usage": current,
                    "limit_value": limit_value,
                    "has_access": limit_value == -1 or current < limit_value,
                    "remaining": (
                        -1 if limit_value == -1 else max(0, limit_value - current)
                    ),
                }
            )

        return {
            "user_id": user_id,
            "plan_name": plan.name,
            "period_start": datetime.combine(today, datetime.min.time()).replace(
                tzinfo=timezone.utc
            ),
            "period_end": datetime.combine(today, datetime.max.time()).replace(
                tzinfo=timezone.utc
            ),
            "usage": usage_list,
            "total_searches_today": daily_usage.get("screening", 0),
            "total_api_calls_today": daily_usage.get("api_call", 0),
        }

    async def _get_current_usage(
        self,
        user_id: int,
        resource_type: str,
        period_type: str,
    ) -> int:
        """Get current usage count for a resource"""
        period_start = self._get_period_start(period_type)

        result = await self.session.execute(
            select(UsageTracking.count).where(
                UsageTracking.user_id == user_id,
                UsageTracking.resource_type == resource_type,
                UsageTracking.period_start == period_start,
                UsageTracking.period_type == period_type,
            )
        )
        count = result.scalar_one_or_none()
        return count or 0

    def _get_period_start(self, period_type: str) -> date:
        """Get period start date"""
        today = date.today()
        if period_type == "monthly":
            return today.replace(day=1)
        return today

    # =========================================================================
    # PAYMENT METHODS
    # =========================================================================

    async def get_payment_methods(self, user_id: int) -> List[PaymentMethod]:
        """Get all payment methods for user"""
        result = await self.session.execute(
            select(PaymentMethod)
            .where(PaymentMethod.user_id == user_id)
            .order_by(PaymentMethod.is_default.desc(), PaymentMethod.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_payment_method(
        self,
        user: User,
        payment_method_id: str,
        set_as_default: bool = True,
    ) -> PaymentMethod:
        """Add a new payment method"""
        return await self.stripe_service.attach_payment_method(
            user, payment_method_id, set_as_default
        )

    async def remove_payment_method(
        self,
        user: User,
        payment_method_id: int,
    ) -> None:
        """Remove a payment method"""
        result = await self.session.execute(
            select(PaymentMethod).where(
                PaymentMethod.id == payment_method_id,
                PaymentMethod.user_id == user.id,
            )
        )
        payment_method = result.scalar_one_or_none()

        if not payment_method:
            raise NotFoundException("Payment method not found")

        # Check if it's the only payment method with active subscription
        subscription = await self.get_user_subscription(user.id)
        if subscription and subscription.is_active:
            payment_methods = await self.get_payment_methods(user.id)
            if len(payment_methods) <= 1:
                raise BadRequestException(
                    "Cannot remove the only payment method while subscription is active"
                )

        await self.stripe_service.detach_payment_method(payment_method)

    async def set_default_payment_method(
        self,
        user: User,
        payment_method_id: int,
    ) -> PaymentMethod:
        """Set a payment method as default"""
        result = await self.session.execute(
            select(PaymentMethod).where(
                PaymentMethod.id == payment_method_id,
                PaymentMethod.user_id == user.id,
            )
        )
        payment_method = result.scalar_one_or_none()

        if not payment_method:
            raise NotFoundException("Payment method not found")

        # Unset other defaults
        await self.session.execute(
            update(PaymentMethod)
            .where(PaymentMethod.user_id == user.id)
            .values(is_default=False)
        )

        payment_method.is_default = True
        await self.session.flush()

        return payment_method

    # =========================================================================
    # PAYMENT HISTORY
    # =========================================================================

    async def get_payment_history(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Payment], int, Decimal]:
        """
        Get payment history for user.

        Returns:
            Tuple of (payments, total_count, total_amount)
        """
        # Get total count
        count_result = await self.session.execute(
            select(func.count(Payment.id)).where(Payment.user_id == user_id)
        )
        total_count = count_result.scalar_one()

        # Get total amount of successful payments
        amount_result = await self.session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.SUCCEEDED.value,
            )
        )
        total_amount = amount_result.scalar_one() or Decimal("0")

        # Get payments
        result = await self.session.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        payments = list(result.scalars().all())

        return payments, total_count, total_amount

    async def retry_payment(
        self,
        user: User,
        payment_id: int,
        payment_method_id: Optional[str] = None,
    ) -> Payment:
        """Retry a failed payment"""
        result = await self.session.execute(
            select(Payment).where(
                Payment.id == payment_id,
                Payment.user_id == user.id,
            )
        )
        payment = result.scalar_one_or_none()

        if not payment:
            raise NotFoundException("Payment not found")

        if payment.status != PaymentStatus.FAILED.value:
            raise BadRequestException("Only failed payments can be retried")

        return await self.stripe_service.retry_payment(payment, payment_method_id)

    # =========================================================================
    # SUBSCRIPTION DETAILS
    # =========================================================================

    async def get_subscription_details(self, user: User) -> Dict[str, Any]:
        """Get comprehensive subscription details for user"""
        subscription = await self.get_user_subscription(user.id)
        plan = await self.get_user_plan(user.id)
        usage_stats = await self.get_usage_stats(user.id)
        payment_methods = await self.get_payment_methods(user.id)

        details = {
            "plan": {
                "id": plan.id,
                "name": plan.name,
                "display_name": plan.display_name,
                "price_monthly": float(plan.price_monthly),
                "price_yearly": float(plan.price_yearly),
                "features": plan.get_all_features(),
                "limits": plan.get_all_limits(),
            },
            "subscription": None,
            "usage": usage_stats,
            "payment_methods": [
                {
                    "id": pm.id,
                    "display_name": pm.display_name,
                    "is_default": pm.is_default,
                    "is_expired": pm.is_expired,
                }
                for pm in payment_methods
            ],
        }

        if subscription:
            details["subscription"] = {
                "id": subscription.id,
                "status": subscription.status,
                "billing_cycle": subscription.billing_cycle,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "trial_end": subscription.trial_end,
                "days_until_renewal": subscription.days_until_renewal,
                "trial_days_remaining": subscription.trial_days_remaining,
            }

        return details
