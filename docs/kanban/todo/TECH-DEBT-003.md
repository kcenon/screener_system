# [TECH-DEBT-003] Database Session Cleanup

## Metadata
- **Status**: TODO
- **Priority**: Low
- **Assignee**: Development Team
- **Estimated Time**: 2 hours
- **Sprint**: Sprint 2 (Week 3-4) or later
- **Tags**: #tech-debt #database #cleanup #sqlalchemy
- **Related Review**: docs/reviews/REVIEW_2025-11-09_initial-setup.md (Initial Review + Follow-up)
- **Related**: DB-001, TECH-DEBT-001 (deferred items)

## Description
Clean up database session management code by removing unnecessary auto-commit behavior and SQLite-specific code that is not needed for this PostgreSQL-only project.

## Issues Identified

### 1. Auto-commit in Database Session
**File**: `backend/app/db/session.py:41`
**Severity**: Low
**Impact**: Commits transactions even for read-only operations, causing unnecessary overhead.

Current implementation:
```python
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # ← Auto-commits for all operations
        except Exception:
            await session.rollback()
            raise
```

**Issues**:
- SELECT queries don't need commit
- Reduces flexibility for transaction management
- Callers can't control transaction boundaries
- Minor performance overhead

### 2. Unnecessary SQLite Check
**File**: `backend/app/db/session.py:15`
**Severity**: Low
**Impact**: Adds unnecessary complexity since project only uses PostgreSQL.

Current implementation:
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
    echo=settings.DB_ECHO,
)
```

**Issues**:
- Project exclusively uses TimescaleDB (PostgreSQL)
- SQLite check adds cognitive overhead
- NullPool would never be used
- Violates YAGNI principle

## Subtasks

### Remove Auto-commit Behavior
- [ ] Review current database usage patterns
  - [ ] Identify all `get_db()` usage locations
  - [ ] Check if any code relies on auto-commit
  - [ ] Document transaction boundaries
- [ ] Update `get_db()` to remove auto-commit
- [ ] Update callers to manage transactions explicitly
  - [ ] Add `await session.commit()` where needed
  - [ ] Ensure rollback on exceptions
- [ ] Test all database operations
- [ ] Update documentation

### Remove SQLite Support Code
- [ ] Remove SQLite check from engine creation
- [ ] Simplify to PostgreSQL-only configuration
- [ ] Remove NullPool import if not used elsewhere
- [ ] Update comments to reflect PostgreSQL-only support

### Testing
- [ ] Test database operations after removing auto-commit
- [ ] Verify transactions work correctly
- [ ] Test rollback on exceptions
- [ ] Ensure connection pooling works as expected

### Documentation
- [ ] Document transaction management strategy
- [ ] Update API documentation
- [ ] Add examples of explicit transaction management

## Implementation Details

### Remove Auto-commit
```python
# backend/app/db/session.py

# Before
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # ← Remove this
        except Exception:
            await session.rollback()
            raise

# After
async def get_db() -> AsyncSession:
    """
    Get database session

    Note: Callers are responsible for committing transactions.
    The session will automatically rollback on exceptions.
    """
    async with AsyncSessionLocal() as session:
        yield session
```

### Update Callers (Example)
```python
# In API endpoints or services

# Read-only operation (no commit needed)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# Write operation (explicit commit)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = User(**user_data.dict())
    db.add(user)
    await db.commit()  # ← Explicit commit
    await db.refresh(user)
    return user

# Transaction with multiple operations
async def transfer_funds(
    from_id: int, to_id: int, amount: Decimal,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Multiple operations in one transaction
        await db.execute(
            update(Account)
            .where(Account.id == from_id)
            .values(balance=Account.balance - amount)
        )
        await db.execute(
            update(Account)
            .where(Account.id == to_id)
            .values(balance=Account.balance + amount)
        )
        await db.commit()  # ← Commit all or nothing
    except Exception:
        await db.rollback()
        raise
```

### Remove SQLite Code
```python
# backend/app/db/session.py

# Before
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
    echo=settings.DB_ECHO,
)

# After
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
)
```

## Acceptance Criteria
- [ ] Auto-commit removed from `get_db()`
- [ ] All database operations still work correctly
- [ ] Transactions are managed explicitly by callers
- [ ] SQLite-specific code removed
- [ ] No unused imports remain
- [ ] Database tests pass
- [ ] Transaction management documented

## Dependencies
- **Depends on**: None (deferred from TECH-DEBT-001)
- **Blocks**: None

## References
- **Review Document**:
  - docs/reviews/REVIEW_2025-11-09_initial-setup.md (Initial Review §6, §11)
  - docs/reviews/REVIEW_2025-11-09_initial-setup.md (Follow-up Review §5, §6)
- **TECH-DEBT-001**: docs/kanban/done/TECH-DEBT-001.md (deferred items)
- **SQLAlchemy Session Docs**: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- **Transaction Management**: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html

## Progress
- **0%** - Not started

## Notes
- Deferred from TECH-DEBT-001 due to low priority
- No immediate impact on functionality
- Good opportunity to add transaction management tests
- Consider adding transaction decorator/context manager for common patterns
- Example decorator pattern:
  ```python
  from contextlib import asynccontextmanager

  @asynccontextmanager
  async def transactional(db: AsyncSession):
      try:
          yield db
          await db.commit()
      except Exception:
          await db.rollback()
          raise

  # Usage
  async with transactional(db):
      # operations here
      pass
  ```
- Can be combined with adding transaction monitoring/logging
- Low priority - can be addressed when adding write operations
