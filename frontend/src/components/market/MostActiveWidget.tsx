/**
 * Most Active Stocks Widget Component (FE-009 Phase 5)
 *
 * Displays stocks with highest trading volume:
 * - Sortable table format
 * - Volume, price, change percentage
 * - Pagination (top 20)
 * - Click-to-detail navigation
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMostActive } from '../../hooks/useMostActive'
import type { MostActiveStock, MarketType } from '../../types/market'

/**
 * Table row for a stock
 */
function StockRow({ stock, rank }: { stock: MostActiveStock; rank: number }) {
  const isPositive = stock.change_percent >= 0

  return (
    <tr className="border-b border-gray-200 transition-colors hover:bg-gray-50">
      <td className="px-3 py-2 text-center text-sm text-gray-500">{rank}</td>
      <td className="px-3 py-2">
        <Link
          to={`/stocks/${stock.code}`}
          className="block hover:text-blue-600"
        >
          <div className="font-medium text-gray-900">{stock.name}</div>
          <div className="text-xs text-gray-500">{stock.code}</div>
        </Link>
      </td>
      <td className="px-3 py-2 text-right text-sm text-gray-900">
        ₩{stock.current_price.toLocaleString()}
      </td>
      <td
        className={`px-3 py-2 text-right text-sm font-medium ${
          isPositive ? 'text-green-600' : 'text-red-600'
        }`}
      >
        {isPositive ? '▲' : '▼'}
        {Math.abs(stock.change_percent).toFixed(2)}%
      </td>
      <td className="px-3 py-2 text-right text-sm text-gray-900">
        {(stock.volume / 1000000).toFixed(1)}M
      </td>
      <td className="px-3 py-2 text-right text-sm text-gray-900">
        {(stock.value / 1000000000).toFixed(1)}억
      </td>
    </tr>
  )
}

/**
 * Most Active Widget Props
 */
export interface MostActiveWidgetProps {
  /** Default market filter */
  defaultMarket?: MarketType
  /** Number of results */
  limit?: number
  /** Enable auto-refresh */
  autoRefresh?: boolean
  /** Class name for styling */
  className?: string
}

/**
 * Most Active Stocks Widget Component
 *
 * @example
 * ```tsx
 * <MostActiveWidget defaultMarket="ALL" limit={20} autoRefresh={true} />
 * ```
 */
export function MostActiveWidget({
  defaultMarket = 'ALL',
  limit = 20,
  autoRefresh = true,
  className = '',
}: MostActiveWidgetProps) {
  const [selectedMarket, setSelectedMarket] = useState<MarketType>(defaultMarket)

  const { data, isLoading, error } = useMostActive({
    market: selectedMarket,
    limit,
    refetchInterval: autoRefresh ? 60000 : undefined,
  })

  return (
    <div className={`rounded-lg bg-white p-4 shadow-sm ${className}`}>
      {/* Header with market filter */}
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-semibold text-gray-900">
          거래 상위 종목 <span className="text-sm font-normal text-gray-500">Most Active</span>
        </h2>

        {/* Market filter */}
        <div className="flex gap-1.5">
          {(['ALL', 'KOSPI', 'KOSDAQ'] as MarketType[]).map((market) => (
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
          <p className="text-sm text-red-600">데이터를 불러오는 중 오류가 발생했습니다.</p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-2">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-14 animate-pulse rounded bg-gray-200"></div>
          ))}
        </div>
      )}

      {/* Data State */}
      {data && !isLoading && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-gray-300 text-sm text-gray-600">
                <th className="px-3 py-2 text-center">순위</th>
                <th className="px-3 py-2 text-left">종목명</th>
                <th className="px-3 py-2 text-right">현재가</th>
                <th className="px-3 py-2 text-right">등락률</th>
                <th className="px-3 py-2 text-right">거래량</th>
                <th className="px-3 py-2 text-right">거래대금</th>
              </tr>
            </thead>
            <tbody>
              {data.stocks.length > 0 ? (
                data.stocks.map((stock, index) => (
                  <StockRow key={stock.code} stock={stock} rank={index + 1} />
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-sm text-gray-500">
                    데이터가 없습니다
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Help text */}
      <div className="mt-4 text-center text-xs text-gray-500">
        종목명을 클릭하면 상세 정보를 볼 수 있습니다
      </div>
    </div>
  )
}
