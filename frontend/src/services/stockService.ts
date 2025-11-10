import { api } from './api'
import type {
  ScreeningRequest,
  ScreeningResponse,
  ScreeningSortField,
  SortOrder,
  ScreeningFilters,
} from '../types/screening'
import type {
  Stock,
  PaginatedResponse,
  StockDetail,
  PriceHistoryResponse,
  FinancialsResponse,
  FinancialPeriod,
} from '../types'

/**
 * Stock service for managing stock screening and stock data operations
 */
class StockService {
  private readonly STOCKS_BASE_URL = '/stocks'
  private readonly SCREENING_BASE_URL = '/screening'

  /**
   * Screen stocks based on filters, sorting, and pagination
   *
   * @param filters - Screening filters to apply
   * @param sortBy - Field to sort by (default: 'market_cap')
   * @param order - Sort order (default: 'desc')
   * @param offset - Number of results to skip for pagination (default: 0)
   * @param limit - Maximum number of results to return (default: 50)
   * @returns Promise with screening response containing matched stocks and metadata
   */
  async screenStocks(
    filters?: ScreeningFilters,
    sortBy: ScreeningSortField = 'market_cap',
    order: SortOrder = 'desc',
    offset: number = 0,
    limit: number = 50
  ): Promise<ScreeningResponse> {
    // Convert offset/limit to page/per_page for backend API
    const page = Math.floor(offset / limit) + 1
    const per_page = limit

    const requestData: ScreeningRequest = {
      filters: filters || {},
      sort_by: sortBy,
      order,
      page,
      per_page,
    }

    const response = await api.post<ScreeningResponse>(
      `${this.SCREENING_BASE_URL}/screen`,
      requestData
    )
    return response.data
  }

  /**
   * Get detailed information for a single stock by code
   *
   * @param code - Stock code (e.g., '005930' for Samsung Electronics)
   * @returns Promise with stock detail containing all available indicators and metadata
   */
  async getStock(code: string): Promise<StockDetail> {
    const response = await api.get<StockDetail>(
      `${this.STOCKS_BASE_URL}/${code}`
    )
    return response.data
  }

  /**
   * Get price history for a stock
   *
   * @param code - Stock code
   * @param fromDate - Start date (ISO 8601 format, e.g., '2023-01-01')
   * @param toDate - End date (ISO 8601 format, e.g., '2023-12-31')
   * @param interval - Time interval ('1D', '1W', '1M', etc.)
   * @returns Promise with price history data
   */
  async getPriceHistory(
    code: string,
    fromDate: string,
    toDate: string,
    interval: string = '1D'
  ): Promise<PriceHistoryResponse> {
    const response = await api.get<PriceHistoryResponse>(
      `${this.STOCKS_BASE_URL}/${code}/prices`,
      {
        params: {
          from_date: fromDate,
          to_date: toDate,
          interval,
        },
      }
    )
    return response.data
  }

  /**
   * Get financial statements for a stock
   *
   * @param code - Stock code
   * @param periodType - Period type ('Q' for quarterly, 'Y' for yearly)
   * @param years - Number of years/periods to fetch (default: 5)
   * @returns Promise with financial statements data
   */
  async getFinancials(
    code: string,
    periodType: FinancialPeriod = 'Y',
    years: number = 5
  ): Promise<FinancialsResponse> {
    const response = await api.get<FinancialsResponse>(
      `${this.STOCKS_BASE_URL}/${code}/financials`,
      {
        params: {
          period_type: periodType,
          years,
        },
      }
    )
    return response.data
  }

  /**
   * List stocks with optional market filter and pagination
   *
   * @param market - Market filter ('KOSPI', 'KOSDAQ', or undefined for all)
   * @param offset - Number of results to skip for pagination (default: 0)
   * @param limit - Maximum number of results to return (default: 50)
   * @returns Promise with paginated list of stocks
   */
  async listStocks(
    market?: 'KOSPI' | 'KOSDAQ',
    offset: number = 0,
    limit: number = 50
  ): Promise<PaginatedResponse<Stock>> {
    const page = Math.floor(offset / limit) + 1

    const params: Record<string, string | number> = {
      page,
      per_page: limit,
    }

    if (market) {
      params.market = market
    }

    const response = await api.get<PaginatedResponse<Stock>>(
      this.STOCKS_BASE_URL,
      { params }
    )
    return response.data
  }
}

export const stockService = new StockService()
