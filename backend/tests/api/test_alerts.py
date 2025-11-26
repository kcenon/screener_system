"""Tests for alert API endpoints.

This module contains comprehensive tests for the alerts API endpoints,
covering CRUD operations, validation, authorization, and edge cases.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import status
from sqlalchemy import select

from app.db.models import Alert, Stock, User


pytestmark = pytest.mark.asyncio


# ============================================================================
# CREATE ALERT TESTS
# ============================================================================


class TestCreateAlert:
    """Tests for POST /v1/alerts"""

    async def test_create_price_above_alert_success(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test successfully creating a PRICE_ABOVE alert."""
        alert_data = {
            "stock_code": test_stock.code,
            "alert_type": "PRICE_ABOVE",
            "condition_value": 50000.00,
            "is_recurring": False,
        }

        response = await client.post(
            "/v1/alerts",
            json=alert_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["stock_code"] == test_stock.code
        assert data["alert_type"] == "PRICE_ABOVE"
        assert data["condition_value"] == 50000.00
        assert data["is_active"] is True
        assert data["is_recurring"] is False
        assert data["triggered_at"] is None
        assert data["user_id"] == test_user.id

    async def test_create_price_below_alert_success(
        self, client, auth_headers, test_user, test_stock
    ):
        """Test successfully creating a PRICE_BELOW alert."""
        alert_data = {
            "stock_code": test_stock.code,
            "alert_type": "PRICE_BELOW",
            "condition_value": 30000.00,
            "is_recurring": True,
        }

        response = await client.post(
            "/v1/alerts",
            json=alert_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["alert_type"] == "PRICE_BELOW"
        assert data["condition_value"] == 30000.00
        assert data["is_recurring"] is True

    async def test_create_volume_spike_alert_success(
        self, client, auth_headers, test_stock
    ):
        """Test successfully creating a VOLUME_SPIKE alert."""
        alert_data = {
            "stock_code": test_stock.code,
            "alert_type": "VOLUME_SPIKE",
            "condition_value": 2.0,  # 2x average volume
            "is_recurring": False,
        }

        response = await client.post(
            "/v1/alerts",
            json=alert_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["alert_type"] == "VOLUME_SPIKE"
        assert data["condition_value"] == 2.0

    async def test_create_change_percent_alert_success(
        self, client, auth_headers, test_stock
    ):
        """Test successfully creating a CHANGE_PERCENT_ABOVE alert."""
        alert_data = {
            "stock_code": test_stock.code,
            "alert_type": "CHANGE_PERCENT_ABOVE",
            "condition_value": 5.0,  # +5% change
            "is_recurring": True,
        }

        response = await client.post(
            "/v1/alerts",
            json=alert_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["alert_type"] == "CHANGE_PERCENT_ABOVE"
        assert data["condition_value"] == 5.0

    async def test_create_alert_unauthorized(self, client, test_stock):
        """Test creating alert without authentication fails."""
        alert_data = {
            "stock_code": test_stock.code,
            "alert_type": "PRICE_ABOVE",
            "condition_value": 50000.00,
        }

        response = await client.post("/v1/alerts", json=alert_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_alert_invalid_stock_code(
        self, client, auth_headers
    ):
        """Test creating alert with non-existent stock code fails."""
        alert_data = {
            "stock_code": "INVALID",
            "alert_type": "PRICE_ABOVE",
            "condition_value": 50000.00,
        }

        response = await client.post(
            "/v1/alerts",
            json=alert_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Stock not found" in response.json()["detail"]

    async def test_create_alert_invalid_alert_type(
        self, client, auth_headers, test_stock
    ):
        """Test creating alert with invalid alert type fails."""
        alert_data = {
            "stock_code": test_stock.code,
            "alert_type": "INVALID_TYPE",
            "condition_value": 50000.00,
        }

        response = await client.post(
            "/v1/alerts",
            json=alert_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_alert_negative_condition_value(
        self, client, auth_headers, test_stock
    ):
        """Test creating alert with negative condition value fails."""
        alert_data = {
            "stock_code": test_stock.code,
            "alert_type": "PRICE_ABOVE",
            "condition_value": -50000.00,
        }

        response = await client.post(
            "/v1/alerts",
            json=alert_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_alert_zero_condition_value(
        self, client, auth_headers, test_stock
    ):
        """Test creating alert with zero condition value fails."""
        alert_data = {
            "stock_code": test_stock.code,
            "alert_type": "PRICE_ABOVE",
            "condition_value": 0,
        }

        response = await client.post(
            "/v1/alerts",
            json=alert_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# LIST ALERTS TESTS
# ============================================================================


class TestListAlerts:
    """Tests for GET /v1/alerts"""

    async def test_list_alerts_empty(self, client, auth_headers):
        """Test listing alerts when user has no alerts."""
        response = await client.get("/v1/alerts", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_alerts_with_data(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test listing alerts with multiple alerts."""
        # Create multiple alerts
        alerts_data = [
            {
                "user_id": test_user.id,
                "stock_code": test_stock.code,
                "alert_type": "PRICE_ABOVE",
                "condition_value": Decimal("50000.00"),
            },
            {
                "user_id": test_user.id,
                "stock_code": test_stock.code,
                "alert_type": "PRICE_BELOW",
                "condition_value": Decimal("30000.00"),
            },
            {
                "user_id": test_user.id,
                "stock_code": test_stock.code,
                "alert_type": "VOLUME_SPIKE",
                "condition_value": Decimal("2.0"),
            },
        ]

        for alert_data in alerts_data:
            alert = Alert(**alert_data)
            db_session.add(alert)
        await db_session.commit()

        response = await client.get("/v1/alerts", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_list_alerts_filter_by_stock_code(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test filtering alerts by stock code."""
        # Create alerts for test_stock
        alert1 = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )
        db_session.add(alert1)

        # Create second stock and alert
        stock2 = Stock(
            code="000660",
            name="하이닉스",
            market="KOSPI",
            sector="반도체",
            industry="반도체",
        )
        db_session.add(stock2)
        await db_session.flush()

        alert2 = Alert(
            user_id=test_user.id,
            stock_code=stock2.code,
            alert_type="PRICE_BELOW",
            condition_value=Decimal("30000.00"),
        )
        db_session.add(alert2)
        await db_session.commit()

        # Filter by first stock
        response = await client.get(
            f"/v1/alerts?stock_code={test_stock.code}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["stock_code"] == test_stock.code

    async def test_list_alerts_filter_by_is_active(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test filtering alerts by is_active status."""
        # Create active and inactive alerts
        active_alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
            is_active=True,
        )
        inactive_alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_BELOW",
            condition_value=Decimal("30000.00"),
            is_active=False,
        )
        db_session.add_all([active_alert, inactive_alert])
        await db_session.commit()

        # Filter by active
        response = await client.get(
            "/v1/alerts?is_active=true", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["is_active"] is True

    async def test_list_alerts_pagination(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test pagination of alerts list."""
        # Create 15 alerts
        for i in range(15):
            alert = Alert(
                user_id=test_user.id,
                stock_code=test_stock.code,
                alert_type="PRICE_ABOVE",
                condition_value=Decimal(f"{40000 + i * 1000}.00"),
            )
            db_session.add(alert)
        await db_session.commit()

        # Get first page
        response = await client.get(
            "/v1/alerts?skip=0&limit=10", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10

        # Get second page
        response = await client.get(
            "/v1/alerts?skip=10&limit=10", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 5

    async def test_list_alerts_unauthorized(self, client):
        """Test listing alerts without authentication fails."""
        response = await client.get("/v1/alerts")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_list_alerts_only_own_alerts(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test that users can only see their own alerts."""
        # Create another user
        other_user = User(
            email="other@example.com",
            name="otheruser",
            password_hash="hashedpassword",
        )
        db_session.add(other_user)
        await db_session.flush()

        # Create alert for test_user
        user_alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )

        # Create alert for other_user
        other_alert = Alert(
            user_id=other_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_BELOW",
            condition_value=Decimal("30000.00"),
        )

        db_session.add_all([user_alert, other_alert])
        await db_session.commit()

        # List alerts as test_user
        response = await client.get("/v1/alerts", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["user_id"] == test_user.id


# ============================================================================
# GET ALERT TESTS
# ============================================================================


class TestGetAlert:
    """Tests for GET /v1/alerts{id}"""

    async def test_get_alert_success(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test successfully getting alert details."""
        alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        response = await client.get(
            f"/v1/alerts{alert.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == alert.id
        assert data["stock_code"] == test_stock.code
        assert data["alert_type"] == "PRICE_ABOVE"

    async def test_get_alert_not_found(self, client, auth_headers):
        """Test getting non-existent alert returns 404."""
        response = await client.get("/v1/alerts99999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_alert_unauthorized(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test getting alert of another user fails."""
        # Create another user
        other_user = User(
            email="other@example.com",
            name="otheruser",
            password_hash="hashedpassword",
        )
        db_session.add(other_user)
        await db_session.flush()

        # Create alert for other_user
        alert = Alert(
            user_id=other_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        # Try to get alert as test_user
        response = await client.get(
            f"/v1/alerts{alert.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# UPDATE ALERT TESTS
# ============================================================================


class TestUpdateAlert:
    """Tests for PUT /v1/alerts{id}"""

    async def test_update_alert_condition_value(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test updating alert condition value."""
        alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        update_data = {"condition_value": 55000.00}

        response = await client.put(
            f"/v1/alerts{alert.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["condition_value"] == 55000.00

    async def test_update_alert_is_recurring(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test updating alert is_recurring status."""
        alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
            is_recurring=False,
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        update_data = {"is_recurring": True}

        response = await client.put(
            f"/v1/alerts{alert.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_recurring"] is True

    async def test_update_alert_not_found(
        self, client, auth_headers
    ):
        """Test updating non-existent alert returns 404."""
        update_data = {"condition_value": 55000.00}

        response = await client.put(
            "/v1/alerts99999",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_alert_unauthorized(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test updating alert of another user fails."""
        # Create another user
        other_user = User(
            email="other@example.com",
            name="otheruser",
            password_hash="hashedpassword",
        )
        db_session.add(other_user)
        await db_session.flush()

        # Create alert for other_user
        alert = Alert(
            user_id=other_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        update_data = {"condition_value": 55000.00}

        # Try to update alert as test_user
        response = await client.put(
            f"/v1/alerts{alert.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# DELETE ALERT TESTS
# ============================================================================


class TestDeleteAlert:
    """Tests for DELETE /v1/alerts{id}"""

    async def test_delete_alert_success(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test successfully deleting an alert."""
        alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)
        alert_id = alert.id

        response = await client.delete(
            f"/v1/alerts{alert_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify alert is deleted
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await db_session.execute(stmt)
        deleted_alert = result.scalar_one_or_none()
        assert deleted_alert is None

    async def test_delete_alert_not_found(self, client, auth_headers):
        """Test deleting non-existent alert returns 404."""
        response = await client.delete(
            "/v1/alerts99999", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_alert_unauthorized(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test deleting alert of another user fails."""
        # Create another user
        other_user = User(
            email="other@example.com",
            name="otheruser",
            password_hash="hashedpassword",
        )
        db_session.add(other_user)
        await db_session.flush()

        # Create alert for other_user
        alert = Alert(
            user_id=other_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        # Try to delete alert as test_user
        response = await client.delete(
            f"/v1/alerts{alert.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# TOGGLE ALERT TESTS
# ============================================================================


class TestToggleAlert:
    """Tests for POST /v1/alerts{id}/toggle"""

    async def test_toggle_alert_deactivate(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test deactivating an active alert."""
        alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
            is_active=True,
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        response = await client.post(
            f"/v1/alerts{alert.id}/toggle", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False

    async def test_toggle_alert_activate(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test activating an inactive alert."""
        alert = Alert(
            user_id=test_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
            is_active=False,
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        response = await client.post(
            f"/v1/alerts{alert.id}/toggle", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is True

    async def test_toggle_alert_not_found(self, client, auth_headers):
        """Test toggling non-existent alert returns 404."""
        response = await client.post(
            "/v1/alerts99999/toggle", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_toggle_alert_unauthorized(
        self, client, auth_headers, test_user, test_stock, db_session
    ):
        """Test toggling alert of another user fails."""
        # Create another user
        other_user = User(
            email="other@example.com",
            name="otheruser",
            password_hash="hashedpassword",
        )
        db_session.add(other_user)
        await db_session.flush()

        # Create alert for other_user
        alert = Alert(
            user_id=other_user.id,
            stock_code=test_stock.code,
            alert_type="PRICE_ABOVE",
            condition_value=Decimal("50000.00"),
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)

        # Try to toggle alert as test_user
        response = await client.post(
            f"/v1/alerts{alert.id}/toggle", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
