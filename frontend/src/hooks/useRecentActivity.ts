/**
 * Recent Activity Hook
 *
 * React hook for fetching user's recent activities with pagination.
 */

import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { RecentActivityResponse } from '../types'

interface UseRecentActivityOptions {
  /** Page number (starts from 1) */
  page?: number
  /** Number of items per page */
  limit?: number
}

/**
 * Fetch recent user activities
 */
async function fetchRecentActivity(
  options: UseRecentActivityOptions = {}
): Promise<RecentActivityResponse> {
  const { page = 1, limit = 10 } = options

  const response = await api.get<RecentActivityResponse>('/users/activities', {
    params: { page, limit },
  })

  return response.data
}

/**
 * Hook for recent user activities
 *
 * Fetches the user's recent activities such as screenings, watchlist updates,
 * stock views, etc.
 *
 * @param options - Pagination options
 * @returns Query object with activities and loading states
 *
 * @example
 * ```tsx
 * function RecentActivity() {
 *   const { data, isLoading } = useRecentActivity({ limit: 5 })
 *
 *   if (isLoading) return <LoadingSkeleton />
 *
 *   return (
 *     <ul>
 *       {data?.activities.map(activity => (
 *         <li key={activity.id}>{activity.description}</li>
 *       ))}
 *     </ul>
 *   )
 * }
 * ```
 */
export function useRecentActivity(options: UseRecentActivityOptions = {}) {
  return useQuery({
    queryKey: ['recent-activity', options],
    queryFn: () => fetchRecentActivity(options),
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  })
}
