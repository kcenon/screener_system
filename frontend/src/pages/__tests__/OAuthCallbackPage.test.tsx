import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import OAuthCallbackPage from '../OAuthCallbackPage'
import * as oauthServiceModule from '@/services/oauthService'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Mock oauthService
vi.mock('@/services/oauthService', () => ({
  oauthService: {
    handleCallback: vi.fn(),
  },
}))

describe('OAuthCallbackPage', () => {
  let queryClient: QueryClient

  const renderWithRoute = (route: string) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>
          <Routes>
            <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
            <Route path="/oauth/callback/:provider" element={<OAuthCallbackPage />} />
            <Route path="/login" element={<div>Login Page</div>} />
            <Route path="/dashboard" element={<div>Dashboard</div>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    )
  }

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    queryClient.clear()
  })

  describe('Initial State', () => {
    it('shows processing state initially', async () => {
      vi.spyOn(oauthServiceModule.oauthService, 'handleCallback').mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )

      renderWithRoute('/oauth/callback?code=test-code&state=test-state&provider=google')

      expect(screen.getByText(/completing sign in/i)).toBeInTheDocument()
      expect(screen.getByText(/please wait while we verify your credentials/i)).toBeInTheDocument()
    })

    it('shows loading spinner during processing', async () => {
      vi.spyOn(oauthServiceModule.oauthService, 'handleCallback').mockImplementation(
        () => new Promise(() => {})
      )

      renderWithRoute('/oauth/callback?code=test-code&state=test-state&provider=google')

      const spinner = document.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })
  })

  describe('Successful Callback', () => {
    it('shows success state after successful callback', async () => {
      vi.spyOn(oauthServiceModule.oauthService, 'handleCallback').mockResolvedValue({
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        token_type: 'bearer',
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
          tier: 'free',
          is_active: true,
          email_verified: true,
          email_verified_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
        },
      })

      renderWithRoute('/oauth/callback?code=test-code&state=test-state&provider=google')

      await waitFor(() => {
        expect(screen.getByText(/sign in successful/i)).toBeInTheDocument()
      })
    })

    it('calls handleCallback with correct parameters', async () => {
      const mockHandleCallback = vi.spyOn(oauthServiceModule.oauthService, 'handleCallback')
        .mockResolvedValue({
          access_token: 'test',
          refresh_token: 'test',
          token_type: 'bearer',
          user: {} as any,
        })

      renderWithRoute('/oauth/callback?code=auth-code&state=csrf-state&provider=google')

      await waitFor(() => {
        expect(mockHandleCallback).toHaveBeenCalledWith('google', 'auth-code', 'csrf-state')
      })
    })
  })

  describe('Error Handling', () => {
    it('shows error state when callback fails', async () => {
      vi.spyOn(oauthServiceModule.oauthService, 'handleCallback')
        .mockRejectedValue(new Error('Authentication failed'))

      renderWithRoute('/oauth/callback?code=test-code&state=test-state&provider=google')

      await waitFor(() => {
        expect(screen.getByText(/sign in failed/i)).toBeInTheDocument()
        expect(screen.getByText(/authentication failed/i)).toBeInTheDocument()
      })
    })

    it('shows error when code is missing', async () => {
      renderWithRoute('/oauth/callback?state=test-state&provider=google')

      await waitFor(() => {
        expect(screen.getByText(/sign in failed/i)).toBeInTheDocument()
        expect(screen.getByText(/missing authorization code or state parameter/i)).toBeInTheDocument()
      })
    })

    it('shows error when state is missing', async () => {
      renderWithRoute('/oauth/callback?code=test-code&provider=google')

      await waitFor(() => {
        expect(screen.getByText(/sign in failed/i)).toBeInTheDocument()
        expect(screen.getByText(/missing authorization code or state parameter/i)).toBeInTheDocument()
      })
    })

    it('shows error when provider is invalid', async () => {
      renderWithRoute('/oauth/callback?code=test-code&state=test-state&provider=invalid')

      await waitFor(() => {
        expect(screen.getByText(/sign in failed/i)).toBeInTheDocument()
        expect(screen.getByText(/invalid or missing oauth provider/i)).toBeInTheDocument()
      })
    })

    it('shows error from OAuth provider error param', async () => {
      renderWithRoute('/oauth/callback?error=access_denied')

      await waitFor(() => {
        expect(screen.getByText(/sign in failed/i)).toBeInTheDocument()
        expect(screen.getByText(/access_denied/i)).toBeInTheDocument()
      })
    })

    it('renders return to login button on error', async () => {
      vi.spyOn(oauthServiceModule.oauthService, 'handleCallback')
        .mockRejectedValue(new Error('Auth failed'))

      renderWithRoute('/oauth/callback?code=test-code&state=test-state&provider=google')

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /return to login/i })).toBeInTheDocument()
      })
    })

    it('navigates to login when clicking return button', async () => {
      const user = userEvent.setup()
      vi.spyOn(oauthServiceModule.oauthService, 'handleCallback')
        .mockRejectedValue(new Error('Auth failed'))

      renderWithRoute('/oauth/callback?code=test-code&state=test-state&provider=google')

      const returnButton = await screen.findByRole('button', { name: /return to login/i })
      await user.click(returnButton)

      expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true })
    })
  })

  describe('Provider Detection', () => {
    it('detects provider from URL param', async () => {
      const mockHandleCallback = vi.spyOn(oauthServiceModule.oauthService, 'handleCallback')
        .mockResolvedValue({
          access_token: 'test',
          refresh_token: 'test',
          token_type: 'bearer',
          user: {} as any,
        })

      renderWithRoute('/oauth/callback?code=test&state=test&provider=kakao')

      await waitFor(() => {
        expect(mockHandleCallback).toHaveBeenCalledWith('kakao', 'test', 'test')
      })
    })

    it('handles naver provider', async () => {
      const mockHandleCallback = vi.spyOn(oauthServiceModule.oauthService, 'handleCallback')
        .mockResolvedValue({
          access_token: 'test',
          refresh_token: 'test',
          token_type: 'bearer',
          user: {} as any,
        })

      renderWithRoute('/oauth/callback?code=test&state=test&provider=naver')

      await waitFor(() => {
        expect(mockHandleCallback).toHaveBeenCalledWith('naver', 'test', 'test')
      })
    })
  })

  describe('Visual States', () => {
    it('shows green checkmark on success', async () => {
      vi.spyOn(oauthServiceModule.oauthService, 'handleCallback').mockResolvedValue({
        access_token: 'test',
        refresh_token: 'test',
        token_type: 'bearer',
        user: {} as any,
      })

      renderWithRoute('/oauth/callback?code=test&state=test&provider=google')

      await waitFor(() => {
        const successIcon = document.querySelector('.bg-green-100')
        expect(successIcon).toBeInTheDocument()
      })
    })

    it('shows red X on error', async () => {
      vi.spyOn(oauthServiceModule.oauthService, 'handleCallback')
        .mockRejectedValue(new Error('Failed'))

      renderWithRoute('/oauth/callback?code=test&state=test&provider=google')

      await waitFor(() => {
        const errorIcon = document.querySelector('.bg-red-100')
        expect(errorIcon).toBeInTheDocument()
      })
    })
  })
})
