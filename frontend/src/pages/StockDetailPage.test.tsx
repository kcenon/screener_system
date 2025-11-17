import { describe, test, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import StockDetailPage from './StockDetailPage'
import type { StockDetail, PriceHistoryResponse } from '@/types'
import * as useStockDataModule from '@/hooks/useStockData'
import * as usePriceChartModule from '@/hooks/usePriceChart'

/**
 * Test suite for StockDetailPage component
 *
 * Tests:
 * - Component rendering with stock data
 * - Loading states
 * - Error states
 * - Data display and formatting
 * - Navigation and breadcrumbs
 */

// Mock hooks
vi.mock('@/hooks/useStockData')
vi.mock('@/hooks/usePriceChart')

// Mock components to avoid complex rendering dependencies
vi.mock('@/components/stock/StockHeader', () => ({
  default: ({ stock }: { stock: StockDetail }) => (
    <div data-testid="stock-header">
      <h1>{stock.name}</h1>
      <span data-testid="stock-code">{stock.code}</span>
      <span data-testid="stock-price">{stock.price}</span>
      <span data-testid="stock-change" className={stock.change >= 0 ? 'text-green-600' : 'text-red-600'}>
        {stock.change > 0 ? '+' : ''}{stock.change}
      </span>
    </div>
  ),
}))

vi.mock('@/components/stock/PriceChart', () => ({
  default: ({ data, loading, timeframe, onTimeframeChange }: {
    data: PriceHistoryResponse | undefined
    loading: boolean
    timeframe: string
    onTimeframeChange: (tf: string) => void
  }) => (
    <div data-testid="price-chart">
      {loading ? (
        <div data-testid="chart-loading">Loading chart...</div>
      ) : data ? (
        <>
          <div data-testid="chart-data">Chart with {data.candles.length} candles</div>
          <div data-testid="chart-timeframe">{timeframe}</div>
          <button onClick={() => onTimeframeChange('1Y')}>1Y</button>
        </>
      ) : (
        <div data-testid="chart-no-data">No chart data</div>
      )}
    </div>
  ),
}))

vi.mock('@/components/stock/StockTabs', () => ({
  default: ({ stock }: { stock: StockDetail }) => (
    <div data-testid="stock-tabs">
      <div>Tabs for {stock.code}</div>
    </div>
  ),
}))

// Test data
const mockStockDetail: StockDetail = {
  code: '005930',
  name: 'Samsung Electronics',
  market: 'KOSPI',
  sector: 'Technology',
  price: 75000,
  change: 1500,
  change_pct: 2.04,
  volume: 15000000,
  market_cap: 450000000000000,
  per: 15.5,
  pbr: 1.2,
  roe: 12.5,
  dividend_yield: 2.1,
  revenue_growth_yoy: 8.5,
}

const mockPriceHistory: PriceHistoryResponse = {
  stock_code: '005930',
  candles: [
    {
      date: '2024-01-01',
      open: 74000,
      high: 75500,
      low: 73500,
      close: 75000,
      volume: 14000000,
      change_pct: 1.35,
    },
    {
      date: '2024-01-02',
      open: 75000,
      high: 76000,
      low: 74500,
      close: 75500,
      volume: 16000000,
      change_pct: 0.67,
    },
  ],
  from_date: '2024-01-01',
  to_date: '2024-01-31',
  interval: '1D',
  count: 2,
}

// Helper function to render component with router and query client
function renderWithProviders(code: string) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/stocks/${code}`]}>
        <Routes>
          <Route path="/stocks/:code" element={<StockDetailPage />} />
          <Route path="/screener" element={<div>Screener Page</div>} />
          <Route path="/" element={<div>Home Page</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('StockDetailPage Rendering', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  test('renders loading state during data fetch', () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: undefined,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    expect(screen.getByText('주식 정보를 불러오는 중...')).toBeInTheDocument()
    // Check for spinner by class instead of role
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  test('renders error state for invalid symbol', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Stock not found'),
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: undefined,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('INVALID')

    await waitFor(() => {
      expect(screen.getByText('주식 정보를 불러올 수 없습니다')).toBeInTheDocument()
      expect(screen.getByText('Stock not found')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: '스크리너로 돌아가기' })).toBeInTheDocument()
    })
  })

  test('renders no data state when stock is null', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: undefined,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('999999')

    await waitFor(() => {
      expect(screen.getByText('주식 정보가 없습니다')).toBeInTheDocument()
      expect(screen.getByText('종목 코드: 999999')).toBeInTheDocument()
    })
  })

  test('renders stock detail page with all components', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: mockStockDetail,
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: mockPriceHistory,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    await waitFor(() => {
      // Stock header should be rendered
      expect(screen.getByTestId('stock-header')).toBeInTheDocument()
      const stockNames = screen.getAllByText('Samsung Electronics')
      expect(stockNames.length).toBeGreaterThan(0)
      expect(screen.getByTestId('stock-code')).toHaveTextContent('005930')

      // Price chart should be rendered
      expect(screen.getByTestId('price-chart')).toBeInTheDocument()
      expect(screen.getByTestId('chart-data')).toHaveTextContent('Chart with 2 candles')

      // Stock tabs should be rendered
      expect(screen.getByTestId('stock-tabs')).toBeInTheDocument()
      expect(screen.getByText('Tabs for 005930')).toBeInTheDocument()
    })
  })

  test('renders breadcrumb navigation', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: mockStockDetail,
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: mockPriceHistory,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    await waitFor(() => {
      expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /홈/ })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /스크리너/ })).toBeInTheDocument()
      const stockNames = screen.getAllByText('Samsung Electronics')
      expect(stockNames.length).toBeGreaterThan(0)
    })
  })
})

describe('StockDetailPage Data Display', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  test('displays stock price and change correctly', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: mockStockDetail,
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: mockPriceHistory,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    await waitFor(() => {
      expect(screen.getByTestId('stock-price')).toHaveTextContent('75000')
      expect(screen.getByTestId('stock-change')).toHaveTextContent('+1500')
    })
  })

  test('displays positive price change in green', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: { ...mockStockDetail, change: 1000 },
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: mockPriceHistory,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    await waitFor(() => {
      const changeElement = screen.getByTestId('stock-change')
      expect(changeElement).toHaveClass('text-green-600')
      expect(changeElement).toHaveTextContent('+1000')
    })
  })

  test('displays negative price change in red', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: { ...mockStockDetail, change: -1000 },
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: mockPriceHistory,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    await waitFor(() => {
      const changeElement = screen.getByTestId('stock-change')
      expect(changeElement).toHaveClass('text-red-600')
      expect(changeElement).toHaveTextContent('-1000')
    })
  })
})

describe('StockDetailPage Chart', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  test('renders price chart with historical data', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: mockStockDetail,
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: mockPriceHistory,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    await waitFor(() => {
      expect(screen.getByTestId('price-chart')).toBeInTheDocument()
      expect(screen.getByTestId('chart-data')).toHaveTextContent('Chart with 2 candles')
    })
  })

  test('shows chart loading state', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: mockStockDetail,
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: undefined,
      isLoading: true,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    await waitFor(() => {
      expect(screen.getByTestId('chart-loading')).toHaveTextContent('Loading chart...')
    })
  })

  test('displays current timeframe', async () => {
    vi.mocked(useStockDataModule.useStockData).mockReturnValue({
      data: mockStockDetail,
      isLoading: false,
      error: null,
    } as any)

    vi.mocked(usePriceChartModule.usePriceChart).mockReturnValue({
      data: mockPriceHistory,
      isLoading: false,
      timeframe: '1M',
      setTimeframe: vi.fn(),
    } as any)

    renderWithProviders('005930')

    await waitFor(() => {
      expect(screen.getByTestId('chart-timeframe')).toHaveTextContent('1M')
    })
  })
})
