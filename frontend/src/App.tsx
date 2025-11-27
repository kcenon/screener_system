import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { Navbar, Breadcrumb } from './components/navigation'
import { GlobalMarketBar } from './components/layout'
import EmailVerificationBanner from './components/auth/EmailVerificationBanner'
import { OfflineIndicator } from './components/common/OfflineIndicator'
import { PWAUpdatePrompt } from './components/common/PWAUpdatePrompt'
import { PWAInstallPrompt } from './components/common/PWAInstallPrompt'
import { useTheme } from './hooks/useTheme'
import { usePageTracking } from './hooks/useAnalytics'
import { initializeCSSVariables } from './design-system/tokens'

function App() {
  // Track page views automatically
  usePageTracking()

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
      <EmailVerificationBanner />
      <GlobalMarketBar />
      <Breadcrumb />
      <main>
        <Outlet />
      </main>

      {/* PWA Components */}
      <OfflineIndicator />
      <PWAUpdatePrompt />
      <PWAInstallPrompt />
    </div>
  )
}

export default App
