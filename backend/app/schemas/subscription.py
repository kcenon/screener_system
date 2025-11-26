"""Subscription Pydantic schemas"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================


class SubscriptionStatusEnum(str, Enum):
    """Subscription status"""

    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    INCOMPLETE = "incomplete"


class BillingCycleEnum(str, Enum):
    """Billing cycle"""

    MONTHLY = "monthly"
    YEARLY = "yearly"


class PaymentStatusEnum(str, Enum):
    """Payment status"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class PaymentMethodTypeEnum(str, Enum):
    """Payment method type"""

    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    SEPA_DEBIT = "sepa_debit"
    IDEAL = "ideal"


class ResourceTypeEnum(str, Enum):
    """Resource type for usage tracking"""

    SCREENING = "screening"
    API_CALL = "api_call"
    ALERT = "alert"
    EXPORT = "export"
    PORTFOLIO = "portfolio"


# =============================================================================
# SUBSCRIPTION PLAN SCHEMAS
# =============================================================================


class SubscriptionPlanBase(BaseModel):
    """Base schema for subscription plan"""

    name: str = Field(..., description="Plan identifier (FREE, PREMIUM, PRO)")
    display_name: str = Field(..., description="Display name for the plan")
    description: Optional[str] = Field(None, description="Plan description")


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Response schema for subscription plan"""

    id: int
    price_monthly: Decimal = Field(..., description="Monthly price")
    price_yearly: Decimal = Field(..., description="Yearly price")
    yearly_discount_percent: float = Field(0.0, description="Discount percentage for yearly billing")
    features: Dict[str, bool] = Field(default_factory=dict, description="Available features")
    limits: Dict[str, int] = Field(default_factory=dict, description="Usage limits")
    is_active: bool = True

    model_config = {"from_attributes": True}


class SubscriptionPlansListResponse(BaseModel):
    """Response schema for listing subscription plans"""

    plans: List[SubscriptionPlanResponse]
    recommended_plan: Optional[str] = Field(None, description="Recommended plan name")


# =============================================================================
# USER SUBSCRIPTION SCHEMAS
# =============================================================================


class SubscribeRequest(BaseModel):
    """Request schema for subscribing to a plan"""

    plan_name: str = Field(..., description="Plan name (PREMIUM or PRO)")
    billing_cycle: BillingCycleEnum = Field(
        BillingCycleEnum.MONTHLY,
        description="Billing cycle",
    )
    payment_method_id: Optional[str] = Field(
        None,
        description="Stripe payment method ID (required for paid plans)",
    )
    promo_code: Optional[str] = Field(None, description="Promotional code")


class SubscriptionResponse(BaseModel):
    """Response schema for user subscription"""

    id: int
    plan_name: str
    plan_display_name: str
    status: SubscriptionStatusEnum
    billing_cycle: BillingCycleEnum
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    canceled_at: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    days_until_renewal: int
    trial_days_remaining: Optional[int] = None
    price_monthly: Decimal
    price_yearly: Decimal
    features: Dict[str, bool] = Field(default_factory=dict)
    limits: Dict[str, int] = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}


class CancelSubscriptionRequest(BaseModel):
    """Request schema for canceling subscription"""

    immediate: bool = Field(
        False,
        description="If true, cancel immediately. Otherwise, cancel at period end.",
    )
    reason: Optional[str] = Field(None, description="Cancellation reason")


class UpgradeSubscriptionRequest(BaseModel):
    """Request schema for upgrading/downgrading subscription"""

    new_plan_name: str = Field(..., description="New plan name")
    prorate: bool = Field(True, description="Whether to prorate the change")


class SubscriptionActionResponse(BaseModel):
    """Response schema for subscription actions"""

    success: bool
    message: str
    subscription: Optional[SubscriptionResponse] = None


# =============================================================================
# PAYMENT SCHEMAS
# =============================================================================


class PaymentResponse(BaseModel):
    """Response schema for payment"""

    id: int
    amount: Decimal
    currency: str
    status: PaymentStatusEnum
    payment_type: str
    stripe_payment_intent_id: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    failure_message: Optional[str] = None
    refund_amount: Optional[Decimal] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentHistoryResponse(BaseModel):
    """Response schema for payment history"""

    payments: List[PaymentResponse]
    total_count: int
    total_amount: Decimal


class RetryPaymentRequest(BaseModel):
    """Request schema for retrying a failed payment"""

    payment_id: int = Field(..., description="Payment ID to retry")
    payment_method_id: Optional[str] = Field(
        None,
        description="New payment method to use (optional)",
    )


# =============================================================================
# PAYMENT METHOD SCHEMAS
# =============================================================================


class AddPaymentMethodRequest(BaseModel):
    """Request schema for adding a payment method"""

    payment_method_id: str = Field(..., description="Stripe payment method ID")
    set_as_default: bool = Field(True, description="Set as default payment method")


class PaymentMethodResponse(BaseModel):
    """Response schema for payment method"""

    id: int
    stripe_payment_method_id: str
    type: PaymentMethodTypeEnum
    is_default: bool
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    expiry_string: Optional[str] = None
    is_expired: bool = False
    display_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentMethodsListResponse(BaseModel):
    """Response schema for listing payment methods"""

    payment_methods: List[PaymentMethodResponse]
    default_payment_method_id: Optional[int] = None


# =============================================================================
# USAGE TRACKING SCHEMAS
# =============================================================================


class UsageLimitCheck(BaseModel):
    """Schema for usage limit check result"""

    resource_type: str
    current_usage: int
    limit_value: int
    has_access: bool
    remaining: int
    reset_at: Optional[datetime] = None


class UsageStatsResponse(BaseModel):
    """Response schema for usage statistics"""

    user_id: int
    plan_name: str
    period_start: datetime
    period_end: datetime
    usage: List[UsageLimitCheck]
    total_searches_today: int = 0
    total_api_calls_today: int = 0


class IncrementUsageRequest(BaseModel):
    """Request schema for incrementing usage (internal use)"""

    resource_type: ResourceTypeEnum
    count: int = Field(1, ge=1)


# =============================================================================
# STRIPE WEBHOOK SCHEMAS
# =============================================================================


class StripeWebhookResponse(BaseModel):
    """Response schema for Stripe webhook processing"""

    received: bool
    event_id: str
    event_type: str
    processed: bool = False
    error: Optional[str] = None


# =============================================================================
# CHECKOUT SCHEMAS
# =============================================================================


class CreateCheckoutSessionRequest(BaseModel):
    """Request schema for creating a Stripe Checkout session"""

    plan_name: str = Field(..., description="Plan name (PREMIUM or PRO)")
    billing_cycle: BillingCycleEnum = Field(
        BillingCycleEnum.MONTHLY,
        description="Billing cycle",
    )
    success_url: str = Field(..., description="URL to redirect after successful checkout")
    cancel_url: str = Field(..., description="URL to redirect after canceled checkout")


class CheckoutSessionResponse(BaseModel):
    """Response schema for checkout session"""

    session_id: str
    url: str


class CreateBillingPortalSessionRequest(BaseModel):
    """Request schema for creating a Stripe Billing Portal session"""

    return_url: str = Field(..., description="URL to return to after portal session")


class BillingPortalSessionResponse(BaseModel):
    """Response schema for billing portal session"""

    url: str


# =============================================================================
# FEATURE ACCESS SCHEMAS
# =============================================================================


class FeatureAccessCheck(BaseModel):
    """Schema for feature access check"""

    feature_name: str
    has_access: bool
    required_plan: Optional[str] = None
    message: Optional[str] = None


class FeatureAccessListResponse(BaseModel):
    """Response schema for listing all feature access"""

    plan_name: str
    features: Dict[str, bool]
    limits: Dict[str, int]
