/**
 * Watchlist Prices Hook (FE-008 Phase 4)
 *
 * Custom hook for managing real-time price updates for all stocks in watchlists
 *
 * Features:
 * - Real-time price updates via WebSocket
 * - Automatic subscription to all watchlist stocks
 * - Dynamic subscription management when stocks change
 * - Error handling and reconnection
 */

import { useEffect, useRef, useState } from 'react'
import {
  WebSocketService,
  createWebSocketService,
  WSConnectionState,
} from '@/services/websocketService'
import { useWatchlistStore } from '@/store/watchlistStore'

/**
 * Watchlist prices hook return type
 */
export interface UseWatchlistPricesReturn {
  /** WebSocket connection state */
  connectionState: WSConnectionState
  /** Whether prices are updating */
  isConnected: boolean
  /** Error state */
  error: string | null
  /** Number of active subscriptions */
  subscriptionCount: number
}

/**
 * Watchlist Prices Hook
 *
 * Automatically subscribes to price updates for all stocks in all watchlists.
 * Updates are applied directly to the watchlistStore in real-time.
 *
 * @param enabled - Whether to enable real-time updates (default: true)
 * @returns Connection state and controls
 *
 * @example
 * ```tsx
 * const { connectionState, isConnected, subscriptionCount } = useWatchlistPrices()
 *
 * return (
 *   <div>
 *     <span>Status: {connectionState}</span>
 *     <span>Subscriptions: {subscriptionCount}</span>
 *   </div>
 * )
 * ```
 */
export function useWatchlistPrices(
  enabled: boolean = true,
): UseWatchlistPricesReturn {
  const [connectionState, setConnectionState] =
    useState<WSConnectionState>('disconnected')
  const [error, setError] = useState<string | null>(null)
  const [subscriptionCount, setSubscriptionCount] = useState<number>(0)

  const wsServiceRef = useRef<WebSocketService | null>(null)
  const subscribedCodesRef = useRef<Set<string>>(new Set())

  // Get watchlists and updateStockPrice from store
  const watchlists = useWatchlistStore(state => state.watchlists)
  const updateStockPrice = useWatchlistStore(state => state.updateStockPrice)

  /**
   * Initialize WebSocket connection and manage subscriptions
   */
  useEffect(() => {
    if (!enabled) {
      return
    }

    // Get JWT token from localStorage (set by authService)
    const token = localStorage.getItem('access_token')
    if (!token) {
      // User not authenticated, skip WebSocket connection
      setConnectionState('disconnected')
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
          setError(null)
        } else if (state === 'error') {
          setError('Connection error')
        }
      })

      // Handle incoming messages
      const unsubscribeMessage = wsService.onMessage(message => {
        if (message.type === 'price_update') {
          const priceMessage = message as {
            type: 'price_update'
            data: {
              stock_code: string
              price: number
              change: number
              change_pct: number
              volume: number
            }
          }

          const { stock_code, price, change, change_pct, volume } =
            priceMessage.data

          // Update stock price in all watchlists containing this stock
          updateStockPrice(stock_code, price, change, change_pct, volume)
        } else if (message.type === 'error') {
          const errorMessage = message as {
            type: 'error'
            error: { message: string }
          }
          console.error('WebSocket error:', errorMessage)
          setError(errorMessage.error?.message || 'Unknown error')
        }
      })

      // Connect to WebSocket
      wsService.connect()

      // Cleanup function
      return () => {
        unsubscribeState()
        unsubscribeMessage()

        // Unsubscribe from all stocks
        subscribedCodesRef.current.forEach(code => {
          wsService.unsubscribe('stock', code)
        })
        subscribedCodesRef.current.clear()

        wsService.disconnect()
      }
    } catch (err) {
      console.error('Failed to initialize WebSocket:', err)
      setError('Failed to connect')
    }
  }, [enabled, updateStockPrice])

  /**
   * Update subscriptions when watchlists change
   */
  useEffect(() => {
    const wsService = wsServiceRef.current
    if (!wsService || connectionState !== 'connected') {
      return
    }

    // Collect all unique stock codes from all watchlists
    const allStockCodes = new Set<string>()
    watchlists.forEach(watchlist => {
      watchlist.stocks.forEach(stock => {
        allStockCodes.add(stock.code)
      })
    })

    // Determine which stocks to subscribe/unsubscribe
    const currentCodes = subscribedCodesRef.current
    const newCodes = allStockCodes

    // Unsubscribe from stocks no longer in watchlists
    currentCodes.forEach(code => {
      if (!newCodes.has(code)) {
        wsService.unsubscribe('stock', code)
        currentCodes.delete(code)
      }
    })

    // Subscribe to new stocks
    newCodes.forEach(code => {
      if (!currentCodes.has(code)) {
        wsService.subscribe('stock', code)
        currentCodes.add(code)
      }
    })

    // Update subscription count
    setSubscriptionCount(currentCodes.size)
  }, [watchlists, connectionState])

  return {
    connectionState,
    isConnected: connectionState === 'connected',
    error,
    subscriptionCount,
  }
}
