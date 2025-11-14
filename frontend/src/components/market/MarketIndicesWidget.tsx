/**
 * Market Indices Widget Component (FE-009 Phase 1)
 *
 * Displays real-time market indices (KOSPI, KOSDAQ, KRX100) with:
 * - Current value, change amount, change percentage
 * - Mini sparkline chart for each index
 * - Real-time updates
 * - Loading and error states
 */

import { useMarketIndices } from '../../hooks/useMarketIndices'
import { Sparkline } from './Sparkline'
import { formatCompactVolume, formatChangePercentage } from '../../utils/formatNumber'
import { componentSpacing, typography } from '../../config/theme'
import type { MarketIndex } from '../../types/market'

/**
 * Single index card component (Compact version for Phase 2C)
 * Height reduced from ~400px to ~140px (-65%)
 */
function IndexCard({ index }: { index: MarketIndex }) {
  const isPositive = index.change >= 0
  const changeClass = isPositive ? 'text-green-600' : 'text-red-600'
  const bgClass = isPositive ? 'bg-green-50' : 'bg-red-50'

  return (
    <div className={`rounded-lg border border-gray-200 p-2 ${bgClass} transition-all hover:shadow-md`}>
      {/* Top row: Name and Code */}
      <div className="flex items-center justify-between mb-1.5">
        <h3 className="text-xs font-semibold text-gray-700">{index.code}</h3>
        <p className="text-[10px] text-gray-500">{index.name}</p>
      </div>

      {/* Main row: Price and Change */}
      <div className="flex items-baseline justify-between mb-1.5">
        {/* Current value */}
        <p className="text-lg font-bold text-gray-900">
          {index.current.toLocaleString('ko-KR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </p>

        {/* Change percentage */}
        <div className={`flex items-center gap-1 text-xs font-semibold ${changeClass}`}>
          <span>{isPositive ? '▲' : '▼'}</span>
          <span>{formatChangePercentage(index.change_percent)}</span>
        </div>
      </div>

      {/* Sparkline chart (reduced height) */}
      <div className="h-8 mb-1.5">
        <Sparkline data={index.sparkline} color={isPositive ? '#16a34a' : '#dc2626'} />
      </div>

      {/* Bottom row: High/Low and Volume */}
      <div className="flex items-center justify-between text-[10px] text-gray-500">
        <span>
          고 {index.high.toLocaleString('ko-KR', { maximumFractionDigits: 0 })}
        </span>
        <span>
          저 {index.low.toLocaleString('ko-KR', { maximumFractionDigits: 0 })}
        </span>
        <span>
          {formatCompactVolume(index.volume)}
        </span>
      </div>
    </div>
  )
}

/**
 * Loading skeleton for index card (Compact version)
 */
function IndexCardSkeleton() {
  return (
    <div className="animate-pulse rounded-lg border border-gray-200 bg-gray-50 p-2">
      {/* Top row */}
      <div className="mb-1.5 flex justify-between">
        <div className="h-3 w-16 rounded bg-gray-300"></div>
        <div className="h-2.5 w-20 rounded bg-gray-300"></div>
      </div>
      {/* Main row */}
      <div className="mb-1.5 flex justify-between">
        <div className="h-5 w-24 rounded bg-gray-300"></div>
        <div className="h-4 w-16 rounded bg-gray-300"></div>
      </div>
      {/* Sparkline */}
      <div className="mb-1.5 h-8 rounded bg-gray-300"></div>
      {/* Bottom row */}
      <div className="flex justify-between">
        <div className="h-2.5 w-12 rounded bg-gray-300"></div>
        <div className="h-2.5 w-12 rounded bg-gray-300"></div>
        <div className="h-2.5 w-12 rounded bg-gray-300"></div>
      </div>
    </div>
  )
}

/**
 * Market Indices Widget Props
 */
export interface MarketIndicesWidgetProps {
  /** Enable auto-refresh (default: true) */
  autoRefresh?: boolean
  /** Refresh interval in milliseconds (default: 60000) */
  refreshInterval?: number
  /** Class name for styling */
  className?: string
}

/**
 * Market Indices Widget Component
 *
 * @example
 * ```tsx
 * <MarketIndicesWidget autoRefresh={true} refreshInterval={60000} />
 * ```
 */
export function MarketIndicesWidget({
  autoRefresh = true,
  refreshInterval = 60000,
  className = '',
}: MarketIndicesWidgetProps) {
  const { data, isLoading, error, dataUpdatedAt } = useMarketIndices({
    refetchInterval: autoRefresh ? refreshInterval : undefined,
  })

  // Format last updated time
  const lastUpdated = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    : ''

  return (
    <div className={`rounded-lg bg-white ${componentSpacing.widget} shadow-sm ${className}`}>
      {/* Header */}
      <div className="mb-3 flex items-center justify-between">
        <h2 className={`${typography.h2} text-gray-900`}>
          시장 지수 <span className="text-xs font-normal text-gray-500">Market Indices</span>
        </h2>
        {lastUpdated && (
          <span className="text-xs text-gray-500">
            마지막 업데이트: {lastUpdated}
          </span>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
          <p className="text-sm text-red-600">
            데이터를 불러오는 중 오류가 발생했습니다.
          </p>
          <p className="mt-1 text-xs text-red-500">{error.message}</p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <IndexCardSkeleton />
          <IndexCardSkeleton />
          <IndexCardSkeleton />
        </div>
      )}

      {/* Data State */}
      {data && !isLoading && (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          {data.indices.map((index) => (
            <IndexCard key={index.code} index={index} />
          ))}
        </div>
      )}
    </div>
  )
}
