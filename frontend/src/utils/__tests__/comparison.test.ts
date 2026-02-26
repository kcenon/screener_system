/**
 * Comparison utility functions tests
 */

import { describe, it, expect } from 'vitest'
import {
  getMetricValue,
  highlightBestWorst,
  formatMetricValue,
  getHighlightClass,
  exportToCSV,
} from '../comparison'
import type { ComparisonStock } from '../../types/comparison'

describe('Comparison Utilities', () => {
  describe('getMetricValue', () => {
    it('should extract number value from stock', () => {
      const stock = {
        code: '005930',
        name: 'Samsung',
        current_price: 75000,
      } as ComparisonStock

      expect(getMetricValue(stock, 'current_price')).toBe(75000)
    })

    it('should return null for missing value', () => {
      const stock = {
        code: '005930',
        name: 'Samsung',
      } as ComparisonStock

      expect(getMetricValue(stock, 'nonexistent')).toBeNull()
    })

    it('should parse string numbers', () => {
      const stock = {
        code: '005930',
        name: 'Samsung',
        per: '12.5',
      } as any

      expect(getMetricValue(stock, 'per')).toBe(12.5)
    })

    it('should return null for invalid string', () => {
      const stock = {
        code: '005930',
        name: 'Samsung',
        invalid: 'not a number',
      } as any

      expect(getMetricValue(stock, 'invalid')).toBeNull()
    })
  })

  describe('highlightBestWorst', () => {
    it('should highlight best when higher is better', () => {
      const values = [10, 20, 15, null]
      const highlights = highlightBestWorst(values, true)

      expect(highlights[0]).toBe('worst') // lowest of 3 valid values
      expect(highlights[1]).toBe('best') // highest
      expect(highlights[2]).toBe('neutral')
      expect(highlights[3]).toBe('neutral') // null is neutral
    })

    it('should highlight worst when higher is better and >2 stocks', () => {
      const values = [10, 20, 15]
      const highlights = highlightBestWorst(values, true)

      expect(highlights[0]).toBe('worst') // lowest
      expect(highlights[1]).toBe('best') // highest
      expect(highlights[2]).toBe('neutral')
    })

    it('should highlight best when lower is better', () => {
      const values = [10, 20, 15]
      const highlights = highlightBestWorst(values, false)

      expect(highlights[0]).toBe('best') // lowest
      expect(highlights[1]).toBe('worst') // highest
      expect(highlights[2]).toBe('neutral')
    })

    it('should return neutral for all same values', () => {
      const values = [10, 10, 10]
      const highlights = highlightBestWorst(values, true)

      expect(highlights.every(h => h === 'neutral')).toBe(true)
    })

    it('should handle all null values', () => {
      const values = [null, null, null]
      const highlights = highlightBestWorst(values, true)

      expect(highlights.every(h => h === 'neutral')).toBe(true)
    })

    it('should ignore null values in comparison', () => {
      const values = [10, null, 20, null, 15]
      const highlights = highlightBestWorst(values, true)

      expect(highlights[0]).toBe('worst')
      expect(highlights[1]).toBe('neutral')
      expect(highlights[2]).toBe('best')
      expect(highlights[3]).toBe('neutral')
      expect(highlights[4]).toBe('neutral')
    })
  })

  describe('formatMetricValue', () => {
    it('should format null as N/A', () => {
      expect(formatMetricValue(null, 'currency')).toBe('N/A')
      expect(formatMetricValue(undefined as any, 'currency')).toBe('N/A')
    })

    it('should format currency values', () => {
      expect(formatMetricValue(75000, 'currency')).toBe('₩75.00K')
      expect(formatMetricValue(1_500_000, 'currency')).toBe('₩1.50M')
      expect(formatMetricValue(2_500_000_000, 'currency')).toBe('₩2.50B')
      expect(formatMetricValue(3_500_000_000_000, 'currency')).toBe('₩3.50T')
    })

    it('should format percent values', () => {
      expect(formatMetricValue(12.5, 'percent')).toBe('12.50%')
      expect(formatMetricValue(-5.25, 'percent')).toBe('-5.25%')
      expect(formatMetricValue(0, 'percent')).toBe('0.00%')
    })

    it('should format ratio values', () => {
      expect(formatMetricValue(1.25, 'ratio')).toBe('1.25')
      expect(formatMetricValue(0.75, 'ratio')).toBe('0.75')
    })

    it('should format number values', () => {
      expect(formatMetricValue(1500, 'number')).toBe('1.50K')
      expect(formatMetricValue(2_500_000, 'number')).toBe('2.50M')
      expect(formatMetricValue(3_500_000_000, 'number')).toBe('3.50B')
    })
  })

  describe('getHighlightClass', () => {
    it('should return green classes for best', () => {
      const classes = getHighlightClass('best')
      expect(classes).toContain('bg-green')
      expect(classes).toContain('font-semibold')
    })

    it('should return red classes for worst', () => {
      const classes = getHighlightClass('worst')
      expect(classes).toContain('bg-red')
    })

    it('should return empty string for neutral', () => {
      expect(getHighlightClass('neutral')).toBe('')
    })
  })

  describe('exportToCSV', () => {
    const mockStocks: ComparisonStock[] = [
      {
        code: '005930',
        name: 'Samsung',
        market: 'KOSPI',
        current_price: 75000,
        per: 12.5,
      },
      {
        code: '000660',
        name: 'SK Hynix',
        market: 'KOSPI',
        current_price: 125000,
        per: 8.3,
      },
    ]

    it('should create CSV blob with headers', () => {
      const blob = exportToCSV(mockStocks, ['current_price', 'per'])

      expect(blob.type).toBe('text/csv;charset=utf-8;')
      expect(blob.size).toBeGreaterThan(0)
    })

    it('should include stock data in CSV', () => {
      const blob = exportToCSV(mockStocks, ['current_price', 'per'])

      return new Promise<void>((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
          const text = reader.result as string
          try {
            expect(text).toContain('Samsung')
            expect(text).toContain('SK Hynix')
            expect(text).toContain('75000')
            expect(text).toContain('125000')
            resolve()
          } catch (error) {
            reject(error)
          }
        }
        reader.onerror = reject
        reader.readAsText(blob)
      })
    })

    it('should handle missing values as N/A', () => {
      const stocksWithNull: ComparisonStock[] = [
        {
          ...mockStocks[0],
          per: null as any,
        },
      ]

      const blob = exportToCSV(stocksWithNull, ['per'])

      return new Promise<void>((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
          const text = reader.result as string
          try {
            expect(text).toContain('N/A')
            resolve()
          } catch (error) {
            reject(error)
          }
        }
        reader.onerror = reject
        reader.readAsText(blob)
      })
    })
  })
})
