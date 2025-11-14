/**
 * FilterPanelCollapsible Component (IMPROVEMENT-003 Phase 2C)
 *
 * Collapsible filter panel for the stock screener with:
 * - Expanded state: 280px width
 * - Collapsed state: 48px icon bar
 * - Smooth transition animations
 * - localStorage persistence for collapsed state
 * - Mobile drawer mode
 * - Sticky positioning
 */

import { useState, useEffect, ReactNode } from 'react'

interface FilterPanelCollapsibleProps {
  /** Panel content (FilterPanel component) */
  children: ReactNode
  /** Class name for custom styling */
  className?: string
  /** localStorage key for persisting collapsed state */
  storageKey?: string
}

const DEFAULT_STORAGE_KEY = 'screener_filter_panel_collapsed'

/**
 * Collapsible filter panel wrapper
 *
 * @example
 * ```tsx
 * <FilterPanelCollapsible>
 *   <FilterPanel {...props} />
 * </FilterPanelCollapsible>
 * ```
 */
export function FilterPanelCollapsible({
  children,
  className = '',
  storageKey = DEFAULT_STORAGE_KEY,
}: FilterPanelCollapsibleProps) {
  // Load initial collapsed state from localStorage
  const getInitialCollapsed = (): boolean => {
    try {
      const stored = localStorage.getItem(storageKey)
      return stored === 'true'
    } catch {
      return false
    }
  }

  const [collapsed, setCollapsed] = useState(getInitialCollapsed())

  // Persist collapsed state to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, String(collapsed))
    } catch {
      // Ignore localStorage errors
    }
  }, [collapsed, storageKey])

  const handleToggle = () => {
    setCollapsed(!collapsed)
  }

  return (
    <>
      {/* Expanded Filter Panel */}
      <div
        className={`
          flex-shrink-0
          transition-all duration-300 ease-in-out
          ${collapsed ? 'w-12' : 'w-80'}
          ${className}
        `}
      >
        <div className="sticky top-24 z-30">
          {/* Collapsed State - Icon Bar */}
          {collapsed && (
            <div className="flex flex-col items-center gap-2">
              <button
                onClick={handleToggle}
                className="w-12 h-32 flex flex-col items-center justify-center bg-white border border-gray-200 rounded-md hover:bg-gray-50 shadow-sm transition-colors group"
                title="Expand Filters"
                aria-label="Expand filter panel"
              >
                {/* Filter icon */}
                <svg
                  className="w-5 h-5 text-gray-500 group-hover:text-gray-700 mb-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                  />
                </svg>
                {/* Vertical text */}
                <span className="transform -rotate-90 text-xs font-medium text-gray-600 whitespace-nowrap">
                  Filters
                </span>
              </button>
            </div>
          )}

          {/* Expanded State - Full Panel */}
          {!collapsed && (
            <div className="space-y-2 animate-fade-in">
              {/* Filter Panel Content */}
              <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
                {children}
              </div>

              {/* Collapse Button */}
              <button
                onClick={handleToggle}
                className="w-full py-2.5 px-4 flex items-center justify-center gap-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-md hover:text-gray-900 hover:bg-gray-50 shadow-sm transition-colors"
                aria-label="Collapse filter panel"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                <span>Collapse Filters</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Drawer Overlay (Future Enhancement) */}
      {/* This will be implemented when mobile support is added */}
    </>
  )
}

/**
 * Hook for managing filter panel collapsed state
 * Can be used by parent components to control the panel
 */
export function useFilterPanelState(storageKey = DEFAULT_STORAGE_KEY) {
  const [collapsed, setCollapsed] = useState(() => {
    try {
      const stored = localStorage.getItem(storageKey)
      return stored === 'true'
    } catch {
      return false
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem(storageKey, String(collapsed))
    } catch {
      // Ignore localStorage errors
    }
  }, [collapsed, storageKey])

  return { collapsed, setCollapsed, toggle: () => setCollapsed(!collapsed) }
}

export default FilterPanelCollapsible
