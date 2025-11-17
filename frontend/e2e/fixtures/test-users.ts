/**
 * Test User Fixtures
 *
 * Provides test user credentials and data for E2E testing.
 * These users should exist in the test database.
 */

export interface TestUser {
  email: string;
  password: string;
  name: string;
}

/**
 * Valid test user with correct credentials
 */
export const validTestUser: TestUser = {
  email: 'test@example.com',
  password: 'TestPassword123!',
  name: 'Test User',
};

/**
 * Invalid test user with incorrect credentials
 */
export const invalidTestUser: TestUser = {
  email: 'invalid@example.com',
  password: 'WrongPassword123!',
  name: 'Invalid User',
};

/**
 * Test user with invalid email format
 */
export const invalidEmailUser = {
  email: 'invalid-email',
  password: 'ValidPassword123!',
};

/**
 * Test user with short password
 */
export const shortPasswordUser = {
  email: 'test@example.com',
  password: 'short',
};
