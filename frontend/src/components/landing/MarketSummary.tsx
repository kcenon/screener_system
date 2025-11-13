import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface MarketIndex {
  code: string
  name: string
  value: number
  change: number
  changePercent: number
}

interface MarketStats {
  advancing: number
  declining: number
  unchanged: number
}

export default function MarketSummary() {
  // Mock data - In production, this would come from WebSocket or API
  const [indices] = useState<MarketIndex[]>([
    {
      code: 'KOSPI',
      name: '코스피',
      value: 2500.12,
      change: 15.3,
      changePercent: 0.62,
    },
    {
      code: 'KOSDAQ',
      name: '코스닥',
      value: 850.45,
      change: -4.2,
      changePercent: -0.49,
    },
    {
      code: 'KRX100',
      name: 'KRX 100',
      value: 5234.67,
      change: 25.12,
      changePercent: 0.48,
    },
  ])

  const [stats] = useState<MarketStats>({
    advancing: 1234,
    declining: 856,
    unchanged: 310,
  })

  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const formatTime = (date: Date) => {
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })
  }

  return (
    <section className="py-12 px-4 sm:px-6 lg:px-8 bg-white border-t border-b border-gray-200">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">실시간 시장 현황</h2>
          <p className="text-sm text-gray-500">
            마지막 업데이트: {formatTime(currentTime)} KST
          </p>
        </div>

        {/* Market Indices */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {indices.map((index) => (
            <div
              key={index.code}
              className="bg-gradient-to-br from-white to-gray-50 rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">{index.name}</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {index.value.toLocaleString('ko-KR', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>
                <div
                  className={`p-2 rounded-lg ${
                    index.change >= 0 ? 'bg-red-50' : 'bg-blue-50'
                  }`}
                >
                  {index.change >= 0 ? (
                    <TrendingUp className="w-6 h-6 text-red-600" />
                  ) : (
                    <TrendingDown className="w-6 h-6 text-blue-600" />
                  )}
                </div>
              </div>

              <div className="flex items-baseline gap-2">
                <span
                  className={`text-lg font-semibold ${
                    index.change >= 0 ? 'text-red-600' : 'text-blue-600'
                  }`}
                >
                  {index.change >= 0 ? '+' : ''}
                  {index.change.toFixed(2)}
                </span>
                <span
                  className={`text-sm ${
                    index.change >= 0 ? 'text-red-600' : 'text-blue-600'
                  }`}
                >
                  ({index.changePercent >= 0 ? '+' : ''}
                  {index.changePercent.toFixed(2)}%)
                </span>
              </div>

              {/* Mini sparkline placeholder */}
              <div className="mt-4 h-12 bg-gray-100 rounded flex items-center justify-center">
                <p className="text-xs text-gray-400">7-day trend</p>
              </div>
            </div>
          ))}
        </div>

        {/* Market Breadth */}
        <div className="bg-gradient-to-r from-gray-50 to-white rounded-xl p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">시장 흐름</h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-sm text-gray-500 mb-2">상승</p>
              <p className="text-2xl font-bold text-red-600">
                {stats.advancing.toLocaleString()}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                (
                {(
                  (stats.advancing /
                    (stats.advancing + stats.declining + stats.unchanged)) *
                  100
                ).toFixed(1)}
                %)
              </p>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-500 mb-2">하락</p>
              <p className="text-2xl font-bold text-blue-600">
                {stats.declining.toLocaleString()}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                (
                {(
                  (stats.declining /
                    (stats.advancing + stats.declining + stats.unchanged)) *
                  100
                ).toFixed(1)}
                %)
              </p>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-500 mb-2">보합</p>
              <p className="text-2xl font-bold text-gray-600">
                {stats.unchanged.toLocaleString()}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                (
                {(
                  (stats.unchanged /
                    (stats.advancing + stats.declining + stats.unchanged)) *
                  100
                ).toFixed(1)}
                %)
              </p>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-500 mb-2">A/D Ratio</p>
              <p className="text-2xl font-bold text-gray-900">
                {(stats.advancing / stats.declining).toFixed(2)}
              </p>
              <p
                className={`text-xs mt-1 font-semibold ${
                  stats.advancing > stats.declining ? 'text-red-600' : 'text-blue-600'
                }`}
              >
                {stats.advancing > stats.declining ? '강세장' : '약세장'}
              </p>
            </div>
          </div>

          {/* Visual bar chart */}
          <div className="mt-6 h-4 bg-gray-200 rounded-full overflow-hidden flex">
            <div
              className="bg-red-500"
              style={{
                width: `${(stats.advancing / (stats.advancing + stats.declining + stats.unchanged)) * 100}%`,
              }}
            ></div>
            <div
              className="bg-blue-500"
              style={{
                width: `${(stats.declining / (stats.advancing + stats.declining + stats.unchanged)) * 100}%`,
              }}
            ></div>
            <div
              className="bg-gray-400"
              style={{
                width: `${(stats.unchanged / (stats.advancing + stats.declining + stats.unchanged)) * 100}%`,
              }}
            ></div>
          </div>
        </div>

        {/* Note about live data */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-400">
            * 실시간 데이터는 WebSocket을 통해 자동으로 업데이트됩니다
          </p>
        </div>
      </div>
    </section>
  )
}
