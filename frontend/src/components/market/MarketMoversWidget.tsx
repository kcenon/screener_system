/**
 * Market Movers Widget Component (FE-009 Phase 4)
 *
 * Displays top gainers and losers:
 * - Dual-column layout for gainers and losers
 * - Market filter (KOSPI/KOSDAQ/ALL)
 * - Stock code, name, price, change percentage
 * - Special indicators for significant moves (>10%)
 * - Links to stock detail page
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMarketMovers } from '../../hooks/useMarketMovers'
import type { MarketMover, MarketType } from '../../types/market'

/**
 * Single stock mover item
 */
function MoverItem({ stock, rank }: { stock: MarketMover; rank: number }) {
  const isGainer = stock.change_percent > 0
  const isSignificant = Math.abs(stock.change_percent) >= 10

  return (
    <Link
      to={`/stocks/${stock.code}`}
      className="flex items-center gap-3 rounded-lg p-3 transition-colors hover:bg-gray-50"
    >
      {/* Rank */}
      <div className="flex-shrink-0 text-lg font-bold text-gray-400 w-8">
        {rank}
      </div>

      {/* Stock info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900 truncate">
            {stock.name}
          </span>
          {isSignificant && <span>🔥</span>}
        </div>
        <div className="text-xs text-gray-500">{stock.code}</div>
      </div>

      {/* Price and change */}
      <div className="flex-shrink-0 text-right">
        <div className="font-medium text-gray-900">
          ₩{stock.current_price.toLocaleString()}
        </div>
        <div
          className={`text-sm font-medium ${
            isGainer ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {isGainer ? '▲' : '▼'}
          {Math.abs(stock.change_percent).toFixed(2)}%
        </div>
      </div>
    </Link>
  )
}

/**
 * Market Movers Widget Props
 */
export interface MarketMoversWidgetProps {
  /** Default market filter */
  defaultMarket?: MarketType
  /** Number of results per category */
  limit?: number
  /** Enable auto-refresh */
  autoRefresh?: boolean
  /** Class name for styling */
  className?: string
}

/**
 * Market Movers Widget Component
 *
 * @example
 * ```tsx
 * <MarketMoversWidget defaultMarket="ALL" limit={10} autoRefresh={true} />
 * ```
 */
export function MarketMoversWidget({
  defaultMarket = 'ALL',
  limit = 10,
  autoRefresh = true,
  className = '',
}: MarketMoversWidgetProps) {
  const [selectedMarket, setSelectedMarket] =
    useState<MarketType>(defaultMarket)

  const { data, isLoading, error } = useMarketMovers({
    market: selectedMarket,
    limit,
    refetchInterval: autoRefresh ? 60000 : undefined,
  })

  return (
    <div className={`rounded-lg bg-white p-4 shadow-sm ${className}`}>
      {/* Header with market filter */}
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-semibold text-gray-900">
          시장 주도주{' '}
          <span className="text-sm font-normal text-gray-500">
            Market Movers
          </span>
        </h2>

        {/* Market filter */}
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
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {[...Array(2)].map((_, col) => (
            <div key={col} className="space-y-2">
              {[...Array(5)].map((_, row) => (
                <div
                  key={row}
                  className="h-16 animate-pulse rounded-lg bg-gray-200"
                ></div>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Data State */}
      {data && !isLoading && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* Top Gainers */}
          <div>
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-green-600">
              <span>📈</span>
              <span>상승률 TOP {limit}</span>
            </h3>
            <div className="space-y-1">
              {data.gainers.length > 0 ? (
                data.gainers.map((stock: MarketMover, index: number) => (
                  <MoverItem key={stock.code} stock={stock} rank={index + 1} />
                ))
              ) : (
                <div className="py-8 text-center text-sm text-gray-500">
                  데이터가 없습니다
                </div>
              )}
            </div>
          </div>

          {/* Top Losers */}
          <div>
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-red-600">
              <span>📉</span>
              <span>하락률 TOP {limit}</span>
            </h3>
            <div className="space-y-1">
              {data.losers.length > 0 ? (
                data.losers.map((stock: MarketMover, index: number) => (
                  <MoverItem key={stock.code} stock={stock} rank={index + 1} />
                ))
              ) : (
                <div className="py-8 text-center text-sm text-gray-500">
                  데이터가 없습니다
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 flex justify-center gap-4 text-xs text-gray-500">
        <span>🔥 = 10% 이상 변동</span>
        <span>클릭하여 상세 정보 보기</span>
      </div>
    </div>
  )
}
