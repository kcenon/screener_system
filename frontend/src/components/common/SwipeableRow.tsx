import { useSwipeable, SwipeEventData } from 'react-swipeable'
import { useState, useCallback, ReactNode } from 'react'

interface SwipeAction {
  icon: ReactNode
  label: string
  color: string
  onClick: () => void
}

interface SwipeableRowProps {
  children: ReactNode
  leftAction?: SwipeAction
  rightAction?: SwipeAction
  threshold?: number
  className?: string
}

/**
 * A row component that reveals action buttons on swipe gestures
 *
 * @example
 * ```tsx
 * <SwipeableRow
 *   leftAction={{
 *     icon: <BookmarkIcon />,
 *     label: 'Add to Watchlist',
 *     color: 'bg-green-500',
 *     onClick: () => addToWatchlist(stock.code)
 *   }}
 *   rightAction={{
 *     icon: <TrashIcon />,
 *     label: 'Remove',
 *     color: 'bg-red-500',
 *     onClick: () => removeStock(stock.code)
 *   }}
 * >
 *   <StockRow stock={stock} />
 * </SwipeableRow>
 * ```
 */
export function SwipeableRow({
  children,
  leftAction,
  rightAction,
  threshold = 80,
  className = '',
}: SwipeableRowProps) {
  const [swipeOffset, setSwipeOffset] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)

  const resetPosition = useCallback(() => {
    setIsAnimating(true)
    setSwipeOffset(0)
    setTimeout(() => setIsAnimating(false), 300)
  }, [])

  const handleSwipeStart = useCallback(() => {
    setIsAnimating(false)
  }, [])

  const handleSwiping = useCallback(
    (event: SwipeEventData) => {
      const { deltaX } = event

      // Limit swipe based on available actions
      let newOffset = deltaX
      if (!leftAction && deltaX > 0) newOffset = 0
      if (!rightAction && deltaX < 0) newOffset = 0

      // Add resistance at boundaries
      const maxOffset = threshold * 1.5
      if (Math.abs(newOffset) > maxOffset) {
        newOffset = newOffset > 0 ? maxOffset : -maxOffset
      }

      setSwipeOffset(newOffset)
    },
    [leftAction, rightAction, threshold],
  )

  const handleSwipeEnd = useCallback(
    (event: SwipeEventData) => {
      const { deltaX, velocity } = event
      const isQuickSwipe = velocity > 0.5

      // Execute action if threshold is met
      if (deltaX > threshold || (deltaX > 50 && isQuickSwipe)) {
        leftAction?.onClick()
      } else if (deltaX < -threshold || (deltaX < -50 && isQuickSwipe)) {
        rightAction?.onClick()
      }

      resetPosition()
    },
    [leftAction, rightAction, threshold, resetPosition],
  )

  const handlers = useSwipeable({
    onSwipeStart: handleSwipeStart,
    onSwiping: handleSwiping,
    onSwiped: handleSwipeEnd,
    trackMouse: false,
    trackTouch: true,
    delta: 10,
    preventScrollOnSwipe: true,
  })

  const showLeftAction = leftAction && swipeOffset > 20
  const showRightAction = rightAction && swipeOffset < -20

  return (
    <div className={`relative overflow-hidden touch-pan-y ${className}`}>
      {/* Left action background */}
      {leftAction && (
        <div
          className={`absolute inset-y-0 left-0 flex items-center justify-start
            px-4 ${leftAction.color} transition-opacity duration-150`}
          style={{
            opacity: showLeftAction ? Math.min(swipeOffset / threshold, 1) : 0,
            width: Math.max(swipeOffset, 0),
          }}
        >
          <div className="text-white flex items-center gap-2">
            {leftAction.icon}
            {swipeOffset > threshold && (
              <span className="text-sm font-medium whitespace-nowrap">
                {leftAction.label}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Right action background */}
      {rightAction && (
        <div
          className={`absolute inset-y-0 right-0 flex items-center justify-end
            px-4 ${rightAction.color} transition-opacity duration-150`}
          style={{
            opacity: showRightAction
              ? Math.min(Math.abs(swipeOffset) / threshold, 1)
              : 0,
            width: Math.max(-swipeOffset, 0),
          }}
        >
          <div className="text-white flex items-center gap-2">
            {swipeOffset < -threshold && (
              <span className="text-sm font-medium whitespace-nowrap">
                {rightAction.label}
              </span>
            )}
            {rightAction.icon}
          </div>
        </div>
      )}

      {/* Main content */}
      <div
        {...handlers}
        className={`relative bg-white ${isAnimating ? 'transition-transform duration-300 ease-out' : ''}`}
        style={{
          transform: `translateX(${swipeOffset}px)`,
        }}
      >
        {children}
      </div>
    </div>
  )
}

export default SwipeableRow
