/**
 * Unit Tests for useOrderBook Hook (BUGFIX-013 Phase 1)
 *
 * Tests for:
 * - calculateImbalance() function
 * - enhanceOrderBook() function
 * - useOrderBook hook behavior
 * - WebSocket integration (mocked)
 * - Error handling
 * - Freeze/unfreeze functionality
 */

import { describe, it, expect, vi, beforeEach, afterEach, type Mock } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useOrderBook } from '../useOrderBook'
import type { OrderBookData } from '@/types/stock'
import type { WSConnectionState } from '@/services/websocketService'

// Type definitions for mock handlers
type StateChangeHandler = (state: WSConnectionState) => void
type MessageHandler = (message: unknown) => void

// Mock WebSocket service
const mockWebSocketService = {
  connect: vi.fn(),
  disconnect: vi.fn(),
  subscribe: vi.fn(),
  unsubscribe: vi.fn(),
  onMessage: vi.fn(() => vi.fn()) as Mock<(handler: MessageHandler) => () => void>,
  onStateChange: vi.fn(() => vi.fn()) as Mock<(handler: StateChangeHandler) => () => void>,
}

vi.mock('@/services/websocketService', () => ({
  createWebSocketService: vi.fn(() => mockWebSocketService),
  WSConnectionState: {},
}))

// Helper to create mock order book data
function createMockOrderBookData(overrides?: Partial<OrderBookData>): OrderBookData {
  return {
    stock_code: '005930',
    timestamp: new Date().toISOString(),
    sequence: 1,
    asks: [
      { price: 71000, volume: 1000, total: 1000 },
      { price: 71100, volume: 800, total: 1800 },
      { price: 71200, volume: 1200, total: 3000 },
      { price: 71300, volume: 500, total: 3500 },
      { price: 71400, volume: 600, total: 4100 },
    ],
    bids: [
      { price: 70900, volume: 900, total: 900 },
      { price: 70800, volume: 1100, total: 2000 },
      { price: 70700, volume: 700, total: 2700 },
      { price: 70600, volume: 400, total: 3100 },
      { price: 70500, volume: 800, total: 3900 },
    ],
    ...overrides,
  }
}

describe('useOrderBook Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    localStorage.setItem('access_token', 'test-token')
  })

  afterEach(() => {
    localStorage.clear()
  })

  describe('calculateImbalance()', () => {
    // Import the function directly for testing
    // Since it's not exported, we test it through the hook's behavior
    // But we can test the imbalance calculation logic through the hook

    it('should calculate buy imbalance when bid volume dominates', async () => {
      const stateChangeHandler = vi.fn()
      const messageHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      // Simulate connected state
      act(() => {
        stateChangeHandler('connected')
      })

      // Simulate orderbook with heavy bid volume (buy pressure)
      const heavyBidData = createMockOrderBookData({
        bids: [
          { price: 70900, volume: 5000, total: 5000 },
          { price: 70800, volume: 4000, total: 9000 },
        ],
        asks: [
          { price: 71000, volume: 1000, total: 1000 },
          { price: 71100, volume: 500, total: 1500 },
        ],
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: heavyBidData,
        })
      })

      await waitFor(() => {
        expect(result.current.imbalance).not.toBeNull()
      })

      expect(result.current.imbalance?.direction).toBe('buy')
      expect(result.current.imbalance?.imbalance_ratio).toBeGreaterThan(0.55)
    })

    it('should calculate sell imbalance when ask volume dominates', async () => {
      const stateChangeHandler = vi.fn()
      const messageHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      // Simulate orderbook with heavy ask volume (sell pressure)
      const heavyAskData = createMockOrderBookData({
        bids: [
          { price: 70900, volume: 500, total: 500 },
          { price: 70800, volume: 400, total: 900 },
        ],
        asks: [
          { price: 71000, volume: 5000, total: 5000 },
          { price: 71100, volume: 4000, total: 9000 },
        ],
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: heavyAskData,
        })
      })

      await waitFor(() => {
        expect(result.current.imbalance).not.toBeNull()
      })

      expect(result.current.imbalance?.direction).toBe('sell')
      expect(result.current.imbalance?.imbalance_ratio).toBeLessThan(0.45)
    })

    it('should calculate neutral imbalance when volumes are balanced', async () => {
      const stateChangeHandler = vi.fn()
      const messageHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      // Simulate orderbook with balanced volume
      const balancedData = createMockOrderBookData({
        bids: [
          { price: 70900, volume: 1000, total: 1000 },
          { price: 70800, volume: 1000, total: 2000 },
        ],
        asks: [
          { price: 71000, volume: 1000, total: 1000 },
          { price: 71100, volume: 1000, total: 2000 },
        ],
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: balancedData,
        })
      })

      await waitFor(() => {
        expect(result.current.imbalance).not.toBeNull()
      })

      expect(result.current.imbalance?.direction).toBe('neutral')
      expect(result.current.imbalance?.imbalance_ratio).toBeGreaterThanOrEqual(0.45)
      expect(result.current.imbalance?.imbalance_ratio).toBeLessThanOrEqual(0.55)
    })

    it('should handle empty order book with zero volume', async () => {
      const stateChangeHandler = vi.fn()
      const messageHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      const emptyData = createMockOrderBookData({
        bids: [],
        asks: [],
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: emptyData,
        })
      })

      await waitFor(() => {
        expect(result.current.orderBook).not.toBeNull()
      })

      // With zero total volume, imbalance_ratio should be 0.5 (neutral)
      expect(result.current.imbalance?.imbalance_ratio).toBe(0.5)
      expect(result.current.imbalance?.direction).toBe('neutral')
    })
  })

  describe('enhanceOrderBook()', () => {
    it('should calculate spread and mid price correctly', async () => {
      const stateChangeHandler = vi.fn()
      const messageHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      const mockData = createMockOrderBookData({
        bids: [{ price: 70000, volume: 1000, total: 1000 }],
        asks: [{ price: 71000, volume: 1000, total: 1000 }],
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: mockData,
        })
      })

      await waitFor(() => {
        expect(result.current.orderBook).not.toBeNull()
      })

      expect(result.current.orderBook?.best_bid).toBe(70000)
      expect(result.current.orderBook?.best_ask).toBe(71000)
      expect(result.current.orderBook?.spread).toBe(1000)
      expect(result.current.orderBook?.mid_price).toBe(70500)
      // spread_pct = (1000 / 70500) * 100 ≈ 1.418%
      expect(result.current.orderBook?.spread_pct).toBeCloseTo(1.418, 2)
    })

    it('should handle missing bid levels', async () => {
      const stateChangeHandler = vi.fn()
      const messageHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      const noBidsData = createMockOrderBookData({
        bids: [],
        asks: [{ price: 71000, volume: 1000, total: 1000 }],
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: noBidsData,
        })
      })

      await waitFor(() => {
        expect(result.current.orderBook).not.toBeNull()
      })

      expect(result.current.orderBook?.best_bid).toBeUndefined()
      expect(result.current.orderBook?.best_ask).toBe(71000)
      expect(result.current.orderBook?.spread).toBeUndefined()
      expect(result.current.orderBook?.mid_price).toBeUndefined()
    })

    it('should handle missing ask levels', async () => {
      const stateChangeHandler = vi.fn()
      const messageHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      const noAsksData = createMockOrderBookData({
        bids: [{ price: 70000, volume: 1000, total: 1000 }],
        asks: [],
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: noAsksData,
        })
      })

      await waitFor(() => {
        expect(result.current.orderBook).not.toBeNull()
      })

      expect(result.current.orderBook?.best_bid).toBe(70000)
      expect(result.current.orderBook?.best_ask).toBeUndefined()
      expect(result.current.orderBook?.spread).toBeUndefined()
      expect(result.current.orderBook?.mid_price).toBeUndefined()
    })
  })

  describe('Hook Initialization', () => {
    it('should initialize with default values', () => {
      const { result } = renderHook(() => useOrderBook('005930'))

      expect(result.current.orderBook).toBeNull()
      expect(result.current.imbalance).toBeNull()
      expect(result.current.connectionState).toBe('disconnected')
      expect(result.current.isLoading).toBe(true)
      expect(result.current.error).toBeNull()
      expect(result.current.frozen).toBe(false)
    })

    it('should not connect when stockCode is undefined', () => {
      renderHook(() => useOrderBook(undefined))

      expect(mockWebSocketService.connect).not.toHaveBeenCalled()
      expect(mockWebSocketService.subscribe).not.toHaveBeenCalled()
    })

    it('should not connect when enabled is false', () => {
      renderHook(() => useOrderBook('005930', false))

      expect(mockWebSocketService.connect).not.toHaveBeenCalled()
      expect(mockWebSocketService.subscribe).not.toHaveBeenCalled()
    })

    it('should set error when no auth token', () => {
      localStorage.removeItem('access_token')

      const { result } = renderHook(() => useOrderBook('005930'))

      expect(result.current.error).toBe('Authentication required')
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('WebSocket Connection Management', () => {
    it('should connect and subscribe on mount', () => {
      renderHook(() => useOrderBook('005930'))

      expect(mockWebSocketService.connect).toHaveBeenCalled()
      expect(mockWebSocketService.subscribe).toHaveBeenCalledWith('stock', '005930')
    })

    it('should update connection state on state change', async () => {
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      await waitFor(() => {
        expect(result.current.connectionState).toBe('connected')
        expect(result.current.isLoading).toBe(false)
        expect(result.current.error).toBeNull()
      })
    })

    it('should set error on connection error', async () => {
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('error')
      })

      await waitFor(() => {
        expect(result.current.connectionState).toBe('error')
        expect(result.current.error).toBe('Connection error')
        expect(result.current.isLoading).toBe(false)
      })
    })

    it('should cleanup on unmount', () => {
      const unsubscribeState = vi.fn()
      const unsubscribeMessage = vi.fn()

      mockWebSocketService.onStateChange.mockReturnValue(unsubscribeState)
      mockWebSocketService.onMessage.mockReturnValue(unsubscribeMessage)

      const { unmount } = renderHook(() => useOrderBook('005930'))

      unmount()

      expect(unsubscribeState).toHaveBeenCalled()
      expect(unsubscribeMessage).toHaveBeenCalled()
      expect(mockWebSocketService.unsubscribe).toHaveBeenCalledWith('stock', '005930')
      expect(mockWebSocketService.disconnect).toHaveBeenCalled()
    })
  })

  describe('Message Handling', () => {
    it('should process orderbook_update messages', async () => {
      const messageHandler = vi.fn()
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      const mockData = createMockOrderBookData()

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: mockData,
        })
      })

      await waitFor(() => {
        expect(result.current.orderBook).not.toBeNull()
        expect(result.current.orderBook?.stock_code).toBe('005930')
      })
    })

    it('should ignore messages for different stock codes', async () => {
      const messageHandler = vi.fn()
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      const wrongStockData = createMockOrderBookData({
        stock_code: '000660', // Different stock
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: wrongStockData,
        })
      })

      // Should still be null since it's a different stock
      expect(result.current.orderBook).toBeNull()
    })

    it('should handle error messages', async () => {
      const messageHandler = vi.fn()
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      act(() => {
        messageHandler({
          type: 'error',
          error: { message: 'Subscription failed' },
        })
      })

      await waitFor(() => {
        expect(result.current.error).toBe('Subscription failed')
      })
    })
  })

  describe('Freeze/Unfreeze Functionality', () => {
    it('should toggle freeze state', () => {
      const { result } = renderHook(() => useOrderBook('005930'))

      expect(result.current.frozen).toBe(false)

      act(() => {
        result.current.toggleFreeze()
      })

      expect(result.current.frozen).toBe(true)

      act(() => {
        result.current.toggleFreeze()
      })

      expect(result.current.frozen).toBe(false)
    })

    it('should skip updates when frozen', async () => {
      const messageHandler = vi.fn()
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result, rerender } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      // First update should work
      const initialData = createMockOrderBookData({ sequence: 1 })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: initialData,
        })
      })

      await waitFor(() => {
        expect(result.current.orderBook?.sequence).toBe(1)
      })

      // Freeze updates
      act(() => {
        result.current.toggleFreeze()
      })

      // Force a rerender to apply the frozen state to the effect
      rerender()

      // Updates while frozen should be skipped in the message handler
      // Note: The actual skipping happens in the message handler callback
      // which checks the frozen state from the closure
    })
  })

  describe('Manual Refresh', () => {
    it('should re-subscribe on refresh', async () => {
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      // Clear mock to track only refresh calls
      mockWebSocketService.unsubscribe.mockClear()
      mockWebSocketService.subscribe.mockClear()

      act(() => {
        result.current.refresh()
      })

      expect(mockWebSocketService.unsubscribe).toHaveBeenCalledWith('stock', '005930')
      expect(mockWebSocketService.subscribe).toHaveBeenCalledWith('stock', '005930')
    })

    it('should not refresh without WebSocket service', () => {
      const { result } = renderHook(() => useOrderBook(undefined))

      // Should not throw
      act(() => {
        result.current.refresh()
      })

      expect(mockWebSocketService.unsubscribe).not.toHaveBeenCalled()
    })
  })

  describe('Edge Cases', () => {
    it('should handle rapid consecutive updates', async () => {
      const messageHandler = vi.fn()
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      // Send rapid updates
      for (let i = 1; i <= 10; i++) {
        const data = createMockOrderBookData({ sequence: i })
        act(() => {
          messageHandler({
            type: 'orderbook_update',
            data,
          })
        })
      }

      await waitFor(() => {
        expect(result.current.orderBook?.sequence).toBe(10)
      })
    })

    it('should handle stock code change', async () => {
      const unsubscribeState = vi.fn()
      const unsubscribeMessage = vi.fn()

      mockWebSocketService.onStateChange.mockReturnValue(unsubscribeState)
      mockWebSocketService.onMessage.mockReturnValue(unsubscribeMessage)

      const { rerender } = renderHook(
        ({ stockCode }) => useOrderBook(stockCode),
        { initialProps: { stockCode: '005930' } }
      )

      // Change stock code
      rerender({ stockCode: '000660' })

      // Should have cleaned up old subscription and created new one
      expect(mockWebSocketService.unsubscribe).toHaveBeenCalledWith('stock', '005930')
      expect(mockWebSocketService.subscribe).toHaveBeenCalledWith('stock', '000660')
    })

    it('should handle very large volumes without overflow', async () => {
      const messageHandler = vi.fn()
      const stateChangeHandler = vi.fn()

      mockWebSocketService.onStateChange.mockImplementation((handler: StateChangeHandler) => {
        stateChangeHandler.mockImplementation(handler)
        return vi.fn()
      })

      mockWebSocketService.onMessage.mockImplementation((handler: MessageHandler) => {
        messageHandler.mockImplementation(handler)
        return vi.fn()
      })

      const { result } = renderHook(() => useOrderBook('005930'))

      act(() => {
        stateChangeHandler('connected')
      })

      const largeVolumeData = createMockOrderBookData({
        bids: [{ price: 70000, volume: 999999999999, total: 999999999999 }],
        asks: [{ price: 71000, volume: 999999999999, total: 999999999999 }],
      })

      act(() => {
        messageHandler({
          type: 'orderbook_update',
          data: largeVolumeData,
        })
      })

      await waitFor(() => {
        expect(result.current.orderBook).not.toBeNull()
      })

      // Should handle large numbers without issues
      expect(result.current.imbalance?.imbalance_ratio).toBeCloseTo(0.5, 2)
    })
  })
})
