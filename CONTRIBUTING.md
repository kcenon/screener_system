# Contributing Guide

## Code Quality Standards

All code must pass the following quality gates before merging. These same checks run in CI
and will **block merges** if they fail.

## Quick Start

### Install pre-commit hooks (recommended)

Pre-commit hooks automatically run quality checks before each commit, catching issues early.

```bash
pip install pre-commit
pre-commit install
```

After installation, hooks run automatically on `git commit`. To run all hooks manually:

```bash
pre-commit run --all-files
```

---

## Backend (Python)

### Setup

```bash
cd backend
pip install -r requirements.txt
pip install black flake8 mypy isort
```

### Checks

| Tool | Command | What it checks |
|------|---------|----------------|
| black | `black --check .` | Code formatting |
| isort | `isort --check-only .` | Import ordering |
| flake8 | `flake8 app tests --max-line-length=100 --extend-ignore=E203,W503` | Linting |
| mypy | `mypy app --ignore-missing-imports` | Type checking |
| pytest | `pytest` | Tests + ≥65% coverage |

### Auto-fix formatting

```bash
cd backend
black .
isort .
```

### Run tests with coverage

```bash
cd backend
pytest
# Coverage report: htmlcov/index.html
```

The minimum coverage threshold is **65%**. PRs that drop coverage below this threshold
will fail CI.

---

## Frontend (TypeScript/React)

### Setup

```bash
cd frontend
npm ci
```

### Checks

| Tool | Command | What it checks |
|------|---------|----------------|
| ESLint | `npm run lint` | Linting |
| Prettier | `npx prettier --check "src/**/*.{js,jsx,ts,tsx,css,md}"` | Formatting |
| TypeScript | `npm run type-check` | Type checking |
| Vitest | `npm test -- --run` | Unit tests |

### Auto-fix formatting

```bash
cd frontend
npx prettier --write "src/**/*.{js,jsx,ts,tsx,css,md}"
npm run lint -- --fix
```

---

## CI Pipeline

The following jobs must all pass before a PR can be merged:

- **backend-lint** — black, isort, flake8, mypy
- **backend-test** — pytest with ≥65% coverage gate
- **frontend-lint** — ESLint, Prettier
- **frontend-test** — TypeScript check + Vitest

Run these locally before pushing to avoid CI round-trips.
