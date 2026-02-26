import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { VolumeBar } from '../VolumeBar'

describe('VolumeBar', () => {
  describe('Rendering', () => {
    it('renders bar container with correct width', () => {
      const { container } = render(
        <VolumeBar volume={2000000} averageVolume={1000000} maxWidth={60} />,
      )

      const barContainer = container.querySelector('.relative.bg-gray-200')
      expect(barContainer).toHaveStyle({ width: '60px' })
    })

    it('renders placeholder when volume is null', () => {
      render(<VolumeBar volume={null} averageVolume={1000000} />)

      expect(
        screen.getByLabelText('No volume data available'),
      ).toBeInTheDocument()
      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('renders placeholder when averageVolume is null', () => {
      render(<VolumeBar volume={1000000} averageVolume={null} />)

      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('renders placeholder when averageVolume is zero', () => {
      render(<VolumeBar volume={1000000} averageVolume={0} />)

      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('applies custom className', () => {
      const { container } = render(
        <VolumeBar
          volume={2000000}
          averageVolume={1000000}
          className="custom-class"
        />,
      )

      expect(container.firstChild).toHaveClass('custom-class')
    })
  })

  describe('Volume ratio calculation', () => {
    it('shows 2.0x label for double volume', () => {
      render(
        <VolumeBar volume={2000000} averageVolume={1000000} showRatio={true} />,
      )

      expect(screen.getByText('2.0x')).toBeInTheDocument()
    })

    it('shows 1.0x label for average volume', () => {
      render(
        <VolumeBar volume={1000000} averageVolume={1000000} showRatio={true} />,
      )

      expect(screen.getByText('1.0x')).toBeInTheDocument()
    })

    it('shows 0.50x label for half volume', () => {
      render(
        <VolumeBar volume={500000} averageVolume={1000000} showRatio={true} />,
      )

      expect(screen.getByText('0.50x')).toBeInTheDocument()
    })

    it('caps display at maxRatio', () => {
      render(
        <VolumeBar
          volume={10000000}
          averageVolume={1000000}
          maxRatio={5}
          showRatio={true}
        />,
      )

      // Should show 10x since ratio is 10, not capped for label
      expect(screen.getByText('10x')).toBeInTheDocument()
    })

    it('hides ratio label when showRatio is false', () => {
      render(
        <VolumeBar
          volume={2000000}
          averageVolume={1000000}
          showRatio={false}
        />,
      )

      expect(screen.queryByText('2.0x')).not.toBeInTheDocument()
    })
  })

  describe('Color coding', () => {
    it('uses green color for high volume (>=2x)', () => {
      const { container } = render(
        <VolumeBar volume={2500000} averageVolume={1000000} />,
      )

      const fillBar = container.querySelector('.bg-green-500')
      expect(fillBar).toBeInTheDocument()
    })

    it('uses lighter green for above average (>=1x)', () => {
      const { container } = render(
        <VolumeBar volume={1200000} averageVolume={1000000} />,
      )

      const fillBar = container.querySelector('.bg-green-400')
      expect(fillBar).toBeInTheDocument()
    })

    it('uses yellow for below average (>=0.5x)', () => {
      const { container } = render(
        <VolumeBar volume={700000} averageVolume={1000000} />,
      )

      const fillBar = container.querySelector('.bg-yellow-400')
      expect(fillBar).toBeInTheDocument()
    })

    it('uses red for very low volume (<0.5x)', () => {
      const { container } = render(
        <VolumeBar volume={300000} averageVolume={1000000} />,
      )

      const fillBar = container.querySelector('.bg-red-400')
      expect(fillBar).toBeInTheDocument()
    })
  })

  describe('Tooltip', () => {
    it('shows tooltip with volume details', () => {
      const { container } = render(
        <VolumeBar volume={2500000} averageVolume={1000000} />,
      )

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper.getAttribute('title')).toContain('Volume:')
      expect(wrapper.getAttribute('title')).toContain('Avg:')
      expect(wrapper.getAttribute('title')).toContain('Ratio:')
    })
  })

  describe('Accessibility', () => {
    it('has descriptive aria-label for above average', () => {
      render(<VolumeBar volume={1500000} averageVolume={1000000} />)

      expect(screen.getByLabelText(/volume above average/i)).toBeInTheDocument()
    })

    it('has descriptive aria-label for below average', () => {
      render(<VolumeBar volume={500000} averageVolume={1000000} />)

      expect(screen.getByLabelText(/volume below average/i)).toBeInTheDocument()
    })
  })

  describe('Reference line', () => {
    it('renders reference line at 1x position', () => {
      const { container } = render(
        <VolumeBar
          volume={2500000}
          averageVolume={1000000}
          maxWidth={60}
          maxRatio={5}
        />,
      )

      // Reference line at 1x = 60/5 = 12px
      const refLine = container.querySelector('.w-px.bg-gray-500')
      expect(refLine).toBeInTheDocument()
      expect(refLine).toHaveStyle({ left: '12px' })
    })
  })

  describe('Edge cases', () => {
    it('handles undefined volume', () => {
      render(<VolumeBar volume={undefined} averageVolume={1000000} />)

      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('handles undefined averageVolume', () => {
      render(<VolumeBar volume={1000000} averageVolume={undefined} />)

      expect(screen.getByText('-')).toBeInTheDocument()
    })

    it('handles very small volumes', () => {
      render(<VolumeBar volume={100} averageVolume={1000000} />)

      const label = screen.getByText('0.00x')
      expect(label).toBeInTheDocument()
    })

    it('handles equal volumes', () => {
      render(<VolumeBar volume={1000000} averageVolume={1000000} />)

      expect(screen.getByText('1.0x')).toBeInTheDocument()
    })
  })
})
