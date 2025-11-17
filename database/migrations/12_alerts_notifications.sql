-- Migration: 12_alerts_notifications.sql
-- Description: Add alerts and notifications system
-- Created: 2025-11-17
-- Ticket: FEATURE-003
-- Phase: Post-MVP - P0 Features

-- ============================================================================
-- 1. ALERTS TABLE
-- ============================================================================

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL REFERENCES stocks(code) ON DELETE CASCADE,
    alert_type VARCHAR(30) NOT NULL,
    condition_value DECIMAL(18, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    triggered_at TIMESTAMPTZ,
    triggered_value DECIMAL(18, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_alert_type CHECK (
        alert_type IN (
            'PRICE_ABOVE',
            'PRICE_BELOW',
            'VOLUME_SPIKE',
            'CHANGE_PERCENT_ABOVE',
            'CHANGE_PERCENT_BELOW'
        )
    ),
    CONSTRAINT positive_condition_value CHECK (condition_value > 0)
);

-- ============================================================================
-- 2. NOTIFICATIONS TABLE
-- ============================================================================

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE SET NULL,
    notification_type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(10) NOT NULL DEFAULT 'NORMAL',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_notification_type CHECK (
        notification_type IN ('ALERT', 'MARKET_EVENT', 'SYSTEM', 'PORTFOLIO')
    ),
    CONSTRAINT valid_priority CHECK (
        priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')
    ),
    CONSTRAINT read_at_requires_is_read CHECK (
        (is_read = FALSE AND read_at IS NULL) OR
        (is_read = TRUE AND read_at IS NOT NULL)
    )
);

-- ============================================================================
-- 3. NOTIFICATION PREFERENCES TABLE
-- ============================================================================

-- Create notification_preferences table
CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Channel preferences
    email_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    push_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    in_app_enabled BOOLEAN NOT NULL DEFAULT TRUE,

    -- Type-specific email preferences
    alert_email BOOLEAN NOT NULL DEFAULT TRUE,
    market_event_email BOOLEAN NOT NULL DEFAULT TRUE,
    system_email BOOLEAN NOT NULL DEFAULT TRUE,
    portfolio_email BOOLEAN NOT NULL DEFAULT FALSE,

    -- Digest preferences
    daily_digest_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    weekly_digest_enabled BOOLEAN NOT NULL DEFAULT FALSE,

    -- Quiet hours (format: HH:MM in user's timezone)
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    quiet_hours_timezone VARCHAR(50) DEFAULT 'Asia/Seoul',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. INDEXES FOR PERFORMANCE
-- ============================================================================

-- Alerts indexes
CREATE INDEX IF NOT EXISTS idx_alerts_user_id
    ON alerts(user_id);

CREATE INDEX IF NOT EXISTS idx_alerts_stock_code
    ON alerts(stock_code);

CREATE INDEX IF NOT EXISTS idx_alerts_active
    ON alerts(is_active, user_id)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_alerts_type
    ON alerts(alert_type, is_active);

CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at
    ON alerts(triggered_at)
    WHERE triggered_at IS NOT NULL;

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id
    ON notifications(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_unread
    ON notifications(user_id, is_read)
    WHERE is_read = FALSE;

CREATE INDEX IF NOT EXISTS idx_notifications_type
    ON notifications(notification_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notifications_alert_id
    ON notifications(alert_id)
    WHERE alert_id IS NOT NULL;

-- Notification preferences indexes
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user_id
    ON notification_preferences(user_id);

-- ============================================================================
-- 5. COMMENTS FOR DOCUMENTATION
-- ============================================================================

-- Alerts table comments
COMMENT ON TABLE alerts IS 'Stores user-defined price and volume alerts';
COMMENT ON COLUMN alerts.alert_type IS 'Type of alert: PRICE_ABOVE, PRICE_BELOW, VOLUME_SPIKE, CHANGE_PERCENT_ABOVE, CHANGE_PERCENT_BELOW';
COMMENT ON COLUMN alerts.condition_value IS 'Threshold value that triggers the alert';
COMMENT ON COLUMN alerts.is_active IS 'Whether the alert is actively being monitored';
COMMENT ON COLUMN alerts.is_recurring IS 'If true, alert reactivates after being triggered';
COMMENT ON COLUMN alerts.triggered_at IS 'Timestamp when alert was last triggered';
COMMENT ON COLUMN alerts.triggered_value IS 'Actual value when alert was triggered';

-- Notifications table comments
COMMENT ON TABLE notifications IS 'Stores all user notifications from various sources';
COMMENT ON COLUMN notifications.notification_type IS 'Category of notification: ALERT, MARKET_EVENT, SYSTEM, PORTFOLIO';
COMMENT ON COLUMN notifications.priority IS 'Priority level: LOW, NORMAL, HIGH, URGENT';
COMMENT ON COLUMN notifications.is_read IS 'Whether user has read the notification';
COMMENT ON COLUMN notifications.read_at IS 'Timestamp when notification was marked as read';

-- Notification preferences table comments
COMMENT ON TABLE notification_preferences IS 'User preferences for notification delivery';
COMMENT ON COLUMN notification_preferences.email_enabled IS 'Master switch for email notifications';
COMMENT ON COLUMN notification_preferences.push_enabled IS 'Master switch for push notifications';
COMMENT ON COLUMN notification_preferences.in_app_enabled IS 'Master switch for in-app notifications';
COMMENT ON COLUMN notification_preferences.quiet_hours_start IS 'Start time for quiet hours (no notifications sent)';
COMMENT ON COLUMN notification_preferences.quiet_hours_end IS 'End time for quiet hours';

-- ============================================================================
-- 6. FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_alerts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for alerts updated_at
CREATE TRIGGER trigger_alerts_updated_at
BEFORE UPDATE ON alerts
FOR EACH ROW
EXECUTE FUNCTION update_alerts_updated_at();

-- Function to update notification_preferences updated_at timestamp
CREATE OR REPLACE FUNCTION update_notification_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for notification_preferences updated_at
CREATE TRIGGER trigger_notification_preferences_updated_at
BEFORE UPDATE ON notification_preferences
FOR EACH ROW
EXECUTE FUNCTION update_notification_preferences_updated_at();

-- Function to auto-set read_at timestamp
CREATE OR REPLACE FUNCTION set_notification_read_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_read = TRUE AND OLD.is_read = FALSE THEN
        NEW.read_at = CURRENT_TIMESTAMP;
    ELSIF NEW.is_read = FALSE THEN
        NEW.read_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for notification read_at
CREATE TRIGGER trigger_set_notification_read_at
BEFORE UPDATE OF is_read ON notifications
FOR EACH ROW
EXECUTE FUNCTION set_notification_read_at();

-- Function to create default notification preferences for new users
CREATE OR REPLACE FUNCTION create_default_notification_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO notification_preferences (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to create notification preferences for new users
CREATE TRIGGER trigger_create_notification_preferences
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_default_notification_preferences();

-- Function to clean up old notifications (older than 90 days)
CREATE OR REPLACE FUNCTION cleanup_old_notifications()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM notifications
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90 days'
    AND is_read = TRUE;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_notifications() IS 'Removes read notifications older than 90 days';

-- Function to get unread notification count
CREATE OR REPLACE FUNCTION get_unread_notification_count(p_user_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    unread_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO unread_count
    FROM notifications
    WHERE user_id = p_user_id
    AND is_read = FALSE;

    RETURN unread_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_unread_notification_count(INTEGER) IS 'Returns count of unread notifications for a user';

-- Function to deactivate triggered alert
CREATE OR REPLACE FUNCTION deactivate_triggered_alert()
RETURNS TRIGGER AS $$
BEGIN
    -- If alert is triggered and not recurring, deactivate it
    IF NEW.triggered_at IS NOT NULL AND OLD.triggered_at IS NULL THEN
        IF NEW.is_recurring = FALSE THEN
            NEW.is_active = FALSE;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to deactivate non-recurring alerts when triggered
CREATE TRIGGER trigger_deactivate_triggered_alert
BEFORE UPDATE OF triggered_at ON alerts
FOR EACH ROW
EXECUTE FUNCTION deactivate_triggered_alert();

COMMENT ON TRIGGER trigger_deactivate_triggered_alert ON alerts IS
'Automatically deactivates non-recurring alerts when triggered';

-- ============================================================================
-- 7. CREATE DEFAULT PREFERENCES FOR EXISTING USERS
-- ============================================================================

-- Insert default notification preferences for all existing users
INSERT INTO notification_preferences (user_id)
SELECT id FROM users
WHERE id NOT IN (SELECT user_id FROM notification_preferences)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================================
-- 8. GRANT PERMISSIONS (if using role-based access)
-- ============================================================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON alerts TO screener_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON notifications TO screener_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON notification_preferences TO screener_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE alerts_id_seq TO screener_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE notifications_id_seq TO screener_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE notification_preferences_id_seq TO screener_app_user;
