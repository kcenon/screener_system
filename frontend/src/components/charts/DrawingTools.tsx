/**
 * Drawing Tools Component
 *
 * Manages drawing tools state and persistence.
 * Supports:
 * - Trendlines
 * - Horizontal lines (support/resistance)
 * - Fibonacci retracements
 * - Rectangles
 * - Text annotations
 */

import { useState, useEffect, useCallback } from 'react'
import { Trash2 } from 'lucide-react'
import type { Drawing, DrawingTool } from './types'
import { DRAWING_TOOL_LABELS } from './types'

interface DrawingToolsProps {
  drawings: Drawing[]
  onDrawingsChange: (drawings: Drawing[]) => void
}

const STORAGE_KEY_PREFIX = 'chart-drawings:'

export function useDrawings(symbol: string) {
  const [drawings, setDrawings] = useState<Drawing[]>(() => {
    if (typeof window === 'undefined') return []
    const saved = localStorage.getItem(`${STORAGE_KEY_PREFIX}${symbol}`)
    return saved ? JSON.parse(saved) : []
  })

  // Persist to localStorage
  useEffect(() => {
    localStorage.setItem(
      `${STORAGE_KEY_PREFIX}${symbol}`,
      JSON.stringify(drawings),
    )
  }, [symbol, drawings])

  const addDrawing = useCallback((drawing: Drawing) => {
    setDrawings(prev => [...prev, drawing])
  }, [])

  const removeDrawing = useCallback((id: string) => {
    setDrawings(prev => prev.filter(d => d.id !== id))
  }, [])

  const updateDrawing = useCallback((id: string, updates: Partial<Drawing>) => {
    setDrawings(prev => prev.map(d => (d.id === id ? { ...d, ...updates } : d)))
  }, [])

  const clearAll = useCallback(() => {
    setDrawings([])
  }, [])

  return {
    drawings,
    addDrawing,
    removeDrawing,
    updateDrawing,
    clearAll,
  }
}

export default function DrawingTools({
  drawings,
  onDrawingsChange,
}: DrawingToolsProps) {
  const [selectedDrawing, setSelectedDrawing] = useState<string | null>(null)

  const handleDelete = (id: string) => {
    onDrawingsChange(drawings.filter(d => d.id !== id))
    if (selectedDrawing === id) {
      setSelectedDrawing(null)
    }
  }

  const handleClearAll = () => {
    onDrawingsChange([])
    setSelectedDrawing(null)
  }

  const handleColorChange = (id: string, color: string) => {
    onDrawingsChange(drawings.map(d => (d.id === id ? { ...d, color } : d)))
  }

  if (drawings.length === 0) {
    return null
  }

  return (
    <div className="absolute top-2 right-2 z-10">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2 min-w-[180px]">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300">
            그리기 ({drawings.length})
          </h4>
          <button
            onClick={handleClearAll}
            className="text-xs text-red-500 hover:text-red-600 flex items-center gap-1"
          >
            <Trash2 className="w-3 h-3" />
            전체 삭제
          </button>
        </div>

        <div className="space-y-1 max-h-32 overflow-y-auto">
          {drawings.map(drawing => (
            <div
              key={drawing.id}
              className={`flex items-center gap-2 px-2 py-1 rounded text-xs ${
                selectedDrawing === drawing.id
                  ? 'bg-blue-50 dark:bg-blue-900/20'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
              onClick={() => setSelectedDrawing(drawing.id)}
            >
              <div
                className="w-3 h-3 rounded"
                style={{ backgroundColor: drawing.color }}
              />
              <span className="flex-1 text-gray-700 dark:text-gray-300 truncate">
                {DRAWING_TOOL_LABELS[drawing.type]}
                {drawing.label && `: ${drawing.label}`}
              </span>
              <input
                type="color"
                value={drawing.color}
                onChange={e => handleColorChange(drawing.id, e.target.value)}
                className="w-4 h-4 rounded cursor-pointer"
                onClick={e => e.stopPropagation()}
              />
              <button
                onClick={e => {
                  e.stopPropagation()
                  handleDelete(drawing.id)
                }}
                className="p-0.5 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

/**
 * Create a new drawing based on tool type and points
 */
export function createDrawing(
  tool: DrawingTool,
  points: { time: string; price: number }[],
  color: string = '#2196F3',
): Drawing | null {
  if (tool === 'none' || points.length === 0) return null

  const id = `drawing-${Date.now()}`

  switch (tool) {
    case 'horizontal':
      if (points.length < 1) return null
      return {
        id,
        type: 'horizontal',
        points: [points[0]],
        color,
        lineWidth: 1,
        label: `${points[0].price.toLocaleString()}`,
      }

    case 'trendline':
      if (points.length < 2) return null
      return {
        id,
        type: 'trendline',
        points: [points[0], points[1]],
        color,
        lineWidth: 1,
      }

    case 'fibonacci':
      if (points.length < 2) return null
      return {
        id,
        type: 'fibonacci',
        points: [points[0], points[1]],
        color,
        lineWidth: 1,
      }

    case 'rectangle':
      if (points.length < 2) return null
      return {
        id,
        type: 'rectangle',
        points: [points[0], points[1]],
        color: `${color}40`, // Semi-transparent
        lineWidth: 1,
      }

    case 'text':
      if (points.length < 1) return null
      return {
        id,
        type: 'text',
        points: [points[0]],
        color,
        lineWidth: 1,
        label: 'Note',
      }

    default:
      return null
  }
}

/**
 * Calculate Fibonacci retracement levels
 */
export function calculateFibonacciLevels(
  startPrice: number,
  endPrice: number,
): { level: number; price: number; label: string }[] {
  const diff = endPrice - startPrice
  const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]

  return levels.map(level => ({
    level,
    price: startPrice + diff * level,
    label: `${(level * 100).toFixed(1)}%`,
  }))
}
