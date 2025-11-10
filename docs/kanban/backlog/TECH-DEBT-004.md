# [TECH-DEBT-004] Code Formatting and Linting Cleanup

## Metadata
- **Status**: TODO
- **Priority**: Medium
- **Assignee**: TBD
- **Estimated Time**: 4 hours
- **Sprint**: Sprint 2 (Week 3-4)
- **Tags**: #tech-debt #code-quality #formatting

## Description
Fix all code formatting and linting issues identified by the CI/CD pipeline. Ensure all code passes black, isort, flake8, mypy (backend) and ESLint, Prettier (frontend) checks.

## Context
CI/CD pipeline (INFRA-002) was implemented with linting checks set to non-blocking mode to allow the initial PR to merge. This ticket addresses the accumulated formatting issues that need to be resolved.

## Subtasks

### Backend Formatting
- [ ] Run black formatter on all backend files
  - [ ] `app/api/error_handlers.py`
  - [ ] `app/core/logging.py`
  - [ ] `app/core/exceptions.py`
  - [ ] `app/db/models/daily_price.py`
  - [ ] `app/db/models/user_session.py`
  - [ ] `app/db/models/user.py`
  - [ ] `app/db/models/financial_statement.py`
  - [ ] `app/repositories/stock_repository.py`
  - [ ] `app/services/stock_service.py`
  - [ ] `tests/api/test_auth.py`

### Backend Import Sorting
- [ ] Run isort on all Python files
- [ ] Verify import order follows PEP 8 standards
- [ ] Group imports: stdlib, third-party, local

### Backend Type Checking
- [ ] Fix mypy type errors
- [ ] Add missing type hints where needed
- [ ] Resolve any type inconsistencies

### Backend Code Quality
- [ ] Fix flake8 violations
- [ ] Ensure max line length (100 chars)
- [ ] Address any code complexity issues

### Frontend Formatting
- [ ] Run Prettier on all frontend files
- [ ] Fix any ESLint errors/warnings
- [ ] Ensure consistent code style

### CI/CD Update
- [ ] After all fixes, change linting to blocking mode
- [ ] Update `.github/workflows/ci.yml`
  - [ ] Remove `continue-on-error: true` from linting steps
  - [ ] Remove non-blocking echo messages
- [ ] Verify all checks pass

## Acceptance Criteria
- [ ] **Backend Code Quality**
  - [ ] `black --check .` passes with 0 files to reformat
  - [ ] `isort --check-only .` passes
  - [ ] `flake8 app tests` passes with 0 errors
  - [ ] `mypy app` passes with 0 errors
  
- [ ] **Frontend Code Quality**
  - [ ] `npm run lint` passes with 0 errors
  - [ ] `npx prettier --check "src/**/*"` passes
  
- [ ] **CI/CD Pipeline**
  - [ ] All linting jobs in CI pipeline pass
  - [ ] Linting is enforced as blocking (no continue-on-error)
  - [ ] No warnings in CI output

## Dependencies
- **Depends on**: INFRA-002 (CI/CD Pipeline)
- **Blocks**: None (but improves code quality)

## References
- **INFRA-002**: CI/CD Pipeline implementation
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [ESLint Documentation](https://eslint.org/)
- [Prettier Documentation](https://prettier.io/)

## Progress
- **0%** - Not started

## Notes
- Run formatters before committing: `black . && isort .` (backend)
- Frontend auto-format: `npm run format` (if configured)
- Consider setting up pre-commit hooks to prevent future issues
- This is a one-time cleanup; CI will enforce standards going forward
- Estimated 10 files need reformatting in backend
- Frontend formatting status to be determined

## Commands

### Backend
```bash
cd backend

# Auto-fix formatting
black .
isort .

# Verify
black --check .
isort --check-only .
flake8 app tests --max-line-length=100 --extend-ignore=E203,W503
mypy app --ignore-missing-imports
```

### Frontend
```bash
cd frontend

# Auto-fix formatting
npm run format
npm run lint -- --fix

# Verify
npm run lint
npx prettier --check "src/**/*.{js,jsx,ts,tsx,css,md}"
```
