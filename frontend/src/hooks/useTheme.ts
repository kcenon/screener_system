/**
 * Theme Management Hook
 *
 * Manages dark/light theme preferences with:
 * - System preference detection
 * - Manual theme override
 * - Persistent storage (localStorage)
 * - Automatic DOM updates
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * Theme preference type
 *
 * - 'light': Force light mode
 * - 'dark': Force dark mode
 * - 'system': Follow system preference
 */
type Theme = 'light' | 'dark' | 'system'

/**
 * Resolved theme type (actual theme being used)
 */
type ResolvedTheme = 'light' | 'dark'

/**
 * Theme store state
 */
interface ThemeStore {
  /**
   * User's theme preference
   */
  theme: Theme

  /**
   * Actual theme being used (resolved from system if theme === 'system')
   */
  resolvedTheme: ResolvedTheme

  /**
   * Set theme preference
   *
   * @param theme - Theme to set ('light', 'dark', or 'system')
   */
  setTheme: (theme: Theme) => void

  /**
   * Initialize theme on mount
   * Called automatically by the hook
   */
  initTheme: () => void
}

/**
 * Get system color scheme preference
 *
 * @returns 'dark' if system prefers dark mode, 'light' otherwise
 */
function getSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') return 'light'

  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

/**
 * Resolve theme based on user preference
 *
 * @param theme - User's theme preference
 * @returns Actual theme to use
 */
function resolveTheme(theme: Theme): ResolvedTheme {
  if (theme === 'system') {
    return getSystemTheme()
  }
  return theme
}

/**
 * Apply theme to DOM
 *
 * Updates document.documentElement.classList to enable Tailwind dark mode
 *
 * @param resolvedTheme - Theme to apply
 */
function applyTheme(resolvedTheme: ResolvedTheme): void {
  const root = document.documentElement

  // Remove both classes first
  root.classList.remove('light', 'dark')

  // Add the resolved theme class
  root.classList.add(resolvedTheme)
}

/**
 * Theme store using Zustand with persistence
 *
 * Automatically saves theme preference to localStorage
 */
export const useTheme = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: 'system',
      resolvedTheme: 'light',

      setTheme: theme => {
        const resolved = resolveTheme(theme)

        set({ theme, resolvedTheme: resolved })
        applyTheme(resolved)
      },

      initTheme: () => {
        const { theme } = get()
        const resolved = resolveTheme(theme)

        set({ resolvedTheme: resolved })
        applyTheme(resolved)

        // Listen for system theme changes (only if theme === 'system')
        if (typeof window !== 'undefined' && theme === 'system') {
          const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

          const listener = (e: MediaQueryListEvent) => {
            const newResolved = e.matches ? 'dark' : 'light'
            set({ resolvedTheme: newResolved })
            applyTheme(newResolved)
          }

          mediaQuery.addEventListener('change', listener)

          // Cleanup function (though Zustand doesn't call it)
          return () => mediaQuery.removeEventListener('change', listener)
        }
      },
    }),
    {
      name: 'theme-preference', // localStorage key
      // Only persist the 'theme' preference, not resolvedTheme
      partialize: state => ({ theme: state.theme }),
    },
  ),
)

/**
 * Initialize theme on app mount
 *
 * Call this in your main App component:
 *
 * @example
 * ```tsx
 * function App() {
 *   useEffect(() => {
 *     useTheme.getState().initTheme()
 *   }, [])
 *
 *   return <YourApp />
 * }
 * ```
 */
export function initializeTheme() {
  useTheme.getState().initTheme()
}
