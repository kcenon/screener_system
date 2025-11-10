import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { stockService } from '../services/stockService'
import type {
  ScreeningFilters,
  ScreeningSortField,
  SortOrder,
  ScreeningResponse,
} from '../types/screening'

/**
 * Pagination state interface
 */
interface PaginationState {
  offset: number
  limit: number
}

/**
 * Sort state interface
 */
interface SortState {
  sortBy: ScreeningSortField
  order: SortOrder
}

/**
 * Custom hook for stock screening with filters, sorting, and pagination
 *
 * Features:
 * - Automatic debouncing of filter changes (500ms)
 * - React Query caching and automatic refetching
 * - Separate state management for filters, sorting, and pagination
 *
 * @returns Object containing screening data, loading state, error, and state setters
 */
export function useScreening() {
  // State management
  const [filters, setFilters] = useState<ScreeningFilters>({
    market: 'ALL',
  })

  const [sort, setSort] = useState<SortState>({
    sortBy: 'market_cap',
    order: 'desc',
  })

  const [pagination, setPagination] = useState<PaginationState>({
    offset: 0,
    limit: 50,
  })

  // Debounced filters state
  const [debouncedFilters, setDebouncedFilters] = useState<ScreeningFilters>(filters)

  // Debounce filter changes (500ms)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedFilters(filters)
      // Reset to first page when filters change
      setPagination((prev) => ({ ...prev, offset: 0 }))
    }, 500)

    return () => clearTimeout(timeoutId)
  }, [filters])

  // React Query for data fetching
  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<ScreeningResponse, Error>({
    queryKey: ['screening', debouncedFilters, sort, pagination],
    queryFn: async () => {
      return await stockService.screenStocks(
        debouncedFilters,
        sort.sortBy,
        sort.order,
        pagination.offset,
        pagination.limit
      )
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    refetchOnWindowFocus: false,
  })

  return {
    // Data
    data,
    isLoading,
    error,

    // State
    filters,
    sort,
    pagination,

    // State setters
    setFilters,
    setSort,
    setPagination,

    // Actions
    refetch,
  }
}
