/**
 * Technical Indicator Calculations
 *
 * Pure functions for calculating common technical analysis indicators.
 * All functions work with standard OHLCV data format.
 */

export interface OHLCV {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface IndicatorPoint {
  time: string
  value: number
}

export interface BollingerBand {
  time: string
  upper: number
  middle: number
  lower: number
}

export interface MACDResult {
  time: string
  macd: number
  signal: number
  histogram: number
}

/**
 * Calculate Simple Moving Average (SMA)
 * @param data - OHLCV data array
 * @param period - Number of periods for SMA calculation
 * @returns Array of SMA values with timestamps
 */
export function calculateSMA(data: OHLCV[], period: number): IndicatorPoint[] {
  if (data.length < period) return []

  const result: IndicatorPoint[] = []

  for (let i = period - 1; i < data.length; i++) {
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close
    }
    result.push({
      time: data[i].time,
      value: sum / period,
    })
  }

  return result
}

/**
 * Calculate Exponential Moving Average (EMA)
 * @param data - OHLCV data array
 * @param period - Number of periods for EMA calculation
 * @returns Array of EMA values with timestamps
 */
export function calculateEMA(data: OHLCV[], period: number): IndicatorPoint[] {
  if (data.length < period) return []

  const result: IndicatorPoint[] = []
  const multiplier = 2 / (period + 1)

  // Start with SMA for the first value
  let sum = 0
  for (let i = 0; i < period; i++) {
    sum += data[i].close
  }
  let ema = sum / period
  result.push({ time: data[period - 1].time, value: ema })

  // Calculate EMA for remaining data
  for (let i = period; i < data.length; i++) {
    ema = (data[i].close - ema) * multiplier + ema
    result.push({ time: data[i].time, value: ema })
  }

  return result
}

/**
 * Calculate Bollinger Bands
 * @param data - OHLCV data array
 * @param period - SMA period (default: 20)
 * @param stdDev - Number of standard deviations (default: 2)
 * @returns Array of Bollinger Band values (upper, middle, lower)
 */
export function calculateBollingerBands(
  data: OHLCV[],
  period: number = 20,
  stdDev: number = 2,
): BollingerBand[] {
  if (data.length < period) return []

  const result: BollingerBand[] = []

  for (let i = period - 1; i < data.length; i++) {
    // Calculate SMA (middle band)
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close
    }
    const sma = sum / period

    // Calculate standard deviation
    let sumSquaredDiff = 0
    for (let j = 0; j < period; j++) {
      const diff = data[i - j].close - sma
      sumSquaredDiff += diff * diff
    }
    const sd = Math.sqrt(sumSquaredDiff / period)

    result.push({
      time: data[i].time,
      upper: sma + stdDev * sd,
      middle: sma,
      lower: sma - stdDev * sd,
    })
  }

  return result
}

/**
 * Calculate Relative Strength Index (RSI)
 * @param data - OHLCV data array
 * @param period - RSI period (default: 14)
 * @returns Array of RSI values (0-100)
 */
export function calculateRSI(
  data: OHLCV[],
  period: number = 14,
): IndicatorPoint[] {
  if (data.length < period + 1) return []

  const result: IndicatorPoint[] = []
  const gains: number[] = []
  const losses: number[] = []

  // Calculate price changes
  for (let i = 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close
    gains.push(change > 0 ? change : 0)
    losses.push(change < 0 ? -change : 0)
  }

  // Calculate initial average gain/loss
  let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period
  let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period

  // First RSI value
  let rs = avgLoss === 0 ? 100 : avgGain / avgLoss
  let rsi = 100 - 100 / (1 + rs)
  result.push({ time: data[period].time, value: rsi })

  // Calculate remaining RSI values using smoothed averages
  for (let i = period; i < gains.length; i++) {
    avgGain = (avgGain * (period - 1) + gains[i]) / period
    avgLoss = (avgLoss * (period - 1) + losses[i]) / period

    rs = avgLoss === 0 ? 100 : avgGain / avgLoss
    rsi = 100 - 100 / (1 + rs)
    result.push({ time: data[i + 1].time, value: rsi })
  }

  return result
}

/**
 * Calculate MACD (Moving Average Convergence Divergence)
 * @param data - OHLCV data array
 * @param fastPeriod - Fast EMA period (default: 12)
 * @param slowPeriod - Slow EMA period (default: 26)
 * @param signalPeriod - Signal line period (default: 9)
 * @returns Array of MACD values (macd, signal, histogram)
 */
export function calculateMACD(
  data: OHLCV[],
  fastPeriod: number = 12,
  slowPeriod: number = 26,
  signalPeriod: number = 9,
): MACDResult[] {
  if (data.length < slowPeriod + signalPeriod) return []

  const fastEMA = calculateEMA(data, fastPeriod)
  const slowEMA = calculateEMA(data, slowPeriod)

  // Align EMAs - slow EMA starts later
  const offset = slowPeriod - fastPeriod
  const macdLine: IndicatorPoint[] = []

  for (let i = 0; i < slowEMA.length; i++) {
    macdLine.push({
      time: slowEMA[i].time,
      value: fastEMA[i + offset].value - slowEMA[i].value,
    })
  }

  // Calculate signal line (EMA of MACD)
  if (macdLine.length < signalPeriod) return []

  const result: MACDResult[] = []
  const multiplier = 2 / (signalPeriod + 1)

  // Initial signal (SMA)
  let signalSum = 0
  for (let i = 0; i < signalPeriod; i++) {
    signalSum += macdLine[i].value
  }
  let signal = signalSum / signalPeriod

  result.push({
    time: macdLine[signalPeriod - 1].time,
    macd: macdLine[signalPeriod - 1].value,
    signal,
    histogram: macdLine[signalPeriod - 1].value - signal,
  })

  // Calculate remaining signal values
  for (let i = signalPeriod; i < macdLine.length; i++) {
    signal = (macdLine[i].value - signal) * multiplier + signal
    result.push({
      time: macdLine[i].time,
      macd: macdLine[i].value,
      signal,
      histogram: macdLine[i].value - signal,
    })
  }

  return result
}

/**
 * Calculate Stochastic Oscillator
 * @param data - OHLCV data array
 * @param kPeriod - %K period (default: 14)
 * @param dPeriod - %D period (default: 3)
 * @returns Array of Stochastic values (%K, %D)
 */
export function calculateStochastic(
  data: OHLCV[],
  kPeriod: number = 14,
  dPeriod: number = 3,
): { time: string; k: number; d: number }[] {
  if (data.length < kPeriod + dPeriod - 1) return []

  const kValues: IndicatorPoint[] = []

  // Calculate %K
  for (let i = kPeriod - 1; i < data.length; i++) {
    let highestHigh = -Infinity
    let lowestLow = Infinity

    for (let j = 0; j < kPeriod; j++) {
      highestHigh = Math.max(highestHigh, data[i - j].high)
      lowestLow = Math.min(lowestLow, data[i - j].low)
    }

    const k =
      highestHigh === lowestLow
        ? 50
        : ((data[i].close - lowestLow) / (highestHigh - lowestLow)) * 100

    kValues.push({ time: data[i].time, value: k })
  }

  // Calculate %D (SMA of %K)
  const result: { time: string; k: number; d: number }[] = []

  for (let i = dPeriod - 1; i < kValues.length; i++) {
    let dSum = 0
    for (let j = 0; j < dPeriod; j++) {
      dSum += kValues[i - j].value
    }
    result.push({
      time: kValues[i].time,
      k: kValues[i].value,
      d: dSum / dPeriod,
    })
  }

  return result
}

/**
 * Convert Candlestick data to Heikin-Ashi format
 * @param data - OHLCV data array
 * @returns Array of Heikin-Ashi candlestick data
 */
export function convertToHeikinAshi(data: OHLCV[]): OHLCV[] {
  if (data.length === 0) return []

  const result: OHLCV[] = []

  // First candle
  const firstCandle = data[0]
  const firstHA: OHLCV = {
    time: firstCandle.time,
    open: (firstCandle.open + firstCandle.close) / 2,
    close:
      (firstCandle.open +
        firstCandle.high +
        firstCandle.low +
        firstCandle.close) /
      4,
    high: firstCandle.high,
    low: firstCandle.low,
    volume: firstCandle.volume,
  }
  result.push(firstHA)

  // Remaining candles
  for (let i = 1; i < data.length; i++) {
    const candle = data[i]
    const prevHA = result[i - 1]

    const haClose = (candle.open + candle.high + candle.low + candle.close) / 4
    const haOpen = (prevHA.open + prevHA.close) / 2
    const haHigh = Math.max(candle.high, haOpen, haClose)
    const haLow = Math.min(candle.low, haOpen, haClose)

    result.push({
      time: candle.time,
      open: haOpen,
      close: haClose,
      high: haHigh,
      low: haLow,
      volume: candle.volume,
    })
  }

  return result
}
