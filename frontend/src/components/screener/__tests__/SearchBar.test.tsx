import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SearchBar from '../SearchBar'

describe('SearchBar', () => {
  let onChangeMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    onChangeMock = vi.fn()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  describe('Rendering', () => {
    it('renders search input with default placeholder', () => {
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox', { name: /search stocks/i })
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute(
        'placeholder',
        'Search by stock code or name (e.g., 005930 or Samsung)'
      )
    })

    it('renders with custom placeholder', () => {
      render(
        <SearchBar
          value=""
          onChange={onChangeMock}
          placeholder="Custom placeholder"
        />
      )

      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('placeholder', 'Custom placeholder')
    })

    it('renders keyboard shortcut hint when enabled and input is empty', () => {
      render(<SearchBar value="" onChange={onChangeMock} enableShortcut={true} />)

      // Keyboard shortcut hint should be visible
      expect(screen.getByText('⌘K')).toBeInTheDocument()
    })

    it('does not render keyboard shortcut hint when disabled', () => {
      render(<SearchBar value="" onChange={onChangeMock} enableShortcut={false} />)

      expect(screen.queryByText('⌘K')).not.toBeInTheDocument()
    })

    it('displays initial value', () => {
      render(<SearchBar value="Samsung" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox')
      expect(input).toHaveValue('Samsung')
    })
  })

  describe('User Input', () => {
    it('updates input value on user typing', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox')
      await user.type(input, 'Samsung')

      expect(input).toHaveValue('Samsung')
    })

    it('debounces onChange callback (300ms)', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox')

      // Type into input
      await user.type(input, 'Sam')

      // Should not call onChange immediately
      expect(onChangeMock).not.toHaveBeenCalled()

      // Fast-forward 300ms to trigger debounce
      act(() => {
        vi.advanceTimersByTime(300)
      })

      // After debounce, onChange should be called
      expect(onChangeMock).toHaveBeenCalledWith('Sam')
      expect(onChangeMock).toHaveBeenCalledTimes(1)
    })

    it('debounces multiple rapid inputs correctly', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox')

      // Type quickly
      await user.type(input, 'S')
      act(() => vi.advanceTimersByTime(100))

      await user.type(input, 'a')
      act(() => vi.advanceTimersByTime(100))

      await user.type(input, 'm')

      // Should not have called onChange yet (only 200ms passed)
      expect(onChangeMock).not.toHaveBeenCalled()

      // Wait for full debounce period
      act(() => {
        vi.advanceTimersByTime(300)
      })

      // Should call onChange only once with final value
      expect(onChangeMock).toHaveBeenCalledWith('Sam')
      expect(onChangeMock).toHaveBeenCalledTimes(1)
    })
  })

  describe('Clear Button', () => {
    it('shows clear button when input has value', () => {
      render(<SearchBar value="Samsung" onChange={onChangeMock} />)

      const clearButton = screen.getByRole('button', { name: /clear search/i })
      expect(clearButton).toBeInTheDocument()
    })

    it('does not show clear button when input is empty', () => {
      render(<SearchBar value="" onChange={onChangeMock} />)

      const clearButton = screen.queryByRole('button', { name: /clear search/i })
      expect(clearButton).not.toBeInTheDocument()
    })

    it('clears input and calls onChange when clear button is clicked', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBar value="Samsung" onChange={onChangeMock} />)

      const clearButton = screen.getByRole('button', { name: /clear search/i })
      await user.click(clearButton)

      const input = screen.getByRole('textbox')
      expect(input).toHaveValue('')
      expect(onChangeMock).toHaveBeenCalledWith('')
    })

    it('focuses input after clearing', async () => {
      const user = userEvent.setup({ delay: null })
      render(<SearchBar value="Samsung" onChange={onChangeMock} />)

      const clearButton = screen.getByRole('button', { name: /clear search/i })
      await user.click(clearButton)

      const input = screen.getByRole('textbox')
      expect(input).toHaveFocus()
    })
  })

  describe('Keyboard Shortcut', () => {
    it('focuses input on Ctrl+K', async () => {
      render(<SearchBar value="" onChange={onChangeMock} enableShortcut={true} />)

      const input = screen.getByRole('textbox')
      expect(input).not.toHaveFocus()

      // Simulate Ctrl+K
      const event = new KeyboardEvent('keydown', {
        key: 'k',
        ctrlKey: true,
        bubbles: true,
      })
      document.dispatchEvent(event)

      expect(input).toHaveFocus()
    })

    it('focuses input on Cmd+K (Meta key)', async () => {
      render(<SearchBar value="" onChange={onChangeMock} enableShortcut={true} />)

      const input = screen.getByRole('textbox')
      expect(input).not.toHaveFocus()

      // Simulate Cmd+K (Meta key for macOS)
      const event = new KeyboardEvent('keydown', {
        key: 'k',
        metaKey: true,
        bubbles: true,
      })
      document.dispatchEvent(event)

      expect(input).toHaveFocus()
    })

    it('does not focus input when shortcut is disabled', async () => {
      render(<SearchBar value="" onChange={onChangeMock} enableShortcut={false} />)

      const input = screen.getByRole('textbox')

      // Simulate Ctrl+K
      const event = new KeyboardEvent('keydown', {
        key: 'k',
        ctrlKey: true,
        bubbles: true,
      })
      document.dispatchEvent(event)

      expect(input).not.toHaveFocus()
    })

    it('prevents default browser behavior on Ctrl+K', async () => {
      render(<SearchBar value="" onChange={onChangeMock} enableShortcut={true} />)

      const event = new KeyboardEvent('keydown', {
        key: 'k',
        ctrlKey: true,
        bubbles: true,
        cancelable: true,
      })

      const preventDefaultSpy = vi.spyOn(event, 'preventDefault')
      document.dispatchEvent(event)

      expect(preventDefaultSpy).toHaveBeenCalled()
    })
  })

  describe('Value Synchronization', () => {
    it('syncs local value when prop value changes', () => {
      const { rerender } = render(<SearchBar value="Initial" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox')
      expect(input).toHaveValue('Initial')

      // Update prop value
      rerender(<SearchBar value="Updated" onChange={onChangeMock} />)

      expect(input).toHaveValue('Updated')
    })

    it('does not call onChange when value prop is updated externally', () => {
      const { rerender } = render(<SearchBar value="" onChange={onChangeMock} />)

      rerender(<SearchBar value="External Update" onChange={onChangeMock} />)

      // Advance timers to ensure debounce completes
      vi.advanceTimersByTime(300)

      // Should not call onChange (external update, not user input)
      expect(onChangeMock).not.toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA label for input', () => {
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox', { name: /search stocks/i })
      expect(input).toHaveAccessibleName('Search stocks')
    })

    it('has proper ARIA label for clear button', () => {
      render(<SearchBar value="Samsung" onChange={onChangeMock} />)

      const clearButton = screen.getByRole('button', { name: /clear search/i })
      expect(clearButton).toHaveAccessibleName('Clear search')
    })

    it('marks search icon as aria-hidden', () => {
      const { container } = render(<SearchBar value="" onChange={onChangeMock} />)

      const searchIcon = container.querySelector('svg[aria-hidden="true"]')
      expect(searchIcon).toBeInTheDocument()
    })
  })
})
