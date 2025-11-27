/**
 * Advanced Chart Component
 *
 * TradingView-style interactive chart with:
 * - Multiple chart types (candlestick, OHLC, line, area, Heikin-Ashi)
 * - Technical indicator overlays
 * - Zoom and pan controls
 * - Crosshair with price/time display
 * - Theme support (light/dark)
 *
 * Built with TradingView's Lightweight Charts library.
 */

import { useEffect, useRef, useCallback, useMemo } from 'react'
import {
  createChart,
  ColorType,
  CrosshairMode,
  LineStyle,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type LineData,
  type HistogramData,
  type Time,
} from 'lightweight-charts'
import {
  calculateSMA,
  calculateEMA,
  calculateBollingerBands,
  calculateRSI,
  calculateMACD,
  convertToHeikinAshi,
} from '@/utils/indicators'
import type { ChartTheme, AdvancedChartProps } from './types'

const LIGHT_THEME: ChartTheme = {
  backgroundColor: '#ffffff',
  textColor: '#333333',
  gridColor: '#f0f0f0',
  borderColor: '#e1e1e1',
  crosshairColor: '#9B7DFF',
  upColor: '#ef5350',
  downColor: '#26a69a',
}

const DARK_THEME: ChartTheme = {
  backgroundColor: '#1f2937',
  textColor: '#f3f4f6',
  gridColor: '#374151',
  borderColor: '#4b5563',
  crosshairColor: '#9B7DFF',
  upColor: '#ef5350',
  downColor: '#26a69a',
}

export default function AdvancedChart({
  symbol,
  data,
  height = 400,
  chartType = 'candlestick',
  theme = 'light',
  indicators = [],
  showVolume = true,
  loading = false,
}: AdvancedChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const mainSeriesRef = useRef<ISeriesApi<'Candlestick' | 'Line' | 'Area' | 'Bar'> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null)
  const indicatorSeriesRef = useRef<Map<string, ISeriesApi<'Line' | 'Histogram'>>>(new Map())
  const rsiPaneRef = useRef<ISeriesApi<'Line'> | null>(null)
  const macdSeriesRef = useRef<{
    macd: ISeriesApi<'Line'> | null
    signal: ISeriesApi<'Line'> | null
    histogram: ISeriesApi<'Histogram'> | null
  }>({ macd: null, signal: null, histogram: null })

  const chartTheme = useMemo(() => (theme === 'dark' ? DARK_THEME : LIGHT_THEME), [theme])

  // Transform OHLCV data based on chart type
  const transformedData = useMemo(() => {
    if (!data || data.length === 0) return []

    if (chartType === 'heikin-ashi') {
      return convertToHeikinAshi(data)
    }
    return data
  }, [data, chartType])

  // Create chart options
  const createChartOptions = useCallback(() => ({
    layout: {
      background: { type: ColorType.Solid, color: chartTheme.backgroundColor },
      textColor: chartTheme.textColor,
    },
    width: chartContainerRef.current?.clientWidth || 800,
    height,
    grid: {
      vertLines: { color: chartTheme.gridColor, style: LineStyle.Solid },
      horzLines: { color: chartTheme.gridColor, style: LineStyle.Solid },
    },
    crosshair: {
      mode: CrosshairMode.Normal,
      vertLine: {
        width: 1 as const,
        color: chartTheme.crosshairColor,
        style: LineStyle.Dashed,
        labelBackgroundColor: chartTheme.crosshairColor,
      },
      horzLine: {
        width: 1 as const,
        color: chartTheme.crosshairColor,
        style: LineStyle.Dashed,
        labelBackgroundColor: chartTheme.crosshairColor,
      },
    },
    rightPriceScale: {
      borderColor: chartTheme.borderColor,
      scaleMargins: {
        top: 0.1,
        bottom: showVolume ? 0.25 : 0.1,
      },
    },
    timeScale: {
      borderColor: chartTheme.borderColor,
      timeVisible: true,
      secondsVisible: false,
    },
    handleScale: {
      axisPressedMouseMove: {
        time: true,
        price: true,
      },
    },
    handleScroll: {
      vertTouchDrag: true,
    },
  }), [chartTheme, height, showVolume])

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, createChartOptions())
    chartRef.current = chart

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    const resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(chartContainerRef.current)

    return () => {
      resizeObserver.disconnect()
      chart.remove()
      chartRef.current = null
      mainSeriesRef.current = null
      volumeSeriesRef.current = null
      indicatorSeriesRef.current.clear()
    }
  }, [])

  // Update theme
  useEffect(() => {
    if (!chartRef.current) return

    chartRef.current.applyOptions({
      layout: {
        background: { type: ColorType.Solid, color: chartTheme.backgroundColor },
        textColor: chartTheme.textColor,
      },
      grid: {
        vertLines: { color: chartTheme.gridColor },
        horzLines: { color: chartTheme.gridColor },
      },
      rightPriceScale: { borderColor: chartTheme.borderColor },
      timeScale: { borderColor: chartTheme.borderColor },
    })
  }, [chartTheme])

  // Create or update main series based on chart type
  useEffect(() => {
    if (!chartRef.current || transformedData.length === 0) return

    const chart = chartRef.current

    // Remove existing main series
    if (mainSeriesRef.current) {
      chart.removeSeries(mainSeriesRef.current)
      mainSeriesRef.current = null
    }

    // Create new series based on chart type
    if (chartType === 'line') {
      const series = chart.addLineSeries({
        color: chartTheme.upColor,
        lineWidth: 2,
      })
      const lineData: LineData[] = transformedData.map((d) => ({
        time: d.time as Time,
        value: d.close,
      }))
      series.setData(lineData)
      mainSeriesRef.current = series
    } else if (chartType === 'area') {
      const series = chart.addAreaSeries({
        topColor: `${chartTheme.upColor}50`,
        bottomColor: `${chartTheme.upColor}10`,
        lineColor: chartTheme.upColor,
        lineWidth: 2,
      })
      const areaData: LineData[] = transformedData.map((d) => ({
        time: d.time as Time,
        value: d.close,
      }))
      series.setData(areaData)
      mainSeriesRef.current = series
    } else if (chartType === 'ohlc') {
      const series = chart.addBarSeries({
        upColor: chartTheme.upColor,
        downColor: chartTheme.downColor,
      })
      const barData = transformedData.map((d) => ({
        time: d.time as Time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }))
      series.setData(barData)
      mainSeriesRef.current = series
    } else {
      // Candlestick (default, also used for Heikin-Ashi)
      const series = chart.addCandlestickSeries({
        upColor: chartTheme.upColor,
        downColor: chartTheme.downColor,
        borderUpColor: chartTheme.upColor,
        borderDownColor: chartTheme.downColor,
        wickUpColor: chartTheme.upColor,
        wickDownColor: chartTheme.downColor,
      })
      const candleData: CandlestickData[] = transformedData.map((d) => ({
        time: d.time as Time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }))
      series.setData(candleData)
      mainSeriesRef.current = series
    }

    // Fit content
    chart.timeScale().fitContent()
  }, [transformedData, chartType, chartTheme])

  // Add/update volume series
  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return

    const chart = chartRef.current

    // Remove existing volume series
    if (volumeSeriesRef.current) {
      chart.removeSeries(volumeSeriesRef.current)
      volumeSeriesRef.current = null
    }

    if (!showVolume) return

    // Create volume series
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    })

    chart.priceScale('volume').applyOptions({
      scaleMargins: {
        top: 0.85,
        bottom: 0,
      },
    })

    const volumeData: HistogramData[] = data.map((d, i) => {
      const prevClose = i > 0 ? data[i - 1].close : d.open
      return {
        time: d.time as Time,
        value: d.volume,
        color: d.close >= prevClose ? `${chartTheme.upColor}80` : `${chartTheme.downColor}80`,
      }
    })

    volumeSeries.setData(volumeData)
    volumeSeriesRef.current = volumeSeries
  }, [data, showVolume, chartTheme])

  // Add/update indicator overlays
  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return

    const chart = chartRef.current

    // Remove existing indicator series
    indicatorSeriesRef.current.forEach((series) => {
      chart.removeSeries(series)
    })
    indicatorSeriesRef.current.clear()

    // Remove RSI pane
    if (rsiPaneRef.current) {
      chart.removeSeries(rsiPaneRef.current)
      rsiPaneRef.current = null
    }

    // Remove MACD series
    if (macdSeriesRef.current.macd) {
      chart.removeSeries(macdSeriesRef.current.macd)
      macdSeriesRef.current.macd = null
    }
    if (macdSeriesRef.current.signal) {
      chart.removeSeries(macdSeriesRef.current.signal)
      macdSeriesRef.current.signal = null
    }
    if (macdSeriesRef.current.histogram) {
      chart.removeSeries(macdSeriesRef.current.histogram)
      macdSeriesRef.current.histogram = null
    }

    // Add new indicators
    indicators.forEach((indicator) => {
      if (!indicator.visible) return

      switch (indicator.type) {
        case 'sma': {
          const smaData = calculateSMA(data, indicator.params.period || 20)
          if (smaData.length === 0) return

          const series = chart.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            priceLineVisible: false,
            lastValueVisible: false,
          })
          series.setData(smaData.map((d) => ({ time: d.time as Time, value: d.value })))
          indicatorSeriesRef.current.set(indicator.id, series)
          break
        }
        case 'ema': {
          const emaData = calculateEMA(data, indicator.params.period || 12)
          if (emaData.length === 0) return

          const series = chart.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            priceLineVisible: false,
            lastValueVisible: false,
          })
          series.setData(emaData.map((d) => ({ time: d.time as Time, value: d.value })))
          indicatorSeriesRef.current.set(indicator.id, series)
          break
        }
        case 'bollinger': {
          const bbData = calculateBollingerBands(
            data,
            indicator.params.period || 20,
            indicator.params.stdDev || 2
          )
          if (bbData.length === 0) return

          // Upper band
          const upperSeries = chart.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            priceLineVisible: false,
            lastValueVisible: false,
          })
          upperSeries.setData(bbData.map((d) => ({ time: d.time as Time, value: d.upper })))
          indicatorSeriesRef.current.set(`${indicator.id}-upper`, upperSeries)

          // Middle band
          const middleSeries = chart.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            priceLineVisible: false,
            lastValueVisible: false,
          })
          middleSeries.setData(bbData.map((d) => ({ time: d.time as Time, value: d.middle })))
          indicatorSeriesRef.current.set(`${indicator.id}-middle`, middleSeries)

          // Lower band
          const lowerSeries = chart.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            priceLineVisible: false,
            lastValueVisible: false,
          })
          lowerSeries.setData(bbData.map((d) => ({ time: d.time as Time, value: d.lower })))
          indicatorSeriesRef.current.set(`${indicator.id}-lower`, lowerSeries)
          break
        }
        case 'rsi': {
          const rsiData = calculateRSI(data, indicator.params.period || 14)
          if (rsiData.length === 0) return

          const series = chart.addLineSeries({
            color: indicator.color,
            lineWidth: 1,
            priceScaleId: 'rsi',
            priceLineVisible: false,
            lastValueVisible: true,
          })

          chart.priceScale('rsi').applyOptions({
            scaleMargins: {
              top: 0.8,
              bottom: 0,
            },
            autoScale: false,
          })

          series.setData(rsiData.map((d) => ({ time: d.time as Time, value: d.value })))
          rsiPaneRef.current = series
          break
        }
        case 'macd': {
          const macdData = calculateMACD(
            data,
            indicator.params.fastPeriod || 12,
            indicator.params.slowPeriod || 26,
            indicator.params.signalPeriod || 9
          )
          if (macdData.length === 0) return

          // MACD line
          const macdSeries = chart.addLineSeries({
            color: '#2196F3',
            lineWidth: 1,
            priceScaleId: 'macd',
            priceLineVisible: false,
            lastValueVisible: false,
          })
          macdSeries.setData(macdData.map((d) => ({ time: d.time as Time, value: d.macd })))
          macdSeriesRef.current.macd = macdSeries

          // Signal line
          const signalSeries = chart.addLineSeries({
            color: '#FF9800',
            lineWidth: 1,
            priceScaleId: 'macd',
            priceLineVisible: false,
            lastValueVisible: false,
          })
          signalSeries.setData(macdData.map((d) => ({ time: d.time as Time, value: d.signal })))
          macdSeriesRef.current.signal = signalSeries

          // Histogram
          const histogramSeries = chart.addHistogramSeries({
            priceScaleId: 'macd',
          })
          histogramSeries.setData(
            macdData.map((d) => ({
              time: d.time as Time,
              value: d.histogram,
              color: d.histogram >= 0 ? '#26a69a80' : '#ef535080',
            }))
          )
          macdSeriesRef.current.histogram = histogramSeries

          chart.priceScale('macd').applyOptions({
            scaleMargins: {
              top: 0.85,
              bottom: 0,
            },
          })
          break
        }
      }
    })
  }, [data, indicators])

  // Loading state
  if (loading) {
    return (
      <div
        className="flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded"
        style={{ height }}
      >
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-solid border-blue-600 dark:border-blue-400 border-r-transparent mb-2" />
          <p className="text-sm text-gray-600 dark:text-gray-300">차트 로딩 중...</p>
        </div>
      </div>
    )
  }

  // No data state
  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded"
        style={{ height }}
      >
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">차트 데이터가 없습니다</p>
        </div>
      </div>
    )
  }

  return (
    <div
      ref={chartContainerRef}
      className="w-full"
      style={{ height }}
      data-symbol={symbol}
    />
  )
}
