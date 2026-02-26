import { useMemo } from 'react'
import type { StockDetail, PriceChange } from '@/types'
import { AddToWatchlistButton } from '@/components/watchlist'

interface StockHeaderProps {
  stock: StockDetail
}

/**
 * Stock Header Component
 *
 * Displays:
 * - Stock name and code
 * - Current price with change (absolute and percentage)
 * - Market capitalization
 * - Add to watchlist / Create alert buttons (Phase 2)
 *
 * @example
 * ```tsx
 * <StockHeader stock={stockData} />
 * ```
 */
export default function StockHeader({ stock }: StockHeaderProps) {
  // Calculate price change
  const priceChange = useMemo<PriceChange | null>(() => {
    if (stock.current_price == null || stock.price_change_1d == null) {
      return null
    }

    const percentage = stock.price_change_1d
    const value = stock.current_price * (percentage / 100)

    return {
      value,
      percentage,
      is_positive: percentage >= 0,
    }
  }, [stock.current_price, stock.price_change_1d])

  // Format market cap
  const formattedMarketCap = useMemo(() => {
    if (stock.market_cap == null) return 'N/A'

    // Market cap is in KRW billion
    if (stock.market_cap >= 1000) {
      return `${(stock.market_cap / 1000).toFixed(2)}조 원`
    }
    return `${stock.market_cap.toFixed(0)}억 원`
  }, [stock.market_cap])

  // Format price
  const formattedPrice = useMemo(() => {
    if (stock.current_price == null) return 'N/A'
    return stock.current_price.toLocaleString('ko-KR')
  }, [stock.current_price])

  return (
    <div className="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-6">
      <div className="max-w-7xl mx-auto">
        {/* Stock Info */}
        <div className="flex items-start justify-between">
          <div>
            {/* Stock Name */}
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              {stock.name}
            </h1>

            {/* Stock Code and Market */}
            <div className="mt-1 flex items-center gap-3">
              <span className="text-sm text-gray-600">{stock.code}</span>
              <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                {stock.market}
              </span>
              {stock.sector && (
                <span className="text-sm text-gray-500">{stock.sector}</span>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <AddToWatchlistButton
              stock={{
                code: stock.code,
                name: stock.name,
                market: stock.market as 'KOSPI' | 'KOSDAQ',
                current_price: stock.current_price || undefined,
                change_percent: stock.price_change_1d || undefined,
                volume: stock.current_volume || undefined,
              }}
              variant="button"
              size="md"
            />
          </div>
        </div>

        {/* Price Section */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Current Price */}
          <div>
            <div className="text-sm text-gray-500 mb-1">현재가</div>
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-bold text-gray-900">
                {formattedPrice}
              </span>
              <span className="text-lg text-gray-600">원</span>
            </div>
          </div>

          {/* Price Change */}
          {priceChange && (
            <div>
              <div className="text-sm text-gray-500 mb-1">전일 대비</div>
              <div className="flex items-baseline gap-2">
                <span
                  className={`text-2xl font-semibold ${
                    priceChange.is_positive
                      ? 'text-red-600'
                      : priceChange.value === 0
                        ? 'text-gray-900'
                        : 'text-blue-600'
                  }`}
                >
                  {priceChange.is_positive ? '+' : ''}
                  {priceChange.value.toLocaleString('ko-KR')}
                </span>
                <span
                  className={`text-xl font-medium ${
                    priceChange.is_positive
                      ? 'text-red-600'
                      : priceChange.value === 0
                        ? 'text-gray-900'
                        : 'text-blue-600'
                  }`}
                >
                  ({priceChange.is_positive ? '+' : ''}
                  {priceChange.percentage.toFixed(2)}%)
                </span>
              </div>
            </div>
          )}

          {/* Market Cap */}
          <div>
            <div className="text-sm text-gray-500 mb-1">시가총액</div>
            <div className="text-2xl font-semibold text-gray-900">
              {formattedMarketCap}
            </div>
          </div>
        </div>

        {/* Last Trade Date */}
        {stock.last_trade_date && (
          <div className="mt-4 text-xs text-gray-400">
            최종 거래일: {stock.last_trade_date}
          </div>
        )}
      </div>
    </div>
  )
}
