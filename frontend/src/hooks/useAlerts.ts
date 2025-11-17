/**
 * Alerts Management Hook.
 *
 * Manages stock price alerts with CRUD operations.
 * Provides automatic caching and real-time updates.
 *
 * @module hooks/useAlerts
 * @category Hooks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { alertService, type Alert, type AlertCreate, type AlertUpdate } from '../services/alertService'

/**
 * Query key factory for alerts.
 *
 * @returns Query key array
 */
export const alertsQueryKey = () => ['alerts'] as const

/**
 * Hook for managing user alerts.
 *
 * Provides:
 * - List of all user alerts
 * - CRUD operations (create, update, delete, toggle)
 * - Automatic background updates
 * - Optimistic updates for better UX
 *
 * ## Query Caching
 *
 * - Stale Time: 30 seconds (data considered fresh)
 * - Cache Time: 5 minutes (unused data kept in cache)
 * - Refetch Interval: 1 minute (check for triggered alerts)
 *
 * @example
 * Basic usage:
 * ```typescript
 * const { alerts, isLoading, createAlert, deleteAlert } = useAlerts();
 *
 * // Create new alert
 * await createAlert({
 *   stock_code: '005930',
 *   alert_type: 'PRICE_ABOVE',
 *   condition_value: 70000,
 *   is_recurring: false,
 * });
 *
 * // Delete alert
 * await deleteAlert(alertId);
 * ```
 *
 * @example
 * With filtering:
 * ```typescript
 * const { alerts } = useAlerts();
 * const activeAlerts = alerts.filter(a => a.is_active);
 * const priceAlerts = alerts.filter(a =>
 *   a.alert_type === 'PRICE_ABOVE' || a.alert_type === 'PRICE_BELOW'
 * );
 * ```
 *
 * @returns Alert management interface
 */
export function useAlerts() {
  const queryClient = useQueryClient()
  const [optimisticAlerts, setOptimisticAlerts] = useState<Alert[]>([])

  // Fetch all alerts
  const {
    data: alerts = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: alertsQueryKey(),
    queryFn: () => alertService.getAlerts(),
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
    refetchInterval: 60 * 1000, // 1 minute
  })

  // Create alert mutation
  const createMutation = useMutation({
    mutationFn: (data: AlertCreate) => alertService.createAlert(data),
    onMutate: async (newAlert) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: alertsQueryKey() })

      // Snapshot previous value
      const previousAlerts = queryClient.getQueryData<Alert[]>(alertsQueryKey())

      // Optimistically update
      const optimisticAlert: Alert = {
        id: Date.now(), // Temporary ID
        user_id: 0,
        stock_code: newAlert.stock_code,
        alert_type: newAlert.alert_type,
        condition_value: newAlert.condition_value,
        is_active: true,
        is_recurring: newAlert.is_recurring || false,
        triggered_at: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        stock: null,
      }

      queryClient.setQueryData<Alert[]>(alertsQueryKey(), (old) => [...(old || []), optimisticAlert])

      return { previousAlerts }
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.previousAlerts) {
        queryClient.setQueryData(alertsQueryKey(), context.previousAlerts)
      }
    },
    onSuccess: () => {
      // Refetch to get server data
      queryClient.invalidateQueries({ queryKey: alertsQueryKey() })
    },
  })

  // Update alert mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: AlertUpdate }) => alertService.updateAlert(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: alertsQueryKey() })

      const previousAlerts = queryClient.getQueryData<Alert[]>(alertsQueryKey())

      queryClient.setQueryData<Alert[]>(alertsQueryKey(), (old) =>
        old?.map((alert) => (alert.id === id ? { ...alert, ...data, updated_at: new Date().toISOString() } : alert))
      )

      return { previousAlerts }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousAlerts) {
        queryClient.setQueryData(alertsQueryKey(), context.previousAlerts)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertsQueryKey() })
    },
  })

  // Delete alert mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => alertService.deleteAlert(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: alertsQueryKey() })

      const previousAlerts = queryClient.getQueryData<Alert[]>(alertsQueryKey())

      queryClient.setQueryData<Alert[]>(alertsQueryKey(), (old) => old?.filter((alert) => alert.id !== id))

      return { previousAlerts }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousAlerts) {
        queryClient.setQueryData(alertsQueryKey(), context.previousAlerts)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertsQueryKey() })
    },
  })

  // Toggle alert active status
  const toggleMutation = useMutation({
    mutationFn: (id: number) => alertService.toggleAlert(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: alertsQueryKey() })

      const previousAlerts = queryClient.getQueryData<Alert[]>(alertsQueryKey())

      queryClient.setQueryData<Alert[]>(alertsQueryKey(), (old) =>
        old?.map((alert) =>
          alert.id === id ? { ...alert, is_active: !alert.is_active, updated_at: new Date().toISOString() } : alert
        )
      )

      return { previousAlerts }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousAlerts) {
        queryClient.setQueryData(alertsQueryKey(), context.previousAlerts)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: alertsQueryKey() })
    },
  })

  return {
    // Data
    alerts,
    isLoading,
    error,

    // Statistics
    totalAlerts: alerts.length,
    activeAlerts: alerts.filter((a) => a.is_active).length,
    triggeredAlerts: alerts.filter((a) => a.triggered_at !== null).length,

    // Actions
    createAlert: createMutation.mutateAsync,
    updateAlert: (id: number, data: AlertUpdate) => updateMutation.mutateAsync({ id, data }),
    deleteAlert: deleteMutation.mutateAsync,
    toggleAlert: toggleMutation.mutateAsync,
    refetch,

    // Mutation states
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isToggling: toggleMutation.isPending,
  }
}
