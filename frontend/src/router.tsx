import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ScreenerPage from './pages/ScreenerPage'
import StockDetailPage from './pages/StockDetailPage'
import StockComparisonPage from './pages/StockComparisonPage'
import WatchlistsPage from './pages/WatchlistsPage'
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
        path: 'watchlists',
        element: <WatchlistsPage />,
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
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
])
