/**
 * Formatting Utility Functions
 *
 * Number and currency formatting helpers
 */

/**
 * Format number with thousand separators
 *
 * @param value - Number to format
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted string
 *
 * @example
 * formatNumber(1234567) // "1,234,567"
 * formatNumber(1234.567, 2) // "1,234.57"
 */
export function formatNumber(
  value: number | null | undefined,
  decimals: number = 0,
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-'
  }

  return value.toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

/**
 * Format price (stock price) with appropriate decimal places
 *
 * @param value - Price to format
 * @returns Formatted price string
 *
 * @example
 * formatPrice(55000) // "55,000"
 * formatPrice(1250.5) // "1,250.5"
 */
export function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-'
  }

  // Determine decimal places based on price magnitude
  let decimals = 0
  if (value < 1000) {
    decimals = 2
  } else if (value < 10000) {
    decimals = 1
  }

  return value.toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

/**
 * Format currency in KRW
 *
 * @param value - Amount in KRW
 * @param compact - Use compact notation for large numbers (default: false)
 * @returns Formatted currency string
 *
 * @example
 * formatCurrency(1000000) // "₩1,000,000"
 * formatCurrency(1000000, true) // "₩1.0M"
 */
export function formatCurrency(
  value: number | null | undefined,
  compact: boolean = false,
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-'
  }

  if (compact) {
    if (value >= 1_000_000_000_000) {
      return `₩${(value / 1_000_000_000_000).toFixed(1)}T`
    } else if (value >= 1_000_000_000) {
      return `₩${(value / 1_000_000_000).toFixed(1)}B`
    } else if (value >= 1_000_000) {
      return `₩${(value / 1_000_000).toFixed(1)}M`
    } else if (value >= 1_000) {
      return `₩${(value / 1_000).toFixed(1)}K`
    }
  }

  return `₩${value.toLocaleString('ko-KR')}`
}

/**
 * Format percentage
 *
 * @param value - Percentage value (0-100 or 0-1 based on asDecimal)
 * @param decimals - Number of decimal places (default: 2)
 * @param asDecimal - Whether input is decimal (0-1) vs percentage (0-100) (default: false)
 * @param showSign - Show + sign for positive values (default: true)
 * @returns Formatted percentage string
 *
 * @example
 * formatPercentage(12.34) // "+12.34%"
 * formatPercentage(-5.67) // "-5.67%"
 * formatPercentage(0.1234, 2, true) // "+12.34%"
 */
export function formatPercentage(
  value: number | null | undefined,
  decimals: number = 2,
  asDecimal: boolean = false,
  showSign: boolean = true,
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-'
  }

  const pctValue = asDecimal ? value * 100 : value
  const sign = showSign && pctValue > 0 ? '+' : ''

  return `${sign}${pctValue.toFixed(decimals)}%`
}

/**
 * Format market cap in Korean units (억원, 조원)
 *
 * @param value - Market cap in KRW
 * @returns Formatted market cap string
 *
 * @example
 * formatMarketCap(1234567890000) // "1.23조원"
 * formatMarketCap(123456789000) // "1,235억원"
 */
export function formatMarketCap(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-'
  }

  // 조원 (trillion)
  if (value >= 1_000_000_000_000) {
    const trillions = value / 1_000_000_000_000
    return `${trillions.toFixed(2)}조원`
  }

  // 억원 (hundred million)
  if (value >= 100_000_000) {
    const hundredMillions = value / 100_000_000
    return `${hundredMillions.toLocaleString('ko-KR', { maximumFractionDigits: 0 })}억원`
  }

  // 백만원 (million)
  if (value >= 1_000_000) {
    const millions = value / 1_000_000
    return `${millions.toFixed(1)}백만원`
  }

  return `${value.toLocaleString('ko-KR')}원`
}

/**
 * Format date
 *
 * @param date - Date string or Date object
 * @param format - Format type ('short', 'medium', 'long')
 * @returns Formatted date string
 *
 * @example
 * formatDate('2024-01-15') // "2024-01-15"
 * formatDate('2024-01-15', 'medium') // "2024년 1월 15일"
 */
export function formatDate(
  date: string | Date | null | undefined,
  format: 'short' | 'medium' | 'long' = 'short',
): string {
  if (!date) {
    return '-'
  }

  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) {
    return '-'
  }

  switch (format) {
    case 'short':
      return d.toISOString().split('T')[0]

    case 'medium':
      return d.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })

    case 'long':
      return d.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
      })

    default:
      return d.toISOString().split('T')[0]
  }
}

/**
 * Format change value with color indicator
 *
 * @param value - Change value
 * @param formatFn - Formatting function to apply (default: formatNumber)
 * @returns Object with formatted value and color class
 *
 * @example
 * const { text, className } = formatChange(1234)
 * // { text: "+1,234", className: "text-green-600" }
 */
export function formatChange(
  value: number | null | undefined,
  formatFn: (v: number) => string = formatNumber,
): { text: string; className: string } {
  if (value === null || value === undefined || isNaN(value)) {
    return { text: '-', className: 'text-gray-500' }
  }

  const sign = value > 0 ? '+' : ''
  const text = `${sign}${formatFn(value)}`

  let className = 'text-gray-500'
  if (value > 0) {
    className = 'text-green-600' // Green for positive (international standard)
  } else if (value < 0) {
    className = 'text-red-600' // Red for negative (international standard)
  }

  return { text, className }
}
