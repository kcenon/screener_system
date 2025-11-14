/**
 * Dashboard Data Hook
 *
 * React hook for fetching and managing dashboard summary data,
 * including market indices, watchlists, and user activity.
 */

import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { DashboardSummary } from '../types'

/**
 * Fetch dashboard summary data
 */
async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const response = await api.get<DashboardSummary>('/users/dashboard')
  return response.data
}

/**
 * Hook for dashboard summary data
 *
 * Fetches comprehensive dashboard data including market indices,
 * watchlists, recent activities, and user statistics.
 *
 * @returns Query object with dashboard data and loading states
 *
 * @example
 * ```tsx
 * function Dashboard() {
 *   const { data, isLoading, error } = useDashboard()
 *
 *   if (isLoading) return <LoadingSpinner />
 *   if (error) return <ErrorMessage />
 *
 *   return (
 *     <div>
 *       <MarketSummary data={data.market_indices} />
 *       <Watchlists data={data.watchlists} />
 *     </div>
 *   )
 * }
 * ```
 */
export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboardSummary,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
    refetchOnWindowFocus: true,
  })
}
