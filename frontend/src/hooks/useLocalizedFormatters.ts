/**
 * Locale-aware formatting utilities hook
 *
 * Provides formatting functions for numbers, currencies, dates, and percentages
 * that respect the current i18n locale setting.
 */

import { useTranslation } from 'react-i18next'
import { useMemo } from 'react'

export interface LocalizedFormatters {
  /** Format a number with locale-specific separators */
  formatNumber: (num: number, options?: Intl.NumberFormatOptions) => string
  /** Format a number as Korean Won currency */
  formatCurrency: (num: number, currency?: string) => string
  /** Format a number as percentage */
  formatPercent: (num: number, fractionDigits?: number) => string
  /** Format a date with locale-specific format */
  formatDate: (date: Date | string | number, options?: Intl.DateTimeFormatOptions) => string
  /** Format a relative time (e.g., "3 hours ago") */
  formatRelativeTime: (date: Date | string | number) => string
  /** Format market cap with appropriate suffix (억, 조 / M, B, T) */
  formatMarketCap: (num: number) => string
  /** Format volume with commas */
  formatVolume: (num: number) => string
}

/**
 * Hook for locale-aware formatting utilities
 *
 * @example
 * ```tsx
 * const { formatCurrency, formatPercent } = useLocalizedFormatters()
 *
 * return (
 *   <div>
 *     <span>{formatCurrency(50000)}</span>
 *     <span>{formatPercent(0.0523)}</span>
 *   </div>
 * )
 * ```
 */
export function useLocalizedFormatters(): LocalizedFormatters {
  const { i18n } = useTranslation()
  const locale = i18n.language === 'ko' ? 'ko-KR' : 'en-US'

  return useMemo(() => {
    const formatNumber = (num: number, options?: Intl.NumberFormatOptions): string => {
      if (num === null || num === undefined || isNaN(num)) return '-'
      return new Intl.NumberFormat(locale, options).format(num)
    }

    const formatCurrency = (num: number, currency = 'KRW'): string => {
      if (num === null || num === undefined || isNaN(num)) return '-'

      // Korean locale uses different format
      if (locale === 'ko-KR') {
        return new Intl.NumberFormat('ko-KR', {
          style: 'currency',
          currency,
          maximumFractionDigits: 0,
        }).format(num)
      }

      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency,
        maximumFractionDigits: 0,
        currencyDisplay: 'narrowSymbol',
      }).format(num)
    }

    const formatPercent = (num: number, fractionDigits = 2): string => {
      if (num === null || num === undefined || isNaN(num)) return '-'

      // Input is already in percentage form (e.g., 5.23 for 5.23%)
      return new Intl.NumberFormat(locale, {
        style: 'percent',
        minimumFractionDigits: fractionDigits,
        maximumFractionDigits: fractionDigits,
      }).format(num / 100)
    }

    const formatDate = (
      date: Date | string | number,
      options?: Intl.DateTimeFormatOptions
    ): string => {
      const d = date instanceof Date ? date : new Date(date)
      if (isNaN(d.getTime())) return '-'

      const defaultOptions: Intl.DateTimeFormatOptions = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      }

      return new Intl.DateTimeFormat(locale, options || defaultOptions).format(d)
    }

    const formatRelativeTime = (date: Date | string | number): string => {
      const d = date instanceof Date ? date : new Date(date)
      if (isNaN(d.getTime())) return '-'

      const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })
      const diff = (d.getTime() - Date.now()) / 1000

      if (Math.abs(diff) < 60) return rtf.format(Math.round(diff), 'second')
      if (Math.abs(diff) < 3600) return rtf.format(Math.round(diff / 60), 'minute')
      if (Math.abs(diff) < 86400) return rtf.format(Math.round(diff / 3600), 'hour')
      if (Math.abs(diff) < 2592000) return rtf.format(Math.round(diff / 86400), 'day')
      return rtf.format(Math.round(diff / 2592000), 'month')
    }

    const formatMarketCap = (num: number): string => {
      if (num === null || num === undefined || isNaN(num)) return '-'

      // Input is in billion KRW
      if (locale === 'ko-KR') {
        if (num >= 10000) {
          // 조 (trillion won)
          return `${(num / 10000).toFixed(1)}조`
        }
        // 억 (hundred million won)
        return `${num.toLocaleString('ko-KR')}억`
      }

      // English locale - convert to USD approximation or keep in KRW
      if (num >= 10000) {
        return `${(num / 10000).toFixed(1)}T KRW`
      }
      if (num >= 1) {
        return `${num.toLocaleString('en-US')}B KRW`
      }
      return `${(num * 1000).toLocaleString('en-US')}M KRW`
    }

    const formatVolume = (num: number): string => {
      if (num === null || num === undefined || isNaN(num)) return '-'
      return new Intl.NumberFormat(locale).format(num)
    }

    return {
      formatNumber,
      formatCurrency,
      formatPercent,
      formatDate,
      formatRelativeTime,
      formatMarketCap,
      formatVolume,
    }
  }, [locale])
}

export default useLocalizedFormatters
