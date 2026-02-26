/**
 * Order Book Component (FE-005)
 *
 * Displays 10-level order book (호가) with real-time updates
 *
 * Features:
 * - 10 levels of bid and ask prices
 * - Color-coded (red=ask, blue=bid)
 * - Volume visualization with horizontal bars
 * - Spread and mid-price display
 * - Order imbalance indicator
 * - Flash animations on updates
 * - Freeze/unfreeze functionality
 * - Responsive design
 */

import { memo, useMemo, useState, useEffect } from 'react'
import { OrderBookData, OrderBookLevel, OrderImbalance } from '@/types/stock'
import { formatNumber, formatPrice } from '@/utils/format'
import clsx from 'clsx'

/**
 * OrderBook Component Props
 */
export interface OrderBookProps {
  /** Order book data */
  data: OrderBookData | null
  /** Order imbalance indicator */
  imbalance: OrderImbalance | null
  /** Loading state */
  isLoading?: boolean
  /** Frozen state (no updates) */
  frozen?: boolean
  /** Freeze toggle callback */
  onToggleFreeze?: () => void
  /** Number of levels to display (default: 10) */
  levels?: number
  /** Show detailed view */
  detailed?: boolean
  /** Mobile view */
  mobile?: boolean
}

/**
 * Order Book Level Row Component
 */
interface LevelRowProps {
  level: OrderBookLevel
  maxVolume: number
  type: 'bid' | 'ask'
  highlight?: boolean
  flash?: boolean
}

const LevelRow = memo<LevelRowProps>(
  ({ level, maxVolume, type, highlight, flash }) => {
    const volumePercentage =
      maxVolume > 0 ? (level.volume / maxVolume) * 100 : 0

    const baseColor = type === 'bid' ? 'bg-blue-500' : 'bg-red-500'
    const lightColor = type === 'bid' ? 'bg-blue-50' : 'bg-red-50'
    const textColor = type === 'bid' ? 'text-blue-600' : 'text-red-600'
    const borderColor = highlight
      ? type === 'bid'
        ? 'border-blue-600'
        : 'border-red-600'
      : 'border-transparent'

    return (
      <div
        className={clsx(
          'relative grid grid-cols-3 gap-2 py-1.5 px-2 text-sm border-l-2 transition-all duration-200',
          borderColor,
          flash && 'animate-pulse',
          lightColor,
        )}
      >
        {/* Volume bar (background) */}
        <div
          className={clsx(
            'absolute inset-0 opacity-10 transition-all duration-300',
            baseColor,
          )}
          style={{ width: `${volumePercentage}%` }}
        />

        {/* Price */}
        <div
          className={clsx(
            'relative z-10 text-right font-mono font-semibold',
            textColor,
          )}
        >
          {formatPrice(level.price)}
        </div>

        {/* Volume */}
        <div className="relative z-10 text-right text-gray-700">
          {formatNumber(level.volume)}
        </div>

        {/* Total (cumulative) */}
        <div className="relative z-10 text-right text-gray-500 text-xs">
          {formatNumber(level.total)}
        </div>
      </div>
    )
  },
)

LevelRow.displayName = 'LevelRow'

/**
 * Spread Display Component
 */
interface SpreadDisplayProps {
  spread?: number
  spreadPct?: number
  midPrice?: number
}

const SpreadDisplay = memo<SpreadDisplayProps>(
  ({ spread, spreadPct, midPrice }) => {
    if (
      spread === undefined ||
      spreadPct === undefined ||
      midPrice === undefined
    ) {
      return null
    }

    return (
      <div className="bg-gray-100 border-y border-gray-300 py-3 px-4">
        <div className="grid grid-cols-3 gap-4 text-center text-sm">
          <div>
            <div className="text-gray-500 text-xs mb-1">호가차</div>
            <div className="font-semibold text-gray-900">
              {formatPrice(spread)}
            </div>
          </div>
          <div>
            <div className="text-gray-500 text-xs mb-1">스프레드</div>
            <div className="font-semibold text-gray-900">
              {spreadPct.toFixed(2)}%
            </div>
          </div>
          <div>
            <div className="text-gray-500 text-xs mb-1">중간가</div>
            <div className="font-semibold text-gray-900">
              {formatPrice(midPrice)}
            </div>
          </div>
        </div>
      </div>
    )
  },
)

SpreadDisplay.displayName = 'SpreadDisplay'

/**
 * Order Imbalance Indicator Component
 */
interface ImbalanceIndicatorProps {
  imbalance: OrderImbalance | null
}

const ImbalanceIndicator = memo<ImbalanceIndicatorProps>(({ imbalance }) => {
  if (!imbalance) {
    return null
  }

  const { imbalance_ratio, direction, total_bid_volume, total_ask_volume } =
    imbalance

  const buyWidth = imbalance_ratio * 100
  const sellWidth = (1 - imbalance_ratio) * 100

  let directionText = '균형'
  let directionColor = 'text-gray-600'

  if (direction === 'buy') {
    directionText = '매수 우세'
    directionColor = 'text-blue-600'
  } else if (direction === 'sell') {
    directionText = '매도 우세'
    directionColor = 'text-red-600'
  }

  return (
    <div className="bg-white border-t border-gray-200 py-3 px-4">
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs text-gray-500">주문 불균형</div>
        <div className={clsx('text-xs font-semibold', directionColor)}>
          {directionText}
        </div>
      </div>

      {/* Visual bar */}
      <div className="flex h-3 rounded-full overflow-hidden bg-gray-200 mb-2">
        <div className="bg-blue-500" style={{ width: `${buyWidth}%` }} />
        <div className="bg-red-500" style={{ width: `${sellWidth}%` }} />
      </div>

      {/* Volume breakdown */}
      <div className="grid grid-cols-2 gap-4 text-xs">
        <div className="text-blue-600">
          <span className="font-semibold">매수:</span>{' '}
          {formatNumber(total_bid_volume)}
        </div>
        <div className="text-red-600 text-right">
          <span className="font-semibold">매도:</span>{' '}
          {formatNumber(total_ask_volume)}
        </div>
      </div>
    </div>
  )
})

ImbalanceIndicator.displayName = 'ImbalanceIndicator'

/**
 * Main OrderBook Component
 */
export const OrderBook = memo<OrderBookProps>(
  ({
    data,
    imbalance,
    isLoading,
    frozen,
    onToggleFreeze,
    levels = 10,
    detailed = true,
  }) => {
    const [flashingLevels, setFlashingLevels] = useState<Set<string>>(new Set())

    // Track price changes for flash effect
    useEffect(() => {
      if (!data) return

      const newFlashing = new Set<string>()

      // Mark changed levels
      data.asks.forEach((level, index) => {
        if (index < levels) {
          newFlashing.add(`ask-${level.price}`)
        }
      })
      data.bids.forEach((level, index) => {
        if (index < levels) {
          newFlashing.add(`bid-${level.price}`)
        }
      })

      setFlashingLevels(newFlashing)

      // Clear flashing after animation
      const timer = setTimeout(() => {
        setFlashingLevels(new Set())
      }, 500)

      return () => clearTimeout(timer)
    }, [data, levels])

    // Calculate max volume for bar scaling
    const maxVolume = useMemo(() => {
      if (!data) return 0

      const allVolumes = [
        ...data.asks.map(l => l.volume),
        ...data.bids.map(l => l.volume),
      ]

      return Math.max(...allVolumes, 0)
    }, [data])

    // Slice to requested number of levels
    const displayAsks = useMemo(() => {
      if (!data) return []
      // Reverse asks to show from lowest to highest (top to bottom)
      return data.asks.slice(0, levels).reverse()
    }, [data, levels])

    const displayBids = useMemo(() => {
      if (!data) return []
      return data.bids.slice(0, levels)
    }, [data, levels])

    if (isLoading) {
      return (
        <div className="bg-white rounded-lg shadow-sm p-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-solid border-blue-600 border-r-transparent mb-3"></div>
          <p className="text-sm text-gray-600">호가 정보를 불러오는 중...</p>
        </div>
      )
    }

    if (!data) {
      return (
        <div className="bg-white rounded-lg shadow-sm p-8 text-center">
          <div className="text-gray-400 mb-2">
            <svg
              className="w-12 h-12 mx-auto"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <p className="text-sm text-gray-600">호가 데이터가 없습니다</p>
        </div>
      )
    }

    return (
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {/* Header */}
        <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h3 className="text-sm font-semibold text-gray-900">
              호가 ({levels}단계)
            </h3>
            <div className="text-xs text-gray-500">
              {new Date(data.timestamp).toLocaleTimeString('ko-KR', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
              })}
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-2">
            {onToggleFreeze && (
              <button
                onClick={onToggleFreeze}
                className={clsx(
                  'px-3 py-1 text-xs font-medium rounded-md transition-colors',
                  frozen
                    ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
                )}
                title={frozen ? '업데이트 재개' : '업데이트 중지'}
              >
                {frozen ? '⏸ 정지됨' : '▶ 실시간'}
              </button>
            )}
          </div>
        </div>

        {/* Column headers */}
        {detailed && (
          <div className="bg-gray-50 border-b border-gray-200 grid grid-cols-3 gap-2 py-2 px-2 text-xs font-medium text-gray-600">
            <div className="text-right">가격</div>
            <div className="text-right">수량</div>
            <div className="text-right">누적</div>
          </div>
        )}

        {/* Ask levels (매도, sell orders) */}
        <div className="border-b border-gray-200">
          {displayAsks.map((level, index) => (
            <LevelRow
              key={`ask-${level.price}-${index}`}
              level={level}
              maxVolume={maxVolume}
              type="ask"
              highlight={index === displayAsks.length - 1}
              flash={flashingLevels.has(`ask-${level.price}`)}
            />
          ))}
        </div>

        {/* Spread display */}
        {detailed && (
          <SpreadDisplay
            spread={data.spread}
            spreadPct={data.spread_pct}
            midPrice={data.mid_price}
          />
        )}

        {/* Bid levels (매수, buy orders) */}
        <div className="border-b border-gray-200">
          {displayBids.map((level, index) => (
            <LevelRow
              key={`bid-${level.price}-${index}`}
              level={level}
              maxVolume={maxVolume}
              type="bid"
              highlight={index === 0}
              flash={flashingLevels.has(`bid-${level.price}`)}
            />
          ))}
        </div>

        {/* Order imbalance indicator */}
        {detailed && <ImbalanceIndicator imbalance={imbalance} />}
      </div>
    )
  },
)

OrderBook.displayName = 'OrderBook'

export default OrderBook
