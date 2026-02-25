"""baseline: initial schema marker

Revision ID: 0001
Revises:
Create Date: 2026-02-26 00:00:00.000000+00:00

This is the baseline migration for the Stock Screening Platform.
It represents the existing database schema established by the raw SQL
migration files in database/migrations/ (00_extensions.sql through
15_create_ml_features.sql).

For existing databases:
    alembic stamp head
    (Marks the database as up-to-date without running any migrations.)

For new databases:
    Apply the SQL migration files first, then stamp:
    psql -f database/migrations/00_extensions.sql ...
    alembic stamp head

All future schema changes should be managed through Alembic migrations
created with: alembic revision --autogenerate -m "description"
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Baseline migration — existing schema is managed by raw SQL files.
    # No operations needed; stamp this revision on existing databases.
    pass


def downgrade() -> None:
    # Cannot downgrade past the baseline.
    pass
