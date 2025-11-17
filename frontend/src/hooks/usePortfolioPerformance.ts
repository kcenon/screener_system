/**
 * Portfolio Performance Hook.
 *
 * Manages portfolio performance metrics and allocation data.
 * Provides real-time updates for portfolio value, gain/loss, and sector allocation.
 *
 * @module hooks/usePortfolioPerformance
 * @category Hooks
 */

import { useQuery } from '@tanstack/react-query'
import { portfolioService } from '../services/portfolioService'

/**
 * Hook for fetching portfolio performance metrics and allocation.
 *
 * Provides:
 * - Performance metrics (total value, gain/loss, return %)
 * - Allocation breakdown (by stock and sector)
 * - Automatic background updates
 * - Error handling
 *
 * ## Query Caching
 *
 * - Stale Time: 30 seconds (data considered fresh)
 * - Cache Time: 5 minutes (unused data kept in cache)
 * - Refetch Interval: 30 seconds (for price updates)
 *
 * @example
 * Basic usage:
 * ```typescript
 * const { performance, allocation, isLoading } = usePortfolioPerformance(portfolioId);
 *
 * console.log('Total Value:', performance?.total_value);
 * console.log('Total Return:', performance?.total_return_percent);
 * console.log('Allocation:', allocation?.by_sector);
 * ```
 *
 * @example
 * With manual refresh:
 * ```typescript
 * const { performance, refresh } = usePortfolioPerformance(portfolioId);
 *
 * // Refresh after transaction
 * await addTransaction(...);
 * refresh();
 * ```
 *
 * @param portfolioId - Portfolio ID to fetch (undefined to skip query)
 * @returns Performance metrics and allocation state
 */
export function usePortfolioPerformance(portfolioId: number | undefined) {
  // Fetch performance metrics
  const performanceQuery = useQuery({
    queryKey: ['portfolio', portfolioId, 'performance'],
    queryFn: async () => {
      const response = await portfolioService.getPerformance(portfolioId!)
      return response.data
    },
    enabled: !!portfolioId,
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
  })

  // Fetch allocation breakdown
  const allocationQuery = useQuery({
    queryKey: ['portfolio', portfolioId, 'allocation'],
    queryFn: async () => {
      const response = await portfolioService.getAllocation(portfolioId!)
      return response.data
    },
    enabled: !!portfolioId,
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000,
    refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
  })

  /**
   * Manually refresh performance and allocation data.
   *
   * Useful after transactions or price updates.
   */
  const refresh = () => {
    performanceQuery.refetch()
    allocationQuery.refetch()
  }

  return {
    // Performance data
    performance: performanceQuery.data,

    // Allocation data
    allocation: allocationQuery.data,
    stockAllocation: allocationQuery.data?.by_stock || [],
    sectorAllocation: allocationQuery.data?.by_sector || [],

    // Loading states
    isLoading: performanceQuery.isLoading || allocationQuery.isLoading,
    isPerformanceLoading: performanceQuery.isLoading,
    isAllocationLoading: allocationQuery.isLoading,

    // Error states
    isError: performanceQuery.isError || allocationQuery.isError,
    error: performanceQuery.error || allocationQuery.error,

    // Refresh functions
    refresh,
    refetchPerformance: performanceQuery.refetch,
    refetchAllocation: allocationQuery.refetch,
  }
}

export default usePortfolioPerformance
