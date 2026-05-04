import os
import sys
from contextvars import ContextVar

from loguru import logger as _logger

# ============================================================
# Context variables (per-request correlation support)
# ============================================================

request_id_ctx: ContextVar[str] = ContextVar("request_id", default=None)
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default=None)


def set_request_id(request_id: str):
    request_id_ctx.set(request_id)


def set_correlation_id(correlation_id: str):
    correlation_id_ctx.set(correlation_id)


def _inject_context(record):
    """
    Inject request_id and correlation_id automatically into every log.
    """
    record["extra"]["request_id"] = request_id_ctx.get()
    record["extra"]["correlation_id"] = correlation_id_ctx.get()


# ============================================================
# Logger configuration
# ============================================================

_logger.remove()

MODE = os.getenv("MODE", "DEV")

if MODE == "staging":
    _logger.add(
        sys.stdout,
        level="INFO",
        serialize=True,
        enqueue=True,  # async safe
        backtrace=False,
        diagnose=False,
    )
else:
    # Developer-friendly console logs
    _logger.add(
        sys.stdout,
        level="DEBUG",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level:<8} | "
            "{name}:{function}:{line} | "
            "{message} | "
            "{extra}"
        ),
        colorize=True,
    )

# Inject correlation IDs automatically
_logger = _logger.patch(_inject_context)


# ============================================================
# Structured Logger Wrapper
# ============================================================


class StructuredLogger:
    """
    Wrapper around loguru to support structured logging.
    """

    def __init__(self, logger):
        self._logger = logger

    def bind(self, **kwargs):
        return self._logger.bind(**kwargs)

    def debug(self, message: str, **kwargs):
        self._logger.bind(**kwargs).debug(message)

    def info(self, message: str, **kwargs):
        self._logger.bind(**kwargs).info(message)

    def warning(self, message: str, **kwargs):
        self._logger.bind(**kwargs).warning(message)

    def error(self, message: str, **kwargs):
        self._logger.bind(**kwargs).error(message)

    def critical(self, message: str, **kwargs):
        self._logger.bind(**kwargs).critical(message)

    def exception(self, message: str, **kwargs):
        self._logger.bind(**kwargs).exception(message)

    def __getattr__(self, name):
        return getattr(self._logger, name)


logger = StructuredLogger(_logger)

__all__ = [
    "logger",
    "set_correlation_id",
    "set_request_id",
]
