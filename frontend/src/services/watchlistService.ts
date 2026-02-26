/**
 * Watchlist Service
 *
 * Provides CRUD operations for watchlist management.
 * Currently uses localStorage for persistence.
 * Can be easily migrated to backend API by implementing the same interface.
 */

import type {
  Watchlist,
  CreateWatchlistDto,
  UpdateWatchlistDto,
  AddStockDto,
  WatchlistStock,
  WatchlistError,
} from '@/types/watchlist'
import { stockService } from './stockService'

const STORAGE_KEY = 'screener_watchlists'
const MAX_WATCHLISTS = 10
const MAX_STOCKS_PER_WATCHLIST = 100

/**
 * Custom error class for watchlist operations
 */
class WatchlistServiceError extends Error {
  constructor(
    public code: WatchlistError['code'],
    message: string,
    public details?: Record<string, unknown>,
  ) {
    super(message)
    this.name = 'WatchlistServiceError'
  }
}

/**
 * Get all watchlists from localStorage
 */
function getStoredWatchlists(): Watchlist[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('Failed to parse watchlists from localStorage:', error)
    return []
  }
}

/**
 * Save watchlists to localStorage
 */
function saveWatchlists(watchlists: Watchlist[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(watchlists))
  } catch (error) {
    console.error('Failed to save watchlists to localStorage:', error)
    throw new WatchlistServiceError(
      'SERVER_ERROR',
      'Failed to save watchlists',
      {
        originalError: error,
      },
    )
  }
}

/**
 * Generate a unique ID for a watchlist
 */
function generateId(): string {
  return `wl_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Get current timestamp in ISO format
 */
function now(): string {
  return new Date().toISOString()
}

/**
 * Watchlist service with localStorage backend
 */
export const watchlistService = {
  /**
   * Get all watchlists for the current user
   */
  async getAll(): Promise<Watchlist[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100))
    return getStoredWatchlists()
  },

  /**
   * Get a single watchlist by ID
   */
  async getById(id: string): Promise<Watchlist> {
    await new Promise(resolve => setTimeout(resolve, 50))

    const watchlists = getStoredWatchlists()
    const watchlist = watchlists.find(w => w.id === id)

    if (!watchlist) {
      throw new WatchlistServiceError(
        'NOT_FOUND',
        `Watchlist with ID ${id} not found`,
      )
    }

    return watchlist
  },

  /**
   * Create a new watchlist
   */
  async create(data: CreateWatchlistDto): Promise<Watchlist> {
    await new Promise(resolve => setTimeout(resolve, 100))

    const watchlists = getStoredWatchlists()

    // Check limit
    if (watchlists.length >= MAX_WATCHLISTS) {
      throw new WatchlistServiceError(
        'LIMIT_EXCEEDED',
        `Maximum number of watchlists (${MAX_WATCHLISTS}) reached`,
        { limit: MAX_WATCHLISTS, current: watchlists.length },
      )
    }

    // Check for duplicate name
    if (
      watchlists.some(w => w.name.toLowerCase() === data.name.toLowerCase())
    ) {
      throw new WatchlistServiceError(
        'DUPLICATE',
        `Watchlist with name "${data.name}" already exists`,
      )
    }

    // Validate name
    if (!data.name.trim()) {
      throw new WatchlistServiceError(
        'INVALID_INPUT',
        'Watchlist name cannot be empty',
      )
    }

    if (data.name.length > 50) {
      throw new WatchlistServiceError(
        'INVALID_INPUT',
        'Watchlist name too long (max 50 characters)',
      )
    }

    const newWatchlist: Watchlist = {
      id: generateId(),
      name: data.name.trim(),
      description: data.description?.trim(),
      user_id: 'local_user', // TODO: Replace with actual user ID from auth
      stocks: [],
      created_at: now(),
      updated_at: now(),
      icon: data.icon,
      color: data.color,
    }

    watchlists.push(newWatchlist)
    saveWatchlists(watchlists)

    return newWatchlist
  },

  /**
   * Update an existing watchlist
   */
  async update(id: string, data: UpdateWatchlistDto): Promise<Watchlist> {
    await new Promise(resolve => setTimeout(resolve, 100))

    const watchlists = getStoredWatchlists()
    const index = watchlists.findIndex(w => w.id === id)

    if (index === -1) {
      throw new WatchlistServiceError(
        'NOT_FOUND',
        `Watchlist with ID ${id} not found`,
      )
    }

    // Check for duplicate name (excluding current watchlist)
    if (
      data.name &&
      watchlists.some(
        (w, i) =>
          i !== index && w.name.toLowerCase() === data.name?.toLowerCase(),
      )
    ) {
      throw new WatchlistServiceError(
        'DUPLICATE',
        `Watchlist with name "${data.name}" already exists`,
      )
    }

    // Validate name if provided
    if (data.name !== undefined) {
      if (!data.name.trim()) {
        throw new WatchlistServiceError(
          'INVALID_INPUT',
          'Watchlist name cannot be empty',
        )
      }
      if (data.name.length > 50) {
        throw new WatchlistServiceError(
          'INVALID_INPUT',
          'Watchlist name too long (max 50 characters)',
        )
      }
    }

    const updatedWatchlist: Watchlist = {
      ...watchlists[index],
      ...(data.name && { name: data.name.trim() }),
      ...(data.description !== undefined && {
        description: data.description?.trim(),
      }),
      ...(data.icon !== undefined && { icon: data.icon }),
      ...(data.color !== undefined && { color: data.color }),
      updated_at: now(),
    }

    watchlists[index] = updatedWatchlist
    saveWatchlists(watchlists)

    return updatedWatchlist
  },

  /**
   * Delete a watchlist
   */
  async delete(id: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 100))

    const watchlists = getStoredWatchlists()
    const index = watchlists.findIndex(w => w.id === id)

    if (index === -1) {
      throw new WatchlistServiceError(
        'NOT_FOUND',
        `Watchlist with ID ${id} not found`,
      )
    }

    watchlists.splice(index, 1)
    saveWatchlists(watchlists)
  },

  /**
   * Add a stock to a watchlist
   */
  async addStock(id: string, dto: AddStockDto): Promise<Watchlist> {
    await new Promise(resolve => setTimeout(resolve, 100))

    const watchlists = getStoredWatchlists()
    const index = watchlists.findIndex(w => w.id === id)

    if (index === -1) {
      throw new WatchlistServiceError(
        'NOT_FOUND',
        `Watchlist with ID ${id} not found`,
      )
    }

    const watchlist = watchlists[index]

    // Check stock limit
    if (watchlist.stocks.length >= MAX_STOCKS_PER_WATCHLIST) {
      throw new WatchlistServiceError(
        'LIMIT_EXCEEDED',
        `Maximum number of stocks (${MAX_STOCKS_PER_WATCHLIST}) reached for this watchlist`,
        { limit: MAX_STOCKS_PER_WATCHLIST, current: watchlist.stocks.length },
      )
    }

    // Check if stock already exists
    if (watchlist.stocks.some(s => s.code === dto.stock_code)) {
      throw new WatchlistServiceError(
        'DUPLICATE',
        `Stock ${dto.stock_code} already exists in this watchlist`,
      )
    }

    // Fetch stock details from stock service
    let stockData: WatchlistStock
    try {
      const stockDetail = await stockService.getStock(dto.stock_code)
      stockData = {
        code: stockDetail.code,
        name: stockDetail.name,
        market: (stockDetail.market as 'KOSPI' | 'KOSDAQ') || 'KOSPI',
        current_price: stockDetail.current_price ?? 0,
        change_percent: stockDetail.price_change_1d ?? 0,
        volume: stockDetail.current_volume ?? 0,
        added_at: now(),
        market_cap: stockDetail.market_cap ?? undefined,
      }
    } catch (error) {
      throw new WatchlistServiceError(
        'INVALID_INPUT',
        `Failed to fetch details for stock ${dto.stock_code}`,
        { stock_code: dto.stock_code, originalError: error },
      )
    }

    watchlist.stocks.push(stockData)
    watchlist.updated_at = now()
    watchlists[index] = watchlist
    saveWatchlists(watchlists)

    return watchlist
  },

  /**
   * Remove a stock from a watchlist
   */
  async removeStock(id: string, stockCode: string): Promise<Watchlist> {
    await new Promise(resolve => setTimeout(resolve, 100))

    const watchlists = getStoredWatchlists()
    const index = watchlists.findIndex(w => w.id === id)

    if (index === -1) {
      throw new WatchlistServiceError(
        'NOT_FOUND',
        `Watchlist with ID ${id} not found`,
      )
    }

    const watchlist = watchlists[index]
    const stockIndex = watchlist.stocks.findIndex(s => s.code === stockCode)

    if (stockIndex === -1) {
      throw new WatchlistServiceError(
        'NOT_FOUND',
        `Stock ${stockCode} not found in this watchlist`,
      )
    }

    watchlist.stocks.splice(stockIndex, 1)
    watchlist.updated_at = now()
    watchlists[index] = watchlist
    saveWatchlists(watchlists)

    return watchlist
  },

  /**
   * Update stock prices in all watchlists
   * This is called periodically to refresh stock data
   */
  async refreshStockPrices(): Promise<void> {
    const watchlists = getStoredWatchlists()
    const allStockCodes = [
      ...new Set(watchlists.flatMap(w => w.stocks.map(s => s.code))),
    ]

    if (allStockCodes.length === 0) {
      return
    }

    try {
      // Fetch fresh data for all stocks
      const stockUpdates = await Promise.all(
        allStockCodes.map(async code => {
          try {
            const stockDetail = await stockService.getStock(code)
            return {
              code,
              current_price: stockDetail.current_price ?? 0,
              change_percent: stockDetail.price_change_1d ?? 0,
              volume: stockDetail.current_volume ?? 0,
              market_cap: stockDetail.market_cap ?? undefined,
            }
          } catch (error) {
            console.warn(`Failed to refresh stock ${code}:`, error)
            return null
          }
        }),
      )

      // Update watchlists with fresh data
      const stockMap = new Map(
        stockUpdates
          .filter((s): s is NonNullable<typeof s> => s !== null)
          .map(s => [s.code, s]),
      )

      watchlists.forEach(watchlist => {
        watchlist.stocks.forEach(stock => {
          const update = stockMap.get(stock.code)
          if (update) {
            stock.current_price = update.current_price
            stock.change_percent = update.change_percent
            stock.volume = update.volume
            if (update.market_cap) {
              stock.market_cap = update.market_cap
            }
          }
        })
        watchlist.updated_at = now()
      })

      saveWatchlists(watchlists)
    } catch (error) {
      console.error('Failed to refresh stock prices:', error)
      throw new WatchlistServiceError(
        'SERVER_ERROR',
        'Failed to refresh stock prices',
        {
          originalError: error,
        },
      )
    }
  },
}
