/**
 * Market Summary Widget
 *
 * Displays market indices (KOSPI, KOSDAQ) with current values,
 * changes, and mini sparkline charts.
 */

import { TrendingUp, TrendingDown } from 'lucide-react'
import type { MarketIndex } from '../../types'

interface MarketSummaryWidgetProps {
  /** KOSPI index data */
  kospi?: MarketIndex
  /** KOSDAQ index data */
  kosdaq?: MarketIndex
  /** Loading state */
  isLoading?: boolean
}

/**
 * Format number with commas
 */
function formatNumber(value: number): string {
  return value.toLocaleString('ko-KR', { maximumFractionDigits: 2 })
}

/**
 * Format percentage with sign
 */
function formatPercent(value: number): string {
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

/**
 * Market Index Card Component
 */
function IndexCard({ index }: { index?: MarketIndex }) {
  if (!index) {
    return (
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
        <div className="h-8 bg-gray-200 rounded w-32 mb-1"></div>
        <div className="h-4 bg-gray-200 rounded w-24"></div>
      </div>
    )
  }

  const isPositive = index.change_percent >= 0
  const Icon = isPositive ? TrendingUp : TrendingDown
  const colorClass = isPositive ? 'text-green-600' : 'text-red-600'
  const bgClass = isPositive ? 'bg-green-50' : 'bg-red-50'

  return (
    <div className={`${bgClass} rounded-lg p-4`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">{index.name}</span>
        <Icon className={`w-4 h-4 ${colorClass}`} />
      </div>

      <div className="mb-1">
        <div className="text-2xl font-bold text-gray-900">
          {formatNumber(index.current)}
        </div>
      </div>

      <div className={`text-sm font-medium ${colorClass}`}>
        <span>
          {isPositive ? '▲' : '▼'} {Math.abs(index.change).toFixed(2)} (
          {formatPercent(index.change_percent)})
        </span>
      </div>

      {/* Additional info */}
      <div className="mt-3 pt-3 border-t border-gray-200 grid grid-cols-2 gap-2 text-xs text-gray-600">
        <div>
          <div className="text-gray-500">High</div>
          <div className="font-medium">{formatNumber(index.high)}</div>
        </div>
        <div>
          <div className="text-gray-500">Low</div>
          <div className="font-medium">{formatNumber(index.low)}</div>
        </div>
      </div>
    </div>
  )
}

/**
 * MarketSummaryWidget Component
 */
export default function MarketSummaryWidget({
  kospi,
  kosdaq,
}: MarketSummaryWidgetProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <IndexCard index={kospi} />
      <IndexCard index={kosdaq} />
    </div>
  )
}
