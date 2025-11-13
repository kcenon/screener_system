/**
 * MetricTooltip Component
 * Displays metric definition on hover
 */

import { HelpCircle } from 'lucide-react'
import { useState } from 'react'

interface MetricTooltipProps {
  /** Metric description */
  description: string
  /** Optional className */
  className?: string
}

export function MetricTooltip({ description, className = '' }: MetricTooltipProps) {
  const [isVisible, setIsVisible] = useState(false)

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        type="button"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
        className="text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Metric information"
      >
        <HelpCircle className="w-4 h-4" />
      </button>

      {isVisible && (
        <div
          className="
            absolute z-10 left-1/2 transform -translate-x-1/2 bottom-full mb-2
            w-64 px-3 py-2
            bg-gray-900 text-white text-sm rounded-lg
            shadow-lg
            pointer-events-none
          "
        >
          {description}
          {/* Arrow */}
          <div
            className="
              absolute top-full left-1/2 transform -translate-x-1/2
              border-4 border-transparent border-t-gray-900
            "
          />
        </div>
      )}
    </div>
  )
}
