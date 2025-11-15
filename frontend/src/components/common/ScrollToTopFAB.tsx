/**
 * Scroll To Top Floating Action Button (FAB)
 *
 * A floating action button that appears when user scrolls down
 * and smoothly scrolls back to top when clicked.
 */

import { useState, useEffect } from 'react'

/**
 * Props for ScrollToTopFAB component
 */
export interface ScrollToTopFABProps {
  /**
   * Scroll threshold in pixels to show button
   * @default 200
   */
  threshold?: number

  /**
   * Position from bottom of viewport
   * @default '2rem'
   */
  bottom?: string

  /**
   * Position from right of viewport
   * @default '2rem'
   */
  right?: string

  /**
   * Scroll container selector or element
   * If not provided, uses window scroll
   */
  scrollContainer?: HTMLElement | string | null

  /**
   * Scroll behavior
   * @default 'smooth'
   */
  behavior?: ScrollBehavior
}

/**
 * Scroll to top floating action button
 *
 * Appears after scrolling down a certain threshold and provides
 * a quick way to return to top of page.
 *
 * @example
 * ```tsx
 * function MyPage() {
 *   return (
 *     <div>
 *       <Content />
 *       <ScrollToTopFAB threshold={300} />
 *     </div>
 *   )
 * }
 * ```
 */
export default function ScrollToTopFAB({
  threshold = 200,
  bottom = '2rem',
  right = '2rem',
  scrollContainer = null,
  behavior = 'smooth',
}: ScrollToTopFABProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Get scroll container element
    let container: HTMLElement | Window = window
    if (scrollContainer) {
      if (typeof scrollContainer === 'string') {
        const element = document.querySelector(scrollContainer) as HTMLElement
        if (element) {
          container = element
        }
      } else {
        container = scrollContainer
      }
    }

    const handleScroll = () => {
      const scrollTop =
        container === window
          ? window.pageYOffset || document.documentElement.scrollTop
          : (container as HTMLElement).scrollTop

      setIsVisible(scrollTop > threshold)
    }

    // Initial check
    handleScroll()

    // Add scroll listener
    container.addEventListener('scroll', handleScroll)

    // Cleanup
    return () => {
      container.removeEventListener('scroll', handleScroll)
    }
  }, [threshold, scrollContainer])

  const scrollToTop = () => {
    if (scrollContainer) {
      // Scroll container element
      const container =
        typeof scrollContainer === 'string'
          ? document.querySelector(scrollContainer)
          : scrollContainer

      if (container) {
        container.scrollTo({
          top: 0,
          behavior,
        })
      }
    } else {
      // Scroll window
      window.scrollTo({
        top: 0,
        behavior,
      })
    }
  }

  if (!isVisible) {
    return null
  }

  return (
    <button
      onClick={scrollToTop}
      className="fixed z-50 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg transition-all duration-300 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      style={{
        bottom,
        right,
      }}
      aria-label="Scroll to top"
      title="Back to top"
    >
      <svg
        className="h-6 w-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 10l7-7m0 0l7 7m-7-7v18"
        />
      </svg>
    </button>
  )
}
