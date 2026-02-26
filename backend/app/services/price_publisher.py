"""Price update publisher service for WebSocket real-time streaming"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.redis_pubsub import redis_pubsub
from app.db.models.stock import Stock
from app.schemas.websocket import (MarketStatus, MessageType, OrderBookLevel,
                                   OrderBookUpdate, PriceUpdate)


class PricePublisher:
    """
    Service for publishing real-time price updates to Redis.

    This service:
    - Fetches price updates from data sources
    - Publishes to Redis channels
    - Supports multiple data sources (KIS API, mock data, etc.)
    """

    def __init__(self):
        """Initialize price publisher"""
        self._running = False
        self._publish_task: Optional[asyncio.Task] = None

    async def publish_price_update(
        self,
        stock_code: str,
        price: float,
        change: float,
        change_percent: float,
        volume: int,
    ):
        """
        Publish a price update to Redis.

        Args:
            stock_code: Stock code (e.g., "005930")
            price: Current price
            change: Price change
            change_percent: Price change percentage
            volume: Trading volume
        """
        try:
            # Create price update message
            update = PriceUpdate(
                type=MessageType.PRICE_UPDATE,
                stock_code=stock_code,
                price=price,
                change=change,
                change_percent=change_percent,
                volume=volume,
                timestamp=datetime.utcnow(),
            )

            # Publish to Redis channel
            channel = f"stock:{stock_code}:price"
            await redis_pubsub.publish(
                channel,
                update.model_dump(mode="json"),
            )

            logger.debug(
                f"Published price update for {stock_code}: "
                f"${price} ({change_percent:+.2f}%)"
            )

        except Exception as e:
            logger.error(f"Error publishing price update for {stock_code}: {e}")

    async def publish_orderbook_update(
        self,
        stock_code: str,
        bids: List[Dict],
        asks: List[Dict],
    ):
        """
        Publish order book update to Redis.

        Args:
            stock_code: Stock code
            bids: List of bid levels
                [{"price": 100, "quantity": 1000, "orders": 5}, ...]
            asks: List of ask levels
                [{"price": 101, "quantity": 800, "orders": 3}, ...]
        """
        try:
            # Convert to OrderBookLevel models
            bid_levels = [OrderBookLevel(**bid) for bid in bids]
            ask_levels = [OrderBookLevel(**ask) for ask in asks]

            # Create order book update message
            update = OrderBookUpdate(
                type=MessageType.ORDERBOOK_UPDATE,
                stock_code=stock_code,
                bids=bid_levels,
                asks=ask_levels,
                timestamp=datetime.utcnow(),
            )

            # Publish to Redis channel
            channel = f"stock:{stock_code}:orderbook"
            await redis_pubsub.publish(
                channel,
                update.model_dump(mode="json"),
            )

            logger.debug(f"Published order book update for {stock_code}")

        except Exception as e:
            logger.error(f"Error publishing order book update for {stock_code}: {e}")

    async def publish_market_status(
        self,
        market: str,
        status: str,
    ):
        """
        Publish market status change to Redis.

        Args:
            market: Market name (KOSPI, KOSDAQ)
            status: Market status (open, closed, pre_market, after_hours)
        """
        try:
            # Create market status message
            update = MarketStatus(
                type=MessageType.MARKET_STATUS,
                market=market,
                status=status,
                timestamp=datetime.utcnow(),
            )

            # Publish to Redis channel
            channel = f"market:{market}:status"
            await redis_pubsub.publish(
                channel,
                update.model_dump(mode="json"),
            )

            logger.info(f"Published market status for {market}: {status}")

        except Exception as e:
            logger.error(f"Error publishing market status for {market}: {e}")

    async def publish_bulk_price_updates(
        self,
        updates: List[Dict],
    ):
        """
        Publish multiple price updates in bulk.

        Args:
            updates: List of price update dicts with keys:
                     stock_code, price, change, change_percent, volume
        """
        tasks = []

        for update in updates:
            task = self.publish_price_update(
                stock_code=update["stock_code"],
                price=update["price"],
                change=update["change"],
                change_percent=update["change_percent"],
                volume=update["volume"],
            )
            tasks.append(task)

        # Execute all publishes concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(f"Published {len(updates)} price updates")

    async def start_mock_publisher(
        self,
        db: AsyncSession,
        interval: float = 1.0,
    ):
        """
        Start mock price publisher for testing.

        Publishes random price updates at regular intervals.

        Args:
            db: Database session
            interval: Update interval in seconds
        """
        if self._running:
            logger.warning("Mock publisher already running")
            return

        self._running = True
        self._publish_task = asyncio.create_task(self._mock_publish_loop(db, interval))

        logger.info(f"Started mock price publisher (interval: {interval}s)")

    async def stop_mock_publisher(self):
        """Stop mock price publisher"""
        self._running = False

        if self._publish_task:
            self._publish_task.cancel()
            try:
                await self._publish_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped mock price publisher")

    async def _mock_publish_loop(
        self,
        db: AsyncSession,
        interval: float,
    ):
        """
        Mock publishing loop for testing.

        Args:
            db: Database session
            interval: Update interval in seconds
        """
        import random

        try:
            # Get some stocks from database
            result = await db.execute(select(Stock).limit(20))
            stocks = result.scalars().all()

            if not stocks:
                logger.warning("No stocks found for mock publisher")
                return

            logger.info(f"Mock publisher using {len(stocks)} stocks")

            while self._running:
                # Generate random updates for stocks
                for stock in stocks:
                    # Random price movement (-2% to +2%)
                    change_percent = random.uniform(-2.0, 2.0)
                    price = 10000 + random.uniform(-200, 200)  # Mock price
                    change = price * (change_percent / 100)
                    volume = random.randint(100000, 10000000)

                    await self.publish_price_update(
                        stock_code=stock.stock_code,
                        price=price,
                        change=change,
                        change_percent=change_percent,
                        volume=volume,
                    )

                # Wait before next update
                await asyncio.sleep(interval)

        except asyncio.CancelledError:
            logger.info("Mock publish loop cancelled")
            raise

        except Exception as e:
            logger.error(f"Error in mock publish loop: {e}")


# Global price publisher instance
price_publisher = PricePublisher()
