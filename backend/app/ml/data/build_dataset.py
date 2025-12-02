import argparse
import os
import shutil

import numpy as np
from app.ml.data.chart_generator import ChartImageGenerator
from PIL import Image


def generate_synthetic_data(pattern_type, length=60):
    """Generate synthetic OHLCV data with specific pattern"""
    # Base random walk
    prices = np.zeros(length)
    prices[0] = 100
    for i in range(1, length):
        prices[i] = prices[i - 1] + np.random.randn()

    # Inject pattern at the end
    if pattern_type == "head_and_shoulders":
        # Inject H&S
        center = length - 15
        prices[center - 5] = prices[center - 5] * 1.05  # Left shoulder
        prices[center] = prices[center] * 1.10  # Head
        prices[center + 5] = prices[center + 5] * 1.05  # Right shoulder
    elif pattern_type == "double_top":
        center = length - 10
        prices[center - 5] = prices[center - 5] * 1.10  # Peak 1
        prices[center] = prices[center] * 0.95  # Trough
        prices[center + 5] = prices[center + 5] * 1.10  # Peak 2

    elif pattern_type == "triangle":
        # Converging
        start = length - 20
        for i in range(20):
            scale = (20 - i) / 20.0
            prices[start + i] = 100 + np.sin(i) * scale * 5

    # Create OHLCV
    ohlcv = np.zeros((length, 5))
    for i in range(length):
        close = prices[i]
        open_ = close + np.random.randn() * 0.5
        high = max(open_, close) + abs(np.random.randn() * 0.5)
        low = min(open_, close) - abs(np.random.randn() * 0.5)
        volume = abs(np.random.randn() * 1000) + 100
        ohlcv[i] = [open_, high, low, close, volume]

    return ohlcv


def build_dataset(output_dir, samples_per_class=100):
    """Build synthetic dataset"""

    generator = ChartImageGenerator()
    # detector = PatternDetector()  # Unused

    patterns = ["head_and_shoulders", "double_top", "triangle", "none"]
    splits = ["train", "val", "test"]
    split_ratios = [0.7, 0.2, 0.1]

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    for split in splits:
        for pattern in patterns:
            os.makedirs(os.path.join(output_dir, split, pattern), exist_ok=True)

    print(f"Generating {samples_per_class} samples per class...")

    for pattern in patterns:
        count = 0
        while count < samples_per_class:
            # Generate data
            if pattern == "none":
                # Random data
                data = generate_synthetic_data("random")
            else:
                data = generate_synthetic_data(pattern)

            # Verify pattern (optional, for synthetic we assume it's correct mostly)
            # detected = detector.detect_pattern(data)
            # if detected != pattern: continue

            # Generate image
            img = generator.generate_chart(data)

            # Determine split
            rand = np.random.random()
            if rand < split_ratios[0]:
                split = "train"
            elif rand < split_ratios[0] + split_ratios[1]:
                split = "val"
            else:
                split = "test"

            # Save
            filename = os.path.join(
                output_dir, split, pattern, f"{pattern}_{count}.png"
            )
            Image.fromarray(img).save(filename)
            count += 1

    print(f"Dataset generated at {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", default="data/patterns")
    parser.add_argument("--samples", type=int, default=50)
    args = parser.parse_args()

    build_dataset(args.output_dir, args.samples)
