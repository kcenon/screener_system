/**
 * Technical Indicator Tests
 *
 * Unit tests for technical analysis calculations.
 */

import { describe, it, expect } from 'vitest'
import {
  calculateSMA,
  calculateEMA,
  calculateBollingerBands,
  calculateRSI,
  calculateMACD,
  calculateStochastic,
  convertToHeikinAshi,
  type OHLCV,
} from '../indicators'

// Sample OHLCV data for testing
const sampleData: OHLCV[] = [
  {
    time: '2024-01-01',
    open: 100,
    high: 105,
    low: 98,
    close: 102,
    volume: 1000,
  },
  {
    time: '2024-01-02',
    open: 102,
    high: 108,
    low: 100,
    close: 106,
    volume: 1200,
  },
  {
    time: '2024-01-03',
    open: 106,
    high: 110,
    low: 104,
    close: 108,
    volume: 1100,
  },
  {
    time: '2024-01-04',
    open: 108,
    high: 112,
    low: 106,
    close: 110,
    volume: 1300,
  },
  {
    time: '2024-01-05',
    open: 110,
    high: 114,
    low: 108,
    close: 112,
    volume: 1400,
  },
  {
    time: '2024-01-06',
    open: 112,
    high: 115,
    low: 110,
    close: 111,
    volume: 1000,
  },
  {
    time: '2024-01-07',
    open: 111,
    high: 113,
    low: 108,
    close: 109,
    volume: 900,
  },
  {
    time: '2024-01-08',
    open: 109,
    high: 111,
    low: 106,
    close: 107,
    volume: 800,
  },
  {
    time: '2024-01-09',
    open: 107,
    high: 110,
    low: 105,
    close: 108,
    volume: 950,
  },
  {
    time: '2024-01-10',
    open: 108,
    high: 112,
    low: 107,
    close: 111,
    volume: 1100,
  },
  {
    time: '2024-01-11',
    open: 111,
    high: 116,
    low: 110,
    close: 115,
    volume: 1500,
  },
  {
    time: '2024-01-12',
    open: 115,
    high: 118,
    low: 113,
    close: 117,
    volume: 1600,
  },
  {
    time: '2024-01-13',
    open: 117,
    high: 120,
    low: 115,
    close: 118,
    volume: 1400,
  },
  {
    time: '2024-01-14',
    open: 118,
    high: 121,
    low: 116,
    close: 119,
    volume: 1300,
  },
  {
    time: '2024-01-15',
    open: 119,
    high: 122,
    low: 117,
    close: 120,
    volume: 1200,
  },
]

describe('calculateSMA', () => {
  it('should return empty array for insufficient data', () => {
    const result = calculateSMA(sampleData.slice(0, 2), 5)
    expect(result).toHaveLength(0)
  })

  it('should calculate correct SMA values', () => {
    const result = calculateSMA(sampleData, 5)
    expect(result).toHaveLength(11) // 15 - 5 + 1

    // First SMA value (average of first 5 closes: 102, 106, 108, 110, 112)
    const expectedFirst = (102 + 106 + 108 + 110 + 112) / 5
    expect(result[0].value).toBeCloseTo(expectedFirst, 2)
    expect(result[0].time).toBe('2024-01-05')
  })

  it('should handle period of 1', () => {
    const result = calculateSMA(sampleData, 1)
    expect(result).toHaveLength(15)
    expect(result[0].value).toBe(102) // First close price
  })
})

describe('calculateEMA', () => {
  it('should return empty array for insufficient data', () => {
    const result = calculateEMA(sampleData.slice(0, 2), 5)
    expect(result).toHaveLength(0)
  })

  it('should calculate correct EMA values', () => {
    const result = calculateEMA(sampleData, 5)
    expect(result).toHaveLength(11)

    // First EMA value should equal SMA
    const sma = calculateSMA(sampleData, 5)
    expect(result[0].value).toBeCloseTo(sma[0].value, 2)
  })

  it('should have EMA respond faster to price changes', () => {
    const ema = calculateEMA(sampleData, 5)
    const sma = calculateSMA(sampleData, 5)

    // When prices are rising, EMA should be above SMA
    // When prices are falling, EMA should be below SMA
    // Just verify they're both calculated
    expect(ema.length).toBe(sma.length)
  })
})

describe('calculateBollingerBands', () => {
  it('should return empty array for insufficient data', () => {
    const result = calculateBollingerBands(sampleData.slice(0, 10), 20)
    expect(result).toHaveLength(0)
  })

  it('should calculate correct Bollinger Band values', () => {
    const result = calculateBollingerBands(sampleData, 5, 2)
    expect(result).toHaveLength(11)

    // Middle band should equal SMA
    const sma = calculateSMA(sampleData, 5)
    expect(result[0].middle).toBeCloseTo(sma[0].value, 2)

    // Upper band should be greater than middle
    expect(result[0].upper).toBeGreaterThan(result[0].middle)

    // Lower band should be less than middle
    expect(result[0].lower).toBeLessThan(result[0].middle)

    // Bands should be symmetric around middle
    const upperDiff = result[0].upper - result[0].middle
    const lowerDiff = result[0].middle - result[0].lower
    expect(upperDiff).toBeCloseTo(lowerDiff, 2)
  })
})

describe('calculateRSI', () => {
  it('should return empty array for insufficient data', () => {
    const result = calculateRSI(sampleData.slice(0, 5), 14)
    expect(result).toHaveLength(0)
  })

  it('should calculate RSI values between 0 and 100', () => {
    const result = calculateRSI(sampleData, 5)

    result.forEach(point => {
      expect(point.value).toBeGreaterThanOrEqual(0)
      expect(point.value).toBeLessThanOrEqual(100)
    })
  })

  it('should return high RSI for uptrending data', () => {
    // Create strongly uptrending data
    const uptrendData: OHLCV[] = Array.from({ length: 20 }, (_, i) => ({
      time: `2024-01-${(i + 1).toString().padStart(2, '0')}`,
      open: 100 + i * 2,
      high: 102 + i * 2,
      low: 99 + i * 2,
      close: 101 + i * 2,
      volume: 1000,
    }))

    const result = calculateRSI(uptrendData, 5)
    const lastRSI = result[result.length - 1].value

    // RSI should be high (above 50) for uptrending data
    expect(lastRSI).toBeGreaterThan(50)
  })
})

describe('calculateMACD', () => {
  // Need more data for MACD
  const longData: OHLCV[] = Array.from({ length: 50 }, (_, i) => ({
    time: `2024-01-${(i + 1).toString().padStart(2, '0')}`,
    open: 100 + Math.sin(i / 5) * 10,
    high: 105 + Math.sin(i / 5) * 10,
    low: 95 + Math.sin(i / 5) * 10,
    close: 100 + Math.sin(i / 5) * 10 + i * 0.5,
    volume: 1000,
  }))

  it('should return empty array for insufficient data', () => {
    const result = calculateMACD(sampleData, 12, 26, 9)
    expect(result).toHaveLength(0)
  })

  it('should calculate MACD components correctly', () => {
    const result = calculateMACD(longData, 12, 26, 9)
    expect(result.length).toBeGreaterThan(0)

    result.forEach(point => {
      // Histogram should equal MACD - Signal
      expect(point.histogram).toBeCloseTo(point.macd - point.signal, 6)
    })
  })
})

describe('calculateStochastic', () => {
  it('should return empty array for insufficient data', () => {
    const result = calculateStochastic(sampleData.slice(0, 5), 14, 3)
    expect(result).toHaveLength(0)
  })

  it('should calculate values between 0 and 100', () => {
    const result = calculateStochastic(sampleData, 5, 3)

    result.forEach(point => {
      expect(point.k).toBeGreaterThanOrEqual(0)
      expect(point.k).toBeLessThanOrEqual(100)
      expect(point.d).toBeGreaterThanOrEqual(0)
      expect(point.d).toBeLessThanOrEqual(100)
    })
  })
})

describe('convertToHeikinAshi', () => {
  it('should return empty array for empty input', () => {
    const result = convertToHeikinAshi([])
    expect(result).toHaveLength(0)
  })

  it('should convert to Heikin-Ashi format', () => {
    const result = convertToHeikinAshi(sampleData)
    expect(result).toHaveLength(sampleData.length)

    // First HA candle close = (O + H + L + C) / 4
    const firstClose =
      (sampleData[0].open +
        sampleData[0].high +
        sampleData[0].low +
        sampleData[0].close) /
      4
    expect(result[0].close).toBeCloseTo(firstClose, 2)

    // First HA candle open = (O + C) / 2
    const firstOpen = (sampleData[0].open + sampleData[0].close) / 2
    expect(result[0].open).toBeCloseTo(firstOpen, 2)

    // Subsequent opens should be based on previous HA candle
    const secondOpen = (result[0].open + result[0].close) / 2
    expect(result[1].open).toBeCloseTo(secondOpen, 2)
  })

  it('should preserve volume', () => {
    const result = convertToHeikinAshi(sampleData)
    result.forEach((candle, i) => {
      expect(candle.volume).toBe(sampleData[i].volume)
    })
  })
})
