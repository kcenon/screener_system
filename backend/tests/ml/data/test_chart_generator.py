
import pytest
import numpy as np
from app.ml.data.chart_generator import ChartImageGenerator

class TestChartImageGenerator:

    @pytest.fixture
    def generator(self):
        return ChartImageGenerator(image_size=(224, 224), lookback_days=60)

    @pytest.fixture
    def sample_ohlcv(self):
        """Generate sample OHLCV data"""
        np.random.seed(42)
        # Random walk for prices
        prices = np.zeros(60)
        prices[0] = 100
        for i in range(1, 60):
            prices[i] = prices[i-1] + np.random.randn()
            
        # Create OHLC from close prices (simplified)
        ohlcv = np.zeros((60, 5))
        for i in range(60):
            close = prices[i]
            open_ = close + np.random.randn() * 0.5
            high = max(open_, close) + abs(np.random.randn() * 0.5)
            low = min(open_, close) - abs(np.random.randn() * 0.5)
            volume = abs(np.random.randn() * 1000) + 100
            ohlcv[i] = [open_, high, low, close, volume]
            
        return ohlcv

    def test_generate_chart_dimensions(self, generator, sample_ohlcv):
        """Test chart image has correct dimensions"""
        img = generator.generate_chart(sample_ohlcv)

        assert img.shape == (224, 224, 3)
        assert img.dtype == np.uint8

    def test_generate_chart_values(self, generator, sample_ohlcv):
        """Test chart image has valid pixel values"""
        img = generator.generate_chart(sample_ohlcv)

        assert img.min() >= 0
        assert img.max() <= 255
        # Should not be completely black or white
        assert img.mean() > 0
        assert img.mean() < 255

    def test_generate_different_data(self, generator):
        """Test different data produces different images"""
        np.random.seed(1)
        data1 = np.random.rand(60, 5) * 100
        np.random.seed(2)
        data2 = np.random.rand(60, 5) * 100

        img1 = generator.generate_chart(data1)
        img2 = generator.generate_chart(data2)

        assert not np.array_equal(img1, img2)
