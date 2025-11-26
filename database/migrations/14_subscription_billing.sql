-- =============================================================================
-- Migration: 14_subscription_billing.sql
-- Description: Subscription and billing system tables
-- Created: 2025-11-26
-- Ticket: FEATURE-006
-- =============================================================================

-- =============================================================================
-- SUBSCRIPTION PLANS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,  -- FREE, PREMIUM, PRO
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    price_yearly DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    features JSONB NOT NULL DEFAULT '{}',
    limits JSONB NOT NULL DEFAULT '{}',  -- Usage limits for this plan
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Add comment
COMMENT ON TABLE subscription_plans IS 'Available subscription plans with pricing and features';
COMMENT ON COLUMN subscription_plans.name IS 'Internal plan identifier (FREE, PREMIUM, PRO)';
COMMENT ON COLUMN subscription_plans.features IS 'JSON object describing plan features';
COMMENT ON COLUMN subscription_plans.limits IS 'JSON object with usage limits (e.g., screening_results_per_query, searches_per_day)';

-- =============================================================================
-- USER SUBSCRIPTIONS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active, canceled, expired, trial, past_due
    billing_cycle VARCHAR(20) NOT NULL DEFAULT 'monthly',  -- monthly, yearly
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    subscription_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT valid_subscription_status CHECK (
        status IN ('active', 'canceled', 'expired', 'trial', 'past_due', 'incomplete')
    ),
    CONSTRAINT valid_billing_cycle CHECK (
        billing_cycle IN ('monthly', 'yearly')
    )
);

-- Indexes for user_subscriptions
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_stripe_subscription_id ON user_subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_stripe_customer_id ON user_subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_period_end ON user_subscriptions(current_period_end);

-- Add comment
COMMENT ON TABLE user_subscriptions IS 'User subscription records linked to Stripe';
COMMENT ON COLUMN user_subscriptions.status IS 'Subscription status: active, canceled, expired, trial, past_due, incomplete';
COMMENT ON COLUMN user_subscriptions.cancel_at_period_end IS 'If true, subscription will cancel at the end of current period';

-- =============================================================================
-- PAYMENTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES user_subscriptions(id) ON DELETE SET NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, succeeded, failed, refunded, canceled
    payment_type VARCHAR(30) NOT NULL DEFAULT 'subscription',  -- subscription, one_time, refund
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_invoice_id VARCHAR(255),
    stripe_charge_id VARCHAR(255),
    failure_code VARCHAR(100),
    failure_message TEXT,
    refund_amount DECIMAL(10, 2),
    refunded_at TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    payment_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT valid_payment_status CHECK (
        status IN ('pending', 'succeeded', 'failed', 'refunded', 'canceled', 'processing')
    ),
    CONSTRAINT valid_payment_type CHECK (
        payment_type IN ('subscription', 'one_time', 'refund')
    )
);

-- Indexes for payments
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_subscription_id ON payments(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_stripe_payment_intent_id ON payments(stripe_payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_payments_stripe_invoice_id ON payments(stripe_invoice_id);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

-- Add comment
COMMENT ON TABLE payments IS 'Payment transaction history';
COMMENT ON COLUMN payments.status IS 'Payment status: pending, succeeded, failed, refunded, canceled, processing';

-- =============================================================================
-- USAGE TRACKING TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS usage_tracking (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL,  -- screening, api_call, alert, export, portfolio
    count INTEGER NOT NULL DEFAULT 1,
    period_start DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL DEFAULT 'daily',  -- daily, monthly
    tracking_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT unique_user_resource_period UNIQUE (user_id, resource_type, period_start, period_type),
    CONSTRAINT valid_period_type CHECK (
        period_type IN ('daily', 'monthly')
    )
);

-- Indexes for usage_tracking
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_period ON usage_tracking(user_id, period_start);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_resource_type ON usage_tracking(resource_type);
CREATE INDEX IF NOT EXISTS idx_usage_tracking_period_start ON usage_tracking(period_start);

-- Add comment
COMMENT ON TABLE usage_tracking IS 'Track user resource usage for rate limiting and analytics';
COMMENT ON COLUMN usage_tracking.resource_type IS 'Type of resource: screening, api_call, alert, export, portfolio';
COMMENT ON COLUMN usage_tracking.period_type IS 'Period type for aggregation: daily, monthly';

-- =============================================================================
-- PAYMENT METHODS TABLE (for storing customer payment methods)
-- =============================================================================

CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_payment_method_id VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(30) NOT NULL DEFAULT 'card',  -- card, bank_account
    is_default BOOLEAN DEFAULT FALSE,
    card_brand VARCHAR(30),  -- visa, mastercard, amex, etc.
    card_last4 VARCHAR(4),
    card_exp_month INTEGER,
    card_exp_year INTEGER,
    billing_name VARCHAR(255),
    billing_email VARCHAR(255),
    method_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT valid_payment_method_type CHECK (
        type IN ('card', 'bank_account', 'sepa_debit', 'ideal')
    )
);

-- Indexes for payment_methods
CREATE INDEX IF NOT EXISTS idx_payment_methods_user_id ON payment_methods(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_stripe_payment_method_id ON payment_methods(stripe_payment_method_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_is_default ON payment_methods(user_id, is_default) WHERE is_default = TRUE;

-- Add comment
COMMENT ON TABLE payment_methods IS 'Customer payment methods from Stripe';

-- =============================================================================
-- STRIPE WEBHOOK EVENTS TABLE (for idempotency)
-- =============================================================================

CREATE TABLE IF NOT EXISTS stripe_webhook_events (
    id SERIAL PRIMARY KEY,
    stripe_event_id VARCHAR(255) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for stripe_webhook_events
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_stripe_event_id ON stripe_webhook_events(stripe_event_id);
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_processed ON stripe_webhook_events(processed);
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_event_type ON stripe_webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_stripe_webhook_events_created_at ON stripe_webhook_events(created_at);

-- Add comment
COMMENT ON TABLE stripe_webhook_events IS 'Store Stripe webhook events for idempotency and debugging';

-- =============================================================================
-- UPDATE USERS TABLE - Add Stripe customer ID
-- =============================================================================

DO $$
BEGIN
    -- Add stripe_customer_id column if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'stripe_customer_id'
    ) THEN
        ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255) UNIQUE;
    END IF;
END $$;

-- Index for stripe_customer_id
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id);

-- =============================================================================
-- TRIGGER: Update updated_at timestamp
-- =============================================================================

-- Create or replace the function to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for all new tables
DO $$
DECLARE
    tables TEXT[] := ARRAY['subscription_plans', 'user_subscriptions', 'payments', 'usage_tracking', 'payment_methods'];
    t TEXT;
BEGIN
    FOREACH t IN ARRAY tables
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%s_updated_at ON %I;
            CREATE TRIGGER update_%s_updated_at
                BEFORE UPDATE ON %I
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        ', t, t, t, t);
    END LOOP;
END $$;

-- =============================================================================
-- SEED DATA: Default subscription plans
-- =============================================================================

INSERT INTO subscription_plans (name, display_name, description, price_monthly, price_yearly, features, limits, sort_order)
VALUES
    (
        'FREE',
        'Free',
        'Basic access with limited features',
        0.00,
        0.00,
        '{
            "screening_results": true,
            "basic_indicators": true,
            "portfolio_tracking": false,
            "alerts": false,
            "api_access": false,
            "export_csv": false,
            "export_excel": false,
            "advanced_charts": false,
            "real_time_data": false,
            "priority_support": false
        }',
        '{
            "screening_results_per_query": 20,
            "searches_per_day": 10,
            "technical_indicators": 20,
            "portfolios": 0,
            "stocks_per_portfolio": 0,
            "alerts": 0,
            "api_calls_per_day": 0
        }',
        1
    ),
    (
        'PREMIUM',
        'Premium',
        'Full access for serious investors',
        9.99,
        99.00,
        '{
            "screening_results": true,
            "basic_indicators": true,
            "advanced_indicators": true,
            "portfolio_tracking": true,
            "alerts": true,
            "api_access": false,
            "export_csv": true,
            "export_json": true,
            "export_excel": false,
            "advanced_charts": true,
            "real_time_data": false,
            "priority_support": false,
            "email_support": true
        }',
        '{
            "screening_results_per_query": -1,
            "searches_per_day": -1,
            "technical_indicators": 200,
            "portfolios": 3,
            "stocks_per_portfolio": 100,
            "alerts": 20,
            "api_calls_per_day": 0
        }',
        2
    ),
    (
        'PRO',
        'Pro',
        'Everything for professional traders',
        29.99,
        299.00,
        '{
            "screening_results": true,
            "basic_indicators": true,
            "advanced_indicators": true,
            "portfolio_tracking": true,
            "alerts": true,
            "api_access": true,
            "export_csv": true,
            "export_json": true,
            "export_excel": true,
            "advanced_charts": true,
            "real_time_data": true,
            "order_book_data": true,
            "priority_support": true,
            "email_support": true
        }',
        '{
            "screening_results_per_query": -1,
            "searches_per_day": -1,
            "technical_indicators": -1,
            "portfolios": -1,
            "stocks_per_portfolio": -1,
            "alerts": -1,
            "api_calls_per_day": 1000
        }',
        3
    )
ON CONFLICT (name) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    price_yearly = EXCLUDED.price_yearly,
    features = EXCLUDED.features,
    limits = EXCLUDED.limits,
    sort_order = EXCLUDED.sort_order,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- FUNCTION: Get user's current subscription plan
-- =============================================================================

CREATE OR REPLACE FUNCTION get_user_subscription_plan(p_user_id INTEGER)
RETURNS TABLE (
    plan_name VARCHAR(50),
    plan_display_name VARCHAR(100),
    subscription_status VARCHAR(20),
    billing_cycle VARCHAR(20),
    current_period_end TIMESTAMP WITH TIME ZONE,
    features JSONB,
    limits JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sp.name,
        sp.display_name,
        COALESCE(us.status, 'active') AS subscription_status,
        COALESCE(us.billing_cycle, 'monthly') AS billing_cycle,
        us.current_period_end,
        sp.features,
        sp.limits
    FROM subscription_plans sp
    LEFT JOIN user_subscriptions us ON us.plan_id = sp.id
        AND us.user_id = p_user_id
        AND us.status IN ('active', 'trial')
    WHERE sp.name = COALESCE(
        (SELECT sp2.name FROM user_subscriptions us2
         JOIN subscription_plans sp2 ON sp2.id = us2.plan_id
         WHERE us2.user_id = p_user_id AND us2.status IN ('active', 'trial')
         ORDER BY us2.created_at DESC LIMIT 1),
        'FREE'
    )
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION: Check usage limit
-- =============================================================================

CREATE OR REPLACE FUNCTION check_usage_limit(
    p_user_id INTEGER,
    p_resource_type VARCHAR(50),
    p_period_type VARCHAR(20) DEFAULT 'daily'
)
RETURNS TABLE (
    current_usage INTEGER,
    limit_value INTEGER,
    has_access BOOLEAN,
    remaining INTEGER
) AS $$
DECLARE
    v_plan_limits JSONB;
    v_limit_key VARCHAR(100);
    v_limit INTEGER;
    v_usage INTEGER;
BEGIN
    -- Get user's plan limits
    SELECT sp.limits INTO v_plan_limits
    FROM subscription_plans sp
    LEFT JOIN user_subscriptions us ON us.plan_id = sp.id
        AND us.user_id = p_user_id
        AND us.status IN ('active', 'trial')
    WHERE sp.name = COALESCE(
        (SELECT sp2.name FROM user_subscriptions us2
         JOIN subscription_plans sp2 ON sp2.id = us2.plan_id
         WHERE us2.user_id = p_user_id AND us2.status IN ('active', 'trial')
         ORDER BY us2.created_at DESC LIMIT 1),
        'FREE'
    );

    -- Map resource type to limit key
    v_limit_key := CASE p_resource_type
        WHEN 'screening' THEN 'searches_per_day'
        WHEN 'api_call' THEN 'api_calls_per_day'
        WHEN 'alert' THEN 'alerts'
        WHEN 'portfolio' THEN 'portfolios'
        ELSE p_resource_type
    END;

    -- Get limit value (-1 means unlimited)
    v_limit := COALESCE((v_plan_limits->>v_limit_key)::INTEGER, 0);

    -- Get current usage
    SELECT COALESCE(ut.count, 0) INTO v_usage
    FROM usage_tracking ut
    WHERE ut.user_id = p_user_id
        AND ut.resource_type = p_resource_type
        AND ut.period_start = CURRENT_DATE
        AND ut.period_type = p_period_type;

    v_usage := COALESCE(v_usage, 0);

    RETURN QUERY SELECT
        v_usage,
        v_limit,
        (v_limit = -1 OR v_usage < v_limit),
        CASE WHEN v_limit = -1 THEN -1 ELSE GREATEST(0, v_limit - v_usage) END;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCTION: Increment usage
-- =============================================================================

CREATE OR REPLACE FUNCTION increment_usage(
    p_user_id INTEGER,
    p_resource_type VARCHAR(50),
    p_count INTEGER DEFAULT 1,
    p_period_type VARCHAR(20) DEFAULT 'daily'
)
RETURNS INTEGER AS $$
DECLARE
    v_new_count INTEGER;
BEGIN
    INSERT INTO usage_tracking (user_id, resource_type, count, period_start, period_type)
    VALUES (p_user_id, p_resource_type, p_count, CURRENT_DATE, p_period_type)
    ON CONFLICT (user_id, resource_type, period_start, period_type)
    DO UPDATE SET count = usage_tracking.count + p_count, updated_at = CURRENT_TIMESTAMP
    RETURNING count INTO v_new_count;

    RETURN v_new_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant permissions (adjust role name as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON subscription_plans TO screener_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON user_subscriptions TO screener_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON payments TO screener_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON usage_tracking TO screener_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON payment_methods TO screener_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON stripe_webhook_events TO screener_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO screener_app;

-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
