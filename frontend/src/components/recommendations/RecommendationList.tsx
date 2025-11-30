import React, { useEffect, useState } from 'react';
import { RecommendationCard } from './RecommendationCard';
import axios from 'axios';

interface Recommendation {
  stock_code: string;
  company_name: string;
  sector: string;
  current_price: number;
  recommendation_score: number;
  confidence: number;
  reasons: string[];
  ai_prediction: {
    direction: string;
    probability: number;
  };
  key_metrics: {
    per: number;
    pbr: number;
    dividend_yield: number;
  };
}

export const RecommendationList: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        // In a real app, use configured API client
        const response = await axios.get('http://localhost:8000/v1/recommendations/daily');
        setRecommendations(response.data);
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  if (loading) {
    return <div className="animate-pulse h-64 bg-gray-100 dark:bg-gray-800 rounded-lg"></div>;
  }

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recommended for You</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recommendations.map((rec) => (
          <RecommendationCard key={rec.stock_code} recommendation={rec} />
        ))}
      </div>
    </div>
  );
};
