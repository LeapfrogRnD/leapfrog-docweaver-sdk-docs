"""Logger configuration for layout parser.

This module configures loguru for consistent logging throughout
the layout parser service.
"""

import os
import sys
from enum import Enum

from dotenv import load_dotenv
from loguru import logger as _logger

load_dotenv()

# Remove default handler
_logger.remove()

# Console handler - show all logs in terminal
_logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level> | "
        "<blue>{extra}</blue>"
    ),
    level="INFO" if os.getenv("MODE") == "PROD" else "DEBUG",
    colorize=True,
    backtrace=False,
    diagnose=False,
    enqueue=False,
)

# File handler for info.log - logs INFO level and above
_logger.add(
    "/tmp/info.log",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message} | "
        "{extra}"
    ),
    level="INFO",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    enqueue=False,
)

# File handler for error.log - logs ERROR level and above
_logger.add(
    "/tmp/error.log",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message} | "
        "{extra}"
    ),
    level="ERROR",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    backtrace=False,
    diagnose=True,
    enqueue=False,
)


class StructuredLogger:
    """Wrapper around loguru logger to support extra parameters."""

    def __init__(self, logger):
        self._logger = logger

    def _format_extra(self, **kwargs) -> str:
        """Format extra parameters as key=value pairs."""
        if not kwargs:
            return ""
        return " | ".join(f"{k}={v}" for k, v in kwargs.items())

    def _format_stage_message(self, stage_name: str, status: str) -> str:
        """Format a standardized stage log message.

        Args:
            stage_name: Name of the stage (e.g., "extraction", "ocr")
            status: Status of the stage (e.g., "completed", "started", "failed")

        Returns:
            Formatted log message string
        """
        return f"{stage_name.capitalize()} {status}"

    def debug(self, message: str, **kwargs):
        extra_str = self._format_extra(**kwargs)
        full_message = f"{message} {extra_str}".strip()
        self._logger.bind(extra=extra_str).debug(full_message)

    def info(self, message: str, **kwargs):
        extra_str = self._format_extra(**kwargs)
        full_message = f"{message} {extra_str}".strip()
        self._logger.bind(extra=extra_str).info(full_message)

    def warning(self, message: str, **kwargs):
        extra_str = self._format_extra(**kwargs)
        full_message = f"{message} {extra_str}".strip()
        self._logger.bind(extra=extra_str).warning(full_message)

    def error(self, message: str, **kwargs):
        extra_str = self._format_extra(**kwargs)
        full_message = f"{message} {extra_str}".strip()
        self._logger.bind(extra=extra_str).error(full_message)

    def stage_log(
        self,
        stage_name: str | Enum,
        status: str,
        level: str = "info",
        **kwargs,
    ):
        """Log a stage event with standardized formatting.

        Args:
            stage_name: Name of the stage (e.g., "extraction", "ocr")
            status: Status of the stage (e.g., "completed", "started", "failed")
            level: Log level (debug, info, warning, error, critical).
                Defaults to "info".
            **kwargs: Additional context to include (e.g., stage_id, duration)
        """
        if isinstance(stage_name, Enum):
            stage_name = stage_name.value
        message = self._format_stage_message(stage_name, status)
        log_method = getattr(self, level.lower(), self.info)
        log_method(message, **kwargs)

    def critical(self, message: str, **kwargs):
        extra_str = self._format_extra(**kwargs)
        full_message = f"{message} {extra_str}".strip()
        self._logger.bind(extra=extra_str).critical(full_message)

    # Delegate other methods to the original logger
    def __getattr__(self, name):
        return getattr(self._logger, name)


# Export structured logger instance
logger = StructuredLogger(_logger)

__all__ = ["logger"]
