# FEATURE-006: Subscription & Billing System

**Type**: FEATURE
**Priority**: P1
**Status**: DONE
**Created**: 2025-11-16
**Completed**: 2025-11-26
**Effort**: 40-50 hours (Backend: ~25 hours completed)
**Phase**: Post-MVP - P1 Features

---

## Description

Implement comprehensive subscription and billing system with multiple pricing tiers, payment processing, and subscription management. This enables monetization of the platform through premium features and tiered access.

## Current Status

- **Implementation**: 100% (Backend complete)
- **Completed Components**:
  - Subscription plans and tiers: 100% ✅
  - Payment processing integration (Stripe): 100% ✅
  - Billing management: 100% ✅
  - Feature gating: 100% ✅
  - Unit tests: 100% ✅

## Implementation Summary

### Files Created
- `database/migrations/14_subscription_billing.sql` - Database schema and seed data
- `backend/app/db/models/subscription_plan.py` - SubscriptionPlan model
- `backend/app/db/models/user_subscription.py` - UserSubscription model
- `backend/app/db/models/payment.py` - Payment model
- `backend/app/db/models/usage_tracking.py` - UsageTracking model
- `backend/app/db/models/payment_method.py` - PaymentMethod model
- `backend/app/db/models/stripe_webhook_event.py` - Webhook idempotency
- `backend/app/schemas/subscription.py` - All Pydantic schemas
- `backend/app/services/stripe_service.py` - Stripe API integration
- `backend/app/services/subscription_service.py` - Subscription business logic
- `backend/app/api/v1/endpoints/subscriptions.py` - Subscription API endpoints
- `backend/app/api/v1/endpoints/webhooks.py` - Stripe webhook handler
- `backend/app/middleware/subscription_guards.py` - Feature gating middleware
- `backend/tests/services/test_subscription_service.py` - Service unit tests
- `backend/tests/api/test_subscriptions.py` - API endpoint tests

### Files Modified
- `backend/app/db/models/user.py` - Added stripe_customer_id and relationships
- `backend/app/db/models/__init__.py` - Export new models
- `backend/app/schemas/__init__.py` - Export new schemas
- `backend/app/services/__init__.py` - Export new services
- `backend/app/api/dependencies.py` - Add service dependencies
- `backend/app/core/config.py` - Add Stripe configuration
- `backend/app/main.py` - Register new routers
- `.env.example` - Add Stripe and subscription settings

### Remaining Work (Frontend - Separate Ticket)
- Frontend pricing page
- Checkout flow with Stripe Elements
- Subscription management UI
- Usage metrics dashboard

## Subscription Tiers

### Free Tier (Current freemium users)
- 20 screening results per query
- 10 searches per day
- Limited technical indicators (20 basic)
- No portfolio tracking
- No alerts
- Community support

### Premium Tier ($9.99/month or $99/year)
- Unlimited screening results
- Unlimited searches
- All 200+ technical indicators
- 3 portfolios, up to 100 stocks each
- 20 price alerts
- Email support
- Export to CSV/JSON

### Pro Tier ($29.99/month or $299/year)
- Everything in Premium
- Unlimited portfolios and holdings
- Unlimited price alerts
- Real-time order book data
- Advanced charting tools
- API access (1,000 calls/day)
- Priority support
- Export to Excel with templates

## Feature Requirements

### 1. Backend Implementation (20-25h)

#### Database Schema (5h)
```sql
-- Subscription plans table
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- FREE, PREMIUM, PRO
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10, 2) NOT NULL,
    price_yearly DECIMAL(10, 2) NOT NULL,
    features JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User subscriptions table
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
    status VARCHAR(20) NOT NULL, -- ACTIVE, CANCELED, EXPIRED, TRIAL
    billing_cycle VARCHAR(20) NOT NULL, -- MONTHLY, YEARLY
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    trial_end TIMESTAMP,
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payment history table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    subscription_id INTEGER REFERENCES user_subscriptions(id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) NOT NULL, -- SUCCEEDED, FAILED, REFUNDED
    stripe_payment_intent_id VARCHAR(255),
    stripe_invoice_id VARCHAR(255),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage tracking table (for rate limiting and feature usage)
CREATE TABLE usage_tracking (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    resource_type VARCHAR(50) NOT NULL, -- SCREENING, API_CALL, ALERT, EXPORT
    count INTEGER NOT NULL DEFAULT 1,
    period_start DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, resource_type, period_start)
);

-- Indexes
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_usage_tracking_user_period ON usage_tracking(user_id, period_start);
```

#### Stripe Integration (8h)
```python
class StripeService:
    """
    Handles Stripe payment processing
    """

    async def create_customer(self, user_id: int, email: str):
        """
        Create Stripe customer
        """

    async def create_subscription(
        self, user_id: int, plan_id: int, billing_cycle: str, payment_method_id: str
    ):
        """
        Create subscription in Stripe
        1. Get or create Stripe customer
        2. Attach payment method
        3. Create subscription with plan price
        4. Handle 3D Secure if required
        5. Store subscription in database
        """

    async def cancel_subscription(self, subscription_id: int, immediate: bool = False):
        """
        Cancel subscription
        - immediate=True: Cancel immediately
        - immediate=False: Cancel at period end
        """

    async def update_subscription(self, subscription_id: int, new_plan_id: int):
        """
        Upgrade/downgrade subscription
        1. Calculate proration
        2. Update Stripe subscription
        3. Update database
        """

    async def handle_webhook(self, event: dict):
        """
        Handle Stripe webhooks
        - invoice.paid: Update subscription status
        - invoice.payment_failed: Handle failed payment
        - customer.subscription.updated: Sync subscription
        - customer.subscription.deleted: Cancel subscription
        """
```

#### Subscription Service (5h)
```python
class SubscriptionService:
    """
    Manages subscription logic and feature access
    """

    async def get_user_plan(self, user_id: int) -> str:
        """
        Get current plan for user (FREE, PREMIUM, PRO)
        """

    async def has_feature_access(self, user_id: int, feature: str) -> bool:
        """
        Check if user has access to feature
        """

    async def check_usage_limit(self, user_id: int, resource_type: str) -> tuple[bool, int]:
        """
        Check if user has reached usage limit
        Returns: (has_access, remaining_count)
        """

    async def increment_usage(self, user_id: int, resource_type: str):
        """
        Increment usage counter for resource
        """

    async def get_subscription_details(self, user_id: int):
        """
        Get full subscription details including:
        - Current plan
        - Billing cycle
        - Next billing date
        - Usage statistics
        """
```

#### API Endpoints (2h)
```python
# Subscription management
GET    /api/v1/subscriptions/plans            # List all plans
GET    /api/v1/subscriptions/current          # Get current subscription
POST   /api/v1/subscriptions/subscribe        # Subscribe to plan
POST   /api/v1/subscriptions/cancel           # Cancel subscription
POST   /api/v1/subscriptions/upgrade          # Upgrade/downgrade plan
GET    /api/v1/subscriptions/usage            # Get usage statistics

# Payment management
GET    /api/v1/payments/history               # Payment history
POST   /api/v1/payments/methods               # Add payment method
GET    /api/v1/payments/methods               # List payment methods
DELETE /api/v1/payments/methods/{id}          # Remove payment method
POST   /api/v1/payments/retry                 # Retry failed payment

# Stripe webhooks
POST   /api/v1/webhooks/stripe                # Stripe webhook endpoint
```

### 2. Frontend Implementation (15-20h)

#### Pages (8h)
- **PricingPage**: Display pricing tiers and features comparison
- **CheckoutPage**: Subscription checkout with payment form
- **SubscriptionSettingsPage**: Manage subscription and billing
- **PaymentHistoryPage**: View payment history and invoices
- **UpgradePage**: Upgrade prompt with benefits

#### Components (7h)
- **PricingTable**: Pricing tiers comparison table
- **PricingCard**: Individual plan card with features
- **CheckoutForm**: Stripe Elements payment form
- **SubscriptionStatus**: Current plan display
- **UsageMetrics**: Display usage vs limits
- **PaymentMethodSelector**: Manage payment methods
- **InvoiceList**: List of past invoices
- **UpgradePrompt**: Contextual upgrade prompts
- **FeatureGate**: Component to gate premium features
- **TrialBanner**: Display trial status

#### Hooks (5h)
- **useSubscription**: Manage subscription state
- **useStripeCheckout**: Handle Stripe checkout flow
- **usePaymentMethods**: Manage payment methods
- **useUsageTracking**: Track feature usage
- **useFeatureAccess**: Check feature access

### 3. Feature Gating (5-5h)

#### Backend Middleware (3h)
```python
async def require_subscription(required_plan: str):
    """
    Decorator to protect endpoints by subscription tier
    """

async def check_usage_limit(resource_type: str, limit: int):
    """
    Decorator to enforce usage limits
    """
```

#### Frontend Guards (2h)
```typescript
// Component to gate features
<FeatureGate feature="advanced_charts" fallback={<UpgradePrompt />}>
  <AdvancedChartComponent />
</FeatureGate>

// Hook to check access
const { hasAccess } = useFeatureAccess('export_excel');
if (!hasAccess) {
  showUpgradePrompt();
}
```

## Acceptance Criteria

### Backend
- [x] Stripe integration working (create customer, subscription, payment)
- [x] Webhook handling implemented for all critical events
- [x] Subscription plans seeded in database
- [x] User can subscribe to Premium or Pro plan
- [x] User can cancel subscription (immediate or at period end)
- [x] User can upgrade/downgrade between plans
- [x] Proration calculated correctly for plan changes
- [x] Failed payments handled gracefully
- [x] Usage limits enforced for free tier
- [x] API endpoints tested (>80% coverage)
- [x] Payment security: PCI compliance via Stripe

### Frontend (Separate ticket - FEATURE-006-FE)
- [ ] Pricing page displays all plans clearly
- [ ] Checkout flow works end-to-end with Stripe Elements
- [ ] 3D Secure authentication handled
- [ ] Subscription status displayed correctly
- [ ] Usage metrics shown with progress bars
- [ ] Payment methods can be added/removed
- [ ] Payment history displayed
- [ ] Upgrade prompts shown for gated features
- [ ] Trial period displayed if applicable
- [ ] Mobile responsive design

### Feature Gating
- [x] Free tier limited to 20 results per query
- [x] Free tier limited to 10 searches per day
- [x] Premium tier has unlimited searches
- [x] Pro tier has API access enabled
- [x] Feature gates enforced on backend (frontend in FEATURE-006-FE)

## Dependencies

- Stripe account and API keys
- SSL certificate (required for payment processing)
- Tax compliance (consider Stripe Tax)

## Testing Strategy

1. **Unit Tests**: Test subscription logic, usage tracking, proration
2. **Integration Tests**: Test Stripe API integration with test mode
3. **Webhook Tests**: Test webhook handling with Stripe CLI
4. **E2E Tests**: Complete checkout flow from pricing to subscription
5. **Payment Tests**: Test successful payment, failed payment, 3D Secure

## Related Files

- Backend:
  - `backend/app/models/subscription.py` (new)
  - `backend/app/services/stripe_service.py` (new)
  - `backend/app/services/subscription_service.py` (new)
  - `backend/app/api/v1/endpoints/subscriptions.py` (new)
  - `backend/app/api/v1/endpoints/webhooks.py` (new)
- Frontend:
  - `frontend/src/pages/PricingPage.tsx` (new)
  - `frontend/src/pages/CheckoutPage.tsx` (new)
  - `frontend/src/components/subscription/` (new directory)
  - `frontend/src/hooks/useSubscription.ts` (new)

## Configuration

```env
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Subscription
FREE_TIER_SCREENING_LIMIT=20
FREE_TIER_SEARCHES_PER_DAY=10
PREMIUM_PRICE_MONTHLY=9.99
PREMIUM_PRICE_YEARLY=99.00
PRO_PRICE_MONTHLY=29.99
PRO_PRICE_YEARLY=299.00

# Trial
TRIAL_PERIOD_DAYS=14
```

## User Stories

1. **As a user**, I want to see pricing options to decide if I want to upgrade
2. **As a user**, I want to subscribe to Premium plan to get unlimited searches
3. **As a user**, I want to enter payment details securely
4. **As a user**, I want to cancel my subscription anytime
5. **As a user**, I want to upgrade from Premium to Pro
6. **As a user**, I want to see my usage statistics
7. **As a user**, I want to view my payment history
8. **As a user**, I want a trial period to test premium features

## Notes

- Use Stripe Checkout for simpler implementation (alternative to Elements)
- Consider Stripe Tax for automatic tax calculation
- Implement dunning management for failed payments
- Consider offering annual discount (17% off)
- Monitor churn rate and implement retention strategies
- Consider affiliate program for user acquisition

---

**References**:
- PRD Section 4.7: Subscription & Billing
- TEST_IMPROVEMENT_PLAN.md - Missing P1 Features
- Freemium model from FEATURE-001 (FE-012)
