"""Email service placeholder for notification delivery.

This module provides a placeholder EmailService that will be implemented
with actual SMTP functionality in future iterations.

Currently returns success without sending actual emails to prevent
import errors and allow testing of the notification system.

Example:
    Send an email notification::

        service = EmailService()
        await service.send_notification_email(
            to_email="user@example.com",
            subject="Alert Triggered",
            body="Your alert has been triggered",
        )
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Placeholder email service for sending notification emails.

    This is a temporary implementation that logs email requests
    but does not send actual emails. Will be replaced with full
    SMTP implementation using SendGrid, AWS SES, or similar.

    Attributes:
        enabled: Whether email sending is enabled (False for placeholder).
    """

    def __init__(self):
        """Initialize the email service placeholder."""
        self.enabled = False
        logger.info(
            "EmailService initialized (placeholder mode - no emails will be sent)"
        )

    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        template_data: Optional[Dict] = None,
    ) -> bool:
        """Send a notification email (placeholder).

        Args:
            to_email: Recipient email address.
            subject: Email subject line.
            body: Plain text email body.
            html_body: HTML version of email body (optional).
            template_data: Data for email template (optional).

        Returns:
            True indicating email was "sent" (logged only).

        Note:
            This is a placeholder implementation. Emails are logged but not sent.
            Replace with actual SMTP implementation when infrastructure is ready.
        """
        logger.info(
            f"[PLACEHOLDER] Email notification: "
            f"to={to_email}, subject='{subject}', "
            f"body_length={len(body)}"
        )

        # TODO: Implement actual email sending using SMTP service
        # - Configure SMTP server (SendGrid, AWS SES, etc.)
        # - Load email templates
        # - Handle delivery failures and retries
        # - Track delivery status

        return True

    async def send_alert_email(
        self,
        to_email: str,
        alert_type: str,
        stock_symbol: str,
        condition_value: float,
        current_value: float,
    ) -> bool:
        """Send an alert notification email (placeholder).

        Args:
            to_email: Recipient email address.
            alert_type: Type of alert (PRICE_ABOVE, PRICE_BELOW, etc.).
            stock_symbol: Stock symbol that triggered the alert.
            condition_value: The alert threshold value.
            current_value: The current stock value.

        Returns:
            True indicating email was "sent" (logged only).
        """
        subject = f"Stock Alert: {stock_symbol} - {alert_type}"
        body = f"""
Stock Alert Triggered

Symbol: {stock_symbol}
Alert Type: {alert_type}
Condition: {condition_value}
Current Value: {current_value}

This is a placeholder email. Configure SMTP to receive actual notifications.
        """.strip()

        return await self.send_notification_email(
            to_email=to_email,
            subject=subject,
            body=body,
        )
