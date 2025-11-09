import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Stock Screening Platform
        </h2>
        <p className="text-xl text-gray-600 mb-8">
          한국 주식 시장 (KOSPI/KOSDAQ) 종합 분석 플랫폼
        </p>
        <div className="flex justify-center gap-4">
          <Link
            to="/screener"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Screening
          </Link>
          <Link
            to="/login"
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Login
          </Link>
        </div>
      </div>
    </div>
  )
}
