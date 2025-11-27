/**
 * AdvancedChart Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import type { OHLCV } from '@/utils/indicators'

// Mock lightweight-charts
vi.mock('lightweight-charts', () => ({
  createChart: vi.fn(() => ({
    addCandlestickSeries: vi.fn(() => ({
      setData: vi.fn(),
    })),
    addLineSeries: vi.fn(() => ({
      setData: vi.fn(),
    })),
    addAreaSeries: vi.fn(() => ({
      setData: vi.fn(),
    })),
    addBarSeries: vi.fn(() => ({
      setData: vi.fn(),
    })),
    addHistogramSeries: vi.fn(() => ({
      setData: vi.fn(),
    })),
    priceScale: vi.fn(() => ({
      applyOptions: vi.fn(),
    })),
    timeScale: vi.fn(() => ({
      fitContent: vi.fn(),
    })),
    applyOptions: vi.fn(),
    remove: vi.fn(),
    removeSeries: vi.fn(),
  })),
  ColorType: { Solid: 'solid' },
  CrosshairMode: { Normal: 0 },
  LineStyle: { Solid: 0, Dashed: 1 },
}))

// Mock ResizeObserver
class MockResizeObserver {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
}
global.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver

import AdvancedChart from '../AdvancedChart'

const sampleData: OHLCV[] = [
  { time: '2024-01-01', open: 100, high: 105, low: 98, close: 102, volume: 1000 },
  { time: '2024-01-02', open: 102, high: 108, low: 100, close: 106, volume: 1200 },
  { time: '2024-01-03', open: 106, high: 110, low: 104, close: 108, volume: 1100 },
]

describe('AdvancedChart', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    render(
      <AdvancedChart
        symbol="005930"
        data={[]}
        loading={true}
      />
    )

    expect(screen.getByText('차트 로딩 중...')).toBeInTheDocument()
  })

  it('should render empty state when no data', () => {
    render(
      <AdvancedChart
        symbol="005930"
        data={[]}
        loading={false}
      />
    )

    expect(screen.getByText('차트 데이터가 없습니다')).toBeInTheDocument()
  })

  it('should render chart container with data', () => {
    const { container } = render(
      <AdvancedChart
        symbol="005930"
        data={sampleData}
        loading={false}
      />
    )

    // Chart container should have data-symbol attribute
    const chartContainer = container.querySelector('[data-symbol="005930"]')
    expect(chartContainer).toBeInTheDocument()
  })

  it('should apply correct height', () => {
    const { container } = render(
      <AdvancedChart
        symbol="005930"
        data={sampleData}
        height={600}
      />
    )

    const chartContainer = container.querySelector('[data-symbol="005930"]')
    expect(chartContainer).toHaveStyle({ height: '600px' })
  })

  it('should render with different chart types', () => {
    const chartTypes = ['candlestick', 'line', 'area', 'ohlc', 'heikin-ashi'] as const

    chartTypes.forEach((chartType) => {
      const { container, unmount } = render(
        <AdvancedChart
          symbol="005930"
          data={sampleData}
          chartType={chartType}
        />
      )

      const chartContainer = container.querySelector('[data-symbol="005930"]')
      expect(chartContainer).toBeInTheDocument()
      unmount()
    })
  })

  it('should handle theme prop', () => {
    const { rerender, container } = render(
      <AdvancedChart
        symbol="005930"
        data={sampleData}
        theme="light"
      />
    )

    let chartContainer = container.querySelector('[data-symbol="005930"]')
    expect(chartContainer).toBeInTheDocument()

    rerender(
      <AdvancedChart
        symbol="005930"
        data={sampleData}
        theme="dark"
      />
    )

    chartContainer = container.querySelector('[data-symbol="005930"]')
    expect(chartContainer).toBeInTheDocument()
  })
})
