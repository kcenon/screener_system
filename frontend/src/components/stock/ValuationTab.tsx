import type { StockDetail } from '@/types'
import MetricCard from './MetricCard'

interface ValuationTabProps {
  stock: StockDetail
}

/**
 * Valuation Tab Component
 *
 * Displays:
 * - Valuation metrics table
 * - Historical valuation trends
 * - Peer comparison (Phase 2)
 *
 * @example
 * ```tsx
 * <ValuationTab stock={stockData} />
 * ```
 */
export default function ValuationTab({ stock }: ValuationTabProps) {
  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          🚧 밸류에이션 탭 구현 예정
        </h3>
        <p className="text-sm text-blue-700 mb-4">
          이 탭은 다음 단계에서 구현됩니다:
        </p>
        <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
          <li>밸류에이션 지표 히스토리 차트</li>
          <li>업종 평균 대비 비교</li>
          <li>동종 업계 기업 비교</li>
        </ul>
      </div>

      {/* Current Valuation Metrics */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          현재 밸류에이션
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <MetricCard
            label="PER"
            value={stock.per}
            unit="배"
            tooltip="주가수익비율"
          />
          <MetricCard
            label="PBR"
            value={stock.pbr}
            unit="배"
            tooltip="주가순자산비율"
          />
          <MetricCard
            label="PSR"
            value={stock.psr}
            unit="배"
            tooltip="주가매출액비율"
          />
          <MetricCard
            label="PCR"
            value={stock.pcr}
            unit="배"
            tooltip="주가현금흐름비율"
          />
          <MetricCard
            label="배당수익률"
            value={stock.dividend_yield}
            unit="%"
            tooltip="배당금/주가"
          />
        </div>
      </section>
    </div>
  )
}
