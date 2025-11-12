/**
 * Authentication State Management Store.
 *
 * Zustand-based store managing user authentication state including user profile,
 * JWT tokens, and authentication status. Includes automatic persistence to
 * localStorage for maintaining login state across sessions.
 *
 * @module store/authStore
 * @category Store
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { authService } from '@/services/authService'

/**
 * Authentication store state and actions.
 *
 * Manages user authentication lifecycle including login, logout, token
 * management, and persistence. Automatically syncs with localStorage
 * to maintain auth state across page refreshes.
 *
 * @interface
 * @category Types
 */
interface AuthState {
  /**
   * Currently authenticated user profile.
   * Null when user is not logged in.
   */
  user: User | null

  /**
   * JWT access token for API authentication.
   * Short-lived token for authorizing requests.
   */
  accessToken: string | null

  /**
   * JWT refresh token for obtaining new access tokens.
   * Long-lived token stored securely in localStorage.
   */
  refreshToken: string | null

  /**
   * Whether user is currently authenticated.
   * True if user is logged in with valid tokens.
   */
  isAuthenticated: boolean

  /**
   * Logs user in and stores authentication credentials.
   *
   * Stores tokens in localStorage and updates auth state.
   * Should be called after successful login API call.
   *
   * @param user - Authenticated user profile
   * @param accessToken - JWT access token from server
   * @param refreshToken - JWT refresh token from server
   *
   * @example
   * ```typescript
   * const { login } = useAuthStore();
   * const response = await authService.login(email, password);
   * login(response.user, response.access_token, response.refresh_token);
   * ```
   */
  login: (user: User, accessToken: string, refreshToken: string) => void

  /**
   * Logs user out and clears authentication state.
   *
   * Removes tokens from localStorage and resets auth state to defaults.
   * Triggers navigation to login page.
   *
   * @example
   * ```typescript
   * const { logout } = useAuthStore();
   * logout();
   * navigate('/login');
   * ```
   */
  logout: () => void

  /**
   * Updates user profile without affecting tokens.
   *
   * Useful for updating user information after profile edits.
   *
   * @param user - Updated user profile or null to clear
   */
  setUser: (user: User | null) => void

  /**
   * Updates stored tokens without changing user profile.
   *
   * Called automatically by token refresh interceptor when access
   * token expires and is renewed.
   *
   * @param accessToken - New access token
   * @param refreshToken - New refresh token
   *
   * @internal
   */
  updateTokens: (accessToken: string, refreshToken: string) => void
}

/**
 * Global authentication store hook.
 *
 * Provides access to authentication state and actions throughout the application.
 * Uses Zustand for simple, performant state management with automatic persistence.
 *
 * ## Features
 *
 * - **Persistent Storage**: Auth state persists across page refreshes
 * - **Token Management**: Automatic token storage and retrieval
 * - **Type Safety**: Full TypeScript support
 * - **Reactive Updates**: Components re-render on auth state changes
 *
 * @example
 * Access auth state
 * ```typescript
 * const { user, isAuthenticated } = useAuthStore();
 *
 * if (!isAuthenticated) {
 *   return <Navigate to="/login" />;
 * }
 *
 * return <div>Welcome, {user.username}!</div>;
 * ```
 *
 * @example
 * Use auth actions
 * ```typescript
 * const { login, logout } = useAuthStore();
 *
 * const handleLogin = async (email, password) => {
 *   const response = await authService.login(email, password);
 *   login(response.user, response.access_token, response.refresh_token);
 * };
 * ```
 *
 * @example
 * Selective subscription (performance optimization)
 * ```typescript
 * // Only re-render when isAuthenticated changes
 * const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
 * ```
 *
 * @returns Authentication store state and actions
 *
 * @see {@link User} for user profile structure
 * @see {@link authService} for authentication API calls
 *
 * @category Store
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: (user, accessToken, refreshToken) => {
        // Store tokens in localStorage
        authService.storeTokens(accessToken, refreshToken)
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
        })
      },

      logout: () => {
        // Clear tokens from localStorage
        authService.clearTokens()
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      setUser: (user) => set({ user }),

      updateTokens: (accessToken, refreshToken) => {
        // Update tokens in localStorage
        authService.storeTokens(accessToken, refreshToken)
        set({ accessToken, refreshToken })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
