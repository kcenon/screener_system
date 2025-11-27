import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QuickFiltersBar } from '../QuickFiltersBar'
import type { ScreeningFilters } from '@/types/screening'

describe('QuickFiltersBar', () => {
  const mockFilters: ScreeningFilters = {
    market: 'KOSPI',
  }

  let onFilterChangeMock: (filters: Partial<ScreeningFilters>) => void
  let onClearAllMock: (() => void) | undefined

  beforeEach(() => {
    onFilterChangeMock = vi.fn() as (filters: Partial<ScreeningFilters>) => void
    onClearAllMock = vi.fn() as () => void
  })

  describe('Rendering', () => {
    it('renders component with header', () => {
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      // With i18n mock, translation keys return their last segment
      expect(screen.getByText('popular_filters')).toBeInTheDocument()
      expect(screen.getByText('quick_filters')).toBeInTheDocument()
    })

    it('renders all 10 quick filter buttons', () => {
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      // All 10 preset filters should be rendered (using i18n key endings)
      expect(screen.getByRole('button', { name: /top_gainers/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /top_losers/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /high_volume/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /one_year_high/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /high_dividend/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /low_pe/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /high_growth/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /small_cap/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /large_cap/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /high_quality/i })).toBeInTheDocument()
    })

    it('renders filter buttons with icons', () => {
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })
      expect(within(topGainersButton).getByText('⬆')).toBeInTheDocument()

      const topLosersButton = screen.getByRole('button', { name: /top_losers/i })
      expect(within(topLosersButton).getByText('⬇')).toBeInTheDocument()

      const highVolumeButton = screen.getByRole('button', { name: /high_volume/i })
      expect(within(highVolumeButton).getByText('📊')).toBeInTheDocument()
    })

    it('does not render "Clear All" button when no filters are active', () => {
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      expect(screen.queryByText('clear_all')).not.toBeInTheDocument()
    })

    it('renders active filters indicator when filters are active', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      // Click on "Top Gainers" filter
      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })
      await user.click(topGainersButton)

      // With count interpolation, mock returns "filters_active (1)"
      expect(screen.getByText(/filters_active/i)).toBeInTheDocument()
    })
  })

  describe('Filter Activation', () => {
    it('activates filter when clicked', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })
      await user.click(topGainersButton)

      // Should call onFilterChange with price_change_1d filter
      expect(onFilterChangeMock).toHaveBeenCalledWith({
        price_change_1d: { min: 5 },
      })

      // Button should have active state (aria-pressed="true")
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'true')
    })

    it('deactivates filter when clicked again', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })

      // First click - activate
      await user.click(topGainersButton)
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'true')

      // Second click - deactivate
      await user.click(topGainersButton)
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'false')

      // Should call onFilterChange with undefined to clear filter
      expect(onFilterChangeMock).toHaveBeenCalledTimes(2)
    })

    it('allows multiple filters to be active simultaneously', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      // Activate Top Gainers
      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })
      await user.click(topGainersButton)

      // Activate High Volume
      const highVolumeButton = screen.getByRole('button', { name: /high_volume/i })
      await user.click(highVolumeButton)

      // Both should be active
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'true')
      expect(highVolumeButton).toHaveAttribute('aria-pressed', 'true')

      // Should show active filters indicator
      expect(screen.getByText(/filters_active/i)).toBeInTheDocument()
    })

    it('applies correct filter values for each preset', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      // Test Top Losers (-5%)
      const topLosersButton = screen.getByRole('button', { name: /top_losers/i })
      await user.click(topLosersButton)
      expect(onFilterChangeMock).toHaveBeenLastCalledWith({
        price_change_1d: { max: -5 },
      })

      // Test High Dividend (4%)
      const highDividendButton = screen.getByRole('button', { name: /high_dividend/i })
      await user.click(highDividendButton)
      expect(onFilterChangeMock).toHaveBeenLastCalledWith({
        dividend_yield: { min: 4 },
      })

      // Test Low P/E (0.1-10)
      const lowPeButton = screen.getByRole('button', { name: /low_pe/i })
      await user.click(lowPeButton)
      expect(onFilterChangeMock).toHaveBeenLastCalledWith({
        per: { min: 0.1, max: 10 },
      })
    })
  })

  describe('Clear All Functionality', () => {
    it('shows "Clear All" button when filters are active', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      // Activate a filter
      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })
      await user.click(topGainersButton)

      // "Clear All" button should appear
      expect(screen.getByText('clear_all')).toBeInTheDocument()
    })

    it('clears all filters when "Clear All" is clicked', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      // Activate two filters
      await user.click(screen.getByRole('button', { name: /top_gainers/i }))
      await user.click(screen.getByRole('button', { name: /high_volume/i }))

      // Click "Clear All"
      const clearAllButton = screen.getByText('clear_all')
      await user.click(clearAllButton)

      // Should call onClearAll callback
      expect(onClearAllMock).toHaveBeenCalledTimes(1)

      // All buttons should be inactive (aria-pressed="false")
      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })
      const highVolumeButton = screen.getByRole('button', { name: /high_volume/i })
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'false')
      expect(highVolumeButton).toHaveAttribute('aria-pressed', 'false')

      // Active filters indicator should disappear
      expect(screen.queryByText(/filters_active/i)).not.toBeInTheDocument()
    })
  })

  describe('Styling and Accessibility', () => {
    it('applies active styling to clicked button', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })

      // Before click - inactive styling
      expect(topGainersButton).toHaveClass('bg-gray-100')
      expect(topGainersButton).not.toHaveClass('bg-blue-600')

      // After click - active styling
      await user.click(topGainersButton)
      expect(topGainersButton).toHaveClass('bg-blue-600')
      expect(topGainersButton).not.toHaveClass('bg-gray-100')
    })

    it('sets correct aria-pressed attribute', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })

      // Initially false
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'false')

      // After click - true
      await user.click(topGainersButton)
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'true')

      // After second click - false again
      await user.click(topGainersButton)
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'false')
    })

    it('accepts custom className prop', () => {
      const { container } = render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
          className="custom-class"
        />
      )

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper).toHaveClass('custom-class')
    })
  })

  describe('Edge Cases', () => {
    it('handles missing onClearAll callback gracefully', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar currentFilters={mockFilters} onFilterChange={onFilterChangeMock} />
      )

      // Activate a filter
      await user.click(screen.getByRole('button', { name: /top_gainers/i }))

      // Click "Clear All" - should not throw error
      const clearAllButton = screen.getByText('clear_all')
      await expect(user.click(clearAllButton)).resolves.not.toThrow()
    })

    it('handles rapid consecutive clicks', async () => {
      const user = userEvent.setup()
      render(
        <QuickFiltersBar
          currentFilters={mockFilters}
          onFilterChange={onFilterChangeMock}
          onClearAll={onClearAllMock}
        />
      )

      const topGainersButton = screen.getByRole('button', { name: /top_gainers/i })

      // Click 5 times rapidly
      await user.click(topGainersButton)
      await user.click(topGainersButton)
      await user.click(topGainersButton)
      await user.click(topGainersButton)
      await user.click(topGainersButton)

      // Should have toggled 5 times (called onFilterChange 5 times)
      expect(onFilterChangeMock).toHaveBeenCalledTimes(5)

      // Final state should be active (odd number of clicks)
      expect(topGainersButton).toHaveAttribute('aria-pressed', 'true')
    })
  })
})
