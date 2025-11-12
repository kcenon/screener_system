import { useState, useEffect } from 'react'
import type { FilterRange } from '@/types/screening'

/**
 * Props for RangeFilter component
 */
interface RangeFilterProps {
  /** Display label for the filter */
  label: string
  /** Current filter range value */
  value?: FilterRange | null
  /** Callback when range value changes */
  onChange: (range: FilterRange | null) => void
  /** Placeholder text for min input */
  minPlaceholder?: string
  /** Placeholder text for max input */
  maxPlaceholder?: string
  /** Unit to display (e.g., "%", "KRW") */
  unit?: string
}

/**
 * RangeFilter component for min/max numeric inputs with validation
 *
 * Features:
 * - Side-by-side min/max inputs
 * - Validation: `min <= max`
 * - Clears filter when both inputs are empty
 * - Shows validation error for invalid ranges
 */
export default function RangeFilter({
  label,
  value,
  onChange,
  minPlaceholder = 'Min',
  maxPlaceholder = 'Max',
  unit,
}: RangeFilterProps) {
  const [minValue, setMinValue] = useState<string>(value?.min?.toString() || '')
  const [maxValue, setMaxValue] = useState<string>(value?.max?.toString() || '')
  const [error, setError] = useState<string>('')

  // Sync with external value changes
  useEffect(() => {
    setMinValue(value?.min?.toString() || '')
    setMaxValue(value?.max?.toString() || '')
  }, [value])

  // Validate and emit change
  const handleChange = (newMin: string, newMax: string) => {
    const min = newMin ? parseFloat(newMin) : null
    const max = newMax ? parseFloat(newMax) : null

    // Validate range
    if (min !== null && max !== null && min > max) {
      setError('Min cannot be greater than max')
      return
    }

    setError('')

    // Clear filter if both are empty
    if (min === null && max === null) {
      onChange(null)
      return
    }

    // Emit valid range
    onChange({ min, max })
  }

  const handleMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setMinValue(newValue)
    handleChange(newValue, maxValue)
  }

  const handleMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setMaxValue(newValue)
    handleChange(minValue, newValue)
  }

  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {unit && <span className="ml-1 text-gray-500">({unit})</span>}
      </label>
      <div className="flex items-center space-x-2">
        <input
          type="number"
          value={minValue}
          onChange={handleMinChange}
          placeholder={minPlaceholder}
          className={`block w-full rounded-md border ${
            error ? 'border-red-300' : 'border-gray-300'
          } px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500`}
        />
        <span className="text-gray-500">—</span>
        <input
          type="number"
          value={maxValue}
          onChange={handleMaxChange}
          placeholder={maxPlaceholder}
          className={`block w-full rounded-md border ${
            error ? 'border-red-300' : 'border-gray-300'
          } px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500`}
        />
      </div>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  )
}
