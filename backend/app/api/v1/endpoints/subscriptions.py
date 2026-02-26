"""Subscription management endpoints"""

# from decimal import Decimal  # Unused
# from typing import Annotated, List  # Unused
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import CurrentActiveUser, get_subscription_service
from app.core.exceptions import BadRequestException, NotFoundException
from app.schemas import (AddPaymentMethodRequest, BillingPortalSessionResponse,
                         CancelSubscriptionRequest, CheckoutSessionResponse,
                         CreateBillingPortalSessionRequest,
                         CreateCheckoutSessionRequest, FeatureAccessCheck,
                         FeatureAccessListResponse, PaymentHistoryResponse,
                         PaymentMethodResponse, PaymentMethodsListResponse,
                         PaymentResponse, RetryPaymentRequest,
                         SubscribeRequest, SubscriptionActionResponse,
                         SubscriptionPlanResponse,
                         SubscriptionPlansListResponse, SubscriptionResponse,
                         UpgradeSubscriptionRequest, UsageLimitCheck,
                         UsageStatsResponse)
from app.services import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# =============================================================================
# SUBSCRIPTION PLANS
# =============================================================================


@router.get(
    "/plans",
    response_model=SubscriptionPlansListResponse,
    summary="List subscription plans",
    description="Get all available subscription plans with pricing and features",
)
async def list_plans(
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> SubscriptionPlansListResponse:
    """Get all available subscription plans"""
    plans = await subscription_service.get_all_plans()

    plan_responses = []
    for plan in plans:
        plan_responses.append(
            SubscriptionPlanResponse(
                id=plan.id,
                name=plan.name,
                display_name=plan.display_name,
                description=plan.description,
                price_monthly=plan.price_monthly,
                price_yearly=plan.price_yearly,
                yearly_discount_percent=plan.yearly_discount_percent,
                features=plan.get_all_features(),
                limits=plan.get_all_limits(),
                is_active=plan.is_active,
            )
        )

    return SubscriptionPlansListResponse(
        plans=plan_responses,
        recommended_plan="PREMIUM",  # Can be dynamically determined
    )


# =============================================================================
# CURRENT SUBSCRIPTION
# =============================================================================


@router.get(
    "/current",
    response_model=SubscriptionResponse,
    summary="Get current subscription",
    description="Get the current user's subscription details",
)
async def get_current_subscription(
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> SubscriptionResponse:
    """Get current user's subscription"""
    subscription = await subscription_service.get_user_subscription(current_user.id)
    plan = await subscription_service.get_user_plan(current_user.id)

    if subscription:
        return SubscriptionResponse(
            id=subscription.id,
            plan_name=plan.name,
            plan_display_name=plan.display_name,
            status=subscription.status,
            billing_cycle=subscription.billing_cycle,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            canceled_at=subscription.canceled_at,
            trial_end=subscription.trial_end,
            days_until_renewal=subscription.days_until_renewal,
            trial_days_remaining=subscription.trial_days_remaining,
            price_monthly=plan.price_monthly,
            price_yearly=plan.price_yearly,
            features=plan.get_all_features(),
            limits=plan.get_all_limits(),
            created_at=subscription.created_at,
        )

    # Return free plan info for users without subscription
    from datetime import datetime, timezone

    return SubscriptionResponse(
        id=0,
        plan_name=plan.name,
        plan_display_name=plan.display_name,
        status="active",
        billing_cycle="monthly",
        current_period_start=datetime.now(timezone.utc),
        current_period_end=datetime.now(timezone.utc),
        cancel_at_period_end=False,
        canceled_at=None,
        trial_end=None,
        days_until_renewal=0,
        trial_days_remaining=None,
        price_monthly=plan.price_monthly,
        price_yearly=plan.price_yearly,
        features=plan.get_all_features(),
        limits=plan.get_all_limits(),
        created_at=current_user.created_at,
    )


@router.post(
    "/subscribe",
    response_model=SubscriptionActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subscribe to a plan",
    description="Subscribe to a paid plan (Premium or Pro)",
)
async def subscribe(
    request: SubscribeRequest,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> SubscriptionActionResponse:
    """Subscribe to a plan"""
    try:
        subscription, client_secret = await subscription_service.subscribe(
            user=current_user,
            plan_name=request.plan_name,
            billing_cycle=request.billing_cycle.value,
            payment_method_id=request.payment_method_id,
        )

        plan = await subscription_service.get_plan_by_id(subscription.plan_id)

        return SubscriptionActionResponse(
            success=True,
            message="Subscription created successfully"
            + (". Please complete payment." if client_secret else ""),
            subscription=SubscriptionResponse(
                id=subscription.id,
                plan_name=plan.name,
                plan_display_name=plan.display_name,
                status=subscription.status,
                billing_cycle=subscription.billing_cycle,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end,
                canceled_at=subscription.canceled_at,
                trial_end=subscription.trial_end,
                days_until_renewal=subscription.days_until_renewal,
                trial_days_remaining=subscription.trial_days_remaining,
                price_monthly=plan.price_monthly,
                price_yearly=plan.price_yearly,
                features=plan.get_all_features(),
                limits=plan.get_all_limits(),
                created_at=subscription.created_at,
            ),
        )

    except (BadRequestException, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/cancel",
    response_model=SubscriptionActionResponse,
    summary="Cancel subscription",
    description="Cancel current subscription (immediately or at period end)",
)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> SubscriptionActionResponse:
    """Cancel subscription"""
    try:
        subscription = await subscription_service.cancel_subscription(
            user=current_user,
            immediate=request.immediate,
            reason=request.reason,
        )

        plan = await subscription_service.get_plan_by_id(subscription.plan_id)

        message = (
            "Subscription canceled immediately"
            if request.immediate
            else (
                f"Subscription will be canceled at the end of the billing period "
                f"({subscription.current_period_end.date()})"
            )
        )

        return SubscriptionActionResponse(
            success=True,
            message=message,
            subscription=SubscriptionResponse(
                id=subscription.id,
                plan_name=plan.name,
                plan_display_name=plan.display_name,
                status=subscription.status,
                billing_cycle=subscription.billing_cycle,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end,
                canceled_at=subscription.canceled_at,
                trial_end=subscription.trial_end,
                days_until_renewal=subscription.days_until_renewal,
                trial_days_remaining=subscription.trial_days_remaining,
                price_monthly=plan.price_monthly,
                price_yearly=plan.price_yearly,
                features=plan.get_all_features(),
                limits=plan.get_all_limits(),
                created_at=subscription.created_at,
            ),
        )

    except (BadRequestException, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/upgrade",
    response_model=SubscriptionActionResponse,
    summary="Upgrade/downgrade subscription",
    description="Change to a different subscription plan",
)
async def upgrade_subscription(
    request: UpgradeSubscriptionRequest,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> SubscriptionActionResponse:
    """Upgrade or downgrade subscription"""
    try:
        subscription = await subscription_service.upgrade_subscription(
            user=current_user,
            new_plan_name=request.new_plan_name,
            prorate=request.prorate,
        )

        plan = await subscription_service.get_plan_by_id(subscription.plan_id)

        return SubscriptionActionResponse(
            success=True,
            message=f"Subscription changed to {plan.display_name}",
            subscription=SubscriptionResponse(
                id=subscription.id,
                plan_name=plan.name,
                plan_display_name=plan.display_name,
                status=subscription.status,
                billing_cycle=subscription.billing_cycle,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end,
                canceled_at=subscription.canceled_at,
                trial_end=subscription.trial_end,
                days_until_renewal=subscription.days_until_renewal,
                trial_days_remaining=subscription.trial_days_remaining,
                price_monthly=plan.price_monthly,
                price_yearly=plan.price_yearly,
                features=plan.get_all_features(),
                limits=plan.get_all_limits(),
                created_at=subscription.created_at,
            ),
        )

    except (BadRequestException, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# =============================================================================
# USAGE & LIMITS
# =============================================================================


@router.get(
    "/usage",
    response_model=UsageStatsResponse,
    summary="Get usage statistics",
    description="Get current usage statistics and limits",
)
async def get_usage_stats(
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> UsageStatsResponse:
    """Get usage statistics"""
    stats = await subscription_service.get_usage_stats(current_user.id)

    return UsageStatsResponse(
        user_id=stats["user_id"],
        plan_name=stats["plan_name"],
        period_start=stats["period_start"],
        period_end=stats["period_end"],
        usage=[
            UsageLimitCheck(
                resource_type=u["resource_type"],
                current_usage=u["current_usage"],
                limit_value=u["limit_value"],
                has_access=u["has_access"],
                remaining=u["remaining"],
            )
            for u in stats["usage"]
        ],
        total_searches_today=stats["total_searches_today"],
        total_api_calls_today=stats["total_api_calls_today"],
    )


@router.get(
    "/features",
    response_model=FeatureAccessListResponse,
    summary="Get feature access",
    description="Get all feature access for current plan",
)
async def get_feature_access(
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> FeatureAccessListResponse:
    """Get all feature access"""
    access = await subscription_service.get_feature_access_list(current_user.id)
    return FeatureAccessListResponse(
        plan_name=access["plan_name"],
        features=access["features"],
        limits=access["limits"],
    )


@router.get(
    "/features/{feature_name}",
    response_model=FeatureAccessCheck,
    summary="Check feature access",
    description="Check if user has access to a specific feature",
)
async def check_feature_access(
    feature_name: str,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> FeatureAccessCheck:
    """Check access to specific feature"""
    result = await subscription_service.check_feature_access(
        current_user.id, feature_name
    )
    return FeatureAccessCheck(
        feature_name=result["feature_name"],
        has_access=result["has_access"],
        required_plan=result.get("required_plan"),
        message=result.get("message"),
    )


# =============================================================================
# PAYMENT METHODS
# =============================================================================


@router.get(
    "/payment-methods",
    response_model=PaymentMethodsListResponse,
    summary="List payment methods",
    description="Get all saved payment methods",
)
async def list_payment_methods(
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> PaymentMethodsListResponse:
    """List payment methods"""
    methods = await subscription_service.get_payment_methods(current_user.id)

    default_id = None
    method_responses = []
    for method in methods:
        if method.is_default:
            default_id = method.id
        method_responses.append(
            PaymentMethodResponse(
                id=method.id,
                stripe_payment_method_id=method.stripe_payment_method_id,
                type=method.type,
                is_default=method.is_default,
                card_brand=method.card_brand,
                card_last4=method.card_last4,
                card_exp_month=method.card_exp_month,
                card_exp_year=method.card_exp_year,
                expiry_string=method.expiry_string,
                is_expired=method.is_expired,
                display_name=method.display_name,
                created_at=method.created_at,
            )
        )

    return PaymentMethodsListResponse(
        payment_methods=method_responses,
        default_payment_method_id=default_id,
    )


@router.post(
    "/payment-methods",
    response_model=PaymentMethodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add payment method",
    description="Add a new payment method",
)
async def add_payment_method(
    request: AddPaymentMethodRequest,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> PaymentMethodResponse:
    """Add a new payment method"""
    try:
        method = await subscription_service.add_payment_method(
            user=current_user,
            payment_method_id=request.payment_method_id,
            set_as_default=request.set_as_default,
        )

        return PaymentMethodResponse(
            id=method.id,
            stripe_payment_method_id=method.stripe_payment_method_id,
            type=method.type,
            is_default=method.is_default,
            card_brand=method.card_brand,
            card_last4=method.card_last4,
            card_exp_month=method.card_exp_month,
            card_exp_year=method.card_exp_year,
            expiry_string=method.expiry_string,
            is_expired=method.is_expired,
            display_name=method.display_name,
            created_at=method.created_at,
        )

    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/payment-methods/{payment_method_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove payment method",
    description="Remove a saved payment method",
)
async def remove_payment_method(
    payment_method_id: int,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> None:
    """Remove a payment method"""
    try:
        await subscription_service.remove_payment_method(
            current_user, payment_method_id
        )
    except (BadRequestException, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# =============================================================================
# PAYMENT HISTORY
# =============================================================================


@router.get(
    "/payments/history",
    response_model=PaymentHistoryResponse,
    summary="Get payment history",
    description="Get payment transaction history",
)
async def get_payment_history(
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
    limit: int = 20,
    offset: int = 0,
) -> PaymentHistoryResponse:
    """Get payment history"""
    payments, total_count, total_amount = (
        await subscription_service.get_payment_history(current_user.id, limit, offset)
    )

    return PaymentHistoryResponse(
        payments=[
            PaymentResponse(
                id=p.id,
                amount=p.amount,
                currency=p.currency,
                status=p.status,
                payment_type=p.payment_type,
                stripe_payment_intent_id=p.stripe_payment_intent_id,
                stripe_invoice_id=p.stripe_invoice_id,
                failure_message=p.failure_message,
                refund_amount=p.refund_amount,
                paid_at=p.paid_at,
                created_at=p.created_at,
            )
            for p in payments
        ],
        total_count=total_count,
        total_amount=total_amount,
    )


@router.post(
    "/payments/retry",
    response_model=PaymentResponse,
    summary="Retry failed payment",
    description="Retry a failed payment with optional new payment method",
)
async def retry_payment(
    request: RetryPaymentRequest,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> PaymentResponse:
    """Retry a failed payment"""
    try:
        payment = await subscription_service.retry_payment(
            user=current_user,
            payment_id=request.payment_id,
            payment_method_id=request.payment_method_id,
        )

        return PaymentResponse(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            payment_type=payment.payment_type,
            stripe_payment_intent_id=payment.stripe_payment_intent_id,
            stripe_invoice_id=payment.stripe_invoice_id,
            failure_message=payment.failure_message,
            refund_amount=payment.refund_amount,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
        )

    except (BadRequestException, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# =============================================================================
# CHECKOUT & BILLING PORTAL
# =============================================================================


@router.post(
    "/checkout/session",
    response_model=CheckoutSessionResponse,
    summary="Create checkout session",
    description="Create a Stripe Checkout session for subscription",
)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> CheckoutSessionResponse:
    """Create Stripe Checkout session"""
    try:
        plan = await subscription_service.get_plan_by_name(request.plan_name)
        if not plan:
            raise NotFoundException(f"Plan '{request.plan_name}' not found")

        result = await subscription_service.stripe_service.create_checkout_session(
            user=current_user,
            plan=plan,
            billing_cycle=request.billing_cycle.value,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )

        return CheckoutSessionResponse(
            session_id=result["session_id"],
            url=result["url"],
        )

    except (BadRequestException, NotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/billing-portal",
    response_model=BillingPortalSessionResponse,
    summary="Create billing portal session",
    description="Create a Stripe Billing Portal session for managing subscription",
)
async def create_billing_portal_session(
    request: CreateBillingPortalSessionRequest,
    current_user: CurrentActiveUser,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
) -> BillingPortalSessionResponse:
    """Create Stripe Billing Portal session"""
    try:
        url = await subscription_service.stripe_service.create_billing_portal_session(
            user=current_user,
            return_url=request.return_url,
        )
        return BillingPortalSessionResponse(url=url)

    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
