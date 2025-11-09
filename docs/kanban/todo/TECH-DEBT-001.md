# [TECH-DEBT-001] Update Deprecated Code Patterns

## Metadata
- **Status**: TODO
- **Priority**: High
- **Assignee**: TBD
- **Estimated Time**: 3 hours
- **Sprint**: Sprint 1 (Week 1-2)
- **Tags**: #tech-debt #refactoring #python
- **Related Review**: docs/reviews/REVIEW_2025-11-09_initial-setup.md

## Description
Update code to use current Python and Pydantic patterns, removing deprecated functions and improving forward compatibility.

## Subtasks

### Update Pydantic to v2 Syntax
- [ ] Update `backend/app/core/config.py`
  - [ ] Replace `@validator` with `@field_validator`
  - [ ] Add `@classmethod` decorator
  - [ ] Update mode parameter to `mode="before"`
  - [ ] Remove unused `AnyHttpUrl` import
  - [ ] Test configuration loading

### Replace datetime.utcnow()
- [ ] Update `backend/app/core/security.py`
  - [ ] Import `timezone` from datetime
  - [ ] Replace all `datetime.utcnow()` with `datetime.now(timezone.utc)`
  - [ ] Test JWT token generation
  - [ ] Test token expiration validation

### Remove SQLite Support Code
- [ ] Update `backend/app/db/session.py`
  - [ ] Remove SQLite check in poolclass
  - [ ] Simplify engine creation
  - [ ] Update documentation

### Replace print() with Logging
- [ ] Update `backend/app/main.py`
  - [ ] Set up structured logging
  - [ ] Replace all print() statements with logger calls
  - [ ] Add log configuration
  - [ ] Test logging output

### Remove Docker Compose Version Field
- [ ] Update `docker-compose.yml`
  - [ ] Remove `version: '3.8'` line
  - [ ] Verify Docker Compose v2 compatibility

## Implementation Details

### Pydantic v2 Update
```python
# Before
from pydantic import AnyHttpUrl, validator

@validator("CORS_ORIGINS", pre=True)
def assemble_cors_origins(cls, v):
    ...

# After
from pydantic import field_validator

@field_validator("CORS_ORIGINS", mode="before")
@classmethod
def assemble_cors_origins(cls, v):
    ...
```

### Datetime Update
```python
# Before
from datetime import datetime, timedelta
expire = datetime.utcnow() + expires_delta

# After
from datetime import datetime, timedelta, timezone
expire = datetime.now(timezone.utc) + expires_delta
```

### Logging Setup
```python
# app/core/logging.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# app/main.py
import logging
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting Stock Screening Platform API")
```

## Acceptance Criteria
- [ ] No deprecation warnings when running the application
- [ ] All Pydantic validators work correctly
- [ ] JWT tokens generate with correct timestamps
- [ ] Logging shows structured output with levels
- [ ] Docker Compose works without version field
- [ ] All unit tests pass (after implementation)

## Dependencies
- **Depends on**: None
- **Blocks**: None (but should be done early)

## References
- **Review Document**: docs/reviews/REVIEW_2025-11-09_initial-setup.md
- **Pydantic v2 Migration**: https://docs.pydantic.dev/latest/migration/
- **Python datetime**: https://docs.python.org/3/library/datetime.html

## Progress
- **0%** - Not started

## Notes
- These changes improve forward compatibility
- No functionality changes, only API updates
- Safe to merge after BUGFIX-001
- Add deprecation warnings check to CI/CD
