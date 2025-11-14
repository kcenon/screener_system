/**
 * WatchlistDialog Component
 * Modal for creating or editing a watchlist
 */

import { useState, useEffect } from 'react'
import { X, Folder, AlertCircle } from 'lucide-react'
import type { Watchlist } from '@/types/watchlist'

interface WatchlistDialogProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: { name: string; description?: string }) => Promise<void>
  watchlist?: Watchlist // If provided, edit mode; otherwise, create mode
  title?: string
}

const WATCHLIST_ICONS = ['📋', '💼', '💰', '👀', '📈', '🎯', '⭐', '🏆']

// Future feature: Color tags for watchlists
// const WATCHLIST_COLORS = [
//   'bg-blue-100 text-blue-800',
//   'bg-green-100 text-green-800',
//   'bg-purple-100 text-purple-800',
//   'bg-orange-100 text-orange-800',
//   'bg-pink-100 text-pink-800',
//   'bg-indigo-100 text-indigo-800',
// ]

export function WatchlistDialog({
  isOpen,
  onClose,
  onSave,
  watchlist,
  title,
}: WatchlistDialogProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [selectedIcon, setSelectedIcon] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Initialize form with watchlist data if editing
  useEffect(() => {
    if (watchlist) {
      setName(watchlist.name)
      setDescription(watchlist.description || '')
      setSelectedIcon(watchlist.icon || WATCHLIST_ICONS[0])
    } else {
      setName('')
      setDescription('')
      setSelectedIcon(WATCHLIST_ICONS[0])
    }
    setError(null)
  }, [watchlist, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!name.trim()) {
      setError('Watchlist name is required')
      return
    }

    if (name.length > 50) {
      setError('Watchlist name is too long (max 50 characters)')
      return
    }

    setIsSubmitting(true)

    try {
      await onSave({
        name: name.trim(),
        description: description.trim() || undefined,
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save watchlist')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    if (!isSubmitting) {
      onClose()
    }
  }

  if (!isOpen) return null

  const dialogTitle = title || (watchlist ? 'Edit Watchlist' : 'Create New Watchlist')

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={handleClose}
      />

      {/* Dialog */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Folder className="w-6 h-6 text-blue-600" />
              {dialogTitle}
            </h2>
            <button
              onClick={handleClose}
              disabled={isSubmitting}
              className="
                text-gray-400 hover:text-gray-600
                disabled:opacity-50 disabled:cursor-not-allowed
              "
              aria-label="Close"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Body */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Name Input */}
            <div>
              <label htmlFor="watchlist-name" className="block text-sm font-medium text-gray-700">
                Watchlist Name <span className="text-red-500">*</span>
              </label>
              <input
                id="watchlist-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., My Favorites, Tech Stocks"
                maxLength={50}
                disabled={isSubmitting}
                className="
                  mt-1 block w-full rounded-lg
                  border border-gray-300
                  px-4 py-2
                  text-gray-900
                  placeholder:text-gray-400
                  focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none
                  disabled:bg-gray-100 disabled:cursor-not-allowed
                "
                autoFocus
              />
              <p className="mt-1 text-xs text-gray-500">
                {name.length}/50 characters
              </p>
            </div>

            {/* Description Input */}
            <div>
              <label
                htmlFor="watchlist-description"
                className="block text-sm font-medium text-gray-700"
              >
                Description (Optional)
              </label>
              <textarea
                id="watchlist-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add a brief description..."
                rows={3}
                maxLength={200}
                disabled={isSubmitting}
                className="
                  mt-1 block w-full rounded-lg
                  border border-gray-300
                  px-4 py-2
                  text-gray-900
                  placeholder:text-gray-400
                  focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none
                  disabled:bg-gray-100 disabled:cursor-not-allowed
                  resize-none
                "
              />
              <p className="mt-1 text-xs text-gray-500">
                {description.length}/200 characters
              </p>
            </div>

            {/* Icon Picker (Optional Feature) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Icon (Optional)
              </label>
              <div className="flex flex-wrap gap-2">
                {WATCHLIST_ICONS.map((icon) => (
                  <button
                    key={icon}
                    type="button"
                    onClick={() => setSelectedIcon(icon)}
                    disabled={isSubmitting}
                    className={`
                      w-10 h-10 rounded-lg
                      flex items-center justify-center
                      text-xl
                      border-2 transition-colors
                      ${
                        selectedIcon === icon
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }
                      disabled:opacity-50 disabled:cursor-not-allowed
                    `}
                  >
                    {icon}
                  </button>
                ))}
              </div>
            </div>
          </form>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 rounded-b-lg">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="
                px-4 py-2 rounded-lg
                text-gray-700 bg-white border border-gray-300
                hover:bg-gray-50
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              Cancel
            </button>
            <button
              type="submit"
              onClick={handleSubmit}
              disabled={isSubmitting || !name.trim()}
              className="
                px-4 py-2 rounded-lg
                text-white bg-blue-600
                hover:bg-blue-700
                disabled:opacity-50 disabled:cursor-not-allowed
                flex items-center gap-2
              "
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>{watchlist ? 'Save Changes' : 'Create Watchlist'}</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
