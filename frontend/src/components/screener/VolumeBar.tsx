import { memo, useMemo } from 'react'

/**
 * Props for VolumeBar component
 */
export interface VolumeBarProps {
  /** Current volume */
  volume: number | null | undefined
  /** Average volume for comparison */
  averageVolume: number | null | undefined
  /** Maximum width in pixels (default: 60) */
  maxWidth?: number
  /** Height in pixels (default: 12) */
  height?: number
  /** CSS class name for container */
  className?: string
  /** Show ratio text */
  showRatio?: boolean
  /** Maximum ratio to cap the bar (default: 5x) */
  maxRatio?: number
}

/**
 * VolumeBar - Mini bar chart showing volume relative to average
 *
 * Features:
 * - Visual indicator of volume relative to average
 * - Green bar: Above average, Red bar: Below average
 * - Width proportional to volume ratio (capped at maxRatio)
 * - Tooltip with exact ratio
 *
 * @example
 * ```tsx
 * <VolumeBar
 *   volume={2500000}
 *   averageVolume={1000000}
 *   maxWidth={60}
 *   height={12}
 * />
 * // Renders: [████████░░░░] 2.5x
 * ```
 */
function VolumeBarComponent({
  volume,
  averageVolume,
  maxWidth = 60,
  height = 12,
  className = '',
  showRatio = true,
  maxRatio = 5,
}: VolumeBarProps) {
  // Calculate volume ratio and bar properties
  const { ratio, fillWidth, barColor, label } = useMemo(() => {
    if (
      volume === null ||
      volume === undefined ||
      averageVolume === null ||
      averageVolume === undefined ||
      averageVolume === 0
    ) {
      return {
        ratio: 0,
        fillWidth: 0,
        barColor: 'bg-gray-300 dark:bg-gray-600',
        label: '-',
      }
    }

    const calculatedRatio = volume / averageVolume
    const cappedRatio = Math.min(calculatedRatio, maxRatio)
    const width = (cappedRatio / maxRatio) * maxWidth

    // Determine color based on ratio
    let color: string
    if (calculatedRatio >= 2) {
      color = 'bg-green-500 dark:bg-green-400' // Very high volume
    } else if (calculatedRatio >= 1) {
      color = 'bg-green-400 dark:bg-green-500' // Above average
    } else if (calculatedRatio >= 0.5) {
      color = 'bg-yellow-400 dark:bg-yellow-500' // Below average
    } else {
      color = 'bg-red-400 dark:bg-red-500' // Very low volume
    }

    return {
      ratio: calculatedRatio,
      fillWidth: width,
      barColor: color,
      label:
        calculatedRatio >= 10
          ? `${calculatedRatio.toFixed(0)}x`
          : calculatedRatio >= 1
            ? `${calculatedRatio.toFixed(1)}x`
            : `${calculatedRatio.toFixed(2)}x`,
    }
  }, [volume, averageVolume, maxWidth, maxRatio])

  // Handle missing data
  if (ratio === 0 && label === '-') {
    return (
      <div
        className={`inline-flex items-center text-gray-400 dark:text-gray-600 ${className}`}
        aria-label="No volume data available"
      >
        <span className="text-xs">-</span>
      </div>
    )
  }

  const tooltipContent = `Volume: ${volume?.toLocaleString()}\nAvg: ${averageVolume?.toLocaleString()}\nRatio: ${label}`

  return (
    <div
      className={`inline-flex items-center gap-1 ${className}`}
      title={tooltipContent}
      aria-label={`Volume ${ratio >= 1 ? 'above' : 'below'} average: ${label}`}
    >
      {/* Bar container */}
      <div
        className="relative bg-gray-200 dark:bg-gray-700 rounded-sm overflow-hidden"
        style={{ width: maxWidth, height }}
      >
        {/* Fill bar */}
        <div
          className={`absolute inset-y-0 left-0 rounded-sm transition-all duration-200 ${barColor}`}
          style={{ width: fillWidth }}
        />
        {/* Reference line at 1x (average) */}
        <div
          className="absolute inset-y-0 w-px bg-gray-500 dark:bg-gray-400 opacity-50"
          style={{ left: maxWidth / maxRatio }}
        />
      </div>

      {/* Ratio label */}
      {showRatio && (
        <span
          className={`text-[10px] font-medium min-w-[24px] ${
            ratio >= 2
              ? 'text-green-600 dark:text-green-400'
              : ratio >= 1
                ? 'text-green-500 dark:text-green-500'
                : ratio >= 0.5
                  ? 'text-yellow-600 dark:text-yellow-400'
                  : 'text-red-500 dark:text-red-400'
          }`}
        >
          {label}
        </span>
      )}
    </div>
  )
}

/**
 * Memoized VolumeBar for optimal performance
 */
export const VolumeBar = memo(VolumeBarComponent)

export default VolumeBar
