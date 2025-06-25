"""
Kiwoom API Python Client

A Python client library for interacting with Kiwoom Securities REST API.
Provides easy-to-use interfaces for market data, trading, account management, and real-time data streaming.
"""

from .client import KiwoomClient
from .easy_api import ELW, ETF, Account, KiwoomAPI, Stock, connect
from .exceptions import KiwoomAPIError, KiwoomAuthError, KiwoomRequestError
from .models import (
    AccountBalance,
    ELWData,
    ETFData,
    MarketData,
    OrderData,
    Position,
    QuoteData,
    TokenRequest,
    TokenResponse,
    TokenRevokeRequest,
    TokenRevokeResponse,
)

# Real-time functionality (optional import)
try:
    from .realtime import (
        KiwoomRealtimeClient,
        RealtimeData,
        RealtimeDataType,
        RealtimeSubscription,
        RealtimeContext,
        create_realtime_client,
        create_realtime_client_with_credentials,
        ConditionalSearchItem,
        ConditionalSearchResult,
        ConditionalSearchRealtimeData,
    )
    _REALTIME_AVAILABLE = True
except ImportError:
    _REALTIME_AVAILABLE = False
    # Provide stub classes for documentation
    class KiwoomRealtimeClient:
        def __init__(self, *args, **kwargs):
            raise ImportError("Real-time functionality requires 'websockets' package. Install with: pip install websockets")

__version__ = "0.3.3"
__author__ = "Kiwoom API Client"
__email__ = "contact@example.com"

__all__ = [
    # Easy-to-use API (recommended for most users)
    "KiwoomAPI",
    "Stock",
    "ETF",
    "ELW",
    "Account",
    "connect",  # Quick connect function
    # Original client (for advanced users)
    "KiwoomClient",
    # Exceptions
    "KiwoomAPIError",
    "KiwoomAuthError",
    "KiwoomRequestError",
    # Data models
    "QuoteData",
    "MarketData",
    "OrderData",
    "ETFData",
    "ELWData",
    "AccountBalance",
    "Position",
    "TokenRequest",
    "TokenResponse",
    "TokenRevokeRequest",
    "TokenRevokeResponse",
]

# Add real-time exports if available
if _REALTIME_AVAILABLE:
    __all__.extend([
        "KiwoomRealtimeClient",
        "RealtimeData",
        "RealtimeDataType",
        "RealtimeSubscription",
        "RealtimeContext",
        "create_realtime_client",
        "create_realtime_client_with_credentials",
        "ConditionalSearchItem",
        "ConditionalSearchResult",
        "ConditionalSearchRealtimeData",
    ])
