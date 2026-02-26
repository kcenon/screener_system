"""Webhook endpoints for handling external service callbacks"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated

from app.core.exceptions import BadRequestException
from app.db.models import (Payment, PaymentStatus, SubscriptionPlan, User,
                           UserSubscription)
from app.db.session import get_db
from app.schemas import StripeWebhookResponse
from app.services import StripeService
from app.services.email_service import EmailService
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/stripe",
    response_model=StripeWebhookResponse,
    summary="Stripe webhook endpoint",
    description="Handle Stripe webhook events for payment processing",
)
async def stripe_webhook(
    request: Request,
    stripe_signature: Annotated[str, Header(alias="Stripe-Signature")],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StripeWebhookResponse:
    """
    Handle Stripe webhook events.

    This endpoint receives webhook events from Stripe for payment processing.
    Events are verified using the webhook signature to ensure authenticity.
    """
    stripe_service = StripeService(db)

    # Get raw payload
    payload = await request.body()

    # Verify signature and construct event
    try:
        event = stripe_service.verify_webhook_signature(payload, stripe_signature)
    except BadRequestException as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        ) from e

    event_id = event.get("id")
    event_type = event.get("type")

    logger.info(f"Received Stripe webhook: {event_type} (ID: {event_id})")

    # Check for duplicate event (idempotency)
    if await stripe_service.is_event_processed(event_id):
        logger.info(f"Event {event_id} already processed, skipping")
        return StripeWebhookResponse(
            received=True,
            event_id=event_id,
            event_type=event_type,
            processed=True,
        )

    # Store event for idempotency
    webhook_event = await stripe_service.store_webhook_event(
        event_id=event_id,
        event_type=event_type,
        payload=event,
    )

    try:
        # Process event based on type
        await _process_webhook_event(db, event, event_type)

        # Mark event as processed
        webhook_event.mark_as_processed()
        await db.commit()

        return StripeWebhookResponse(
            received=True,
            event_id=event_id,
            event_type=event_type,
            processed=True,
        )

    except Exception as e:
        logger.error(f"Error processing webhook {event_id}: {e}")
        webhook_event.mark_as_failed(str(e))
        await db.commit()

        return StripeWebhookResponse(
            received=True,
            event_id=event_id,
            event_type=event_type,
            processed=False,
            error=str(e),
        )


async def _process_webhook_event(
    db: AsyncSession,
    event: dict,
    event_type: str,
) -> None:
    """Process webhook event based on type"""
    data = event.get("data", {})
    obj = data.get("object", {})

    # Invoice events
    if event_type == "invoice.paid":
        await _handle_invoice_paid(db, obj)
    elif event_type == "invoice.payment_failed":
        await _handle_invoice_payment_failed(db, obj)
    elif event_type == "invoice.upcoming":
        await _handle_invoice_upcoming(db, obj)

    # Subscription events
    elif event_type == "customer.subscription.created":
        await _handle_subscription_created(db, obj)
    elif event_type == "customer.subscription.updated":
        await _handle_subscription_updated(db, obj)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(db, obj)
    elif event_type == "customer.subscription.trial_will_end":
        await _handle_trial_will_end(db, obj)

    # Payment intent events
    elif event_type == "payment_intent.succeeded":
        await _handle_payment_intent_succeeded(db, obj)
    elif event_type == "payment_intent.payment_failed":
        await _handle_payment_intent_failed(db, obj)

    # Customer events
    elif event_type == "customer.created":
        await _handle_customer_created(db, obj)
    elif event_type == "customer.updated":
        await _handle_customer_updated(db, obj)

    # Checkout session events
    elif event_type == "checkout.session.completed":
        await _handle_checkout_session_completed(db, obj)

    else:
        logger.info(f"Unhandled event type: {event_type}")


# =============================================================================
# INVOICE EVENT HANDLERS
# =============================================================================


async def _handle_invoice_paid(db: AsyncSession, invoice: dict) -> None:
    """Handle successful invoice payment"""
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")
    amount_paid = invoice.get("amount_paid", 0) / 100  # Convert from cents
    invoice_id = invoice.get("id")

    logger.info(f"Invoice paid: {invoice_id} for customer {customer_id}")

    # Find user by Stripe customer ID
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found for customer {customer_id}")
        return

    # Find subscription
    if subscription_id:
        result = await db.execute(
            select(UserSubscription).where(
                UserSubscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            # Update subscription status
            subscription.status = "active"
            await db.flush()

    # Create payment record
    payment = Payment(
        user_id=user.id,
        amount=Decimal(str(amount_paid)),
        currency=invoice.get("currency", "usd").upper(),
        status=PaymentStatus.SUCCEEDED.value,
        payment_type="subscription",
        stripe_invoice_id=invoice_id,
        paid_at=datetime.now(timezone.utc),
    )
    db.add(payment)
    await db.flush()


async def _handle_invoice_payment_failed(db: AsyncSession, invoice: dict) -> None:
    """Handle failed invoice payment"""
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")
    invoice_id = invoice.get("id")
    amount = invoice.get("amount_due", 0) / 100

    logger.warning(f"Invoice payment failed: {invoice_id} for customer {customer_id}")

    # Find user
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return

    # Update subscription status to past_due
    if subscription_id:
        result = await db.execute(
            select(UserSubscription).where(
                UserSubscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = "past_due"
            await db.flush()

    # Create failed payment record
    payment = Payment(
        user_id=user.id,
        amount=Decimal(str(amount)),
        currency=invoice.get("currency", "usd").upper(),
        status=PaymentStatus.FAILED.value,
        payment_type="subscription",
        stripe_invoice_id=invoice_id,
        failure_code=invoice.get("last_finalization_error", {}).get("code"),
        failure_message=invoice.get("last_finalization_error", {}).get("message"),
    )
    db.add(payment)
    await db.flush()

    # Send payment failure notification
    email_service = EmailService()
    await email_service.send_payment_failure_email(
        to_email=user.email,
        amount=amount,
        currency=invoice.get("currency", "usd").upper(),
        failure_reason=invoice.get("last_finalization_error", {}).get("message"),
    )


async def _handle_invoice_upcoming(db: AsyncSession, invoice: dict) -> None:
    """Handle upcoming invoice notification"""
    customer_id = invoice.get("customer")
    amount = invoice.get("amount_due", 0) / 100
    currency = invoice.get("currency", "usd").upper()

    logger.info(f"Upcoming invoice for customer {customer_id}")

    # Find user
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return

    # Derive due date from next_payment_attempt or period_end
    due_ts = invoice.get("next_payment_attempt") or invoice.get("period_end")
    due_date = (
        datetime.fromtimestamp(due_ts, tz=timezone.utc).strftime("%Y-%m-%d")
        if due_ts
        else "N/A"
    )

    email_service = EmailService()
    await email_service.send_upcoming_invoice_email(
        to_email=user.email,
        amount=amount,
        currency=currency,
        due_date=due_date,
    )


# =============================================================================
# SUBSCRIPTION EVENT HANDLERS
# =============================================================================


async def _handle_subscription_created(db: AsyncSession, subscription: dict) -> None:
    """Handle new subscription created"""
    logger.info(f"Subscription created: {subscription.get('id')}")
    # Most creation logic is handled by our API, this is for subscriptions
    # created directly in Stripe Dashboard or via Checkout


async def _handle_subscription_updated(db: AsyncSession, subscription: dict) -> None:
    """Handle subscription update"""
    stripe_subscription_id = subscription.get("id")
    status = subscription.get("status")

    logger.info(f"Subscription updated: {stripe_subscription_id} to status {status}")

    # Find and update local subscription
    result = await db.execute(
        select(UserSubscription).where(
            UserSubscription.stripe_subscription_id == stripe_subscription_id
        )
    )
    user_subscription = result.scalar_one_or_none()

    if not user_subscription:
        logger.warning(f"Subscription {stripe_subscription_id} not found in database")
        return

    # Map Stripe status to our status
    status_map = {
        "active": "active",
        "trialing": "trial",
        "past_due": "past_due",
        "canceled": "canceled",
        "unpaid": "past_due",
        "incomplete": "incomplete",
        "incomplete_expired": "expired",
    }

    user_subscription.status = status_map.get(status, status)
    user_subscription.current_period_start = datetime.fromtimestamp(
        subscription.get("current_period_start"), tz=timezone.utc
    )
    user_subscription.current_period_end = datetime.fromtimestamp(
        subscription.get("current_period_end"), tz=timezone.utc
    )
    user_subscription.cancel_at_period_end = subscription.get(
        "cancel_at_period_end", False
    )

    if subscription.get("canceled_at"):
        user_subscription.canceled_at = datetime.fromtimestamp(
            subscription.get("canceled_at"), tz=timezone.utc
        )

    await db.flush()

    # Update user's subscription tier
    result = await db.execute(select(User).where(User.id == user_subscription.user_id))
    user = result.scalar_one_or_none()

    if user:
        result = await db.execute(
            select(SubscriptionPlan).where(
                SubscriptionPlan.id == user_subscription.plan_id
            )
        )
        plan = result.scalar_one_or_none()

        if plan:
            if user_subscription.status in ("active", "trial"):
                user.subscription_tier = plan.name.lower()
                user.subscription_expires_at = user_subscription.current_period_end
            elif user_subscription.status in ("canceled", "expired"):
                user.subscription_tier = "free"
                user.subscription_expires_at = None

            await db.flush()


async def _handle_subscription_deleted(db: AsyncSession, subscription: dict) -> None:
    """Handle subscription cancellation/deletion"""
    stripe_subscription_id = subscription.get("id")

    logger.info(f"Subscription deleted: {stripe_subscription_id}")

    result = await db.execute(
        select(UserSubscription).where(
            UserSubscription.stripe_subscription_id == stripe_subscription_id
        )
    )
    user_subscription = result.scalar_one_or_none()

    if user_subscription:
        user_subscription.status = "canceled"
        user_subscription.canceled_at = datetime.now(timezone.utc)
        await db.flush()

        # Reset user to free tier
        result = await db.execute(
            select(User).where(User.id == user_subscription.user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.subscription_tier = "free"
            user.subscription_expires_at = None
            await db.flush()


async def _handle_trial_will_end(db: AsyncSession, subscription: dict) -> None:
    """Handle trial ending soon notification"""
    stripe_subscription_id = subscription.get("id")
    trial_end = subscription.get("trial_end")

    logger.info(f"Trial will end for subscription {stripe_subscription_id}")

    # Find subscription and user
    result = await db.execute(
        select(UserSubscription).where(
            UserSubscription.stripe_subscription_id == stripe_subscription_id
        )
    )
    user_subscription = result.scalar_one_or_none()

    if not user_subscription:
        return

    result = await db.execute(
        select(User).where(User.id == user_subscription.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return

    # Get plan name
    result = await db.execute(
        select(SubscriptionPlan).where(
            SubscriptionPlan.id == user_subscription.plan_id
        )
    )
    plan = result.scalar_one_or_none()
    plan_name = plan.name if plan else "Premium"

    trial_end_date = (
        datetime.fromtimestamp(trial_end, tz=timezone.utc).strftime("%Y-%m-%d")
        if trial_end
        else "N/A"
    )

    email_service = EmailService()
    await email_service.send_trial_ending_email(
        to_email=user.email,
        trial_end_date=trial_end_date,
        plan_name=plan_name,
    )


# =============================================================================
# PAYMENT INTENT EVENT HANDLERS
# =============================================================================


async def _handle_payment_intent_succeeded(
    db: AsyncSession, payment_intent: dict
) -> None:
    """Handle successful payment"""
    payment_intent_id = payment_intent.get("id")
    # customer_id = payment_intent.get("customer")
    # amount = payment_intent.get("amount", 0) / 100

    logger.info(f"Payment intent succeeded: {payment_intent_id}")

    # Update existing payment record if exists
    result = await db.execute(
        select(Payment).where(Payment.stripe_payment_intent_id == payment_intent_id)
    )
    payment = result.scalar_one_or_none()

    if payment:
        payment.status = PaymentStatus.SUCCEEDED.value
        payment.paid_at = datetime.now(timezone.utc)
        await db.flush()


async def _handle_payment_intent_failed(db: AsyncSession, payment_intent: dict) -> None:
    """Handle failed payment"""
    payment_intent_id = payment_intent.get("id")
    error = payment_intent.get("last_payment_error", {})

    logger.warning(f"Payment intent failed: {payment_intent_id}")

    # Update existing payment record if exists
    result = await db.execute(
        select(Payment).where(Payment.stripe_payment_intent_id == payment_intent_id)
    )
    payment = result.scalar_one_or_none()

    if payment:
        payment.status = PaymentStatus.FAILED.value
        payment.failure_code = error.get("code")
        payment.failure_message = error.get("message")
        await db.flush()


# =============================================================================
# CUSTOMER EVENT HANDLERS
# =============================================================================


async def _handle_customer_created(db: AsyncSession, customer: dict) -> None:
    """Handle customer created in Stripe"""
    # Usually handled by our API, but log for monitoring
    logger.info(f"Customer created: {customer.get('id')}")


async def _handle_customer_updated(db: AsyncSession, customer: dict) -> None:
    """Handle customer updated in Stripe"""
    customer_id = customer.get("id")
    email = customer.get("email")

    logger.info(f"Customer updated: {customer_id}")

    # Sync email if changed
    if email:
        result = await db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()

        if user and user.email != email:
            # Note: We don't auto-update email as it might be intentionally different
            logger.info(
                f"Customer {customer_id} email differs from user: "
                f"Stripe={email}, User={user.email}"
            )


# =============================================================================
# CHECKOUT SESSION EVENT HANDLERS
# =============================================================================


async def _handle_checkout_session_completed(db: AsyncSession, session: dict) -> None:
    """Handle completed checkout session"""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    mode = session.get("mode")

    logger.info(f"Checkout session completed: {session.get('id')}")

    if mode != "subscription":
        return

    # Find user
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Try to find by metadata
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        if user_id:
            result = await db.execute(select(User).where(User.id == int(user_id)))
            user = result.scalar_one_or_none()

    if not user:
        logger.warning("User not found for checkout session")
        return

    # Update user's Stripe customer ID if not set
    if not user.stripe_customer_id:
        user.stripe_customer_id = customer_id
        await db.flush()

    # Check if subscription already exists
    result = await db.execute(
        select(UserSubscription).where(
            UserSubscription.stripe_subscription_id == subscription_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        logger.info(f"Subscription {subscription_id} already exists")
        return

    # The subscription details will be synced via subscription.created webhook
    logger.info("Checkout completed, waiting for subscription.created webhook")
