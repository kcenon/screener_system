import { render, screen, waitFor } from '@testing-library/react';
import { RecommendationList } from '../RecommendationList';
import axios from 'axios';
import { vi, describe, it, expect } from 'vitest';

vi.mock('axios');

const mockRecommendations = [
  {
    stock_code: 'AAPL',
    company_name: 'Apple Inc.',
    sector: 'Technology',
    current_price: 150.0,
    recommendation_score: 0.95,
    confidence: 0.9,
    reasons: ['Reason 1', 'Reason 2'],
    ai_prediction: {
      direction: 'bullish',
      probability: 0.85,
    },
    key_metrics: {
      per: 25.5,
      pbr: 10.2,
      dividend_yield: 0.5,
    },
  },
];

describe('RecommendationList', () => {
  it('renders recommendations after fetching', async () => {
    (axios.get as any).mockResolvedValue({ data: mockRecommendations });

    render(<RecommendationList />);

    await waitFor(() => {
      expect(screen.getByText('Recommended for You')).toBeInTheDocument();
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
    });
  });

  it('renders nothing if no recommendations', async () => {
    (axios.get as any).mockResolvedValue({ data: [] });

    render(<RecommendationList />);

    await waitFor(() => {
      expect(screen.queryByText('Recommended for You')).not.toBeInTheDocument();
    });
  });
});
