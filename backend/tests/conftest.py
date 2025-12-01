"""Pytest configuration and fixtures"""

import asyncio
import os
import sys
from typing import AsyncGenerator
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

# Mock Redis connection to prevent startup failures
from unittest.mock import AsyncMock

from app.core.cache import cache_manager
from app.core.redis_pubsub import redis_pubsub
from app.core.websocket import connection_manager

cache_manager.connect = AsyncMock()
cache_manager.disconnect = AsyncMock()
connection_manager.initialize_redis = AsyncMock()
redis_pubsub.disconnect = AsyncMock()

# Mock ML dependencies if not installed (for local testing on incompatible platforms)
for module_name in [
    "mlflow",
    "mlflow.tracking",
    "numpy",
    "pandas",
    "lightgbm",
    "xgboost",
    "optuna",
    "sklearn",
    "sklearn.metrics",
    "sklearn.model_selection",
    "scipy",
    "scipy.stats",
    "tensorflow",
    "keras",
]:
    try:
        __import__(module_name)
    except ImportError:
        sys.modules[module_name] = MagicMock()

import app.db.models  # noqa: F401, E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

# Test database URL (use PostgreSQL test database)
# Use environment variable or default to test database
# Support both Docker (screener_postgres) and CI (localhost/postgres) environments
DEFAULT_TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://screener_user:your_secure_password_here@"
        "localhost:5432/screener_test",
    )
    .replace("screener_db", "screener_test")
    .replace("postgresql://", "postgresql+asyncpg://")
    .replace("postgres://", "postgresql+asyncpg://"),
)

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop

    # Clean up pending tasks
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()

    # Allow tasks to cancel
    if pending:
        try:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass

    loop.close()


@pytest_asyncio.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with transaction rollback"""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    # Create connection
    async with db_engine.connect() as connection:
        # Begin transaction
        async with connection.begin() as transaction:
            # Create session bound to connection
            async_session = async_sessionmaker(
                bind=connection,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            async with async_session() as session:
                yield session

            # Rollback transaction (cleanup)
            await transaction.rollback()


@pytest_asyncio.fixture
async def db_session(db: AsyncSession) -> AsyncSession:
    """Alias for db session to match test naming"""
    return db


@pytest_asyncio.fixture
async def test_user(db: AsyncSession):
    """Create test user"""
    from app.core.security import get_password_hash
    from app.db.models import User

    user = User(
        email="test@example.com",
        name="testuser",
        password_hash=get_password_hash("testpassword"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_stock(db: AsyncSession):
    """Create test stock"""
    from app.db.models import Stock

    stock = Stock(
        code="005930",
        name="삼성전자",
        market="KOSPI",
        sector="전기전자",
        industry="반도체",
    )
    db.add(stock)
    await db.commit()
    await db.refresh(stock)
    return stock


@pytest_asyncio.fixture
async def auth_headers(test_user):
    """Create authentication headers for test user"""
    from app.core.security import create_access_token

    access_token = create_access_token(
        subject=test_user.id,
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client"""

    # Override database dependency
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    # Create client (httpx 0.28+ requires ASGITransport instead of app parameter)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    # Clear overrides
    app.dependency_overrides.clear()
