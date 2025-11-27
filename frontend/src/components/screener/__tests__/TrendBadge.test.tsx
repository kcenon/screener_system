import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TrendBadge } from '../TrendBadge'

describe('TrendBadge', () => {
  describe('Rendering', () => {
    it('renders badge with trend icon', () => {
      render(<TrendBadge shortTermChange={5} longTermChange={10} />)

      const badge = screen.getByRole('status')
      expect(badge).toBeInTheDocument()
    })

    it('applies custom className', () => {
      render(
        <TrendBadge
          shortTermChange={5}
          longTermChange={10}
          className="custom-class"
        />
      )

      expect(screen.getByRole('status')).toHaveClass('custom-class')
    })

    it('shows label when showLabel is true', () => {
      render(<TrendBadge trend="strong_up" showLabel={true} />)

      expect(screen.getByText('Strong')).toBeInTheDocument()
    })

    it('hides label when showLabel is false', () => {
      render(<TrendBadge trend="strong_up" showLabel={false} />)

      expect(screen.queryByText('Strong')).not.toBeInTheDocument()
    })

    it('applies sm size classes', () => {
      render(<TrendBadge trend="up" size="sm" />)

      const badge = screen.getByRole('status')
      expect(badge).toHaveClass('text-[10px]')
    })

    it('applies md size classes', () => {
      render(<TrendBadge trend="up" size="md" />)

      const badge = screen.getByRole('status')
      expect(badge).toHaveClass('text-xs')
    })
  })

  describe('Trend detection from price changes', () => {
    it('shows strong_up for both positive and high momentum', () => {
      render(<TrendBadge shortTermChange={8} longTermChange={10} />)

      expect(screen.getByText('↗')).toBeInTheDocument()
    })

    it('shows strong_down for both negative and significant decline', () => {
      render(<TrendBadge shortTermChange={-8} longTermChange={-10} />)

      expect(screen.getByText('↘')).toBeInTheDocument()
    })

    it('shows up for positive momentum', () => {
      render(<TrendBadge shortTermChange={3} longTermChange={2} />)

      expect(screen.getByText('↑')).toBeInTheDocument()
    })

    it('shows down for negative momentum', () => {
      render(<TrendBadge shortTermChange={-3} longTermChange={-2} />)

      expect(screen.getByText('↓')).toBeInTheDocument()
    })

    it('shows neutral for mixed signals', () => {
      render(<TrendBadge shortTermChange={0.5} longTermChange={-0.5} />)

      expect(screen.getByText('→')).toBeInTheDocument()
    })

    it('shows neutral when both changes are null', () => {
      render(<TrendBadge shortTermChange={null} longTermChange={null} />)

      expect(screen.getByText('→')).toBeInTheDocument()
    })

    it('handles only shortTermChange provided', () => {
      render(<TrendBadge shortTermChange={5} longTermChange={undefined} />)

      const badge = screen.getByRole('status')
      expect(badge).toBeInTheDocument()
    })

    it('handles only longTermChange provided', () => {
      render(<TrendBadge shortTermChange={undefined} longTermChange={8} />)

      const badge = screen.getByRole('status')
      expect(badge).toBeInTheDocument()
    })
  })

  describe('Explicit trend override', () => {
    it('uses explicit strong_up trend', () => {
      render(<TrendBadge trend="strong_up" />)

      expect(screen.getByText('↗')).toBeInTheDocument()
      expect(screen.getByLabelText('Strong upward trend')).toBeInTheDocument()
    })

    it('uses explicit up trend', () => {
      render(<TrendBadge trend="up" />)

      expect(screen.getByText('↑')).toBeInTheDocument()
      expect(screen.getByLabelText('Upward trend')).toBeInTheDocument()
    })

    it('uses explicit neutral trend', () => {
      render(<TrendBadge trend="neutral" />)

      expect(screen.getByText('→')).toBeInTheDocument()
      expect(screen.getByLabelText('Neutral trend')).toBeInTheDocument()
    })

    it('uses explicit down trend', () => {
      render(<TrendBadge trend="down" />)

      expect(screen.getByText('↓')).toBeInTheDocument()
      expect(screen.getByLabelText('Downward trend')).toBeInTheDocument()
    })

    it('uses explicit strong_down trend', () => {
      render(<TrendBadge trend="strong_down" />)

      expect(screen.getByText('↘')).toBeInTheDocument()
      expect(screen.getByLabelText('Strong downward trend')).toBeInTheDocument()
    })

    it('explicit trend overrides calculated trend', () => {
      render(
        <TrendBadge trend="down" shortTermChange={10} longTermChange={15} />
      )

      // Despite positive changes, should show down trend
      expect(screen.getByText('↓')).toBeInTheDocument()
    })
  })

  describe('Color coding', () => {
    it('uses green background for strong_up', () => {
      render(<TrendBadge trend="strong_up" />)

      const badge = screen.getByRole('status')
      expect(badge).toHaveClass('bg-green-100')
      expect(badge).toHaveClass('text-green-700')
    })

    it('uses lighter green for up', () => {
      render(<TrendBadge trend="up" />)

      const badge = screen.getByRole('status')
      expect(badge).toHaveClass('bg-green-50')
      expect(badge).toHaveClass('text-green-600')
    })

    it('uses gray for neutral', () => {
      render(<TrendBadge trend="neutral" />)

      const badge = screen.getByRole('status')
      expect(badge).toHaveClass('bg-gray-100')
      expect(badge).toHaveClass('text-gray-600')
    })

    it('uses lighter red for down', () => {
      render(<TrendBadge trend="down" />)

      const badge = screen.getByRole('status')
      expect(badge).toHaveClass('bg-red-50')
      expect(badge).toHaveClass('text-red-600')
    })

    it('uses red background for strong_down', () => {
      render(<TrendBadge trend="strong_down" />)

      const badge = screen.getByRole('status')
      expect(badge).toHaveClass('bg-red-100')
      expect(badge).toHaveClass('text-red-700')
    })
  })

  describe('Tooltip', () => {
    it('shows tooltip with trend info when changes provided', () => {
      render(<TrendBadge shortTermChange={5.25} longTermChange={8.5} />)

      const badge = screen.getByRole('status')
      expect(badge.getAttribute('title')).toContain('Trend:')
      expect(badge.getAttribute('title')).toContain('Short-term: +5.25%')
      expect(badge.getAttribute('title')).toContain('Long-term: +8.50%')
    })

    it('shows simple tooltip when only trend provided', () => {
      render(<TrendBadge trend="up" />)

      const badge = screen.getByRole('status')
      expect(badge.getAttribute('title')).toBe('Trend: Up')
    })

    it('shows negative values correctly in tooltip', () => {
      render(<TrendBadge shortTermChange={-3.5} longTermChange={-7.2} />)

      const badge = screen.getByRole('status')
      expect(badge.getAttribute('title')).toContain('-3.50%')
      expect(badge.getAttribute('title')).toContain('-7.20%')
    })
  })

  describe('Accessibility', () => {
    it('has status role', () => {
      render(<TrendBadge trend="up" />)

      expect(screen.getByRole('status')).toBeInTheDocument()
    })

    it('has descriptive aria-label', () => {
      render(<TrendBadge trend="strong_up" />)

      expect(screen.getByLabelText('Strong upward trend')).toBeInTheDocument()
    })
  })

  describe('Labels', () => {
    it('shows Strong label for strong_up', () => {
      render(<TrendBadge trend="strong_up" showLabel />)

      expect(screen.getByText('Strong')).toBeInTheDocument()
    })

    it('shows Up label for up', () => {
      render(<TrendBadge trend="up" showLabel />)

      expect(screen.getByText('Up')).toBeInTheDocument()
    })

    it('shows Flat label for neutral', () => {
      render(<TrendBadge trend="neutral" showLabel />)

      expect(screen.getByText('Flat')).toBeInTheDocument()
    })

    it('shows Down label for down', () => {
      render(<TrendBadge trend="down" showLabel />)

      expect(screen.getByText('Down')).toBeInTheDocument()
    })

    it('shows Weak label for strong_down', () => {
      render(<TrendBadge trend="strong_down" showLabel />)

      expect(screen.getByText('Weak')).toBeInTheDocument()
    })
  })

  describe('Edge cases', () => {
    it('handles zero changes', () => {
      render(<TrendBadge shortTermChange={0} longTermChange={0} />)

      expect(screen.getByText('→')).toBeInTheDocument()
    })

    it('handles very small positive changes', () => {
      render(<TrendBadge shortTermChange={0.01} longTermChange={0.02} />)

      expect(screen.getByText('→')).toBeInTheDocument()
    })

    it('handles very small negative changes', () => {
      render(<TrendBadge shortTermChange={-0.01} longTermChange={-0.02} />)

      expect(screen.getByText('→')).toBeInTheDocument()
    })

    it('handles conflicting short/long term trends', () => {
      // Short term up, long term down
      render(<TrendBadge shortTermChange={5} longTermChange={-3} />)

      // Should show some direction based on weighted average
      const badge = screen.getByRole('status')
      expect(badge).toBeInTheDocument()
    })
  })
})
