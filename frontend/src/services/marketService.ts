/**
 * Market Overview API Service (FE-009)
 *
 * Service for fetching market indices, sector performance, market breadth,
 * top movers, and market trend data from the backend.
 */

import { api } from './api'
import type {
  MarketIndicesResponse,
  MarketBreadth,
  MarketType,
  SectorsPerformanceResponse,
  MarketMoversResponse,
  MostActiveResponse,
  MarketTrendResponse,
  TrendTimeframe,
} from '../types/market'

/**
 * Market overview API endpoints
 */
const MARKET_API_BASE = '/api/v1/market'

/**
 * Fetch current market indices (KOSPI, KOSDAQ, KRX100)
 *
 * @returns Promise with market indices data
 * @throws Error if request fails
 */
export async function getMarketIndices(): Promise<MarketIndicesResponse> {
  const response = await api.get<MarketIndicesResponse>(`${MARKET_API_BASE}/indices`)
  return response.data
}

/**
 * Fetch market breadth indicators
 *
 * @param market - Market filter (ALL, KOSPI, KOSDAQ)
 * @returns Promise with market breadth data
 * @throws Error if request fails
 */
export async function getMarketBreadth(market: MarketType = 'ALL'): Promise<MarketBreadth> {
  const response = await api.get<MarketBreadth>(`${MARKET_API_BASE}/breadth`, {
    params: { market },
  })
  return response.data
}

/**
 * Fetch sector performance data
 *
 * @param timeframe - Timeframe for performance calculation (1D, 1W, 1M, 3M)
 * @returns Promise with sector performance data
 * @throws Error if request fails
 */
export async function getSectorPerformance(
  timeframe: '1D' | '1W' | '1M' | '3M' = '1D'
): Promise<SectorsPerformanceResponse> {
  const response = await api.get<SectorsPerformanceResponse>(`${MARKET_API_BASE}/sectors`, {
    params: { timeframe },
  })
  return response.data
}

/**
 * Fetch top market movers (gainers and losers)
 *
 * @param market - Market filter (ALL, KOSPI, KOSDAQ)
 * @param limit - Number of results per category (default: 10)
 * @returns Promise with market movers data
 * @throws Error if request fails
 */
export async function getMarketMovers(
  market: MarketType = 'ALL',
  limit: number = 10
): Promise<MarketMoversResponse> {
  const response = await api.get<MarketMoversResponse>(`${MARKET_API_BASE}/movers`, {
    params: { market, limit },
  })
  return response.data
}

/**
 * Fetch most active stocks by volume
 *
 * @param market - Market filter (ALL, KOSPI, KOSDAQ)
 * @param limit - Number of results (default: 20)
 * @returns Promise with most active stocks data
 * @throws Error if request fails
 */
export async function getMostActive(
  market: MarketType = 'ALL',
  limit: number = 20
): Promise<MostActiveResponse> {
  const response = await api.get<MostActiveResponse>(`${MARKET_API_BASE}/active`, {
    params: { market, limit },
  })
  return response.data
}

/**
 * Fetch historical market trend data
 *
 * @param timeframe - Timeframe for historical data (1D, 5D, 1M, 3M, 6M, 1Y)
 * @param indices - Array of index codes to fetch (default: ['KOSPI', 'KOSDAQ'])
 * @returns Promise with market trend data
 * @throws Error if request fails
 */
export async function getMarketTrend(
  timeframe: TrendTimeframe = '3M',
  indices: string[] = ['KOSPI', 'KOSDAQ']
): Promise<MarketTrendResponse> {
  const response = await api.get<MarketTrendResponse>(`${MARKET_API_BASE}/trend`, {
    params: {
      timeframe,
      indices: indices.join(','),
    },
  })
  return response.data
}

/**
 * Market service object with all API functions
 */
const marketService = {
  getMarketIndices,
  getMarketBreadth,
  getSectorPerformance,
  getMarketMovers,
  getMostActive,
  getMarketTrend,
}

export default marketService
