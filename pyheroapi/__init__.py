"""
Kiwoom API Python Client

A Python client library for interacting with Kiwoom Securities REST API.
Provides easy-to-use interfaces for market data, trading, and account management.
"""

from .client import KiwoomClient
from .easy_api import KiwoomAPI, Stock, ETF, ELW, Account, connect
from .exceptions import KiwoomAPIError, KiwoomAuthError, KiwoomRequestError
from .models import (
    QuoteData,
    MarketData,
    OrderData,
    ETFData,
    ELWData,
    AccountBalance,
    Position,
    TokenRequest,
    TokenResponse,
    TokenRevokeRequest,
    TokenRevokeResponse
)

__version__ = "0.2.1"
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