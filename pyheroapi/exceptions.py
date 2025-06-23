"""
Exception classes for Kiwoom API client.
"""

from typing import Any, Dict, Optional


class KiwoomAPIError(Exception):
    """Base exception for all Kiwoom API errors."""

    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.response_data = response_data


class KiwoomAuthError(KiwoomAPIError):
    """Raised when authentication fails."""

    pass


class KiwoomRequestError(KiwoomAPIError):
    """Raised when a request fails due to client or server error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, response_data)
        self.status_code = status_code


class KiwoomRateLimitError(KiwoomAPIError):
    """Raised when rate limit is exceeded."""

    pass


class KiwoomServerError(KiwoomAPIError):
    """Raised when server returns a 5xx error."""

    pass
