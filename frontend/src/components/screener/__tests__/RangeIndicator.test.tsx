import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RangeIndicator } from '../RangeIndicator'

describe('RangeIndicator', () => {
  describe('Rendering', () => {
    it('renders bar with correct width', () => {
      const { container } = render(
        <RangeIndicator
          currentPrice={50000}
          low52w={40000}
          high52w={60000}
          width={60}
        />
      )

      const bar = container.querySelector('.bg-gradient-to-r')
      expect(bar).toHaveStyle({ width: '60px' })
    })

    it('renders placeholder when currentPrice is null', () => {
      render(
        <RangeIndicator
          currentPrice={null}
          low52w={40000}
          high52w={60000}
        />
      )

      expect(screen.getByText('-')).toBeInTheDocument()
      expect(screen.getByLabelText('No 52-week range data available')).toBeInTheDocument()
    })

    it('renders placeholder when low52w is null', () => {
      render(
        <RangeIndicator
          currentPrice={50000}
          low52w={null}
          high52w={60000}
        />
      )

      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('renders placeholder when high52w is null', () => {
      render(
        <RangeIndicator
          currentPrice={50000}
          low52w={40000}
          high52w={null}
        />
      )

      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('renders placeholder when high52w <= low52w', () => {
      render(
        <RangeIndicator
          currentPrice={50000}
          low52w={60000}
          high52w={40000}
        />
      )

      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('applies custom className', () => {
      const { container } = render(
        <RangeIndicator
          currentPrice={50000}
          low52w={40000}
          high52w={60000}
          className="custom-class"
        />
      )

      expect(container.firstChild).toHaveClass('custom-class')
    })
  })

  describe('Position calculation', () => {
    it('shows 50% for price at midpoint', () => {
      render(
        <RangeIndicator
          currentPrice={50000}
          low52w={40000}
          high52w={60000}
          showPercent={true}
        />
      )

      expect(screen.getByText('50%')).toBeInTheDocument()
    })

    it('shows 0% for price at low', () => {
      render(
        <RangeIndicator
          currentPrice={40000}
          low52w={40000}
          high52w={60000}
          showPercent={true}
        />
      )

      expect(screen.getByText('0%')).toBeInTheDocument()
    })

    it('shows 100% for price at high', () => {
      render(
        <RangeIndicator
          currentPrice={60000}
          low52w={40000}
          high52w={60000}
          showPercent={true}
        />
      )

      expect(screen.getByText('100%')).toBeInTheDocument()
    })

    it('shows 25% for price at quarter', () => {
      render(
        <RangeIndicator
          currentPrice={45000}
          low52w={40000}
          high52w={60000}
          showPercent={true}
        />
      )

      expect(screen.getByText('25%')).toBeInTheDocument()
    })

    it('shows 75% for price at three-quarters', () => {
      render(
        <RangeIndicator
          currentPrice={55000}
          low52w={40000}
          high52w={60000}
          showPercent={true}
        />
      )

      expect(screen.getByText('75%')).toBeInTheDocument()
    })

    it('hides percentage when showPercent is false', () => {
      render(
        <RangeIndicator
          currentPrice={50000}
          low52w={40000}
          high52w={60000}
          showPercent={false}
        />
      )

      expect(screen.queryByText('50%')).not.toBeInTheDocument()
    })
  })

  describe('Color coding', () => {
    it('uses green marker for high position (>=80%)', () => {
      const { container } = render(
        <RangeIndicator
          currentPrice={58000}
          low52w={40000}
          high52w={60000}
        />
      )

      const marker = container.querySelector('.bg-green-500')
      expect(marker).toBeInTheDocument()
    })

    it('uses lighter green marker for position >=60%', () => {
      const { container } = render(
        <RangeIndicator
          currentPrice={54000}
          low52w={40000}
          high52w={60000}
        />
      )

      const marker = container.querySelector('.bg-green-400')
      expect(marker).toBeInTheDocument()
    })

    it('uses yellow marker for middle position (>=40%)', () => {
      const { container } = render(
        <RangeIndicator
          currentPrice={48000}
          low52w={40000}
          high52w={60000}
        />
      )

      const marker = container.querySelector('.bg-yellow-400')
      expect(marker).toBeInTheDocument()
    })

    it('uses orange marker for low position (>=20%)', () => {
      const { container } = render(
        <RangeIndicator
          currentPrice={44000}
          low52w={40000}
          high52w={60000}
        />
      )

      const marker = container.querySelector('.bg-orange-400')
      expect(marker).toBeInTheDocument()
    })

    it('uses red marker for very low position (<20%)', () => {
      const { container } = render(
        <RangeIndicator
          currentPrice={41000}
          low52w={40000}
          high52w={60000}
        />
      )

      const marker = container.querySelector('.bg-red-500')
      expect(marker).toBeInTheDocument()
    })
  })

  describe('Tooltip', () => {
    it('shows tooltip with range details', () => {
      const { container } = render(
        <RangeIndicator
          currentPrice={50000}
          low52w={40000}
          high52w={60000}
        />
      )

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper.getAttribute('title')).toContain('52W Range')
      expect(wrapper.getAttribute('title')).toContain('High:')
      expect(wrapper.getAttribute('title')).toContain('Low:')
      expect(wrapper.getAttribute('title')).toContain('Current:')
    })
  })

  describe('Accessibility', () => {
    it('has descriptive aria-label', () => {
      render(
        <RangeIndicator
          currentPrice={50000}
          low52w={40000}
          high52w={60000}
        />
      )

      expect(
        screen.getByLabelText(/52-week range position/i)
      ).toBeInTheDocument()
    })
  })

  describe('Edge cases', () => {
    it('clamps price below low to 0%', () => {
      render(
        <RangeIndicator
          currentPrice={35000}
          low52w={40000}
          high52w={60000}
          showPercent={true}
        />
      )

      expect(screen.getByText('0%')).toBeInTheDocument()
    })

    it('clamps price above high to 100%', () => {
      render(
        <RangeIndicator
          currentPrice={70000}
          low52w={40000}
          high52w={60000}
          showPercent={true}
        />
      )

      expect(screen.getByText('100%')).toBeInTheDocument()
    })

    it('handles equal high and low (invalid range)', () => {
      render(
        <RangeIndicator
          currentPrice={50000}
          low52w={50000}
          high52w={50000}
        />
      )

      expect(screen.getByText('-')).toBeInTheDocument()
    })
  })
})
