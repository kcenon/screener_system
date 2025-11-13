/**
 * StockSelector Component
 * Autocomplete search for adding stocks to comparison
 */

import { useState, useRef, useEffect } from 'react'
import { Search, Plus } from 'lucide-react'
import { stockService } from '../../services/stockService'
import type { Stock } from '../../types'

interface StockSelectorProps {
  /** Already selected stock codes */
  selectedCodes: string[]
  /** Add stock handler */
  onAddStock: (code: string) => void
  /** Maximum stocks allowed */
  maxStocks: number
  /** Optional className */
  className?: string
}

export function StockSelector({
  selectedCodes,
  onAddStock,
  maxStocks,
  className = '',
}: StockSelectorProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Stock[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const isMaxReached = selectedCodes.length >= maxStocks

  // Search stocks
  useEffect(() => {
    const searchStocks = async () => {
      if (query.length < 2) {
        setResults([])
        setIsOpen(false)
        return
      }

      setIsLoading(true)
      try {
        const response = await stockService.listStocks(undefined, 0, 20)
        // Filter by query (code or name)
        const filtered = response.data.filter(
          (stock) =>
            stock.code.toLowerCase().includes(query.toLowerCase()) ||
            stock.name.toLowerCase().includes(query.toLowerCase())
        )
        setResults(filtered)
        setIsOpen(filtered.length > 0)
      } catch (error) {
        console.error('Stock search error:', error)
        setResults([])
      } finally {
        setIsLoading(false)
      }
    }

    const debounce = setTimeout(searchStocks, 300)
    return () => clearTimeout(debounce)
  }, [query])

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((prev) =>
          prev < results.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : prev))
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0 && selectedIndex < results.length) {
          handleSelectStock(results[selectedIndex].code)
        }
        break
      case 'Escape':
        setIsOpen(false)
        setSelectedIndex(-1)
        break
    }
  }

  const handleSelectStock = (code: string) => {
    if (!selectedCodes.includes(code) && !isMaxReached) {
      onAddStock(code)
      setQuery('')
      setResults([])
      setIsOpen(false)
      setSelectedIndex(-1)
      inputRef.current?.focus()
    }
  }

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length >= 2 && setIsOpen(results.length > 0)}
          placeholder={
            isMaxReached
              ? `Maximum ${maxStocks} stocks reached`
              : 'Search stocks by code or name...'
          }
          disabled={isMaxReached}
          className={`
            w-full pl-10 pr-4 py-2.5
            border border-gray-300 rounded-lg
            focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            disabled:bg-gray-100 disabled:cursor-not-allowed
            transition-all
          `}
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500" />
          </div>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && results.length > 0 && (
        <div
          ref={dropdownRef}
          className="
            absolute z-10 w-full mt-2
            bg-white border border-gray-200 rounded-lg shadow-lg
            max-h-80 overflow-y-auto
          "
        >
          {results.map((stock, index) => {
            const isAlreadySelected = selectedCodes.includes(stock.code)
            const isHighlighted = index === selectedIndex

            return (
              <button
                key={stock.code}
                onClick={() => !isAlreadySelected && handleSelectStock(stock.code)}
                disabled={isAlreadySelected}
                className={`
                  w-full px-4 py-3 text-left
                  hover:bg-gray-50
                  disabled:bg-gray-100 disabled:cursor-not-allowed
                  border-b border-gray-100 last:border-b-0
                  ${isHighlighted ? 'bg-blue-50' : ''}
                  transition-colors
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-900">
                        {stock.code}
                      </span>
                      <span
                        className={`
                          text-xs px-2 py-0.5 rounded
                          ${stock.market === 'KOSPI' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}
                        `}
                      >
                        {stock.market}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 truncate">
                      {stock.name}
                    </p>
                  </div>
                  {isAlreadySelected ? (
                    <span className="text-xs text-gray-500 ml-2">
                      Already added
                    </span>
                  ) : (
                    <Plus className="w-5 h-5 text-gray-400 ml-2" />
                  )}
                </div>
              </button>
            )
          })}
        </div>
      )}

      {/* No Results */}
      {isOpen && results.length === 0 && query.length >= 2 && !isLoading && (
        <div
          ref={dropdownRef}
          className="
            absolute z-10 w-full mt-2
            bg-white border border-gray-200 rounded-lg shadow-lg
            px-4 py-6 text-center
          "
        >
          <p className="text-gray-500">No stocks found for "{query}"</p>
        </div>
      )}
    </div>
  )
}
