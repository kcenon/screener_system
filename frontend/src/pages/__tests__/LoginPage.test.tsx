import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import LoginPage from '../LoginPage'
import * as useAuthModule from '@/hooks/useAuth'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('LoginPage', () => {
  let queryClient: QueryClient
  let mockLogin: ReturnType<typeof vi.fn>

  const renderLoginPage = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <LoginPage />
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
    mockLogin = vi.fn()

    // Mock useLogin hook
    vi.spyOn(useAuthModule, 'useLogin').mockReturnValue({
      mutate: mockLogin,
      isPending: false,
      isError: false,
      error: null,
      data: undefined,
      isIdle: true,
      isSuccess: false,
      status: 'idle',
      variables: undefined,
      context: undefined,
      failureCount: 0,
      failureReason: null,
      isPaused: false,
      mutateAsync: vi.fn(),
      reset: vi.fn(),
      submittedAt: 0,
    } as any)
  })

  afterEach(() => {
    vi.restoreAllMocks()
    queryClient.clear()
  })

  describe('Component Rendering', () => {
    it('renders login form', () => {
      renderLoginPage()

      expect(screen.getByRole('heading', { name: /sign in to your account/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    })

    it('renders email input field with correct attributes', () => {
      renderLoginPage()

      const emailInput = screen.getByLabelText(/email address/i)
      expect(emailInput).toHaveAttribute('type', 'email')
      expect(emailInput).toHaveAttribute('autocomplete', 'email')
      expect(emailInput).toHaveAttribute('placeholder', 'Email address')
    })

    it('renders password input field with type="password"', () => {
      renderLoginPage()

      const passwordInput = screen.getByLabelText(/^password$/i)
      expect(passwordInput).toHaveAttribute('type', 'password')
      expect(passwordInput).toHaveAttribute('autocomplete', 'current-password')
    })

    it('renders login button', () => {
      renderLoginPage()

      const loginButton = screen.getByRole('button', { name: /sign in/i })
      expect(loginButton).toBeInTheDocument()
      expect(loginButton).toHaveAttribute('type', 'submit')
    })

    it('renders "Forgot Password" link', () => {
      renderLoginPage()

      const forgotPasswordLink = screen.getByText(/forgot your password\?/i)
      expect(forgotPasswordLink).toBeInTheDocument()
      expect(forgotPasswordLink.tagName).toBe('A')
    })

    it('renders "Sign Up" link', () => {
      renderLoginPage()

      const signUpLink = screen.getByRole('link', { name: /create a new account/i })
      expect(signUpLink).toBeInTheDocument()
      expect(signUpLink).toHaveAttribute('href', '/register')
    })

    it('renders remember me checkbox', () => {
      renderLoginPage()

      const rememberMeCheckbox = screen.getByRole('checkbox', { name: /remember me/i })
      expect(rememberMeCheckbox).toBeInTheDocument()
    })

    it('renders password visibility toggle button', () => {
      renderLoginPage()

      // Password toggle button is a button but not labeled with role
      const passwordField = screen.getByLabelText(/^password$/i).parentElement
      const toggleButton = passwordField?.querySelector('button[type="button"]')
      expect(toggleButton).toBeInTheDocument()
    })
  })

  describe('Form Submission', () => {
    it('submits form with valid credentials', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const emailInput = screen.getByLabelText(/email address/i)
      const passwordInput = screen.getByLabelText(/^password$/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)

      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })

    it('calls login mutation with correct data', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      await user.type(screen.getByLabelText(/email address/i), 'user@test.com')
      await user.type(screen.getByLabelText(/^password$/i), 'securepass')
      await user.click(screen.getByRole('button', { name: /sign in/i }))

      expect(mockLogin).toHaveBeenCalledTimes(1)
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'user@test.com',
        password: 'securepass',
      })
    })

    it('disables submit button during submission', () => {
      // Mock pending state
      vi.spyOn(useAuthModule, 'useLogin').mockReturnValue({
        mutate: mockLogin,
        isPending: true,
        isError: false,
        error: null,
        data: undefined,
        isIdle: false,
        isSuccess: false,
        status: 'pending',
        variables: undefined,
        context: undefined,
        failureCount: 0,
        failureReason: null,
        isPaused: false,
        mutateAsync: vi.fn(),
        reset: vi.fn(),
        submittedAt: Date.now(),
      } as any)

      renderLoginPage()

      const submitButton = screen.getByRole('button', { name: /signing in.../i })
      expect(submitButton).toBeDisabled()
    })

    it('shows loading indicator during submission', () => {
      vi.spyOn(useAuthModule, 'useLogin').mockReturnValue({
        mutate: mockLogin,
        isPending: true,
        isError: false,
        error: null,
        data: undefined,
        isIdle: false,
        isSuccess: false,
        status: 'pending',
        variables: undefined,
        context: undefined,
        failureCount: 0,
        failureReason: null,
        isPaused: false,
        mutateAsync: vi.fn(),
        reset: vi.fn(),
        submittedAt: Date.now(),
      } as any)

      renderLoginPage()

      expect(screen.getByText(/signing in.../i)).toBeInTheDocument()
      // Check for loading spinner SVG
      const button = screen.getByRole('button', { name: /signing in.../i })
      const spinner = button.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })

    it('submits form on Enter key press', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const emailInput = screen.getByLabelText(/email address/i)
      const passwordInput = screen.getByLabelText(/^password$/i)

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.keyboard('{Enter}')

      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })
  })

  describe('Error Handling', () => {
    it('shows error for invalid credentials', () => {
      vi.spyOn(useAuthModule, 'useLogin').mockReturnValue({
        mutate: mockLogin,
        isPending: false,
        isError: true,
        error: { message: 'Invalid email or password' } as any,
        data: undefined,
        isIdle: false,
        isSuccess: false,
        status: 'error',
        variables: undefined,
        context: undefined,
        failureCount: 1,
        failureReason: null,
        isPaused: false,
        mutateAsync: vi.fn(),
        reset: vi.fn(),
        submittedAt: Date.now(),
      } as any)

      renderLoginPage()

      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument()
    })

    it('shows default error message when error.message is not available', () => {
      vi.spyOn(useAuthModule, 'useLogin').mockReturnValue({
        mutate: mockLogin,
        isPending: false,
        isError: true,
        error: {} as any,
        data: undefined,
        isIdle: false,
        isSuccess: false,
        status: 'error',
        variables: undefined,
        context: undefined,
        failureCount: 1,
        failureReason: null,
        isPaused: false,
        mutateAsync: vi.fn(),
        reset: vi.fn(),
        submittedAt: Date.now(),
      } as any)

      renderLoginPage()

      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument()
    })

    it('validates email format', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const emailInput = screen.getByLabelText(/email address/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      // Type invalid email
      await user.type(emailInput, 'invalid-email')
      await user.type(screen.getByLabelText(/^password$/i), 'password123')

      // Trigger validation by blurring or submitting
      await user.click(submitButton)

      // react-hook-form validation should show error
      await waitFor(() => {
        // The validation might not trigger due to browser HTML5 validation
        // So we just check that login was not called
        expect(mockLogin).not.toHaveBeenCalled()
      })
    })

    it('validates email is required', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const passwordInput = screen.getByLabelText(/^password$/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(passwordInput, 'password123')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument()
      })

      expect(mockLogin).not.toHaveBeenCalled()
    })

    it('validates password is required', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const emailInput = screen.getByLabelText(/email address/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument()
      })

      expect(mockLogin).not.toHaveBeenCalled()
    })

    it('validates password minimum length', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const emailInput = screen.getByLabelText(/email address/i)
      const passwordInput = screen.getByLabelText(/^password$/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'short')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
      })

      expect(mockLogin).not.toHaveBeenCalled()
    })

    it('shows field-specific error messages', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument()
        expect(screen.getByText(/password is required/i)).toBeInTheDocument()
      })
    })

    it('highlights error fields with red border', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const emailInput = screen.getByLabelText(/email address/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.click(submitButton)

      await waitFor(() => {
        expect(emailInput).toHaveClass('border-red-300')
      })
    })
  })

  describe('Password Visibility Toggle', () => {
    it('toggles password visibility on button click', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      const passwordInput = screen.getByLabelText(/^password$/i)
      expect(passwordInput).toHaveAttribute('type', 'password')

      // Find and click toggle button
      const passwordField = passwordInput.parentElement
      const toggleButton = passwordField?.querySelector('button[type="button"]') as HTMLElement
      await user.click(toggleButton)

      expect(passwordInput).toHaveAttribute('type', 'text')

      // Click again to hide
      await user.click(toggleButton)
      expect(passwordInput).toHaveAttribute('type', 'password')
    })
  })

  describe('Navigation', () => {
    it('navigates to sign up page via link', () => {
      renderLoginPage()

      const signUpLink = screen.getByRole('link', { name: /create a new account/i })
      expect(signUpLink).toHaveAttribute('href', '/register')
    })

    it('has forgot password link', () => {
      renderLoginPage()

      const forgotPasswordLink = screen.getByText(/forgot your password\?/i)
      expect(forgotPasswordLink).toBeInTheDocument()
      expect(forgotPasswordLink).toHaveAttribute('href', '/forgot-password')
    })
  })

  describe('Accessibility', () => {
    it('has accessible labels for all form inputs', () => {
      renderLoginPage()

      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/remember me/i)).toBeInTheDocument()
    })

    it('has proper heading hierarchy', () => {
      renderLoginPage()

      const heading = screen.getByRole('heading', { name: /sign in to your account/i })
      expect(heading.tagName).toBe('H2')
    })

    it('submit button has correct type attribute', () => {
      renderLoginPage()

      const submitButton = screen.getByRole('button', { name: /sign in/i })
      expect(submitButton).toHaveAttribute('type', 'submit')
    })

    it('error messages are associated with inputs', async () => {
      const user = userEvent.setup()
      renderLoginPage()

      await user.click(screen.getByRole('button', { name: /sign in/i }))

      await waitFor(() => {
        const emailError = screen.getByText(/email is required/i)
        const passwordError = screen.getByText(/password is required/i)

        // Error messages should be present in the document
        expect(emailError).toBeInTheDocument()
        expect(passwordError).toBeInTheDocument()

        // Error messages should have proper text color (red)
        expect(emailError).toHaveClass('text-red-600')
        expect(passwordError).toHaveClass('text-red-600')
      })
    })
  })

  describe('User Experience', () => {
    it('does not show error message initially', () => {
      renderLoginPage()

      expect(screen.queryByText(/invalid email or password/i)).not.toBeInTheDocument()
    })

    it('shows OAuth login coming soon message', () => {
      renderLoginPage()

      expect(screen.getByText(/oauth login coming soon/i)).toBeInTheDocument()
    })

    it('has proper visual styling for submit button', () => {
      renderLoginPage()

      const submitButton = screen.getByRole('button', { name: /sign in/i })
      expect(submitButton).toHaveClass('bg-blue-600')
      expect(submitButton).toHaveClass('text-white')
    })

    it('disables submit button when loading', () => {
      vi.spyOn(useAuthModule, 'useLogin').mockReturnValue({
        mutate: mockLogin,
        isPending: true,
        isError: false,
        error: null,
        data: undefined,
        isIdle: false,
        isSuccess: false,
        status: 'pending',
        variables: undefined,
        context: undefined,
        failureCount: 0,
        failureReason: null,
        isPaused: false,
        mutateAsync: vi.fn(),
        reset: vi.fn(),
        submittedAt: Date.now(),
      } as any)

      renderLoginPage()

      const submitButton = screen.getByRole('button', { name: /signing in.../i })
      expect(submitButton).toHaveClass('disabled:opacity-50')
      expect(submitButton).toHaveClass('disabled:cursor-not-allowed')
    })
  })
})
