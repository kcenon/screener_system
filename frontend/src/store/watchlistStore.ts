/**
 * Watchlist Store (Zustand)
 *
 * Global state management for watchlists with optimistic updates.
 * Provides actions for CRUD operations and syncs with localStorage via service layer.
 */

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import type {
  Watchlist,
  CreateWatchlistDto,
  UpdateWatchlistDto,
  AddStockDto,
} from '@/types/watchlist'
import { watchlistService } from '@/services/watchlistService'

interface WatchlistState {
  // State
  watchlists: Watchlist[]
  activeWatchlistId: string | null
  isLoading: boolean
  error: string | null

  // Actions - Fetching
  fetchWatchlists: () => Promise<void>
  fetchWatchlist: (id: string) => Promise<Watchlist | null>

  // Actions - Watchlist CRUD
  createWatchlist: (data: CreateWatchlistDto) => Promise<Watchlist | null>
  updateWatchlist: (id: string, data: UpdateWatchlistDto) => Promise<Watchlist | null>
  deleteWatchlist: (id: string) => Promise<boolean>

  // Actions - Stock management
  addStockToWatchlist: (watchlistId: string, dto: AddStockDto) => Promise<boolean>
  removeStockFromWatchlist: (watchlistId: string, stockCode: string) => Promise<boolean>

  // Actions - UI state
  setActiveWatchlist: (id: string | null) => void
  clearError: () => void

  // Actions - Utilities
  refreshStockPrices: () => Promise<void>
  getWatchlistById: (id: string) => Watchlist | undefined
  isStockInWatchlist: (watchlistId: string, stockCode: string) => boolean
  getWatchlistsContainingStock: (stockCode: string) => Watchlist[]
}

export const useWatchlistStore = create<WatchlistState>()(
  devtools(
    (set, get) => ({
      // Initial state
      watchlists: [],
      activeWatchlistId: null,
      isLoading: false,
      error: null,

      // Fetch all watchlists
      fetchWatchlists: async () => {
        set({ isLoading: true, error: null })
        try {
          const watchlists = await watchlistService.getAll()
          set({ watchlists, isLoading: false })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch watchlists'
          set({ error: errorMessage, isLoading: false })
        }
      },

      // Fetch single watchlist
      fetchWatchlist: async (id: string) => {
        try {
          const watchlist = await watchlistService.getById(id)
          // Update in store if exists
          set((state) => ({
            watchlists: state.watchlists.map((w) => (w.id === id ? watchlist : w)),
          }))
          return watchlist
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch watchlist'
          set({ error: errorMessage })
          return null
        }
      },

      // Create new watchlist
      createWatchlist: async (data: CreateWatchlistDto) => {
        set({ isLoading: true, error: null })
        try {
          const newWatchlist = await watchlistService.create(data)
          set((state) => ({
            watchlists: [...state.watchlists, newWatchlist],
            activeWatchlistId: newWatchlist.id,
            isLoading: false,
          }))
          return newWatchlist
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to create watchlist'
          set({ error: errorMessage, isLoading: false })
          return null
        }
      },

      // Update watchlist
      updateWatchlist: async (id: string, data: UpdateWatchlistDto) => {
        set({ error: null })
        try {
          const updatedWatchlist = await watchlistService.update(id, data)
          set((state) => ({
            watchlists: state.watchlists.map((w) => (w.id === id ? updatedWatchlist : w)),
          }))
          return updatedWatchlist
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to update watchlist'
          set({ error: errorMessage })
          return null
        }
      },

      // Delete watchlist
      deleteWatchlist: async (id: string) => {
        set({ error: null })
        try {
          await watchlistService.delete(id)
          set((state) => ({
            watchlists: state.watchlists.filter((w) => w.id !== id),
            activeWatchlistId: state.activeWatchlistId === id ? null : state.activeWatchlistId,
          }))
          return true
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to delete watchlist'
          set({ error: errorMessage })
          return false
        }
      },

      // Add stock to watchlist with optimistic update
      addStockToWatchlist: async (watchlistId: string, dto: AddStockDto) => {
        set({ error: null })

        // Optimistic update: Add placeholder stock
        const tempStockCode = dto.stock_code
        set((state) => ({
          watchlists: state.watchlists.map((w) => {
            if (w.id === watchlistId && !w.stocks.some((s) => s.code === tempStockCode)) {
              return {
                ...w,
                stocks: [
                  ...w.stocks,
                  {
                    code: tempStockCode,
                    name: 'Loading...',
                    market: 'KOSPI' as const,
                    current_price: 0,
                    change_percent: 0,
                    volume: 0,
                    added_at: new Date().toISOString(),
                  },
                ],
              }
            }
            return w
          }),
        }))

        try {
          const updatedWatchlist = await watchlistService.addStock(watchlistId, dto)
          set((state) => ({
            watchlists: state.watchlists.map((w) =>
              w.id === watchlistId ? updatedWatchlist : w
            ),
          }))
          return true
        } catch (error) {
          // Rollback optimistic update
          set((state) => ({
            watchlists: state.watchlists.map((w) => {
              if (w.id === watchlistId) {
                return {
                  ...w,
                  stocks: w.stocks.filter((s) => s.code !== tempStockCode || s.name !== 'Loading...'),
                }
              }
              return w
            }),
          }))

          const errorMessage = error instanceof Error ? error.message : 'Failed to add stock'
          set({ error: errorMessage })
          return false
        }
      },

      // Remove stock from watchlist with optimistic update
      removeStockFromWatchlist: async (watchlistId: string, stockCode: string) => {
        set({ error: null })

        // Store original state for rollback
        const originalWatchlists = get().watchlists
        const targetWatchlist = originalWatchlists.find((w) => w.id === watchlistId)

        if (!targetWatchlist) {
          set({ error: 'Watchlist not found' })
          return false
        }

        // Optimistic update: Remove stock
        set((state) => ({
          watchlists: state.watchlists.map((w) => {
            if (w.id === watchlistId) {
              return {
                ...w,
                stocks: w.stocks.filter((s) => s.code !== stockCode),
              }
            }
            return w
          }),
        }))

        try {
          await watchlistService.removeStock(watchlistId, stockCode)
          return true
        } catch (error) {
          // Rollback optimistic update
          set({ watchlists: originalWatchlists })

          const errorMessage = error instanceof Error ? error.message : 'Failed to remove stock'
          set({ error: errorMessage })
          return false
        }
      },

      // Set active watchlist
      setActiveWatchlist: (id: string | null) => {
        set({ activeWatchlistId: id })
      },

      // Clear error
      clearError: () => {
        set({ error: null })
      },

      // Refresh stock prices in all watchlists
      refreshStockPrices: async () => {
        try {
          await watchlistService.refreshStockPrices()
          // Re-fetch all watchlists to get updated prices
          const watchlists = await watchlistService.getAll()
          set({ watchlists })
        } catch (error) {
          console.error('Failed to refresh stock prices:', error)
          // Don't set error state for background refresh failures
        }
      },

      // Get watchlist by ID (from current state)
      getWatchlistById: (id: string) => {
        return get().watchlists.find((w) => w.id === id)
      },

      // Check if stock is in a specific watchlist
      isStockInWatchlist: (watchlistId: string, stockCode: string) => {
        const watchlist = get().watchlists.find((w) => w.id === watchlistId)
        return watchlist?.stocks.some((s) => s.code === stockCode) ?? false
      },

      // Get all watchlists containing a specific stock
      getWatchlistsContainingStock: (stockCode: string) => {
        return get().watchlists.filter((w) => w.stocks.some((s) => s.code === stockCode))
      },
    }),
    { name: 'WatchlistStore' }
  )
)

/**
 * Selectors for common use cases
 */
export const watchlistSelectors = {
  /** Get the active watchlist */
  selectActiveWatchlist: (state: WatchlistState) => {
    if (!state.activeWatchlistId) return null
    return state.watchlists.find((w) => w.id === state.activeWatchlistId) || null
  },

  /** Get total number of watchlists */
  selectWatchlistCount: (state: WatchlistState) => state.watchlists.length,

  /** Check if at watchlist limit */
  selectIsAtLimit: (state: WatchlistState) => state.watchlists.length >= 10,

  /** Get watchlists sorted by name */
  selectWatchlistsSorted: (state: WatchlistState) =>
    [...state.watchlists].sort((a, b) => a.name.localeCompare(b.name)),

  /** Get watchlists sorted by update time (most recent first) */
  selectWatchlistsByRecent: (state: WatchlistState) =>
    [...state.watchlists].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    ),
}
