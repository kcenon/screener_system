# E2E Tests

End-to-end tests for the Stock Screening Platform using Playwright.

## Overview

This directory contains E2E tests that verify complete user workflows across the application. The tests use Playwright, a modern testing framework that supports multiple browsers and provides excellent developer experience.

## Test Structure

```
e2e/
├── fixtures/           # Test data and fixtures
│   └── test-users.ts   # User credentials for testing
├── auth.setup.ts       # Authentication setup (runs before tests)
├── auth-flow.spec.ts   # Authentication flow E2E tests
└── README.md           # This file
```

## Running Tests

### Prerequisites

1. Install dependencies:
   ```bash
   npm install
   ```

2. Install Playwright browsers (if not already installed):
   ```bash
   npx playwright install chromium
   ```

### Test Commands

```bash
# Run all E2E tests (headless)
npm run test:e2e

# Run tests with UI mode (interactive)
npm run test:e2e:ui

# Run tests in headed mode (visible browser)
npm run test:e2e:headed

# Debug tests
npm run test:e2e:debug

# View test report
npm run test:e2e:report
```

### Running Specific Tests

```bash
# Run specific test file
npx playwright test auth-flow

# Run specific test by name
npx playwright test -g "successful login"

# Run tests in specific browser
npx playwright test --project=chromium
```

## Test Files

### `auth-flow.spec.ts`

Comprehensive authentication flow tests including:

- **Login Flow** (1.5h implementation)
  - Successful login with redirect
  - Invalid credentials error handling
  - Form validation (empty fields, invalid email, short password)
  - Remember me functionality

- **Authentication State** (1h implementation)
  - Authenticated access to protected routes
  - Unauthenticated redirect to login
  - Token persistence across page reloads
  - Expired token handling

- **Protected Routes** (1h implementation)
  - Public routes accessible without auth
  - Protected routes require authentication
  - Logged-in user cannot access login page

- **Logout Flow** (0.5h implementation)
  - Logout clears authentication
  - Logout clears local storage
  - Logout from any page redirects properly

## Test Data

### Test Users

Test user credentials are defined in `fixtures/test-users.ts`:

- **Valid User**: `test@example.com` / `TestPassword123!`
- **Invalid User**: `invalid@example.com` / `WrongPassword123!`

⚠️ **Important**: These users must exist in your test database for tests to pass.

## Configuration

Test configuration is in `playwright.config.ts` at the frontend root:

- **Test Directory**: `./e2e`
- **Base URL**: `http://localhost:5173` (configurable via `VITE_APP_URL`)
- **Browsers**: Chromium (uses system Chrome)
- **Screenshots**: On failure only
- **Videos**: Retained on failure
- **Traces**: On first retry

## CI/CD Integration

Tests are configured to run in CI environments:

- Retries: 2 (only in CI)
- Workers: 1 (serial execution in CI)
- Reporter: GitHub Actions format + HTML report

### GitHub Actions Example

```yaml
- name: Install dependencies
  run: npm ci

- name: Install Playwright Browsers
  run: npx playwright install --with-deps chromium

- name: Run E2E tests
  run: npm run test:e2e
  env:
    VITE_APP_URL: http://localhost:5173

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Best Practices

### 1. Use Data Test IDs

For stable selectors, use `data-testid` attributes:

```tsx
<button data-testid="logout-button">Logout</button>
```

```ts
await page.click('[data-testid="logout-button"]');
```

### 2. Wait for Network Idle

After navigation or actions:

```ts
await page.waitForLoadState('networkidle');
```

### 3. Use Descriptive Test Names

```ts
test('successful login redirects to dashboard', async ({ page }) => {
  // ...
});
```

### 4. Clean Up After Tests

Playwright automatically cleans up:
- Browser contexts
- Cookies
- Local storage

But you can manually reset if needed:

```ts
test.beforeEach(async ({ page }) => {
  await page.context().clearCookies();
});
```

## Troubleshooting

### Tests Fail with "Element not found"

- Check if selectors match actual HTML
- Use `data-testid` attributes for stability
- Wait for elements: `await page.waitForSelector('#email')`

### Tests Fail with "Navigation timeout"

- Increase timeout in config
- Check if dev server is running
- Verify network connectivity

### Tests Pass Locally but Fail in CI

- Check browser versions
- Verify test database state
- Check environment variables
- Review CI logs and screenshots

## Coverage

Current E2E test coverage:

- ✅ Authentication flows: 100%
- ⏳ Stock screener flows: 0% (TODO)
- ⏳ Stock detail flows: 0% (TODO)
- ⏳ Watchlist flows: 0% (TODO)

**Target**: 85%+ coverage of critical user paths

## References

- [Playwright Documentation](https://playwright.dev)
- [TEST-010 Ticket](../../docs/kanban/todo/TEST-010.md)
- [Test Improvement Plan](../../docs/TEST_IMPROVEMENT_PLAN.md)

---

**Last Updated**: 2025-11-17
**Implemented By**: TEST-010 ticket
**Total Effort**: 4 hours
