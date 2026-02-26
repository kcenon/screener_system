import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SearchBar from '../SearchBar'

describe('SearchBar', () => {
  let onChangeMock: (value: string) => void

  beforeEach(() => {
    onChangeMock = vi.fn()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Rendering', () => {
    it('renders search input with default placeholder', () => {
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox', { name: /search stocks/i })
      expect(input).toBeInTheDocument()
      expect(input).toHaveAttribute(
        'placeholder',
        'Search by stock code or name (e.g., 005930 or Samsung)',
      )
    })

    it('renders with custom placeholder', () => {
      render(
        <SearchBar
          value=""
          onChange={onChangeMock}
          placeholder="Custom placeholder"
        />,
      )

      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('placeholder', 'Custom placeholder')
    })

    it('renders keyboard shortcut hint when enabled and input is empty', () => {
      render(
        <SearchBar value="" onChange={onChangeMock} enableShortcut={true} />,
      )

      // Keyboard shortcut hint should be visible
      expect(screen.getByText('⌘K')).toBeInTheDocument()
    })

    it('does not render keyboard shortcut hint when disabled', () => {
      render(
        <SearchBar value="" onChange={onChangeMock} enableShortcut={false} />,
      )

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
      const user = userEvent.setup()
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox')
      await user.type(input, 'Samsung')

      expect(input).toHaveValue('Samsung')
    })

    it('debounces onChange callback (300ms)', async () => {
      const user = userEvent.setup()
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox')

      // Type into input
      await user.type(input, 'Sam')

      // Should not call onChange immediately
      expect(onChangeMock).not.toHaveBeenCalled()

      // Wait for debounce (300ms)
      await waitFor(
        () => {
          expect(onChangeMock).toHaveBeenCalledWith('Sam')
        },
        { timeout: 500 },
      )

      expect(onChangeMock).toHaveBeenCalledTimes(1)
    })

    it('debounces multiple rapid inputs correctly', async () => {
      const user = userEvent.setup()
      render(<SearchBar value="" onChange={onChangeMock} />)

      const input = screen.getByRole('textbox')

      // Type quickly
      await user.type(input, 'Sam')

      // Should not have called onChange yet
      expect(onChangeMock).not.toHaveBeenCalled()

      // Wait for debounce to complete
      await waitFor(
        () => {
          expect(onChangeMock).toHaveBeenCalledWith('Sam')
        },
        { timeout: 500 },
      )

      // Should call onChange only once with final value
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

      const clearButton = screen.queryByRole('button', {
        name: /clear search/i,
      })
      expect(clearButton).not.toBeInTheDocument()
    })

    it('clears input and calls onChange when clear button is clicked', async () => {
      const user = userEvent.setup()
      render(<SearchBar value="Samsung" onChange={onChangeMock} />)

      const clearButton = screen.getByRole('button', { name: /clear search/i })
      await user.click(clearButton)

      const input = screen.getByRole('textbox')
      expect(input).toHaveValue('')
      expect(onChangeMock).toHaveBeenCalledWith('')
    })

    it('focuses input after clearing', async () => {
      const user = userEvent.setup()
      render(<SearchBar value="Samsung" onChange={onChangeMock} />)

      const clearButton = screen.getByRole('button', { name: /clear search/i })
      await user.click(clearButton)

      const input = screen.getByRole('textbox')
      expect(input).toHaveFocus()
    })
  })

  describe('Keyboard Shortcut', () => {
    it('focuses input on Ctrl+K', async () => {
      render(
        <SearchBar value="" onChange={onChangeMock} enableShortcut={true} />,
      )

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
      render(
        <SearchBar value="" onChange={onChangeMock} enableShortcut={true} />,
      )

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
      render(
        <SearchBar value="" onChange={onChangeMock} enableShortcut={false} />,
      )

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
      render(
        <SearchBar value="" onChange={onChangeMock} enableShortcut={true} />,
      )

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
      const { rerender } = render(
        <SearchBar value="Initial" onChange={onChangeMock} />,
      )

      const input = screen.getByRole('textbox')
      expect(input).toHaveValue('Initial')

      // Update prop value
      rerender(<SearchBar value="Updated" onChange={onChangeMock} />)

      expect(input).toHaveValue('Updated')
    })

    it('does not call onChange when value prop is updated externally', async () => {
      const { rerender } = render(
        <SearchBar value="" onChange={onChangeMock} />,
      )

      rerender(<SearchBar value="External Update" onChange={onChangeMock} />)

      // Wait to ensure debounce would have completed
      await new Promise(resolve => setTimeout(resolve, 400))

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
      const { container } = render(
        <SearchBar value="" onChange={onChangeMock} />,
      )

      const searchIcon = container.querySelector('svg[aria-hidden="true"]')
      expect(searchIcon).toBeInTheDocument()
    })
  })
})
