import type { StockScreeningResult } from '@/types/screening'

/**
 * Export format types
 */
export type ExportFormat = 'csv' | 'json'

/**
 * Convert array of objects to CSV string
 */
function arrayToCSV(data: Record<string, unknown>[]): string {
  if (data.length === 0) return ''

  // Get headers from first object
  const headers = Object.keys(data[0])

  // Create CSV header row
  const headerRow = headers.join(',')

  // Create CSV data rows
  const dataRows = data.map(row => {
    return headers.map(header => {
      const value = row[header]

      // Handle null/undefined
      if (value === null || value === undefined) return ''

      // Convert to string and escape if contains comma, quote, or newline
      const stringValue = String(value)
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`
      }

      return stringValue
    }).join(',')
  })

  return [headerRow, ...dataRows].join('\n')
}

/**
 * Download data as file
 */
function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Prepare stock screening results for export
 * Converts StockScreeningResult to a flat object with readable keys
 */
function prepareStockDataForExport(stocks: StockScreeningResult[]): Record<string, unknown>[] {
  return stocks.map(stock => ({
    'Stock Code': stock.code,
    'Stock Name': stock.name,
    'Market': stock.market,
    'Sector': stock.sector || '',
    'Industry': stock.industry || '',
    'Price (KRW)': stock.current_price || '',
    'Market Cap (B KRW)': stock.market_cap || '',
    'PER': stock.per || '',
    'PBR': stock.pbr || '',
    'PSR': stock.psr || '',
    'Dividend Yield (%)': stock.dividend_yield || '',
    'ROE (%)': stock.roe || '',
    'ROA (%)': stock.roa || '',
    'ROIC (%)': stock.roic || '',
    'Gross Margin (%)': stock.gross_margin || '',
    'Operating Margin (%)': stock.operating_margin || '',
    'Net Margin (%)': stock.net_margin || '',
    'Revenue Growth YoY (%)': stock.revenue_growth_yoy || '',
    'Profit Growth YoY (%)': stock.profit_growth_yoy || '',
    'EPS Growth YoY (%)': stock.eps_growth_yoy || '',
    'Debt-to-Equity': stock.debt_to_equity || '',
    'Current Ratio': stock.current_ratio || '',
    'Altman Z-Score': stock.altman_z_score || '',
    'Piotroski F-Score': stock.piotroski_f_score || '',
    '1D Change (%)': stock.price_change_1d || '',
    '1W Change (%)': stock.price_change_1w || '',
    '1M Change (%)': stock.price_change_1m || '',
    '3M Change (%)': stock.price_change_3m || '',
    '6M Change (%)': stock.price_change_6m || '',
    '1Y Change (%)': stock.price_change_1y || '',
    'Volume Surge (%)': stock.volume_surge_pct || '',
    'Quality Score': stock.quality_score || '',
    'Value Score': stock.value_score || '',
    'Growth Score': stock.growth_score || '',
    'Momentum Score': stock.momentum_score || '',
    'Overall Score': stock.overall_score || '',
  }))
}

/**
 * Export stock screening results to CSV
 */
export function exportToCSV(stocks: StockScreeningResult[], filename?: string) {
  const preparedData = prepareStockDataForExport(stocks)
  const csv = arrayToCSV(preparedData)
  const timestamp = new Date().toISOString().split('T')[0]
  const finalFilename = filename || `stock_screening_${timestamp}.csv`

  downloadFile(csv, finalFilename, 'text/csv;charset=utf-8;')
}

/**
 * Export stock screening results to JSON
 */
export function exportToJSON(stocks: StockScreeningResult[], filename?: string) {
  const json = JSON.stringify(stocks, null, 2)
  const timestamp = new Date().toISOString().split('T')[0]
  const finalFilename = filename || `stock_screening_${timestamp}.json`

  downloadFile(json, finalFilename, 'application/json;charset=utf-8;')
}

/**
 * Export stock screening results based on format
 */
export function exportStocks(
  stocks: StockScreeningResult[],
  format: ExportFormat,
  filename?: string
) {
  if (stocks.length === 0) {
    throw new Error('No data to export')
  }

  switch (format) {
    case 'csv':
      exportToCSV(stocks, filename)
      break
    case 'json':
      exportToJSON(stocks, filename)
      break
    default:
      throw new Error(`Unsupported export format: ${format}`)
  }
}
