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
 * Pagination state for screening results.
 *
 * Controls which subset of results to display using offset-based pagination.
 *
 * @interface
 * @category Types
 * @internal
 */
interface PaginationState {
  /**
   * Number of results to skip (0-indexed).
   *
   * @example 0 for first page, 50 for second page with limit=50
   */
  offset: number

  /**
   * Maximum number of results to return per page.
   *
   * @minimum 1
   * @maximum 100
   * @defaultValue 50
   */
  limit: number
}

/**
 * Sort configuration for screening results.
 *
 * Determines the field and direction for result ordering.
 *
 * @interface
 * @category Types
 * @internal
 */
interface SortState {
  /**
   * Field to sort results by.
   *
   * @see {@link ScreeningSortField} for available sort fields
   */
  sortBy: ScreeningSortField

  /**
   * Sort direction (ascending or descending).
   *
   * @example "asc" or "desc"
   */
  order: SortOrder
}

/**
 * React Query hook for stock screening with advanced filtering capabilities.
 *
 * Provides a complete screening experience with automatic debouncing, caching,
 * and state management for filters, sorting, and pagination. Uses React Query
 * for efficient data fetching with background refetching and cache management.
 *
 * ## Features
 *
 * - **Automatic Debouncing**: Filter changes are debounced by 500ms to reduce API calls
 * - **React Query Integration**: Automatic caching (5min), background refetching, and error handling
 * - **Pagination Management**: Offset-based pagination with automatic page reset on filter changes
 * - **Sort Management**: Configurable sorting by any screening field
 * - **Type Safety**: Full TypeScript support with type inference
 *
 * ## Query Caching
 *
 * - Stale Time: 5 minutes (data considered fresh for 5 minutes)
 * - Garbage Collection: 10 minutes (cached data kept for 10 minutes)
 * - Window Focus Refetching: Disabled (manual refetch required)
 *
 * @hook
 * @example
 * Basic usage with default filters
 * ```tsx
 * const {
 *   data,
 *   isLoading,
 *   error,
 *   setFilters,
 *   pagination,
 *   setPagination
 * } = useScreening();
 *
 * if (isLoading) return <Spinner />;
 * if (error) return <ErrorAlert error={error} />;
 *
 * return (
 *   <StockTable
 *     stocks={data.items}
 *     total={data.meta.total}
 *     onPageChange={(page) => setPagination({ offset: page * 50, limit: 50 })}
 *   />
 * );
 * ```
 *
 * @example
 * Advanced usage with filters and sorting
 * ```tsx
 * const { data, setFilters, setSort } = useScreening();
 *
 * // Apply filters (debounced automatically)
 * setFilters({
 *   market: 'KOSPI',
 *   per: { min: 0, max: 20 },
 *   pbr: { min: 0, max: 1.5 },
 *   roe: { min: 10 }
 * });
 *
 * // Change sort order
 * setSort({ sortBy: 'market_cap', order: 'desc' });
 *
 * // Manual refetch
 * refetch();
 * ```
 *
 * @example
 * Pagination control
 * ```tsx
 * const { pagination, setPagination, data } = useScreening();
 *
 * const goToPage = (pageNumber: number) => {
 *   setPagination({
 *     offset: pageNumber * pagination.limit,
 *     limit: pagination.limit
 *   });
 * };
 *
 * const changePageSize = (newSize: number) => {
 *   setPagination({ offset: 0, limit: newSize });
 * };
 * ```
 *
 * @returns Screening state and control functions
 * @returns data - Screening results with items and metadata
 * @returns data.items - Array of stocks matching the current filters
 * @returns data.meta - Metadata including total count, page info, and applied filters
 * @returns isLoading - True while fetching data
 * @returns error - Error object if request failed, null otherwise
 * @returns filters - Current filter state
 * @returns sort - Current sort configuration
 * @returns pagination - Current pagination state
 * @returns setFilters - Function to update filters (triggers debounced refetch)
 * @returns setSort - Function to update sort configuration
 * @returns setPagination - Function to update pagination state
 * @returns refetch - Function to manually refetch data
 *
 * @see {@link ScreeningFilters} for available filter options
 * @see {@link ScreeningResponse} for response data structure
 * @see {@link stockService.screenStocks} for underlying API call
 *
 * @category Hooks
 * @subcategory Data Fetching
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
