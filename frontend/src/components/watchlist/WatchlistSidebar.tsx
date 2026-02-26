/**
 * WatchlistSidebar Component
 * Displays list of user's watchlists with stock counts
 */

import { Plus, Folder, Edit2, Trash2 } from 'lucide-react'
import type { Watchlist } from '@/types/watchlist'

interface WatchlistSidebarProps {
  watchlists: Watchlist[]
  activeWatchlistId: string | null
  onSelectWatchlist: (id: string) => void
  onCreateWatchlist: () => void
  onEditWatchlist: (watchlist: Watchlist) => void
  onDeleteWatchlist: (id: string) => void
  isLoading?: boolean
}

export function WatchlistSidebar({
  watchlists,
  activeWatchlistId,
  onSelectWatchlist,
  onCreateWatchlist,
  onEditWatchlist,
  onDeleteWatchlist,
  isLoading = false,
}: WatchlistSidebarProps) {
  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this watchlist?')) {
      onDeleteWatchlist(id)
    }
  }

  const handleEdit = (e: React.MouseEvent, watchlist: Watchlist) => {
    e.stopPropagation()
    onEditWatchlist(watchlist)
  }

  if (isLoading) {
    return (
      <div className="w-64 bg-white border-r border-gray-200 p-4">
        <div className="space-y-2">
          {[1, 2, 3].map(i => (
            <div
              key={i}
              className="h-16 bg-gray-100 rounded-lg animate-pulse"
            />
          ))}
        </div>
      </div>
    )
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onCreateWatchlist}
          className="
            w-full px-4 py-2 rounded-lg
            bg-blue-600 text-white
            hover:bg-blue-700
            flex items-center justify-center gap-2
            font-medium
            transition-colors
          "
        >
          <Plus className="w-4 h-4" />
          New Watchlist
        </button>
      </div>

      {/* Watchlist List */}
      <div className="flex-1 overflow-y-auto p-2">
        {watchlists.length === 0 ? (
          <div className="text-center py-8 px-4">
            <Folder className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">
              No watchlists yet.
              <br />
              Create one to get started!
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {watchlists.map(watchlist => {
              const isActive = watchlist.id === activeWatchlistId

              return (
                <div
                  key={watchlist.id}
                  onClick={() => onSelectWatchlist(watchlist.id)}
                  className={`
                    group
                    relative
                    px-3 py-3 rounded-lg
                    cursor-pointer
                    transition-colors
                    ${
                      isActive
                        ? 'bg-blue-50 border-2 border-blue-500'
                        : 'border-2 border-transparent hover:bg-gray-50'
                    }
                  `}
                >
                  {/* Main Content */}
                  <div className="flex items-start gap-3">
                    {/* Icon */}
                    <div className="text-2xl flex-shrink-0">
                      {watchlist.icon || '📋'}
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <h3
                        className={`
                          text-sm font-medium truncate
                          ${isActive ? 'text-blue-900' : 'text-gray-900'}
                        `}
                      >
                        {watchlist.name}
                      </h3>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {watchlist.stocks.length} stock
                        {watchlist.stocks.length !== 1 ? 's' : ''}
                      </p>
                    </div>

                    {/* Action Buttons (shown on hover or when active) */}
                    <div
                      className={`
                        flex items-center gap-1
                        ${isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}
                        transition-opacity
                      `}
                    >
                      <button
                        onClick={e => handleEdit(e, watchlist)}
                        className="
                          p-1 rounded
                          text-gray-400 hover:text-blue-600 hover:bg-blue-100
                          transition-colors
                        "
                        title="Edit watchlist"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={e => handleDelete(e, watchlist.id)}
                        className="
                          p-1 rounded
                          text-gray-400 hover:text-red-600 hover:bg-red-100
                          transition-colors
                        "
                        title="Delete watchlist"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Description (if available) */}
                  {watchlist.description && (
                    <p className="text-xs text-gray-500 mt-2 ml-11 line-clamp-2">
                      {watchlist.description}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
        <p>{watchlists.length} / 10 watchlists</p>
      </div>
    </aside>
  )
}
