/**
 * Hook for fetching market indices data
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query'
import { getMarketIndices } from '../services/marketService'
import type { MarketIndicesResponse } from '../types/market'

/**
 * Hook options
 */
export interface UseMarketIndicesOptions {
  /** Enable auto-refetch interval (milliseconds) */
  refetchInterval?: number
  /** Enable the query */
  enabled?: boolean
}

/**
 * Fetch market indices data (KOSPI, KOSDAQ, KRX100)
 *
 * @param options - Hook options
 * @returns Query result with market indices data
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useMarketIndices({
 *   refetchInterval: 30000 // Refetch every 30 seconds
 * })
 * ```
 */
export function useMarketIndices(
  options: UseMarketIndicesOptions = {}
): UseQueryResult<MarketIndicesResponse, Error> {
  const { refetchInterval = 60000, enabled = true } = options

  return useQuery<MarketIndicesResponse, Error>({
    queryKey: ['market', 'indices'],
    queryFn: getMarketIndices,
    refetchInterval,
    enabled,
    staleTime: 30000, // Consider data stale after 30 seconds
    gcTime: 5 * 60 * 1000, // Keep in cache for 5 minutes
  })
}
