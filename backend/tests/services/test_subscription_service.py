"""Tests for SubscriptionService"""

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SubscriptionPlan, UsageTracking, User, UserSubscription
from app.services.subscription_service import SubscriptionService


@pytest_asyncio.fixture
async def subscription_plans(db: AsyncSession) -> list[SubscriptionPlan]:
    """Create test subscription plans"""
    plans = [
        SubscriptionPlan(
            name="FREE",
            display_name="Free",
            description="Basic free plan",
            price_monthly=Decimal("0.00"),
            price_yearly=Decimal("0.00"),
            features={
                "screening_results": True,
                "basic_indicators": True,
                "api_access": False,
            },
            limits={
                "searches_per_day": 10,
                "api_calls_per_day": 0,
                "portfolios": 0,
            },
            sort_order=1,
        ),
        SubscriptionPlan(
            name="PREMIUM",
            display_name="Premium",
            description="Premium plan",
            price_monthly=Decimal("9.99"),
            price_yearly=Decimal("99.00"),
            features={
                "screening_results": True,
                "basic_indicators": True,
                "advanced_indicators": True,
                "api_access": False,
            },
            limits={
                "searches_per_day": -1,  # Unlimited
                "api_calls_per_day": 0,
                "portfolios": 3,
            },
            sort_order=2,
        ),
        SubscriptionPlan(
            name="PRO",
            display_name="Pro",
            description="Pro plan",
            price_monthly=Decimal("29.99"),
            price_yearly=Decimal("299.00"),
            features={
                "screening_results": True,
                "basic_indicators": True,
                "advanced_indicators": True,
                "api_access": True,
            },
            limits={
                "searches_per_day": -1,
                "api_calls_per_day": 1000,
                "portfolios": -1,
            },
            sort_order=3,
        ),
    ]

    for plan in plans:
        db.add(plan)

    await db.commit()

    for plan in plans:
        await db.refresh(plan)

    return plans


@pytest_asyncio.fixture
async def subscription_service(db: AsyncSession) -> SubscriptionService:
    """Create SubscriptionService instance"""
    return SubscriptionService(db)


class TestGetAllPlans:
    """Tests for get_all_plans method"""

    @pytest.mark.asyncio
    async def test_returns_all_active_plans(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should return all active plans sorted by sort_order"""
        plans = await subscription_service.get_all_plans()

        assert len(plans) == 3
        assert plans[0].name == "FREE"
        assert plans[1].name == "PREMIUM"
        assert plans[2].name == "PRO"

    @pytest.mark.asyncio
    async def test_excludes_inactive_plans(
        self,
        db: AsyncSession,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should exclude inactive plans"""
        # Deactivate one plan
        subscription_plans[1].is_active = False
        await db.commit()

        plans = await subscription_service.get_all_plans(active_only=True)

        assert len(plans) == 2
        assert all(p.name != "PREMIUM" for p in plans)


class TestGetPlanByName:
    """Tests for get_plan_by_name method"""

    @pytest.mark.asyncio
    async def test_returns_plan_when_exists(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should return plan when it exists"""
        plan = await subscription_service.get_plan_by_name("PREMIUM")

        assert plan is not None
        assert plan.name == "PREMIUM"
        assert plan.price_monthly == 9.99

    @pytest.mark.asyncio
    async def test_case_insensitive_lookup(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should find plan regardless of case"""
        plan = await subscription_service.get_plan_by_name("premium")

        assert plan is not None
        assert plan.name == "PREMIUM"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_exists(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should return None when plan doesn't exist"""
        plan = await subscription_service.get_plan_by_name("NONEXISTENT")

        assert plan is None


class TestGetUserPlan:
    """Tests for get_user_plan method"""

    @pytest.mark.asyncio
    async def test_returns_free_plan_for_user_without_subscription(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Should return FREE plan for users without active subscription"""
        plan = await subscription_service.get_user_plan(test_user.id)

        assert plan.name == "FREE"

    @pytest.mark.asyncio
    async def test_returns_subscribed_plan(
        self,
        db: AsyncSession,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Should return user's active subscription plan"""
        # Create subscription for user
        premium_plan = subscription_plans[1]  # PREMIUM
        subscription = UserSubscription(
            user_id=test_user.id,
            plan_id=premium_plan.id,
            status="active",
            billing_cycle="monthly",
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc),
        )
        db.add(subscription)
        await db.commit()

        plan = await subscription_service.get_user_plan(test_user.id)

        assert plan.name == "PREMIUM"


class TestHasFeatureAccess:
    """Tests for has_feature_access method"""

    @pytest.mark.asyncio
    async def test_free_user_has_basic_features(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Free user should have access to basic features"""
        has_access = await subscription_service.has_feature_access(
            test_user.id, "basic_indicators"
        )

        assert has_access is True

    @pytest.mark.asyncio
    async def test_free_user_no_api_access(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Free user should not have API access"""
        has_access = await subscription_service.has_feature_access(
            test_user.id, "api_access"
        )

        assert has_access is False


class TestCheckUsageLimit:
    """Tests for check_usage_limit method"""

    @pytest.mark.asyncio
    async def test_allows_usage_under_limit(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Should allow usage when under limit"""
        has_access, remaining = await subscription_service.check_usage_limit(
            test_user.id, "screening"
        )

        assert has_access is True
        assert remaining == 10  # FREE tier limit

    @pytest.mark.asyncio
    async def test_denies_usage_at_limit(
        self,
        db: AsyncSession,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Should deny usage when at limit"""
        # Add usage record at limit
        usage = UsageTracking(
            user_id=test_user.id,
            resource_type="screening",
            count=10,  # At FREE tier limit
            period_start=date.today(),
            period_type="daily",
        )
        db.add(usage)
        await db.commit()

        has_access, remaining = await subscription_service.check_usage_limit(
            test_user.id, "screening"
        )

        assert has_access is False
        assert remaining == 0


class TestIncrementUsage:
    """Tests for increment_usage method"""

    @pytest.mark.asyncio
    async def test_creates_new_usage_record(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Should create new usage record if none exists"""
        new_count = await subscription_service.increment_usage(
            test_user.id, "screening"
        )

        assert new_count == 1

    @pytest.mark.asyncio
    async def test_increments_existing_usage(
        self,
        db: AsyncSession,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Should increment existing usage record"""
        # Create initial usage
        usage = UsageTracking(
            user_id=test_user.id,
            resource_type="screening",
            count=5,
            period_start=date.today(),
            period_type="daily",
        )
        db.add(usage)
        await db.commit()

        new_count = await subscription_service.increment_usage(
            test_user.id, "screening"
        )

        assert new_count == 6


class TestGetUsageStats:
    """Tests for get_usage_stats method"""

    @pytest.mark.asyncio
    async def test_returns_usage_stats(
        self,
        subscription_service: SubscriptionService,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
    ):
        """Should return usage statistics"""
        stats = await subscription_service.get_usage_stats(test_user.id)

        assert stats["user_id"] == test_user.id
        assert stats["plan_name"] == "FREE"
        assert "usage" in stats
        assert isinstance(stats["usage"], list)


class TestSubscriptionPlanModel:
    """Tests for SubscriptionPlan model methods"""

    def test_has_feature(self):
        """Should correctly check feature availability"""
        plan = SubscriptionPlan(
            name="TEST",
            display_name="Test",
            features={"feature_a": True, "feature_b": False},
            limits={},
        )

        assert plan.has_feature("feature_a") is True
        assert plan.has_feature("feature_b") is False
        assert plan.has_feature("feature_c") is False

    def test_get_limit(self):
        """Should correctly get limit values"""
        plan = SubscriptionPlan(
            name="TEST",
            display_name="Test",
            features={},
            limits={"searches_per_day": 10, "portfolios": -1},
        )

        assert plan.get_limit("searches_per_day") == 10
        assert plan.get_limit("portfolios") == -1  # Unlimited
        assert plan.get_limit("nonexistent") == 0

    def test_yearly_discount_percent(self):
        """Should calculate yearly discount percentage"""
        plan = SubscriptionPlan(
            name="TEST",
            display_name="Test",
            price_monthly=Decimal("10.00"),
            price_yearly=Decimal("100.00"),  # ~17% discount
            features={},
            limits={},
        )

        assert plan.yearly_discount_percent == pytest.approx(16.7, abs=0.1)
