import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { Navbar, Breadcrumb } from './components/navigation'
import { GlobalMarketBar } from './components/layout'
import { useTheme } from './hooks/useTheme'

function App() {
  // Initialize theme on mount
  useEffect(() => {
    useTheme.getState().initTheme()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <Navbar />
      <GlobalMarketBar />
      <Breadcrumb />
      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default App
