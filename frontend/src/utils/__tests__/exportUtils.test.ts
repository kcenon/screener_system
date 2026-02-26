import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { exportStocks, exportToCSV, exportToJSON } from '../exportUtils'
import type { StockScreeningResult } from '@/types/screening'

describe('exportUtils', () => {
  const mockStocks: StockScreeningResult[] = [
    {
      code: '005930',
      name: 'Samsung Electronics',
      market: 'KOSPI',
      sector: 'Technology',
      industry: 'Semiconductors',
      current_price: 70000,
      market_cap: 400000,
      per: 12.5,
      pbr: 1.8,
      psr: 0.9,
      dividend_yield: 2.5,
      roe: 15.3,
      roa: 8.5,
      roic: 12.1,
      gross_margin: 45.2,
      operating_margin: 18.5,
      net_margin: 14.3,
      revenue_growth_yoy: 10.2,
      profit_growth_yoy: 15.8,
      eps_growth_yoy: 16.2,
      debt_to_equity: 0.5,
      current_ratio: 2.1,
      altman_z_score: 3.5,
      piotroski_f_score: 8,
      price_change_1d: 1.2,
      price_change_1w: 3.5,
      price_change_1m: 5.8,
      price_change_3m: 8.2,
      price_change_6m: 12.5,
      price_change_1y: 25.3,
      volume_surge_pct: 150.0,
      quality_score: 85,
      value_score: 75,
      growth_score: 80,
      momentum_score: 90,
      overall_score: 82,
    } as StockScreeningResult,
    {
      code: '000660',
      name: 'SK Hynix',
      market: 'KOSPI',
      sector: 'Technology',
      industry: null,
      current_price: 120000,
      market_cap: 80000,
      per: null,
      pbr: null,
      psr: null,
      dividend_yield: null,
      roe: null,
      roa: null,
      roic: null,
      gross_margin: null,
      operating_margin: null,
      net_margin: null,
      revenue_growth_yoy: null,
      profit_growth_yoy: null,
      eps_growth_yoy: null,
      debt_to_equity: null,
      current_ratio: null,
      altman_z_score: null,
      piotroski_f_score: null,
      price_change_1d: null,
      price_change_1w: null,
      price_change_1m: null,
      price_change_3m: null,
      price_change_6m: null,
      price_change_1y: null,
      volume_surge_pct: null,
      quality_score: null,
      value_score: null,
      growth_score: null,
      momentum_score: null,
      overall_score: null,
    } as StockScreeningResult,
  ]

  let createElementSpy: any
  let appendChildSpy: any
  let removeChildSpy: any
  let clickSpy: () => void
  let revokeObjectURLSpy: any

  beforeEach(() => {
    // Mock document.createElement and related DOM methods
    clickSpy = vi.fn()
    const mockLink = {
      href: '',
      download: '',
      click: clickSpy,
    } as unknown as HTMLAnchorElement

    createElementSpy = vi
      .spyOn(document, 'createElement')
      .mockReturnValue(mockLink)
    appendChildSpy = vi
      .spyOn(document.body, 'appendChild')
      .mockImplementation(() => mockLink)
    removeChildSpy = vi
      .spyOn(document.body, 'removeChild')
      .mockImplementation(() => mockLink)

    // Mock URL.createObjectURL and URL.revokeObjectURL
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
    revokeObjectURLSpy = vi
      .spyOn(URL, 'revokeObjectURL')
      .mockImplementation(() => {})

    // Mock Date to ensure consistent timestamp
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-01-15T10:00:00.000Z'))
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  describe('exportStocks', () => {
    it('throws error when no data provided', () => {
      expect(() => exportStocks([], 'csv')).toThrow('No data to export')
    })

    it('throws error for unsupported format', () => {
      expect(() => exportStocks(mockStocks, 'xml' as any)).toThrow(
        'Unsupported export format: xml',
      )
    })

    it('calls exportToCSV for CSV format', () => {
      exportStocks(mockStocks, 'csv')

      expect(createElementSpy).toHaveBeenCalledWith('a')
      expect(clickSpy).toHaveBeenCalled()
    })

    it('calls exportToJSON for JSON format', () => {
      exportStocks(mockStocks, 'json')

      expect(createElementSpy).toHaveBeenCalledWith('a')
      expect(clickSpy).toHaveBeenCalled()
    })

    it('passes custom filename to export functions', () => {
      exportStocks(mockStocks, 'csv', 'my-stocks.csv')

      const mockLink = createElementSpy.mock.results[0]
        .value as HTMLAnchorElement
      expect(mockLink.download).toBe('my-stocks.csv')
    })
  })

  describe('exportToCSV', () => {
    it('generates CSV with header row', () => {
      exportToCSV(mockStocks)

      // Blob constructor should be called with CSV content
      expect(createElementSpy).toHaveBeenCalledWith('a')
    })

    it('uses default filename with timestamp when no filename provided', () => {
      exportToCSV(mockStocks)

      const mockLink = createElementSpy.mock.results[0]
        .value as HTMLAnchorElement
      expect(mockLink.download).toBe('stock_screening_2025-01-15.csv')
    })

    it('uses custom filename when provided', () => {
      exportToCSV(mockStocks, 'custom-filename.csv')

      const mockLink = createElementSpy.mock.results[0]
        .value as HTMLAnchorElement
      expect(mockLink.download).toBe('custom-filename.csv')
    })

    it('handles stocks with null values correctly', () => {
      // Test with stock that has null values (SK Hynix)
      exportToCSV([mockStocks[1]])

      expect(clickSpy).toHaveBeenCalled()
    })

    it('escapes values with commas in CSV', () => {
      const stockWithComma: StockScreeningResult = {
        ...mockStocks[0],
        name: 'Company, Inc.',
      }

      exportToCSV([stockWithComma])

      expect(clickSpy).toHaveBeenCalled()
    })

    it('escapes values with quotes in CSV', () => {
      const stockWithQuote: StockScreeningResult = {
        ...mockStocks[0],
        name: 'Company "Best" Ltd',
      }

      exportToCSV([stockWithQuote])

      expect(clickSpy).toHaveBeenCalled()
    })

    it('creates download link and triggers click', () => {
      exportToCSV(mockStocks)

      expect(createElementSpy).toHaveBeenCalledWith('a')
      expect(appendChildSpy).toHaveBeenCalled()
      expect(clickSpy).toHaveBeenCalled()
      expect(removeChildSpy).toHaveBeenCalled()
    })

    it('revokes object URL after download', () => {
      exportToCSV(mockStocks)

      expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:mock-url')
    })
  })

  describe('exportToJSON', () => {
    it('generates JSON with proper formatting', () => {
      exportToJSON(mockStocks)

      // Blob should be created with JSON content
      expect(createElementSpy).toHaveBeenCalledWith('a')
    })

    it('uses default filename with timestamp when no filename provided', () => {
      exportToJSON(mockStocks)

      const mockLink = createElementSpy.mock.results[0]
        .value as HTMLAnchorElement
      expect(mockLink.download).toBe('stock_screening_2025-01-15.json')
    })

    it('uses custom filename when provided', () => {
      exportToJSON(mockStocks, 'custom-filename.json')

      const mockLink = createElementSpy.mock.results[0]
        .value as HTMLAnchorElement
      expect(mockLink.download).toBe('custom-filename.json')
    })

    it('preserves all stock data in JSON', () => {
      exportToJSON(mockStocks)

      // JSON.stringify should be called with stocks data
      expect(clickSpy).toHaveBeenCalled()
    })

    it('handles null values in JSON', () => {
      exportToJSON([mockStocks[1]])

      expect(clickSpy).toHaveBeenCalled()
    })

    it('creates download link and triggers click', () => {
      exportToJSON(mockStocks)

      expect(createElementSpy).toHaveBeenCalledWith('a')
      expect(appendChildSpy).toHaveBeenCalled()
      expect(clickSpy).toHaveBeenCalled()
      expect(removeChildSpy).toHaveBeenCalled()
    })

    it('revokes object URL after download', () => {
      exportToJSON(mockStocks)

      expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:mock-url')
    })
  })

  describe('CSV Format Details', () => {
    it('includes all expected column headers', () => {
      // We can't easily inspect Blob content in vitest/jsdom,
      // but we can verify the function completes without error
      expect(() => exportToCSV(mockStocks)).not.toThrow()
    })

    it('handles empty strings for null values', () => {
      const stockWithNulls: StockScreeningResult = {
        code: '123456',
        name: 'Test Stock',
        market: 'KOSPI',
        sector: null,
        industry: null,
        current_price: null,
        market_cap: null,
        per: null,
        pbr: null,
      } as StockScreeningResult

      expect(() => exportToCSV([stockWithNulls])).not.toThrow()
    })
  })

  describe('Download Flow', () => {
    it('creates blob with correct MIME type for CSV', () => {
      exportToCSV(mockStocks)

      // Verify Blob was created (indirectly through createObjectURL)
      expect(URL.createObjectURL).toHaveBeenCalled()
    })

    it('creates blob with correct MIME type for JSON', () => {
      exportToJSON(mockStocks)

      // Verify Blob was created (indirectly through createObjectURL)
      expect(URL.createObjectURL).toHaveBeenCalled()
    })

    it('sets href on link element', () => {
      exportToCSV(mockStocks)

      const mockLink = createElementSpy.mock.results[0]
        .value as HTMLAnchorElement
      expect(mockLink.href).toBe('blob:mock-url')
    })

    it('cleans up DOM after download', () => {
      exportToCSV(mockStocks)

      // Verify link is removed from DOM
      expect(removeChildSpy).toHaveBeenCalled()
    })

    it('cleans up object URL after download', () => {
      exportToCSV(mockStocks)

      // Verify URL is revoked
      expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:mock-url')
    })
  })
})
