"""Skip all ML tests when ML dependencies are not installed."""

import importlib

import pytest

# Check if real numpy is available (not a MagicMock)
_ml_available = False
try:
    numpy = importlib.import_module("numpy")
    # MagicMock won't have __version__
    if hasattr(numpy, "__version__"):
        _ml_available = True
except ImportError:
    pass


def pytest_collection_modifyitems(config, items):
    """Skip ML tests when ML packages are mocked (not actually installed)."""
    if _ml_available:
        return

    skip_ml = pytest.mark.skip(reason="ML dependencies not installed")
    for item in items:
        if "/ml/" in str(item.fspath):
            item.add_marker(skip_ml)
