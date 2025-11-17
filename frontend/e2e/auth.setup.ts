/**
 * Authentication Setup for E2E Tests
 *
 * This file provides helper functions and setup utilities for authentication testing.
 */

import { test as setup } from '@playwright/test';
import { validTestUser } from './fixtures/test-users';

const authFile = '.auth/user.json';

/**
 * Setup: Authenticate and save state
 *
 * This runs once before all tests and saves the authenticated state.
 * Other tests can reuse this state to skip login.
 */
setup('authenticate', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');

  // Fill in login form
  await page.fill('#email', validTestUser.email);
  await page.fill('#password', validTestUser.password);

  // Submit form
  await page.click('button[type="submit"]');

  // Wait for navigation to complete
  await page.waitForURL(/dashboard|screener/);

  // Save signed-in state
  await page.context().storageState({ path: authFile });
});

export { authFile };
