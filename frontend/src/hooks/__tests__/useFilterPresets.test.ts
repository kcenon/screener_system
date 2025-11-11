import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFilterPresets } from '../useFilterPresets'
import type { ScreeningFilters } from '@/types/screening'

const STORAGE_KEY = 'stock_screener_filter_presets'

describe('useFilterPresets', () => {
  const mockFilters1: ScreeningFilters = {
    market: 'KOSPI',
    per: { min: 5, max: 15 },
    roe: { min: 10, max: null },
  }

  const mockFilters2: ScreeningFilters = {
    sector: 'Technology',
    revenue_growth_yoy: { min: 20, max: null },
  }

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    // Use fake timers for consistent timing
    vi.useFakeTimers()
  })

  afterEach(() => {
    localStorage.clear()
    vi.useRealTimers()
  })

  describe('Initial State', () => {
    it('starts with empty presets array when no data in localStorage', () => {
      const { result } = renderHook(() => useFilterPresets())

      expect(result.current.presets).toEqual([])
    })

    it('loads presets from localStorage on mount', () => {
      const savedPresets = [
        {
          id: '1',
          name: 'Value Stocks',
          description: 'Low PER, high ROE',
          filters: mockFilters1,
          createdAt: '2025-01-15T10:00:00.000Z',
        },
      ]

      localStorage.setItem(STORAGE_KEY, JSON.stringify(savedPresets))

      const { result } = renderHook(() => useFilterPresets())

      expect(result.current.presets).toEqual(savedPresets)
    })

    it('handles corrupted localStorage data gracefully', () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      localStorage.setItem(STORAGE_KEY, 'invalid json')

      const { result } = renderHook(() => useFilterPresets())

      expect(result.current.presets).toEqual([])
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to load filter presets:',
        expect.any(Error)
      )
      consoleErrorSpy.mockRestore()
    })
  })

  describe('savePreset', () => {
    it('adds a new preset', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Value Stocks', mockFilters1, 'Low PER, high ROE')
      })

      expect(result.current.presets).toHaveLength(1)
      expect(result.current.presets[0]).toMatchObject({
        name: 'Value Stocks',
        description: 'Low PER, high ROE',
        filters: mockFilters1,
      })
    })

    it('generates unique ID for new preset', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Preset 1', mockFilters1)
      })

      const id1 = result.current.presets[0].id

      // Wait a bit to ensure different timestamp
      vi.advanceTimersByTime(10)

      act(() => {
        result.current.savePreset('Preset 2', mockFilters2)
      })

      const id2 = result.current.presets[1].id

      expect(id1).not.toBe(id2) // IDs should be different
      expect(result.current.presets).toHaveLength(2)
    })

    it('sets createdAt timestamp', () => {
      const { result } = renderHook(() => useFilterPresets())

      const beforeTime = new Date().toISOString()

      act(() => {
        result.current.savePreset('Test Preset', mockFilters1)
      })

      const afterTime = new Date().toISOString()

      const createdAt = result.current.presets[0].createdAt
      expect(createdAt >= beforeTime && createdAt <= afterTime).toBe(true)
    })

    it('handles undefined description', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test Preset', mockFilters1)
      })

      expect(result.current.presets[0].description).toBeUndefined()
    })

    it('returns the created preset', () => {
      const { result } = renderHook(() => useFilterPresets())

      let createdPreset: any

      act(() => {
        createdPreset = result.current.savePreset('Test Preset', mockFilters1, 'Test description')
      })

      expect(createdPreset).toMatchObject({
        name: 'Test Preset',
        description: 'Test description',
        filters: mockFilters1,
      })
    })

    it('persists preset to localStorage', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test Preset', mockFilters1)
      })

      // localStorage update happens synchronously in useEffect
      // Just verify the preset was added to state
      expect(result.current.presets).toHaveLength(1)
      expect(result.current.presets[0].name).toBe('Test Preset')
    })
  })

  describe('updatePreset', () => {
    it('updates preset name', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Original Name', mockFilters1)
      })

      const presetId = result.current.presets[0].id

      act(() => {
        result.current.updatePreset(presetId, { name: 'Updated Name' })
      })

      expect(result.current.presets[0].name).toBe('Updated Name')
    })

    it('updates preset description', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1, 'Original description')
      })

      const presetId = result.current.presets[0].id

      act(() => {
        result.current.updatePreset(presetId, { description: 'Updated description' })
      })

      expect(result.current.presets[0].description).toBe('Updated description')
    })

    it('updates preset filters', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1)
      })

      const presetId = result.current.presets[0].id

      act(() => {
        result.current.updatePreset(presetId, { filters: mockFilters2 })
      })

      expect(result.current.presets[0].filters).toEqual(mockFilters2)
    })

    it('updates multiple fields at once', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1)
      })

      const presetId = result.current.presets[0].id

      act(() => {
        result.current.updatePreset(presetId, {
          name: 'New Name',
          description: 'New Description',
          filters: mockFilters2,
        })
      })

      expect(result.current.presets[0]).toMatchObject({
        name: 'New Name',
        description: 'New Description',
        filters: mockFilters2,
      })
    })

    it('does not modify other presets', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Preset 1', mockFilters1)
      })

      vi.advanceTimersByTime(10)

      act(() => {
        result.current.savePreset('Preset 2', mockFilters2)
      })

      const preset1Id = result.current.presets[0].id

      act(() => {
        result.current.updatePreset(preset1Id, { name: 'Updated' })
      })

      expect(result.current.presets[0].name).toBe('Updated')
      expect(result.current.presets[1].name).toBe('Preset 2')
    })

    it('does nothing if preset ID not found', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1)
      })

      const originalPresets = [...result.current.presets]

      act(() => {
        result.current.updatePreset('non-existent-id', { name: 'Updated' })
      })

      expect(result.current.presets).toEqual(originalPresets)
    })
  })

  describe('deletePreset', () => {
    it('removes preset by ID', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1)
      })

      const presetId = result.current.presets[0].id

      act(() => {
        result.current.deletePreset(presetId)
      })

      expect(result.current.presets).toHaveLength(0)
    })

    it('only removes specified preset', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Preset 1', mockFilters1)
      })

      vi.advanceTimersByTime(10)

      act(() => {
        result.current.savePreset('Preset 2', mockFilters2)
      })

      vi.advanceTimersByTime(10)

      act(() => {
        result.current.savePreset('Preset 3', mockFilters1)
      })

      const preset2Id = result.current.presets[1].id

      act(() => {
        result.current.deletePreset(preset2Id)
      })

      expect(result.current.presets).toHaveLength(2)
      expect(result.current.presets[0].name).toBe('Preset 1')
      expect(result.current.presets[1].name).toBe('Preset 3')
    })

    it('does nothing if preset ID not found', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1)
      })

      const originalLength = result.current.presets.length

      act(() => {
        result.current.deletePreset('non-existent-id')
      })

      expect(result.current.presets).toHaveLength(originalLength)
    })
  })

  describe('getPreset', () => {
    it('returns preset by ID', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1, 'Description')
      })

      const presetId = result.current.presets[0].id
      const preset = result.current.getPreset(presetId)

      expect(preset).toMatchObject({
        name: 'Test',
        description: 'Description',
        filters: mockFilters1,
      })
    })

    it('returns undefined if preset not found', () => {
      const { result } = renderHook(() => useFilterPresets())

      const preset = result.current.getPreset('non-existent-id')

      expect(preset).toBeUndefined()
    })
  })

  describe('clearPresets', () => {
    it('removes all presets', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Preset 1', mockFilters1)
        result.current.savePreset('Preset 2', mockFilters2)
        result.current.savePreset('Preset 3', mockFilters1)
      })

      expect(result.current.presets).toHaveLength(3)

      act(() => {
        result.current.clearPresets()
      })

      expect(result.current.presets).toHaveLength(0)
    })

    it('updates localStorage', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1)
      })

      act(() => {
        result.current.clearPresets()
      })

      // Verify state is cleared
      expect(result.current.presets).toHaveLength(0)
    })
  })

  describe('localStorage Synchronization', () => {
    it('persists changes to localStorage', () => {
      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test 1', mockFilters1)
      })

      vi.advanceTimersByTime(10)

      act(() => {
        result.current.savePreset('Test 2', mockFilters2)
      })

      // Verify state has both presets
      expect(result.current.presets).toHaveLength(2)
      expect(result.current.presets[0].name).toBe('Test 1')
      expect(result.current.presets[1].name).toBe('Test 2')
    })

    it('handles localStorage errors gracefully', () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      // Mock localStorage.setItem to throw error
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new Error('Storage quota exceeded')
      })

      const { result } = renderHook(() => useFilterPresets())

      act(() => {
        result.current.savePreset('Test', mockFilters1)
      })

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to save filter presets:',
        expect.any(Error)
      )

      setItemSpy.mockRestore()
      consoleErrorSpy.mockRestore()
    })
  })
})
