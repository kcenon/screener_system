import { useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { ScreeningFilters, ScreeningSortField, SortOrder } from '@/types/screening'

/**
 * Serialize filters to URL search params
 */
function serializeFilters(filters: ScreeningFilters): URLSearchParams {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (value === null || value === undefined) return

    // Handle range filters
    if (typeof value === 'object' && 'min' in value && 'max' in value) {
      if (value.min !== null && value.min !== undefined) {
        params.set(`${key}_min`, String(value.min))
      }
      if (value.max !== null && value.max !== undefined) {
        params.set(`${key}_max`, String(value.max))
      }
    }
    // Handle simple values
    else {
      params.set(key, String(value))
    }
  })

  return params
}

/**
 * Deserialize filters from URL search params
 */
function deserializeFilters(params: URLSearchParams): ScreeningFilters {
  const filters: ScreeningFilters = {}

  // Extract search
  if (params.has('search')) {
    filters.search = params.get('search')
  }

  // Extract market
  if (params.has('market')) {
    const market = params.get('market')
    if (market === 'ALL' || market === 'KOSPI' || market === 'KOSDAQ') {
      filters.market = market
    }
  }

  // Extract sector/industry
  if (params.has('sector')) filters.sector = params.get('sector')
  if (params.has('industry')) filters.industry = params.get('industry')

  // Extract range filters
  const rangeFields = [
    'per', 'pbr', 'psr', 'pcr', 'dividend_yield',
    'roe', 'roa', 'roic', 'gross_margin', 'operating_margin', 'net_margin',
    'revenue_growth_yoy', 'profit_growth_yoy', 'eps_growth_yoy',
    'debt_to_equity', 'current_ratio', 'altman_z_score', 'piotroski_f_score',
    'price_change_1d', 'price_change_1w', 'price_change_1m', 'price_change_3m', 'price_change_6m', 'price_change_1y',
    'volume_surge_pct',
    'quality_score', 'value_score', 'growth_score', 'momentum_score', 'overall_score',
    'current_price', 'market_cap',
  ] as const

  rangeFields.forEach(field => {
    const minKey = `${field}_min`
    const maxKey = `${field}_max`

    if (params.has(minKey) || params.has(maxKey)) {
      const min = params.has(minKey) ? Number(params.get(minKey)) : null
      const max = params.has(maxKey) ? Number(params.get(maxKey)) : null

      if (!isNaN(min as number) || !isNaN(max as number)) {
        filters[field] = {
          min: !isNaN(min as number) ? min : null,
          max: !isNaN(max as number) ? max : null,
        }
      }
    }
  })

  return filters
}

/**
 * Hook for synchronizing filters, sort, and pagination with URL
 *
 * Features:
 * - Automatic URL update when state changes
 * - State initialization from URL on mount
 * - Browser back/forward support
 * - URL sharing support
 */
export function useURLSync(
  filters: ScreeningFilters,
  setFilters: (filters: ScreeningFilters) => void,
  sort: { sortBy: ScreeningSortField; order: SortOrder },
  setSort: (sort: { sortBy: ScreeningSortField; order: SortOrder }) => void,
  pagination: { offset: number; limit: number },
  setPagination: (pagination: { offset: number; limit: number }) => void
) {
  const [searchParams, setSearchParams] = useSearchParams()

  // Initialize state from URL on mount
  useEffect(() => {
    const urlFilters = deserializeFilters(searchParams)

    // Only update if URL has filters
    if (Object.keys(urlFilters).length > 0) {
      setFilters(urlFilters)
    }

    // Extract sort params
    if (searchParams.has('sort_by')) {
      const sortBy = searchParams.get('sort_by') as ScreeningSortField
      const order = (searchParams.get('order') as SortOrder) || 'desc'
      setSort({ sortBy, order })
    }

    // Extract pagination params
    if (searchParams.has('offset') || searchParams.has('limit')) {
      const offset = searchParams.has('offset') ? Number(searchParams.get('offset')) : 0
      const limit = searchParams.has('limit') ? Number(searchParams.get('limit')) : 50
      setPagination({ offset, limit })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Only run on mount

  // Update URL when state changes
  const updateURL = useCallback(() => {
    const params = serializeFilters(filters)

    // Add sort params
    params.set('sort_by', sort.sortBy)
    params.set('order', sort.order)

    // Add pagination params
    params.set('offset', String(pagination.offset))
    params.set('limit', String(pagination.limit))

    setSearchParams(params, { replace: true })
  }, [filters, sort, pagination, setSearchParams])

  // Sync URL with state changes (debounced)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      updateURL()
    }, 500)

    return () => clearTimeout(timeoutId)
  }, [updateURL])
}
