"""Alert engine service for monitoring and triggering stock alerts.

This module provides the AlertEngine class that continuously monitors active alerts
and triggers notifications when alert conditions are met.

The alert engine runs as a background task and checks all active alerts against
current market data at regular intervals.

Example:
    Run the alert engine as a background task::

        from app.services import AlertEngine
        from app.db import get_session

        async with get_session() as session:
            engine = AlertEngine(session)
            await engine.check_all_alerts()
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import Alert, DailyPrice, Notification
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class AlertEngine:
    """Service for monitoring and triggering stock alerts.

    This class implements the core alert checking logic that runs periodically
    to evaluate all active alerts against current market data.

    Attributes:
        CHECK_INTERVAL_SECONDS: Interval between alert checks (60 seconds).
        MAX_ALERTS_PER_CHECK: Maximum number of alerts to process per check (10000).
    """

    CHECK_INTERVAL_SECONDS = 60  # Check alerts every 1 minute
    MAX_ALERTS_PER_CHECK = 10000  # Process up to 10,000 alerts per check

    def __init__(
        self,
        session: AsyncSession,
        notification_service: Optional[NotificationService] = None,
    ):
        """Initialize the alert engine.

        Args:
            session: Database session for queries.
            notification_service: Service for sending notifications.
                If None, will be created automatically.
        """
        self.session = session
        self.notification_service = notification_service or NotificationService(session)

    async def check_all_alerts(self) -> int:
        """Check all active alerts and trigger those that meet conditions.

        This is the main entry point for the alert checking process.
        It retrieves all active alerts and processes them in batches.

        Returns:
            Number of alerts triggered.
        """
        logger.info("Starting alert check cycle")

        # Get all active alerts with related stock data
        result = await self.session.execute(
            select(Alert)
            .options(joinedload(Alert.stock), joinedload(Alert.user))
            .where(Alert.is_active == True)  # noqa: E712
            .limit(self.MAX_ALERTS_PER_CHECK)
        )
        active_alerts = result.unique().scalars().all()

        logger.info(f"Found {len(active_alerts)} active alerts to check")

        triggered_count = 0

        # Group alerts by stock code for efficient price fetching
        alerts_by_stock: dict[str, List[Alert]] = {}
        for alert in active_alerts:
            if alert.stock_code not in alerts_by_stock:
                alerts_by_stock[alert.stock_code] = []
            alerts_by_stock[alert.stock_code].append(alert)

        # Check alerts for each stock
        for stock_code, stock_alerts in alerts_by_stock.items():
            try:
                # Get latest price data for this stock
                price_data = await self._get_latest_price(stock_code)

                if not price_data:
                    logger.warning(f"No price data found for stock {stock_code}")
                    continue

                # Check each alert for this stock
                for alert in stock_alerts:
                    try:
                        if await self._check_alert(alert, price_data):
                            triggered_count += 1
                    except Exception as e:
                        logger.error(
                            f"Error checking alert {alert.id}: {str(e)}",
                            exc_info=True,
                        )
            except Exception as e:
                logger.error(
                    f"Error processing alerts for stock {stock_code}: {str(e)}",
                    exc_info=True,
                )

        await self.session.commit()

        logger.info(
            f"Alert check cycle complete. Triggered {triggered_count} out of "
            f"{len(active_alerts)} alerts"
        )

        return triggered_count

    async def _get_latest_price(self, stock_code: str) -> Optional[DailyPrice]:
        """Get the latest price data for a stock.

        Args:
            stock_code: Stock code to get price for.

        Returns:
            Latest price data or None if not found.
        """
        result = await self.session.execute(
            select(DailyPrice)
            .where(DailyPrice.stock_code == stock_code)
            .order_by(DailyPrice.date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _check_alert(
        self,
        alert: Alert,
        price_data: DailyPrice,
    ) -> bool:
        """Check if an alert should be triggered.

        Args:
            alert: Alert to check.
            price_data: Latest price data for the stock.

        Returns:
            True if alert was triggered, False otherwise.
        """
        should_trigger = False
        current_value = Decimal("0")

        # Check price alerts
        if alert.alert_type == "PRICE_ABOVE":
            current_value = price_data.close_price
            should_trigger = current_value >= alert.condition_value

        elif alert.alert_type == "PRICE_BELOW":
            current_value = price_data.close_price
            should_trigger = current_value <= alert.condition_value

        # Check volume alerts
        elif alert.alert_type == "VOLUME_SPIKE":
            # Get average volume from last 20 days
            avg_volume = await self._get_average_volume(
                alert.stock_code,
                days=20,
            )
            if avg_volume:
                current_value = Decimal(str(price_data.volume))
                # condition_value is the multiplier (e.g., 2.0 for 2x average)
                should_trigger = current_value >= (avg_volume * alert.condition_value)

        # Check percentage change alerts
        elif alert.alert_type == "CHANGE_PERCENT_ABOVE":
            if price_data.change_percent is not None:
                current_value = price_data.change_percent
                should_trigger = current_value >= alert.condition_value

        elif alert.alert_type == "CHANGE_PERCENT_BELOW":
            if price_data.change_percent is not None:
                current_value = price_data.change_percent
                should_trigger = current_value <= alert.condition_value

        # Trigger alert if condition is met
        if should_trigger:
            await self._trigger_alert(alert, current_value, price_data.date)
            return True

        return False

    async def _get_average_volume(
        self,
        stock_code: str,
        days: int = 20,
    ) -> Optional[Decimal]:
        """Calculate average trading volume over specified days.

        Args:
            stock_code: Stock code.
            days: Number of days to average (default: 20).

        Returns:
            Average volume or None if insufficient data.
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.avg(DailyPrice.volume))
            .where(DailyPrice.stock_code == stock_code)
            .order_by(DailyPrice.date.desc())
            .limit(days)
        )
        avg = result.scalar_one_or_none()

        return Decimal(str(avg)) if avg else None

    async def _trigger_alert(
        self,
        alert: Alert,
        current_value: Decimal,
        trigger_date: datetime,
    ) -> None:
        """Trigger an alert and create notification.

        Args:
            alert: Alert to trigger.
            current_value: Current value that triggered the alert.
            trigger_date: Date when alert was triggered.
        """
        logger.info(
            f"Triggering alert {alert.id} for user {alert.user_id}: "
            f"{alert.alert_type} on {alert.stock_code}"
        )

        # Mark alert as triggered
        alert.trigger(current_value, trigger_date)

        # Create notification
        notification_title, notification_message = self._create_notification_message(
            alert,
            current_value,
        )

        notification = Notification.create_from_alert(
            user_id=alert.user_id,
            alert_id=alert.id,
            title=notification_title,
            message=notification_message,
            priority="HIGH",
        )

        self.session.add(notification)
        await self.session.flush()  # Get notification ID

        # Send notification via enabled channels
        await self.notification_service.send_notification(
            user_id=alert.user_id,
            notification_id=notification.id,
        )

        logger.info(
            f"Alert {alert.id} triggered successfully. "
            f"Notification {notification.id} created and sent."
        )

    def _create_notification_message(
        self,
        alert: Alert,
        current_value: Decimal,
    ) -> tuple[str, str]:
        """Create notification title and message for triggered alert.

        Args:
            alert: Triggered alert.
            current_value: Current value that triggered the alert.

        Returns:
            Tuple of (title, message).
        """
        stock_code = alert.stock_code
        alert_type = alert.alert_type
        condition_value = alert.condition_value

        # Price alerts
        if alert_type == "PRICE_ABOVE":
            title = f"{stock_code} price alert triggered"
            message = (
                f"{stock_code} has reached your target price of "
                f"₩{condition_value:,.0f}. Current price: ₩{current_value:,.0f}"
            )
        elif alert_type == "PRICE_BELOW":
            title = f"{stock_code} price alert triggered"
            message = (
                f"{stock_code} has fallen below your target price of "
                f"₩{condition_value:,.0f}. Current price: ₩{current_value:,.0f}"
            )

        # Volume alerts
        elif alert_type == "VOLUME_SPIKE":
            title = f"{stock_code} volume spike detected"
            message = (
                f"{stock_code} trading volume has spiked to "
                f"{current_value:,.0f} shares ({condition_value}x average volume)"
            )

        # Change percentage alerts
        elif alert_type == "CHANGE_PERCENT_ABOVE":
            title = f"{stock_code} price change alert"
            message = (
                f"{stock_code} has increased by {current_value:.2f}%, "
                f"exceeding your threshold of {condition_value:.2f}%"
            )
        elif alert_type == "CHANGE_PERCENT_BELOW":
            title = f"{stock_code} price change alert"
            message = (
                f"{stock_code} has decreased by {current_value:.2f}%, "
                f"falling below your threshold of {condition_value:.2f}%"
            )
        else:
            title = f"{stock_code} alert triggered"
            message = f"Your alert for {stock_code} has been triggered"

        return title, message

    async def check_price_alerts(self) -> int:
        """Check only price alerts (PRICE_ABOVE, PRICE_BELOW).

        This is a convenience method for checking specific alert types.

        Returns:
            Number of price alerts triggered.
        """
        result = await self.session.execute(
            select(Alert)
            .options(joinedload(Alert.stock), joinedload(Alert.user))
            .where(
                and_(
                    Alert.is_active == True,  # noqa: E712
                    Alert.alert_type.in_(["PRICE_ABOVE", "PRICE_BELOW"]),
                )
            )
            .limit(self.MAX_ALERTS_PER_CHECK)
        )
        alerts = result.unique().scalars().all()

        triggered_count = 0

        for alert in alerts:
            try:
                price_data = await self._get_latest_price(alert.stock_code)
                if price_data and await self._check_alert(alert, price_data):
                    triggered_count += 1
            except Exception as e:
                logger.error(
                    f"Error checking price alert {alert.id}: {str(e)}",
                    exc_info=True,
                )

        await self.session.commit()
        return triggered_count

    async def check_volume_alerts(self) -> int:
        """Check only volume spike alerts.

        Returns:
            Number of volume alerts triggered.
        """
        result = await self.session.execute(
            select(Alert)
            .options(joinedload(Alert.stock), joinedload(Alert.user))
            .where(
                and_(
                    Alert.is_active == True,  # noqa: E712
                    Alert.alert_type == "VOLUME_SPIKE",
                )
            )
            .limit(self.MAX_ALERTS_PER_CHECK)
        )
        alerts = result.unique().scalars().all()

        triggered_count = 0

        for alert in alerts:
            try:
                price_data = await self._get_latest_price(alert.stock_code)
                if price_data and await self._check_alert(alert, price_data):
                    triggered_count += 1
            except Exception as e:
                logger.error(
                    f"Error checking volume alert {alert.id}: {str(e)}",
                    exc_info=True,
                )

        await self.session.commit()
        return triggered_count

    async def check_change_alerts(self) -> int:
        """Check only percentage change alerts.

        Returns:
            Number of change alerts triggered.
        """
        result = await self.session.execute(
            select(Alert)
            .options(joinedload(Alert.stock), joinedload(Alert.user))
            .where(
                and_(
                    Alert.is_active == True,  # noqa: E712
                    Alert.alert_type.in_([
                        "CHANGE_PERCENT_ABOVE",
                        "CHANGE_PERCENT_BELOW",
                    ]),
                )
            )
            .limit(self.MAX_ALERTS_PER_CHECK)
        )
        alerts = result.unique().scalars().all()

        triggered_count = 0

        for alert in alerts:
            try:
                price_data = await self._get_latest_price(alert.stock_code)
                if price_data and await self._check_alert(alert, price_data):
                    triggered_count += 1
            except Exception as e:
                logger.error(
                    f"Error checking change alert {alert.id}: {str(e)}",
                    exc_info=True,
                )

        await self.session.commit()
        return triggered_count
