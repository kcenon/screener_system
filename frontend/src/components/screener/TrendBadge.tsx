import { memo, useMemo } from 'react'

/**
 * Trend strength levels
 */
export type TrendStrength =
  | 'strong_up'
  | 'up'
  | 'neutral'
  | 'down'
  | 'strong_down'

/**
 * Props for TrendBadge component
 */
export interface TrendBadgeProps {
  /** Short-term price change percentage (e.g., 1 week) */
  shortTermChange?: number | null
  /** Long-term price change percentage (e.g., 1 month) */
  longTermChange?: number | null
  /** Or provide explicit trend strength */
  trend?: TrendStrength
  /** Show label text */
  showLabel?: boolean
  /** Size variant */
  size?: 'sm' | 'md'
  /** CSS class name */
  className?: string
}

/**
 * Trend configuration with visual properties
 */
interface TrendConfig {
  icon: string
  label: string
  bgColor: string
  textColor: string
  ariaLabel: string
}

/**
 * Trend configurations map
 */
const TREND_CONFIGS: Record<TrendStrength, TrendConfig> = {
  strong_up: {
    icon: '↗',
    label: 'Strong',
    bgColor: 'bg-green-100 dark:bg-green-900/50',
    textColor: 'text-green-700 dark:text-green-300',
    ariaLabel: 'Strong upward trend',
  },
  up: {
    icon: '↑',
    label: 'Up',
    bgColor: 'bg-green-50 dark:bg-green-900/30',
    textColor: 'text-green-600 dark:text-green-400',
    ariaLabel: 'Upward trend',
  },
  neutral: {
    icon: '→',
    label: 'Flat',
    bgColor: 'bg-gray-100 dark:bg-gray-800',
    textColor: 'text-gray-600 dark:text-gray-400',
    ariaLabel: 'Neutral trend',
  },
  down: {
    icon: '↓',
    label: 'Down',
    bgColor: 'bg-red-50 dark:bg-red-900/30',
    textColor: 'text-red-600 dark:text-red-400',
    ariaLabel: 'Downward trend',
  },
  strong_down: {
    icon: '↘',
    label: 'Weak',
    bgColor: 'bg-red-100 dark:bg-red-900/50',
    textColor: 'text-red-700 dark:text-red-300',
    ariaLabel: 'Strong downward trend',
  },
}

/**
 * Calculate trend strength from price changes
 * Uses a combination of short-term and long-term momentum
 */
function calculateTrendStrength(
  shortTermChange: number | null | undefined,
  longTermChange: number | null | undefined,
): TrendStrength {
  // Default to neutral if no data
  if (
    (shortTermChange === null || shortTermChange === undefined) &&
    (longTermChange === null || longTermChange === undefined)
  ) {
    return 'neutral'
  }

  const short = shortTermChange ?? 0
  const long = longTermChange ?? 0

  // Combined momentum score
  const momentum = short * 0.6 + long * 0.4

  // Strong up: Both positive with high momentum
  if (momentum > 5 && short > 0 && long > 0) {
    return 'strong_up'
  }

  // Strong down: Both negative with significant decline
  if (momentum < -5 && short < 0 && long < 0) {
    return 'strong_down'
  }

  // Up: Positive momentum
  if (momentum > 1) {
    return 'up'
  }

  // Down: Negative momentum
  if (momentum < -1) {
    return 'down'
  }

  // Neutral: Mixed or flat signals
  return 'neutral'
}

/**
 * TrendBadge - Compact badge showing trend direction and strength
 *
 * Features:
 * - Visual indicator based on moving average crossovers
 * - 5 levels: Strong Up, Up, Neutral, Down, Strong Down
 * - Automatic calculation from price change data
 * - Optional explicit trend override
 *
 * @example
 * ```tsx
 * // Auto-calculate from price changes
 * <TrendBadge
 *   shortTermChange={3.5}
 *   longTermChange={8.2}
 * />
 *
 * // Or explicit trend
 * <TrendBadge trend="strong_up" showLabel />
 * ```
 */
function TrendBadgeComponent({
  shortTermChange,
  longTermChange,
  trend,
  showLabel = false,
  size = 'sm',
  className = '',
}: TrendBadgeProps) {
  // Calculate or use provided trend
  const trendStrength = useMemo(() => {
    if (trend) return trend
    return calculateTrendStrength(shortTermChange, longTermChange)
  }, [trend, shortTermChange, longTermChange])

  const config = TREND_CONFIGS[trendStrength]

  // Size classes
  const sizeClasses = {
    sm: 'px-1 py-0.5 text-[10px]',
    md: 'px-1.5 py-0.5 text-xs',
  }

  const tooltipContent = (() => {
    const hasShortTerm =
      shortTermChange !== null && shortTermChange !== undefined
    const hasLongTerm = longTermChange !== null && longTermChange !== undefined

    if (!hasShortTerm && !hasLongTerm) {
      return `Trend: ${config.label}`
    }

    const parts = [`Trend: ${config.label}`]
    if (hasShortTerm) {
      parts.push(
        `Short-term: ${shortTermChange > 0 ? '+' : ''}${shortTermChange.toFixed(2)}%`,
      )
    }
    if (hasLongTerm) {
      parts.push(
        `Long-term: ${longTermChange > 0 ? '+' : ''}${longTermChange.toFixed(2)}%`,
      )
    }
    return parts.join('\n')
  })()

  return (
    <span
      className={`inline-flex items-center gap-0.5 rounded font-medium ${config.bgColor} ${config.textColor} ${sizeClasses[size]} ${className}`}
      title={tooltipContent}
      aria-label={config.ariaLabel}
      role="status"
    >
      <span className="leading-none">{config.icon}</span>
      {showLabel && <span className="leading-none">{config.label}</span>}
    </span>
  )
}

/**
 * Memoized TrendBadge for optimal performance
 */
export const TrendBadge = memo(TrendBadgeComponent)

export default TrendBadge
