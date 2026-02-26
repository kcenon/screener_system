import { useEffect, useRef } from 'react'
import { Search, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useGlobalSearch } from '@/hooks/useGlobalSearch'
import { useKeyboardShortcut } from '@/hooks/useKeyboardShortcut'

export default function GlobalSearch() {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)
  const {
    query,
    setQuery,
    results,
    isLoading,
    isOpen,
    setIsOpen,
    clearSearch,
  } = useGlobalSearch()

  useKeyboardShortcut(
    'k',
    () => {
      setIsOpen(true)
      inputRef.current?.focus()
    },
    ['cmd', 'ctrl'],
  )

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus()
    }
  }, [isOpen])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('.global-search-container')) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, setIsOpen])

  const handleSelectStock = (code: string) => {
    navigate(`/stocks/${code}`)
    clearSearch()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      clearSearch()
    }
  }

  return (
    <div className="relative global-search-container">
      {/* Search Input */}
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <Search size={18} />
        </div>
        <input
          ref={inputRef}
          type="text"
          placeholder="Search stocks... (Cmd+K)"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          className="w-full md:w-64 pl-10 pr-10 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {query && (
          <button
            onClick={clearSearch}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            aria-label="Clear search"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && query.length >= 2 && (
        <div className="absolute top-full mt-2 w-full md:w-96 bg-white border border-gray-200 rounded-md shadow-lg z-50 max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-sm text-gray-500">
              Searching...
            </div>
          ) : results.length > 0 ? (
            <ul className="py-2">
              {results.map(stock => (
                <li key={stock.code}>
                  <button
                    onClick={() => handleSelectStock(stock.code)}
                    className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {stock.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {stock.code} • {stock.market}
                        </p>
                      </div>
                      {stock.current_price && (
                        <p className="text-sm font-medium text-gray-700">
                          ₩{stock.current_price.toLocaleString()}
                        </p>
                      )}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-4 text-center text-sm text-gray-500">
              No stocks found for "{query}"
            </div>
          )}
        </div>
      )}
    </div>
  )
}
