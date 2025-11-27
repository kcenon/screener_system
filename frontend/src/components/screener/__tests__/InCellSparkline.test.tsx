import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { InCellSparkline } from '../InCellSparkline'

// Mock canvas context
const mockCanvasContext = {
  clearRect: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  stroke: vi.fn(),
  fill: vi.fn(),
  arc: vi.fn(),
  scale: vi.fn(),
}

describe('InCellSparkline', () => {
  beforeEach(() => {
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
      mockCanvasContext as unknown as CanvasRenderingContext2D
    )
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders canvas element with correct dimensions', () => {
      const { container } = render(
        <InCellSparkline data={[100, 102, 101, 103, 105]} width={40} height={20} />
      )

      const canvas = container.querySelector('canvas')
      expect(canvas).toBeInTheDocument()
      expect(canvas).toHaveStyle({ width: '40px', height: '20px' })
    })

    it('renders placeholder when data is empty', () => {
      render(<InCellSparkline data={[]} />)

      expect(screen.getByLabelText('No price data available')).toBeInTheDocument()
      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('renders placeholder when data has single point', () => {
      render(<InCellSparkline data={[100]} />)

      expect(screen.getByLabelText('No price data available')).toBeInTheDocument()
    })

    it('applies custom width and height', () => {
      const { container } = render(
        <InCellSparkline data={[100, 105, 103]} width={60} height={30} />
      )

      const canvas = container.querySelector('canvas')
      expect(canvas).toHaveStyle({ width: '60px', height: '30px' })
    })

    it('applies custom className', () => {
      const { container } = render(
        <InCellSparkline data={[100, 105]} className="custom-class" />
      )

      const canvas = container.querySelector('canvas')
      expect(canvas).toHaveClass('custom-class')
    })
  })

  describe('Trend detection', () => {
    it('displays positive trend aria label for upward data', () => {
      render(<InCellSparkline data={[100, 102, 104, 106, 108]} />)

      const canvas = screen.getByRole('img')
      expect(canvas).toHaveAttribute(
        'aria-label',
        expect.stringContaining('up')
      )
    })

    it('displays negative trend aria label for downward data', () => {
      render(<InCellSparkline data={[108, 106, 104, 102, 100]} />)

      const canvas = screen.getByRole('img')
      expect(canvas).toHaveAttribute(
        'aria-label',
        expect.stringContaining('down')
      )
    })
  })

  describe('Tooltip', () => {
    it('shows tooltip with trend percentage when showTooltip is true', () => {
      const { container } = render(
        <InCellSparkline data={[100, 110]} showTooltip={true} />
      )

      const canvas = container.querySelector('canvas')
      expect(canvas).toHaveAttribute('title', expect.stringContaining('%'))
    })

    it('does not show tooltip when showTooltip is false', () => {
      const { container } = render(
        <InCellSparkline data={[100, 110]} showTooltip={false} />
      )

      const canvas = container.querySelector('canvas')
      expect(canvas).not.toHaveAttribute('title')
    })
  })

  describe('Canvas drawing', () => {
    it('initializes canvas context with correct settings', () => {
      render(<InCellSparkline data={[100, 105, 103]} />)

      expect(mockCanvasContext.clearRect).toHaveBeenCalled()
      expect(mockCanvasContext.beginPath).toHaveBeenCalled()
      expect(mockCanvasContext.stroke).toHaveBeenCalled()
    })

    it('draws line through all data points', () => {
      render(<InCellSparkline data={[100, 105, 103, 108, 110]} />)

      // moveTo called once for first point
      expect(mockCanvasContext.moveTo).toHaveBeenCalledTimes(1)
      // lineTo called for remaining points
      expect(mockCanvasContext.lineTo).toHaveBeenCalledTimes(4)
    })

    it('draws end dot marker', () => {
      render(<InCellSparkline data={[100, 105]} />)

      expect(mockCanvasContext.arc).toHaveBeenCalled()
      expect(mockCanvasContext.fill).toHaveBeenCalled()
    })
  })

  describe('Color modes', () => {
    it('uses auto color mode by default', () => {
      const { container } = render(
        <InCellSparkline data={[100, 105]} />
      )

      const canvas = container.querySelector('canvas')
      expect(canvas).toBeInTheDocument()
      // Canvas drawing verified through mock calls
    })

    it('accepts green color prop', () => {
      const { container } = render(
        <InCellSparkline data={[100, 95]} color="green" />
      )

      expect(container.querySelector('canvas')).toBeInTheDocument()
    })

    it('accepts red color prop', () => {
      const { container } = render(
        <InCellSparkline data={[100, 105]} color="red" />
      )

      expect(container.querySelector('canvas')).toBeInTheDocument()
    })

    it('accepts gray color prop', () => {
      const { container } = render(
        <InCellSparkline data={[100, 100]} color="gray" />
      )

      expect(container.querySelector('canvas')).toBeInTheDocument()
    })
  })

  describe('Edge cases', () => {
    it('handles identical values gracefully', () => {
      const { container } = render(
        <InCellSparkline data={[100, 100, 100, 100, 100]} />
      )

      expect(container.querySelector('canvas')).toBeInTheDocument()
    })

    it('handles negative values', () => {
      const { container } = render(
        <InCellSparkline data={[-10, -5, 0, 5, 10]} />
      )

      expect(container.querySelector('canvas')).toBeInTheDocument()
    })

    it('handles large value ranges', () => {
      const { container } = render(
        <InCellSparkline data={[1, 1000000, 500000, 2000000]} />
      )

      expect(container.querySelector('canvas')).toBeInTheDocument()
    })

    it('handles 7 data points (typical use case)', () => {
      const { container } = render(
        <InCellSparkline data={[100, 102, 99, 101, 103, 105, 104]} />
      )

      expect(container.querySelector('canvas')).toBeInTheDocument()
      expect(mockCanvasContext.moveTo).toHaveBeenCalledTimes(1)
      expect(mockCanvasContext.lineTo).toHaveBeenCalledTimes(6)
    })
  })

  describe('Accessibility', () => {
    it('has img role for screen readers', () => {
      render(<InCellSparkline data={[100, 105]} />)

      expect(screen.getByRole('img')).toBeInTheDocument()
    })

    it('has descriptive aria-label', () => {
      render(<InCellSparkline data={[100, 105]} />)

      const canvas = screen.getByRole('img')
      expect(canvas.getAttribute('aria-label')).toContain('Price trend')
    })
  })
})
