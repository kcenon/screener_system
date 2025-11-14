/**
 * Hook for fetching market movers (top gainers and losers)
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query'
import { getMarketMovers } from '../services/marketService'
import type { MarketMoversResponse, MarketType } from '../types/market'

/**
 * Hook options
 */
export interface UseMarketMoversOptions {
  /** Market filter */
  market?: MarketType
  /** Number of results per category */
  limit?: number
  /** Enable auto-refetch interval (milliseconds) */
  refetchInterval?: number
  /** Enable the query */
  enabled?: boolean
}

/**
 * Fetch top market movers (gainers and losers)
 *
 * @param options - Hook options
 * @returns Query result with market movers data
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useMarketMovers({
 *   market: 'ALL',
 *   limit: 10,
 *   refetchInterval: 60000
 * })
 * ```
 */
export function useMarketMovers(
  options: UseMarketMoversOptions = {}
): UseQueryResult<MarketMoversResponse, Error> {
  const { market = 'ALL', limit = 10, refetchInterval = 60000, enabled = true } = options

  return useQuery<MarketMoversResponse, Error>({
    queryKey: ['market', 'movers', market, limit],
    queryFn: () => getMarketMovers(market, limit),
    refetchInterval,
    enabled,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  })
}
