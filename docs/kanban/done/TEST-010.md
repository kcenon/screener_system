# TEST-010: E2E Authentication Flow Tests

**Type**: TEST
**Priority**: P0
**Status**: TODO
**Created**: 2025-11-16
**Effort**: 4 hours
**Phase**: Phase 1 - Critical Tests

---

## Description

Implement end-to-end (E2E) tests for the complete authentication flow. This tests the entire user journey from login through dashboard access to logout, ensuring authentication state is properly managed across the application.

## Current Status

- **Test File**: `frontend/e2e/auth_flow.e2e.ts` does not exist
- **Framework**: Playwright or Cypress (to be determined)
- **Coverage Impact**: E2E authentication flow with 0% test coverage

## Test Requirements

### 1. Login Flow (1.5h)

```typescript
describe('E2E Authentication Flow', () => {
  test('successful login redirects to dashboard', async () => {
    // 1. Visit login page
    // 2. Enter valid credentials
    // 3. Click login button
    // 4. Wait for redirect to /dashboard
    // 5. Verify dashboard content visible
  });

  test('login with invalid credentials shows error', async () => {
    // 1. Visit login page
    // 2. Enter invalid credentials
    // 3. Click login button
    // 4. Verify error message displayed
    // 5. Verify still on login page
  });

  test('login form validation', async () => {
    // 1. Visit login page
    // 2. Submit empty form
    // 3. Verify validation errors
    // 4. Enter invalid email format
    // 5. Verify email validation error
  });

  test('remember me functionality', async () => {
    // 1. Login with "Remember Me" checked
    // 2. Close browser
    // 3. Open browser and visit site
    // 4. Verify still logged in
  });
});
```

### 2. Authentication State (1h)

```typescript
describe('Authentication State Management', () => {
  test('authenticated user can access protected routes', async () => {
    // 1. Login
    // 2. Navigate to /screener
    // 3. Verify screener page loads
    // 4. Navigate to /watchlist
    // 5. Verify watchlist page loads
  });

  test('unauthenticated user redirected to login', async () => {
    // 1. Ensure logged out
    // 2. Try to visit /dashboard
    // 3. Verify redirected to /login
    // 4. Verify returnUrl includes /dashboard
  });

  test('authentication token persists across page reloads', async () => {
    // 1. Login
    // 2. Navigate to /screener
    // 3. Reload page
    // 4. Verify still logged in
    // 5. Verify screener page still loads
  });

  test('expired token redirects to login', async () => {
    // 1. Login
    // 2. Mock expired token (modify localStorage)
    // 3. Navigate to protected route
    // 4. Verify redirected to login
    // 5. Verify error message shown
  });
});
```

### 3. Protected Routes (1h)

```typescript
describe('Protected Routes', () => {
  test('all main routes require authentication', async () => {
    const protectedRoutes = [
      '/dashboard',
      '/screener',
      '/watchlist',
      '/stock/AAPL'
    ];

    for (const route of protectedRoutes) {
      // 1. Ensure logged out
      // 2. Visit route
      // 3. Verify redirected to /login
    }
  });

  test('public routes accessible without auth', async () => {
    const publicRoutes = ['/login', '/signup', '/forgot-password'];

    for (const route of publicRoutes) {
      // 1. Ensure logged out
      // 2. Visit route
      // 3. Verify page loads without redirect
    }
  });

  test('logged in user redirected from login page', async () => {
    // 1. Login
    // 2. Try to visit /login
    // 3. Verify redirected to /dashboard
  });
});
```

### 4. Logout Flow (0.5h)

```typescript
describe('Logout Flow', () => {
  test('logout clears authentication and redirects', async () => {
    // 1. Login
    // 2. Navigate to /dashboard
    // 3. Click logout button
    // 4. Verify redirected to /login
    // 5. Try to visit /dashboard
    // 6. Verify redirected to /login again
  });

  test('logout clears local storage', async () => {
    // 1. Login
    // 2. Verify token in localStorage
    // 3. Logout
    // 4. Verify localStorage cleared
  });

  test('logout from any page redirects to login', async () => {
    // 1. Login
    // 2. Navigate to /screener
    // 3. Logout
    // 4. Verify redirected to /login
  });
});
```

## Acceptance Criteria

- [ ] Complete login flow tested (success and failure)
- [ ] Authentication state persistence tested (localStorage, page reloads)
- [ ] Protected routes tested (redirect to login when not authenticated)
- [ ] Public routes tested (accessible without authentication)
- [ ] Logout flow tested (clears state and redirects)
- [ ] Token expiration tested
- [ ] E2E test coverage for authentication reaches >85%
- [ ] All tests pass in CI/CD pipeline
- [ ] Tests run in headless mode for CI

## Dependencies

- Playwright or Cypress (E2E testing framework)
- Test database with seed data
- Backend server running (or mocked)
- Environment variables for test URLs

## Testing Strategy

1. **Full Stack Tests**: Test complete frontend + backend integration
2. **Real Browser**: Run in real browser environments (Chrome, Firefox)
3. **Database Cleanup**: Reset test database between tests
4. **Network Inspection**: Verify API calls and responses
5. **Visual Regression**: Screenshot comparison (optional)

## Related Files

- Test: `frontend/e2e/auth_flow.e2e.ts` (to be created)
- Pages: LoginPage, DashboardPage, ScreenerPage, etc.
- Auth: `frontend/src/hooks/useAuth.ts`
- API: `frontend/src/services/auth.ts`
- Backend: `backend/app/api/v1/endpoints/auth.py`

## Environment Setup

```bash
# Playwright example
npm install -D @playwright/test

# Cypress example
npm install -D cypress
```

## Test Data Requirements

```typescript
// Test user credentials
const testUser = {
  email: 'test@example.com',
  password: 'TestPassword123!',
  name: 'Test User'
};

// Invalid credentials for error testing
const invalidUser = {
  email: 'invalid@example.com',
  password: 'WrongPassword'
};
```

## Notes

- Run E2E tests against test environment, not production
- Use dedicated test database (reset between test runs)
- Test with both valid and invalid authentication
- Verify token storage and retrieval from localStorage
- Test keyboard navigation (Tab, Enter for login)
- Test accessibility (screen reader navigation)
- Consider visual regression testing for UI consistency
- Run in CI/CD pipeline with headless browser

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Run E2E Tests
  run: |
    npm run test:e2e
  env:
    VITE_API_URL: http://localhost:8000
    DATABASE_URL: postgresql://test:test@localhost:5432/screener_test
```

---

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #10
