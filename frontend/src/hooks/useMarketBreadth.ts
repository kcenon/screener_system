/**
 * Hook for fetching market breadth data
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query'
import { getMarketBreadth } from '../services/marketService'
import type { MarketBreadth, MarketType } from '../types/market'

/**
 * Hook options
 */
export interface UseMarketBreadthOptions {
  /** Market filter */
  market?: MarketType
  /** Enable auto-refetch interval (milliseconds) */
  refetchInterval?: number
  /** Enable the query */
  enabled?: boolean
}

/**
 * Fetch market breadth indicators
 *
 * @param options - Hook options
 * @returns Query result with market breadth data
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useMarketBreadth({
 *   market: 'KOSPI',
 *   refetchInterval: 60000
 * })
 * ```
 */
export function useMarketBreadth(
  options: UseMarketBreadthOptions = {}
): UseQueryResult<MarketBreadth, Error> {
  const { market = 'ALL', refetchInterval = 60000, enabled = true } = options

  return useQuery<MarketBreadth, Error>({
    queryKey: ['market', 'breadth', market],
    queryFn: () => getMarketBreadth(market),
    refetchInterval,
    enabled,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  })
}
