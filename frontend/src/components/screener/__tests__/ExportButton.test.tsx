import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ExportButton from '../ExportButton'
import * as exportUtils from '@/utils/exportUtils'
import type { StockScreeningResult } from '@/types/screening'

// Mock exportUtils
vi.mock('@/utils/exportUtils', () => ({
  exportStocks: vi.fn(),
}))

describe('ExportButton', () => {
  const mockData: StockScreeningResult[] = [
    {
      code: '005930',
      name: 'Samsung Electronics',
      market: 'KOSPI',
      sector: 'Technology',
      current_price: 70000,
      market_cap: 400000,
      per: 12.5,
      roe: 15.3,
      revenue_growth_yoy: 10.2,
    } as StockScreeningResult,
    {
      code: '000660',
      name: 'SK Hynix',
      market: 'KOSPI',
      sector: 'Technology',
      current_price: 120000,
      market_cap: 80000,
      pbr: 1.8,
      roa: 8.5,
    } as StockScreeningResult,
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders export button', () => {
      render(<ExportButton data={mockData} />)

      const button = screen.getByRole('button', { name: /export/i })
      expect(button).toBeInTheDocument()
    })

    it('is enabled when data is provided', () => {
      render(<ExportButton data={mockData} />)

      const button = screen.getByRole('button', { name: /export/i })
      expect(button).not.toBeDisabled()
    })

    it('is disabled when data is empty', () => {
      render(<ExportButton data={[]} />)

      const button = screen.getByRole('button', { name: /export/i })
      expect(button).toBeDisabled()
    })

    it('is disabled when disabled prop is true', () => {
      render(<ExportButton data={mockData} disabled={true} />)

      const button = screen.getByRole('button', { name: /export/i })
      expect(button).toBeDisabled()
    })

    it('is disabled when disabled prop is true even with data', () => {
      render(<ExportButton data={mockData} disabled={true} />)

      const button = screen.getByRole('button', { name: /export/i })
      expect(button).toBeDisabled()
    })

    it('displays download icon', () => {
      const { container } = render(<ExportButton data={mockData} />)

      const downloadIcon = container.querySelector('svg[aria-hidden="true"]')
      expect(downloadIcon).toBeInTheDocument()
    })
  })

  describe('Dropdown Menu', () => {
    it('opens dropdown menu when button is clicked', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} />)

      const button = screen.getByRole('button', { name: /export/i })
      await user.click(button)

      expect(screen.getByText(/export as csv/i)).toBeInTheDocument()
      expect(screen.getByText(/export as json/i)).toBeInTheDocument()
    })

    it('displays CSV menu item', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))

      const csvItem = screen.getByText(/export as csv/i)
      expect(csvItem).toBeInTheDocument()
    })

    it('displays JSON menu item', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))

      const jsonItem = screen.getByText(/export as json/i)
      expect(jsonItem).toBeInTheDocument()
    })

    it('displays stock count in menu', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))

      expect(screen.getByText('2 stocks')).toBeInTheDocument()
    })

    it('displays singular "stock" for single item', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={[mockData[0]]} />)

      await user.click(screen.getByRole('button', { name: /export/i }))

      expect(screen.getByText('1 stock')).toBeInTheDocument()
    })
  })

  describe('CSV Export', () => {
    it('calls exportStocks with CSV format when CSV menu item is clicked', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      await user.click(screen.getByText(/export as csv/i))

      expect(exportUtils.exportStocks).toHaveBeenCalledWith(mockData, 'csv', undefined)
    })

    it('passes custom filename to exportStocks for CSV', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} filename="my-stocks" />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      await user.click(screen.getByText(/export as csv/i))

      expect(exportUtils.exportStocks).toHaveBeenCalledWith(mockData, 'csv', 'my-stocks')
    })

    it('closes dropdown after CSV export', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      expect(screen.getByText(/export as csv/i)).toBeInTheDocument()

      await user.click(screen.getByText(/export as csv/i))

      // Menu should close
      expect(screen.queryByText(/export as csv/i)).not.toBeInTheDocument()
    })
  })

  describe('JSON Export', () => {
    it('calls exportStocks with JSON format when JSON menu item is clicked', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      await user.click(screen.getByText(/export as json/i))

      expect(exportUtils.exportStocks).toHaveBeenCalledWith(mockData, 'json', undefined)
    })

    it('passes custom filename to exportStocks for JSON', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} filename="my-stocks" />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      await user.click(screen.getByText(/export as json/i))

      expect(exportUtils.exportStocks).toHaveBeenCalledWith(mockData, 'json', 'my-stocks')
    })

    it('closes dropdown after JSON export', async () => {
      const user = userEvent.setup()
      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      expect(screen.getByText(/export as json/i)).toBeInTheDocument()

      await user.click(screen.getByText(/export as json/i))

      // Menu should close
      expect(screen.queryByText(/export as json/i)).not.toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('shows alert when export fails', async () => {
      const user = userEvent.setup()
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})
      vi.mocked(exportUtils.exportStocks).mockImplementation(() => {
        throw new Error('Export failed')
      })

      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      await user.click(screen.getByText(/export as csv/i))

      expect(alertSpy).toHaveBeenCalledWith('Failed to export data. Please try again.')
      alertSpy.mockRestore()
    })

    it('logs error to console when export fails', async () => {
      const user = userEvent.setup()
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})
      const testError = new Error('Export failed')

      vi.mocked(exportUtils.exportStocks).mockImplementation(() => {
        throw testError
      })

      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      await user.click(screen.getByText(/export as csv/i))

      expect(consoleErrorSpy).toHaveBeenCalledWith('Export failed:', testError)
      consoleErrorSpy.mockRestore()
      alertSpy.mockRestore()
    })

    it('closes dropdown even when export fails', async () => {
      const user = userEvent.setup()
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})
      vi.mocked(exportUtils.exportStocks).mockImplementation(() => {
        throw new Error('Export failed')
      })

      render(<ExportButton data={mockData} />)

      await user.click(screen.getByRole('button', { name: /export/i }))
      await user.click(screen.getByText(/export as csv/i))

      // Menu should still close
      expect(screen.queryByText(/export as csv/i)).not.toBeInTheDocument()
      alertSpy.mockRestore()
    })
  })
})
