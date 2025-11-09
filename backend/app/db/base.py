"""Base database model"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


def utc_now() -> datetime:
    """Return current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base class for all database models"""

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class BaseModel(Base, TimestampMixin):
    """Base model with id and timestamps"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
