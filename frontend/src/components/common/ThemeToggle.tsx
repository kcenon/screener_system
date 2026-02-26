/**
 * Theme Toggle Component
 *
 * Allows users to switch between light, dark, and system theme preferences.
 *
 * Features:
 * - Three options: Light, Dark, System
 * - Visual feedback for current selection
 * - Keyboard accessible
 * - Persists preference to localStorage
 *
 * @example
 * ```tsx
 * <ThemeToggle />
 * ```
 */

import { Moon, Sun, Monitor } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'

/**
 * Theme toggle button group
 *
 * Displays three buttons for light, system, and dark mode selection
 */
export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg transition-colors">
      {/* Light mode button */}
      <button
        onClick={() => setTheme('light')}
        className={`
          p-2 rounded transition-all
          ${
            theme === 'light'
              ? 'bg-white dark:bg-gray-700 shadow text-yellow-600'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
          }
        `}
        aria-label="Switch to light mode"
        title="Light mode"
      >
        <Sun className="w-4 h-4" />
      </button>

      {/* System preference button */}
      <button
        onClick={() => setTheme('system')}
        className={`
          p-2 rounded transition-all
          ${
            theme === 'system'
              ? 'bg-white dark:bg-gray-700 shadow text-blue-600'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
          }
        `}
        aria-label="Use system theme"
        title="System theme"
      >
        <Monitor className="w-4 h-4" />
      </button>

      {/* Dark mode button */}
      <button
        onClick={() => setTheme('dark')}
        className={`
          p-2 rounded transition-all
          ${
            theme === 'dark'
              ? 'bg-white dark:bg-gray-700 shadow text-indigo-600'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
          }
        `}
        aria-label="Switch to dark mode"
        title="Dark mode"
      >
        <Moon className="w-4 h-4" />
      </button>
    </div>
  )
}

/**
 * Compact theme toggle (icon only, cycles through themes)
 *
 * Single button that cycles: light → dark → system
 *
 * @example
 * ```tsx
 * <CompactThemeToggle />
 * ```
 */
export function CompactThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme()

  const cycleTheme = () => {
    if (theme === 'light') setTheme('dark')
    else if (theme === 'dark') setTheme('system')
    else setTheme('light')
  }

  const Icon =
    theme === 'system' ? Monitor : resolvedTheme === 'dark' ? Moon : Sun

  return (
    <button
      onClick={cycleTheme}
      className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      aria-label={`Current theme: ${theme}. Click to cycle.`}
      title={`Theme: ${theme}`}
    >
      <Icon className="w-5 h-5 text-gray-700 dark:text-gray-300" />
    </button>
  )
}
