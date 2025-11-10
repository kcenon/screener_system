-- ============================================================================
-- Migration: 06_add_calculated_indicators_updated_at.sql
-- Description: Add missing updated_at column to calculated_indicators table
-- Author: Database Team
-- Created: 2025-11-10
-- Fixes: BUGFIX-003
-- ============================================================================

-- Add updated_at column to calculated_indicators table
ALTER TABLE calculated_indicators
    ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();

COMMENT ON COLUMN calculated_indicators.updated_at IS 'Timestamp of last update';

-- Create trigger to automatically update updated_at on row modification
CREATE TRIGGER update_calculated_indicators_updated_at
    BEFORE UPDATE ON calculated_indicators
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TRIGGER update_calculated_indicators_updated_at ON calculated_indicators
    IS 'Automatically update updated_at timestamp when indicators are recalculated';
