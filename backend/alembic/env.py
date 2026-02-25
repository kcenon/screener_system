"""Alembic environment configuration.

Imports all SQLAlchemy models so that autogenerate can detect schema changes.
Converts the async DATABASE_URL to a synchronous one for Alembic.
"""

import os
import re
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import Base metadata — this is the target for autogenerate.
from app.db.base import Base

# Import ALL models so they register with Base.metadata.
# The __init__.py re-exports every model; importing it is sufficient.
import app.db.models  # noqa: F401

# Alembic Config object (provides access to alembic.ini values).
config = context.config

# Set up Python logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData object for autogenerate support.
target_metadata = Base.metadata


def get_sync_url() -> str:
    """Convert async DATABASE_URL to a synchronous one for Alembic.

    postgresql+asyncpg://...  ->  postgresql://...
    """
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Alembic requires it to connect to the database."
        )
    # Strip async driver suffixes (+asyncpg, +aiosqlite, etc.)
    return re.sub(r"\+\w+", "", url, count=1)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    Useful for reviewing migration SQL before applying.

    Usage:
        alembic upgrade head --sql
    """
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Connects to the database and applies migrations directly.
    """
    # Override sqlalchemy.url with the environment variable.
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_sync_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
