import { useState, useEffect, useRef } from 'react'

/**
 * Props for SearchBar component
 */
interface SearchBarProps {
  /** Current search query value */
  value: string
  /** Callback when search query changes */
  onChange: (value: string) => void
  /** Placeholder text */
  placeholder?: string
  /** Whether to enable keyboard shortcut (Ctrl+K) */
  enableShortcut?: boolean
}

/**
 * SearchBar component with keyboard shortcut support
 *
 * Features:
 * - Debounced search input
 * - Keyboard shortcut (Ctrl+K / Cmd+K)
 * - Clear button
 * - Loading indicator (optional)
 * - Accessible with proper ARIA labels
 */
export default function SearchBar({
  value,
  onChange,
  placeholder = 'Search by stock code or name (e.g., 005930 or Samsung)',
  enableShortcut = true,
}: SearchBarProps) {
  const [localValue, setLocalValue] = useState(value)
  const inputRef = useRef<HTMLInputElement>(null)

  // Sync local value with prop value
  useEffect(() => {
    setLocalValue(value)
  }, [value])

  // Debounce onChange callback (300ms)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue)
      }
    }, 300)

    return () => clearTimeout(timeoutId)
  }, [localValue, value, onChange])

  // Keyboard shortcut: Ctrl+K or Cmd+K to focus search
  useEffect(() => {
    if (!enableShortcut) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [enableShortcut])

  const handleClear = () => {
    setLocalValue('')
    onChange('')
    inputRef.current?.focus()
  }

  return (
    <div className="relative">
      {/* Search Icon */}
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <svg
          className="h-5 w-5 text-gray-400 dark:text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Input */}
      <input
        ref={inputRef}
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder}
        className="block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 py-2 pl-10 pr-20 text-sm shadow-sm placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors"
        aria-label="Search stocks"
      />

      {/* Right side controls */}
      <div className="absolute inset-y-0 right-0 flex items-center pr-2 space-x-1">
        {/* Clear button */}
        {localValue && (
          <button
            type="button"
            onClick={handleClear}
            className="rounded-md p-1 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            aria-label="Clear search"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}

        {/* Keyboard shortcut hint */}
        {enableShortcut && !localValue && (
          <div className="hidden sm:flex items-center space-x-1 text-xs text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-700 rounded px-1.5 py-0.5">
            <kbd className="font-sans">⌘K</kbd>
          </div>
        )}
      </div>
    </div>
  )
}
