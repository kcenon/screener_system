"""Tests for the push notification service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.push_subscription import PushSubscription
from app.services.push_service import PushService


class TestPushService:
    """Tests for PushService."""

    @pytest_asyncio.fixture
    async def push_service(self, db: AsyncSession) -> PushService:
        return PushService(db)

    @pytest.mark.asyncio
    async def test_subscribe_creates_new_subscription(
        self, push_service: PushService, test_user, db: AsyncSession
    ):
        """Test creating a new push subscription."""
        sub = await push_service.subscribe(
            user_id=test_user.id,
            endpoint="https://push.example.com/sub/abc123",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
            user_agent="TestBrowser/1.0",
        )

        assert sub.id is not None
        assert sub.user_id == test_user.id
        assert sub.endpoint == "https://push.example.com/sub/abc123"
        assert sub.p256dh_key == "test-p256dh-key"
        assert sub.auth_key == "test-auth-key"
        assert sub.user_agent == "TestBrowser/1.0"

    @pytest.mark.asyncio
    async def test_subscribe_updates_existing_endpoint(
        self, push_service: PushService, test_user, db: AsyncSession
    ):
        """Test that re-subscribing with same endpoint updates keys."""
        endpoint = "https://push.example.com/sub/existing"

        # First subscription
        sub1 = await push_service.subscribe(
            user_id=test_user.id,
            endpoint=endpoint,
            p256dh_key="old-key",
            auth_key="old-auth",
        )

        # Re-subscribe with new keys
        sub2 = await push_service.subscribe(
            user_id=test_user.id,
            endpoint=endpoint,
            p256dh_key="new-key",
            auth_key="new-auth",
        )

        assert sub2.id == sub1.id
        assert sub2.p256dh_key == "new-key"
        assert sub2.auth_key == "new-auth"

    @pytest.mark.asyncio
    async def test_unsubscribe_removes_subscription(
        self, push_service: PushService, test_user, db: AsyncSession
    ):
        """Test removing a push subscription."""
        endpoint = "https://push.example.com/sub/to-remove"

        await push_service.subscribe(
            user_id=test_user.id,
            endpoint=endpoint,
            p256dh_key="key",
            auth_key="auth",
        )

        removed = await push_service.unsubscribe(test_user.id, endpoint)
        assert removed is True

        # Verify it's gone
        subs = await push_service.get_user_subscriptions(test_user.id)
        assert len(subs) == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_returns_false(
        self, push_service: PushService, test_user
    ):
        """Test unsubscribing a non-existent endpoint returns False."""
        removed = await push_service.unsubscribe(
            test_user.id, "https://push.example.com/nonexistent"
        )
        assert removed is False

    @pytest.mark.asyncio
    async def test_get_user_subscriptions(self, push_service: PushService, test_user):
        """Test retrieving all user subscriptions."""
        for i in range(3):
            await push_service.subscribe(
                user_id=test_user.id,
                endpoint=f"https://push.example.com/sub/{i}",
                p256dh_key=f"key-{i}",
                auth_key=f"auth-{i}",
            )

        subs = await push_service.get_user_subscriptions(test_user.id)
        assert len(subs) == 3

    @pytest.mark.asyncio
    async def test_is_configured_returns_false_without_keys(self):
        """Test is_configured when VAPID keys are not set."""
        with patch("app.services.push_service.settings") as mock_settings:
            mock_settings.VAPID_PRIVATE_KEY = ""
            mock_settings.VAPID_PUBLIC_KEY = ""
            mock_settings.VAPID_CLAIMS_EMAIL = ""
            assert PushService.is_configured() is False

    @pytest.mark.asyncio
    async def test_send_push_skips_when_not_configured(
        self, push_service: PushService, test_user
    ):
        """Test send_push returns 0 when not configured."""
        with patch.object(PushService, "is_configured", return_value=False):
            count = await push_service.send_push(
                user_id=test_user.id,
                title="Test",
                body="Test body",
            )
            assert count == 0

    @pytest.mark.asyncio
    async def test_send_push_delivers_to_subscriptions(
        self, push_service: PushService, test_user
    ):
        """Test send_push delivers to registered subscriptions."""
        await push_service.subscribe(
            user_id=test_user.id,
            endpoint="https://push.example.com/sub/1",
            p256dh_key="key1",
            auth_key="auth1",
        )

        with (
            patch.object(PushService, "is_configured", return_value=True),
            patch("app.services.push_service.webpush") as mock_webpush,
        ):
            count = await push_service.send_push(
                user_id=test_user.id,
                title="Alert",
                body="Stock alert triggered",
            )

            assert count == 1
            mock_webpush.assert_called_once()
