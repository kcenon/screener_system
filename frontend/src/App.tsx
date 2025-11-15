import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { Navbar, Breadcrumb } from './components/navigation'
import { GlobalMarketBar } from './components/layout'
import { useTheme } from './hooks/useTheme'
import { initializeCSSVariables } from './design-system/tokens'

function App() {
  // Initialize theme and CSS variables on mount
  useEffect(() => {
    const { initTheme, resolvedTheme } = useTheme.getState()
    initTheme()

    // Initialize CSS variables for color tokens
    initializeCSSVariables(resolvedTheme)
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
