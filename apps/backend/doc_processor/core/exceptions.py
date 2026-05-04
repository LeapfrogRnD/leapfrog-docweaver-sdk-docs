"""Custom exceptions for the document processor."""


class ProcessorException(Exception):
    """Base exception for processor errors."""


class TaskNotFoundException(ProcessorException):
    """Raised when a task is not found in the database."""


class TaskLockedException(ProcessorException):
    """Raised when a task is already being processed by another worker."""


class LeapXProcessingException(ProcessorException):
    """Raised when LeapX SDK processing fails."""
