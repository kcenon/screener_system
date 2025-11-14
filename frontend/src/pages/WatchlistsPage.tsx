/**
 * WatchlistsPage Component
 * Main page for managing watchlists and tracking favorite stocks
 */

import { useEffect, useState } from 'react'
import { Star, RefreshCw, AlertCircle } from 'lucide-react'
import { useWatchlistStore, watchlistSelectors } from '@/store/watchlistStore'
import { WatchlistSidebar } from '@/components/watchlist/WatchlistSidebar'
import { WatchlistStockTable } from '@/components/watchlist/WatchlistStockTable'
import { WatchlistDialog } from '@/components/watchlist/WatchlistDialog'
import type { Watchlist } from '@/types/watchlist'

export default function WatchlistsPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingWatchlist, setEditingWatchlist] = useState<Watchlist | undefined>()
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Zustand store
  const {
    watchlists,
    activeWatchlistId,
    isLoading,
    error,
    fetchWatchlists,
    createWatchlist,
    updateWatchlist,
    deleteWatchlist,
    setActiveWatchlist,
    removeStockFromWatchlist,
    refreshStockPrices,
    clearError,
  } = useWatchlistStore()

  const activeWatchlist = useWatchlistStore(watchlistSelectors.selectActiveWatchlist)

  // Fetch watchlists on mount
  useEffect(() => {
    fetchWatchlists()
  }, [fetchWatchlists])

  // Auto-select first watchlist if none selected
  useEffect(() => {
    if (!activeWatchlistId && watchlists.length > 0) {
      setActiveWatchlist(watchlists[0].id)
    }
  }, [watchlists, activeWatchlistId, setActiveWatchlist])

  // Handle create new watchlist
  const handleCreateWatchlist = () => {
    setEditingWatchlist(undefined)
    setIsDialogOpen(true)
  }

  // Handle edit watchlist
  const handleEditWatchlist = (watchlist: Watchlist) => {
    setEditingWatchlist(watchlist)
    setIsDialogOpen(true)
  }

  // Handle save watchlist (create or update)
  const handleSaveWatchlist = async (data: { name: string; description?: string }) => {
    if (editingWatchlist) {
      // Update existing
      await updateWatchlist(editingWatchlist.id, data)
    } else {
      // Create new
      await createWatchlist(data)
    }
  }

  // Handle delete watchlist
  const handleDeleteWatchlist = async (id: string) => {
    await deleteWatchlist(id)
  }

  // Handle remove stock from active watchlist
  const handleRemoveStock = async (stockCode: string) => {
    if (!activeWatchlistId) return
    await removeStockFromWatchlist(activeWatchlistId, stockCode)
  }

  // Handle refresh stock prices
  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      await refreshStockPrices()
    } finally {
      setIsRefreshing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Star className="w-8 h-8 text-yellow-500 fill-yellow-500" />
                My Watchlists
              </h1>
              <p className="mt-2 text-gray-600">
                Track and monitor your favorite stocks
              </p>
            </div>

            {activeWatchlist && (
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="
                  px-4 py-2 rounded-lg
                  text-gray-700 bg-white border border-gray-300
                  hover:bg-gray-50
                  disabled:opacity-50 disabled:cursor-not-allowed
                  flex items-center gap-2
                "
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                Refresh Prices
              </button>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <button
                onClick={clearError}
                className="text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Dismiss
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Sidebar */}
        <WatchlistSidebar
          watchlists={watchlists}
          activeWatchlistId={activeWatchlistId}
          onSelectWatchlist={setActiveWatchlist}
          onCreateWatchlist={handleCreateWatchlist}
          onEditWatchlist={handleEditWatchlist}
          onDeleteWatchlist={handleDeleteWatchlist}
          isLoading={isLoading}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-hidden">
          {activeWatchlist ? (
            <div className="h-full flex flex-col">
              {/* Watchlist Header */}
              <div className="px-6 py-4 bg-white border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{activeWatchlist.icon || '📋'}</span>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      {activeWatchlist.name}
                    </h2>
                    {activeWatchlist.description && (
                      <p className="text-sm text-gray-500 mt-1">
                        {activeWatchlist.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Stock Table */}
              <div className="flex-1 overflow-hidden">
                <WatchlistStockTable
                  stocks={activeWatchlist.stocks}
                  onRemoveStock={handleRemoveStock}
                  isLoading={false}
                />
              </div>
            </div>
          ) : (
            // No watchlist selected
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <Star className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {watchlists.length === 0
                    ? 'No watchlists yet'
                    : 'Select a watchlist'}
                </h3>
                <p className="text-gray-500 mb-6">
                  {watchlists.length === 0
                    ? 'Create your first watchlist to get started'
                    : 'Choose a watchlist from the sidebar to view stocks'}
                </p>
                {watchlists.length === 0 && (
                  <button
                    onClick={handleCreateWatchlist}
                    className="
                      px-6 py-3 rounded-lg
                      bg-blue-600 text-white
                      hover:bg-blue-700
                      font-medium
                    "
                  >
                    Create Your First Watchlist
                  </button>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Watchlist Dialog */}
      <WatchlistDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onSave={handleSaveWatchlist}
        watchlist={editingWatchlist}
      />
    </div>
  )
}
