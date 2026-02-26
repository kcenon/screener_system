/**
 * Unread Notification Count Hook.
 *
 * Tracks unread notification count with real-time updates.
 * Optimized for performance with aggressive caching.
 *
 * @module hooks/useUnreadCount
 * @category Hooks
 */

import { useQuery } from '@tanstack/react-query'
import { notificationService } from '../services/notificationService'

/**
 * Query key for unread count.
 *
 * @returns Query key array
 */
export const unreadCountQueryKey = () =>
  ['notifications', 'unread-count'] as const

/**
 * Hook for tracking unread notification count.
 *
 * Provides:
 * - Real-time unread count
 * - Automatic background updates
 * - Optimized caching for performance
 *
 * ## Query Caching
 *
 * - Stale Time: 5 seconds (data considered fresh)
 * - Cache Time: 10 minutes (kept in cache longer)
 * - Refetch Interval: 15 seconds (frequent updates for header badge)
 *
 * @example
 * Basic usage in notification bell:
 * ```typescript
 * function NotificationBell() {
 *   const { unreadCount, isLoading } = useUnreadCount();
 *
 *   return (
 *     <button className="relative">
 *       <BellIcon />
 *       {unreadCount > 0 && (
 *         <span className="absolute top-0 right-0 badge">
 *           {unreadCount > 99 ? '99+' : unreadCount}
 *         </span>
 *       )}
 *     </button>
 *   );
 * }
 * ```
 *
 * @example
 * With manual refresh:
 * ```typescript
 * const { unreadCount, refetch } = useUnreadCount();
 *
 * // Refresh after marking notification as read
 * await markAsRead(notificationId);
 * refetch();
 * ```
 *
 * @returns Unread count interface
 */
export function useUnreadCount() {
  const {
    data: unreadCount = 0,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: unreadCountQueryKey(),
    queryFn: () => notificationService.getUnreadCount(),
    staleTime: 5 * 1000, // 5 seconds
    gcTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 15 * 1000, // 15 seconds for real-time feel
    refetchIntervalInBackground: true, // Keep updating even when tab is not focused
  })

  return {
    unreadCount,
    isLoading,
    error,
    refetch,

    // Helper properties
    hasUnread: unreadCount > 0,
    displayCount: unreadCount > 99 ? '99+' : unreadCount.toString(),
  }
}
