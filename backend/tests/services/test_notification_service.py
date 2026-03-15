"""Unit tests for NotificationService"""

from datetime import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models import Notification, NotificationPreference
from app.schemas.websocket import MessageType, NotificationMessage
from app.services.notification_service import NotificationService


def _make_notification(
    notification_id: int = 1,
    user_id: int = 42,
    notification_type: str = "ALERT",
    title: str = "Test Alert",
    message: str = "Test message",
    priority: str = "NORMAL",
) -> MagicMock:
    n = MagicMock(spec=Notification)
    n.id = notification_id
    n.user_id = user_id
    n.notification_type = notification_type
    n.title = title
    n.message = message
    n.priority = priority
    n.user = MagicMock(email="user@example.com")
    return n


def _make_preferences(
    in_app_enabled: bool = True,
    email_enabled: bool = True,
    push_enabled: bool = False,
    is_quiet: bool = False,
    quiet_hours_delay: int = 3600,
) -> MagicMock:
    prefs = MagicMock(spec=NotificationPreference)
    prefs.is_in_quiet_hours.return_value = is_quiet
    prefs.seconds_until_quiet_hours_end.return_value = quiet_hours_delay
    prefs.should_send_in_app.return_value = in_app_enabled
    prefs.should_send_email.return_value = email_enabled
    prefs.should_send_push.return_value = push_enabled
    return prefs


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def email_service():
    svc = AsyncMock()
    svc.send_notification_email = AsyncMock(return_value=True)
    return svc


@pytest.fixture
def service(session, email_service):
    return NotificationService(session=session, email_service=email_service)


class TestSendInAppNotification:
    """Tests for WebSocket integration in _send_in_app_notification."""

    @pytest.mark.asyncio
    async def test_sends_websocket_message(self, service):
        notification = _make_notification()
        mock_cm = MagicMock()
        mock_cm.send_personal_message = AsyncMock()

        with patch("app.core.websocket.connection_manager", mock_cm):
            result = await service._send_in_app_notification(notification)

        assert result is True
        mock_cm.send_personal_message.assert_awaited_once()
        call_args = mock_cm.send_personal_message.call_args
        ws_msg, user_id_str = call_args[0]
        assert isinstance(ws_msg, NotificationMessage)
        assert ws_msg.type == MessageType.NOTIFICATION
        assert ws_msg.notification_id == notification.id
        assert ws_msg.title == notification.title
        assert ws_msg.message == notification.message
        assert user_id_str == str(notification.user_id)

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self, service):
        notification = _make_notification()
        mock_cm = MagicMock()
        mock_cm.send_personal_message = AsyncMock(
            side_effect=RuntimeError("WebSocket error")
        )

        with patch("app.core.websocket.connection_manager", mock_cm):
            result = await service._send_in_app_notification(notification)

        assert result is False


class TestQuietHoursQueuing:
    """Tests for quiet hours deferral in send_notification."""

    @pytest.mark.asyncio
    async def test_schedules_task_during_quiet_hours(self, service, session):
        notification = _make_notification()
        preferences = _make_preferences(is_quiet=True, quiet_hours_delay=1800)

        session.execute = AsyncMock(
            side_effect=[
                _scalar_result(notification),
                _scalar_result(preferences),
            ]
        )

        with patch("asyncio.create_task") as mock_create_task:
            result = await service.send_notification(1, 1)

        assert result is False
        mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_quiet_hours_when_flag_set(self, service, session):
        notification = _make_notification()
        preferences = _make_preferences(is_quiet=True)

        session.execute = AsyncMock(
            side_effect=[
                _scalar_result(notification),
                _scalar_result(preferences),
            ]
        )

        mock_cm = MagicMock()
        mock_cm.send_personal_message = AsyncMock()

        with patch("app.core.websocket.connection_manager", mock_cm):
            result = await service.send_notification(1, 1, skip_quiet_hours=True)

        assert result is True
        preferences.is_in_quiet_hours.assert_not_called()


class TestSecondsUntilQuietHoursEnd:
    """Tests for NotificationPreference.seconds_until_quiet_hours_end."""

    def test_returns_zero_when_no_quiet_hours(self):
        pref = NotificationPreference()
        pref.quiet_hours_start = None
        pref.quiet_hours_end = None
        assert pref.seconds_until_quiet_hours_end() == 0

    def test_returns_zero_when_not_in_quiet_hours(self):
        pref = NotificationPreference()
        # Set quiet hours to far future (won't be in quiet hours during test)
        pref.quiet_hours_start = time(3, 0)
        pref.quiet_hours_end = time(4, 0)
        with patch.object(pref, "is_in_quiet_hours", return_value=False):
            assert pref.seconds_until_quiet_hours_end() == 0

    def test_returns_positive_when_in_quiet_hours(self):
        pref = NotificationPreference()
        pref.quiet_hours_start = time(0, 0)
        pref.quiet_hours_end = time(23, 59)
        with patch.object(pref, "is_in_quiet_hours", return_value=True):
            result = pref.seconds_until_quiet_hours_end()
        assert result > 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scalar_result(value):
    """Return a mock that mimics SQLAlchemy scalar_one_or_none()."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result
