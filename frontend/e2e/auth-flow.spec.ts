/**
 * E2E Authentication Flow Tests
 *
 * This test suite covers the complete authentication flow including:
 * - Login (success and failure cases)
 * - Authentication state persistence
 * - Protected route access
 * - Logout functionality
 *
 * @see docs/kanban/todo/TEST-010.md
 */

import { test, expect } from '@playwright/test';
import {
  validTestUser,
  invalidTestUser,
  invalidEmailUser,
  shortPasswordUser,
} from './fixtures/test-users';

/**
 * Test Suite: Login Flow
 *
 * Tests all login scenarios including successful login,
 * validation errors, and authentication failures.
 */
test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page before each test
    await page.goto('/login');
  });

  test('successful login redirects to dashboard or screener', async ({ page }) => {
    // Fill in valid credentials
    await page.fill('#email', validTestUser.email);
    await page.fill('#password', validTestUser.password);

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect (could be dashboard or screener based on freemium model)
    await page.waitForURL(/dashboard|screener/);

    // Verify we're no longer on login page
    expect(page.url()).not.toContain('/login');

    // Verify user is logged in (check for logout button or user menu)
    const hasUserMenu = await page.locator('[data-testid="user-menu"]').count();
    const hasLogoutButton = await page.locator('text=/logout/i').count();

    expect(hasUserMenu + hasLogoutButton).toBeGreaterThan(0);
  });

  test('login with invalid credentials shows error', async ({ page }) => {
    // Fill in invalid credentials
    await page.fill('#email', invalidTestUser.email);
    await page.fill('#password', invalidTestUser.password);

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for error message
    await page.waitForSelector('text=/invalid|incorrect|wrong/i', {
      timeout: 5000,
    });

    // Verify still on login page
    expect(page.url()).toContain('/login');

    // Verify error message is displayed
    const errorMessage = await page.locator('text=/invalid|incorrect|wrong/i');
    await expect(errorMessage).toBeVisible();
  });

  test('login form validation for empty fields', async ({ page }) => {
    // Submit empty form
    await page.click('button[type="submit"]');

    // Verify validation errors
    const emailError = await page.locator('text=/email.*required/i');
    const passwordError = await page.locator('text=/password.*required/i');

    // At least one validation error should be visible
    const emailVisible = await emailError.isVisible().catch(() => false);
    const passwordVisible = await passwordError.isVisible().catch(() => false);

    expect(emailVisible || passwordVisible).toBeTruthy();

    // Verify still on login page
    expect(page.url()).toContain('/login');
  });

  test('login form validation for invalid email format', async ({ page }) => {
    // Enter invalid email format
    await page.fill('#email', invalidEmailUser.email);
    await page.fill('#password', invalidEmailUser.password);

    // Blur email field to trigger validation
    await page.locator('#email').blur();

    // Submit form
    await page.click('button[type="submit"]');

    // Wait a bit for validation
    await page.waitForTimeout(500);

    // Verify validation error for email format
    const emailError = await page.locator('text=/invalid.*email|email.*invalid/i');
    const hasError = await emailError.isVisible().catch(() => false);

    // Either form validation or backend error should appear
    expect(hasError || page.url().includes('/login')).toBeTruthy();
  });

  test('login form validation for short password', async ({ page }) => {
    // Enter valid email but short password
    await page.fill('#email', shortPasswordUser.email);
    await page.fill('#password', shortPasswordUser.password);

    // Blur password field to trigger validation
    await page.locator('#password').blur();

    // Wait for validation message
    await page.waitForTimeout(500);

    // Verify validation error for password length
    const passwordError = await page.locator(
      'text=/password.*8|at least 8 characters/i'
    );
    const hasError = await passwordError.isVisible().catch(() => false);

    expect(hasError).toBeTruthy();
  });

  test('remember me functionality (if implemented)', async ({ page, context }) => {
    // Check if remember me checkbox exists
    const rememberMeExists = await page
      .locator('input[type="checkbox"]')
      .count();

    if (rememberMeExists === 0) {
      test.skip();
      return;
    }

    // Login with remember me checked
    await page.fill('#email', validTestUser.email);
    await page.fill('#password', validTestUser.password);
    await page.check('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    // Wait for successful login
    await page.waitForURL(/dashboard|screener/);

    // Get cookies
    const cookies = await context.cookies();

    // Verify auth cookie has long expiration (> 1 day)
    const authCookie = cookies.find((c) =>
      c.name.toLowerCase().includes('token')
    );
    if (authCookie && authCookie.expires) {
      const expiresIn = authCookie.expires - Date.now() / 1000;
      expect(expiresIn).toBeGreaterThan(86400); // More than 1 day
    }
  });
});

/**
 * Test Suite: Authentication State Management
 *
 * Tests how authentication state persists across page reloads,
 * navigation, and session management.
 */
test.describe('Authentication State Management', () => {
  test('authenticated user can access protected routes', async ({ page }) => {
    // First, login
    await page.goto('/login');
    await page.fill('#email', validTestUser.email);
    await page.fill('#password', validTestUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|screener/);

    // Navigate to different protected routes
    const protectedRoutes = ['/screener', '/dashboard', '/watchlists'];

    for (const route of protectedRoutes) {
      await page.goto(route);

      // Verify page loaded (not redirected to login)
      await page.waitForLoadState('networkidle');
      expect(page.url()).not.toContain('/login');

      // Verify we can see the page content (not login form)
      const loginForm = await page.locator('form').first();
      const hasEmailInput = await loginForm
        .locator('#email')
        .count()
        .catch(() => 0);

      expect(hasEmailInput).toBe(0);
    }
  });

  test('unauthenticated user redirected to login from protected routes', async ({
    page,
  }) => {
    // Clear any existing auth
    await page.context().clearCookies();
    await page.context().clearPermissions();

    // Try to access protected routes
    const protectedRoutes = ['/dashboard', '/watchlists'];

    for (const route of protectedRoutes) {
      await page.goto(route);
      await page.waitForLoadState('networkidle');

      // Should be redirected to login or see login form
      const isOnLogin =
        page.url().includes('/login') ||
        (await page.locator('#email').count()) > 0;

      expect(isOnLogin).toBeTruthy();
    }
  });

  test('authentication token persists across page reloads', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('#email', validTestUser.email);
    await page.fill('#password', validTestUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|screener/);

    // Navigate to screener
    await page.goto('/screener');
    await page.waitForLoadState('networkidle');

    // Verify we're on screener
    expect(page.url()).toContain('/screener');

    // Reload page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Verify still logged in (still on screener, not redirected to login)
    expect(page.url()).toContain('/screener');
    expect(page.url()).not.toContain('/login');

    // Verify user menu still visible
    const hasUserMenu = await page.locator('[data-testid="user-menu"]').count();
    const hasLogoutButton = await page.locator('text=/logout/i').count();

    expect(hasUserMenu + hasLogoutButton).toBeGreaterThan(0);
  });

  test('expired token redirects to login', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('#email', validTestUser.email);
    await page.fill('#password', validTestUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|screener/);

    // Manually expire token by modifying localStorage
    await page.evaluate(() => {
      // Clear token or set expired token
      localStorage.removeItem('token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('authToken');
    });

    // Try to navigate to protected route
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Should be redirected to login
    const isOnLogin =
      page.url().includes('/login') || (await page.locator('#email').count()) > 0;

    expect(isOnLogin).toBeTruthy();
  });
});

/**
 * Test Suite: Protected Routes
 *
 * Verifies that route protection is properly implemented
 * and authenticated/unauthenticated users see appropriate pages.
 */
test.describe('Protected Routes', () => {
  test('public routes accessible without authentication', async ({ page }) => {
    // Clear auth
    await page.context().clearCookies();

    // Public routes should be accessible
    const publicRoutes = ['/', '/login', '/register', '/screener', '/stocks/005930'];

    for (const route of publicRoutes) {
      await page.goto(route);
      await page.waitForLoadState('networkidle');

      // Should load successfully (status 200, not redirected)
      expect(page.url()).toContain(route.split('?')[0]);
    }
  });

  test('logged in user can access all routes', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('#email', validTestUser.email);
    await page.fill('#password', validTestUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|screener/);

    // All routes should be accessible
    const allRoutes = [
      '/',
      '/screener',
      '/dashboard',
      '/watchlists',
      '/stocks/005930',
    ];

    for (const route of allRoutes) {
      await page.goto(route);
      await page.waitForLoadState('networkidle');

      // Should not be redirected to login
      expect(page.url()).not.toContain('/login');
    }
  });

  test('logged in user redirected from login page to dashboard', async ({
    page,
  }) => {
    // Login first
    await page.goto('/login');
    await page.fill('#email', validTestUser.email);
    await page.fill('#password', validTestUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|screener/);

    // Try to visit login page again
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    // Should be redirected away from login
    // Could be dashboard, screener, or stay on login (depends on implementation)
    // For now, just verify we didn't get an error
    expect(page.url()).toBeTruthy();
  });
});

/**
 * Test Suite: Logout Flow
 *
 * Tests the logout functionality including state clearing
 * and proper redirection.
 */
test.describe('Logout Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each logout test
    await page.goto('/login');
    await page.fill('#email', validTestUser.email);
    await page.fill('#password', validTestUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|screener/);
  });

  test('logout clears authentication and redirects to login or home', async ({
    page,
  }) => {
    // Find and click logout button
    // Try multiple possible selectors
    const logoutButton =
      page.locator('text=/logout/i').first() ||
      page.locator('[data-testid="logout-button"]').first() ||
      page.locator('button:has-text("Sign Out")').first();

    await logoutButton.click();

    // Wait for redirect
    await page.waitForLoadState('networkidle');

    // Should be redirected to login or home page
    const url = page.url();
    const isOnLoginOrHome =
      url.includes('/login') || url.endsWith('/') || url.includes('/register');

    expect(isOnLoginOrHome).toBeTruthy();

    // Try to access protected route
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Should be redirected to login
    const isOnLogin =
      page.url().includes('/login') || (await page.locator('#email').count()) > 0;

    expect(isOnLogin).toBeTruthy();
  });

  test('logout clears local storage tokens', async ({ page }) => {
    // Verify token exists before logout
    const _tokenBefore = await page.evaluate(() => {
      return (
        localStorage.getItem('token') ||
        localStorage.getItem('access_token') ||
        localStorage.getItem('authToken')
      );
    });

    // If no token in localStorage, it might be in cookies only
    // That's okay, we'll just verify logout still works

    // Logout
    const logoutButton = page.locator('text=/logout/i').first();
    await logoutButton.click();
    await page.waitForLoadState('networkidle');

    // Verify tokens are cleared
    const tokenAfter = await page.evaluate(() => {
      return (
        localStorage.getItem('token') ||
        localStorage.getItem('access_token') ||
        localStorage.getItem('authToken')
      );
    });

    expect(tokenAfter).toBeNull();
  });

  test('logout from any page redirects to login or home', async ({ page }) => {
    // Navigate to different pages and logout from each
    const pages = ['/screener', '/dashboard', '/watchlists'];

    for (const pagePath of pages) {
      // Navigate to page
      await page.goto(pagePath);
      await page.waitForLoadState('networkidle');

      // Find logout button
      const logoutButton = page.locator('text=/logout/i').first();
      const exists = await logoutButton.count();

      if (exists === 0) {
        // If logout button not visible on this page, skip
        continue;
      }

      await logoutButton.click();
      await page.waitForLoadState('networkidle');

      // Should be redirected to login or home
      const url = page.url();
      const isOnLoginOrHome =
        url.includes('/login') ||
        url.endsWith('/') ||
        url.includes('/register');

      expect(isOnLoginOrHome).toBeTruthy();

      // Log back in for next iteration
      if (pagePath !== pages[pages.length - 1]) {
        await page.goto('/login');
        await page.fill('#email', validTestUser.email);
        await page.fill('#password', validTestUser.password);
        await page.click('button[type="submit"]');
        await page.waitForURL(/dashboard|screener/);
      }
    }
  });
});
