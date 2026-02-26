"""Unit tests for email service"""

import smtplib
from email.mime.multipart import MIMEMultipart
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.email_service import EmailService


class TestEmailService:
    """Test EmailService"""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for email service"""
        settings = Mock()
        settings.SMTP_HOST = "smtp.example.com"
        settings.SMTP_PORT = 587
        settings.SMTP_USERNAME = "user@example.com"
        settings.SMTP_PASSWORD = "secret"
        settings.SMTP_USE_TLS = True
        settings.EMAIL_SENDER_ADDRESS = "noreply@example.com"
        settings.EMAIL_SENDER_NAME = "Test Platform"
        settings.EMAIL_ENABLED = True
        settings.FRONTEND_URL = "https://example.com"
        return settings

    @pytest.fixture
    def disabled_settings(self):
        """Create mock settings with email disabled"""
        settings = Mock()
        settings.SMTP_HOST = ""
        settings.SMTP_PORT = 587
        settings.SMTP_USERNAME = ""
        settings.SMTP_PASSWORD = ""
        settings.SMTP_USE_TLS = True
        settings.EMAIL_SENDER_ADDRESS = ""
        settings.EMAIL_SENDER_NAME = "Test Platform"
        settings.EMAIL_ENABLED = False
        settings.FRONTEND_URL = "https://example.com"
        return settings

    @pytest.fixture
    def email_service(self, mock_settings):
        """Create EmailService with mocked settings"""
        with patch("app.core.config.settings", mock_settings):
            service = EmailService()
        return service

    @pytest.fixture
    def disabled_service(self, disabled_settings):
        """Create EmailService with email disabled"""
        with patch("app.core.config.settings", disabled_settings):
            service = EmailService()
        return service

    def test_init_enabled(self, email_service):
        """Test initialization with email enabled"""
        assert email_service.enabled is True
        assert email_service.smtp_host == "smtp.example.com"
        assert email_service.smtp_port == 587
        assert email_service.sender_address == "noreply@example.com"

    def test_init_disabled(self, disabled_service):
        """Test initialization with email disabled"""
        assert disabled_service.enabled is False

    def test_build_message(self, email_service):
        """Test MIME message construction"""
        msg = email_service._build_message(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Plain text body",
            html_body="<p>HTML body</p>",
        )

        assert isinstance(msg, MIMEMultipart)
        assert msg["To"] == "recipient@example.com"
        assert msg["Subject"] == "Test Subject"
        assert "noreply@example.com" in msg["From"]

    def test_build_message_plain_only(self, email_service):
        """Test MIME message with plain text only"""
        msg = email_service._build_message(
            to_email="recipient@example.com",
            subject="Test",
            body="Plain text",
        )

        payloads = msg.get_payload()
        assert len(payloads) == 1
        assert payloads[0].get_content_type() == "text/plain"

    def test_build_message_with_html(self, email_service):
        """Test MIME message with both plain and HTML"""
        msg = email_service._build_message(
            to_email="recipient@example.com",
            subject="Test",
            body="Plain text",
            html_body="<p>HTML</p>",
        )

        payloads = msg.get_payload()
        assert len(payloads) == 2
        assert payloads[0].get_content_type() == "text/plain"
        assert payloads[1].get_content_type() == "text/html"

    @pytest.mark.asyncio
    async def test_send_notification_email_disabled(self, disabled_service):
        """Test that disabled service logs but returns True"""
        result = await disabled_service.send_notification_email(
            to_email="test@example.com",
            subject="Test",
            body="Body",
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_send_notification_email_success(self, email_service):
        """Test successful email sending"""
        with patch.object(email_service, "_send_smtp") as mock_smtp:
            result = await email_service.send_notification_email(
                to_email="test@example.com",
                subject="Test Subject",
                body="Test body",
            )

        assert result is True
        mock_smtp.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_email_failure(self, email_service):
        """Test email sending failure returns False"""
        with patch.object(
            email_service,
            "_send_smtp",
            side_effect=smtplib.SMTPException("Connection failed"),
        ):
            result = await email_service.send_notification_email(
                to_email="test@example.com",
                subject="Test Subject",
                body="Test body",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_send_verification_email(self, email_service):
        """Test verification email sends with correct URL"""
        with patch.object(email_service, "send_notification_email") as mock_send:
            mock_send.return_value = True

            result = await email_service.send_verification_email(
                to_email="user@example.com",
                token="test-token-123",
            )

        assert result is True
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["to_email"] == "user@example.com"
        assert call_kwargs["subject"] == "Verify Your Email Address"
        assert "test-token-123" in call_kwargs["body"]
        assert (
            "https://example.com/auth/verify-email?token=test-token-123"
            in call_kwargs["body"]
        )

    @pytest.mark.asyncio
    async def test_send_password_reset_email(self, email_service):
        """Test password reset email sends with correct URL"""
        with patch.object(email_service, "send_notification_email") as mock_send:
            mock_send.return_value = True

            result = await email_service.send_password_reset_email(
                to_email="user@example.com",
                token="reset-token-456",
            )

        assert result is True
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["to_email"] == "user@example.com"
        assert call_kwargs["subject"] == "Reset Your Password"
        assert "reset-token-456" in call_kwargs["body"]
        assert (
            "https://example.com/auth/reset-password?token=reset-token-456"
            in call_kwargs["body"]
        )

    @pytest.mark.asyncio
    async def test_send_password_changed_email(self, email_service):
        """Test password changed confirmation email"""
        with patch.object(email_service, "send_notification_email") as mock_send:
            mock_send.return_value = True

            result = await email_service.send_password_changed_email(
                to_email="user@example.com",
            )

        assert result is True
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["subject"] == "Your Password Has Been Changed"

    @pytest.mark.asyncio
    async def test_send_alert_email(self, email_service):
        """Test stock alert email"""
        with patch.object(email_service, "send_notification_email") as mock_send:
            mock_send.return_value = True

            result = await email_service.send_alert_email(
                to_email="user@example.com",
                alert_type="PRICE_ABOVE",
                stock_symbol="AAPL",
                condition_value=150.0,
                current_value=155.0,
            )

        assert result is True
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert "AAPL" in call_kwargs["subject"]
        assert "PRICE_ABOVE" in call_kwargs["subject"]

    def test_send_smtp_with_tls(self, email_service):
        """Test SMTP sending with TLS"""
        mock_msg = MagicMock(spec=MIMEMultipart)
        mock_msg.as_string.return_value = "email content"

        with patch("app.services.email_service.smtplib.SMTP") as mock_smtp_class:
            mock_server = MagicMock()
            mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_server)
            mock_smtp_class.return_value.__exit__ = Mock(return_value=False)

            email_service._send_smtp(mock_msg, "test@example.com")

            mock_server.ehlo.assert_called()
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("user@example.com", "secret")
            mock_server.sendmail.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_alert_email_with_html_template(self, email_service):
        """Test stock alert email renders HTML template with correct context"""
        with (
            patch.object(
                email_service, "_render_template", return_value="<html>rendered</html>"
            ) as mock_render,
            patch.object(email_service, "send_notification_email") as mock_send,
        ):
            mock_send.return_value = True

            result = await email_service.send_alert_email(
                to_email="user@example.com",
                alert_type="PRICE_ABOVE",
                stock_symbol="AAPL",
                condition_value=150.0,
                current_value=155.0,
            )

        assert result is True
        mock_render.assert_called_once()
        template_name, ctx = mock_render.call_args[0]
        assert template_name == "price_alert.html"
        assert ctx["stock_symbol"] == "AAPL"
        assert ctx["alert_type"] == "PRICE_ABOVE"
        assert ctx["condition_value"] == 150.0
        assert ctx["current_value"] == 155.0
        assert "dashboard_url" in ctx

        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["html_body"] == "<html>rendered</html>"

    @pytest.mark.asyncio
    async def test_send_payment_failure_email(self, email_service):
        """Test payment failure email with amount, currency, and template context"""
        with (
            patch.object(
                email_service, "_render_template", return_value="<html>pf</html>"
            ) as mock_render,
            patch.object(email_service, "send_notification_email") as mock_send,
        ):
            mock_send.return_value = True

            result = await email_service.send_payment_failure_email(
                to_email="user@example.com",
                amount=29.99,
                currency="USD",
                failure_reason="Card declined",
            )

        assert result is True
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["subject"] == "Payment Failed - Action Required"
        assert "29.99" in call_kwargs["body"]
        assert "Card declined" in call_kwargs["body"]

        mock_render.assert_called_once()
        template_name, ctx = mock_render.call_args[0]
        assert template_name == "payment_failure.html"
        assert ctx["amount"] == "29.99"
        assert ctx["currency"] == "USD"
        assert ctx["failure_reason"] == "Card declined"
        assert "billing_url" in ctx

    @pytest.mark.asyncio
    async def test_send_payment_failure_email_no_reason(self, email_service):
        """Test payment failure email without failure reason"""
        with patch.object(email_service, "send_notification_email") as mock_send:
            mock_send.return_value = True

            result = await email_service.send_payment_failure_email(
                to_email="user@example.com",
                amount=9.99,
                currency="USD",
            )

        assert result is True
        call_kwargs = mock_send.call_args[1]
        assert "9.99" in call_kwargs["body"]
        assert "Reason" not in call_kwargs["body"]

    @pytest.mark.asyncio
    async def test_send_upcoming_invoice_email(self, email_service):
        """Test upcoming invoice email with amount, due date, and template context"""
        with (
            patch.object(
                email_service, "_render_template", return_value="<html>ui</html>"
            ) as mock_render,
            patch.object(email_service, "send_notification_email") as mock_send,
        ):
            mock_send.return_value = True

            result = await email_service.send_upcoming_invoice_email(
                to_email="user@example.com",
                amount=49.99,
                currency="USD",
                due_date="2025-02-01",
            )

        assert result is True
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["subject"] == "Upcoming Invoice"
        assert "49.99" in call_kwargs["body"]
        assert "2025-02-01" in call_kwargs["body"]

        mock_render.assert_called_once()
        template_name, ctx = mock_render.call_args[0]
        assert template_name == "upcoming_invoice.html"
        assert ctx["amount"] == "49.99"
        assert ctx["currency"] == "USD"
        assert ctx["due_date"] == "2025-02-01"
        assert "billing_url" in ctx

    @pytest.mark.asyncio
    async def test_send_trial_ending_email(self, email_service):
        """Test trial ending email with plan name, date, and template context"""
        with (
            patch.object(
                email_service, "_render_template", return_value="<html>te</html>"
            ) as mock_render,
            patch.object(email_service, "send_notification_email") as mock_send,
        ):
            mock_send.return_value = True

            result = await email_service.send_trial_ending_email(
                to_email="user@example.com",
                trial_end_date="2025-02-15",
                plan_name="Pro",
            )

        assert result is True
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert "Pro" in call_kwargs["subject"]
        assert "2025-02-15" in call_kwargs["body"]
        assert "Pro" in call_kwargs["body"]

        mock_render.assert_called_once()
        template_name, ctx = mock_render.call_args[0]
        assert template_name == "trial_ending.html"
        assert ctx["plan_name"] == "Pro"
        assert ctx["trial_end_date"] == "2025-02-15"
        assert "billing_url" in ctx

    def test_render_template_missing(self, email_service):
        """Test template rendering when template doesn't exist"""
        email_service._jinja_env = None
        result = email_service._render_template("nonexistent.html", {})
        assert result is None
