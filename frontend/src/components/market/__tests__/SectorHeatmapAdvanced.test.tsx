/**
 * SectorHeatmapAdvanced Component Tests
 * IMPROVEMENT-004 Phase 3A
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SectorHeatmapAdvanced } from '../SectorHeatmapAdvanced'

// Mock the useSectorPerformance hook
vi.mock('../../../hooks/useSectorPerformance', () => ({
  useSectorPerformance: () => ({
    data: {
      sectors: [
        {
          code: 'technology',
          name: '기술',
          change_percent: 2.5,
          market_cap: 500000000000000,
          stock_count: 150,
        },
        {
          code: 'finance',
          name: '금융',
          change_percent: -1.2,
          market_cap: 300000000000000,
          stock_count: 80,
        },
      ],
      timeframe: '1D',
      updated_at: '2025-11-15T00:00:00Z',
    },
    isLoading: false,
    error: null,
  }),
}))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </BrowserRouter>
  )
}

describe('SectorHeatmapAdvanced', () => {
  it('renders component with title', () => {
    render(
      <TestWrapper>
        <SectorHeatmapAdvanced />
      </TestWrapper>,
    )

    expect(screen.getByText(/섹터 성과 맵/i)).toBeInTheDocument()
  })

  it('renders timeframe selector buttons', () => {
    render(
      <TestWrapper>
        <SectorHeatmapAdvanced />
      </TestWrapper>,
    )

    expect(screen.getByText('1일')).toBeInTheDocument()
    expect(screen.getByText('1주')).toBeInTheDocument()
    expect(screen.getByText('1개월')).toBeInTheDocument()
    expect(screen.getByText('3개월')).toBeInTheDocument()
  })

  it('renders legend with color scale', () => {
    render(
      <TestWrapper>
        <SectorHeatmapAdvanced />
      </TestWrapper>,
    )

    expect(screen.getByText('+3% 이상')).toBeInTheDocument()
    expect(screen.getByText('+1% ~ +3%')).toBeInTheDocument()
    expect(screen.getByText('-1% ~ +1%')).toBeInTheDocument()
    expect(screen.getByText('-3% ~ -1%')).toBeInTheDocument()
    expect(screen.getByText('-3% 이하')).toBeInTheDocument()
  })

  it('renders help text', () => {
    render(
      <TestWrapper>
        <SectorHeatmapAdvanced />
      </TestWrapper>,
    )

    expect(screen.getByText(/크기는 시가총액에 비례하며/)).toBeInTheDocument()
  })

  it('renders with custom height', () => {
    const { container } = render(
      <TestWrapper>
        <SectorHeatmapAdvanced height={600} />
      </TestWrapper>,
    )

    expect(container).toBeInTheDocument()
  })

  it('supports auto-refresh option', () => {
    render(
      <TestWrapper>
        <SectorHeatmapAdvanced autoRefresh={true} />
      </TestWrapper>,
    )

    expect(screen.getByText(/섹터 성과 맵/i)).toBeInTheDocument()
  })

  it('supports different default timeframes', () => {
    render(
      <TestWrapper>
        <SectorHeatmapAdvanced defaultTimeframe="1W" />
      </TestWrapper>,
    )

    expect(screen.getByText('1주')).toBeInTheDocument()
  })
})
