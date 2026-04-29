"""
Custom exceptions for DailyWriting application.
"""

from __future__ import annotations


class DailyWritingError(Exception):
    """Base exception for all DailyWriting errors."""
    pass


class StorageError(DailyWritingError):
    """Error during session storage operations (save, load, delete)."""

    def __init__(self, message: str, path: str | None = None, operation: str | None = None):
        self.path = path
        self.operation = operation
        super().__init__(message)


class SessionNotFoundError(StorageError):
    """Requested session does not exist."""

    def __init__(self, session_id: str, path: str | None = None):
        self.session_id = session_id
        super().__init__(
            f"Session not found: {session_id}",
            path=path,
            operation="load"
        )


class TopicGenerationError(DailyWritingError):
    """Error during AI topic generation."""

    def __init__(self, message: str, is_api_error: bool = False, is_timeout: bool = False):
        self.is_api_error = is_api_error
        self.is_timeout = is_timeout
        super().__init__(message)


class ConfigError(DailyWritingError):
    """Error loading or saving configuration."""
    pass
