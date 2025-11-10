import { ReactNode } from 'react'

interface MetricCardProps {
  /** Metric label */
  label: string
  /** Metric value (formatted) */
  value: string | number | null | undefined
  /** Unit (e.g., '%', '원', '배') */
  unit?: string
  /** Tooltip explanation */
  tooltip?: string
  /** Color coding */
  variant?: 'default' | 'positive' | 'negative' | 'neutral'
  /** Custom icon */
  icon?: ReactNode
  /** Additional className */
  className?: string
}

/**
 * Metric Card Component
 *
 * Displays a single financial/technical metric with label, value, and optional tooltip
 *
 * Features:
 * - Formatted value display
 * - Color coding (positive/negative)
 * - Tooltip with explanation
 * - Responsive design
 *
 * @example
 * ```tsx
 * <MetricCard
 *   label="PER"
 *   value={12.5}
 *   unit="배"
 *   tooltip="주가수익비율: 주가 / 주당순이익"
 *   variant="positive"
 * />
 * ```
 */
export default function MetricCard({
  label,
  value,
  unit,
  tooltip,
  variant = 'default',
  icon,
  className = '',
}: MetricCardProps) {
  // Format value
  const formattedValue = (() => {
    if (value === null || value === undefined) return 'N/A'
    if (typeof value === 'number') {
      return value.toLocaleString('ko-KR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      })
    }
    return value
  })()

  // Determine color class based on variant
  const valueColorClass = {
    default: 'text-gray-900',
    positive: 'text-red-600',
    negative: 'text-blue-600',
    neutral: 'text-gray-600',
  }[variant]

  return (
    <div
      className={`bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow ${className}`}
      title={tooltip}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        {icon && <div className="text-gray-400">{icon}</div>}
        <div className="text-sm font-medium text-gray-600">{label}</div>
        {tooltip && (
          <div className="relative group">
            <svg
              className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {/* Tooltip popup */}
            <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-48 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-10">
              {tooltip}
              <div className="absolute left-4 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
            </div>
          </div>
        )}
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-1">
        <span className={`text-2xl font-bold ${valueColorClass}`}>
          {formattedValue}
        </span>
        {unit && (
          <span className="text-sm text-gray-500 font-medium">{unit}</span>
        )}
      </div>
    </div>
  )
}
