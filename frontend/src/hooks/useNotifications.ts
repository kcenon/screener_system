/**
 * Notifications Management Hook.
 *
 * Manages user notifications with pagination and filtering.
 * Provides automatic caching and real-time updates.
 *
 * @module hooks/useNotifications
 * @category Hooks
 */

import {
  useInfiniteQuery,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query'
import {
  type Notification,
  NotificationPriority,
  notificationService,
  type NotificationType,
} from '../services/notificationService'

/**
 * Query key factory for notifications.
 *
 * @param filters - Optional filters
 * @returns Query key array
 */
export const notificationsQueryKey = (filters?: {
  notification_type?: NotificationType
  is_read?: boolean
  priority?: NotificationPriority
}) => ['notifications', filters] as const

/**
 * Hook for managing user notifications with infinite scroll.
 *
 * Provides:
 * - Paginated notification list
 * - Infinite scroll support
 * - Mark as read operations
 * - Delete operations
 * - Filtering by type, read status, priority
 *
 * ## Query Caching
 *
 * - Stale Time: 10 seconds (data considered fresh)
 * - Cache Time: 5 minutes (unused data kept in cache)
 * - Refetch Interval: 30 seconds (check for new notifications)
 *
 * @example
 * Basic usage:
 * ```typescript
 * const {
 *   notifications,
 *   isLoading,
 *   hasMore,
 *   loadMore,
 *   markAsRead,
 * } = useNotifications();
 *
 * return (
 *   <div>
 *     {notifications.map(notif => (
 *       <NotificationItem
 *         key={notif.id}
 *         notification={notif}
 *         onRead={() => markAsRead(notif.id)}
 *       />
 *     ))}
 *     {hasMore && <button onClick={loadMore}>Load More</button>}
 *   </div>
 * );
 * ```
 *
 * @example
 * With filtering:
 * ```typescript
 * const { notifications } = useNotifications({
 *   notification_type: NotificationType.ALERT,
 *   is_read: false,
 * });
 * ```
 *
 * @param filters - Optional notification filters
 * @returns Notification management interface
 */
export function useNotifications(filters?: {
  notification_type?: NotificationType
  is_read?: boolean
  priority?: NotificationPriority
}) {
  const queryClient = useQueryClient()
  const pageSize = 20

  // Infinite query for paginated notifications
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
  } = useInfiniteQuery({
    queryKey: notificationsQueryKey(filters),
    queryFn: ({ pageParam = 1 }) =>
      notificationService.getNotifications({
        page: pageParam,
        page_size: pageSize,
        ...filters,
      }),
    getNextPageParam: (lastPage, allPages) => {
      const currentCount = allPages.reduce(
        (sum, page) => sum + page.items.length,
        0,
      )
      return currentCount < lastPage.total ? allPages.length + 1 : undefined
    },
    initialPageParam: 1,
    staleTime: 10 * 1000, // 10 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // 30 seconds
  })

  // Flatten notifications from all pages
  const notifications = data?.pages.flatMap(page => page.items) ?? []
  const total = data?.pages[0]?.total ?? 0
  const unreadCount = data?.pages[0]?.unread_count ?? 0

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: (id: number) => notificationService.markAsRead(id),
    onMutate: async id => {
      await queryClient.cancelQueries({
        queryKey: notificationsQueryKey(filters),
      })

      const previousData = queryClient.getQueryData(
        notificationsQueryKey(filters),
      )

      // Optimistically update
      queryClient.setQueryData(notificationsQueryKey(filters), (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((notif: Notification) =>
              notif.id === id
                ? { ...notif, is_read: true, read_at: new Date().toISOString() }
                : notif,
            ),
            unread_count: page.unread_count > 0 ? page.unread_count - 1 : 0,
          })),
        }
      })

      return { previousData }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(
          notificationsQueryKey(filters),
          context.previousData,
        )
      }
    },
    onSuccess: () => {
      // Invalidate unread count query
      queryClient.invalidateQueries({
        queryKey: ['notifications', 'unread-count'],
      })
    },
  })

  // Mark all as read mutation
  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationService.markAllAsRead(),
    onMutate: async () => {
      await queryClient.cancelQueries({
        queryKey: notificationsQueryKey(filters),
      })

      const previousData = queryClient.getQueryData(
        notificationsQueryKey(filters),
      )

      // Optimistically update all notifications
      queryClient.setQueryData(notificationsQueryKey(filters), (old: any) => {
        if (!old) return old

        const now = new Date().toISOString()
        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((notif: Notification) => ({
              ...notif,
              is_read: true,
              read_at: notif.read_at || now,
            })),
            unread_count: 0,
          })),
        }
      })

      return { previousData }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(
          notificationsQueryKey(filters),
          context.previousData,
        )
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['notifications', 'unread-count'],
      })
    },
  })

  // Delete notification mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => notificationService.deleteNotification(id),
    onMutate: async id => {
      await queryClient.cancelQueries({
        queryKey: notificationsQueryKey(filters),
      })

      const previousData = queryClient.getQueryData(
        notificationsQueryKey(filters),
      )

      queryClient.setQueryData(notificationsQueryKey(filters), (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.filter((notif: Notification) => notif.id !== id),
            total: page.total - 1,
          })),
        }
      })

      return { previousData }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(
          notificationsQueryKey(filters),
          context.previousData,
        )
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: notificationsQueryKey(filters),
      })
    },
  })

  return {
    // Data
    notifications,
    total,
    unreadCount,
    isLoading,
    error,

    // Pagination
    hasMore: hasNextPage,
    loadMore: fetchNextPage,
    isLoadingMore: isFetchingNextPage,

    // Actions
    markAsRead: markAsReadMutation.mutateAsync,
    markAllAsRead: markAllAsReadMutation.mutateAsync,
    deleteNotification: deleteMutation.mutateAsync,
    refetch,

    // Mutation states
    isMarkingAsRead: markAsReadMutation.isPending,
    isMarkingAllAsRead: markAllAsReadMutation.isPending,
    isDeleting: deleteMutation.isPending,
  }
}
