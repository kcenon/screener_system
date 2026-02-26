import { useEffect, useState } from 'react'

interface Statistic {
  label: string
  value: string
  description: string
  delay: number
}

export default function StatisticsSection() {
  const [isVisible, setIsVisible] = useState(false)

  const statistics: Statistic[] = [
    {
      label: '분석 가능한 종목',
      value: '2,400+',
      description: 'KOSPI & KOSDAQ',
      delay: 0,
    },
    {
      label: '기술 지표',
      value: '200+',
      description: 'Technical Indicators',
      delay: 100,
    },
    {
      label: '쿼리 성능',
      value: '<500ms',
      description: 'Average Response Time',
      delay: 200,
    },
    {
      label: '실시간 업데이트',
      value: '24/7',
      description: 'Real-time Data',
      delay: 300,
    },
  ]

  useEffect(() => {
    // Trigger animation when component mounts
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 dark:from-blue-900 dark:via-blue-950 dark:to-gray-900 text-white transition-all">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">플랫폼 통계</h2>
          <p className="text-xl text-blue-100 dark:text-blue-200">
            신뢰할 수 있는 데이터와 빠른 성능
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {statistics.map((stat, index) => (
            <div
              key={index}
              className={`text-center transform transition-all duration-700 ${
                isVisible
                  ? 'translate-y-0 opacity-100'
                  : 'translate-y-10 opacity-0'
              }`}
              style={{ transitionDelay: `${stat.delay}ms` }}
            >
              <div className="bg-white/10 dark:bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/20 dark:border-white/10 hover:bg-white/20 dark:hover:bg-white/10 transition-colors">
                <div className="text-5xl font-bold mb-2 bg-gradient-to-r from-white to-blue-100 dark:to-blue-300 bg-clip-text text-transparent">
                  {stat.value}
                </div>
                <div className="text-lg font-semibold mb-2">{stat.label}</div>
                <div className="text-sm text-blue-100 dark:text-blue-200">
                  {stat.description}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Data Sources */}
        <div className="mt-16 pt-12 border-t border-white/20 dark:border-white/10">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-semibold mb-4">데이터 출처</h3>
            <p className="text-blue-100 dark:text-blue-200">
              신뢰할 수 있는 공식 데이터를 사용합니다
            </p>
          </div>

          <div className="flex flex-wrap justify-center items-center gap-8">
            <div className="bg-white/10 dark:bg-white/5 backdrop-blur-sm px-8 py-4 rounded-lg border border-white/20 dark:border-white/10">
              <p className="text-lg font-semibold">한국거래소 (KRX)</p>
            </div>
            <div className="bg-white/10 dark:bg-white/5 backdrop-blur-sm px-8 py-4 rounded-lg border border-white/20 dark:border-white/10">
              <p className="text-lg font-semibold">에프앤가이드 (F&Guide)</p>
            </div>
            <div className="bg-white/10 dark:bg-white/5 backdrop-blur-sm px-8 py-4 rounded-lg border border-white/20 dark:border-white/10">
              <p className="text-lg font-semibold">한국투자증권 (KIS) API</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
