import io

import matplotlib
import numpy as np
from PIL import Image

matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


class ChartImageGenerator:
    """Generate candlestick chart images from OHLCV data"""

    def __init__(self, image_size=(224, 224), lookback_days=60):
        self.image_size = image_size
        self.lookback_days = lookback_days

    def generate_chart(self, ohlcv_data: np.ndarray) -> np.ndarray:
        """
        Generate candlestick chart image

        Args:
            ohlcv_data: Array of shape (N, 5) with OHLC and Volume
                       Columns: [Open, High, Low, Close, Volume]

        Returns:
            RGB image array of shape (224, 224, 3)
        """
        # Create figure without GUI
        plt.ioff()
        fig, (ax1, ax2) = plt.subplots(
            2,
            1,
            figsize=(self.image_size[0] / 100, self.image_size[1] / 100),
            gridspec_kw={"height_ratios": [3, 1]},
            dpi=100,
        )

        # Remove axes, labels, ticks
        for ax in [ax1, ax2]:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)

        # Plot candlesticks
        self._plot_candlesticks(ax1, ohlcv_data[:, :4])  # OHLC

        # Plot volume
        self._plot_volume(ax2, ohlcv_data[:, 4])  # Volume

        # Convert to image array
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
        img = img.resize(self.image_size)

        plt.close(fig)

        return np.array(img)

    def create_chart_image(self, df) -> bytes:
        """
        Create chart image from DataFrame and return bytes
        """
        if df.empty:
            raise ValueError("DataFrame is empty")

        # Convert DataFrame to numpy array expected by generate_chart
        # Expected columns: Open, High, Low, Close, Volume
        # We assume the DataFrame has these columns (case-insensitive)
        df = df.rename(columns=str.lower)
        required_cols = ["open", "high", "low", "close", "volume"]

        if not all(col in df.columns for col in required_cols):
            # Fallback or error? For now, assume columns exist or try to use iloc
            # If columns are missing, this will fail.
            pass

        ohlcv_data = df[required_cols].values

        # Generate chart (returns numpy array)
        # But we want bytes. We can reuse the logic or convert back.
        # Since generate_chart converts PIL->Numpy, we might want to refactor.
        # But to minimize changes, let's just use generate_chart and convert back to PNG bytes.

        img_array = self.generate_chart(ohlcv_data)
        img = Image.fromarray(img_array)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def _plot_candlesticks(self, ax, ohlc_data):
        """Plot candlestick chart"""
        # Calculate width of each candle
        width = 0.6
        for i, (open_, high, low, close) in enumerate(ohlc_data):
            color = "green" if close >= open_ else "red"

            # Plot high-low line
            ax.plot([i, i], [low, high], color=color, linewidth=0.5)

            # Plot open-close box
            height = abs(close - open_)
            bottom = min(open_, close)
            # Ensure minimum height for visibility
            if height == 0:
                height = (high - low) * 0.01 if high != low else 0.01

            rect = mpatches.Rectangle(
                (i - width / 2, bottom), width, height, facecolor=color, edgecolor=color
            )
            ax.add_patch(rect)
        ax.set_xlim(-1, len(ohlc_data))
        # Set Y limits with some padding
        min_price = ohlc_data[:, 2].min()
        max_price = ohlc_data[:, 1].max()
        padding = (max_price - min_price) * 0.05
        if padding == 0:
            padding = 1.0

        ax.set_ylim(min_price - padding, max_price + padding)

    def _plot_volume(self, ax, volume_data):
        """Plot volume bars"""
        ax.bar(range(len(volume_data)), volume_data, color="blue", alpha=0.5, width=0.8)
        ax.set_xlim(-1, len(volume_data))
        ax.set_ylim(0, volume_data.max() * 1.1 if volume_data.max() > 0 else 1)

    def generate_dataset(
        self, stock_codes: list, start_date: str, end_date: str, output_dir: str
    ):
        """
        Generate chart images for multiple stocks

        Args:
            stock_codes: List of stock codes
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_dir: Directory to save images
        """
        # This would typically import from repository, but to keep this class
        # independent we'll assume data fetching is handled outside or injected.
        # For now, this is a placeholder for the batch generation logic.
        pass
