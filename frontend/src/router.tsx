import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import EmailVerificationPage from './pages/EmailVerificationPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import OAuthCallbackPage from './pages/OAuthCallbackPage'
import ScreenerPage from './pages/ScreenerPage'
import StockDetailPage from './pages/StockDetailPage'
import StockComparisonPage from './pages/StockComparisonPage'
import WatchlistsPage from './pages/WatchlistsPage'
import DashboardPage from './pages/DashboardPage'
import MarketDashboardPage from './pages/MarketDashboardPage'
import MarketOverviewPage from './pages/MarketOverviewPage'
import PortfolioListPage from './pages/PortfolioListPage'
import PortfolioDetailPage from './pages/PortfolioDetailPage'
import AlertsPage from './pages/AlertsPage'
import NotificationsPage from './pages/NotificationsPage'
import NotFoundPage from './pages/NotFoundPage'

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
        element: <ScreenerPage />,
      },
      {
        path: 'stocks/:code',
        element: <StockDetailPage />,
      },
      {
        path: 'compare',
        element: <StockComparisonPage />,
      },
      {
        path: 'market',
        element: <MarketDashboardPage />,
      },
      {
        path: 'market-overview',
        element: <MarketOverviewPage />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'watchlists',
        element: <WatchlistsPage />,
      },
      {
        path: 'portfolios',
        element: <PortfolioListPage />,
      },
      {
        path: 'portfolios/:id',
        element: <PortfolioDetailPage />,
      },
      {
        path: 'alerts',
        element: <AlertsPage />,
      },
      {
        path: 'notifications',
        element: <NotificationsPage />,
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
