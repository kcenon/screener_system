import type { StockDetail } from '@/types'
import MetricCard from './MetricCard'

interface OverviewTabProps {
  stock: StockDetail
}

/**
 * Overview Tab Component
 *
 * Displays:
 * - Key metrics (PER, PBR, PSR, ROE, ROA, etc.)
 * - Company information (sector, industry, listing date)
 * - Composite scores (Quality, Value, Growth, Overall)
 *
 * @example
 * ```tsx
 * <OverviewTab stock={stockData} />
 * ```
 */
export default function OverviewTab({ stock }: OverviewTabProps) {
  return (
    <div className="space-y-8">
      {/* Company Information */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">기업 정보</h2>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">섹터</dt>
              <dd className="mt-1 text-base text-gray-900">
                {stock.sector || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">산업</dt>
              <dd className="mt-1 text-base text-gray-900">
                {stock.industry || 'N/A'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">시장</dt>
              <dd className="mt-1 text-base text-gray-900">{stock.market}</dd>
            </div>
            {stock.metadata?.listing_date && (
              <div>
                <dt className="text-sm font-medium text-gray-500">상장일</dt>
                <dd className="mt-1 text-base text-gray-900">
                  {stock.metadata.listing_date}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </section>

      {/* Valuation Metrics */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">밸류에이션</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <MetricCard
            label="PER"
            value={stock.per}
            unit="배"
            tooltip="주가수익비율: 주가 / 주당순이익. 낮을수록 저평가"
          />
          <MetricCard
            label="PBR"
            value={stock.pbr}
            unit="배"
            tooltip="주가순자산비율: 주가 / 주당순자산. 1배 이하면 저평가"
          />
          <MetricCard
            label="PSR"
            value={stock.psr}
            unit="배"
            tooltip="주가매출액비율: 주가 / 주당매출액"
          />
          <MetricCard
            label="PCR"
            value={stock.pcr}
            unit="배"
            tooltip="주가현금흐름비율: 주가 / 주당현금흐름"
          />
          <MetricCard
            label="배당수익률"
            value={stock.dividend_yield}
            unit="%"
            tooltip="배당금 / 주가 × 100"
            variant={
              stock.dividend_yield && stock.dividend_yield > 3
                ? 'positive'
                : 'default'
            }
          />
        </div>
      </section>

      {/* Profitability Metrics */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">수익성</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <MetricCard
            label="ROE"
            value={stock.roe}
            unit="%"
            tooltip="자기자본이익률: 당기순이익 / 자기자본 × 100"
            variant={stock.roe && stock.roe > 10 ? 'positive' : 'default'}
          />
          <MetricCard
            label="ROA"
            value={stock.roa}
            unit="%"
            tooltip="총자산이익률: 당기순이익 / 총자산 × 100"
            variant={stock.roa && stock.roa > 5 ? 'positive' : 'default'}
          />
          <MetricCard
            label="ROIC"
            value={stock.roic}
            unit="%"
            tooltip="투하자본이익률: 영업이익 / 투하자본 × 100"
          />
          <MetricCard
            label="매출총이익률"
            value={stock.gross_margin}
            unit="%"
            tooltip="매출총이익 / 매출액 × 100"
          />
          <MetricCard
            label="영업이익률"
            value={stock.operating_margin}
            unit="%"
            tooltip="영업이익 / 매출액 × 100"
          />
          <MetricCard
            label="순이익률"
            value={stock.net_margin}
            unit="%"
            tooltip="당기순이익 / 매출액 × 100"
          />
        </div>
      </section>

      {/* Growth Metrics */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">성장성</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <MetricCard
            label="매출 성장률 (YoY)"
            value={stock.revenue_growth_yoy}
            unit="%"
            tooltip="전년 대비 매출액 성장률"
            variant={
              stock.revenue_growth_yoy && stock.revenue_growth_yoy > 0
                ? 'positive'
                : stock.revenue_growth_yoy && stock.revenue_growth_yoy < 0
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="이익 성장률 (YoY)"
            value={stock.profit_growth_yoy}
            unit="%"
            tooltip="전년 대비 당기순이익 성장률"
            variant={
              stock.profit_growth_yoy && stock.profit_growth_yoy > 0
                ? 'positive'
                : stock.profit_growth_yoy && stock.profit_growth_yoy < 0
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="EPS 성장률 (YoY)"
            value={stock.eps_growth_yoy}
            unit="%"
            tooltip="전년 대비 주당순이익 성장률"
            variant={
              stock.eps_growth_yoy && stock.eps_growth_yoy > 0
                ? 'positive'
                : stock.eps_growth_yoy && stock.eps_growth_yoy < 0
                  ? 'negative'
                  : 'default'
            }
          />
        </div>
      </section>

      {/* Stability Metrics */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">안정성</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <MetricCard
            label="부채비율"
            value={stock.debt_to_equity}
            unit="%"
            tooltip="부채 / 자기자본 × 100. 낮을수록 안정적"
            variant={
              stock.debt_to_equity && stock.debt_to_equity < 100
                ? 'positive'
                : stock.debt_to_equity && stock.debt_to_equity > 200
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="유동비율"
            value={stock.current_ratio}
            unit="%"
            tooltip="유동자산 / 유동부채 × 100. 100% 이상이면 양호"
            variant={
              stock.current_ratio && stock.current_ratio > 100
                ? 'positive'
                : 'default'
            }
          />
          <MetricCard
            label="알트만 Z-Score"
            value={stock.altman_z_score}
            tooltip="파산 위험도. 3 이상: 안전, 1.8-3: 주의, 1.8 미만: 위험"
            variant={
              stock.altman_z_score && stock.altman_z_score > 3
                ? 'positive'
                : stock.altman_z_score && stock.altman_z_score < 1.8
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="피오트로스키 F-Score"
            value={stock.piotroski_f_score}
            tooltip="재무 건전성 점수 (0-9). 7 이상: 우수, 4-6: 보통, 3 이하: 미흡"
            variant={
              stock.piotroski_f_score && stock.piotroski_f_score >= 7
                ? 'positive'
                : stock.piotroski_f_score && stock.piotroski_f_score <= 3
                  ? 'negative'
                  : 'default'
            }
          />
        </div>
      </section>

      {/* Composite Scores */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">종합 점수</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <MetricCard
            label="품질 점수"
            value={stock.quality_score}
            tooltip="재무 건전성 및 수익성 종합 점수 (0-100)"
            variant={
              stock.quality_score && stock.quality_score >= 70
                ? 'positive'
                : 'default'
            }
          />
          <MetricCard
            label="가치 점수"
            value={stock.value_score}
            tooltip="밸류에이션 매력도 점수 (0-100)"
            variant={
              stock.value_score && stock.value_score >= 70
                ? 'positive'
                : 'default'
            }
          />
          <MetricCard
            label="성장 점수"
            value={stock.growth_score}
            tooltip="성장성 종합 점수 (0-100)"
            variant={
              stock.growth_score && stock.growth_score >= 70
                ? 'positive'
                : 'default'
            }
          />
          <MetricCard
            label="모멘텀 점수"
            value={stock.momentum_score}
            tooltip="가격 모멘텀 종합 점수 (0-100)"
            variant={
              stock.momentum_score && stock.momentum_score >= 70
                ? 'positive'
                : 'default'
            }
          />
          <MetricCard
            label="종합 점수"
            value={stock.overall_score}
            tooltip="전체 종합 점수 (0-100)"
            variant={
              stock.overall_score && stock.overall_score >= 70
                ? 'positive'
                : 'default'
            }
          />
        </div>
      </section>

      {/* Indicator Update Date */}
      {stock.indicators_date && (
        <div className="text-sm text-gray-500 text-center">
          지표 업데이트: {stock.indicators_date}
        </div>
      )}
    </div>
  )
}
