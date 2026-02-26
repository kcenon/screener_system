"""Tests for Stripe webhook email notification integration.

Verifies that webhook handlers call the correct EmailService methods
with the expected arguments when processing Stripe events.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.webhooks import (
    _handle_invoice_payment_failed,
    _handle_invoice_upcoming,
    _handle_trial_will_end,
)


@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    db = AsyncMock(spec=AsyncSession)
    return db


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = MagicMock()
    user.id = 1
    user.email = "user@example.com"
    user.stripe_customer_id = "cus_test123"
    return user


@pytest.fixture
def mock_subscription():
    """Create a mock user subscription."""
    sub = MagicMock()
    sub.user_id = 1
    sub.plan_id = 10
    sub.stripe_subscription_id = "sub_test456"
    sub.status = "trial"
    return sub


@pytest.fixture
def mock_plan():
    """Create a mock subscription plan."""
    plan = MagicMock()
    plan.id = 10
    plan.name = "Pro"
    return plan


class TestWebhookPaymentFailedEmail:
    """Test email sending in _handle_invoice_payment_failed."""

    @pytest.mark.asyncio
    async def test_sends_payment_failure_email(self, mock_db, mock_user):
        """Payment failure sends notification email to user."""
        invoice = {
            "customer": "cus_test123",
            "subscription": "sub_test456",
            "id": "inv_001",
            "amount_due": 2999,
            "currency": "usd",
            "last_finalization_error": {
                "code": "card_declined",
                "message": "Your card was declined",
            },
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [mock_user, None]
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.flush = AsyncMock()

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_payment_failure_email = AsyncMock(return_value=True)
            MockEmailService.return_value = mock_email

            await _handle_invoice_payment_failed(mock_db, invoice)

            mock_email.send_payment_failure_email.assert_called_once_with(
                to_email="user@example.com",
                amount=29.99,
                currency="USD",
                failure_reason="Your card was declined",
            )

    @pytest.mark.asyncio
    async def test_no_email_when_user_not_found(self, mock_db):
        """No email sent when user is not found."""
        invoice = {
            "customer": "cus_unknown",
            "subscription": None,
            "id": "inv_002",
            "amount_due": 999,
            "currency": "usd",
            "last_finalization_error": {},
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_payment_failure_email = AsyncMock()
            MockEmailService.return_value = mock_email

            await _handle_invoice_payment_failed(mock_db, invoice)

            mock_email.send_payment_failure_email.assert_not_called()


class TestWebhookUpcomingInvoiceEmail:
    """Test email sending in _handle_invoice_upcoming."""

    @pytest.mark.asyncio
    async def test_sends_upcoming_invoice_email(self, mock_db, mock_user):
        """Upcoming invoice sends notification email to user."""
        invoice = {
            "customer": "cus_test123",
            "amount_due": 4999,
            "currency": "usd",
            "next_payment_attempt": int(
                datetime(2025, 3, 1, tzinfo=timezone.utc).timestamp()
            ),
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_upcoming_invoice_email = AsyncMock(return_value=True)
            MockEmailService.return_value = mock_email

            await _handle_invoice_upcoming(mock_db, invoice)

            mock_email.send_upcoming_invoice_email.assert_called_once_with(
                to_email="user@example.com",
                amount=49.99,
                currency="USD",
                due_date="2025-03-01",
            )

    @pytest.mark.asyncio
    async def test_falls_back_to_period_end_for_due_date(self, mock_db, mock_user):
        """Uses period_end when next_payment_attempt is missing."""
        invoice = {
            "customer": "cus_test123",
            "amount_due": 1999,
            "currency": "usd",
            "period_end": int(
                datetime(2025, 4, 15, tzinfo=timezone.utc).timestamp()
            ),
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_upcoming_invoice_email = AsyncMock(return_value=True)
            MockEmailService.return_value = mock_email

            await _handle_invoice_upcoming(mock_db, invoice)

            call_kwargs = mock_email.send_upcoming_invoice_email.call_args[1]
            assert call_kwargs["due_date"] == "2025-04-15"
            assert call_kwargs["amount"] == 19.99

    @pytest.mark.asyncio
    async def test_no_email_when_user_not_found(self, mock_db):
        """No email sent when user is not found."""
        invoice = {
            "customer": "cus_unknown",
            "amount_due": 999,
            "currency": "usd",
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_upcoming_invoice_email = AsyncMock()
            MockEmailService.return_value = mock_email

            await _handle_invoice_upcoming(mock_db, invoice)

            mock_email.send_upcoming_invoice_email.assert_not_called()


class TestWebhookTrialEndingEmail:
    """Test email sending in _handle_trial_will_end."""

    @pytest.mark.asyncio
    async def test_sends_trial_ending_email(
        self, mock_db, mock_user, mock_subscription, mock_plan
    ):
        """Trial ending sends notification email with plan name."""
        subscription_data = {
            "id": "sub_test456",
            "trial_end": int(
                datetime(2025, 2, 15, tzinfo=timezone.utc).timestamp()
            ),
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            mock_subscription,
            mock_user,
            mock_plan,
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_trial_ending_email = AsyncMock(return_value=True)
            MockEmailService.return_value = mock_email

            await _handle_trial_will_end(mock_db, subscription_data)

            mock_email.send_trial_ending_email.assert_called_once_with(
                to_email="user@example.com",
                trial_end_date="2025-02-15",
                plan_name="Pro",
            )

    @pytest.mark.asyncio
    async def test_no_email_when_subscription_not_found(self, mock_db):
        """No email sent when subscription is not found."""
        subscription_data = {
            "id": "sub_unknown",
            "trial_end": 1739577600,
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_trial_ending_email = AsyncMock()
            MockEmailService.return_value = mock_email

            await _handle_trial_will_end(mock_db, subscription_data)

            mock_email.send_trial_ending_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_email_when_user_not_found(
        self, mock_db, mock_subscription
    ):
        """No email sent when user is not found for subscription."""
        subscription_data = {
            "id": "sub_test456",
            "trial_end": 1739577600,
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            mock_subscription,
            None,  # User not found
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_trial_ending_email = AsyncMock()
            MockEmailService.return_value = mock_email

            await _handle_trial_will_end(mock_db, subscription_data)

            mock_email.send_trial_ending_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_uses_default_plan_name_when_plan_not_found(
        self, mock_db, mock_user, mock_subscription
    ):
        """Uses 'Premium' as default plan name when plan is not found."""
        subscription_data = {
            "id": "sub_test456",
            "trial_end": int(
                datetime(2025, 2, 15, tzinfo=timezone.utc).timestamp()
            ),
        }

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            mock_subscription,
            mock_user,
            None,  # Plan not found
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch(
            "app.api.v1.endpoints.webhooks.EmailService"
        ) as MockEmailService:
            mock_email = MagicMock()
            mock_email.send_trial_ending_email = AsyncMock(return_value=True)
            MockEmailService.return_value = mock_email

            await _handle_trial_will_end(mock_db, subscription_data)

            call_kwargs = mock_email.send_trial_ending_email.call_args[1]
            assert call_kwargs["plan_name"] == "Premium"
