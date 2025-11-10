import { api } from './api'
import type {
  ScreeningRequest,
  ScreeningResponse,
  ScreeningSortField,
  SortOrder,
  StockScreeningResult,
  ScreeningFilters,
} from '../types/screening'
import type { Stock, PaginatedResponse } from '../types'

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
   * @returns Promise with stock screening result containing all available indicators
   */
  async getStock(code: string): Promise<StockScreeningResult> {
    const response = await api.get<StockScreeningResult>(
      `${this.STOCKS_BASE_URL}/${code}`
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
