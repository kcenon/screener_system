# [TECH-DEBT-002] Resolve Logging Circular Import Risk

## Metadata
- **Status**: REVIEW
- **Priority**: Medium
- **Assignee**: Development Team
- **Estimated Time**: 2 hours (Actual: 1.5 hours)
- **Sprint**: Sprint 2 (Week 3-4)
- **Tags**: #tech-debt #logging #refactoring
- **Related Review**: docs/reviews/REVIEW_2025-11-09_initial-setup.md (Follow-up Review)
- **Related**: TECH-DEBT-001 (Logging Implementation)

## Description
Restructure the logging module to eliminate potential circular import issues between `app.core.logging` and `app.core.config`. While currently not causing problems, this dependency pattern is fragile and could break with future changes.

## Issue Identified

**File**: `backend/app/core/logging.py:5`
**Severity**: Medium (Preventive)
**Current Impact**: None (working correctly)
**Future Risk**: High (could break with architectural changes)

Current dependency chain:
```
app.core.logging (imports) → app.core.config
app.core.config (could import) → app.core.logging (for logging config values)
```

This creates a fragile dependency where adding logging to the config module would cause a circular import.

## Subtasks

### Analyze Current Dependencies
- [x] Map all import dependencies between core modules
- [x] Identify potential circular import scenarios
- [x] Document current module initialization order

### Implement Solution
Choose one of the following approaches:

#### Option A: Lazy Import (CHOSEN)
- [x] Move `settings` import inside `setup_logging()` function
- [x] Test that logging still works correctly
- [x] Update docstrings

#### Option B: Dependency Injection
- [ ] Accept `log_level` as parameter to `setup_logging()`
- [ ] Pass `settings.LOG_LEVEL` from `main.py`
- [ ] Update all callers

#### Option C: Environment Variable Direct Access
- [ ] Use `os.getenv("LOG_LEVEL")` instead of `settings.LOG_LEVEL`
- [ ] Remove settings import
- [ ] Update documentation

### Testing
- [x] Verify no circular import errors
- [x] Test logging configuration with different levels
- [x] Test import order variations
- [x] Verify backend health check still works

### Documentation
- [x] Update module docstrings
- [x] Document chosen approach and rationale
- [x] Add comments explaining import strategy

## Implementation Details

### Option A: Lazy Import (Recommended)
```python
# backend/app/core/logging.py
"""Logging configuration for the application"""

import logging
import sys


def setup_logging() -> logging.Logger:
    """
    Configure application logging

    Note: Imports settings lazily to avoid circular import issues.

    Returns:
        Logger instance for the application
    """
    # Lazy import to avoid circular dependency
    from app.core.config import settings

    # Create logger
    logger = logging.getLogger("screener")

    # Set log level based on environment
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # ... rest of implementation
    return logger


# Global logger instance
logger = setup_logging()
```

**Pros**: Minimal code changes, clear intent
**Cons**: Settings imported on every module load

### Option B: Dependency Injection
```python
# backend/app/core/logging.py
"""Logging configuration for the application"""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure application logging

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger instance for the application
    """
    # Create logger
    logger = logging.getLogger("screener")

    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # ... rest of implementation
    return logger


# Default logger (can be reconfigured later)
logger = setup_logging()
```

```python
# backend/app/main.py
from app.core.config import settings
from app.core.logging import setup_logging

# Configure logging with settings
logger = setup_logging(settings.LOG_LEVEL)
```

**Pros**: Clear dependencies, testable
**Cons**: Requires updating callers

### Option C: Environment Variable Access
```python
# backend/app/core/logging.py
"""Logging configuration for the application"""

import logging
import os
import sys


def setup_logging() -> logging.Logger:
    """
    Configure application logging

    Reads LOG_LEVEL directly from environment to avoid circular imports.

    Returns:
        Logger instance for the application
    """
    # Create logger
    logger = logging.getLogger("screener")

    # Get log level from environment (no settings dependency)
    log_level = os.getenv("LOG_LEVEL", "INFO")
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # ... rest of implementation
    return logger


# Global logger instance
logger = setup_logging()
```

**Pros**: No settings dependency, simple
**Cons**: Bypasses Pydantic validation, could diverge from settings

## Acceptance Criteria
- [x] No circular import warnings or errors
- [x] Logging functionality unchanged
- [x] Log level configuration still works
- [x] Code is more maintainable and clear
- [x] Import order doesn't matter
- [x] Documentation explains import strategy

## Dependencies
- **Depends on**: TECH-DEBT-001 (completed)
- **Blocks**: None

## References
- **Review Document**: docs/reviews/REVIEW_2025-11-09_initial-setup.md (§ New Issues #3)
- **Python Circular Imports**: https://docs.python.org/3/faq/programming.html#what-are-the-best-practices-for-using-import-in-a-module
- **Logging Best Practices**: https://docs.python.org/3/howto/logging.html

## Progress
- **100%** - Completed

## Implementation Summary

**Chosen Approach**: Option A (Lazy Import)

**Changes Made**:
1. Moved `from app.core.config import settings` from module-level to inside `setup_logging()` function
2. Added clear documentation in docstring explaining the circular import avoidance
3. Added inline comment before the lazy import

**Tests Performed**:
1. ✅ Logging module import successful
2. ✅ Config module import successful
3. ✅ Logger instance created correctly (level 20 = INFO)
4. ✅ Config module reload without circular import
5. ✅ Logging functionality works (info/warning messages)
6. ✅ Backend health check endpoint responds correctly

**Verification**:
- All tests passed in Docker environment
- No changes required to consuming modules
- Zero impact on functionality
- Prevention of future circular import issues

## Notes
- Current implementation works fine, but this is technical debt prevention
- Best addressed before the codebase grows larger
- ✅ Chose Option A (lazy import) for quickest fix with minimal changes
- Option B (dependency injection) would be clearest architecture but requires more changes
- Avoided Option C as it bypasses Pydantic validation
- Consider adding import order tests to CI/CD (future improvement)
