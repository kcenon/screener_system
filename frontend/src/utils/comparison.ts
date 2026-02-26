/**
 * Comparison utility functions
 */

import type { ComparisonStock, MetricHighlight } from '../types/comparison'

/**
 * Get value from stock by metric key
 */
export function getMetricValue(
  stock: ComparisonStock,
  metricKey: string,
): number | null {
  // Handle nested properties
  const value = (stock as any)[metricKey]

  if (value === undefined || value === null) {
    return null
  }

  // Convert to number if string
  if (typeof value === 'string') {
    const parsed = parseFloat(value)
    return isNaN(parsed) ? null : parsed
  }

  return typeof value === 'number' ? value : null
}

/**
 * Highlight best and worst values for a metric across stocks
 */
export function highlightBestWorst(
  values: (number | null)[],
  higherIsBetter: boolean,
): MetricHighlight[] {
  // Filter out null values for comparison
  const validValues = values
    .map((v, i) => ({ value: v, index: i }))
    .filter(v => v.value !== null) as { value: number; index: number }[]

  if (validValues.length === 0) {
    return values.map(() => 'neutral')
  }

  // Find best and worst
  const sorted = [...validValues].sort((a, b) =>
    higherIsBetter ? b.value - a.value : a.value - b.value,
  )

  const bestIndex = sorted[0]?.index
  const worstIndex = sorted[sorted.length - 1]?.index

  // Only highlight if there are differences
  const hasVariation = sorted[0]?.value !== sorted[sorted.length - 1]?.value

  return values.map((v, i) => {
    if (v === null || !hasVariation) {
      return 'neutral'
    }
    if (i === bestIndex) {
      return 'best'
    }
    if (i === worstIndex && validValues.length > 2) {
      return 'worst'
    }
    return 'neutral'
  })
}

/**
 * Format number based on format type
 */
export function formatMetricValue(
  value: number | null,
  format: 'currency' | 'percent' | 'number' | 'ratio',
): string {
  if (value === null || value === undefined) {
    return 'N/A'
  }

  switch (format) {
    case 'currency':
      // Format as KRW (Korean Won)
      if (value >= 1_000_000_000_000) {
        return `₩${(value / 1_000_000_000_000).toFixed(2)}T`
      }
      if (value >= 1_000_000_000) {
        return `₩${(value / 1_000_000_000).toFixed(2)}B`
      }
      if (value >= 1_000_000) {
        return `₩${(value / 1_000_000).toFixed(2)}M`
      }
      if (value >= 1_000) {
        return `₩${(value / 1_000).toFixed(2)}K`
      }
      return `₩${value.toLocaleString()}`

    case 'percent':
      return `${value.toFixed(2)}%`

    case 'ratio':
      return value.toFixed(2)

    case 'number':
      if (value >= 1_000_000_000) {
        return `${(value / 1_000_000_000).toFixed(2)}B`
      }
      if (value >= 1_000_000) {
        return `${(value / 1_000_000).toFixed(2)}M`
      }
      if (value >= 1_000) {
        return `${(value / 1_000).toFixed(2)}K`
      }
      return value.toLocaleString()

    default:
      return String(value)
  }
}

/**
 * Get highlight color classes
 */
export function getHighlightClass(highlight: MetricHighlight): string {
  switch (highlight) {
    case 'best':
      return 'bg-green-50 text-green-900 font-semibold'
    case 'worst':
      return 'bg-red-50 text-red-900'
    case 'neutral':
    default:
      return ''
  }
}

/**
 * Export comparison data to CSV
 */
export function exportToCSV(
  stocks: ComparisonStock[],
  metricKeys: string[],
): Blob {
  // Header row
  const headers = ['Metric', ...stocks.map(s => `${s.code} (${s.name})`)]

  // Data rows
  const rows = metricKeys.map(key => {
    const label = key.replace(/_/g, ' ').toUpperCase()
    const values = stocks.map(stock => {
      const value = getMetricValue(stock, key)
      return value !== null ? value : 'N/A'
    })
    return [label, ...values]
  })

  // Convert to CSV string
  const csvContent = [headers, ...rows]
    .map(row => row.map(cell => `"${cell}"`).join(','))
    .join('\n')

  return new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
}

/**
 * Download blob as file
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
