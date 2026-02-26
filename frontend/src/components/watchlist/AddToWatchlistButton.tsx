/**
 * AddToWatchlistButton Component (FE-008 Phase 5)
 * Quick add/remove stocks to/from watchlists
 */

import { useState, useEffect } from 'react'
import { Star, Check, Plus } from 'lucide-react'
import { useWatchlistStore, watchlistSelectors } from '@/store/watchlistStore'
import { WatchlistDialog } from './WatchlistDialog'

interface AddToWatchlistButtonProps {
  stock: {
    code: string
    name: string
    market: 'KOSPI' | 'KOSDAQ'
    current_price?: number
    change_percent?: number
    volume?: number
  }
  variant?: 'icon' | 'button'
  size?: 'sm' | 'md' | 'lg'
}

export function AddToWatchlistButton({
  stock,
  variant = 'button',
  size = 'md',
}: AddToWatchlistButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const {
    watchlists,
    fetchWatchlists,
    addStockToWatchlist,
    removeStockFromWatchlist,
    getWatchlistsContainingStock,
  } = useWatchlistStore()

  const isAtLimit = useWatchlistStore(watchlistSelectors.selectIsAtLimit)
  const watchlistsWithStock = getWatchlistsContainingStock(stock.code)
  const isInAnyWatchlist = watchlistsWithStock.length > 0

  // Fetch watchlists on mount
  useEffect(() => {
    fetchWatchlists()
  }, [fetchWatchlists])

  // Handle toggle watchlist
  const handleToggleWatchlist = async (watchlistId: string) => {
    const isInWatchlist = watchlistsWithStock.some(w => w.id === watchlistId)

    if (isInWatchlist) {
      await removeStockFromWatchlist(watchlistId, stock.code)
    } else {
      const watchlist = watchlists.find(w => w.id === watchlistId)
      if (watchlist && watchlist.stocks.length >= 100) {
        alert('Watchlist is full (100 stocks maximum)')
        return
      }

      await addStockToWatchlist(watchlistId, {
        stock_code: stock.code,
      })
    }
  }

  // Handle create new watchlist
  const handleCreateWatchlist = () => {
    setIsOpen(false)
    setIsDialogOpen(true)
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!isOpen) return

    const handleClickOutside = () => setIsOpen(false)
    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [isOpen])

  // Size classes
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  }

  const iconSizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  }

  if (variant === 'icon') {
    return (
      <div className="relative">
        <button
          onClick={e => {
            e.preventDefault()
            e.stopPropagation()
            setIsOpen(!isOpen)
          }}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          className={`
            p-1.5 rounded-full
            ${
              isInAnyWatchlist
                ? 'text-yellow-500 hover:text-yellow-600 bg-yellow-50 hover:bg-yellow-100'
                : 'text-gray-400 hover:text-yellow-500 hover:bg-yellow-50'
            }
            transition-colors
          `}
          title={
            isInAnyWatchlist
              ? `In ${watchlistsWithStock.length} watchlist(s)`
              : 'Add to watchlist'
          }
        >
          <Star
            className={`${iconSizeClasses[size]} ${isInAnyWatchlist || isHovered ? 'fill-current' : ''}`}
          />
        </button>

        {/* Dropdown */}
        {isOpen && (
          <div
            className="
              absolute right-0 top-full mt-2 z-50
              w-64 bg-white rounded-lg shadow-lg border border-gray-200
              py-2
            "
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="px-4 py-2 border-b border-gray-200">
              <p className="font-medium text-gray-900">Add to Watchlist</p>
              <p className="text-xs text-gray-500 mt-0.5">
                {stock.code} - {stock.name}
              </p>
            </div>

            {/* Watchlist items */}
            <div className="max-h-64 overflow-y-auto">
              {watchlists.length === 0 ? (
                <div className="px-4 py-6 text-center text-gray-500 text-sm">
                  No watchlists yet
                </div>
              ) : (
                watchlists.map(watchlist => {
                  const isInWatchlist = watchlistsWithStock.some(
                    w => w.id === watchlist.id,
                  )
                  const isFull = watchlist.stocks.length >= 100

                  return (
                    <button
                      key={watchlist.id}
                      onClick={() => handleToggleWatchlist(watchlist.id)}
                      disabled={!isInWatchlist && isFull}
                      className="
                        w-full px-4 py-2.5
                        flex items-center justify-between
                        hover:bg-gray-50
                        disabled:opacity-50 disabled:cursor-not-allowed
                        transition-colors
                      "
                    >
                      <div className="flex items-center gap-2 flex-1">
                        <span className="text-lg">
                          {watchlist.icon || '📋'}
                        </span>
                        <div className="text-left">
                          <p className="text-sm font-medium text-gray-900">
                            {watchlist.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {watchlist.stocks.length}/100 stocks
                            {isFull && ' (Full)'}
                          </p>
                        </div>
                      </div>
                      {isInWatchlist && (
                        <Check className="w-4 h-4 text-green-600 flex-shrink-0" />
                      )}
                    </button>
                  )
                })
              )}
            </div>

            {/* Footer */}
            <div className="px-4 py-2 border-t border-gray-200">
              <button
                onClick={handleCreateWatchlist}
                disabled={isAtLimit}
                className="
                  w-full px-3 py-2 rounded
                  text-sm font-medium
                  bg-blue-50 text-blue-600
                  hover:bg-blue-100
                  disabled:opacity-50 disabled:cursor-not-allowed
                  flex items-center justify-center gap-2
                  transition-colors
                "
              >
                <Plus className="w-4 h-4" />
                New Watchlist {isAtLimit && '(Max 10)'}
              </button>
            </div>
          </div>
        )}

        {/* Create Watchlist Dialog */}
        <WatchlistDialog
          isOpen={isDialogOpen}
          onClose={() => setIsDialogOpen(false)}
          onSave={async () => {
            // Dialog will handle creation, just close it
            setIsDialogOpen(false)
            // Refresh watchlists
            await fetchWatchlists()
          }}
        />
      </div>
    )
  }

  // Button variant
  return (
    <div className="relative">
      <button
        onClick={e => {
          e.preventDefault()
          e.stopPropagation()
          setIsOpen(!isOpen)
        }}
        className={`
          ${sizeClasses[size]}
          rounded-lg font-medium
          flex items-center gap-2
          ${
            isInAnyWatchlist
              ? 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100 border border-yellow-200'
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
          }
          transition-colors
        `}
      >
        <Star
          className={`${iconSizeClasses[size]} ${isInAnyWatchlist ? 'fill-current' : ''}`}
        />
        {isInAnyWatchlist
          ? `In ${watchlistsWithStock.length} list(s)`
          : 'Add to Watchlist'}
      </button>

      {/* Dropdown - same as icon variant */}
      {isOpen && (
        <div
          className="
            absolute left-0 top-full mt-2 z-50
            w-64 bg-white rounded-lg shadow-lg border border-gray-200
            py-2
          "
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-4 py-2 border-b border-gray-200">
            <p className="font-medium text-gray-900">Add to Watchlist</p>
            <p className="text-xs text-gray-500 mt-0.5">
              {stock.code} - {stock.name}
            </p>
          </div>

          {/* Watchlist items */}
          <div className="max-h-64 overflow-y-auto">
            {watchlists.length === 0 ? (
              <div className="px-4 py-6 text-center text-gray-500 text-sm">
                No watchlists yet
              </div>
            ) : (
              watchlists.map(watchlist => {
                const isInWatchlist = watchlistsWithStock.some(
                  w => w.id === watchlist.id,
                )
                const isFull = watchlist.stocks.length >= 100

                return (
                  <button
                    key={watchlist.id}
                    onClick={() => handleToggleWatchlist(watchlist.id)}
                    disabled={!isInWatchlist && isFull}
                    className="
                      w-full px-4 py-2.5
                      flex items-center justify-between
                      hover:bg-gray-50
                      disabled:opacity-50 disabled:cursor-not-allowed
                      transition-colors
                    "
                  >
                    <div className="flex items-center gap-2 flex-1">
                      <span className="text-lg">{watchlist.icon || '📋'}</span>
                      <div className="text-left">
                        <p className="text-sm font-medium text-gray-900">
                          {watchlist.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {watchlist.stocks.length}/100 stocks
                          {isFull && ' (Full)'}
                        </p>
                      </div>
                    </div>
                    {isInWatchlist && (
                      <Check className="w-4 h-4 text-green-600 flex-shrink-0" />
                    )}
                  </button>
                )
              })
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 border-t border-gray-200">
            <button
              onClick={handleCreateWatchlist}
              disabled={isAtLimit}
              className="
                w-full px-3 py-2 rounded
                text-sm font-medium
                bg-blue-50 text-blue-600
                hover:bg-blue-100
                disabled:opacity-50 disabled:cursor-not-allowed
                flex items-center justify-center gap-2
                transition-colors
              "
            >
              <Plus className="w-4 h-4" />
              New Watchlist {isAtLimit && '(Max 10)'}
            </button>
          </div>
        </div>
      )}

      {/* Create Watchlist Dialog */}
      <WatchlistDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onSave={async () => {
          setIsDialogOpen(false)
          await fetchWatchlists()
        }}
      />
    </div>
  )
}
