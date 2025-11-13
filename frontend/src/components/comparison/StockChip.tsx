/**
 * StockChip Component
 * Displays a selected stock with remove button for comparison
 */

import { X } from 'lucide-react'

interface StockChipProps {
  /** Stock code */
  code: string
  /** Stock name */
  name: string
  /** Market (KOSPI/KOSDAQ) */
  market: 'KOSPI' | 'KOSDAQ'
  /** Remove handler */
  onRemove: (code: string) => void
  /** Optional className */
  className?: string
}

export function StockChip({
  code,
  name,
  market,
  onRemove,
  className = '',
}: StockChipProps) {
  return (
    <div
      className={`
        inline-flex items-center gap-2 px-3 py-2
        bg-blue-50 border border-blue-200 rounded-lg
        hover:bg-blue-100 transition-colors
        ${className}
      `}
    >
      <div className="flex flex-col min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-900">{code}</span>
          <span
            className={`
              text-xs px-1.5 py-0.5 rounded
              ${market === 'KOSPI' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}
            `}
          >
            {market}
          </span>
        </div>
        <span className="text-xs text-gray-600 truncate">{name}</span>
      </div>
      <button
        onClick={() => onRemove(code)}
        className="
          flex-shrink-0 p-1 rounded-full
          hover:bg-red-100 text-gray-500 hover:text-red-600
          transition-colors
        "
        aria-label={`Remove ${name}`}
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}
