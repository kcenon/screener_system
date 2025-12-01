import numpy as np
import pandas as pd
import pytest
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
            prices[i] = prices[i - 1] + np.random.randn()

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

    def test_create_chart_image(self, generator):
        """Test chart image creation from DataFrame"""
        # Create dummy data
        dates = pd.date_range(start="2023-01-01", periods=30)
        data = {
            "open": np.linspace(100, 200, 30),
            "high": np.linspace(110, 210, 30),
            "low": np.linspace(90, 190, 30),
            "close": np.linspace(105, 205, 30),
            "volume": np.random.randint(1000, 10000, 30),
        }
        df = pd.DataFrame(data, index=dates)

        # Generate image
        image_bytes = generator.create_chart_image(df)

        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_create_chart_image_empty(self, generator):
        """Test chart image creation with empty data"""
        df = pd.DataFrame()
        with pytest.raises(ValueError):
            generator.create_chart_image(df)
