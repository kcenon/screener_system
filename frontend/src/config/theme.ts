/**
 * Global Theme Configuration
 *
 * Centralized color system, typography, and spacing definitions
 * for consistent UI/UX across the application.
 *
 * Based on international market conventions:
 * - Green: Positive price movements (up)
 * - Red: Negative price movements (down)
 * - Gray: Neutral/no change
 */

/**
 * Market color system
 *
 * Provides consistent colors for price movements and market sentiment
 */
export const marketColors = {
  /**
   * Positive price movement (up)
   * Color: Green (international standard)
   */
  positive: {
    text: 'text-green-600',
    bg: 'bg-green-50',
    border: 'border-green-200',
    hover: 'hover:bg-green-100',
    hex: '#16a34a',
  },

  /**
   * Negative price movement (down)
   * Color: Red (international standard)
   */
  negative: {
    text: 'text-red-600',
    bg: 'bg-red-50',
    border: 'border-red-200',
    hover: 'hover:bg-red-100',
    hex: '#dc2626',
  },

  /**
   * Neutral (no change)
   * Color: Gray
   */
  neutral: {
    text: 'text-gray-600',
    bg: 'bg-gray-50',
    border: 'border-gray-200',
    hover: 'hover:bg-gray-100',
    icon: '➡️',
    hex: '#6b7280',
  },

  /**
   * Bullish market sentiment
   * Color: Emerald green
   */
  bullish: {
    text: 'text-emerald-700',
    bg: 'bg-emerald-100',
    border: 'border-emerald-300',
    icon: '🐂',
    hex: '#059669',
  },

  /**
   * Bearish market sentiment
   * Color: Rose red
   */
  bearish: {
    text: 'text-rose-700',
    bg: 'bg-rose-100',
    border: 'border-rose-300',
    icon: '🐻',
    hex: '#e11d48',
  },
} as const

/**
 * Typography scale
 *
 * Compact font sizes for higher information density
 */
export const typography = {
  h1: 'text-xl font-bold', // 20px (reduced from 24px)
  h2: 'text-base font-semibold', // 16px (reduced from 20px)
  h3: 'text-sm font-semibold', // 14px (reduced from 16px)
  body: 'text-sm', // 14px (reduced from 16px)
  small: 'text-xs', // 12px
} as const

/**
 * Spacing scale
 *
 * Consistent spacing values across components
 */
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
} as const

/**
 * Component spacing presets
 *
 * Standardized padding/margin for compact layout
 */
export const componentSpacing = {
  /**
   * Widget/Card padding
   * Reduced from p-6 (24px) to p-4 (16px)
   */
  widget: 'p-4',

  /**
   * Card internal spacing
   * Reduced from space-y-6 to space-y-3
   */
  cardStack: 'space-y-3',

  /**
   * Table cell padding
   * Reduced from px-4 py-3 to px-3 py-2
   */
  tableCell: 'px-3 py-2',

  /**
   * Table row height
   * Reduced from h-12 (48px) to h-9 (36px)
   */
  tableRow: 'h-9',
} as const

/**
 * Color utility function
 *
 * Get market color based on value change
 *
 * @param value - Change value (positive, negative, or zero)
 * @returns Color configuration object
 *
 * @example
 * const color = getMarketColor(5.2) // positive
 * console.log(color.text) // 'text-green-600'
 */
export function getMarketColor(value: number | null | undefined) {
  if (value === null || value === undefined || isNaN(value)) {
    return marketColors.neutral
  }

  if (value > 0) {
    return marketColors.positive
  } else if (value < 0) {
    return marketColors.negative
  } else {
    return marketColors.neutral
  }
}

/**
 * Sentiment utility function
 *
 * Get market sentiment color based on sentiment value
 *
 * @param sentiment - Sentiment indicator (-1 to 1, or categorical string)
 * @returns Color configuration object
 *
 * @example
 * const color = getMarketSentiment(0.7) // bullish
 * console.log(color.icon) // '🐂'
 */
export function getMarketSentiment(sentiment: number | 'bullish' | 'bearish' | 'neutral') {
  if (typeof sentiment === 'string') {
    if (sentiment === 'bullish') return marketColors.bullish
    if (sentiment === 'bearish') return marketColors.bearish
    return marketColors.neutral
  }

  // Numeric sentiment: > 0.3 = bullish, < -0.3 = bearish, else neutral
  if (sentiment > 0.3) {
    return marketColors.bullish
  } else if (sentiment < -0.3) {
    return marketColors.bearish
  } else {
    return marketColors.neutral
  }
}

/**
 * Direction arrow icon
 *
 * Get arrow icon based on value change
 *
 * @param value - Change value
 * @returns Arrow character (↑, ↓, or →)
 *
 * @example
 * const arrow = getChangeArrow(5.2) // '↑'
 */
export function getChangeArrow(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '→'
  }

  if (value > 0) {
    return '▲'
  } else if (value < 0) {
    return '▼'
  } else {
    return '→'
  }
}

/**
 * Type exports for TypeScript autocomplete
 */
export type MarketColorKey = keyof typeof marketColors
export type TypographyKey = keyof typeof typography
export type SpacingKey = keyof typeof spacing
export type ComponentSpacingKey = keyof typeof componentSpacing
