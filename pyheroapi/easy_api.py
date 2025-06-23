"""
Easy-to-use wrapper for Kiwoom API - User-friendly interface.

This module provides a simplified, intuitive interface for the Kiwoom API
that handles authentication, retries, and data parsing automatically.
"""

import time
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import logging

from .client import KiwoomClient
from .exceptions import KiwoomAPIError, KiwoomAuthError
from .models import QuoteData, ETFData, ELWData, AccountBalance, Position


# Set up logging
logger = logging.getLogger(__name__)


class Stock:
    """User-friendly wrapper for stock operations."""
    
    def __init__(self, client: KiwoomClient, symbol: str):
        self._client = client
        self.symbol = symbol
        self._cache = {}
        self._cache_timeout = 5  # seconds
    
    def _get_cached_or_fetch(self, key: str, fetch_func):
        """Get data from cache or fetch if expired."""
        now = time.time()
        if key in self._cache and now - self._cache[key]['timestamp'] < self._cache_timeout:
            return self._cache[key]['data']
        
        data = fetch_func()
        self._cache[key] = {'data': data, 'timestamp': now}
        return data
    
    @property
    def current_price(self) -> Optional[float]:
        """Get current stock price."""
        try:
            quote = self._get_cached_or_fetch('quote', lambda: self._client.get_quote(self.symbol))
            # Extract price from quote data - this would need to be adjusted based on actual API response
            return float(quote.buy_fpr_bid) if quote.buy_fpr_bid else None
        except Exception as e:
            logger.warning(f"Failed to get current price for {self.symbol}: {e}")
            return None
    
    @property 
    def quote(self) -> Dict[str, Any]:
        """Get full quote data in a user-friendly format."""
        try:
            raw_quote = self._get_cached_or_fetch('quote', lambda: self._client.get_quote(self.symbol))
            return {
                'symbol': self.symbol,
                'best_bid': float(raw_quote.buy_fpr_bid) if raw_quote.buy_fpr_bid else None,
                'best_ask': float(raw_quote.sel_fpr_bid) if raw_quote.sel_fpr_bid else None,
                'total_bid_quantity': int(raw_quote.tot_buy_req) if raw_quote.tot_buy_req else None,
                'total_ask_quantity': int(raw_quote.tot_sel_req) if raw_quote.tot_sel_req else None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get quote for {self.symbol}: {e}")
            return {'symbol': self.symbol, 'error': str(e)}
    
    def history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical price data."""
        try:
            raw_data = self._client.get_daily_prices(self.symbol, period="D", count=days)
            # Convert to user-friendly format
            return [
                {
                    'date': item.get('date', ''),
                    'open': float(item.get('open', 0)) if item.get('open') else None,
                    'high': float(item.get('high', 0)) if item.get('high') else None,
                    'low': float(item.get('low', 0)) if item.get('low') else None,
                    'close': float(item.get('close', 0)) if item.get('close') else None,
                    'volume': int(item.get('volume', 0)) if item.get('volume') else None,
                }
                for item in raw_data
            ]
        except Exception as e:
            logger.error(f"Failed to get history for {self.symbol}: {e}")
            return []


class ETF:
    """User-friendly wrapper for ETF operations."""
    
    def __init__(self, client: KiwoomClient, symbol: str):
        self._client = client
        self.symbol = symbol
        self._cache = {}
        self._cache_timeout = 10  # ETF data changes less frequently
    
    def _get_cached_or_fetch(self, key: str, fetch_func):
        """Get data from cache or fetch if expired."""
        now = time.time()
        if key in self._cache and now - self._cache[key]['timestamp'] < self._cache_timeout:
            return self._cache[key]['data']
        
        data = fetch_func()
        self._cache[key] = {'data': data, 'timestamp': now}
        return data
    
    @property
    def info(self) -> Dict[str, Any]:
        """Get ETF information in user-friendly format."""
        try:
            raw_data = self._get_cached_or_fetch('info', lambda: self._client.get_etf_info(self.symbol))
            return {
                'symbol': self.symbol,
                'name': raw_data.name,
                'nav': float(raw_data.nav) if raw_data.nav else None,
                'tracking_error': float(raw_data.tracking_error) if raw_data.tracking_error else None,
                'discount_premium': float(raw_data.discount_premium) if raw_data.discount_premium else None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get ETF info for {self.symbol}: {e}")
            return {'symbol': self.symbol, 'error': str(e)}
    
    def returns(self, period: str = "1") -> Dict[str, Any]:
        """Get ETF returns for specified period."""
        try:
            # This would need adjustment based on actual API
            raw_data = self._client.get_etf_returns(self.symbol, "207", period)
            return {
                'symbol': self.symbol,
                'period': period,
                'returns': raw_data,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get ETF returns for {self.symbol}: {e}")
            return {'symbol': self.symbol, 'error': str(e)}


class ELW:
    """User-friendly wrapper for ELW operations."""
    
    def __init__(self, client: KiwoomClient, symbol: str):
        self._client = client
        self.symbol = symbol
        self._cache = {}
        self._cache_timeout = 5  # ELW data changes frequently
    
    def _get_cached_or_fetch(self, key: str, fetch_func):
        """Get data from cache or fetch if expired."""
        now = time.time()
        if key in self._cache and now - self._cache[key]['timestamp'] < self._cache_timeout:
            return self._cache[key]['data']
        
        data = fetch_func()
        self._cache[key] = {'data': data, 'timestamp': now}
        return data
    
    @property
    def info(self) -> Dict[str, Any]:
        """Get ELW information in user-friendly format."""
        try:
            raw_data = self._get_cached_or_fetch('info', lambda: self._client.get_elw_info(self.symbol))
            return {
                'symbol': self.symbol,
                'name': raw_data.name,
                'underlying_asset': raw_data.underlying_asset,
                'strike_price': float(raw_data.strike_price) if raw_data.strike_price else None,
                'expiry_date': raw_data.expiry_date,
                'conversion_ratio': float(raw_data.conversion_ratio) if raw_data.conversion_ratio else None,
                'greeks': {
                    'delta': float(raw_data.delta) if raw_data.delta else None,
                    'gamma': float(raw_data.gamma) if raw_data.gamma else None,
                    'theta': float(raw_data.theta) if raw_data.theta else None,
                    'vega': float(raw_data.vega) if raw_data.vega else None,
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get ELW info for {self.symbol}: {e}")
            return {'symbol': self.symbol, 'error': str(e)}
    
    @property
    def greeks(self) -> Dict[str, float]:
        """Get ELW Greeks (sensitivities)."""
        try:
            raw_data = self._get_cached_or_fetch('sensitivity', lambda: self._client.get_elw_sensitivity(self.symbol))
            # Assuming raw_data is a list, take first item
            if raw_data and len(raw_data) > 0:
                item = raw_data[0]
                return {
                    'delta': float(item.get('delta', 0)) if item.get('delta') else None,
                    'gamma': float(item.get('gam', 0)) if item.get('gam') else None,
                    'theta': float(item.get('theta', 0)) if item.get('theta') else None,
                    'vega': float(item.get('vega', 0)) if item.get('vega') else None,
                }
            return {}
        except Exception as e:
            logger.error(f"Failed to get ELW Greeks for {self.symbol}: {e}")
            return {}


class Account:
    """User-friendly wrapper for account operations."""
    
    def __init__(self, client: KiwoomClient, account_number: str):
        self._client = client
        self.account_number = account_number
        self._cache = {}
        self._cache_timeout = 30  # Account data can be cached longer
    
    def _get_cached_or_fetch(self, key: str, fetch_func):
        """Get data from cache or fetch if expired."""
        now = time.time()
        if key in self._cache and now - self._cache[key]['timestamp'] < self._cache_timeout:
            return self._cache[key]['data']
        
        data = fetch_func()
        self._cache[key] = {'data': data, 'timestamp': now}
        return data
    
    @property
    def balance(self) -> Dict[str, Any]:
        """Get account balance in user-friendly format."""
        try:
            raw_data = self._get_cached_or_fetch('balance', lambda: self._client.get_account_balance(self.account_number))
            return {
                'account_number': self.account_number,
                'total_balance': float(raw_data.total_balance) if raw_data.total_balance else None,
                'available_balance': float(raw_data.available_balance) if raw_data.available_balance else None,
                'deposit': float(raw_data.deposit) if raw_data.deposit else None,
                'substitute': float(raw_data.substitute) if raw_data.substitute else None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get account balance for {self.account_number}: {e}")
            return {'account_number': self.account_number, 'error': str(e)}
    
    @property
    def positions(self) -> List[Dict[str, Any]]:
        """Get all positions in user-friendly format."""
        try:
            raw_data = self._get_cached_or_fetch('positions', lambda: self._client.get_positions(self.account_number))
            return [
                {
                    'symbol': pos.symbol,
                    'name': pos.name,
                    'quantity': int(pos.quantity) if pos.quantity else None,
                    'available_quantity': int(pos.available_quantity) if pos.available_quantity else None,
                    'average_price': float(pos.average_price) if pos.average_price else None,
                    'current_price': float(pos.current_price) if pos.current_price else None,
                    'market_value': float(pos.evaluation_amount) if pos.evaluation_amount else None,
                    'profit_loss': float(pos.profit_loss) if pos.profit_loss else None,
                    'profit_loss_rate': float(pos.profit_loss_rate) if pos.profit_loss_rate else None,
                }
                for pos in raw_data
            ]
        except Exception as e:
            logger.error(f"Failed to get positions for {self.account_number}: {e}")
            return []


class KiwoomAPI:
    """
    Main user-friendly interface for Kiwoom API.
    
    This class provides a simple, intuitive way to interact with Kiwoom Securities API
    with automatic authentication, error handling, and data formatting.
    """
    
    def __init__(self, client: KiwoomClient):
        self._client = client
        self._token_expires = None
        
    @classmethod
    def connect(
        cls,
        app_key: str,
        secret_key: str,
        sandbox: bool = True,
        auto_retry: bool = True,
        cache_timeout: int = 5
    ) -> 'KiwoomAPI':
        """
        Connect to Kiwoom API with automatic token management.
        
        Args:
            app_key: Your Kiwoom app key
            secret_key: Your Kiwoom secret key  
            sandbox: Use sandbox environment (True) or production (False)
            auto_retry: Automatically retry failed requests
            cache_timeout: How long to cache data in seconds
            
        Returns:
            Connected KiwoomAPI instance
            
        Example:
            >>> api = KiwoomAPI.connect("your_key", "your_secret", sandbox=True)
            >>> price = api.stock("005930").current_price
        """
        try:
            # Create client with automatic token management
            client = KiwoomClient.create_with_credentials(
                appkey=app_key,
                secretkey=secret_key,
                is_production=not sandbox,
                retry_attempts=3 if auto_retry else 1,
                rate_limit_delay=0.1
            )
            
            instance = cls(client)
            instance._app_key = app_key
            instance._secret_key = secret_key
            instance._sandbox = sandbox
            
            logger.info(f"Successfully connected to Kiwoom API ({'sandbox' if sandbox else 'production'})")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to connect to Kiwoom API: {e}")
            raise KiwoomAPIError(f"Connection failed: {e}")
    
    def stock(self, symbol: str) -> Stock:
        """
        Get stock interface for the given symbol.
        
        Args:
            symbol: Stock symbol (e.g., "005930" for Samsung)
            
        Returns:
            Stock interface object
            
        Example:
            >>> samsung = api.stock("005930")
            >>> price = samsung.current_price
            >>> history = samsung.history(days=30)
        """
        return Stock(self._client, symbol)
    
    def etf(self, symbol: str) -> ETF:
        """
        Get ETF interface for the given symbol.
        
        Args:
            symbol: ETF symbol (e.g., "069500" for KODEX 200)
            
        Returns:
            ETF interface object
            
        Example:
            >>> kodex = api.etf("069500")
            >>> info = kodex.info
            >>> returns = kodex.returns(period="1")
        """
        return ETF(self._client, symbol)
    
    def elw(self, symbol: str) -> ELW:
        """
        Get ELW interface for the given symbol.
        
        Args:
            symbol: ELW symbol
            
        Returns:
            ELW interface object
            
        Example:
            >>> warrant = api.elw("57JBHH")
            >>> info = warrant.info
            >>> greeks = warrant.greeks
        """
        return ELW(self._client, symbol)
    
    def account(self, account_number: str) -> Account:
        """
        Get account interface for the given account number.
        
        Args:
            account_number: Account number
            
        Returns:
            Account interface object
            
        Example:
            >>> acc = api.account("12345678")
            >>> balance = acc.balance
            >>> positions = acc.positions
        """
        return Account(self._client, account_number)
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for stocks by name or symbol.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of stock information
        """
        try:
            results = self._client.search_stocks(query)
            return results[:limit] if results else []
        except Exception as e:
            logger.error(f"Stock search failed for '{query}': {e}")
            return []
    
    @property
    def market_status(self) -> Dict[str, Any]:
        """Get current market status."""
        try:
            return self._client.get_market_status()
        except Exception as e:
            logger.error(f"Failed to get market status: {e}")
            return {'error': str(e)}
    
    def disconnect(self):
        """Clean up and disconnect from API."""
        try:
            if hasattr(self, '_app_key') and hasattr(self, '_secret_key'):
                self._client.revoke_current_token(self._app_key, self._secret_key)
                logger.info("Successfully disconnected and revoked token")
        except Exception as e:
            logger.warning(f"Failed to revoke token during disconnect: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatic cleanup."""
        self.disconnect()


# Convenience function for quick access
def connect(app_key: str, secret_key: str, sandbox: bool = True) -> KiwoomAPI:
    """
    Quick connect function.
    
    Example:
        >>> import kiwoom_api
        >>> api = kiwoom_api.connect("your_key", "your_secret")
        >>> price = api.stock("005930").current_price
    """
    return KiwoomAPI.connect(app_key, secret_key, sandbox) 