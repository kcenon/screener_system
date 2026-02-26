/**
 * Design System Color Tokens
 *
 * Centralized color token system for consistent theming across light and dark modes.
 * These tokens provide semantic color names that automatically adapt to the active theme.
 *
 * @module design-system/tokens/colors
 */

/**
 * Color token structure for semantic color usage
 */
export const colorTokens = {
  /**
   * Background hierarchy
   * - primary: Main app background
   * - secondary: Section backgrounds
   * - tertiary: Nested component backgrounds
   * - elevated: Floating components (cards, modals)
   * - overlay: Backdrops and overlays
   */
  background: {
    primary: 'var(--bg-primary)',
    secondary: 'var(--bg-secondary)',
    tertiary: 'var(--bg-tertiary)',
    elevated: 'var(--bg-elevated)',
    overlay: 'var(--bg-overlay)',
  },

  /**
   * Text hierarchy
   * - primary: Headings, important text
   * - secondary: Body text, descriptions
   * - tertiary: Metadata, labels
   * - inverse: Text on dark backgrounds (e.g., buttons)
   * - disabled: Disabled state text
   */
  text: {
    primary: 'var(--text-primary)',
    secondary: 'var(--text-secondary)',
    tertiary: 'var(--text-tertiary)',
    inverse: 'var(--text-inverse)',
    disabled: 'var(--text-disabled)',
  },

  /**
   * Border colors
   * - default: Standard borders
   * - strong: Emphasized borders
   * - subtle: Dividers, low-emphasis separators
   */
  border: {
    default: 'var(--border-default)',
    strong: 'var(--border-strong)',
    subtle: 'var(--border-subtle)',
  },

  /**
   * Market-specific colors (semantic)
   * Automatically adjusted for dark mode
   */
  market: {
    gain: {
      text: 'var(--market-gain-text)',
      bg: 'var(--market-gain-bg)',
      border: 'var(--market-gain-border)',
    },
    loss: {
      text: 'var(--market-loss-text)',
      bg: 'var(--market-loss-bg)',
      border: 'var(--market-loss-border)',
    },
    neutral: {
      text: 'var(--market-neutral-text)',
      bg: 'var(--market-neutral-bg)',
      border: 'var(--market-neutral-border)',
    },
  },

  /**
   * Semantic colors for UI states
   * - success: Successful operations, confirmations
   * - warning: Cautions, non-critical issues
   * - danger: Errors, destructive actions
   * - info: Informational messages, tips
   */
  semantic: {
    success: {
      text: 'text-success',
      bg: 'bg-success',
      border: 'border-success',
    },
    warning: {
      text: 'text-warning',
      bg: 'bg-warning',
      border: 'border-warning',
    },
    danger: {
      text: 'text-danger',
      bg: 'bg-danger',
      border: 'border-danger',
    },
    info: {
      text: 'text-info',
      bg: 'bg-info',
      border: 'border-info',
    },
  },
} as const

/**
 * CSS Variables for Light Theme
 *
 * Applied when theme is 'light'
 */
export const cssVariablesLight = {
  // Backgrounds
  '--bg-primary': '#ffffff',
  '--bg-secondary': '#f9fafb',
  '--bg-tertiary': '#f3f4f6',
  '--bg-elevated': '#ffffff',
  '--bg-overlay': 'rgba(255, 255, 255, 0.95)',

  // Text
  '--text-primary': '#111827',
  '--text-secondary': '#6b7280',
  '--text-tertiary': '#9ca3af',
  '--text-inverse': '#ffffff',
  '--text-disabled': '#d1d5db',

  // Borders
  '--border-default': '#e5e7eb',
  '--border-strong': '#d1d5db',
  '--border-subtle': '#f3f4f6',

  // Market colors (light mode)
  '--market-gain-text': '#059669',
  '--market-gain-bg': '#ecfdf5',
  '--market-gain-border': '#a7f3d0',

  '--market-loss-text': '#dc2626',
  '--market-loss-bg': '#fef2f2',
  '--market-loss-border': '#fecaca',

  '--market-neutral-text': '#6b7280',
  '--market-neutral-bg': '#f9fafb',
  '--market-neutral-border': '#e5e7eb',
} as const

/**
 * CSS Variables for Dark Theme
 *
 * Applied when theme is 'dark'
 */
export const cssVariablesDark = {
  // Backgrounds
  '--bg-primary': '#111827',
  '--bg-secondary': '#1f2937',
  '--bg-tertiary': '#374151',
  '--bg-elevated': '#2d3748',
  '--bg-overlay': 'rgba(31, 41, 55, 0.95)',

  // Text
  '--text-primary': '#f3f4f6',
  '--text-secondary': '#9ca3af',
  '--text-tertiary': '#6b7280',
  '--text-inverse': '#111827',
  '--text-disabled': '#4b5563',

  // Borders
  '--border-default': '#374151',
  '--border-strong': '#4b5563',
  '--border-subtle': '#1f2937',

  // Market colors (dark mode - brighter for contrast)
  '--market-gain-text': '#34d399',
  '--market-gain-bg': 'rgba(16, 185, 129, 0.1)',
  '--market-gain-border': '#065f46',

  '--market-loss-text': '#f87171',
  '--market-loss-bg': 'rgba(239, 68, 68, 0.1)',
  '--market-loss-border': '#991b1b',

  '--market-neutral-text': '#9ca3af',
  '--market-neutral-bg': 'rgba(156, 163, 175, 0.1)',
  '--market-neutral-border': '#4b5563',
} as const

/**
 * Apply CSS variables to the document root
 *
 * @param theme - 'light' or 'dark'
 *
 * @example
 * applyCSSVariables('dark') // Applies dark theme variables
 */
export function applyCSSVariables(theme: 'light' | 'dark'): void {
  const variables = theme === 'light' ? cssVariablesLight : cssVariablesDark
  const root = document.documentElement

  Object.entries(variables).forEach(([key, value]) => {
    root.style.setProperty(key, value)
  })
}

/**
 * Initialize theme CSS variables
 *
 * Should be called on app initialization to set up CSS variables
 *
 * @param theme - Initial theme ('light' or 'dark')
 */
export function initializeCSSVariables(theme: 'light' | 'dark'): void {
  applyCSSVariables(theme)

  // Watch for theme changes
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      if (mutation.attributeName === 'class') {
        const classList = document.documentElement.classList
        const isDark = classList.contains('dark')
        applyCSSVariables(isDark ? 'dark' : 'light')
      }
    })
  })

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class'],
  })
}

/**
 * Type exports for TypeScript autocomplete
 */
export type ColorTokenKey = keyof typeof colorTokens
export type CSSVariableKey = keyof typeof cssVariablesLight
