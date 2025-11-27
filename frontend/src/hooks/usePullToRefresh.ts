import { useState, useRef, useCallback, useEffect } from 'react'

interface PullToRefreshOptions {
  onRefresh: () => Promise<void>
  threshold?: number
  disabled?: boolean
}

interface PullToRefreshReturn {
  isRefreshing: boolean
  pullDistance: number
  containerRef: React.RefObject<HTMLDivElement>
  indicatorStyle: React.CSSProperties
}

/**
 * Hook for implementing pull-to-refresh functionality
 *
 * @param options - Configuration options
 * @returns Pull-to-refresh state and handlers
 *
 * @example
 * ```tsx
 * const { isRefreshing, containerRef, indicatorStyle } = usePullToRefresh({
 *   onRefresh: async () => {
 *     await fetchData()
 *   }
 * })
 *
 * return (
 *   <div ref={containerRef}>
 *     <div style={indicatorStyle}>
 *       {isRefreshing ? <Spinner /> : 'Pull to refresh'}
 *     </div>
 *     <Content />
 *   </div>
 * )
 * ```
 */
export function usePullToRefresh({
  onRefresh,
  threshold = 80,
  disabled = false,
}: PullToRefreshOptions): PullToRefreshReturn {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [pullDistance, setPullDistance] = useState(0)

  const containerRef = useRef<HTMLDivElement>(null)
  const startY = useRef(0)
  const currentY = useRef(0)
  const isPulling = useRef(false)

  const handleTouchStart = useCallback(
    (e: TouchEvent) => {
      if (disabled || isRefreshing) return

      const container = containerRef.current
      if (!container) return

      // Only start pull-to-refresh if scrolled to top
      if (container.scrollTop === 0) {
        startY.current = e.touches[0].clientY
        isPulling.current = true
      }
    },
    [disabled, isRefreshing]
  )

  const handleTouchMove = useCallback(
    (e: TouchEvent) => {
      if (!isPulling.current || disabled || isRefreshing) return

      currentY.current = e.touches[0].clientY
      const distance = Math.max(0, currentY.current - startY.current)

      // Apply resistance to the pull
      const resistedDistance = Math.min(distance * 0.5, threshold * 1.5)
      setPullDistance(resistedDistance)

      // Prevent default scroll if we're pulling
      if (distance > 10) {
        e.preventDefault()
      }
    },
    [disabled, isRefreshing, threshold]
  )

  const handleTouchEnd = useCallback(async () => {
    if (!isPulling.current || disabled) return

    isPulling.current = false

    if (pullDistance >= threshold && !isRefreshing) {
      setIsRefreshing(true)
      try {
        await onRefresh()
      } catch (error) {
        console.error('Refresh failed:', error)
      } finally {
        setIsRefreshing(false)
      }
    }

    setPullDistance(0)
  }, [disabled, isRefreshing, onRefresh, pullDistance, threshold])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    container.addEventListener('touchstart', handleTouchStart, { passive: true })
    container.addEventListener('touchmove', handleTouchMove, { passive: false })
    container.addEventListener('touchend', handleTouchEnd)

    return () => {
      container.removeEventListener('touchstart', handleTouchStart)
      container.removeEventListener('touchmove', handleTouchMove)
      container.removeEventListener('touchend', handleTouchEnd)
    }
  }, [handleTouchStart, handleTouchMove, handleTouchEnd])

  const indicatorStyle: React.CSSProperties = {
    transform: `translateY(${pullDistance}px)`,
    transition: isPulling.current ? 'none' : 'transform 0.3s ease-out',
    opacity: Math.min(pullDistance / threshold, 1),
  }

  return {
    isRefreshing,
    pullDistance,
    containerRef,
    indicatorStyle,
  }
}

export default usePullToRefresh
