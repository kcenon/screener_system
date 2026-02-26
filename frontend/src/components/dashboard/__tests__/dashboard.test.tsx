/**
 * Dashboard Components Tests
 *
 * Basic unit tests for dashboard widgets to ensure proper rendering
 * and functionality.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import MarketSummaryWidget from '../MarketSummaryWidget'
import WatchlistWidget from '../WatchlistWidget'
import RecentActivityWidget from '../RecentActivityWidget'
import QuickActionsWidget from '../QuickActionsWidget'
import PlatformStatsWidget from '../PlatformStatsWidget'
import type {
  MarketIndex,
  WatchlistSummary,
  UserActivity,
} from '../../../types'

/**
 * Helper to wrap components with Router
 */
const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('MarketSummaryWidget', () => {
  it('renders loading state', () => {
    render(<MarketSummaryWidget isLoading={true} />)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('renders market indices', () => {
    const kospi: MarketIndex = {
      code: 'KOSPI',
      name: 'KOSPI',
      current: 2500.12,
      change: 15.3,
      change_percent: 0.6,
      high: 2520.0,
      low: 2490.0,
      volume: 1000000,
      timestamp: new Date().toISOString(),
    }

    const kosdaq: MarketIndex = {
      code: 'KOSDAQ',
      name: 'KOSDAQ',
      current: 850.45,
      change: -4.2,
      change_percent: -0.5,
      high: 860.0,
      low: 845.0,
      volume: 500000,
      timestamp: new Date().toISOString(),
    }

    render(<MarketSummaryWidget kospi={kospi} kosdaq={kosdaq} />)
    expect(screen.getByText('KOSPI')).toBeInTheDocument()
    expect(screen.getByText('KOSDAQ')).toBeInTheDocument()
  })
})

describe('WatchlistWidget', () => {
  it('renders empty state when no watchlists', () => {
    renderWithRouter(<WatchlistWidget watchlists={[]} />)
    expect(screen.getByText('No Watchlists Yet')).toBeInTheDocument()
  })

  it('renders watchlist cards', () => {
    const watchlists: WatchlistSummary[] = [
      {
        id: '1',
        name: 'Tech Stocks',
        description: 'My favorite tech stocks',
        stock_count: 5,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: '2',
        name: 'Value Plays',
        stock_count: 3,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ]

    renderWithRouter(<WatchlistWidget watchlists={watchlists} />)
    expect(screen.getByText('Tech Stocks')).toBeInTheDocument()
    expect(screen.getByText('Value Plays')).toBeInTheDocument()
    expect(screen.getByText('5 stocks')).toBeInTheDocument()
  })
})

describe('RecentActivityWidget', () => {
  it('renders empty state when no activities', () => {
    render(<RecentActivityWidget activities={[]} />)
    expect(screen.getByText('No recent activity')).toBeInTheDocument()
  })

  it('renders activity items', () => {
    const activities: UserActivity[] = [
      {
        id: '1',
        activity_type: 'screening',
        description: 'Performed stock screening',
        created_at: new Date().toISOString(),
      },
      {
        id: '2',
        activity_type: 'watchlist_create',
        description: 'Created watchlist "Tech Stocks"',
        created_at: new Date().toISOString(),
      },
    ]

    render(<RecentActivityWidget activities={activities} />)
    expect(screen.getByText('Performed stock screening')).toBeInTheDocument()
    expect(
      screen.getByText('Created watchlist "Tech Stocks"'),
    ).toBeInTheDocument()
  })
})

describe('QuickActionsWidget', () => {
  it('renders all quick action buttons', () => {
    renderWithRouter(<QuickActionsWidget />)
    expect(screen.getByText('New Screening')).toBeInTheDocument()
    expect(screen.getByText('Watchlists')).toBeInTheDocument()
    expect(screen.getByText('Compare Stocks')).toBeInTheDocument()
  })
})

describe('PlatformStatsWidget', () => {
  it('renders loading state', () => {
    render(
      <PlatformStatsWidget
        screeningCount={0}
        totalWatchlistStocks={0}
        isLoading={true}
      />,
    )
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('renders user statistics', () => {
    render(
      <PlatformStatsWidget
        screeningCount={15}
        totalWatchlistStocks={25}
        lastLogin={new Date().toISOString()}
      />,
    )
    expect(screen.getByText('15')).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()
    expect(screen.getByText('Screenings this month')).toBeInTheDocument()
  })
})
