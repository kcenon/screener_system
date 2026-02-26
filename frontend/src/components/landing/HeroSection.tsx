import { Link } from 'react-router-dom'
import { TrendingUp, BarChart3, Zap } from 'lucide-react'

export default function HeroSection() {
  return (
    <section className="relative bg-gradient-to-br from-blue-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-20 px-4 sm:px-6 lg:px-8 transition-colors">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          {/* Main Headline */}
          <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 dark:text-gray-100 mb-6 leading-tight transition-colors">
            한국 주식 시장,
            <br />
            <span className="text-blue-600 dark:text-blue-400">
              데이터로 분석하세요
            </span>
          </h1>

          {/* Subheading with key features */}
          <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-400 mb-4 max-w-3xl mx-auto transition-colors">
            200+ 기술 지표, 실시간 데이터, 고급 스크리닝으로
            <br />
            최적의 투자 기회를 발견하세요
          </p>

          {/* Feature Highlights */}
          <div className="flex flex-wrap justify-center gap-6 mb-10 text-sm sm:text-base">
            <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300 transition-colors">
              <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span>2,400+ 종목 분석</span>
            </div>
            <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300 transition-colors">
              <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span>200+ 기술 지표</span>
            </div>
            <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300 transition-colors">
              <Zap className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span>500ms 이하 쿼리 성능</span>
            </div>
          </div>

          {/* Call-to-Action Buttons */}
          <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
            <Link
              to="/screener"
              className="px-8 py-4 bg-blue-600 dark:bg-blue-500 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              무료로 시작하기
            </Link>
            <Link
              to="/market"
              className="px-8 py-4 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 text-lg font-semibold rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 shadow-md hover:shadow-lg border-2 border-blue-600 dark:border-blue-400"
            >
              시장 둘러보기
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-500 dark:text-gray-400 transition-colors">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              <span>회원가입 불필요</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              <span>신용카드 불필요</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              <span>즉시 사용 가능</span>
            </div>
          </div>
        </div>

        {/* Visual Element Placeholder */}
        <div className="mt-16 relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-600 dark:from-blue-500 dark:to-blue-700 rounded-2xl transform rotate-1 opacity-10 dark:opacity-20"></div>
          <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl dark:shadow-blue-900/20 p-8 border border-gray-200 dark:border-gray-700 transition-colors">
            <div className="aspect-video bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-lg flex items-center justify-center transition-colors">
              <p className="text-gray-400 dark:text-gray-500 text-lg">
                Platform Preview (Chart/Screenshot Placeholder)
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Background decoration */}
      <div className="absolute top-0 left-0 right-0 h-full overflow-hidden -z-10">
        <div className="absolute top-20 right-20 w-72 h-72 bg-blue-200 dark:bg-blue-900 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-20 dark:opacity-10 animate-blob"></div>
        <div className="absolute bottom-20 left-20 w-72 h-72 bg-purple-200 dark:bg-purple-900 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-20 dark:opacity-10 animate-blob animation-delay-2000"></div>
      </div>

      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </section>
  )
}
