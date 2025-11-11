import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FilterPresetManager from '../FilterPresetManager'
import type { FilterPreset } from '@/hooks/useFilterPresets'
import type { ScreeningFilters } from '@/types/screening'

describe('FilterPresetManager', () => {
  const mockFilters: ScreeningFilters = {
    market: 'KOSPI',
    per: { min: 5, max: 15 },
    roe: { min: 10, max: null },
  }

  const mockPresets: FilterPreset[] = [
    {
      id: '1',
      name: 'Value Stocks',
      description: 'Low PER, high ROE stocks',
      filters: mockFilters,
      createdAt: '2025-01-15T10:00:00.000Z',
    },
    {
      id: '2',
      name: 'Growth Stocks',
      description: 'High growth potential',
      filters: { revenue_growth_yoy: { min: 20, max: null } },
      createdAt: '2025-01-16T11:30:00.000Z',
    },
    {
      id: '3',
      name: 'Tech Stocks',
      // No description
      filters: { sector: 'Technology' },
      createdAt: '2025-01-17T14:00:00.000Z',
    },
  ]

  let onLoadPresetMock: ReturnType<typeof vi.fn>
  let onSavePresetMock: ReturnType<typeof vi.fn>
  let onDeletePresetMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    onLoadPresetMock = vi.fn()
    onSavePresetMock = vi.fn()
    onDeletePresetMock = vi.fn()
  })

  describe('Rendering', () => {
    it('renders "Saved Presets" label', () => {
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      expect(screen.getByText('Saved Presets')).toBeInTheDocument()
    })

    it('renders "Save Current" button', () => {
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      expect(screen.getByRole('button', { name: /save current/i })).toBeInTheDocument()
    })

    it('displays empty state message when no presets', () => {
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      expect(screen.getByText(/no saved presets yet/i)).toBeInTheDocument()
      expect(screen.getByText(/click.*save current.*to save your filters/i)).toBeInTheDocument()
    })

    it('renders list of presets', () => {
      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      expect(screen.getByText('Value Stocks')).toBeInTheDocument()
      expect(screen.getByText('Growth Stocks')).toBeInTheDocument()
      expect(screen.getByText('Tech Stocks')).toBeInTheDocument()
    })

    it('displays preset descriptions when available', () => {
      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      expect(screen.getByText('Low PER, high ROE stocks')).toBeInTheDocument()
      expect(screen.getByText('High growth potential')).toBeInTheDocument()
    })

    it('displays preset creation dates', () => {
      const { container } = render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      // Dates should be formatted as locale date strings
      // Check that dates are displayed (format may vary by locale)
      const dateElements = container.querySelectorAll('.text-xs.text-gray-400')
      expect(dateElements).toHaveLength(3)

      // Verify dates contain year 2025 (locale-independent check)
      const dateTexts = Array.from(dateElements).map(el => el.textContent)
      expect(dateTexts.every(text => text && text.includes('2025'))).toBe(true)
    })

    it('does not display empty state when presets exist', () => {
      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      expect(screen.queryByText(/no saved presets yet/i)).not.toBeInTheDocument()
    })
  })

  describe('Save Dialog', () => {
    it('opens save dialog when "Save Current" button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      const saveButton = screen.getByRole('button', { name: /save current/i })
      await user.click(saveButton)

      expect(screen.getByRole('dialog')).toBeInTheDocument()
      expect(screen.getByText('Save Filter Preset')).toBeInTheDocument()
    })

    it('renders preset name input in dialog', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      expect(nameInput).toBeInTheDocument()
      expect(nameInput).toHaveAttribute('placeholder', 'e.g., High Growth Tech Stocks')
    })

    it('renders optional description textarea in dialog', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const descriptionInput = screen.getByLabelText(/description \(optional\)/i)
      expect(descriptionInput).toBeInTheDocument()
      expect(descriptionInput.tagName).toBe('TEXTAREA')
    })

    it('autofocuses preset name input when dialog opens', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      expect(nameInput).toHaveFocus()
    })

    it('renders Cancel and Save Preset buttons', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /save preset/i })).toBeInTheDocument()
    })

    it('disables Save button when preset name is empty', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const saveButton = screen.getByRole('button', { name: /save preset/i })
      expect(saveButton).toBeDisabled()
    })

    it('enables Save button when preset name is entered', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      await user.type(nameInput, 'My Preset')

      const saveButton = screen.getByRole('button', { name: /save preset/i })
      expect(saveButton).not.toBeDisabled()
    })

    it('disables Save button when preset name is only whitespace', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      await user.type(nameInput, '   ')

      const saveButton = screen.getByRole('button', { name: /save preset/i })
      expect(saveButton).toBeDisabled()
    })

    it('calls onSavePreset with trimmed name when Save button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      await user.type(nameInput, '  My Preset  ')

      const saveButton = screen.getByRole('button', { name: /save preset/i })
      await user.click(saveButton)

      expect(onSavePresetMock).toHaveBeenCalledWith('My Preset', undefined)
    })

    it('calls onSavePreset with name and description when both provided', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      const descriptionInput = screen.getByLabelText(/description \(optional\)/i)

      await user.type(nameInput, 'My Preset')
      await user.type(descriptionInput, 'My description')

      const saveButton = screen.getByRole('button', { name: /save preset/i })
      await user.click(saveButton)

      expect(onSavePresetMock).toHaveBeenCalledWith('My Preset', 'My description')
    })

    it('calls onSavePreset with undefined description when description is only whitespace', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      const descriptionInput = screen.getByLabelText(/description \(optional\)/i)

      await user.type(nameInput, 'My Preset')
      await user.type(descriptionInput, '   ')

      const saveButton = screen.getByRole('button', { name: /save preset/i })
      await user.click(saveButton)

      expect(onSavePresetMock).toHaveBeenCalledWith('My Preset', undefined)
    })

    it('closes dialog after saving preset', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      await user.type(nameInput, 'My Preset')

      const saveButton = screen.getByRole('button', { name: /save preset/i })
      await user.click(saveButton)

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('clears form inputs after saving preset', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      // First save
      await user.click(screen.getByRole('button', { name: /save current/i }))
      const nameInput1 = screen.getByLabelText(/preset name/i)
      const descInput1 = screen.getByLabelText(/description \(optional\)/i)
      await user.type(nameInput1, 'Preset 1')
      await user.type(descInput1, 'Description 1')
      await user.click(screen.getByRole('button', { name: /save preset/i }))

      // Open dialog again
      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput2 = screen.getByLabelText(/preset name/i)
      const descInput2 = screen.getByLabelText(/description \(optional\)/i)

      expect(nameInput2).toHaveValue('')
      expect(descInput2).toHaveValue('')
    })

    it('closes dialog when Cancel button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))
      expect(screen.getByRole('dialog')).toBeInTheDocument()

      const cancelButton = screen.getByRole('button', { name: /cancel/i })
      await user.click(cancelButton)

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('does not call onSavePreset when Cancel button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={[]}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      await user.click(screen.getByRole('button', { name: /save current/i }))

      const nameInput = screen.getByLabelText(/preset name/i)
      await user.type(nameInput, 'My Preset')

      const cancelButton = screen.getByRole('button', { name: /cancel/i })
      await user.click(cancelButton)

      expect(onSavePresetMock).not.toHaveBeenCalled()
    })
  })

  describe('Load Preset', () => {
    it('calls onLoadPreset when preset is clicked', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      const preset = screen.getByText('Value Stocks').closest('div[class*="cursor-pointer"]')!
      await user.click(preset)

      expect(onLoadPresetMock).toHaveBeenCalledWith(mockPresets[0].filters)
    })

    it('loads correct filters for each preset', async () => {
      const user = userEvent.setup()
      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      // Click second preset
      const preset2 = screen.getByText('Growth Stocks').closest('div[class*="cursor-pointer"]')!
      await user.click(preset2)

      expect(onLoadPresetMock).toHaveBeenCalledWith(mockPresets[1].filters)
    })
  })

  describe('Delete Preset', () => {
    it('renders delete button for each preset', () => {
      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: /delete preset/i })
      expect(deleteButtons).toHaveLength(mockPresets.length)
    })

    it('shows confirmation dialog before deleting', async () => {
      const user = userEvent.setup()
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)

      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: /delete preset/i })
      await user.click(deleteButtons[0])

      expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this preset?')
      confirmSpy.mockRestore()
    })

    it('calls onDeletePreset when confirmed', async () => {
      const user = userEvent.setup()
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)

      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: /delete preset/i })
      await user.click(deleteButtons[0])

      expect(onDeletePresetMock).toHaveBeenCalledWith(mockPresets[0].id)
      confirmSpy.mockRestore()
    })

    it('does not call onDeletePreset when cancelled', async () => {
      const user = userEvent.setup()
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)

      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: /delete preset/i })
      await user.click(deleteButtons[0])

      expect(onDeletePresetMock).not.toHaveBeenCalled()
      confirmSpy.mockRestore()
    })

    it('prevents event propagation when delete button is clicked', async () => {
      const user = userEvent.setup()
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)

      render(
        <FilterPresetManager
          presets={mockPresets}
          onLoadPreset={onLoadPresetMock}
          onSavePreset={onSavePresetMock}
          onDeletePreset={onDeletePresetMock}
        />
      )

      const deleteButtons = screen.getAllByRole('button', { name: /delete preset/i })
      await user.click(deleteButtons[0])

      // onLoadPreset should NOT be called (event should not propagate to parent div)
      expect(onLoadPresetMock).not.toHaveBeenCalled()
      expect(onDeletePresetMock).toHaveBeenCalled()
      confirmSpy.mockRestore()
    })
  })
})
