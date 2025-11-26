"""Tests for subscription API endpoints"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SubscriptionPlan, User, UserSubscription


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
            },
            limits={
                "searches_per_day": -1,
                "api_calls_per_day": 0,
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


class TestListPlans:
    """Tests for GET /v1/subscriptions/plans"""

    @pytest.mark.asyncio
    async def test_list_plans_returns_all_plans(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should return all subscription plans"""
        response = await client.get("/v1/subscriptions/plans")

        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 3

    @pytest.mark.asyncio
    async def test_list_plans_includes_features(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should include features for each plan"""
        response = await client.get("/v1/subscriptions/plans")

        data = response.json()
        for plan in data["plans"]:
            assert "features" in plan
            assert "limits" in plan

    @pytest.mark.asyncio
    async def test_list_plans_ordered_by_price(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should return plans in order"""
        response = await client.get("/v1/subscriptions/plans")

        data = response.json()
        plan_names = [p["name"] for p in data["plans"]]
        assert plan_names == ["FREE", "PREMIUM", "PRO"]


class TestGetCurrentSubscription:
    """Tests for GET /v1/subscriptions/current"""

    @pytest.mark.asyncio
    async def test_requires_authentication(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should require authentication"""
        response = await client.get("/v1/subscriptions/current")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_free_plan_for_new_user(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
        auth_headers: dict,
    ):
        """Should return FREE plan for users without subscription"""
        response = await client.get(
            "/v1/subscriptions/current",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["plan_name"] == "FREE"

    @pytest.mark.asyncio
    async def test_returns_active_subscription(
        self,
        db: AsyncSession,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
        test_user: User,
        auth_headers: dict,
    ):
        """Should return active subscription details"""
        # Create subscription
        premium_plan = subscription_plans[1]
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

        response = await client.get(
            "/v1/subscriptions/current",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["plan_name"] == "PREMIUM"
        assert data["status"] == "active"


class TestGetUsageStats:
    """Tests for GET /v1/subscriptions/usage"""

    @pytest.mark.asyncio
    async def test_requires_authentication(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should require authentication"""
        response = await client.get("/v1/subscriptions/usage")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_usage_stats(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
        auth_headers: dict,
        test_user: User,
    ):
        """Should return usage statistics"""
        response = await client.get(
            "/v1/subscriptions/usage",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert "usage" in data


class TestGetFeatureAccess:
    """Tests for GET /v1/subscriptions/features"""

    @pytest.mark.asyncio
    async def test_requires_authentication(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
    ):
        """Should require authentication"""
        response = await client.get("/v1/subscriptions/features")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_feature_access(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
        auth_headers: dict,
    ):
        """Should return feature access list"""
        response = await client.get(
            "/v1/subscriptions/features",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert "limits" in data


class TestCheckFeatureAccess:
    """Tests for GET /v1/subscriptions/features/{feature_name}"""

    @pytest.mark.asyncio
    async def test_check_available_feature(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
        auth_headers: dict,
    ):
        """Should return access info for available feature"""
        response = await client.get(
            "/v1/subscriptions/features/basic_indicators",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["feature_name"] == "basic_indicators"
        assert data["has_access"] is True

    @pytest.mark.asyncio
    async def test_check_unavailable_feature(
        self,
        client: AsyncClient,
        subscription_plans: list[SubscriptionPlan],
        auth_headers: dict,
    ):
        """Should return access info for unavailable feature"""
        response = await client.get(
            "/v1/subscriptions/features/api_access",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["feature_name"] == "api_access"
        assert data["has_access"] is False


class TestListPaymentMethods:
    """Tests for GET /v1/subscriptions/payment-methods"""

    @pytest.mark.asyncio
    async def test_requires_authentication(
        self,
        client: AsyncClient,
    ):
        """Should require authentication"""
        response = await client.get("/v1/subscriptions/payment-methods")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_new_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Should return empty list for users without payment methods"""
        response = await client.get(
            "/v1/subscriptions/payment-methods",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["payment_methods"] == []


class TestGetPaymentHistory:
    """Tests for GET /v1/subscriptions/payments/history"""

    @pytest.mark.asyncio
    async def test_requires_authentication(
        self,
        client: AsyncClient,
    ):
        """Should require authentication"""
        response = await client.get("/v1/subscriptions/payments/history")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_empty_history_for_new_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Should return empty payment history for new user"""
        response = await client.get(
            "/v1/subscriptions/payments/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["payments"] == []
        assert data["total_count"] == 0
