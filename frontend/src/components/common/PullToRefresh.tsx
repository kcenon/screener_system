import { ReactNode } from 'react'
import { RefreshCw } from 'lucide-react'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'

interface PullToRefreshProps {
  children: ReactNode
  onRefresh: () => Promise<void>
  disabled?: boolean
  threshold?: number
  className?: string
}

/**
 * Wrapper component that adds pull-to-refresh functionality
 *
 * @example
 * ```tsx
 * <PullToRefresh onRefresh={refetchData}>
 *   <StockList stocks={stocks} />
 * </PullToRefresh>
 * ```
 */
export function PullToRefresh({
  children,
  onRefresh,
  disabled = false,
  threshold = 80,
  className = '',
}: PullToRefreshProps) {
  const { isRefreshing, pullDistance, containerRef, indicatorStyle } =
    usePullToRefresh({
      onRefresh,
      threshold,
      disabled,
    })

  const progress = Math.min(pullDistance / threshold, 1)
  const rotation = progress * 180

  return (
    <div
      ref={containerRef}
      className={`relative overflow-y-auto overflow-x-hidden ${className}`}
    >
      {/* Pull indicator */}
      <div
        className="absolute left-0 right-0 flex justify-center items-center pointer-events-none z-10"
        style={{
          ...indicatorStyle,
          top: -40,
          height: 40,
        }}
      >
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full
            bg-white shadow-md border border-gray-200
            ${isRefreshing ? 'animate-pulse' : ''}`}
        >
          <RefreshCw
            className={`w-4 h-4 text-green-600 ${isRefreshing ? 'animate-spin' : ''}`}
            style={{
              transform: isRefreshing ? 'none' : `rotate(${rotation}deg)`,
              transition: isRefreshing ? 'none' : 'transform 0.1s ease-out',
            }}
          />
        </div>
      </div>

      {/* Content with transform applied during pull */}
      <div
        style={{
          transform: pullDistance > 0 ? `translateY(${pullDistance}px)` : 'none',
          transition: pullDistance > 0 ? 'none' : 'transform 0.3s ease-out',
        }}
      >
        {children}
      </div>

      {/* Loading overlay during refresh */}
      {isRefreshing && (
        <div className="absolute inset-0 bg-white/50 flex items-start justify-center pt-4 pointer-events-none">
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full shadow-sm border border-gray-200">
            <RefreshCw className="w-4 h-4 text-green-600 animate-spin" />
            <span className="text-sm text-gray-600">Refreshing...</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default PullToRefresh
