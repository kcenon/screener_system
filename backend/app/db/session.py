"""Database session management for PostgreSQL + TimescaleDB"""

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.core.config import settings

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency to get database session.

    Note: Callers are responsible for committing transactions explicitly.
    The session will automatically rollback on exceptions.

    Usage for read-only operations:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Usage for write operations:
        @app.post("/items/")
        async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
            db_item = Item(**item.dict())
            db.add(db_item)
            await db.commit()  # Explicit commit required
            await db.refresh(db_item)
            return db_item
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
