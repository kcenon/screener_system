import { useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import type { FilterPreset } from '@/hooks/useFilterPresets'
import type { ScreeningFilters } from '@/types/screening'

/**
 * Props for FilterPresetManager component
 */
interface FilterPresetManagerProps {
  /** List of saved presets */
  presets: FilterPreset[]
  /** Callback when a preset is loaded */
  onLoadPreset: (filters: ScreeningFilters) => void
  /** Callback when a preset is saved */
  onSavePreset: (name: string, description?: string) => void
  /** Callback when a preset is deleted */
  onDeletePreset: (id: string) => void
}

/**
 * FilterPresetManager component for managing filter presets
 *
 * Features:
 * - Display list of saved presets
 * - Save current filters as preset
 * - Load preset filters
 * - Delete presets
 * - Modal dialog for save preset
 */
export default function FilterPresetManager({
  presets,
  onLoadPreset,
  onSavePreset,
  onDeletePreset,
}: FilterPresetManagerProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [presetName, setPresetName] = useState('')
  const [presetDescription, setPresetDescription] = useState('')

  const handleSave = () => {
    if (!presetName.trim()) return

    onSavePreset(presetName.trim(), presetDescription.trim() || undefined)
    setPresetName('')
    setPresetDescription('')
    setIsDialogOpen(false)
  }

  const handleLoad = (preset: FilterPreset) => {
    onLoadPreset(preset.filters)
  }

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Are you sure you want to delete this preset?')) {
      onDeletePreset(id)
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Saved Presets
        </label>
        <Dialog.Root open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <Dialog.Trigger asChild>
            <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium transition-colors">
              Save Current
            </button>
          </Dialog.Trigger>

          <Dialog.Portal>
            <Dialog.Overlay className="fixed inset-0 bg-black/50 dark:bg-black/70 z-50 transition-colors" />
            <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md z-50 transition-colors">
              <Dialog.Title className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Save Filter Preset
              </Dialog.Title>
              <Dialog.Description className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Enter a name for your filter preset to save it for future use.
              </Dialog.Description>

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="preset-name"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Preset Name *
                  </label>
                  <input
                    id="preset-name"
                    type="text"
                    value={presetName}
                    onChange={e => setPresetName(e.target.value)}
                    placeholder="e.g., High Growth Tech Stocks"
                    className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-400 px-3 py-2 text-sm shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors"
                    autoFocus
                  />
                </div>

                <div>
                  <label
                    htmlFor="preset-description"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Description (Optional)
                  </label>
                  <textarea
                    id="preset-description"
                    value={presetDescription}
                    onChange={e => setPresetDescription(e.target.value)}
                    placeholder="e.g., Technology stocks with >20% revenue growth"
                    rows={3}
                    className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-400 px-3 py-2 text-sm shadow-sm focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 resize-none transition-colors"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <Dialog.Close asChild>
                    <button className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
                      Cancel
                    </button>
                  </Dialog.Close>
                  <button
                    onClick={handleSave}
                    disabled={!presetName.trim()}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 dark:bg-blue-500 rounded-md hover:bg-blue-700 dark:hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Save Preset
                  </button>
                </div>
              </div>
            </Dialog.Content>
          </Dialog.Portal>
        </Dialog.Root>
      </div>

      {/* Presets List */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {presets.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            No saved presets yet.
            <br />
            Click &ldquo;Save Current&rdquo; to save your filters.
          </p>
        ) : (
          presets.map(preset => (
            <div
              key={preset.id}
              className="group flex items-start justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-md hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors"
              onClick={() => handleLoad(preset)}
            >
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {preset.name}
                </h4>
                {preset.description && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">
                    {preset.description}
                  </p>
                )}
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  {new Date(preset.createdAt).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={e => handleDelete(preset.id, e)}
                className="ml-2 p-1 text-gray-400 dark:text-gray-500 hover:text-red-600 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                aria-label="Delete preset"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
