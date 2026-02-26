/**
 * Infinite Scroll Hook
 *
 * Provides infinite scrolling functionality for list views
 * with automatic loading of more items when user scrolls near bottom.
 */

import { useEffect, useState, useCallback, useRef } from 'react'

/**
 * Configuration options for infinite scroll
 */
export interface UseInfiniteScrollOptions {
  /**
   * Threshold distance from bottom (in pixels) to trigger loading
   * @default 500
   */
  threshold?: number

  /**
   * Whether infinite scroll is enabled
   * @default true
   */
  enabled?: boolean

  /**
   * Whether there are more items to load
   * @default true
   */
  hasMore?: boolean

  /**
   * Whether currently loading items
   * @default false
   */
  isLoading?: boolean
}

/**
 * Return type for useInfiniteScroll hook
 */
export interface UseInfiniteScrollReturn {
  /** Whether currently fetching more items */
  isFetching: boolean
  /** Reference to scroll container element */
  scrollContainerRef: React.RefObject<HTMLDivElement | null>
  /** Manually trigger load more */
  loadMore: () => void
}

/**
 * Custom hook for infinite scroll functionality
 *
 * Automatically loads more items when user scrolls near bottom of container.
 * Prevents duplicate loads and provides manual trigger option.
 *
 * @param fetchMore - Callback function to fetch more items
 * @param options - Configuration options
 * @returns Scroll state and utilities
 *
 * @example
 * ```tsx
 * function MyList() {
 *   const [page, setPage] = useState(1)
 *   const [hasMore, setHasMore] = useState(true)
 *   const [isLoading, setIsLoading] = useState(false)
 *
 *   const fetchMoreItems = async () => {
 *     setIsLoading(true)
 *     const newItems = await api.fetchItems(page + 1)
 *     setPage(page + 1)
 *     setHasMore(newItems.length > 0)
 *     setIsLoading(false)
 *   }
 *
 *   const { scrollContainerRef, isFetching, loadMore } = useInfiniteScroll(
 *     fetchMoreItems,
 *     { hasMore, isLoading }
 *   )
 *
 *   return (
 *     <div ref={scrollContainerRef}>
 *       {items.map(item => <Item key={item.id} {...item} />)}
 *       {isFetching && <Spinner />}
 *       <button onClick={loadMore}>Load More</button>
 *     </div>
 *   )
 * }
 * ```
 */
export function useInfiniteScroll(
  fetchMore: () => void | Promise<void>,
  options: UseInfiniteScrollOptions = {},
): UseInfiniteScrollReturn {
  const {
    threshold = 500,
    enabled = true,
    hasMore = true,
    isLoading = false,
  } = options

  const [isFetching, setIsFetching] = useState(false)
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const fetchingRef = useRef(false)

  /**
   * Manually trigger load more
   */
  const loadMore = useCallback(async () => {
    if (!enabled || !hasMore || isLoading || fetchingRef.current) {
      return
    }

    fetchingRef.current = true
    setIsFetching(true)

    try {
      await fetchMore()
    } finally {
      fetchingRef.current = false
      setIsFetching(false)
    }
  }, [enabled, hasMore, isLoading, fetchMore])

  /**
   * Handle scroll event
   */
  useEffect(() => {
    if (!enabled || !hasMore || isLoading) {
      return
    }

    const container = scrollContainerRef.current
    if (!container) {
      return
    }

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container

      // Check if scrolled near bottom
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight

      if (distanceFromBottom < threshold && !fetchingRef.current) {
        void loadMore()
      }
    }

    // Add scroll event listener
    container.addEventListener('scroll', handleScroll)

    // Cleanup
    return () => {
      container.removeEventListener('scroll', handleScroll)
    }
  }, [enabled, hasMore, isLoading, threshold, loadMore])

  return {
    isFetching,
    scrollContainerRef,
    loadMore,
  }
}
