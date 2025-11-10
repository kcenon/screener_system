import { useQuery } from '@tanstack/react-query'
import { stockService } from '@/services/stockService'
import type { StockDetail } from '@/types'

/**
 * Hook for fetching and caching stock detail data
 *
 * Features:
 * - Automatic caching with 5-minute stale time
 * - Auto-refetch on window focus
 * - Error handling
 * - Loading states
 *
 * @param code - Stock code (e.g., '005930')
 * @returns Query result with stock data, loading state, and error
 *
 * @example
 * ```tsx
 * const { data, isLoading, error } = useStockData('005930')
 *
 * if (isLoading) return <div>Loading...</div>
 * if (error) return <div>Error: {error.message}</div>
 * if (data) return <div>{data.name}</div>
 * ```
 */
export function useStockData(code: string | undefined) {
  return useQuery<StockDetail, Error>({
    queryKey: ['stock', code],
    queryFn: async () => {
      if (!code) {
        throw new Error('Stock code is required')
      }
      return stockService.getStock(code)
    },
    enabled: !!code, // Only fetch if code is provided
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    refetchOnWindowFocus: true,
    retry: 2,
  })
}
