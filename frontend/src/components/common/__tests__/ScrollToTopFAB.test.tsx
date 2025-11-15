import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ScrollToTopFAB from '../ScrollToTopFAB'

describe('ScrollToTopFAB', () => {
  // Mock window.scrollTo
  const originalScrollTo = window.scrollTo
  let scrollToMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    scrollToMock = vi.fn()
    window.scrollTo = scrollToMock as typeof window.scrollTo
  })

  afterEach(() => {
    window.scrollTo = originalScrollTo
    vi.clearAllMocks()
  })

  describe('Visibility Behavior', () => {
    it('is hidden when page scroll is below threshold', () => {
      // Set scroll position below default threshold (200px)
      Object.defineProperty(window, 'pageYOffset', { value: 100, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 100, writable: true })

      render(<ScrollToTopFAB />)

      // Button should not be in the document
      expect(screen.queryByRole('button', { name: /scroll to top/i })).not.toBeInTheDocument()
    })

    it('is visible when page scroll is above threshold', async () => {
      // Set scroll position above default threshold (200px)
      Object.defineProperty(window, 'pageYOffset', { value: 300, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 300, writable: true })

      render(<ScrollToTopFAB />)

      // Trigger scroll event to update visibility
      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /scroll to top/i })).toBeInTheDocument()
      })
    })

    it('respects custom threshold prop', async () => {
      // Set scroll position at 250px
      Object.defineProperty(window, 'pageYOffset', { value: 250, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 250, writable: true })

      // Render with custom threshold of 300px
      render(<ScrollToTopFAB threshold={300} />)

      // Button should be hidden (250 < 300)
      expect(screen.queryByRole('button', { name: /scroll to top/i })).not.toBeInTheDocument()

      // Change scroll to 350px (above threshold)
      Object.defineProperty(window, 'pageYOffset', { value: 350, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 350, writable: true })

      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /scroll to top/i })).toBeInTheDocument()
      })
    })

    it('shows and hides button on scroll events', async () => {
      // Start below threshold
      Object.defineProperty(window, 'pageYOffset', { value: 100, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 100, writable: true })

      render(<ScrollToTopFAB threshold={200} />)

      // Button should be hidden
      expect(screen.queryByRole('button', { name: /scroll to top/i })).not.toBeInTheDocument()

      // Scroll down (above threshold)
      Object.defineProperty(window, 'pageYOffset', { value: 300, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 300, writable: true })
      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /scroll to top/i })).toBeInTheDocument()
      })

      // Scroll up (below threshold)
      Object.defineProperty(window, 'pageYOffset', { value: 100, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 100, writable: true })
      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /scroll to top/i })).not.toBeInTheDocument()
      })
    })
  })

  describe('Scroll Functionality', () => {
    beforeEach(() => {
      // Set scroll position above threshold to make button visible
      Object.defineProperty(window, 'pageYOffset', { value: 500, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 500, writable: true })
    })

    it('scrolls to top when button is clicked', async () => {
      const user = userEvent.setup()
      render(<ScrollToTopFAB />)

      // Trigger scroll event to show button
      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /scroll to top/i })).toBeInTheDocument()
      })

      // Click button
      const button = screen.getByRole('button', { name: /scroll to top/i })
      await user.click(button)

      // Should call window.scrollTo with top: 0
      expect(scrollToMock).toHaveBeenCalledWith({
        top: 0,
        behavior: 'smooth',
      })
    })

    it('uses custom scroll behavior when provided', async () => {
      const user = userEvent.setup()
      render(<ScrollToTopFAB behavior="auto" />)

      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /scroll to top/i })).toBeInTheDocument()
      })

      const button = screen.getByRole('button', { name: /scroll to top/i })
      await user.click(button)

      expect(scrollToMock).toHaveBeenCalledWith({
        top: 0,
        behavior: 'auto',
      })
    })
  })

  describe('Custom Positioning', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'pageYOffset', { value: 500, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 500, writable: true })
    })

    it('uses default positioning (bottom: 2rem, right: 2rem)', async () => {
      render(<ScrollToTopFAB />)

      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /scroll to top/i })
        expect(button).toHaveStyle({
          bottom: '2rem',
          right: '2rem',
        })
      })
    })

    it('uses custom positioning when provided', async () => {
      render(<ScrollToTopFAB bottom="5rem" right="3rem" />)

      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /scroll to top/i })
        expect(button).toHaveStyle({
          bottom: '5rem',
          right: '3rem',
        })
      })
    })
  })

  describe('Accessibility', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'pageYOffset', { value: 500, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 500, writable: true })
    })

    it('has accessible label', async () => {
      render(<ScrollToTopFAB />)

      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /scroll to top/i })
        expect(button).toHaveAttribute('aria-label', 'Scroll to top')
      })
    })

    it('has title attribute for tooltip', async () => {
      render(<ScrollToTopFAB />)

      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /scroll to top/i })
        expect(button).toHaveAttribute('title', 'Back to top')
      })
    })

    it('is keyboard accessible (focusable)', async () => {
      const user = userEvent.setup()
      render(<ScrollToTopFAB />)

      window.dispatchEvent(new Event('scroll'))

      await waitFor(async () => {
        const button = screen.getByRole('button', { name: /scroll to top/i })

        // Tab to focus button
        await user.tab()

        // Button should be focused
        expect(button).toHaveFocus()
      })
    })
  })

  describe('Styling', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'pageYOffset', { value: 500, writable: true })
      Object.defineProperty(document.documentElement, 'scrollTop', { value: 500, writable: true })
    })

    it('renders with correct CSS classes', async () => {
      render(<ScrollToTopFAB />)

      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /scroll to top/i })

        // Check for key styling classes
        expect(button).toHaveClass('fixed')
        expect(button).toHaveClass('z-50')
        expect(button).toHaveClass('bg-blue-600')
        expect(button).toHaveClass('rounded-full')
        expect(button).toHaveClass('shadow-lg')
      })
    })

    it('renders SVG icon', async () => {
      render(<ScrollToTopFAB />)

      window.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /scroll to top/i })
        const svg = button.querySelector('svg')

        expect(svg).toBeInTheDocument()
        expect(svg).toHaveClass('h-6 w-6')
      })
    })
  })

  describe('Custom Scroll Container', () => {
    it('works with custom scroll container element', async () => {
      // Create mock container
      const container = document.createElement('div')
      Object.defineProperty(container, 'scrollTop', { value: 500, writable: true })
      document.body.appendChild(container)

      const containerScrollToMock = vi.fn()
      container.scrollTo = containerScrollToMock

      const user = userEvent.setup()
      render(<ScrollToTopFAB scrollContainer={container} />)

      // Trigger scroll event on container
      container.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /scroll to top/i })).toBeInTheDocument()
      })

      // Click button
      const button = screen.getByRole('button', { name: /scroll to top/i })
      await user.click(button)

      // Should call container.scrollTo, not window.scrollTo
      expect(containerScrollToMock).toHaveBeenCalledWith({
        top: 0,
        behavior: 'smooth',
      })
      expect(scrollToMock).not.toHaveBeenCalled()

      // Cleanup
      document.body.removeChild(container)
    })

    it('works with scroll container CSS selector', async () => {
      // Create mock container with ID
      const container = document.createElement('div')
      container.id = 'scroll-container'
      Object.defineProperty(container, 'scrollTop', { value: 500, writable: true })
      document.body.appendChild(container)

      const containerScrollToMock = vi.fn()
      container.scrollTo = containerScrollToMock

      const user = userEvent.setup()
      render(<ScrollToTopFAB scrollContainer="#scroll-container" />)

      // Trigger scroll event on container
      container.dispatchEvent(new Event('scroll'))

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /scroll to top/i })).toBeInTheDocument()
      })

      // Click button
      const button = screen.getByRole('button', { name: /scroll to top/i })
      await user.click(button)

      // Should call container.scrollTo
      expect(containerScrollToMock).toHaveBeenCalledWith({
        top: 0,
        behavior: 'smooth',
      })

      // Cleanup
      document.body.removeChild(container)
    })
  })

  describe('Event Listener Cleanup', () => {
    it('removes scroll event listener on unmount', () => {
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

      const { unmount } = render(<ScrollToTopFAB />)

      unmount()

      expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function))

      removeEventListenerSpy.mockRestore()
    })
  })
})
