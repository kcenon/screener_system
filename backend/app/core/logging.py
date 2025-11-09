"""Logging configuration for the application"""

import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """
    Configure application logging

    Returns:
        Logger instance for the application
    """
    # Create logger
    logger = logging.getLogger("screener")

    # Set log level based on environment
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = setup_logging()
