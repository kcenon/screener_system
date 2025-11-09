import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="max-w-md mx-auto px-4 py-12 text-center">
      <h2 className="text-4xl font-bold text-gray-900 mb-4">404</h2>
      <p className="text-xl text-gray-600 mb-8">Page not found</p>
      <Link
        to="/"
        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-block"
      >
        Go Home
      </Link>
    </div>
  )
}
