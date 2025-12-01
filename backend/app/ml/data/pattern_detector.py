from typing import Optional

import numpy as np
from scipy.signal import find_peaks


class PatternDetector:
    """Detect technical chart patterns in OHLCV data"""

    def detect_head_and_shoulders(self, prices: np.ndarray) -> bool:
        """
        Detect Head and Shoulders pattern

        Args:
            prices: Close prices array

        Returns:
            True if pattern detected
        """
        # Find peaks
        peaks, _ = find_peaks(prices, distance=5)

        if len(peaks) < 3:
            return False

        # Check for three peaks with middle highest
        # We look at the last 3 peaks found in the window
        if len(peaks) >= 3:
            left_peak, head, right_peak = peaks[-3:]

            # Basic H&S logic: Head > Shoulders
            if prices[head] > prices[left_peak] and prices[head] > prices[right_peak]:
                # Check shoulders at similar level (within 5% tolerance)
                if (
                    abs(prices[left_peak] - prices[right_peak]) / prices[left_peak]
                    < 0.05
                ):
                    return True

        return False

    def detect_double_top(self, prices: np.ndarray) -> bool:
        """Detect Double Top pattern"""
        peaks, _ = find_peaks(prices, distance=10)

        if len(peaks) < 2:
            return False

        # Last two peaks
        peak1, peak2 = peaks[-2:]

        # Check peaks at similar level (within 2%)
        if abs(prices[peak1] - prices[peak2]) / prices[peak1] < 0.02:
            # Check trough between peaks
            # Find minimum between the two peaks
            trough_idx = np.argmin(prices[peak1:peak2]) + peak1

            # Trough should be significantly lower (e.g., > 5% drop from peak)
            avg_peak_price = (prices[peak1] + prices[peak2]) / 2
            if prices[trough_idx] < avg_peak_price * 0.95:
                return True

        return False

    def detect_triangle(self, prices: np.ndarray) -> bool:
        """Detect Triangle pattern (Symmetrical)"""
        # Find highs and lows
        highs, _ = find_peaks(prices, distance=5)
        lows, _ = find_peaks(-prices, distance=5)

        if len(highs) < 3 or len(lows) < 3:
            return False

        # Check if highs are descending and lows are ascending (converging)
        # Simple linear regression on the last 3 points
        try:
            high_trend = np.polyfit(highs[-3:], prices[highs[-3:]], 1)
            low_trend = np.polyfit(lows[-3:], prices[lows[-3:]], 1)

            # Highs descending (slope < 0), lows ascending (slope > 0)
            if high_trend[0] < -0.01 and low_trend[0] > 0.01:
                return True
        except Exception:
            pass

        return False

    def detect_pattern(self, ohlcv_data: np.ndarray) -> Optional[str]:
        """
        Detect all patterns and return pattern name

        Args:
            ohlcv_data: Array of OHLCV data

        Returns:
            Pattern name or None
        """
        close_prices = ohlcv_data[:, 3]  # Close prices

        if self.detect_head_and_shoulders(close_prices):
            return "head_and_shoulders"
        elif self.detect_double_top(close_prices):
            return "double_top"
        elif self.detect_triangle(close_prices):
            return "triangle"
        # ... more patterns can be added here

        return None

    def build_labeled_dataset(
        self, stock_codes: list, start_date: str, end_date: str, output_dir: str
    ):
        """
        Generate labeled dataset for all patterns

        Args:
            stock_codes: List of stock codes
            start_date: Start date
            end_date: End date
            output_dir: Output directory
        """
        # This implementation requires dependencies like ChartImageGenerator
        # and data fetching which we will mock or assume available in integration.
        # For unit testing purposes, we focus on the detection logic above.
        pass
