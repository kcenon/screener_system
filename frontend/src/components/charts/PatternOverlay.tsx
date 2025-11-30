import React, { useEffect, useState, useRef } from 'react';
import { IChartApi, ISeriesApi, Time } from 'lightweight-charts';
import { Pattern } from '@/types/pattern';

interface PatternOverlayProps {
  chart: IChartApi;
  series: ISeriesApi<'Candlestick' | 'Line' | 'Area' | 'Bar'>;
  patterns: Pattern[];
  width: number;
  height: number;
  onPatternClick?: (pattern: Pattern) => void;
}

export const PatternOverlay: React.FC<PatternOverlayProps> = ({
  chart,
  series,
  patterns,
  width,
  height,
  onPatternClick,
}) => {
  const [overlayPaths, setOverlayPaths] = useState<React.ReactNode[]>([]);
  const requestRef = useRef<number>();

  const updateOverlay = () => {
    if (!chart || !series) return;

    const newPaths: React.ReactNode[] = [];

    patterns.forEach((pattern) => {
      const points = pattern.coordinates.map((coord) => {
        const time = coord.x as Time;
        const price = coord.y;
        
        const x = chart.timeScale().timeToCoordinate(time);
        const y = series.priceToCoordinate(price);
        
        return { x, y };
      });

      // Filter out points that are off-screen (null coordinates)
      const validPoints = points.filter(p => p.x !== null && p.y !== null) as {x: number, y: number}[];

      if (validPoints.length < 2) return;

      const pathData = validPoints.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ');
      
      const color = pattern.expected_movement === 'bullish' ? '#22c55e' : '#ef4444';

      newPaths.push(
        <g key={pattern.pattern_id} onClick={() => onPatternClick?.(pattern)} style={{ cursor: 'pointer' }}>
          <path
            d={pathData}
            stroke={color}
            strokeWidth={2}
            fill="none"
            strokeDasharray="5,5"
          />
          {validPoints.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r={4} fill={color} />
          ))}
          {/* Highlight area */}
           <path
            d={pathData}
            stroke={color}
            strokeWidth={15}
            fill="none"
            opacity={0.1}
          />
        </g>
      );
    });

    setOverlayPaths(newPaths);
  };

  useEffect(() => {
    // Subscribe to visible time range changes
    const handleTimeChange = () => {
       requestRef.current = requestAnimationFrame(updateOverlay);
    };

    chart.timeScale().subscribeVisibleLogicalRangeChange(handleTimeChange);
    
    // Initial update
    updateOverlay();

    return () => {
      chart.timeScale().unsubscribeVisibleLogicalRangeChange(handleTimeChange);
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [chart, series, patterns, width, height]);

  return (
    <svg
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: width,
        height: height,
        pointerEvents: 'none', // Allow clicks to pass through to chart, but we need clicks on patterns
        zIndex: 2,
      }}
    >
      {/* Enable pointer events for patterns */}
      <g style={{ pointerEvents: 'auto' }}>
        {overlayPaths}
      </g>
    </svg>
  );
};
