/**
 * Compact Number Formatting Utilities
 *
 * Functions for displaying numbers in compact, space-efficient formats
 * suitable for tables and compact UI components.
 */

/**
 * Format number in compact international notation
 *
 * Converts large numbers to K/M/B/T notation
 *
 * @param num - Number to format
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted string
 *
 * @example
 * formatCompactNumber(1500) // "1.5K"
 * formatCompactNumber(2500000) // "2.5M"
 * formatCompactNumber(1234567890) // "1.2B"
 */
export function formatCompactNumber(num: number | null | undefined, decimals: number = 1): string {
  if (num === null || num === undefined || isNaN(num)) {
    return '-'
  }

  const absNum = Math.abs(num)
  const sign = num < 0 ? '-' : ''

  if (absNum >= 1e12) {
    return `${sign}${(absNum / 1e12).toFixed(decimals)}T`
  }
  if (absNum >= 1e9) {
    return `${sign}${(absNum / 1e9).toFixed(decimals)}B`
  }
  if (absNum >= 1e6) {
    return `${sign}${(absNum / 1e6).toFixed(decimals)}M`
  }
  if (absNum >= 1e3) {
    return `${sign}${(absNum / 1e3).toFixed(decimals)}K`
  }

  return num.toString()
}

/**
 * Format number in compact Korean notation
 *
 * Converts large numbers to Korean units (만, 억, 조)
 *
 * @param num - Number to format
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted string
 *
 * @example
 * formatCompactKoreanNumber(15000) // "1.5만"
 * formatCompactKoreanNumber(250000000) // "2.5억"
 * formatCompactKoreanNumber(1234567890000) // "1.2조"
 */
export function formatCompactKoreanNumber(
  num: number | null | undefined,
  decimals: number = 1
): string {
  if (num === null || num === undefined || isNaN(num)) {
    return '-'
  }

  const absNum = Math.abs(num)
  const sign = num < 0 ? '-' : ''

  // 조 (trillion, 10^12)
  if (absNum >= 1e12) {
    return `${sign}${(absNum / 1e12).toFixed(decimals)}조`
  }
  // 억 (hundred million, 10^8)
  if (absNum >= 1e8) {
    return `${sign}${(absNum / 1e8).toFixed(decimals)}억`
  }
  // 만 (ten thousand, 10^4)
  if (absNum >= 1e4) {
    return `${sign}${(absNum / 1e4).toFixed(decimals)}만`
  }

  return num.toLocaleString('ko-KR')
}

/**
 * Format volume in compact notation
 *
 * Optimized for trading volume display
 *
 * @param volume - Volume value
 * @returns Formatted volume string
 *
 * @example
 * formatCompactVolume(1234567) // "1.2M"
 * formatCompactVolume(54321) // "54.3K"
 */
export function formatCompactVolume(volume: number | null | undefined): string {
  return formatCompactNumber(volume, 1)
}

/**
 * Format market cap in compact Korean notation
 *
 * Specialized for market capitalization display
 *
 * @param marketCap - Market cap value in KRW
 * @returns Formatted market cap string
 *
 * @example
 * formatCompactMarketCap(425000000000000) // "425조"
 * formatCompactMarketCap(15000000000) // "150억"
 */
export function formatCompactMarketCap(marketCap: number | null | undefined): string {
  if (marketCap === null || marketCap === undefined || isNaN(marketCap)) {
    return '-'
  }

  const absNum = Math.abs(marketCap)
  const sign = marketCap < 0 ? '-' : ''

  // 조 (trillion)
  if (absNum >= 1e12) {
    return `${sign}${(absNum / 1e12).toFixed(0)}조`
  }
  // 억 (hundred million)
  if (absNum >= 1e8) {
    return `${sign}${(absNum / 1e8).toFixed(0)}억`
  }
  // 만 (ten thousand)
  if (absNum >= 1e4) {
    return `${sign}${(absNum / 1e4).toFixed(0)}만`
  }

  return marketCap.toLocaleString('ko-KR')
}

/**
 * Format change percentage with sign
 *
 * Adds + sign for positive values, preserves - for negative
 *
 * @param percent - Percentage value
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted percentage string
 *
 * @example
 * formatChangePercentage(5.234) // "+5.23%"
 * formatChangePercentage(-2.5) // "-2.50%"
 * formatChangePercentage(0) // "0.00%"
 */
export function formatChangePercentage(
  percent: number | null | undefined,
  decimals: number = 2
): string {
  if (percent === null || percent === undefined || isNaN(percent)) {
    return '-'
  }

  const sign = percent > 0 ? '+' : ''
  return `${sign}${percent.toFixed(decimals)}%`
}

/**
 * Format price with appropriate precision
 *
 * Automatically adjusts decimal places based on price magnitude
 *
 * @param price - Stock price
 * @returns Formatted price string
 *
 * @example
 * formatCompactPrice(71000) // "71,000"
 * formatCompactPrice(1250.5) // "1,250.5"
 * formatCompactPrice(125.75) // "125.75"
 */
export function formatCompactPrice(price: number | null | undefined): string {
  if (price === null || price === undefined || isNaN(price)) {
    return '-'
  }

  // Determine decimal places based on price magnitude
  let decimals = 0
  if (price < 1000) {
    decimals = 2
  } else if (price < 10000) {
    decimals = 1
  }

  return price.toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

/**
 * Format table number based on type
 *
 * Unified formatter for table cells with type-specific formatting
 *
 * @param num - Number to format
 * @param type - Type of number ('price' | 'volume' | 'marketcap' | 'percent')
 * @returns Formatted string
 *
 * @example
 * formatTableNumber(71000, 'price') // "71,000"
 * formatTableNumber(1234567, 'volume') // "1.2M"
 * formatTableNumber(425000000000000, 'marketcap') // "425조"
 * formatTableNumber(5.23, 'percent') // "+5.23%"
 */
export function formatTableNumber(
  num: number | null | undefined,
  type: 'price' | 'volume' | 'marketcap' | 'percent'
): string {
  if (num === null || num === undefined || isNaN(num)) {
    return '-'
  }

  switch (type) {
    case 'price':
      return formatCompactPrice(num)

    case 'volume':
      return formatCompactVolume(num)

    case 'marketcap':
      return formatCompactMarketCap(num)

    case 'percent':
      return formatChangePercentage(num)

    default:
      return num.toString()
  }
}

/**
 * Format number with intelligent unit selection
 *
 * Automatically chooses between international (K/M/B) and Korean (만/억/조)
 * based on context
 *
 * @param num - Number to format
 * @param preferKorean - Prefer Korean units (default: true)
 * @returns Formatted string
 *
 * @example
 * formatIntelligentNumber(1500000, true) // "150만"
 * formatIntelligentNumber(1500000, false) // "1.5M"
 */
export function formatIntelligentNumber(
  num: number | null | undefined,
  preferKorean: boolean = true
): string {
  if (num === null || num === undefined || isNaN(num)) {
    return '-'
  }

  return preferKorean ? formatCompactKoreanNumber(num) : formatCompactNumber(num)
}
