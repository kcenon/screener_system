import { useParams } from 'react-router-dom'

export default function StockDetailPage() {
  const { code } = useParams<{ code: string }>()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Stock Detail: {code}
      </h2>
      <div className="bg-white p-6 rounded-lg shadow">
        <p className="text-gray-600">
          Stock detail page will be implemented in FE-004
        </p>
      </div>
    </div>
  )
}
