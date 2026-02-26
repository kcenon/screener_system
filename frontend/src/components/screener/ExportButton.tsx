import { useState } from 'react'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { exportStocks, type ExportFormat } from '@/utils/exportUtils'
import type { StockScreeningResult } from '@/types/screening'

/**
 * Props for ExportButton component
 */
interface ExportButtonProps {
  /** Data to export */
  data: StockScreeningResult[]
  /** Whether export is disabled */
  disabled?: boolean
  /** Custom filename (without extension) */
  filename?: string
}

/**
 * ExportButton component with dropdown menu for export formats
 *
 * Features:
 * - Export to CSV
 * - Export to JSON
 * - Dropdown menu for format selection
 * - Disabled state when no data
 */
export default function ExportButton({
  data,
  disabled = false,
  filename,
}: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false)

  const handleExport = (format: ExportFormat) => {
    try {
      exportStocks(data, format, filename)
      setIsOpen(false)
    } catch (error) {
      console.error('Export failed:', error)
      alert('Failed to export data. Please try again.')
    }
  }

  const isDisabled = disabled || data.length === 0

  return (
    <DropdownMenu.Root open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenu.Trigger asChild>
        <button
          disabled={isDisabled}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg
            className="h-4 w-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          Export
          <svg
            className="h-4 w-4 ml-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="min-w-[180px] bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 p-1 z-50 transition-colors"
          sideOffset={5}
        >
          <DropdownMenu.Item
            className="flex items-center px-3 py-2 text-sm text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer outline-none transition-colors"
            onSelect={() => handleExport('csv')}
          >
            <svg
              className="h-4 w-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Export as CSV
          </DropdownMenu.Item>

          <DropdownMenu.Item
            className="flex items-center px-3 py-2 text-sm text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer outline-none transition-colors"
            onSelect={() => handleExport('json')}
          >
            <svg
              className="h-4 w-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
              />
            </svg>
            Export as JSON
          </DropdownMenu.Item>

          <DropdownMenu.Separator className="h-px bg-gray-200 dark:bg-gray-700 my-1" />

          <div className="px-3 py-2 text-xs text-gray-500 dark:text-gray-400">
            {data.length} {data.length === 1 ? 'stock' : 'stocks'}
          </div>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
