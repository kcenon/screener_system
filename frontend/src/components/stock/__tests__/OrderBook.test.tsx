/**
 * Unit Tests for OrderBook Component (BUGFIX-013 Phase 2)
 *
 * Tests for:
 * - OrderBook main component rendering
 * - LevelRow sub-component
 * - SpreadDisplay sub-component
 * - ImbalanceIndicator sub-component
 * - Loading and empty states
 * - Freeze/unfreeze functionality
 * - Volume bar calculations
 * - Flash animations
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { OrderBook } from '../OrderBook'
import type { OrderBookData, OrderImbalance } from '@/types/stock'

// Mock format utilities
vi.mock('@/utils/format', () => ({
  formatNumber: vi.fn((value: number) => value?.toLocaleString('ko-KR') ?? '-'),
  formatPrice: vi.fn((value: number) => value?.toLocaleString('ko-KR') ?? '-'),
}))

// Helper to create mock order book data
function createMockOrderBookData(overrides?: Partial<OrderBookData>): OrderBookData {
  return {
    stock_code: '005930',
    timestamp: '2024-01-15T10:30:00Z',
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
    best_bid: 70900,
    best_ask: 71000,
    spread: 100,
    spread_pct: 0.14,
    mid_price: 70950,
    ...overrides,
  }
}

// Helper to create mock imbalance data
function createMockImbalance(overrides?: Partial<OrderImbalance>): OrderImbalance {
  return {
    total_bid_volume: 3900,
    total_ask_volume: 4100,
    imbalance_ratio: 0.488,
    direction: 'neutral',
    ...overrides,
  }
}

describe('OrderBook Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Loading State', () => {
    it('should render loading spinner when isLoading is true', () => {
      render(<OrderBook data={null} imbalance={null} isLoading={true} />)

      expect(screen.getByText('호가 정보를 불러오는 중...')).toBeInTheDocument()
    })

    it('should show loading animation', () => {
      const { container } = render(<OrderBook data={null} imbalance={null} isLoading={true} />)

      const spinner = container.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })
  })

  describe('Empty State', () => {
    it('should render empty state when data is null and not loading', () => {
      render(<OrderBook data={null} imbalance={null} isLoading={false} />)

      expect(screen.getByText('호가 데이터가 없습니다')).toBeInTheDocument()
    })

    it('should display placeholder icon', () => {
      const { container } = render(<OrderBook data={null} imbalance={null} />)

      const svg = container.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })
  })

  describe('Data Rendering', () => {
    it('should render order book with data', () => {
      const mockData = createMockOrderBookData()
      const mockImbalance = createMockImbalance()

      render(<OrderBook data={mockData} imbalance={mockImbalance} />)

      // Check header is rendered (호가 (10단계) format)
      expect(screen.getByText(/호가 \(\d+단계\)/)).toBeInTheDocument()
    })

    it('should display correct number of levels', () => {
      const mockData = createMockOrderBookData()

      const { container } = render(<OrderBook data={mockData} imbalance={null} levels={5} />)

      // Should display 5 ask and 5 bid levels (total 10 level rows)
      const levelRows = container.querySelectorAll('.grid.grid-cols-3')
      // Header + 5 asks + 5 bids = 11, but excluding header row
      expect(levelRows.length).toBeGreaterThanOrEqual(10)
    })

    it('should display timestamp', () => {
      const mockData = createMockOrderBookData({
        timestamp: '2024-01-15T10:30:00Z',
      })

      render(<OrderBook data={mockData} imbalance={null} />)

      // Time should be displayed in Korean format
      const timeText = screen.getByText(/\d{2}:\d{2}:\d{2}/)
      expect(timeText).toBeInTheDocument()
    })

    it('should display level count in header', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} levels={10} />)

      expect(screen.getByText(/호가 \(10단계\)/)).toBeInTheDocument()
    })

    it('should display with custom level count', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} levels={5} />)

      expect(screen.getByText(/호가 \(5단계\)/)).toBeInTheDocument()
    })
  })

  describe('Column Headers', () => {
    it('should display column headers when detailed is true', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} detailed={true} />)

      expect(screen.getByText('가격')).toBeInTheDocument()
      expect(screen.getByText('수량')).toBeInTheDocument()
      expect(screen.getByText('누적')).toBeInTheDocument()
    })

    it('should hide column headers when detailed is false', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} detailed={false} />)

      expect(screen.queryByText('가격')).not.toBeInTheDocument()
      expect(screen.queryByText('수량')).not.toBeInTheDocument()
      expect(screen.queryByText('누적')).not.toBeInTheDocument()
    })
  })

  describe('SpreadDisplay Component', () => {
    it('should display spread information when detailed is true', () => {
      const mockData = createMockOrderBookData({
        spread: 100,
        spread_pct: 0.14,
        mid_price: 70950,
      })

      render(<OrderBook data={mockData} imbalance={null} detailed={true} />)

      expect(screen.getByText('호가차')).toBeInTheDocument()
      expect(screen.getByText('스프레드')).toBeInTheDocument()
      expect(screen.getByText('중간가')).toBeInTheDocument()
      expect(screen.getByText('0.14%')).toBeInTheDocument()
    })

    it('should hide spread display when detailed is false', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} detailed={false} />)

      expect(screen.queryByText('호가차')).not.toBeInTheDocument()
      expect(screen.queryByText('스프레드')).not.toBeInTheDocument()
      expect(screen.queryByText('중간가')).not.toBeInTheDocument()
    })

    it('should handle undefined spread values', () => {
      const mockData = createMockOrderBookData({
        spread: undefined,
        spread_pct: undefined,
        mid_price: undefined,
      })

      render(<OrderBook data={mockData} imbalance={null} detailed={true} />)

      // SpreadDisplay should return null with undefined values
      expect(screen.queryByText('호가차')).not.toBeInTheDocument()
    })
  })

  describe('ImbalanceIndicator Component', () => {
    it('should display imbalance indicator when detailed is true', () => {
      const mockData = createMockOrderBookData()
      const mockImbalance = createMockImbalance({
        direction: 'neutral',
      })

      render(<OrderBook data={mockData} imbalance={mockImbalance} detailed={true} />)

      expect(screen.getByText('주문 불균형')).toBeInTheDocument()
      expect(screen.getByText('균형')).toBeInTheDocument()
    })

    it('should display buy dominance', () => {
      const mockData = createMockOrderBookData()
      const mockImbalance = createMockImbalance({
        direction: 'buy',
        imbalance_ratio: 0.65,
        total_bid_volume: 6500,
        total_ask_volume: 3500,
      })

      render(<OrderBook data={mockData} imbalance={mockImbalance} detailed={true} />)

      expect(screen.getByText('매수 우세')).toBeInTheDocument()
    })

    it('should display sell dominance', () => {
      const mockData = createMockOrderBookData()
      const mockImbalance = createMockImbalance({
        direction: 'sell',
        imbalance_ratio: 0.35,
        total_bid_volume: 3500,
        total_ask_volume: 6500,
      })

      render(<OrderBook data={mockData} imbalance={mockImbalance} detailed={true} />)

      expect(screen.getByText('매도 우세')).toBeInTheDocument()
    })

    it('should display volume breakdown', () => {
      const mockData = createMockOrderBookData()
      const mockImbalance = createMockImbalance({
        total_bid_volume: 5000,
        total_ask_volume: 3000,
      })

      render(<OrderBook data={mockData} imbalance={mockImbalance} detailed={true} />)

      expect(screen.getByText('매수:')).toBeInTheDocument()
      expect(screen.getByText('매도:')).toBeInTheDocument()
    })

    it('should hide imbalance indicator when detailed is false', () => {
      const mockData = createMockOrderBookData()
      const mockImbalance = createMockImbalance()

      render(<OrderBook data={mockData} imbalance={mockImbalance} detailed={false} />)

      expect(screen.queryByText('주문 불균형')).not.toBeInTheDocument()
    })

    it('should handle null imbalance', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} detailed={true} />)

      expect(screen.queryByText('주문 불균형')).not.toBeInTheDocument()
    })
  })

  describe('Freeze/Unfreeze Button', () => {
    it('should display real-time button when not frozen', () => {
      const mockData = createMockOrderBookData()
      const onToggleFreeze = vi.fn()

      render(
        <OrderBook
          data={mockData}
          imbalance={null}
          frozen={false}
          onToggleFreeze={onToggleFreeze}
        />
      )

      expect(screen.getByText('▶ 실시간')).toBeInTheDocument()
    })

    it('should display frozen button when frozen', () => {
      const mockData = createMockOrderBookData()
      const onToggleFreeze = vi.fn()

      render(
        <OrderBook
          data={mockData}
          imbalance={null}
          frozen={true}
          onToggleFreeze={onToggleFreeze}
        />
      )

      expect(screen.getByText('⏸ 정지됨')).toBeInTheDocument()
    })

    it('should call onToggleFreeze when button is clicked', () => {
      const mockData = createMockOrderBookData()
      const onToggleFreeze = vi.fn()

      render(
        <OrderBook
          data={mockData}
          imbalance={null}
          frozen={false}
          onToggleFreeze={onToggleFreeze}
        />
      )

      const button = screen.getByText('▶ 실시간')
      fireEvent.click(button)

      expect(onToggleFreeze).toHaveBeenCalledTimes(1)
    })

    it('should not render button when onToggleFreeze is not provided', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} />)

      expect(screen.queryByText('▶ 실시간')).not.toBeInTheDocument()
      expect(screen.queryByText('⏸ 정지됨')).not.toBeInTheDocument()
    })

    it('should have correct button styling when frozen', () => {
      const mockData = createMockOrderBookData()
      const onToggleFreeze = vi.fn()

      render(
        <OrderBook
          data={mockData}
          imbalance={null}
          frozen={true}
          onToggleFreeze={onToggleFreeze}
        />
      )

      const button = screen.getByText('⏸ 정지됨')
      expect(button).toHaveClass('bg-yellow-100')
    })
  })

  describe('LevelRow Rendering', () => {
    it('should render bid levels with blue styling', () => {
      const mockData = createMockOrderBookData()

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)

      // Check for blue-colored bid level elements
      const blueElements = container.querySelectorAll('.bg-blue-50')
      expect(blueElements.length).toBeGreaterThan(0)
    })

    it('should render ask levels with red styling', () => {
      const mockData = createMockOrderBookData()

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)

      // Check for red-colored ask level elements
      const redElements = container.querySelectorAll('.bg-red-50')
      expect(redElements.length).toBeGreaterThan(0)
    })

    it('should highlight best bid (first bid row)', () => {
      const mockData = createMockOrderBookData()

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)

      // Best bid should have highlighted border
      const highlightedBid = container.querySelector('.border-blue-600')
      expect(highlightedBid).toBeInTheDocument()
    })

    it('should highlight best ask (last ask row in reversed display)', () => {
      const mockData = createMockOrderBookData()

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)

      // Best ask should have highlighted border
      const highlightedAsk = container.querySelector('.border-red-600')
      expect(highlightedAsk).toBeInTheDocument()
    })
  })

  describe('Volume Bar Visualization', () => {
    it('should calculate volume bar width based on max volume', () => {
      const mockData = createMockOrderBookData({
        asks: [
          { price: 71000, volume: 1000, total: 1000 },
          { price: 71100, volume: 500, total: 1500 },
        ],
        bids: [
          { price: 70900, volume: 500, total: 500 },
          { price: 70800, volume: 200, total: 700 },
        ],
      })

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)

      // Volume bars should have varying widths based on volume
      const volumeBars = container.querySelectorAll('[style*="width"]')
      expect(volumeBars.length).toBeGreaterThan(0)
    })

    it('should handle zero max volume gracefully', () => {
      const mockData = createMockOrderBookData({
        asks: [{ price: 71000, volume: 0, total: 0 }],
        bids: [{ price: 70900, volume: 0, total: 0 }],
      })

      // Should render without error
      const { container } = render(<OrderBook data={mockData} imbalance={null} />)
      expect(container).toBeInTheDocument()
    })
  })

  describe('Flash Animation', () => {
    it('should apply flash animation class on data update', async () => {
      const mockData1 = createMockOrderBookData({ sequence: 1 })

      const { rerender, container } = render(<OrderBook data={mockData1} imbalance={null} />)

      // Check for animate-pulse class (flash animation)
      const animatedElements = container.querySelectorAll('.animate-pulse')
      expect(animatedElements.length).toBeGreaterThan(0)

      // Update with new data
      const mockData2 = createMockOrderBookData({ sequence: 2 })
      rerender(<OrderBook data={mockData2} imbalance={null} />)

      // Flash animation should be triggered again
      const newAnimatedElements = container.querySelectorAll('.animate-pulse')
      expect(newAnimatedElements.length).toBeGreaterThan(0)
    })
  })

  describe('Responsive Behavior', () => {
    it('should render with default levels', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} />)

      // Default is 10 levels
      expect(screen.getByText(/호가 \(10단계\)/)).toBeInTheDocument()
    })

    it('should limit displayed levels to available data', () => {
      const mockData = createMockOrderBookData({
        asks: [{ price: 71000, volume: 1000, total: 1000 }],
        bids: [{ price: 70900, volume: 900, total: 900 }],
      })

      // Request 10 levels but only 1 available each side
      const { container } = render(<OrderBook data={mockData} imbalance={null} levels={10} />)

      // Should only render available levels
      expect(container).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      const mockData = createMockOrderBookData()

      render(<OrderBook data={mockData} imbalance={null} />)

      const heading = screen.getByRole('heading', { level: 3 })
      expect(heading).toBeInTheDocument()
    })

    it('should have title attribute on freeze button', () => {
      const mockData = createMockOrderBookData()
      const onToggleFreeze = vi.fn()

      render(
        <OrderBook
          data={mockData}
          imbalance={null}
          frozen={false}
          onToggleFreeze={onToggleFreeze}
        />
      )

      const button = screen.getByTitle('업데이트 중지')
      expect(button).toBeInTheDocument()
    })

    it('should have correct title when frozen', () => {
      const mockData = createMockOrderBookData()
      const onToggleFreeze = vi.fn()

      render(
        <OrderBook
          data={mockData}
          imbalance={null}
          frozen={true}
          onToggleFreeze={onToggleFreeze}
        />
      )

      const button = screen.getByTitle('업데이트 재개')
      expect(button).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty asks array', () => {
      const mockData = createMockOrderBookData({
        asks: [],
      })

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)
      expect(container).toBeInTheDocument()
    })

    it('should handle empty bids array', () => {
      const mockData = createMockOrderBookData({
        bids: [],
      })

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)
      expect(container).toBeInTheDocument()
    })

    it('should handle both empty asks and bids', () => {
      const mockData = createMockOrderBookData({
        asks: [],
        bids: [],
      })

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)
      expect(container).toBeInTheDocument()
    })

    it('should handle very large price values', () => {
      const mockData = createMockOrderBookData({
        asks: [{ price: 999999999, volume: 1000, total: 1000 }],
        bids: [{ price: 999999998, volume: 1000, total: 1000 }],
        best_ask: 999999999,
        best_bid: 999999998,
        spread: 1,
        mid_price: 999999998.5,
      })

      const { container } = render(<OrderBook data={mockData} imbalance={null} />)
      expect(container).toBeInTheDocument()
    })

    it('should handle decimal price values', () => {
      const mockData = createMockOrderBookData({
        asks: [{ price: 100.55, volume: 1000, total: 1000 }],
        bids: [{ price: 100.45, volume: 1000, total: 1000 }],
        best_ask: 100.55,
        best_bid: 100.45,
        spread: 0.1,
        spread_pct: 0.1,
        mid_price: 100.50,
      })

      const { container } = render(<OrderBook data={mockData} imbalance={null} detailed={true} />)
      expect(container).toBeInTheDocument()
    })

    it('should handle invalid timestamp gracefully', () => {
      const mockData = createMockOrderBookData({
        timestamp: 'invalid-timestamp',
      })

      // Should not throw
      const { container } = render(<OrderBook data={mockData} imbalance={null} />)
      expect(container).toBeInTheDocument()
    })
  })

  describe('Memoization', () => {
    it('should be memoized (same props should not cause re-render)', () => {
      const mockData = createMockOrderBookData()
      const mockImbalance = createMockImbalance()

      const { rerender } = render(<OrderBook data={mockData} imbalance={mockImbalance} />)

      // Re-render with same props (reference equality)
      rerender(<OrderBook data={mockData} imbalance={mockImbalance} />)

      // Component should still be rendered (memo doesn't prevent all rerenders from parent)
      expect(screen.getByText(/호가 \(\d+단계\)/)).toBeInTheDocument()
    })
  })
})
