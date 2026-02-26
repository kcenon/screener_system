/**
 * Portfolio Service - API client for portfolio management
 *
 * Provides TypeScript interfaces and API methods for:
 * - Portfolio CRUD operations
 * - Holdings management
 * - Transaction recording
 * - Performance metrics
 * - Allocation analysis
 *
 * @module services/portfolioService
 * @category Services
 */

import { api } from './api'

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Transaction type enumeration
 */
export enum TransactionType {
  BUY = 'BUY',
  SELL = 'SELL',
}

// ============================================================================
// PORTFOLIO TYPES
// ============================================================================

/**
 * Portfolio entity from backend
 */
export interface Portfolio {
  id: number
  user_id: number
  name: string
  description: string | null
  is_default: boolean
  holding_count: number
  total_cost: string // Decimal as string
  total_value?: string | null
  unrealized_gain?: string | null
  return_percent?: string | null
  day_change?: string | null
  day_change_percent?: string | null
  created_at: string // ISO datetime
  updated_at: string // ISO datetime
}

/**
 * Portfolio creation request
 */
export interface PortfolioCreate {
  name: string
  description?: string | null
  is_default?: boolean
}

/**
 * Portfolio update request
 */
export interface PortfolioUpdate {
  name?: string
  description?: string | null
  is_default?: boolean
}

/**
 * Paginated portfolio list response
 */
export interface PortfolioListResponse {
  items: Portfolio[]
  total: number
  skip: number
  limit: number
}

// ============================================================================
// HOLDING TYPES
// ============================================================================

/**
 * Holding entity (stock position in portfolio)
 */
export interface Holding {
  id: number
  portfolio_id: number
  stock_symbol: string // 6-digit code (e.g., "005930")
  stock_name?: string | null
  sector?: string | null
  shares: string // Decimal as string
  average_cost: string // Decimal as string
  current_price?: string | null
  current_value?: string | null
  total_cost?: string | null
  unrealized_gain?: string | null
  unrealized_gain_percent?: string | null
  weight_percent?: string | null
  first_purchase_date?: string | null // ISO date
  last_update_date: string // ISO datetime
}

/**
 * Holding creation request
 */
export interface HoldingCreate {
  stock_symbol: string
  shares: number | string
  average_cost: number | string
  first_purchase_date?: string | null
}

/**
 * Holding update request
 */
export interface HoldingUpdate {
  shares?: number | string
  average_cost?: number | string
}

/**
 * Holdings list response
 */
export interface HoldingListResponse {
  items: Holding[]
  total: number
}

// ============================================================================
// TRANSACTION TYPES
// ============================================================================

/**
 * Transaction entity (buy/sell record)
 */
export interface Transaction {
  id: number
  portfolio_id: number
  stock_symbol: string
  transaction_type: TransactionType
  shares: string // Decimal as string
  price: string // Decimal as string
  commission: string // Decimal as string
  total_amount: string // Decimal as string
  transaction_date: string // ISO datetime
  notes: string | null
}

/**
 * Transaction creation request
 */
export interface TransactionCreate {
  stock_symbol: string
  transaction_type: TransactionType
  shares: number | string
  price: number | string
  commission?: number | string
  transaction_date?: string // ISO datetime
  notes?: string | null
}

/**
 * Transactions list response
 */
export interface TransactionListResponse {
  items: Transaction[]
  total: number
  skip: number
  limit: number
}

// ============================================================================
// PERFORMANCE & ALLOCATION TYPES
// ============================================================================

/**
 * Portfolio performance metrics
 */
export interface PerformanceMetrics {
  total_value: string // Decimal as string
  total_cost: string
  total_gain: string
  total_return_percent: string
  day_change: string
  day_change_percent: string
  holding_count: number
  realized_gain?: string | null
  unrealized_gain?: string | null
}

/**
 * Single allocation item (stock or sector)
 */
export interface AllocationItem {
  label: string // Stock symbol or sector name
  value: string // Decimal as string
  weight_percent: string // Percentage as string
  gain: string // Decimal as string
  gain_percent: string // Percentage as string
}

/**
 * Portfolio allocation breakdown
 */
export interface PortfolioAllocation {
  by_stock: AllocationItem[]
  by_sector: AllocationItem[]
  total_value: string
}

// ============================================================================
// API SERVICE
// ============================================================================

/**
 * Portfolio Service - API client for all portfolio operations
 *
 * @example
 * Basic usage:
 * ```typescript
 * import { portfolioService } from '@/services/portfolioService';
 *
 * // List all portfolios
 * const { data } = await portfolioService.list();
 * console.log(data.items);
 *
 * // Create new portfolio
 * const portfolio = await portfolioService.create({
 *   name: "My Portfolio",
 *   description: "Long-term holdings"
 * });
 * ```
 */
export const portfolioService = {
  // ============================================================================
  // Portfolio CRUD Operations
  // ============================================================================

  /**
   * List all portfolios for the current user
   *
   * @param skip - Number of items to skip for pagination
   * @param limit - Maximum number of items to return (1-100)
   * @returns Paginated list of portfolios
   */
  list: (skip: number = 0, limit: number = 10) => {
    return api.get<PortfolioListResponse>('/api/v1/portfolios', {
      params: { skip, limit },
    })
  },

  /**
   * Create a new portfolio
   *
   * @param data - Portfolio creation data
   * @returns Created portfolio
   */
  create: (data: PortfolioCreate) => {
    return api.post<Portfolio>('/api/v1/portfolios', data)
  },

  /**
   * Get single portfolio details
   *
   * @param id - Portfolio ID
   * @returns Portfolio details
   */
  get: (id: number) => {
    return api.get<Portfolio>(`/api/v1/portfolios/${id}`)
  },

  /**
   * Update portfolio information
   *
   * @param id - Portfolio ID
   * @param data - Fields to update
   * @returns Updated portfolio
   */
  update: (id: number, data: PortfolioUpdate) => {
    return api.put<Portfolio>(`/api/v1/portfolios/${id}`, data)
  },

  /**
   * Delete a portfolio
   *
   * @param id - Portfolio ID
   */
  delete: (id: number) => {
    return api.delete(`/api/v1/portfolios/${id}`)
  },

  /**
   * Get portfolio performance metrics
   *
   * @param id - Portfolio ID
   * @returns Performance metrics (value, gain, return %)
   */
  getPerformance: (id: number) => {
    return api.get<PerformanceMetrics>(`/api/v1/portfolios/${id}/performance`)
  },

  /**
   * Get portfolio allocation breakdown
   *
   * @param id - Portfolio ID
   * @returns Allocation by stock and sector
   */
  getAllocation: (id: number) => {
    return api.get<PortfolioAllocation>(`/api/v1/portfolios/${id}/allocation`)
  },

  // ============================================================================
  // Holdings Management
  // ============================================================================

  /**
   * List all holdings in a portfolio
   *
   * @param portfolioId - Portfolio ID
   * @returns List of holdings with current values
   */
  getHoldings: (portfolioId: number) => {
    return api.get<HoldingListResponse>(
      `/api/v1/portfolios/${portfolioId}/holdings`,
    )
  },

  /**
   * Add a new holding to portfolio (manual entry)
   *
   * @param portfolioId - Portfolio ID
   * @param data - Holding data (symbol, shares, average cost)
   * @returns Created holding
   */
  addHolding: (portfolioId: number, data: HoldingCreate) => {
    return api.post<Holding>(`/api/v1/portfolios/${portfolioId}/holdings`, data)
  },

  /**
   * Update an existing holding
   *
   * @param portfolioId - Portfolio ID
   * @param holdingId - Holding ID
   * @param data - Fields to update
   * @returns Updated holding
   */
  updateHolding: (
    portfolioId: number,
    holdingId: number,
    data: HoldingUpdate,
  ) => {
    return api.put<Holding>(
      `/api/v1/portfolios/${portfolioId}/holdings/${holdingId}`,
      data,
    )
  },

  /**
   * Remove a holding from portfolio
   *
   * @param portfolioId - Portfolio ID
   * @param holdingId - Holding ID
   */
  deleteHolding: (portfolioId: number, holdingId: number) => {
    return api.delete(`/api/v1/portfolios/${portfolioId}/holdings/${holdingId}`)
  },

  // ============================================================================
  // Transaction Management
  // ============================================================================

  /**
   * List all transactions for a portfolio
   *
   * @param portfolioId - Portfolio ID
   * @param skip - Number of items to skip
   * @param limit - Maximum items to return
   * @returns Paginated transaction history
   */
  getTransactions: (
    portfolioId: number,
    skip: number = 0,
    limit: number = 50,
  ) => {
    return api.get<TransactionListResponse>(
      `/api/v1/portfolios/${portfolioId}/transactions`,
      {
        params: { skip, limit },
      },
    )
  },

  /**
   * Record a new transaction (buy or sell)
   *
   * Automatically updates holdings and average cost.
   *
   * @param portfolioId - Portfolio ID
   * @param data - Transaction data
   * @returns Created transaction
   */
  addTransaction: (portfolioId: number, data: TransactionCreate) => {
    return api.post<Transaction>(
      `/api/v1/portfolios/${portfolioId}/transactions`,
      data,
    )
  },

  /**
   * Delete a transaction
   *
   * Note: This may require manual holding adjustment if the
   * transaction was previously applied to holdings.
   *
   * @param portfolioId - Portfolio ID
   * @param transactionId - Transaction ID
   */
  deleteTransaction: (portfolioId: number, transactionId: number) => {
    return api.delete(
      `/api/v1/portfolios/${portfolioId}/transactions/${transactionId}`,
    )
  },
}

export default portfolioService
