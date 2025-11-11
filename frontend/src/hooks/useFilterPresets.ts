import { useState, useEffect } from 'react'
import type { ScreeningFilters } from '@/types/screening'

/**
 * Filter preset interface
 */
export interface FilterPreset {
  id: string
  name: string
  description?: string
  filters: ScreeningFilters
  createdAt: string
}

/**
 * Local storage key for filter presets
 */
const STORAGE_KEY = 'stock_screener_filter_presets'

/**
 * Custom hook for managing filter presets with localStorage
 *
 * Features:
 * - Save current filters as a preset
 * - Load saved presets
 * - Delete presets
 * - Update preset name/description
 * - Automatic localStorage synchronization
 *
 * @returns Object with presets array and management functions
 */
export function useFilterPresets() {
  const [presets, setPresets] = useState<FilterPreset[]>([])

  // Load presets from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved) as FilterPreset[]
        setPresets(parsed)
      }
    } catch (error) {
      console.error('Failed to load filter presets:', error)
    }
  }, [])

  // Save presets to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(presets))
    } catch (error) {
      console.error('Failed to save filter presets:', error)
    }
  }, [presets])

  /**
   * Save current filters as a new preset
   */
  const savePreset = (name: string, filters: ScreeningFilters, description?: string) => {
    const newPreset: FilterPreset = {
      id: Date.now().toString(),
      name,
      description,
      filters,
      createdAt: new Date().toISOString(),
    }

    setPresets((prev) => [...prev, newPreset])
    return newPreset
  }

  /**
   * Update an existing preset
   */
  const updatePreset = (
    id: string,
    updates: { name?: string; description?: string; filters?: ScreeningFilters }
  ) => {
    setPresets((prev) =>
      prev.map((preset) =>
        preset.id === id
          ? {
              ...preset,
              ...updates,
            }
          : preset
      )
    )
  }

  /**
   * Delete a preset by ID
   */
  const deletePreset = (id: string) => {
    setPresets((prev) => prev.filter((preset) => preset.id !== id))
  }

  /**
   * Get a preset by ID
   */
  const getPreset = (id: string): FilterPreset | undefined => {
    return presets.find((preset) => preset.id === id)
  }

  /**
   * Clear all presets
   */
  const clearPresets = () => {
    setPresets([])
  }

  return {
    presets,
    savePreset,
    updatePreset,
    deletePreset,
    getPreset,
    clearPresets,
  }
}
