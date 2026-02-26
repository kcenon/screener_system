/**
 * Hook for fetching historical market trend data
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query'
import { getMarketTrend } from '../services/marketService'
import type { MarketTrendResponse, TrendTimeframe } from '../types/market'

/**
 * Hook options
 */
export interface UseMarketTrendOptions {
  /** Timeframe for historical data */
  timeframe?: TrendTimeframe
  /** Array of index codes to fetch */
  indices?: string[]
  /** Enable auto-refetch interval (milliseconds) */
  refetchInterval?: number
  /** Enable the query */
  enabled?: boolean
}

/**
 * Fetch historical market trend data
 *
 * @param options - Hook options
 * @returns Query result with market trend data
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useMarketTrend({
 *   timeframe: '3M',
 *   indices: ['KOSPI', 'KOSDAQ']
 * })
 * ```
 */
export function useMarketTrend(
  options: UseMarketTrendOptions = {},
): UseQueryResult<MarketTrendResponse, Error> {
  const {
    timeframe = '3M',
    indices = ['KOSPI', 'KOSDAQ'],
    refetchInterval,
    enabled = true,
  } = options

  return useQuery<MarketTrendResponse, Error>({
    queryKey: ['market', 'trend', timeframe, indices],
    queryFn: () => getMarketTrend(timeframe, indices),
    refetchInterval,
    enabled,
    staleTime: 5 * 60 * 1000, // Historical data can be stale for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep in cache for 30 minutes
  })
}
