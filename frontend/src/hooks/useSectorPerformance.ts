/**
 * Hook for fetching sector performance data
 */

import { useQuery, type UseQueryResult } from '@tanstack/react-query'
import { getSectorPerformance } from '../services/marketService'
import type { SectorsPerformanceResponse } from '../types/market'

/**
 * Hook options
 */
export interface UseSectorPerformanceOptions {
  /** Timeframe for performance calculation */
  timeframe?: '1D' | '1W' | '1M' | '3M'
  /** Enable auto-refetch interval (milliseconds) */
  refetchInterval?: number
  /** Enable the query */
  enabled?: boolean
}

/**
 * Fetch sector performance data
 *
 * @param options - Hook options
 * @returns Query result with sector performance data
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useSectorPerformance({
 *   timeframe: '1D',
 *   refetchInterval: 60000
 * })
 * ```
 */
export function useSectorPerformance(
  options: UseSectorPerformanceOptions = {}
): UseQueryResult<SectorsPerformanceResponse, Error> {
  const { timeframe = '1D', refetchInterval, enabled = true } = options

  return useQuery<SectorsPerformanceResponse, Error>({
    queryKey: ['market', 'sectors', timeframe],
    queryFn: () => getSectorPerformance(timeframe),
    refetchInterval,
    enabled,
    staleTime: 60000, // Sector data can be stale for 1 minute
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
  })
}
