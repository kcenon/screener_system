import { lazy, Suspense } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import PageLoader from './components/common/PageLoader'

// =============================================================================
// Eagerly loaded pages (small, fast loading)
// =============================================================================
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import EmailVerificationPage from './pages/EmailVerificationPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import OAuthCallbackPage from './pages/OAuthCallbackPage'
import NotFoundPage from './pages/NotFoundPage'

// =============================================================================
// Lazily loaded pages (heavy components, charts, complex logic)
// =============================================================================
const ScreenerPage = lazy(() => import('./pages/ScreenerPage'))
const StockDetailPage = lazy(() => import('./pages/StockDetailPage'))
const StockComparisonPage = lazy(() => import('./pages/StockComparisonPage'))
const WatchlistsPage = lazy(() => import('./pages/WatchlistsPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const MarketDashboardPage = lazy(() => import('./pages/MarketDashboardPage'))
const MarketOverviewPage = lazy(() => import('./pages/MarketOverviewPage'))
const PortfolioListPage = lazy(() => import('./pages/PortfolioListPage'))
const PortfolioDetailPage = lazy(() => import('./pages/PortfolioDetailPage'))
const AlertsPage = lazy(() => import('./pages/AlertsPage'))
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'))

/**
 * Wrapper component that provides Suspense boundary for lazy-loaded pages
 */
function LazyPage({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'screener',
        element: (
          <LazyPage>
            <ScreenerPage />
          </LazyPage>
        ),
      },
      {
        path: 'stocks/:code',
        element: (
          <LazyPage>
            <StockDetailPage />
          </LazyPage>
        ),
      },
      {
        path: 'compare',
        element: (
          <LazyPage>
            <StockComparisonPage />
          </LazyPage>
        ),
      },
      {
        path: 'market',
        element: (
          <LazyPage>
            <MarketDashboardPage />
          </LazyPage>
        ),
      },
      {
        path: 'market-overview',
        element: (
          <LazyPage>
            <MarketOverviewPage />
          </LazyPage>
        ),
      },
      {
        path: 'dashboard',
        element: (
          <LazyPage>
            <DashboardPage />
          </LazyPage>
        ),
      },
      {
        path: 'watchlists',
        element: (
          <LazyPage>
            <WatchlistsPage />
          </LazyPage>
        ),
      },
      {
        path: 'portfolios',
        element: (
          <LazyPage>
            <PortfolioListPage />
          </LazyPage>
        ),
      },
      {
        path: 'portfolios/:id',
        element: (
          <LazyPage>
            <PortfolioDetailPage />
          </LazyPage>
        ),
      },
      {
        path: 'alerts',
        element: (
          <LazyPage>
            <AlertsPage />
          </LazyPage>
        ),
      },
      {
        path: 'notifications',
        element: (
          <LazyPage>
            <NotificationsPage />
          </LazyPage>
        ),
      },
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'register',
        element: <RegisterPage />,
      },
      {
        path: 'verify-email',
        element: <EmailVerificationPage />,
      },
      {
        path: 'forgot-password',
        element: <ForgotPasswordPage />,
      },
      {
        path: 'reset-password',
        element: <ResetPasswordPage />,
      },
      {
        path: 'oauth/callback',
        element: <OAuthCallbackPage />,
      },
      {
        path: 'oauth/callback/:provider',
        element: <OAuthCallbackPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
])
