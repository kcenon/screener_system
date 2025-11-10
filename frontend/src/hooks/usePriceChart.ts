import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { subDays, format } from 'date-fns'
import { stockService } from '@/services/stockService'
import type { PriceHistoryResponse, PriceInterval } from '@/types'

/**
 * Hook for managing price chart data and timeframe
 *
 * Features:
 * - Timeframe selection (1D, 1W, 1M, 3M, 6M, 1Y, 3Y, 5Y, ALL)
 * - Automatic date range calculation
 * - Data caching per timeframe
 * - Loading and error states
 *
 * @param code - Stock code
 * @param initialTimeframe - Initial timeframe (default: '1M')
 * @returns Chart data, timeframe state, and controls
 *
 * @example
 * ```tsx
 * const { data, isLoading, timeframe, setTimeframe } = usePriceChart('005930')
 *
 * return (
 *   <div>
 *     <button onClick={() => setTimeframe('1M')}>1M</button>
 *     <button onClick={() => setTimeframe('1Y')}>1Y</button>
 *     <PriceChart data={data} loading={isLoading} />
 *   </div>
 * )
 * ```
 */
export function usePriceChart(
  code: string | undefined,
  initialTimeframe: PriceInterval = '1M'
) {
  const [timeframe, setTimeframe] = useState<PriceInterval>(initialTimeframe)

  // Calculate date range based on timeframe
  const { fromDate, toDate } = useMemo(() => {
    const today = new Date()
    const endDate = format(today, 'yyyy-MM-dd')

    let startDate: string
    switch (timeframe) {
      case '1D':
        startDate = format(subDays(today, 1), 'yyyy-MM-dd')
        break
      case '1W':
        startDate = format(subDays(today, 7), 'yyyy-MM-dd')
        break
      case '1M':
        startDate = format(subDays(today, 30), 'yyyy-MM-dd')
        break
      case '3M':
        startDate = format(subDays(today, 90), 'yyyy-MM-dd')
        break
      case '6M':
        startDate = format(subDays(today, 180), 'yyyy-MM-dd')
        break
      case '1Y':
        startDate = format(subDays(today, 365), 'yyyy-MM-dd')
        break
      case '3Y':
        startDate = format(subDays(today, 1095), 'yyyy-MM-dd')
        break
      case '5Y':
        startDate = format(subDays(today, 1825), 'yyyy-MM-dd')
        break
      case 'ALL':
        // Fetch all available data (backend will handle)
        startDate = '1990-01-01'
        break
      default:
        startDate = format(subDays(today, 30), 'yyyy-MM-dd')
    }

    return { fromDate: startDate, toDate: endDate }
  }, [timeframe])

  // Fetch price history
  const query = useQuery<PriceHistoryResponse, Error>({
    queryKey: ['priceHistory', code, timeframe, fromDate, toDate],
    queryFn: async () => {
      if (!code) {
        throw new Error('Stock code is required')
      }
      return stockService.getPriceHistory(code, fromDate, toDate, timeframe)
    },
    enabled: !!code,
    staleTime: 2 * 60 * 1000, // 2 minutes (price data changes less frequently)
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false, // Don't refetch price history on focus
    retry: 2,
  })

  return {
    ...query,
    timeframe,
    setTimeframe,
    fromDate,
    toDate,
  }
}
