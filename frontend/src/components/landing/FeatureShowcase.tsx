import { Search, BarChart3, TrendingUp, Briefcase, Bell, Zap } from 'lucide-react'

interface Feature {
  icon: React.ReactNode
  title: string
  description: string
  badge?: string
}

export default function FeatureShowcase() {
  const features: Feature[] = [
    {
      icon: <Search className="w-8 h-8" />,
      title: '고급 스크리닝',
      description:
        '200+ 기술 지표와 필터로 원하는 조건의 종목을 정확하게 검색하세요. 저장된 필터 프리셋으로 반복 작업을 간소화하세요.',
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: '실시간 데이터',
      description:
        'WebSocket 기반 실시간 시세 스트리밍으로 호가창, 체결가, 거래량을 즉시 확인하세요. 500ms 이하의 빠른 쿼리 성능을 제공합니다.',
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: '기술적 분석',
      description:
        'MACD, RSI, 볼린저 밴드 등 200+ 기술 지표를 차트와 함께 제공합니다. TradingView 라이브러리 기반의 전문가급 차트를 사용하세요.',
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: '종목 비교 분석',
      description:
        '최대 5개 종목을 동시에 비교하여 최적의 투자 선택을 하세요. 재무제표, 밸류에이션, 기술적 지표를 한눈에 비교합니다.',
      badge: 'Coming Soon',
    },
    {
      icon: <Briefcase className="w-8 h-8" />,
      title: '포트폴리오 관리',
      description:
        '관심 종목을 워치리스트에 추가하고 실시간으로 모니터링하세요. 여러 개의 워치리스트로 종목을 분류하고 관리할 수 있습니다.',
      badge: 'Coming Soon',
    },
    {
      icon: <Bell className="w-8 h-8" />,
      title: '가격 알림',
      description:
        '원하는 가격에 도달하면 알림을 받으세요. 이메일, 웹 푸시 등 다양한 알림 방식을 지원합니다.',
      badge: 'Coming Soon',
    },
  ]

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">강력한 기능들</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            전문 투자자부터 개인 투자자까지,
            <br />
            모두를 위한 종합 주식 분석 플랫폼
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative bg-white rounded-2xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-200 hover:border-blue-300"
            >
              {/* Badge */}
              {feature.badge && (
                <div className="absolute top-4 right-4">
                  <span className="px-3 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded-full border border-blue-200">
                    {feature.badge}
                  </span>
                </div>
              )}

              {/* Icon */}
              <div className="mb-6 inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl text-blue-600 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300">
                {feature.icon}
              </div>

              {/* Title */}
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {feature.title}
              </h3>

              {/* Description */}
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>

              {/* Hover Effect */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-400 to-blue-600 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 rounded-b-2xl"></div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="text-gray-600 mb-6">
            모든 기능을 무료로 사용해보세요. 신용카드 필요 없습니다.
          </p>
          <a
            href="/screener"
            className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
          >
            지금 시작하기
            <svg
              className="w-5 h-5 ml-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
          </a>
        </div>
      </div>
    </section>
  )
}
