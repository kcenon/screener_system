import type { StockDetail } from '@/types'

interface FinancialsTabProps {
  stock: StockDetail
}

/**
 * Financials Tab Component
 *
 * Displays:
 * - Financial statement tables (quarterly/annual)
 * - Revenue, profit, cash flow trends
 * - Balance sheet overview
 *
 * TODO: Full implementation in next phase
 *
 * @example
 * ```tsx
 * <FinancialsTab stock={stockData} />
 * ```
 */
export default function FinancialsTab({ stock }: FinancialsTabProps) {
  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          🚧 재무 탭 구현 예정
        </h3>
        <p className="text-sm text-blue-700 mb-4">
          이 탭은 다음 단계에서 구현됩니다:
        </p>
        <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
          <li>분기별/연간 재무제표</li>
          <li>매출, 영업이익, 순이익 추이 차트</li>
          <li>자산, 부채, 자본 구조</li>
          <li>현금흐름표 (영업/투자/재무 활동)</li>
        </ul>
      </div>

      {/* Temporary: Show basic financial metrics */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          기본 재무 정보
        </h3>
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">영업이익률</dt>
            <dd className="mt-1 text-lg font-semibold text-gray-900">
              {stock.operating_margin
                ? `${stock.operating_margin.toFixed(2)}%`
                : 'N/A'}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">순이익률</dt>
            <dd className="mt-1 text-lg font-semibold text-gray-900">
              {stock.net_margin ? `${stock.net_margin.toFixed(2)}%` : 'N/A'}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">부채비율</dt>
            <dd className="mt-1 text-lg font-semibold text-gray-900">
              {stock.debt_to_equity
                ? `${stock.debt_to_equity.toFixed(0)}%`
                : 'N/A'}
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">유동비율</dt>
            <dd className="mt-1 text-lg font-semibold text-gray-900">
              {stock.current_ratio
                ? `${stock.current_ratio.toFixed(0)}%`
                : 'N/A'}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  )
}
