import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { router } from './router'
import { analytics } from './services/analytics'
import './index.css'

// Initialize analytics
analytics.init({
  token: import.meta.env.VITE_MIXPANEL_TOKEN || '',
  debug: import.meta.env.VITE_ANALYTICS_DEBUG === 'true',
  disabled: import.meta.env.VITE_ANALYTICS_DISABLED === 'true',
  respectDoNotTrack: import.meta.env.VITE_ANALYTICS_RESPECT_DNT !== 'false',
  trackPageviews: false, // We handle this manually with usePageTracking
  persistence: 'localStorage',
})

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>,
)
