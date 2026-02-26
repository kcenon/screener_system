import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import SocialLoginButtons from '../SocialLoginButtons'
import * as oauthServiceModule from '@/services/oauthService'

// Mock oauthService
vi.mock('@/services/oauthService', () => ({
  oauthService: {
    initiateLogin: vi.fn(),
    initiateLink: vi.fn(),
  },
}))

describe('SocialLoginButtons', () => {
  let queryClient: QueryClient

  const renderComponent = (props = {}) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <SocialLoginButtons {...props} />
      </QueryClientProvider>,
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

  describe('Component Rendering', () => {
    it('renders all three OAuth provider buttons', () => {
      renderComponent()

      expect(
        screen.getByRole('button', { name: /sign in with google/i }),
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: /sign in with kakao/i }),
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: /sign in with naver/i }),
      ).toBeInTheDocument()
    })

    it('renders "Or continue with" divider in login mode', () => {
      renderComponent({ mode: 'login' })

      expect(screen.getByText(/or continue with/i)).toBeInTheDocument()
    })

    it('renders "Link your account" divider in link mode', () => {
      renderComponent({ mode: 'link' })

      expect(screen.getByText(/link your account/i)).toBeInTheDocument()
    })

    it('applies custom className', () => {
      const { container } = renderComponent({ className: 'custom-class' })

      expect(container.firstChild).toHaveClass('custom-class')
    })
  })

  describe('Button Interactions', () => {
    it('calls initiateLogin when clicking Google button in login mode', async () => {
      const user = userEvent.setup()
      const mockInitiateLogin = vi.fn().mockResolvedValue(undefined)
      vi.spyOn(
        oauthServiceModule.oauthService,
        'initiateLogin',
      ).mockImplementation(mockInitiateLogin)

      renderComponent({ mode: 'login' })

      await user.click(
        screen.getByRole('button', { name: /sign in with google/i }),
      )

      expect(mockInitiateLogin).toHaveBeenCalledWith('google')
    })

    it('calls initiateLogin when clicking Kakao button', async () => {
      const user = userEvent.setup()
      const mockInitiateLogin = vi.fn().mockResolvedValue(undefined)
      vi.spyOn(
        oauthServiceModule.oauthService,
        'initiateLogin',
      ).mockImplementation(mockInitiateLogin)

      renderComponent({ mode: 'login' })

      await user.click(
        screen.getByRole('button', { name: /sign in with kakao/i }),
      )

      expect(mockInitiateLogin).toHaveBeenCalledWith('kakao')
    })

    it('calls initiateLogin when clicking Naver button', async () => {
      const user = userEvent.setup()
      const mockInitiateLogin = vi.fn().mockResolvedValue(undefined)
      vi.spyOn(
        oauthServiceModule.oauthService,
        'initiateLogin',
      ).mockImplementation(mockInitiateLogin)

      renderComponent({ mode: 'login' })

      await user.click(
        screen.getByRole('button', { name: /sign in with naver/i }),
      )

      expect(mockInitiateLogin).toHaveBeenCalledWith('naver')
    })

    it('calls initiateLink when in link mode', async () => {
      const user = userEvent.setup()
      const mockInitiateLink = vi.fn().mockResolvedValue(undefined)
      vi.spyOn(
        oauthServiceModule.oauthService,
        'initiateLink',
      ).mockImplementation(mockInitiateLink)

      renderComponent({ mode: 'link' })

      await user.click(
        screen.getByRole('button', { name: /sign in with google/i }),
      )

      expect(mockInitiateLink).toHaveBeenCalledWith('google')
    })
  })

  describe('Loading State', () => {
    it('shows loading spinner when button is clicked', async () => {
      const user = userEvent.setup()
      // Create a promise that doesn't resolve immediately
      let resolveLogin: () => void
      const loginPromise = new Promise<void>(resolve => {
        resolveLogin = resolve
      })
      vi.spyOn(
        oauthServiceModule.oauthService,
        'initiateLogin',
      ).mockImplementation(() => loginPromise)

      renderComponent({ mode: 'login' })

      const googleButton = screen.getByRole('button', {
        name: /sign in with google/i,
      })
      await user.click(googleButton)

      // Check for loading spinner
      await waitFor(() => {
        const spinner = googleButton.querySelector('.animate-spin')
        expect(spinner).toBeInTheDocument()
      })

      // Cleanup
      resolveLogin!()
    })

    it('disables all buttons while loading', async () => {
      const user = userEvent.setup()
      let resolveLogin: () => void
      const loginPromise = new Promise<void>(resolve => {
        resolveLogin = resolve
      })
      vi.spyOn(
        oauthServiceModule.oauthService,
        'initiateLogin',
      ).mockImplementation(() => loginPromise)

      renderComponent({ mode: 'login' })

      await user.click(
        screen.getByRole('button', { name: /sign in with google/i }),
      )

      await waitFor(() => {
        const buttons = screen.getAllByRole('button')
        buttons.forEach(button => {
          expect(button).toBeDisabled()
        })
      })

      // Cleanup
      resolveLogin!()
    })
  })

  describe('Error Handling', () => {
    it('calls onError callback when login fails', async () => {
      const user = userEvent.setup()
      const onError = vi.fn()
      const error = new Error('OAuth failed')
      vi.spyOn(
        oauthServiceModule.oauthService,
        'initiateLogin',
      ).mockRejectedValue(error)

      renderComponent({ mode: 'login', onError })

      await user.click(
        screen.getByRole('button', { name: /sign in with google/i }),
      )

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(error)
      })
    })

    it('re-enables buttons after error', async () => {
      const user = userEvent.setup()
      vi.spyOn(
        oauthServiceModule.oauthService,
        'initiateLogin',
      ).mockRejectedValue(new Error('Failed'))

      renderComponent({ mode: 'login' })

      await user.click(
        screen.getByRole('button', { name: /sign in with google/i }),
      )

      await waitFor(() => {
        const buttons = screen.getAllByRole('button')
        buttons.forEach(button => {
          expect(button).not.toBeDisabled()
        })
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper aria-labels for all buttons', () => {
      renderComponent()

      expect(
        screen.getByRole('button', { name: /sign in with google/i }),
      ).toHaveAttribute('aria-label')
      expect(
        screen.getByRole('button', { name: /sign in with kakao/i }),
      ).toHaveAttribute('aria-label')
      expect(
        screen.getByRole('button', { name: /sign in with naver/i }),
      ).toHaveAttribute('aria-label')
    })

    it('all buttons are of type="button"', () => {
      renderComponent()

      const buttons = screen.getAllByRole('button')
      buttons.forEach(button => {
        expect(button).toHaveAttribute('type', 'button')
      })
    })
  })

  describe('Visual Styling', () => {
    it('Google button has correct styling', () => {
      renderComponent()

      const googleButton = screen.getByRole('button', {
        name: /sign in with google/i,
      })
      expect(googleButton).toHaveClass('bg-white')
      expect(googleButton).toHaveClass('text-gray-700')
    })

    it('Kakao button has correct styling', () => {
      renderComponent()

      const kakaoButton = screen.getByRole('button', {
        name: /sign in with kakao/i,
      })
      expect(kakaoButton).toHaveClass('bg-[#FEE500]')
    })

    it('Naver button has correct styling', () => {
      renderComponent()

      const naverButton = screen.getByRole('button', {
        name: /sign in with naver/i,
      })
      expect(naverButton).toHaveClass('bg-[#03C75A]')
      expect(naverButton).toHaveClass('text-white')
    })
  })
})
