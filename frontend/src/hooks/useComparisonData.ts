/**
 * useComparisonData Hook
 * Fetches stock data for multiple stocks in parallel
 */

import { useQueries } from '@tanstack/react-query'
import { stockService } from '../services/stockService'
import type { ComparisonStock } from '../types/comparison'

export function useComparisonData(stockCodes: string[]) {
  // Fetch all stocks in parallel using useQueries
  const queries = useQueries({
    queries: stockCodes.map(code => ({
      queryKey: ['stock', code],
      queryFn: () => stockService.getStock(code),
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (renamed from cacheTime)
      retry: 2,
      enabled: !!code,
    })),
  })

  // Transform query results into ComparisonStock array
  const stocks: ComparisonStock[] = queries.map((query, index) => {
    const code = stockCodes[index]

    if (query.isLoading) {
      return {
        code,
        name: '',
        market: 'KOSPI',
        sector: '',
        current_price: 0,
        isLoading: true,
      } as ComparisonStock
    }

    if (query.error || !query.data) {
      return {
        code,
        name: '',
        market: 'KOSPI',
        sector: '',
        current_price: 0,
        error: query.error ? String(query.error) : 'Failed to load stock data',
      } as ComparisonStock
    }

    return {
      ...query.data,
      isLoading: false,
      error: null,
    } as ComparisonStock
  })

  const isLoading = queries.some(q => q.isLoading)
  const isError = queries.some(q => q.isError)
  const errors = queries
    .map((q, i) => ({ code: stockCodes[i], error: q.error }))
    .filter(e => e.error)

  return {
    stocks,
    isLoading,
    isError,
    errors,
    refetch: () => queries.forEach(q => q.refetch()),
  }
}
