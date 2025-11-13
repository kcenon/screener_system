/**
 * StockChip Component Tests
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { StockChip } from '../StockChip'

describe('StockChip', () => {
  const defaultProps = {
    code: '005930',
    name: 'Samsung Electronics',
    market: 'KOSPI' as const,
    onRemove: vi.fn(),
  }

  it('should render stock code and name', () => {
    render(<StockChip {...defaultProps} />)

    expect(screen.getByText('005930')).toBeDefined()
    expect(screen.getByText('Samsung Electronics')).toBeDefined()
  })

  it('should display market badge', () => {
    render(<StockChip {...defaultProps} />)

    const marketBadge = screen.getByText('KOSPI')
    expect(marketBadge).toBeDefined()
  })

  it('should display KOSDAQ with different styling', () => {
    render(<StockChip {...defaultProps} market="KOSDAQ" />)

    const marketBadge = screen.getByText('KOSDAQ')
    expect(marketBadge).toBeDefined()
    expect(marketBadge.className).toContain('green')
  })

  it('should call onRemove with stock code when remove button clicked', () => {
    const onRemove = vi.fn()
    render(<StockChip {...defaultProps} onRemove={onRemove} />)

    const removeButton = screen.getByRole('button', {
      name: /remove samsung electronics/i,
    })
    fireEvent.click(removeButton)

    expect(onRemove).toHaveBeenCalledWith('005930')
    expect(onRemove).toHaveBeenCalledTimes(1)
  })

  it('should have proper aria-label for accessibility', () => {
    render(<StockChip {...defaultProps} />)

    const removeButton = screen.getByLabelText('Remove Samsung Electronics')
    expect(removeButton).toBeDefined()
  })

  it('should apply custom className', () => {
    const { container } = render(
      <StockChip {...defaultProps} className="custom-class" />
    )

    const chip = container.firstChild as HTMLElement
    expect(chip.className).toContain('custom-class')
  })

  it('should have hover styles', () => {
    const { container } = render(<StockChip {...defaultProps} />)

    const chip = container.firstChild as HTMLElement
    expect(chip.className).toContain('hover:bg-blue-100')
  })

  it('should render X icon for remove button', () => {
    render(<StockChip {...defaultProps} />)

    const removeButton = screen.getByRole('button', {
      name: /remove/i,
    })

    // Check for X icon (lucide-react renders as svg)
    const svg = removeButton.querySelector('svg')
    expect(svg).toBeDefined()
  })
})
