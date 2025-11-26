"""Stripe payment service for handling Stripe API interactions"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.db.models import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    StripeWebhookEvent,
    SubscriptionPlan,
    User,
    UserSubscription,
)

logger = logging.getLogger(__name__)


class StripeService:
    """Service for handling Stripe payment operations"""

    def __init__(self, session: AsyncSession):
        """Initialize Stripe service with database session"""
        self.session = session
        stripe.api_key = settings.STRIPE_SECRET_KEY

    # =========================================================================
    # CUSTOMER MANAGEMENT
    # =========================================================================

    async def get_or_create_customer(self, user: User) -> str:
        """
        Get existing Stripe customer or create new one.

        Args:
            user: User to get/create customer for

        Returns:
            Stripe customer ID
        """
        if user.stripe_customer_id:
            return user.stripe_customer_id

        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name,
                metadata={
                    "user_id": str(user.id),
                    "environment": settings.ENVIRONMENT,
                },
            )

            user.stripe_customer_id = customer.id
            await self.session.flush()

            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
            return customer.id

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise BadRequestException(f"Payment service error: {str(e)}")

    async def update_customer(self, user: User) -> None:
        """Update Stripe customer information"""
        if not user.stripe_customer_id:
            return

        try:
            stripe.Customer.modify(
                user.stripe_customer_id,
                email=user.email,
                name=user.name,
            )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update Stripe customer: {e}")

    # =========================================================================
    # PAYMENT METHOD MANAGEMENT
    # =========================================================================

    async def attach_payment_method(
        self,
        user: User,
        payment_method_id: str,
        set_as_default: bool = True,
    ) -> PaymentMethod:
        """
        Attach a payment method to a customer.

        Args:
            user: User to attach payment method to
            payment_method_id: Stripe payment method ID
            set_as_default: Whether to set as default payment method

        Returns:
            Created PaymentMethod model
        """
        customer_id = await self.get_or_create_customer(user)

        try:
            # Attach payment method to customer
            pm = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )

            # Set as default if requested
            if set_as_default:
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={"default_payment_method": payment_method_id},
                )
                # Unset other defaults
                from sqlalchemy import update
                await self.session.execute(
                    update(PaymentMethod)
                    .where(PaymentMethod.user_id == user.id)
                    .values(is_default=False)
                )

            # Create local payment method record
            payment_method = PaymentMethod(
                user_id=user.id,
                stripe_payment_method_id=payment_method_id,
                type=pm.type,
                is_default=set_as_default,
                card_brand=pm.card.brand if pm.card else None,
                card_last4=pm.card.last4 if pm.card else None,
                card_exp_month=pm.card.exp_month if pm.card else None,
                card_exp_year=pm.card.exp_year if pm.card else None,
                billing_name=pm.billing_details.name if pm.billing_details else None,
                billing_email=pm.billing_details.email if pm.billing_details else None,
            )

            self.session.add(payment_method)
            await self.session.flush()
            await self.session.refresh(payment_method)

            logger.info(f"Attached payment method {payment_method_id} for user {user.id}")
            return payment_method

        except stripe.error.StripeError as e:
            logger.error(f"Failed to attach payment method: {e}")
            raise BadRequestException(f"Failed to add payment method: {str(e)}")

    async def detach_payment_method(self, payment_method: PaymentMethod) -> None:
        """Detach a payment method from customer"""
        try:
            stripe.PaymentMethod.detach(payment_method.stripe_payment_method_id)
            await self.session.delete(payment_method)
            await self.session.flush()
            logger.info(f"Detached payment method {payment_method.id}")
        except stripe.error.StripeError as e:
            logger.error(f"Failed to detach payment method: {e}")
            raise BadRequestException(f"Failed to remove payment method: {str(e)}")

    # =========================================================================
    # SUBSCRIPTION MANAGEMENT
    # =========================================================================

    async def create_subscription(
        self,
        user: User,
        plan: SubscriptionPlan,
        billing_cycle: str,
        payment_method_id: Optional[str] = None,
        trial_days: Optional[int] = None,
    ) -> Tuple[UserSubscription, Optional[str]]:
        """
        Create a Stripe subscription.

        Args:
            user: User to create subscription for
            plan: Subscription plan
            billing_cycle: 'monthly' or 'yearly'
            payment_method_id: Payment method to use
            trial_days: Trial period in days

        Returns:
            Tuple of (UserSubscription, client_secret if requires action)
        """
        customer_id = await self.get_or_create_customer(user)

        # Get Stripe price ID
        price_id = self._get_price_id(plan.name, billing_cycle)
        if not price_id:
            raise BadRequestException(f"Price not configured for {plan.name} {billing_cycle}")

        try:
            subscription_params: Dict[str, Any] = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"],
                "metadata": {
                    "user_id": str(user.id),
                    "plan_name": plan.name,
                    "billing_cycle": billing_cycle,
                },
            }

            # Add payment method if provided
            if payment_method_id:
                subscription_params["default_payment_method"] = payment_method_id

            # Add trial if specified
            if trial_days and trial_days > 0:
                subscription_params["trial_period_days"] = trial_days

            subscription = stripe.Subscription.create(**subscription_params)

            # Determine subscription status
            status = "active"
            if subscription.status == "trialing":
                status = "trial"
            elif subscription.status == "incomplete":
                status = "incomplete"

            # Create local subscription record
            user_subscription = UserSubscription(
                user_id=user.id,
                plan_id=plan.id,
                status=status,
                billing_cycle=billing_cycle,
                current_period_start=datetime.fromtimestamp(
                    subscription.current_period_start, tz=timezone.utc
                ),
                current_period_end=datetime.fromtimestamp(
                    subscription.current_period_end, tz=timezone.utc
                ),
                stripe_subscription_id=subscription.id,
                stripe_customer_id=customer_id,
                stripe_price_id=price_id,
            )

            # Set trial dates if applicable
            if subscription.trial_start:
                user_subscription.trial_start = datetime.fromtimestamp(
                    subscription.trial_start, tz=timezone.utc
                )
            if subscription.trial_end:
                user_subscription.trial_end = datetime.fromtimestamp(
                    subscription.trial_end, tz=timezone.utc
                )

            self.session.add(user_subscription)

            # Update user's subscription tier
            user.subscription_tier = plan.name.lower()
            if plan.name != "FREE":
                user.subscription_starts_at = user_subscription.current_period_start
                user.subscription_expires_at = user_subscription.current_period_end

            await self.session.flush()
            await self.session.refresh(user_subscription)

            # Get client secret for incomplete subscriptions
            client_secret = None
            if subscription.status == "incomplete":
                latest_invoice = subscription.latest_invoice
                if latest_invoice and latest_invoice.payment_intent:
                    client_secret = latest_invoice.payment_intent.client_secret

            logger.info(
                f"Created subscription {subscription.id} for user {user.id} "
                f"on plan {plan.name}"
            )

            return user_subscription, client_secret

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            raise BadRequestException(f"Failed to create subscription: {str(e)}")

    async def cancel_subscription(
        self,
        subscription: UserSubscription,
        immediate: bool = False,
    ) -> UserSubscription:
        """
        Cancel a subscription.

        Args:
            subscription: Subscription to cancel
            immediate: If True, cancel immediately. Otherwise, cancel at period end.

        Returns:
            Updated subscription
        """
        if not subscription.stripe_subscription_id:
            subscription.mark_as_canceled(immediate)
            await self.session.flush()
            return subscription

        try:
            if immediate:
                stripe.Subscription.delete(subscription.stripe_subscription_id)
                subscription.status = "canceled"
            else:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True,
                )
                subscription.cancel_at_period_end = True

            subscription.canceled_at = datetime.now(timezone.utc)
            await self.session.flush()

            logger.info(
                f"Canceled subscription {subscription.id} "
                f"(immediate={immediate})"
            )

            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise BadRequestException(f"Failed to cancel subscription: {str(e)}")

    async def update_subscription(
        self,
        subscription: UserSubscription,
        new_plan: SubscriptionPlan,
        prorate: bool = True,
    ) -> UserSubscription:
        """
        Update subscription to a new plan (upgrade/downgrade).

        Args:
            subscription: Current subscription
            new_plan: New plan to switch to
            prorate: Whether to prorate the change

        Returns:
            Updated subscription
        """
        if not subscription.stripe_subscription_id:
            raise BadRequestException("Cannot upgrade free subscription directly")

        new_price_id = self._get_price_id(new_plan.name, subscription.billing_cycle)
        if not new_price_id:
            raise BadRequestException(
                f"Price not configured for {new_plan.name} {subscription.billing_cycle}"
            )

        try:
            # Get current subscription from Stripe
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)

            # Update subscription
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[
                    {
                        "id": stripe_sub["items"]["data"][0].id,
                        "price": new_price_id,
                    }
                ],
                proration_behavior="create_prorations" if prorate else "none",
                metadata={
                    "plan_name": new_plan.name,
                    "previous_plan_id": str(subscription.plan_id),
                },
            )

            subscription.plan_id = new_plan.id
            subscription.stripe_price_id = new_price_id
            await self.session.flush()

            # Update user tier
            from sqlalchemy import select
            result = await self.session.execute(
                select(User).where(User.id == subscription.user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user.subscription_tier = new_plan.name.lower()

            logger.info(
                f"Updated subscription {subscription.id} to plan {new_plan.name}"
            )

            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription: {e}")
            raise BadRequestException(f"Failed to update subscription: {str(e)}")

    # =========================================================================
    # CHECKOUT SESSION
    # =========================================================================

    async def create_checkout_session(
        self,
        user: User,
        plan: SubscriptionPlan,
        billing_cycle: str,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, str]:
        """
        Create a Stripe Checkout session.

        Args:
            user: User creating checkout
            plan: Plan to subscribe to
            billing_cycle: 'monthly' or 'yearly'
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            Dict with session_id and url
        """
        customer_id = await self.get_or_create_customer(user)
        price_id = self._get_price_id(plan.name, billing_cycle)

        if not price_id:
            raise BadRequestException(f"Price not configured for {plan.name} {billing_cycle}")

        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    "metadata": {
                        "user_id": str(user.id),
                        "plan_name": plan.name,
                        "billing_cycle": billing_cycle,
                    },
                },
                metadata={
                    "user_id": str(user.id),
                },
            )

            return {"session_id": session.id, "url": session.url}

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise BadRequestException(f"Failed to create checkout session: {str(e)}")

    async def create_billing_portal_session(
        self,
        user: User,
        return_url: str,
    ) -> str:
        """
        Create a Stripe Billing Portal session.

        Args:
            user: User to create portal for
            return_url: URL to return to after portal

        Returns:
            Portal session URL
        """
        if not user.stripe_customer_id:
            raise BadRequestException("No billing information found")

        try:
            session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=return_url,
            )
            return session.url

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            raise BadRequestException(f"Failed to access billing portal: {str(e)}")

    # =========================================================================
    # PAYMENT OPERATIONS
    # =========================================================================

    async def create_payment_record(
        self,
        user_id: int,
        amount: Decimal,
        subscription_id: Optional[int] = None,
        stripe_payment_intent_id: Optional[str] = None,
        stripe_invoice_id: Optional[str] = None,
    ) -> Payment:
        """Create a payment record"""
        payment = Payment(
            user_id=user_id,
            subscription_id=subscription_id,
            amount=amount,
            stripe_payment_intent_id=stripe_payment_intent_id,
            stripe_invoice_id=stripe_invoice_id,
            status=PaymentStatus.PENDING.value,
        )
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def retry_payment(
        self,
        payment: Payment,
        payment_method_id: Optional[str] = None,
    ) -> Payment:
        """Retry a failed payment"""
        if not payment.stripe_invoice_id:
            raise BadRequestException("Cannot retry this payment")

        try:
            if payment_method_id:
                stripe.Invoice.modify(
                    payment.stripe_invoice_id,
                    default_payment_method=payment_method_id,
                )

            stripe.Invoice.pay(payment.stripe_invoice_id)

            payment.status = PaymentStatus.PROCESSING.value
            await self.session.flush()

            return payment

        except stripe.error.StripeError as e:
            logger.error(f"Failed to retry payment: {e}")
            raise BadRequestException(f"Failed to retry payment: {str(e)}")

    # =========================================================================
    # WEBHOOK EVENT HANDLING
    # =========================================================================

    async def store_webhook_event(
        self,
        event_id: str,
        event_type: str,
        payload: Dict[str, Any],
    ) -> StripeWebhookEvent:
        """Store webhook event for idempotency"""
        event = StripeWebhookEvent(
            stripe_event_id=event_id,
            event_type=event_type,
            payload=payload,
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def is_event_processed(self, event_id: str) -> bool:
        """Check if webhook event has already been processed"""
        from sqlalchemy import select

        result = await self.session.execute(
            select(StripeWebhookEvent).where(
                StripeWebhookEvent.stripe_event_id == event_id
            )
        )
        event = result.scalar_one_or_none()
        return event is not None and event.processed

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature.

        Args:
            payload: Raw request body
            signature: Stripe-Signature header value

        Returns:
            Verified event data

        Raises:
            BadRequestException if signature is invalid
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET,
            )
            return event

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise BadRequestException("Invalid webhook signature")

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_price_id(self, plan_name: str, billing_cycle: str) -> Optional[str]:
        """Get Stripe price ID for plan and billing cycle"""
        price_map = {
            ("PREMIUM", "monthly"): settings.STRIPE_PRICE_PREMIUM_MONTHLY,
            ("PREMIUM", "yearly"): settings.STRIPE_PRICE_PREMIUM_YEARLY,
            ("PRO", "monthly"): settings.STRIPE_PRICE_PRO_MONTHLY,
            ("PRO", "yearly"): settings.STRIPE_PRICE_PRO_YEARLY,
        }
        return price_map.get((plan_name.upper(), billing_cycle.lower()))
