/**
 * Order Book Hook (FE-005)
 *
 * Custom hook for managing real-time order book data via WebSocket
 *
 * Features:
 * - Real-time order book updates
 * - Automatic subscription management
 * - Spread and imbalance calculations
 * - Error handling and reconnection
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { OrderBookData, OrderImbalance } from '@/types/stock'
import {
  WebSocketService,
  createWebSocketService,
  WSConnectionState,
} from '@/services/websocketService'

/**
 * Order book hook return type
 */
export interface UseOrderBookReturn {
  /** Current order book data */
  orderBook: OrderBookData | null
  /** Order imbalance indicator */
  imbalance: OrderImbalance | null
  /** WebSocket connection state */
  connectionState: WSConnectionState
  /** Loading state */
  isLoading: boolean
  /** Error state */
  error: string | null
  /** Manually refresh order book */
  refresh: () => void
  /** Freeze/unfreeze updates */
  frozen: boolean
  /** Toggle freeze state */
  toggleFreeze: () => void
}

/**
 * Calculate order imbalance from order book data
 */
function calculateImbalance(orderBook: OrderBookData): OrderImbalance {
  const totalBidVolume = orderBook.bids.reduce(
    (sum, level) => sum + level.volume,
    0,
  )
  const totalAskVolume = orderBook.asks.reduce(
    (sum, level) => sum + level.volume,
    0,
  )
  const totalVolume = totalBidVolume + totalAskVolume

  const imbalanceRatio = totalVolume > 0 ? totalBidVolume / totalVolume : 0.5

  let direction: 'buy' | 'sell' | 'neutral' = 'neutral'
  if (imbalanceRatio > 0.55) {
    direction = 'buy'
  } else if (imbalanceRatio < 0.45) {
    direction = 'sell'
  }

  return {
    total_bid_volume: totalBidVolume,
    total_ask_volume: totalAskVolume,
    imbalance_ratio: imbalanceRatio,
    direction,
  }
}

/**
 * Enhance order book data with calculated fields
 */
function enhanceOrderBook(data: OrderBookData): OrderBookData {
  const bestBid = data.bids.length > 0 ? data.bids[0].price : undefined
  const bestAsk = data.asks.length > 0 ? data.asks[0].price : undefined

  let spread: number | undefined
  let spreadPct: number | undefined
  let midPrice: number | undefined

  if (bestBid !== undefined && bestAsk !== undefined) {
    spread = bestAsk - bestBid
    midPrice = (bestBid + bestAsk) / 2
    spreadPct = (spread / midPrice) * 100
  }

  return {
    ...data,
    best_bid: bestBid,
    best_ask: bestAsk,
    spread,
    spread_pct: spreadPct,
    mid_price: midPrice,
  }
}

/**
 * Order Book Hook
 *
 * @param stockCode - Stock code to subscribe to (e.g., '005930')
 * @param enabled - Whether to enable the hook (default: true)
 * @returns Order book data and controls
 *
 * @example
 * ```tsx
 * const { orderBook, imbalance, connectionState, frozen, toggleFreeze } = useOrderBook('005930')
 *
 * if (connectionState !== 'connected') {
 *   return <div>Connecting...</div>
 * }
 *
 * return (
 *   <div>
 *     <button onClick={toggleFreeze}>{frozen ? 'Unfreeze' : 'Freeze'}</button>
 *     <OrderBook data={orderBook} imbalance={imbalance} />
 *   </div>
 * )
 * ```
 */
export function useOrderBook(
  stockCode: string | undefined,
  enabled: boolean = true,
): UseOrderBookReturn {
  const [orderBook, setOrderBook] = useState<OrderBookData | null>(null)
  const [imbalance, setImbalance] = useState<OrderImbalance | null>(null)
  const [connectionState, setConnectionState] =
    useState<WSConnectionState>('disconnected')
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [frozen, setFrozen] = useState<boolean>(false)

  const wsServiceRef = useRef<WebSocketService | null>(null)

  /**
   * Toggle freeze state
   */
  const toggleFreeze = useCallback(() => {
    setFrozen(prev => !prev)
  }, [])

  /**
   * Manual refresh (re-subscribe)
   */
  const refresh = useCallback(() => {
    if (wsServiceRef.current && stockCode) {
      wsServiceRef.current.unsubscribe('stock', stockCode)
      wsServiceRef.current.subscribe('stock', stockCode)
    }
  }, [stockCode])

  /**
   * Initialize WebSocket connection
   */
  useEffect(() => {
    if (!enabled || !stockCode) {
      return
    }

    // Get JWT token from localStorage (set by authService)
    const token = localStorage.getItem('access_token')
    if (!token) {
      setError('Authentication required')
      setIsLoading(false)
      return
    }

    try {
      // Create WebSocket service
      const wsService = createWebSocketService(token)
      wsServiceRef.current = wsService

      // Handle state changes
      const unsubscribeState = wsService.onStateChange(state => {
        setConnectionState(state)

        if (state === 'connected') {
          setIsLoading(false)
          setError(null)
        } else if (state === 'error') {
          setError('Connection error')
          setIsLoading(false)
        }
      })

      // Handle incoming messages
      const unsubscribeMessage = wsService.onMessage(message => {
        // Skip updates if frozen
        if (frozen) {
          return
        }

        if (message.type === 'orderbook_update') {
          const orderBookMessage = message as {
            type: 'orderbook_update'
            data: OrderBookData
          }
          const data = orderBookMessage.data

          // Only process updates for the subscribed stock
          if (data.stock_code === stockCode) {
            const enhanced = enhanceOrderBook(data)
            setOrderBook(enhanced)
            setImbalance(calculateImbalance(enhanced))
          }
        } else if (message.type === 'error') {
          const errorMessage = message as {
            type: 'error'
            error: { message: string }
          }
          console.error('WebSocket error:', errorMessage)
          setError(errorMessage.error?.message || 'Unknown error')
        }
      })

      // Connect and subscribe
      wsService.connect()
      wsService.subscribe('stock', stockCode)

      // Cleanup function
      return () => {
        unsubscribeState()
        unsubscribeMessage()
        wsService.unsubscribe('stock', stockCode)
        wsService.disconnect()
      }
    } catch (err) {
      console.error('Failed to initialize WebSocket:', err)
      setError('Failed to connect')
      setIsLoading(false)
    }
  }, [stockCode, enabled, frozen])

  return {
    orderBook,
    imbalance,
    connectionState,
    isLoading,
    error,
    refresh,
    frozen,
    toggleFreeze,
  }
}
