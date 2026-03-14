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

/**
 * Authentication store state and actions.
 *
 * Manages user authentication state. JWT tokens are stored in HttpOnly
 * cookies by the backend — this store only tracks the user profile and
 * authentication status.
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
   * Whether user is currently authenticated.
   * True if user is logged in with valid session cookies.
   */
  isAuthenticated: boolean

  /**
   * Logs user in and stores user profile.
   *
   * Tokens are handled via HttpOnly cookies set by the backend.
   *
   * @param user - Authenticated user profile
   *
   * @example
   * ```typescript
   * const { login } = useAuthStore();
   * const response = await authService.login(email, password);
   * login(response.user);
   * ```
   */
  login: (user: User) => void

  /**
   * Logs user out and clears authentication state.
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
   * Updates user profile without affecting authentication status.
   *
   * @param user - Updated user profile or null to clear
   */
  setUser: (user: User | null) => void
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
    set => ({
      user: null,
      isAuthenticated: false,

      login: user => {
        // Tokens are managed via HttpOnly cookies by the backend
        set({ user, isAuthenticated: true })
      },

      logout: () => {
        set({ user: null, isAuthenticated: false })
      },

      setUser: user => set({ user }),
    }),
    {
      name: 'auth-storage',
    },
  ),
)
