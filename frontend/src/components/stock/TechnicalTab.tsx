import type { StockDetail } from '@/types'
import MetricCard from './MetricCard'

interface TechnicalTabProps {
  stock: StockDetail
}

/**
 * Technical Tab Component
 *
 * Displays:
 * - Price momentum indicators (1D, 1W, 1M, 3M, 6M, 1Y)
 * - Volume analysis
 * - Moving averages
 *
 * @example
 * ```tsx
 * <TechnicalTab stock={stockData} />
 * ```
 */
export default function TechnicalTab({ stock }: TechnicalTabProps) {
  return (
    <div className="space-y-6">
      {/* Price Momentum */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          가격 모멘텀
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <MetricCard
            label="1일"
            value={stock.price_change_1d}
            unit="%"
            variant={
              stock.price_change_1d && stock.price_change_1d > 0
                ? 'positive'
                : stock.price_change_1d && stock.price_change_1d < 0
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="1주"
            value={stock.price_change_1w}
            unit="%"
            variant={
              stock.price_change_1w && stock.price_change_1w > 0
                ? 'positive'
                : stock.price_change_1w && stock.price_change_1w < 0
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="1개월"
            value={stock.price_change_1m}
            unit="%"
            variant={
              stock.price_change_1m && stock.price_change_1m > 0
                ? 'positive'
                : stock.price_change_1m && stock.price_change_1m < 0
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="3개월"
            value={stock.price_change_3m}
            unit="%"
            variant={
              stock.price_change_3m && stock.price_change_3m > 0
                ? 'positive'
                : stock.price_change_3m && stock.price_change_3m < 0
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="6개월"
            value={stock.price_change_6m}
            unit="%"
            variant={
              stock.price_change_6m && stock.price_change_6m > 0
                ? 'positive'
                : stock.price_change_6m && stock.price_change_6m < 0
                  ? 'negative'
                  : 'default'
            }
          />
          <MetricCard
            label="1년"
            value={stock.price_change_1y}
            unit="%"
            variant={
              stock.price_change_1y && stock.price_change_1y > 0
                ? 'positive'
                : stock.price_change_1y && stock.price_change_1y < 0
                  ? 'negative'
                  : 'default'
            }
          />
        </div>
      </section>

      {/* Volume Analysis */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          거래량 분석
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            label="현재 거래량"
            value={stock.current_volume}
            tooltip="당일 거래량"
          />
          <MetricCard
            label="거래량 급증률"
            value={stock.volume_surge_pct}
            unit="%"
            tooltip="평균 대비 거래량 증가율"
            variant={
              stock.volume_surge_pct && stock.volume_surge_pct > 50
                ? 'positive'
                : 'default'
            }
          />
        </div>
      </section>

      {/* Additional Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          🚧 추가 기술적 지표 구현 예정
        </h3>
        <p className="text-sm text-blue-700">
          이동평균선(MA20, MA60, MA120, MA200), RSI, MACD 등의 지표가 추가될
          예정입니다.
        </p>
      </div>
    </div>
  )
}
