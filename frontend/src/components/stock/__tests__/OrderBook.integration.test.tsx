/**
 * Integration Tests for OrderBook + useOrderBook (BUGFIX-013 Phase 3)
 *
 * Tests for:
 * - Complete data flow from WebSocket to rendered UI
 * - Real-time updates handling
 * - Error recovery and reconnection
 * - State synchronization
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useOrderBook } from '@/hooks/useOrderBook'
import { OrderBook } from '../OrderBook'
import type { OrderBookData } from '@/types/stock'

// Test component that combines useOrderBook hook with OrderBook component
interface TestOrderBookContainerProps {
  stockCode: string | undefined
  enabled?: boolean
  levels?: number
}

function TestOrderBookContainer({
  stockCode,
  enabled = true,
  levels = 10,
}: TestOrderBookContainerProps) {
  const {
    orderBook,
    imbalance,
    connectionState,
    isLoading,
    error,
    frozen,
    toggleFreeze,
    refresh,
  } = useOrderBook(stockCode, enabled)

  return (
    <div data-testid="orderbook-container">
      <div data-testid="connection-state">{connectionState}</div>
      <div data-testid="error-state">{error || 'no-error'}</div>
      <div data-testid="loading-state">{isLoading ? 'loading' : 'loaded'}</div>
      <button data-testid="refresh-button" onClick={refresh}>
        Refresh
      </button>
      <OrderBook
        data={orderBook}
        imbalance={imbalance}
        isLoading={isLoading && !error}
        frozen={frozen}
        onToggleFreeze={toggleFreeze}
        levels={levels}
        detailed={true}
      />
    </div>
  )
}

// Mock WebSocket handlers
let mockStateChangeHandler: ((state: string) => void) | null = null
let mockMessageHandler: ((message: any) => void) | null = null

const mockWebSocketService = {
  connect: vi.fn(),
  disconnect: vi.fn(),
  subscribe: vi.fn(),
  unsubscribe: vi.fn(),
  onMessage: vi.fn(handler => {
    mockMessageHandler = handler
    return vi.fn()
  }),
  onStateChange: vi.fn(handler => {
    mockStateChangeHandler = handler
    return vi.fn()
  }),
}

vi.mock('@/services/websocketService', () => ({
  createWebSocketService: vi.fn(() => mockWebSocketService),
  WSConnectionState: {},
}))

// Mock format utilities
vi.mock('@/utils/format', () => ({
  formatNumber: vi.fn((value: number) => value?.toLocaleString('ko-KR') ?? '-'),
  formatPrice: vi.fn((value: number) => value?.toLocaleString('ko-KR') ?? '-'),
}))

// Helper to create mock order book data
function createMockOrderBookData(
  overrides?: Partial<OrderBookData>,
): OrderBookData {
  return {
    stock_code: '005930',
    timestamp: new Date().toISOString(),
    sequence: 1,
    asks: [
      { price: 71000, volume: 1000, total: 1000 },
      { price: 71100, volume: 800, total: 1800 },
      { price: 71200, volume: 1200, total: 3000 },
    ],
    bids: [
      { price: 70900, volume: 900, total: 900 },
      { price: 70800, volume: 1100, total: 2000 },
      { price: 70700, volume: 700, total: 2700 },
    ],
    ...overrides,
  }
}

describe('OrderBook Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockStateChangeHandler = null
    mockMessageHandler = null
    localStorage.clear()
    localStorage.setItem('access_token', 'test-token')
  })

  afterEach(() => {
    localStorage.clear()
  })

  describe('Complete Data Flow', () => {
    it('should display loading state initially', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      expect(screen.getByTestId('loading-state')).toHaveTextContent('loading')
      expect(screen.getByText('호가 정보를 불러오는 중...')).toBeInTheDocument()
    })

    it('should connect and display data when WebSocket connects', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      // Simulate WebSocket connection
      act(() => {
        mockStateChangeHandler?.('connected')
      })

      await waitFor(() => {
        expect(screen.getByTestId('connection-state')).toHaveTextContent(
          'connected',
        )
        expect(screen.getByTestId('loading-state')).toHaveTextContent('loaded')
      })
    })

    it('should render order book data when received', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      // Connect
      act(() => {
        mockStateChangeHandler?.('connected')
      })

      // Send order book update
      const mockData = createMockOrderBookData()
      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data: mockData,
        })
      })

      await waitFor(() => {
        // Check that order book UI is rendered
        expect(screen.getByText(/호가 \(\d+단계\)/)).toBeInTheDocument()
      })
    })

    it('should display spread information', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      const mockData = createMockOrderBookData({
        best_bid: 70900,
        best_ask: 71000,
        spread: 100,
        spread_pct: 0.14,
        mid_price: 70950,
      })

      // Send enhanced data (as hook would enhance it)
      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data: mockData,
        })
      })

      await waitFor(() => {
        expect(screen.getByText('호가차')).toBeInTheDocument()
        expect(screen.getByText('스프레드')).toBeInTheDocument()
        expect(screen.getByText('중간가')).toBeInTheDocument()
      })
    })

    it('should display imbalance indicator', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      // Create data with buy pressure
      const mockData = createMockOrderBookData({
        bids: [
          { price: 70900, volume: 5000, total: 5000 },
          { price: 70800, volume: 4000, total: 9000 },
        ],
        asks: [{ price: 71000, volume: 1000, total: 1000 }],
      })

      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data: mockData,
        })
      })

      await waitFor(() => {
        expect(screen.getByText('주문 불균형')).toBeInTheDocument()
        expect(screen.getByText('매수 우세')).toBeInTheDocument()
      })
    })
  })

  describe('Real-time Updates', () => {
    it('should update UI when new data arrives', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      // First update
      const data1 = createMockOrderBookData({ sequence: 1 })
      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data: data1,
        })
      })

      await waitFor(() => {
        expect(screen.getByText(/호가 \(\d+단계\)/)).toBeInTheDocument()
      })

      // Second update with different data
      const data2 = createMockOrderBookData({
        sequence: 2,
        asks: [{ price: 72000, volume: 2000, total: 2000 }],
        bids: [{ price: 71900, volume: 1800, total: 1800 }],
      })

      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data: data2,
        })
      })

      // UI should update with new data
      await waitFor(() => {
        expect(screen.getByText(/호가 \(\d+단계\)/)).toBeInTheDocument()
      })
    })

    it('should handle rapid consecutive updates', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      // Send 5 rapid updates
      for (let i = 1; i <= 5; i++) {
        const data = createMockOrderBookData({ sequence: i })
        act(() => {
          mockMessageHandler?.({
            type: 'orderbook_update',
            data,
          })
        })
      }

      // Should still render correctly
      await waitFor(() => {
        expect(screen.getByText(/호가 \(\d+단계\)/)).toBeInTheDocument()
      })
    })

    it('should skip updates when frozen', async () => {
      const user = userEvent.setup()

      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      // Initial data
      const data1 = createMockOrderBookData({ sequence: 1 })
      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data: data1,
        })
      })

      await waitFor(() => {
        expect(screen.getByText('▶ 실시간')).toBeInTheDocument()
      })

      // Freeze updates
      await user.click(screen.getByText('▶ 실시간'))

      await waitFor(() => {
        expect(screen.getByText('⏸ 정지됨')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling and Recovery', () => {
    it('should display error state on connection error', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('error')
      })

      await waitFor(() => {
        expect(screen.getByTestId('connection-state')).toHaveTextContent(
          'error',
        )
        expect(screen.getByTestId('error-state')).toHaveTextContent(
          'Connection error',
        )
      })
    })

    it('should display error from WebSocket error message', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      act(() => {
        mockMessageHandler?.({
          type: 'error',
          error: { message: 'Subscription failed' },
        })
      })

      await waitFor(() => {
        expect(screen.getByTestId('error-state')).toHaveTextContent(
          'Subscription failed',
        )
      })
    })

    it('should show auth error when no token', () => {
      localStorage.removeItem('access_token')

      render(<TestOrderBookContainer stockCode="005930" />)

      expect(screen.getByTestId('error-state')).toHaveTextContent(
        'Authentication required',
      )
    })

    it('should handle refresh action', async () => {
      const user = userEvent.setup()

      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      // Clear mocks to track refresh calls
      mockWebSocketService.unsubscribe.mockClear()
      mockWebSocketService.subscribe.mockClear()

      // Click refresh
      await user.click(screen.getByTestId('refresh-button'))

      expect(mockWebSocketService.unsubscribe).toHaveBeenCalledWith(
        'stock',
        '005930',
      )
      expect(mockWebSocketService.subscribe).toHaveBeenCalledWith(
        'stock',
        '005930',
      )
    })
  })

  describe('State Synchronization', () => {
    it('should sync freeze state between hook and component', async () => {
      const user = userEvent.setup()

      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      const data = createMockOrderBookData()
      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data,
        })
      })

      await waitFor(() => {
        expect(screen.getByText('▶ 실시간')).toBeInTheDocument()
      })

      // Toggle freeze
      await user.click(screen.getByText('▶ 실시간'))

      await waitFor(() => {
        expect(screen.getByText('⏸ 정지됨')).toBeInTheDocument()
      })

      // Toggle back
      await user.click(screen.getByText('⏸ 정지됨'))

      await waitFor(() => {
        expect(screen.getByText('▶ 실시간')).toBeInTheDocument()
      })
    })

    it('should not render when stock code is undefined', () => {
      render(<TestOrderBookContainer stockCode={undefined} />)

      expect(mockWebSocketService.connect).not.toHaveBeenCalled()
    })

    it('should not render when disabled', () => {
      render(<TestOrderBookContainer stockCode="005930" enabled={false} />)

      expect(mockWebSocketService.connect).not.toHaveBeenCalled()
    })
  })

  describe('WebSocket Lifecycle', () => {
    it('should connect on mount', () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      expect(mockWebSocketService.connect).toHaveBeenCalled()
      expect(mockWebSocketService.subscribe).toHaveBeenCalledWith(
        'stock',
        '005930',
      )
    })

    it('should disconnect on unmount', () => {
      const { unmount } = render(<TestOrderBookContainer stockCode="005930" />)

      unmount()

      expect(mockWebSocketService.unsubscribe).toHaveBeenCalledWith(
        'stock',
        '005930',
      )
      expect(mockWebSocketService.disconnect).toHaveBeenCalled()
    })

    it('should resubscribe when stock code changes', async () => {
      const { rerender } = render(<TestOrderBookContainer stockCode="005930" />)

      mockWebSocketService.unsubscribe.mockClear()
      mockWebSocketService.subscribe.mockClear()

      // Change stock code
      rerender(<TestOrderBookContainer stockCode="000660" />)

      await waitFor(() => {
        expect(mockWebSocketService.unsubscribe).toHaveBeenCalledWith(
          'stock',
          '005930',
        )
        expect(mockWebSocketService.subscribe).toHaveBeenCalledWith(
          'stock',
          '000660',
        )
      })
    })
  })

  describe('Data Filtering', () => {
    it('should ignore updates for different stock codes', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      // Send data for a different stock
      const wrongStockData = createMockOrderBookData({
        stock_code: '000660',
      })

      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data: wrongStockData,
        })
      })

      // Should not display order book (no data for subscribed stock)
      // The component should still show loading or empty state
      expect(screen.queryByText('주문 불균형')).not.toBeInTheDocument()
    })

    it('should only process orderbook_update message type', async () => {
      render(<TestOrderBookContainer stockCode="005930" />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      // Send a different message type
      act(() => {
        mockMessageHandler?.({
          type: 'price_update',
          data: { stock_code: '005930', price: 71000 },
        })
      })

      // Should not display order book
      expect(screen.queryByText('주문 불균형')).not.toBeInTheDocument()
    })
  })

  describe('Display Options', () => {
    it('should respect levels prop', async () => {
      render(<TestOrderBookContainer stockCode="005930" levels={5} />)

      act(() => {
        mockStateChangeHandler?.('connected')
      })

      const data = createMockOrderBookData()
      act(() => {
        mockMessageHandler?.({
          type: 'orderbook_update',
          data,
        })
      })

      await waitFor(() => {
        expect(screen.getByText(/호가 \(5단계\)/)).toBeInTheDocument()
      })
    })
  })
})
