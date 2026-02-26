/**
 * Market Breadth Widget Component (FE-009 Phase 2)
 *
 * Displays market breadth indicators:
 * - Advancing/declining/unchanged stock counts
 * - Advance/Decline ratio
 * - Market sentiment indicator
 * - Visual distribution bar chart
 */

import { useState } from 'react'
import { useMarketBreadth } from '../../hooks/useMarketBreadth'
import { componentSpacing, typography } from '../../config/theme'
import type { MarketType, MarketSentiment } from '../../types/market'

/**
 * Sentiment badge component
 */
function SentimentBadge({ sentiment }: { sentiment: MarketSentiment }) {
  const badges = {
    bullish: {
      label: '강세',
      className: 'bg-green-100 text-green-800 border-green-300',
      icon: '📈',
    },
    neutral: {
      label: '중립',
      className: 'bg-gray-100 text-gray-800 border-gray-300',
      icon: '➡️',
    },
    bearish: {
      label: '약세',
      className: 'bg-red-100 text-red-800 border-red-300',
      icon: '📉',
    },
  }

  const badge = badges[sentiment]

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium ${badge.className}`}
    >
      <span>{badge.icon}</span>
      <span>{badge.label}</span>
    </span>
  )
}

/**
 * Distribution bar chart component
 */
function DistributionBar({
  advancing,
  declining,
  unchanged,
  total,
}: {
  advancing: number
  declining: number
  unchanged: number
  total: number
}) {
  const advancingPct = (advancing / total) * 100
  const decliningPct = (declining / total) * 100
  const unchangedPct = (unchanged / total) * 100

  return (
    <div>
      {/* Bar */}
      <div className="flex h-6 overflow-hidden rounded-lg">
        {/* Advancing */}
        <div
          className="bg-green-500 transition-all"
          style={{ width: `${advancingPct}%` }}
          title={`상승: ${advancing} (${advancingPct.toFixed(1)}%)`}
        />
        {/* Declining */}
        <div
          className="bg-red-500 transition-all"
          style={{ width: `${decliningPct}%` }}
          title={`하락: ${declining} (${decliningPct.toFixed(1)}%)`}
        />
        {/* Unchanged */}
        <div
          className="bg-gray-400 transition-all"
          style={{ width: `${unchangedPct}%` }}
          title={`보합: ${unchanged} (${unchangedPct.toFixed(1)}%)`}
        />
      </div>

      {/* Legend */}
      <div className="mt-2 flex justify-between text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <div className="h-2.5 w-2.5 rounded bg-green-500"></div>
          <span>상승 {advancingPct.toFixed(1)}%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-2.5 w-2.5 rounded bg-red-500"></div>
          <span>하락 {decliningPct.toFixed(1)}%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-2.5 w-2.5 rounded bg-gray-400"></div>
          <span>보합 {unchangedPct.toFixed(1)}%</span>
        </div>
      </div>
    </div>
  )
}

/**
 * Market Breadth Widget Props
 */
export interface MarketBreadthWidgetProps {
  /** Default market filter */
  defaultMarket?: MarketType
  /** Enable auto-refresh */
  autoRefresh?: boolean
  /** Refresh interval in milliseconds */
  refreshInterval?: number
  /** Class name for styling */
  className?: string
}

/**
 * Market Breadth Widget Component
 *
 * @example
 * ```tsx
 * <MarketBreadthWidget defaultMarket="ALL" autoRefresh={true} />
 * ```
 */
export function MarketBreadthWidget({
  defaultMarket = 'ALL',
  autoRefresh = true,
  refreshInterval = 60000,
  className = '',
}: MarketBreadthWidgetProps) {
  const [selectedMarket, setSelectedMarket] =
    useState<MarketType>(defaultMarket)

  const { data, isLoading, error } = useMarketBreadth({
    market: selectedMarket,
    refetchInterval: autoRefresh ? refreshInterval : undefined,
  })

  return (
    <div
      className={`rounded-lg bg-white ${componentSpacing.widget} shadow-sm ${className}`}
    >
      {/* Header with market filter */}
      <div className="mb-3 flex items-center justify-between">
        <h2 className={`${typography.h2} text-gray-900`}>
          시장 폭{' '}
          <span className="text-xs font-normal text-gray-500">
            Market Breadth
          </span>
        </h2>

        {/* Market filter buttons */}
        <div className="flex gap-1.5">
          {(['ALL', 'KOSPI', 'KOSDAQ'] as MarketType[]).map(market => (
            <button
              key={market}
              onClick={() => setSelectedMarket(market)}
              className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
                selectedMarket === market
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {market}
            </button>
          ))}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
          <p className="text-sm text-red-600">
            데이터를 불러오는 중 오류가 발생했습니다.
          </p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="animate-pulse">
          <div className="mb-4 grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 rounded-lg bg-gray-200"></div>
            ))}
          </div>
          <div className="h-8 rounded-lg bg-gray-200"></div>
        </div>
      )}

      {/* Data State */}
      {data && !isLoading && (
        <>
          {/* Stats - Inline Layout */}
          <div className="mb-3 flex flex-wrap items-center gap-3">
            {/* Advancing */}
            <div className="flex items-baseline gap-2 rounded-lg border border-green-200 bg-green-50 px-3 py-2">
              <span className="text-xs text-gray-600">상승</span>
              <span className="text-lg font-bold text-green-600">
                {data.advancing.toLocaleString()}
              </span>
              <span className="text-xs text-gray-500">
                ({((data.advancing / data.total) * 100).toFixed(1)}%)
              </span>
            </div>

            {/* Declining */}
            <div className="flex items-baseline gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2">
              <span className="text-xs text-gray-600">하락</span>
              <span className="text-lg font-bold text-red-600">
                {data.declining.toLocaleString()}
              </span>
              <span className="text-xs text-gray-500">
                ({((data.declining / data.total) * 100).toFixed(1)}%)
              </span>
            </div>

            {/* Unchanged */}
            <div className="flex items-baseline gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
              <span className="text-xs text-gray-600">보합</span>
              <span className="text-lg font-bold text-gray-600">
                {data.unchanged.toLocaleString()}
              </span>
              <span className="text-xs text-gray-500">
                ({((data.unchanged / data.total) * 100).toFixed(1)}%)
              </span>
            </div>

            {/* A/D Ratio */}
            <div className="flex items-baseline gap-2 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2">
              <span className="text-xs text-gray-600">A/D 비율</span>
              <span className="text-lg font-bold text-blue-600">
                {data.ad_ratio.toFixed(2)}
              </span>
              <SentimentBadge sentiment={data.sentiment} />
            </div>
          </div>

          {/* Distribution Bar Chart */}
          <DistributionBar
            advancing={data.advancing}
            declining={data.declining}
            unchanged={data.unchanged}
            total={data.total}
          />
        </>
      )}
    </div>
  )
}
