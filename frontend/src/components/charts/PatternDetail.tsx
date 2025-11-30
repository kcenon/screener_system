import React from 'react';
import { Pattern } from '@/types/pattern';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface PatternDetailProps {
  pattern: Pattern;
  onClose: () => void;
}

export const PatternDetail: React.FC<PatternDetailProps> = ({ pattern, onClose }) => {
  const isBullish = pattern.expected_movement === 'bullish';
  const colorClass = isBullish ? 'text-green-500' : 'text-red-500';
  
  return (
    <div className="absolute top-4 right-4 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 w-64 z-10">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          {isBullish ? <TrendingUp className={colorClass} size={18} /> : <TrendingDown className={colorClass} size={18} />}
          {pattern.pattern_type}
        </h3>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
          ×
        </button>
      </div>
      
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-500 dark:text-gray-400">Confidence</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">{(pattern.confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${isBullish ? 'bg-green-500' : 'bg-red-500'}`} 
              style={{ width: `${pattern.confidence * 100}%` }}
            />
          </div>
        </div>
        
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Detected: {new Date(pattern.detected_at).toLocaleString()}
        </div>
        
        {pattern.breakout_level && (
           <div className="text-sm">
            <span className="text-gray-500 dark:text-gray-400">Breakout Level: </span>
            <span className="font-medium text-gray-900 dark:text-gray-100">{pattern.breakout_level}</span>
           </div>
        )}
      </div>
    </div>
  );
};
