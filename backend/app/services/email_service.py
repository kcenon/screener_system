"""Email service for sending transactional emails via SMTP.

This module provides an EmailService that sends actual emails through
any SMTP provider (SendGrid, AWS SES, Gmail, etc.) with retry logic
and Jinja2 HTML template support.

Example:
    Send an email notification::

        service = EmailService()
        await service.send_notification_email(
            to_email="user@example.com",
            subject="Alert Triggered",
            body="Your alert has been triggered",
        )
"""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"


class EmailService:
    """Email service for sending transactional emails via SMTP.

    Supports any SMTP provider and uses Jinja2 for HTML email templates.
    Falls back to logging-only mode when SMTP is not configured.

    Attributes:
        enabled: Whether email sending is enabled.
    """

    def __init__(self):
        """Initialize the email service from application settings."""
        from app.core.config import settings

        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.sender_address = settings.EMAIL_SENDER_ADDRESS
        self.sender_name = settings.EMAIL_SENDER_NAME
        self.enabled = settings.EMAIL_ENABLED
        self.frontend_url = settings.FRONTEND_URL

        self._jinja_env: Optional[Environment] = None
        if TEMPLATE_DIR.exists():
            self._jinja_env = Environment(
                loader=FileSystemLoader(str(TEMPLATE_DIR)),
                autoescape=select_autoescape(["html"]),
            )

        if self.enabled:
            logger.info("EmailService initialized (SMTP mode)")
        else:
            logger.info(
                "EmailService initialized (disabled — emails will be logged only)"
            )

    def _render_template(
        self, template_name: str, context: Dict
    ) -> Optional[str]:
        """Render an HTML email template with the given context.

        Args:
            template_name: Template file name (e.g., "email_verification.html").
            context: Template variables.

        Returns:
            Rendered HTML string, or None if template not found.
        """
        if not self._jinja_env:
            return None
        try:
            template = self._jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception:
            logger.warning(f"Failed to render template: {template_name}")
            return None

    def _build_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> MIMEMultipart:
        """Build a MIME email message.

        Args:
            to_email: Recipient email address.
            subject: Email subject line.
            body: Plain text body.
            html_body: HTML body (optional).

        Returns:
            Constructed MIMEMultipart message.
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.sender_address}>"
        msg["To"] = to_email

        msg.attach(MIMEText(body, "plain", "utf-8"))
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        return msg

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((smtplib.SMTPException, OSError)),
        reraise=True,
    )
    def _send_smtp(self, msg: MIMEMultipart, to_email: str) -> None:
        """Send email via SMTP with retry logic.

        Args:
            msg: Constructed MIME message.
            to_email: Recipient email address.

        Raises:
            smtplib.SMTPException: On SMTP delivery failure after retries.
        """
        if self.smtp_use_tls:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if self.smtp_username:
                    server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_address, to_email, msg.as_string())
        else:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                if self.smtp_username:
                    server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_address, to_email, msg.as_string())

    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        template_data: Optional[Dict] = None,
    ) -> bool:
        """Send a notification email.

        Args:
            to_email: Recipient email address.
            subject: Email subject line.
            body: Plain text email body.
            html_body: HTML version of email body (optional).
            template_data: Data for email template (optional).

        Returns:
            True if email was sent successfully.
        """
        if not self.enabled:
            logger.info(
                f"[DISABLED] Email to={to_email}, subject='{subject}', "
                f"body_length={len(body)}"
            )
            return True

        msg = self._build_message(to_email, subject, body, html_body)

        try:
            await asyncio.to_thread(self._send_smtp, msg, to_email)
            logger.info(f"Email sent: to={to_email}, subject='{subject}'")
            return True
        except Exception:
            logger.exception(f"Failed to send email: to={to_email}, subject='{subject}'")
            return False

    async def send_verification_email(
        self,
        to_email: str,
        token: str,
    ) -> bool:
        """Send an email verification email with a verification link.

        Args:
            to_email: Recipient email address.
            token: Verification token.

        Returns:
            True if email was sent successfully.
        """
        verification_url = f"{self.frontend_url}/auth/verify-email?token={token}"

        body = (
            f"Welcome to Stock Screening Platform!\n\n"
            f"Please verify your email address by clicking the link below:\n"
            f"{verification_url}\n\n"
            f"This link expires in 24 hours.\n\n"
            f"If you did not create an account, please ignore this email."
        )

        html_body = self._render_template(
            "email_verification.html",
            {
                "verification_url": verification_url,
                "expire_hours": 24,
            },
        )

        return await self.send_notification_email(
            to_email=to_email,
            subject="Verify Your Email Address",
            body=body,
            html_body=html_body,
        )

    async def send_password_reset_email(
        self,
        to_email: str,
        token: str,
    ) -> bool:
        """Send a password reset email with a reset link.

        Args:
            to_email: Recipient email address.
            token: Password reset token.

        Returns:
            True if email was sent successfully.
        """
        reset_url = f"{self.frontend_url}/auth/reset-password?token={token}"

        body = (
            f"You requested a password reset for your Stock Screening Platform account.\n\n"
            f"Click the link below to reset your password:\n"
            f"{reset_url}\n\n"
            f"This link expires in 1 hour.\n\n"
            f"If you did not request this, please ignore this email."
        )

        html_body = self._render_template(
            "password_reset.html",
            {
                "reset_url": reset_url,
                "expire_hours": 1,
            },
        )

        return await self.send_notification_email(
            to_email=to_email,
            subject="Reset Your Password",
            body=body,
            html_body=html_body,
        )

    async def send_password_changed_email(
        self,
        to_email: str,
    ) -> bool:
        """Send a password changed confirmation email.

        Args:
            to_email: Recipient email address.

        Returns:
            True if email was sent successfully.
        """
        body = (
            "Your password has been changed successfully.\n\n"
            "All active sessions have been logged out for security.\n\n"
            "If you did not make this change, please contact support immediately."
        )

        html_body = self._render_template("password_changed.html", {})

        return await self.send_notification_email(
            to_email=to_email,
            subject="Your Password Has Been Changed",
            body=body,
            html_body=html_body,
        )

    async def send_alert_email(
        self,
        to_email: str,
        alert_type: str,
        stock_symbol: str,
        condition_value: float,
        current_value: float,
    ) -> bool:
        """Send a stock alert notification email.

        Args:
            to_email: Recipient email address.
            alert_type: Type of alert (PRICE_ABOVE, PRICE_BELOW, etc.).
            stock_symbol: Stock symbol that triggered the alert.
            condition_value: The alert threshold value.
            current_value: The current stock value.

        Returns:
            True if email was sent successfully.
        """
        subject = f"Stock Alert: {stock_symbol} - {alert_type}"
        body = (
            f"Stock Alert Triggered\n\n"
            f"Symbol: {stock_symbol}\n"
            f"Alert Type: {alert_type}\n"
            f"Condition: {condition_value}\n"
            f"Current Value: {current_value}"
        )

        return await self.send_notification_email(
            to_email=to_email,
            subject=subject,
            body=body,
        )
