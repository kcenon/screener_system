# FEATURE-004: Email Verification & Password Reset System

**Type**: FEATURE
**Priority**: P0
**Status**: IN_PROGRESS
**Created**: 2025-11-16
**Updated**: 2025-11-17
**Effort**: 20-30 hours
**Phase**: Post-MVP - P0 Features

---

## Description

Implement email verification for new user registrations and password reset functionality for account recovery. This is a P0 security feature from the PRD that is currently missing.

## Current Status

- **Implementation**: 60% (backend complete, frontend pending)
- **Completed Components**:
  - ✅ Database Schema (100%)
  - ✅ Token Models (100%)
  - ✅ Email Verification Service (100%)
  - ✅ Password Reset Service (100%)
  - ✅ API Endpoints (100%)
- **Pending Components**:
  - ⏳ Frontend Implementation (0%)
  - ⏳ Email Templates (0%)
  - ⏳ Email Service Integration (0%)
  - ⏳ Unit Tests (0%)
  - ⏳ E2E Tests (0%)

## Feature Requirements

### 1. Backend Implementation (12-15h)

#### Database Schema (2h)
```sql
-- Update users table to add email verification
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP;

-- Email verification tokens
CREATE TABLE email_verification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP
);

-- Password reset tokens
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_email_verification_tokens_token ON email_verification_tokens(token);
CREATE INDEX idx_email_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
```

#### Email Verification Service (4h)
```python
class EmailVerificationService:
    """
    Handles email verification flow
    """

    async def send_verification_email(self, user_id: int, email: str):
        """
        1. Generate secure verification token (UUID)
        2. Store token in database with 24h expiration
        3. Send verification email with link
        """

    async def verify_email(self, token: str) -> bool:
        """
        1. Validate token exists and not expired
        2. Mark user email as verified
        3. Mark token as used
        4. Return success/failure
        """

    async def resend_verification_email(self, user_id: int):
        """
        1. Invalidate old tokens
        2. Generate new token
        3. Send new verification email
        """
```

#### Password Reset Service (4h)
```python
class PasswordResetService:
    """
    Handles password reset flow
    """

    async def request_password_reset(self, email: str):
        """
        1. Verify user exists with this email
        2. Generate secure reset token
        3. Store token with 1h expiration
        4. Send password reset email
        """

    async def validate_reset_token(self, token: str) -> bool:
        """
        1. Validate token exists and not expired
        2. Return validity status
        """

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        1. Validate token
        2. Hash new password
        3. Update user password
        4. Mark token as used
        5. Invalidate all user sessions
        6. Send password changed confirmation email
        """
```

#### API Endpoints (2h)
```python
# Email verification endpoints
POST   /api/v1/auth/verify-email              # Verify email with token
POST   /api/v1/auth/resend-verification       # Resend verification email
GET    /api/v1/auth/verification-status       # Check verification status

# Password reset endpoints
POST   /api/v1/auth/forgot-password           # Request password reset
POST   /api/v1/auth/reset-password            # Reset password with token
GET    /api/v1/auth/validate-reset-token      # Validate reset token
```

### 2. Frontend Implementation (6-10h)

#### Pages (4h)
- **EmailVerificationPage**: Verify email from link
- **EmailVerificationPendingPage**: Prompt to check email
- **ForgotPasswordPage**: Enter email to request reset
- **ResetPasswordPage**: Enter new password with token
- **ResetPasswordSuccessPage**: Confirmation page

#### Components (3h)
- **EmailVerificationBanner**: Banner prompting unverified users to verify
- **EmailVerificationForm**: Resend verification email
- **ForgotPasswordForm**: Request password reset form
- **ResetPasswordForm**: New password input with validation
- **VerificationStatus**: Display verification status

#### Hooks (3h)
- **useEmailVerification**: Handle email verification
- **usePasswordReset**: Handle password reset flow

### 3. Email Templates (2-5h)

#### Email Verification Template (1h)
```html
Subject: Verify your email for Stock Screener

Hi {user_name},

Welcome to Stock Screener! Please verify your email address to activate your account.

[Verify Email Button] → {verification_url}

This link will expire in 24 hours.

If you didn't create an account, you can safely ignore this email.

Best regards,
Stock Screener Team
```

#### Password Reset Template (1h)
```html
Subject: Reset your Stock Screener password

Hi {user_name},

We received a request to reset your password. Click the button below to reset it:

[Reset Password Button] → {reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, you can safely ignore this email.

Best regards,
Stock Screener Team
```

#### Password Changed Confirmation (1h)
```html
Subject: Your password was changed

Hi {user_name},

Your Stock Screener password was successfully changed at {timestamp}.

If you didn't make this change, please contact support immediately.

Best regards,
Stock Screener Team
```

## Security Considerations

### Token Security
- Use cryptographically secure random tokens (UUID4 or secrets.token_urlsafe)
- Store hashed tokens in database (use SHA-256)
- Set short expiration times (24h for verification, 1h for reset)
- Invalidate tokens after use
- Limit token generation rate (max 3 per hour per user)

### Password Reset Security
- Don't reveal if email exists in database (prevent user enumeration)
- Invalidate all existing sessions after password reset
- Require strong passwords (min 8 chars, uppercase, lowercase, number, special char)
- Log all password reset attempts
- Send confirmation email after password change

### Email Verification Security
- Block login for unverified users (configurable)
- Allow resend with rate limiting (max 3 per hour)
- Invalidate old tokens when new one requested

## Acceptance Criteria

### Backend
- [ ] Email verification tokens generated securely
- [ ] Verification emails sent successfully
- [ ] Email verification updates user status correctly
- [ ] Password reset tokens generated securely
- [ ] Password reset emails sent successfully
- [ ] Password reset updates password correctly
- [ ] All sessions invalidated after password reset
- [ ] Token expiration enforced
- [ ] Rate limiting prevents abuse
- [ ] API endpoints tested (>85% coverage)

### Frontend
- [ ] Email verification page verifies token correctly
- [ ] Unverified users see verification banner
- [ ] Resend verification email works
- [ ] Forgot password form validates email
- [ ] Reset password form validates new password
- [ ] Success/error messages displayed correctly
- [ ] Password strength indicator shown
- [ ] Mobile responsive design

### Email
- [ ] Email templates professional and branded
- [ ] Verification links work correctly
- [ ] Reset links work correctly
- [ ] Links expire correctly
- [ ] Email delivery rate >95%
- [ ] HTML and plain text versions provided

## Dependencies

- Email service (SendGrid, AWS SES, etc.) - **same as FEATURE-003**
- User authentication (from existing auth system)
- Password hashing (from existing security module)

## Testing Strategy

1. **Unit Tests**: Test token generation, validation, expiration
2. **Integration Tests**: Test complete verification and reset flows
3. **E2E Tests**: Register → verify email → login, Forgot password → reset → login
4. **Security Tests**: Test token expiration, rate limiting, session invalidation
5. **Email Tests**: Test email delivery and link functionality

## Related Files

- Backend:
  - `backend/app/models/user.py` (update)
  - `backend/app/services/email_verification_service.py` (new)
  - `backend/app/services/password_reset_service.py` (new)
  - `backend/app/api/v1/endpoints/auth.py` (update)
  - `backend/app/templates/emails/` (new directory)
- Frontend:
  - `frontend/src/pages/EmailVerificationPage.tsx` (new)
  - `frontend/src/pages/ForgotPasswordPage.tsx` (new)
  - `frontend/src/pages/ResetPasswordPage.tsx` (new)
  - `frontend/src/hooks/useEmailVerification.ts` (new)

## Configuration

```env
# Email verification
EMAIL_VERIFICATION_EXPIRY_HOURS=24
EMAIL_VERIFICATION_RATE_LIMIT=3  # per hour
REQUIRE_EMAIL_VERIFICATION=true  # block login if false

# Password reset
PASSWORD_RESET_EXPIRY_HOURS=1
PASSWORD_RESET_RATE_LIMIT=3  # per hour

# Email service
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=${SENDGRID_API_KEY}
FROM_EMAIL=noreply@stockscreener.com
```

## User Stories

1. **As a new user**, I want to verify my email address to activate my account
2. **As a user**, I want to resend verification email if I didn't receive it
3. **As a user**, I want to reset my password if I forget it
4. **As a user**, I want to receive confirmation when my password is changed
5. **As a user**, I want password reset links to expire for security

---

**References**:
- PRD Section 4.1: User Authentication (Email Verification)
- TEST_IMPROVEMENT_PLAN.md - Missing P0 Features
