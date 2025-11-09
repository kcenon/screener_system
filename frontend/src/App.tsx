import { Outlet } from 'react-router-dom'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Stock Screening Platform
          </h1>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default App
