/**
 * Indicator Panel Component
 *
 * Panel for adding, configuring, and removing technical indicators.
 * Supports:
 * - SMA, EMA (Moving Averages)
 * - Bollinger Bands
 * - RSI, MACD, Stochastic
 */

import { useState } from 'react'
import { Plus, X, ChevronDown, ChevronUp, Eye, EyeOff } from 'lucide-react'
import type { IndicatorConfig, IndicatorType } from './types'
import {
  INDICATOR_LABELS,
  DEFAULT_INDICATOR_COLORS,
  DEFAULT_INDICATOR_PARAMS,
} from './types'

interface IndicatorPanelProps {
  indicators: IndicatorConfig[]
  onAddIndicator: (indicator: IndicatorConfig) => void
  onRemoveIndicator: (id: string) => void
  onUpdateIndicator: (id: string, updates: Partial<IndicatorConfig>) => void
  onClose: () => void
}

const INDICATOR_GROUPS = {
  overlay: ['sma', 'ema', 'bollinger'] as IndicatorType[],
  oscillator: ['rsi', 'macd', 'stochastic'] as IndicatorType[],
}

export default function IndicatorPanel({
  indicators,
  onAddIndicator,
  onRemoveIndicator,
  onUpdateIndicator,
  onClose,
}: IndicatorPanelProps) {
  const [expandedIndicator, setExpandedIndicator] = useState<string | null>(null)

  const handleAddIndicator = (type: IndicatorType) => {
    const newIndicator: IndicatorConfig = {
      id: `${type}-${Date.now()}`,
      type,
      params: { ...DEFAULT_INDICATOR_PARAMS[type] },
      color: DEFAULT_INDICATOR_COLORS[type],
      visible: true,
    }
    onAddIndicator(newIndicator)
  }

  const toggleExpand = (id: string) => {
    setExpandedIndicator(expandedIndicator === id ? null : id)
  }

  const handleParamChange = (id: string, paramName: string, value: number) => {
    const indicator = indicators.find((i) => i.id === id)
    if (indicator) {
      onUpdateIndicator(id, {
        params: { ...indicator.params, [paramName]: value },
      })
    }
  }

  const renderParamInputs = (indicator: IndicatorConfig) => {
    const params = Object.entries(indicator.params)
    if (params.length === 0) return null

    return (
      <div className="mt-2 space-y-2">
        {params.map(([key, value]) => (
          <div key={key} className="flex items-center gap-2">
            <label className="text-xs text-gray-600 dark:text-gray-400 w-20 capitalize">
              {key.replace(/([A-Z])/g, ' $1').trim()}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleParamChange(indicator.id, key, Number(e.target.value))}
              className="flex-1 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              min={1}
              max={200}
            />
          </div>
        ))}
        {/* Color picker */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-600 dark:text-gray-400 w-20">Color</label>
          <input
            type="color"
            value={indicator.color}
            onChange={(e) => onUpdateIndicator(indicator.id, { color: e.target.value })}
            className="w-8 h-6 rounded cursor-pointer"
          />
        </div>
      </div>
    )
  }

  return (
    <div className="w-64 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">기술적 지표</h3>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Active Indicators */}
      <div className="flex-1 overflow-y-auto">
        {indicators.length > 0 && (
          <div className="p-2 border-b border-gray-200 dark:border-gray-700">
            <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
              활성 지표
            </h4>
            <div className="space-y-1">
              {indicators.map((indicator) => (
                <div
                  key={indicator.id}
                  className="bg-gray-50 dark:bg-gray-700 rounded-md overflow-hidden"
                >
                  <div className="flex items-center gap-2 px-2 py-1.5">
                    <button
                      onClick={() => onUpdateIndicator(indicator.id, { visible: !indicator.visible })}
                      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
                    >
                      {indicator.visible ? (
                        <Eye className="w-3.5 h-3.5 text-gray-600 dark:text-gray-400" />
                      ) : (
                        <EyeOff className="w-3.5 h-3.5 text-gray-400 dark:text-gray-500" />
                      )}
                    </button>
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: indicator.color }}
                    />
                    <span className="flex-1 text-xs font-medium text-gray-700 dark:text-gray-300">
                      {INDICATOR_LABELS[indicator.type]}
                      {indicator.params.period && ` (${indicator.params.period})`}
                    </span>
                    <button
                      onClick={() => toggleExpand(indicator.id)}
                      className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
                    >
                      {expandedIndicator === indicator.id ? (
                        <ChevronUp className="w-3.5 h-3.5 text-gray-500" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5 text-gray-500" />
                      )}
                    </button>
                    <button
                      onClick={() => onRemoveIndicator(indicator.id)}
                      className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  {expandedIndicator === indicator.id && (
                    <div className="px-2 pb-2">
                      {renderParamInputs(indicator)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Add Indicators */}
        <div className="p-2">
          {/* Overlay Indicators */}
          <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
            오버레이 지표
          </h4>
          <div className="grid grid-cols-2 gap-1 mb-3">
            {INDICATOR_GROUPS.overlay.map((type) => (
              <button
                key={type}
                onClick={() => handleAddIndicator(type)}
                className="flex items-center gap-1 px-2 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
              >
                <Plus className="w-3 h-3" />
                {INDICATOR_LABELS[type]}
              </button>
            ))}
          </div>

          {/* Oscillator Indicators */}
          <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
            오실레이터 지표
          </h4>
          <div className="grid grid-cols-2 gap-1">
            {INDICATOR_GROUPS.oscillator.map((type) => (
              <button
                key={type}
                onClick={() => handleAddIndicator(type)}
                className="flex items-center gap-1 px-2 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
              >
                <Plus className="w-3 h-3" />
                {INDICATOR_LABELS[type]}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Presets */}
      <div className="p-2 border-t border-gray-200 dark:border-gray-700">
        <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
          빠른 설정
        </h4>
        <div className="space-y-1">
          <button
            onClick={() => {
              // Clear existing and add common setup
              indicators.forEach((i) => onRemoveIndicator(i.id))
              handleAddIndicator('sma')
              setTimeout(() => {
                handleAddIndicator('ema')
              }, 10)
            }}
            className="w-full px-2 py-1.5 text-xs text-left text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
          >
            📊 이동평균선 (SMA + EMA)
          </button>
          <button
            onClick={() => {
              indicators.forEach((i) => onRemoveIndicator(i.id))
              handleAddIndicator('bollinger')
              setTimeout(() => {
                handleAddIndicator('rsi')
              }, 10)
            }}
            className="w-full px-2 py-1.5 text-xs text-left text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
          >
            📈 볼린저밴드 + RSI
          </button>
          <button
            onClick={() => {
              indicators.forEach((i) => onRemoveIndicator(i.id))
              handleAddIndicator('macd')
            }}
            className="w-full px-2 py-1.5 text-xs text-left text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
          >
            📉 MACD
          </button>
        </div>
      </div>
    </div>
  )
}
