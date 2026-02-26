/**
 * Sparkline Chart Component
 *
 * Simple SVG-based line chart for displaying trends in a compact space.
 * Used in market indices cards to show historical price movement.
 */

import { useMemo } from 'react'

/**
 * Sparkline Props
 */
export interface SparklineProps {
  /** Array of numeric data points */
  data: number[]
  /** Line color (hex or CSS color) */
  color?: string
  /** Chart width (default: 100%) */
  width?: number | string
  /** Chart height (default: 100%) */
  height?: number | string
  /** Line thickness in pixels */
  strokeWidth?: number
  /** Show filled area under line */
  showArea?: boolean
  /** Class name for styling */
  className?: string
}

/**
 * Sparkline Component
 *
 * @example
 * ```tsx
 * <Sparkline
 *   data={[100, 105, 103, 108, 110]}
 *   color="#16a34a"
 *   strokeWidth={2}
 *   showArea={true}
 * />
 * ```
 */
export function Sparkline({
  data,
  color = '#3b82f6',
  width = '100%',
  height = '100%',
  strokeWidth = 1.5,
  showArea = false,
  className = '',
}: SparklineProps) {
  // Calculate path data for SVG
  const pathData = useMemo(() => {
    if (!data || data.length === 0) {
      return { line: '', area: '' }
    }

    // Find min and max values for scaling
    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1 // Avoid division by zero

    // Calculate points
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * 100
      const y = 100 - ((value - min) / range) * 100
      return { x, y }
    })

    // Generate line path
    const linePath = points
      .map((point, index) => {
        const command = index === 0 ? 'M' : 'L'
        return `${command} ${point.x} ${point.y}`
      })
      .join(' ')

    // Generate area path (filled region under line)
    const areaPath = showArea ? `${linePath} L 100 100 L 0 100 Z` : ''

    return {
      line: linePath,
      area: areaPath,
    }
  }, [data, showArea])

  // Handle empty data
  if (!data || data.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <span className="text-xs text-gray-400">No data</span>
      </div>
    )
  }

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 100 100"
      preserveAspectRatio="none"
      className={className}
    >
      {/* Filled area under line */}
      {showArea && pathData.area && (
        <path d={pathData.area} fill={color} fillOpacity={0.1} />
      )}

      {/* Line */}
      <path
        d={pathData.line}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  )
}
