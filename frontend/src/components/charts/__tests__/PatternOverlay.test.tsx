import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { PatternOverlay } from '../PatternOverlay'
import { Pattern } from '@/types/pattern'

describe('PatternOverlay', () => {
  const mockChart = {
    timeScale: vi.fn(() => ({
      timeToCoordinate: vi.fn((_time) => 100),
      subscribeVisibleLogicalRangeChange: vi.fn(),
      unsubscribeVisibleLogicalRangeChange: vi.fn(),
    })),
  } as any

  const mockSeries = {
    priceToCoordinate: vi.fn((_price) => 100),
  } as any

  const mockPatterns: Pattern[] = [
    {
      pattern_id: 'p1',
      pattern_type: 'Head and Shoulders',
      confidence: 0.9,
      detected_at: '2024-01-01',
      timeframe: '1D',
      coordinates: [
        { x: 1000, y: 100 },
        { x: 2000, y: 110 },
      ],
      expected_movement: 'bearish',
    },
  ]

  it('should render SVG overlay', () => {
    const { container } = render(
      <PatternOverlay
        chart={mockChart}
        series={mockSeries}
        patterns={mockPatterns}
        width={800}
        height={600}
      />
    )

    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg).toHaveStyle({ width: '800px', height: '600px' })
  })

  it('should render pattern paths', () => {
    const { container } = render(
      <PatternOverlay
        chart={mockChart}
        series={mockSeries}
        patterns={mockPatterns}
        width={800}
        height={600}
      />
    )

    // Should render a path for the pattern
    const path = container.querySelector('path')
    expect(path).toBeInTheDocument()
    
    // Should render circles for points
    const circles = container.querySelectorAll('circle')
    expect(circles).toHaveLength(2)
  })
})
