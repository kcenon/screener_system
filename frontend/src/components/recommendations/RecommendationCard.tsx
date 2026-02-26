import React from 'react'
import { TrendingUp, TrendingDown, Info } from 'lucide-react'

interface RecommendationCardProps {
  recommendation: {
    stock_code: string
    company_name: string
    sector: string
    current_price: number
    recommendation_score: number
    confidence: number
    reasons: string[]
    ai_prediction: {
      direction: string
      probability: number
    }
    key_metrics: {
      per: number
      pbr: number
      dividend_yield: number
    }
  }
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
}) => {
  const isBullish = recommendation.ai_prediction.direction === 'bullish'
  const confidencePercent = (recommendation.confidence * 100).toFixed(0)

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
            {recommendation.stock_code}
            <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
              {recommendation.company_name}
            </span>
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {recommendation.sector}
          </p>
        </div>
        <div
          className={`flex items-center gap-1 px-2 py-1 rounded text-sm font-medium ${
            isBullish
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {isBullish ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
          {confidencePercent}% Conf.
        </div>
      </div>

      <div className="mb-4">
        <div className="text-2xl font-bold text-gray-900 dark:text-white">
          ${recommendation.current_price.toFixed(2)}
        </div>
      </div>

      <div className="space-y-2 mb-4">
        {recommendation.reasons.slice(0, 2).map((reason, idx) => (
          <div
            key={idx}
            className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300"
          >
            <Info size={16} className="mt-0.5 text-blue-500 shrink-0" />
            <span>{reason}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-gray-100 dark:border-gray-700">
        <div className="text-center">
          <div className="text-xs text-gray-500">PER</div>
          <div className="font-medium text-gray-900 dark:text-white">
            {recommendation.key_metrics.per}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">PBR</div>
          <div className="font-medium text-gray-900 dark:text-white">
            {recommendation.key_metrics.pbr}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">Div. Yield</div>
          <div className="font-medium text-gray-900 dark:text-white">
            {recommendation.key_metrics.dividend_yield}%
          </div>
        </div>
      </div>
    </div>
  )
}
