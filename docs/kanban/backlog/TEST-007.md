# TEST-007: LoginPage Component Tests

**Type**: TEST
**Priority**: P0
**Status**: TODO
**Created**: 2025-11-16
**Effort**: 3 hours
**Phase**: Phase 1 - Critical Tests

---

## Description

Implement comprehensive tests for the LoginPage component. This is the entry point to the application and critical for user authentication flow.

## Current Status

- **Test File**: `frontend/src/pages/LoginPage.test.tsx` does not exist
- **Component**: `frontend/src/pages/LoginPage.tsx` (exists, untested)
- **Coverage Impact**: Critical authentication UI with 0% test coverage

## Test Requirements

### 1. Component Rendering (0.5h)

```typescript
describe('LoginPage Rendering', () => {
  test('renders login form', () => {
    // Test form elements are present
  });

  test('renders email input field', () => {
    // Test email input exists with correct attributes
  });

  test('renders password input field', () => {
    // Test password input exists with type="password"
  });

  test('renders login button', () => {
    // Test login button is present
  });

  test('renders "Forgot Password" link', () => {
    // Test forgot password link exists
  });

  test('renders "Sign Up" link', () => {
    // Test sign up link exists
  });
});
```

### 2. Form Submission (1h)

```typescript
describe('LoginPage Form Submission', () => {
  test('submits form with valid credentials', async () => {
    // Test successful login flow
  });

  test('calls login API with correct data', async () => {
    // Test API called with email and password
  });

  test('disables submit button during submission', async () => {
    // Test button disabled while loading
  });

  test('shows loading indicator during submission', async () => {
    // Test loading state displayed
  });

  test('clears password field on submission error', async () => {
    // Test password cleared for security
  });
});
```

### 3. Error Handling (1h)

```typescript
describe('LoginPage Error Handling', () => {
  test('shows error for invalid credentials', async () => {
    // Test error message displayed for 401
  });

  test('shows error for network failure', async () => {
    // Test error handling for network errors
  });

  test('validates email format', async () => {
    // Test email validation feedback
  });

  test('validates password is not empty', async () => {
    // Test password required validation
  });

  test('shows field-specific error messages', async () => {
    // Test validation errors per field
  });

  test('clears errors when user starts typing', async () => {
    // Test errors cleared on input change
  });
});
```

### 4. Redirect After Login (0.5h)

```typescript
describe('LoginPage Navigation', () => {
  test('redirects to dashboard on successful login', async () => {
    // Test navigation to /dashboard
  });

  test('redirects to intended page if redirected to login', async () => {
    // Test returnUrl functionality
  });

  test('redirects to dashboard if already logged in', () => {
    // Test redirect when user already authenticated
  });

  test('navigates to sign up page', async () => {
    // Test sign up link navigation
  });

  test('navigates to forgot password page', async () => {
    // Test forgot password link navigation
  });
});
```

## Acceptance Criteria

- [ ] All rendering tests pass (form elements present)
- [ ] Form submission tested (success and loading states)
- [ ] Error handling tested (validation, API errors, network errors)
- [ ] Navigation tested (redirect after login, sign up, forgot password)
- [ ] Accessibility tested (keyboard navigation, screen reader labels)
- [ ] Test coverage for LoginPage reaches >85%
- [ ] All tests pass in CI/CD pipeline

## Dependencies

- @testing-library/react
- @testing-library/user-event
- @testing-library/jest-dom
- MSW (Mock Service Worker) for API mocking
- React Router (for navigation testing)

## Testing Strategy

1. **Component Tests**: Render and interaction tests
2. **Integration Tests**: Test with mocked API responses
3. **User Event Tests**: Simulate real user interactions
4. **Accessibility Tests**: Verify ARIA labels and keyboard navigation

## Related Files

- Component: `frontend/src/pages/LoginPage.tsx`
- Test: `frontend/src/pages/LoginPage.test.tsx` (to be created)
- Hook: `frontend/src/hooks/useAuth.ts`
- API: `frontend/src/services/auth.ts`

## Mock Data Requirements

```typescript
// Mock successful login response
const mockLoginSuccess = {
  access_token: 'mock-jwt-token',
  token_type: 'bearer',
  user: {
    id: 1,
    email: 'test@example.com',
    name: 'Test User'
  }
};

// Mock error responses
const mockLoginError401 = {
  detail: 'Invalid credentials'
};
```

## Notes

- Use MSW to mock authentication API
- Test keyboard accessibility (Tab, Enter key)
- Verify password field is type="password" (hidden)
- Test remember me checkbox if implemented
- Test OAuth login buttons if implemented
- Verify security: password not stored in state after error

---

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #7
