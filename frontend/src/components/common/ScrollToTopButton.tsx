/**
 * Scroll to Top FAB (Floating Action Button)
 *
 * Features:
 * - Appears after scrolling 200px down
 * - Smooth scroll animation to top
 * - Fixed position bottom-right
 * - Accessible with keyboard
 */

import { useState, useEffect } from 'react'
import { ChevronUp } from 'lucide-react'

interface ScrollToTopButtonProps {
  /** Scroll threshold in pixels (default: 200) */
  threshold?: number
  /** Additional className for custom styling */
  className?: string
}

export function ScrollToTopButton({ threshold = 200, className = '' }: ScrollToTopButtonProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsVisible(window.scrollY > threshold)
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // Check initial state
    return () => window.removeEventListener('scroll', handleScroll)
  }, [threshold])

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  if (!isVisible) {
    return null
  }

  return (
    <button
      onClick={scrollToTop}
      className={`fixed bottom-6 right-6 z-50 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 hover:shadow-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${className}`}
      aria-label="Scroll to top"
      title="Scroll to top"
    >
      <ChevronUp className="h-6 w-6" />
    </button>
  )
}

export default ScrollToTopButton
