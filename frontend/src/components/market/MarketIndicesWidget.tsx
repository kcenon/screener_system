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
import type { MarketIndex } from '../../types/market'

/**
 * Single index card component
 */
function IndexCard({ index }: { index: MarketIndex }) {
  const isPositive = index.change >= 0
  const changeClass = isPositive ? 'text-green-600' : 'text-red-600'
  const bgClass = isPositive ? 'bg-green-50' : 'bg-red-50'

  return (
    <div className={`rounded-lg border border-gray-200 p-4 ${bgClass} transition-all hover:shadow-md`}>
      {/* Index name and code */}
      <div className="mb-2">
        <h3 className="text-sm font-medium text-gray-600">{index.code}</h3>
        <p className="text-xs text-gray-500">{index.name}</p>
      </div>

      {/* Current value */}
      <div className="mb-2">
        <p className="text-2xl font-bold text-gray-900">
          {index.current.toLocaleString('ko-KR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </p>
      </div>

      {/* Change amount and percentage */}
      <div className={`mb-3 flex items-center gap-2 text-sm font-medium ${changeClass}`}>
        <span>{isPositive ? '▲' : '▼'}</span>
        <span>
          {Math.abs(index.change).toLocaleString('ko-KR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </span>
        <span>
          ({isPositive ? '+' : ''}
          {index.change_percent.toFixed(2)}%)
        </span>
      </div>

      {/* High/Low */}
      <div className="mb-3 flex justify-between text-xs text-gray-600">
        <span>
          고: {index.high.toLocaleString('ko-KR', { minimumFractionDigits: 2 })}
        </span>
        <span>
          저: {index.low.toLocaleString('ko-KR', { minimumFractionDigits: 2 })}
        </span>
      </div>

      {/* Sparkline chart */}
      <div className="h-12">
        <Sparkline data={index.sparkline} color={isPositive ? '#16a34a' : '#dc2626'} />
      </div>

      {/* Volume */}
      <div className="mt-2 text-xs text-gray-500">
        거래량: {(index.volume / 1000000).toFixed(1)}M
      </div>
    </div>
  )
}

/**
 * Loading skeleton for index card
 */
function IndexCardSkeleton() {
  return (
    <div className="animate-pulse rounded-lg border border-gray-200 bg-gray-50 p-4">
      <div className="mb-2 h-4 w-20 rounded bg-gray-300"></div>
      <div className="mb-2 h-8 w-32 rounded bg-gray-300"></div>
      <div className="mb-3 h-4 w-24 rounded bg-gray-300"></div>
      <div className="mb-3 flex justify-between">
        <div className="h-3 w-16 rounded bg-gray-300"></div>
        <div className="h-3 w-16 rounded bg-gray-300"></div>
      </div>
      <div className="mb-2 h-12 rounded bg-gray-300"></div>
      <div className="h-3 w-20 rounded bg-gray-300"></div>
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
    <div className={`rounded-lg bg-white p-6 shadow-sm ${className}`}>
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          시장 지수 <span className="text-sm font-normal text-gray-500">Market Indices</span>
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
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <IndexCardSkeleton />
          <IndexCardSkeleton />
          <IndexCardSkeleton />
        </div>
      )}

      {/* Data State */}
      {data && !isLoading && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {data.indices.map((index) => (
            <IndexCard key={index.code} index={index} />
          ))}
        </div>
      )}
    </div>
  )
}
