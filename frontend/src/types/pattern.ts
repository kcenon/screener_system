export interface PatternCoordinate {
  x: number; // timestamp
  y: number; // price
}

export interface Pattern {
  pattern_id: string;
  pattern_type: string;
  confidence: number;
  detected_at: string;
  timeframe: string;
  coordinates: PatternCoordinate[];
  expected_movement?: 'bullish' | 'bearish';
  breakout_level?: number;
  metadata?: Record<string, any>;
}

export interface PatternResponse {
  pattern_id: string;
  pattern_type: string;
  confidence: number;
  detected_at: string;
  timeframe: string;
  metadata?: Record<string, any>;
}
