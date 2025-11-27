import { memo, useMemo } from 'react'

/**
 * Props for RangeIndicator component
 */
export interface RangeIndicatorProps {
  /** Current price */
  currentPrice: number | null | undefined
  /** 52-week low price */
  low52w: number | null | undefined
  /** 52-week high price */
  high52w: number | null | undefined
  /** Width in pixels (default: 60) */
  width?: number
  /** Height in pixels (default: 8) */
  height?: number
  /** CSS class name for container */
  className?: string
  /** Show percentage text */
  showPercent?: boolean
}

/**
 * Get gradient color based on position percentage
 * Red (near low) → Yellow (middle) → Green (near high)
 */
function getPositionColor(percent: number): {
  marker: string
  text: string
} {
  if (percent >= 80) {
    return {
      marker: 'bg-green-500 dark:bg-green-400',
      text: 'text-green-600 dark:text-green-400',
    }
  } else if (percent >= 60) {
    return {
      marker: 'bg-green-400 dark:bg-green-500',
      text: 'text-green-500 dark:text-green-500',
    }
  } else if (percent >= 40) {
    return {
      marker: 'bg-yellow-400 dark:bg-yellow-500',
      text: 'text-yellow-600 dark:text-yellow-400',
    }
  } else if (percent >= 20) {
    return {
      marker: 'bg-orange-400 dark:bg-orange-500',
      text: 'text-orange-500 dark:text-orange-400',
    }
  } else {
    return {
      marker: 'bg-red-500 dark:bg-red-400',
      text: 'text-red-500 dark:text-red-400',
    }
  }
}

/**
 * RangeIndicator - Visual indicator showing current price position in 52-week range
 *
 * Features:
 * - Horizontal bar with marker showing current position
 * - Color gradient: Red (near low) → Yellow (middle) → Green (near high)
 * - Tooltip with high/low values
 * - Percentage label option
 *
 * @example
 * ```tsx
 * <RangeIndicator
 *   currentPrice={50000}
 *   low52w={40000}
 *   high52w={60000}
 *   width={60}
 * />
 * // Renders: [━━━━━━●━━━] 50%
 * ```
 */
function RangeIndicatorComponent({
  currentPrice,
  low52w,
  high52w,
  width = 60,
  height = 8,
  className = '',
  showPercent = true,
}: RangeIndicatorProps) {
  // Calculate position and styling
  const { position, percent, colors, isValid } = useMemo(() => {
    if (
      currentPrice === null ||
      currentPrice === undefined ||
      low52w === null ||
      low52w === undefined ||
      high52w === null ||
      high52w === undefined ||
      high52w <= low52w
    ) {
      return {
        position: 0,
        percent: 0,
        colors: getPositionColor(50),
        isValid: false,
      }
    }

    const range = high52w - low52w
    const calculatedPercent = ((currentPrice - low52w) / range) * 100
    const clampedPercent = Math.max(0, Math.min(100, calculatedPercent))
    const markerPosition = (clampedPercent / 100) * width

    return {
      position: markerPosition,
      percent: clampedPercent,
      colors: getPositionColor(clampedPercent),
      isValid: true,
    }
  }, [currentPrice, low52w, high52w, width])

  // Handle missing or invalid data
  if (!isValid) {
    return (
      <div
        className={`inline-flex items-center text-gray-400 dark:text-gray-600 ${className}`}
        aria-label="No 52-week range data available"
      >
        <span className="text-xs">-</span>
      </div>
    )
  }

  const tooltipContent = `52W Range\nHigh: ${high52w?.toLocaleString()}\nLow: ${low52w?.toLocaleString()}\nCurrent: ${currentPrice?.toLocaleString()} (${percent.toFixed(0)}%)`

  return (
    <div
      className={`inline-flex items-center gap-1 ${className}`}
      title={tooltipContent}
      aria-label={`52-week range position: ${percent.toFixed(0)}% from low`}
    >
      {/* Range bar container */}
      <div
        className="relative bg-gradient-to-r from-red-200 via-yellow-200 to-green-200 dark:from-red-900 dark:via-yellow-900 dark:to-green-900 rounded-full"
        style={{ width, height }}
      >
        {/* Current position marker */}
        <div
          className={`absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-gray-800 shadow-sm ${colors.marker}`}
          style={{ left: position }}
        />
      </div>

      {/* Percentage label */}
      {showPercent && (
        <span className={`text-[10px] font-medium min-w-[28px] ${colors.text}`}>
          {percent.toFixed(0)}%
        </span>
      )}
    </div>
  )
}

/**
 * Memoized RangeIndicator for optimal performance
 */
export const RangeIndicator = memo(RangeIndicatorComponent)

export default RangeIndicator
