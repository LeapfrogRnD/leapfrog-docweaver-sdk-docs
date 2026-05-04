"""
Structured logging configuration using loguru.

Production mode uses structured JSON logging suitable for AWS CloudWatch.
"""

import os
import sys

from config.settings import settings
from loguru import logger


def setup_logger():
    """Configure loguru logger with structured output."""

    logger.remove()

    # ===============================
    # Production Environment (AWS)
    # ===============================
    if settings.ENVIRONMENT == "staging":
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL or "INFO",
            serialize=True,
            enqueue=True,
            backtrace=False,
            diagnose=False,
        )

    # ===============================
    # Development Environment
    # ===============================
    else:
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL or "DEBUG",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level:<8} | "
                "{name}:{function}:{line} | "
                "{message} | "
                "{extra}"
            ),
            colorize=True,
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

    # ===============================
    # Optional File Logging (Production)
    # ===============================
    if settings.ENVIRONMENT == "staging":
        log_path = f"/var/log/{settings.APP_NAME}"

        os.makedirs(log_path, exist_ok=True)

        logger.add(
            f"{log_path}/app.log",
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            level="INFO",
            serialize=False,  # File logs can be plain text if needed
        )

    return logger


# Initialize logger
log = setup_logger()

__all__ = ["log"]
