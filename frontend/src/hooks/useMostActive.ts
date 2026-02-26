/**
 * Hook for fetching most active stocks by volume
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query'
import { getMostActive } from '../services/marketService'
import type { MostActiveResponse, MarketType } from '../types/market'

/**
 * Hook options
 */
export interface UseMostActiveOptions {
  /** Market filter */
  market?: MarketType
  /** Number of results */
  limit?: number
  /** Enable auto-refetch interval (milliseconds) */
  refetchInterval?: number
  /** Enable the query */
  enabled?: boolean
}

/**
 * Fetch most active stocks by volume
 *
 * @param options - Hook options
 * @returns Query result with most active stocks data
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useMostActive({
 *   market: 'ALL',
 *   limit: 20,
 *   refetchInterval: 60000
 * })
 * ```
 */
export function useMostActive(
  options: UseMostActiveOptions = {},
): UseQueryResult<MostActiveResponse, Error> {
  const {
    market = 'ALL',
    limit = 20,
    refetchInterval = 60000,
    enabled = true,
  } = options

  return useQuery<MostActiveResponse, Error>({
    queryKey: ['market', 'active', market, limit],
    queryFn: () => getMostActive(market, limit),
    refetchInterval,
    enabled,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  })
}
