/**
 * Portfolio Detail Hook.
 *
 * Manages single portfolio details with holdings.
 * Provides automatic caching and background refetching.
 *
 * @module hooks/usePortfolioDetail
 * @category Hooks
 */

import { useQuery, useQueryClient } from '@tanstack/react-query'
import { portfolioService } from '../services/portfolioService'

/**
 * Query key factory for portfolio details.
 *
 * @param id - Portfolio ID
 * @returns Query key array
 */
export const portfolioDetailQueryKey = (id: number) =>
  ['portfolio', id] as const

/**
 * Hook for fetching single portfolio details with holdings.
 *
 * Provides:
 * - Portfolio information
 * - Holdings list with current prices
 * - Automatic background updates
 * - Error handling
 *
 * ## Query Caching
 *
 * - Stale Time: 1 minute (data considered fresh)
 * - Cache Time: 5 minutes (unused data kept in cache)
 * - Refetch Interval: 30 seconds (for price updates)
 *
 * @example
 * Basic usage:
 * ```typescript
 * const { portfolio, holdings, isLoading } = usePortfolioDetail(portfolioId);
 *
 * if (isLoading) return <Spinner />;
 *
 * return (
 *   <div>
 *     <h1>{portfolio?.name}</h1>
 *     <p>Holdings: {holdings.length}</p>
 *   </div>
 * );
 * ```
 *
 * @param portfolioId - Portfolio ID to fetch (undefined to skip query)
 * @returns Portfolio details and holdings state
 */
export function usePortfolioDetail(portfolioId: number | undefined) {
  const queryClient = useQueryClient()

  // Fetch portfolio details
  const portfolioQuery = useQuery({
    queryKey: portfolioDetailQueryKey(portfolioId!),
    queryFn: async () => {
      const response = await portfolioService.get(portfolioId!)
      return response.data
    },
    enabled: !!portfolioId,
    staleTime: 1 * 60 * 1000, // 1 minute
    gcTime: 5 * 60 * 1000, // 5 minutes
  })

  // Fetch holdings for this portfolio
  const holdingsQuery = useQuery({
    queryKey: ['portfolio', portfolioId, 'holdings'],
    queryFn: async () => {
      const response = await portfolioService.getHoldings(portfolioId!)
      return response.data
    },
    enabled: !!portfolioId,
    staleTime: 30 * 1000, // 30 seconds (for price updates)
    gcTime: 5 * 60 * 1000,
    refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
  })

  /**
   * Invalidate and refetch portfolio details.
   *
   * Useful after adding/removing holdings or transactions.
   */
  const refresh = () => {
    if (portfolioId) {
      queryClient.invalidateQueries({
        queryKey: portfolioDetailQueryKey(portfolioId),
      })
      queryClient.invalidateQueries({
        queryKey: ['portfolio', portfolioId, 'holdings'],
      })
    }
  }

  return {
    // Portfolio data
    portfolio: portfolioQuery.data,
    holdings: holdingsQuery.data?.items || [],
    totalHoldings: holdingsQuery.data?.total || 0,

    // Loading states
    isLoading: portfolioQuery.isLoading || holdingsQuery.isLoading,
    isPortfolioLoading: portfolioQuery.isLoading,
    isHoldingsLoading: holdingsQuery.isLoading,

    // Error states
    isError: portfolioQuery.isError || holdingsQuery.isError,
    error: portfolioQuery.error || holdingsQuery.error,

    // Refresh function
    refresh,
    refetchPortfolio: portfolioQuery.refetch,
    refetchHoldings: holdingsQuery.refetch,
  }
}

export default usePortfolioDetail
