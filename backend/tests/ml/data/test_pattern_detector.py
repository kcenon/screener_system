
import pytest
import numpy as np
from app.ml.data.pattern_detector import PatternDetector


class TestPatternDetector:

    @pytest.fixture
    def detector(self):
        return PatternDetector()

    def test_detect_head_and_shoulders(self, detector):
        """Test head and shoulders detection"""
        # Create synthetic H&S pattern
        # Prices array needs to be long enough for peak detection
        prices = np.array([
            10, 11, 12, 11, 10,  # Left shoulder peak at 12
            10, 13, 15, 13, 10,  # Head peak at 15
            10, 11, 12, 11, 10   # Right shoulder peak at 12
        ])

        # Note: find_peaks needs some context, so we might need to adjust
        # the synthetic data to ensure peaks are detected with distance=5

        # Let's mock the internal logic or create a more robust synthetic signal
        # For unit testing the specific logic in the method:

        # Manually constructing a signal that find_peaks will like
        x = np.linspace(0, 30, 30)
        prices = np.zeros_like(x)

        # Left shoulder
        prices[5] = 12
        prices[4] = 10
        prices[6] = 10

        # Head
        prices[15] = 15
        prices[14] = 10
        prices[16] = 10

        # Right shoulder
        prices[25] = 12
        prices[24] = 10
        prices[26] = 10

        # Fill zeros with baseline
        prices[prices == 0] = 8

        # Test Head and Shoulders
        hs_pattern = detector.detect_head_and_shoulders(prices)
        assert hs_pattern["detected"] is True
        assert hs_pattern["confidence"] > 0.5

    def test_detect_double_top(self, detector):
        """Test double top detection"""
        # Two peaks at similar level
        prices = np.zeros(30)
        prices[:] = 10

        # Peak 1
        prices[5] = 15
        prices[4] = 12
        prices[6] = 12

        # Trough
        prices[15] = 10

        # Peak 2
        prices[25] = 15
        prices[24] = 12
        prices[26] = 12

        # Test Double Top
        dt_pattern = detector.detect_double_top(prices)
        assert dt_pattern["detected"] is True

    def test_detect_double_bottom(self, detector):
        """Test double bottom detection"""
        # Two troughs at similar level
        prices = np.zeros(30)
        prices[:] = 15

        # Trough 1
        prices[5] = 10
        prices[4] = 12
        prices[6] = 12

        # Peak
        prices[15] = 15

        # Trough 2
        prices[25] = 10
        prices[24] = 12
        prices[26] = 12

        # Test Double Bottom
        db_pattern = detector.detect_double_bottom(prices)
        assert db_pattern["detected"] is True

    def test_detect_flag(self, detector):
        """Test flag pattern detection"""
        # Prices moving in a narrow, downward-sloping channel after a sharp rise
        prices = np.linspace(10, 20, 10)  # Pole
        # Downward channel
        flag_prices = np.linspace(20, 18, 10) + np.sin(
            np.linspace(0, 2 * np.pi, 10)
        ) * 0.5
        prices = np.concatenate((prices, flag_prices))

        # Test Flag
        flag_pattern = detector.detect_flag(prices)
        assert flag_pattern["detected"] is True

    def test_detect_wedge(self, detector):
        """Test wedge pattern detection"""
        # Converging highs and lows, both sloping in the same direction
        prices = np.zeros(30)

        # Rising wedge (converging upwards)
        # Highs: 10, 11, 11.5
        prices[5] = 10
        prices[15] = 11
        prices[25] = 11.5

        # Lows: 5, 7, 8
        prices[2] = 5
        prices[10] = 7
        prices[20] = 8

        # Fill in between to make them peaks/troughs
        for i in range(30):
            if prices[i] == 0:
                prices[i] = 9

        # Test Wedge
        wedge_pattern = detector.detect_wedge(prices)
        assert wedge_pattern["detected"] is True

    def test_detect_triangle(self, detector):
        """Test triangle detection"""
        # Converging highs and lows
        prices = np.zeros(30)

        # Highs: 15, 14, 13
        prices[5] = 15
        prices[15] = 14
        prices[25] = 13

        # Lows: 5, 6, 7
        # Note: find_peaks(-prices) finds local minima
        prices[2] = 4  # Add an earlier low
        prices[10] = 5
        prices[20] = 6

        # Fill in between to make them peaks/troughs
        for i in range(30):
            if prices[i] == 0:
                prices[i] = 10

        assert detector.detect_triangle(prices)["detected"] is True
