# Database Migration Workflow

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema
migrations. All schema changes should go through Alembic to ensure safe,
versioned, and rollback-capable database evolution.

## Quick Reference

```bash
cd backend/

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current database revision
alembic current

# Show migration history
alembic history --verbose

# Create a new migration (auto-detect model changes)
alembic revision --autogenerate -m "add column X to table Y"

# Generate SQL without applying (for review)
alembic upgrade head --sql

# Check for unapplied model changes
alembic check
```

## Setup for Existing Databases

If the database already has tables created by the raw SQL migration files
(`database/migrations/`), stamp the baseline revision to mark it as current:

```bash
cd backend/
export DATABASE_URL="postgresql://user:password@localhost:5432/screener_db"
alembic stamp head
```

This tells Alembic "the database is already at the latest migration" without
running any DDL.

## Creating a New Migration

1. **Modify your SQLAlchemy model** in `backend/app/db/models/`.

2. **Generate the migration**:

   ```bash
   cd backend/
   export DATABASE_URL="postgresql://user:password@localhost:5432/screener_db"
   alembic revision --autogenerate -m "add email_verified column to user"
   ```

3. **Review the generated file** in `backend/alembic/versions/`. Autogenerate
   may miss or incorrectly detect some changes (see Limitations below).

4. **Apply the migration**:

   ```bash
   alembic upgrade head
   ```

5. **Commit** both the model change and the migration file together.

## Rollback

```bash
# Rollback one step
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# Rollback everything (use with caution)
alembic downgrade base
```

## Environment Variable

Alembic reads `DATABASE_URL` from the environment. The `env.py` automatically
converts async URLs (`postgresql+asyncpg://`) to synchronous ones
(`postgresql://`) for compatibility.

| Environment | DATABASE_URL Example |
|-------------|---------------------|
| Development | `postgresql://screener_user:pass@localhost:5432/screener_db` |
| CI | `postgresql://postgres:postgres@localhost:5432/screener_test` |
| Docker | `postgresql://screener_user:pass@postgres:5432/screener_db` |

## CI Integration

The CI pipeline validates the migration chain on every push:

- **Single head check**: Ensures no branching in migration history.
- **Syntax validation**: Migration files are imported during the check.

If the CI check fails with "Multiple migration heads detected", merge the
branches:

```bash
alembic merge -m "merge heads" <head1> <head2>
```

## Autogenerate Limitations

Alembic's `--autogenerate` **can** detect:
- Table additions and removals
- Column additions and removals
- Column type changes (with caveats)
- Nullable changes
- Index and unique constraint changes

Alembic's `--autogenerate` **cannot** detect:
- Table or column renames (detected as drop + add)
- Changes to column constraints beyond nullable/unique
- Changes to `server_default` values
- Enum value additions
- Custom DDL (e.g., TimescaleDB hypertables, PostgreSQL extensions)

For these cases, write the migration manually with `alembic revision -m "..."`.

## Deprecation of Raw SQL Migrations

The files in `database/migrations/` (00_extensions.sql through
15_create_ml_features.sql) are retained as **historical reference**. New schema
changes must go through Alembic.

| Phase | Action |
|-------|--------|
| Current | Raw SQL files retained for reference; Alembic for new changes |
| Future | Once all environments are on Alembic, SQL files can be archived |
