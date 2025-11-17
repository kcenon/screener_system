/**
 * Portfolio List Hook.
 *
 * Manages portfolio list with CRUD operations using React Query.
 * Provides automatic caching, background refetching, and mutation handling.
 *
 * @module hooks/usePortfolios
 * @category Hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { portfolioService } from '../services/portfolioService'
import type { PortfolioCreate, PortfolioUpdate } from '../services/portfolioService'

/**
 * Query key for portfolios list.
 *
 * Used for React Query caching and invalidation.
 */
export const PORTFOLIOS_QUERY_KEY = ['portfolios'] as const

/**
 * Hook for managing user's portfolio list.
 *
 * Provides:
 * - Portfolio list fetching with pagination
 * - Create, update, delete operations
 * - Automatic cache invalidation
 * - Loading and error states
 *
 * ## Query Caching
 *
 * - Stale Time: 2 minutes (data considered fresh)
 * - Cache Time: 5 minutes (unused data kept in cache)
 * - Auto refetch: On window focus and mount
 *
 * @example
 * Basic usage:
 * ```typescript
 * const {
 *   portfolios,
 *   isLoading,
 *   createPortfolio,
 *   deletePortfolio
 * } = usePortfolios();
 *
 * // Create new portfolio
 * await createPortfolio.mutateAsync({
 *   name: "Tech Stocks",
 *   description: "High-growth tech companies"
 * });
 * ```
 *
 * @param skip - Number of items to skip for pagination (default: 0)
 * @param limit - Maximum number of items to return (default: 100)
 * @returns Portfolio list operations and state
 */
export function usePortfolios(skip: number = 0, limit: number = 100) {
  const queryClient = useQueryClient()

  // Fetch portfolios list
  const query = useQuery({
    queryKey: [...PORTFOLIOS_QUERY_KEY, skip, limit],
    queryFn: async () => {
      const response = await portfolioService.list(skip, limit)
      return response.data
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
  })

  // Create portfolio mutation
  const createPortfolio = useMutation({
    mutationFn: async (data: PortfolioCreate) => {
      const response = await portfolioService.create(data)
      return response.data
    },
    onSuccess: () => {
      // Invalidate and refetch portfolios list
      queryClient.invalidateQueries({ queryKey: PORTFOLIOS_QUERY_KEY })
    },
  })

  // Update portfolio mutation
  const updatePortfolio = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: PortfolioUpdate }) => {
      const response = await portfolioService.update(id, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      // Invalidate both list and detail queries
      queryClient.invalidateQueries({ queryKey: PORTFOLIOS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: ['portfolio', variables.id] })
    },
  })

  // Delete portfolio mutation
  const deletePortfolio = useMutation({
    mutationFn: async (id: number) => {
      await portfolioService.delete(id)
      return id
    },
    onSuccess: () => {
      // Invalidate portfolios list
      queryClient.invalidateQueries({ queryKey: PORTFOLIOS_QUERY_KEY })
    },
  })

  return {
    // Query data
    portfolios: query.data?.items || [],
    total: query.data?.total || 0,

    // Query state
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,

    // Mutations
    createPortfolio,
    updatePortfolio,
    deletePortfolio,

    // Refetch function
    refetch: query.refetch,
  }
}

export default usePortfolios
