-- ML Features Table
-- Stores processed features for ML model training

CREATE TABLE IF NOT EXISTS ml_features (
    stock_code VARCHAR(6) NOT NULL,
    calculation_date DATE NOT NULL,
    feature_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (stock_code, calculation_date),
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE
);

-- Index for faster retrieval by date
CREATE INDEX IF NOT EXISTS idx_ml_features_date ON ml_features(calculation_date DESC);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_ml_features_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_ml_features_timestamp
    BEFORE UPDATE ON ml_features
    FOR EACH ROW
    EXECUTE FUNCTION update_ml_features_updated_at();

-- Comments
COMMENT ON TABLE ml_features IS 'Stores preprocessed ML features for stocks';
COMMENT ON COLUMN ml_features.feature_data IS 'JSONB object containing all feature values';
