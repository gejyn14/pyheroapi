"""
Easy-to-use wrapper for Kiwoom API - User-friendly interface.

This module provides a simplified, intuitive interface for the Kiwoom API
that handles authentication, retries, and data parsing automatically.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from .client import KiwoomClient
from .exceptions import KiwoomAPIError, KiwoomAuthError

# Optional real-time functionality
try:
    from .realtime import KiwoomRealtimeClient, create_realtime_client
    _REALTIME_AVAILABLE = True
except ImportError:
    _REALTIME_AVAILABLE = False
from .models import AccountBalance, ELWData, ETFData, Position, QuoteData

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
        if (
            key in self._cache
            and now - self._cache[key]["timestamp"] < self._cache_timeout
        ):
            return self._cache[key]["data"]

        data = fetch_func()
        self._cache[key] = {"data": data, "timestamp": now}
        return data

    @property
    def current_price(self) -> Optional[float]:
        """Get current stock price."""
        try:
            quote = self._get_cached_or_fetch(
                "quote", lambda: self._client.get_quote(self.symbol)
            )
            # Extract price from quote data - this would need to be adjusted based on actual API response
            return float(quote.buy_fpr_bid) if quote.buy_fpr_bid else None
        except Exception as e:
            logger.warning(f"Failed to get current price for {self.symbol}: {e}")
            return None

    @property
    def quote(self) -> Dict[str, Any]:
        """Get full quote data in a user-friendly format."""
        try:
            raw_quote = self._get_cached_or_fetch(
                "quote", lambda: self._client.get_quote(self.symbol)
            )
            return {
                "symbol": self.symbol,
                "best_bid": (
                    float(raw_quote.buy_fpr_bid) if raw_quote.buy_fpr_bid else None
                ),
                "best_ask": (
                    float(raw_quote.sel_fpr_bid) if raw_quote.sel_fpr_bid else None
                ),
                "total_bid_quantity": (
                    int(raw_quote.tot_buy_req) if raw_quote.tot_buy_req else None
                ),
                "total_ask_quantity": (
                    int(raw_quote.tot_sel_req) if raw_quote.tot_sel_req else None
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get quote for {self.symbol}: {e}")
            return {"symbol": self.symbol, "error": str(e)}

    def history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical price data."""
        try:
            raw_data = self._client.get_daily_prices(
                self.symbol, period="D", count=days
            )
            # Convert to user-friendly format
            return [
                {
                    "date": item.get("date", ""),
                    "open": float(item.get("open", 0)) if item.get("open") else None,
                    "high": float(item.get("high", 0)) if item.get("high") else None,
                    "low": float(item.get("low", 0)) if item.get("low") else None,
                    "close": float(item.get("close", 0)) if item.get("close") else None,
                    "volume": (
                        int(item.get("volume", 0)) if item.get("volume") else None
                    ),
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
        if (
            key in self._cache
            and now - self._cache[key]["timestamp"] < self._cache_timeout
        ):
            return self._cache[key]["data"]

        data = fetch_func()
        self._cache[key] = {"data": data, "timestamp": now}
        return data

    @property
    def info(self) -> Dict[str, Any]:
        """Get ETF information in user-friendly format."""
        try:
            raw_data = self._get_cached_or_fetch(
                "info", lambda: self._client.get_etf_info(self.symbol)
            )
            return {
                "symbol": self.symbol,
                "name": raw_data.name,
                "nav": float(raw_data.nav) if raw_data.nav else None,
                "tracking_error": (
                    float(raw_data.tracking_error) if raw_data.tracking_error else None
                ),
                "discount_premium": (
                    float(raw_data.discount_premium)
                    if raw_data.discount_premium
                    else None
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get ETF info for {self.symbol}: {e}")
            return {"symbol": self.symbol, "error": str(e)}

    def returns(self, period: str = "1") -> Dict[str, Any]:
        """Get ETF returns for specified period."""
        try:
            # This would need adjustment based on actual API
            raw_data = self._client.get_etf_returns(self.symbol, "207", period)
            return {
                "symbol": self.symbol,
                "period": period,
                "returns": raw_data,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get ETF returns for {self.symbol}: {e}")
            return {"symbol": self.symbol, "error": str(e)}


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
        if (
            key in self._cache
            and now - self._cache[key]["timestamp"] < self._cache_timeout
        ):
            return self._cache[key]["data"]

        data = fetch_func()
        self._cache[key] = {"data": data, "timestamp": now}
        return data

    @property
    def info(self) -> Dict[str, Any]:
        """Get ELW information in user-friendly format."""
        try:
            raw_data = self._get_cached_or_fetch(
                "info", lambda: self._client.get_elw_info(self.symbol)
            )
            return {
                "symbol": self.symbol,
                "name": raw_data.name,
                "underlying_asset": raw_data.underlying_asset,
                "strike_price": (
                    float(raw_data.strike_price) if raw_data.strike_price else None
                ),
                "expiry_date": raw_data.expiry_date,
                "conversion_ratio": (
                    float(raw_data.conversion_ratio)
                    if raw_data.conversion_ratio
                    else None
                ),
                "greeks": {
                    "delta": float(raw_data.delta) if raw_data.delta else None,
                    "gamma": float(raw_data.gamma) if raw_data.gamma else None,
                    "theta": float(raw_data.theta) if raw_data.theta else None,
                    "vega": float(raw_data.vega) if raw_data.vega else None,
                },
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get ELW info for {self.symbol}: {e}")
            return {"symbol": self.symbol, "error": str(e)}

    @property
    def greeks(self) -> Dict[str, float]:
        """Get ELW Greeks (sensitivities)."""
        try:
            raw_data = self._get_cached_or_fetch(
                "sensitivity", lambda: self._client.get_elw_sensitivity(self.symbol)
            )
            # Assuming raw_data is a list, take first item
            if raw_data and len(raw_data) > 0:
                item = raw_data[0]
                return {
                    "delta": float(item.get("delta", 0)) if item.get("delta") else None,
                    "gamma": float(item.get("gam", 0)) if item.get("gam") else None,
                    "theta": float(item.get("theta", 0)) if item.get("theta") else None,
                    "vega": float(item.get("vega", 0)) if item.get("vega") else None,
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
        self._cache_timeout = 30  # Account data changes less frequently

    def _get_cached_or_fetch(self, key: str, fetch_func):
        """Get data from cache or fetch if expired."""
        now = time.time()
        if (
            key in self._cache
            and now - self._cache[key]["timestamp"] < self._cache_timeout
        ):
            return self._cache[key]["data"]

        data = fetch_func()
        self._cache[key] = {"data": data, "timestamp": now}
        return data

    @property
    def balance(self) -> Dict[str, Any]:
        """Get account balance in user-friendly format."""
        try:
            raw_balance = self._get_cached_or_fetch(
                "balance", lambda: self._client.get_account_balance(self.account_number)
            )
            return {
                "account_number": self.account_number,
                "total_balance": (
                    float(raw_balance.total_balance)
                    if raw_balance.total_balance
                    else 0.0
                ),
                "available_balance": (
                    float(raw_balance.available_balance)
                    if raw_balance.available_balance
                    else 0.0
                ),
                "securities_balance": (
                    float(raw_balance.securities_balance)
                    if raw_balance.securities_balance
                    else 0.0
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(
                f"Failed to get balance for account {self.account_number}: {e}"
            )
            return {
                "account_number": self.account_number,
                "error": str(e),
                "total_balance": 0.0,
                "available_balance": 0.0,
                "securities_balance": 0.0,
            }

    @property
    def positions(self) -> List[Dict[str, Any]]:
        """Get account positions in user-friendly format."""
        try:
            raw_positions = self._get_cached_or_fetch(
                "positions", lambda: self._client.get_positions(self.account_number)
            )
            return [
                {
                    "symbol": pos.symbol,
                    "quantity": int(pos.quantity) if pos.quantity else 0,
                    "average_price": (
                        float(pos.average_price) if pos.average_price else 0.0
                    ),
                    "current_price": (
                        float(pos.current_price) if pos.current_price else 0.0
                    ),
                    "market_value": (
                        float(pos.market_value) if pos.market_value else 0.0
                    ),
                    "unrealized_pnl": (
                        float(pos.unrealized_pnl) if pos.unrealized_pnl else 0.0
                    ),
                    "unrealized_pnl_rate": (
                        float(pos.unrealized_pnl_rate)
                        if pos.unrealized_pnl_rate
                        else 0.0
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
                for pos in raw_positions
            ]
        except Exception as e:
            logger.error(
                f"Failed to get positions for account {self.account_number}: {e}"
            )
            return []

    @property
    def unfilled_orders(self) -> List[Dict[str, Any]]:
        """Get unfilled orders in user-friendly format."""
        try:
            raw_orders = self._client.get_unfilled_orders()
            return [
                {
                    "order_number": order.ord_no,
                    "symbol": order.stk_cd,
                    "stock_name": order.stk_nm,
                    "order_quantity": int(order.ord_qty) if order.ord_qty else 0,
                    "order_price": float(order.ord_uv) if order.ord_uv else 0.0,
                    "remaining_quantity": int(order.rmn_qty) if order.rmn_qty else 0,
                    "order_type": order.ord_dvsn,
                    "order_time": order.ord_tm,
                    "timestamp": datetime.now().isoformat(),
                }
                for order in raw_orders
            ]
        except Exception as e:
            logger.error(f"Failed to get unfilled orders: {e}")
            return []

    @property
    def filled_orders(self) -> List[Dict[str, Any]]:
        """Get today's filled orders in user-friendly format."""
        try:
            raw_orders = self._client.get_filled_orders()
            return [
                {
                    "order_number": order.ord_no,
                    "symbol": order.stk_cd,
                    "stock_name": order.stk_nm,
                    "order_quantity": int(order.ord_qty) if order.ord_qty else 0,
                    "order_price": float(order.ord_uv) if order.ord_uv else 0.0,
                    "filled_quantity": int(order.cntr_qty) if order.cntr_qty else 0,
                    "filled_price": float(order.cntr_uv) if order.cntr_uv else 0.0,
                    "filled_time": order.cntr_tm,
                    "order_type": order.ord_dvsn,
                    "timestamp": datetime.now().isoformat(),
                }
                for order in raw_orders
            ]
        except Exception as e:
            logger.error(f"Failed to get filled orders: {e}")
            return []

    def get_profit_loss(
        self, symbol: str, start_date: str, end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get profit/loss for a specific stock."""
        try:
            if end_date:
                raw_pnl = self._client.get_period_stock_profit_loss(
                    symbol, start_date, end_date
                )
            else:
                raw_pnl = self._client.get_daily_stock_profit_loss(symbol, start_date)

            return [
                {
                    "symbol": symbol,
                    "stock_name": pnl.stk_nm,
                    "quantity": int(pnl.cntr_qty) if pnl.cntr_qty else 0,
                    "buy_price": float(pnl.buy_uv) if pnl.buy_uv else 0.0,
                    "sell_price": float(pnl.cntr_pric) if pnl.cntr_pric else 0.0,
                    "realized_pnl": float(pnl.tdy_sel_pl) if pnl.tdy_sel_pl else 0.0,
                    "pnl_rate": float(pnl.pl_rt) if pnl.pl_rt else 0.0,
                    "commission": (
                        float(pnl.tdy_trde_cmsn) if pnl.tdy_trde_cmsn else 0.0
                    ),
                    "tax": float(pnl.tdy_trde_tax) if pnl.tdy_trde_tax else 0.0,
                    "timestamp": datetime.now().isoformat(),
                }
                for pnl in raw_pnl
            ]
        except Exception as e:
            logger.error(f"Failed to get profit/loss for {symbol}: {e}")
            return []

    def get_return_rate(self, period: str = "1") -> Dict[str, Any]:
        """Get account return rate for specified period."""
        try:
            raw_return = self._client.get_account_return_rate(period)
            return {
                "period": period,
                "return_rate": raw_return.get("return_rate", 0.0),
                "profit_loss": raw_return.get("profit_loss", 0.0),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get return rate: {e}")
            return {"period": period, "error": str(e)}


class Trading:
    """User-friendly wrapper for trading operations."""

    def __init__(self, client: KiwoomClient):
        self._client = client

    def buy(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "market",
        market: str = "KRX",
    ) -> Dict[str, Any]:
        """
        Place a buy order with user-friendly parameters.

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price per share (None for market orders)
            order_type: "market", "limit", "stop", etc.
            market: Market type

        Returns:
            Order result with order number
        """
        try:
            # Convert user-friendly order type to API format
            order_type_map = {"market": "3", "limit": "0", "stop": "28", "best": "6"}
            api_order_type = order_type_map.get(order_type.lower(), "3")

            result = self._client.buy_stock(
                symbol=symbol,
                quantity=quantity,
                price=price,
                order_type=api_order_type,
                market=market,
            )

            return {
                "success": True,
                "order_number": result.ord_no,
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "order_type": order_type,
                "market": market,
                "message": result.return_msg,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to place buy order for {symbol}: {e}")
            return {
                "success": False,
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def sell(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "market",
        market: str = "KRX",
    ) -> Dict[str, Any]:
        """
        Place a sell order with user-friendly parameters.

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price per share (None for market orders)
            order_type: "market", "limit", "stop", etc.
            market: Market type

        Returns:
            Order result with order number
        """
        try:
            # Convert user-friendly order type to API format
            order_type_map = {"market": "3", "limit": "0", "stop": "28", "best": "6"}
            api_order_type = order_type_map.get(order_type.lower(), "3")

            result = self._client.sell_stock(
                symbol=symbol,
                quantity=quantity,
                price=price,
                order_type=api_order_type,
                market=market,
            )

            return {
                "success": True,
                "order_number": result.ord_no,
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "order_type": order_type,
                "market": market,
                "message": result.return_msg,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to place sell order for {symbol}: {e}")
            return {
                "success": False,
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def modify_order(
        self,
        order_number: str,
        symbol: str,
        new_quantity: int,
        new_price: float,
        market: str = "KRX",
    ) -> Dict[str, Any]:
        """
        Modify an existing order.

        Args:
            order_number: Original order number
            symbol: Stock symbol
            new_quantity: New quantity
            new_price: New price
            market: Market type

        Returns:
            Modification result
        """
        try:
            result = self._client.modify_order(
                original_order_number=order_number,
                symbol=symbol,
                new_quantity=new_quantity,
                new_price=new_price,
                market=market,
            )

            return {
                "success": True,
                "new_order_number": result.ord_no,
                "original_order_number": order_number,
                "symbol": symbol,
                "new_quantity": new_quantity,
                "new_price": new_price,
                "message": result.return_msg,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to modify order {order_number}: {e}")
            return {
                "success": False,
                "order_number": order_number,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def cancel_order(
        self, order_number: str, symbol: str, quantity: int, market: str = "KRX"
    ) -> Dict[str, Any]:
        """
        Cancel an existing order.

        Args:
            order_number: Order number to cancel
            symbol: Stock symbol
            quantity: Quantity to cancel
            market: Market type

        Returns:
            Cancellation result
        """
        try:
            result = self._client.cancel_order(
                original_order_number=order_number,
                symbol=symbol,
                cancel_quantity=quantity,
                market=market,
            )

            return {
                "success": True,
                "cancelled_order_number": result.ord_no,
                "original_order_number": order_number,
                "symbol": symbol,
                "cancelled_quantity": quantity,
                "message": result.return_msg,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to cancel order {order_number}: {e}")
            return {
                "success": False,
                "order_number": order_number,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


class KiwoomAPI:
    """
    Main user-friendly API wrapper that provides easy access to all Kiwoom functionality.

    This class provides a simplified interface that handles authentication,
    caching, error handling, and data formatting automatically.
    """

    def __init__(self, client: KiwoomClient):
        self._client = client
        self.trading = Trading(client)
        self._realtime_client = None

    @classmethod
    def connect(
        cls,
        app_key: str,
        secret_key: str,
        sandbox: bool = True,
        auto_retry: bool = True,
        cache_timeout: int = 5,
    ) -> "KiwoomAPI":
        """
        Create a KiwoomAPI instance with automatic authentication.

        Args:
            app_key: Your Kiwoom app key
            secret_key: Your Kiwoom secret key
            sandbox: Whether to use sandbox (True) or production (False)
            auto_retry: Whether to automatically retry failed requests
            cache_timeout: Cache timeout in seconds

        Returns:
            Connected KiwoomAPI instance

        Example:
            ```python
            import pyheroapi

            # Connect to sandbox
            api = pyheroapi.connect("app_key", "secret_key", sandbox=True)

            # Get stock price
            price = api.stock("005930").current_price

            # Place a buy order
            result = api.trading.buy("005930", 10, 75000, "limit")
            ```
        """
        try:
            client = KiwoomClient.create_with_credentials(
                appkey=app_key,
                secretkey=secret_key,
                is_production=not sandbox,
                retry_attempts=3 if auto_retry else 1,
            )
            logger.info(
                f"✅ Connected to Kiwoom API ({'sandbox' if sandbox else 'production'})"
            )
            return cls(client)
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kiwoom API: {e}")
            raise

    def stock(self, symbol: str) -> Stock:
        """
        Get a Stock wrapper for the given symbol.

        Args:
            symbol: Stock symbol (e.g., "005930" for Samsung)

        Returns:
            Stock wrapper instance

        Example:
            ```python
            samsung = api.stock("005930")
            price = samsung.current_price
            quote = samsung.quote
            history = samsung.history(30)
            ```
        """
        return Stock(self._client, symbol)

    def etf(self, symbol: str) -> ETF:
        """
        Get an ETF wrapper for the given symbol.

        Args:
            symbol: ETF symbol (e.g., "069500" for KODEX 200)

        Returns:
            ETF wrapper instance

        Example:
            ```python
            kodex = api.etf("069500")
            info = kodex.info
            returns = kodex.returns("3")
            ```
        """
        return ETF(self._client, symbol)

    def elw(self, symbol: str) -> ELW:
        """
        Get an ELW wrapper for the given symbol.

        Args:
            symbol: ELW symbol

        Returns:
            ELW wrapper instance

        Example:
            ```python
            elw = api.elw("57JBHH")
            info = elw.info
            greeks = elw.greeks
            ```
        """
        return ELW(self._client, symbol)

    def account(self, account_number: str) -> Account:
        """
        Get an Account wrapper for the given account number.

        Args:
            account_number: Your account number

        Returns:
            Account wrapper instance

        Example:
            ```python
            account = api.account("1234567890")
            balance = account.balance
            positions = account.positions
            unfilled = account.unfilled_orders
            filled = account.filled_orders
            pnl = account.get_profit_loss("005930", "20241201", "20241210")
            ```
        """
        return Account(self._client, account_number)

    def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for stocks by name or symbol.

        Args:
            query: Search query (stock name or symbol)
            limit: Maximum number of results

        Returns:
            List of matching stocks
        """
        try:
            results = self._client.search_stocks(query)[:limit]
            return [
                {
                    "symbol": result.get("symbol", ""),
                    "name": result.get("name", ""),
                    "market": result.get("market", ""),
                    "timestamp": datetime.now().isoformat(),
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Failed to search stocks for '{query}': {e}")
            return []

    @property
    def market_status(self) -> Dict[str, Any]:
        """
        Get current market status.

        Returns:
            Market status information
        """
        try:
            status = self._client.get_market_status()
            return {
                "is_open": status.get("is_open", False),
                "market_time": status.get("market_time", ""),
                "next_open": status.get("next_open", ""),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get market status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def create_realtime_client(self, **kwargs) -> "KiwoomRealtimeClient":
        """
        Create a real-time WebSocket client for market data streaming.
        
        Args:
            **kwargs: Additional arguments for KiwoomRealtimeClient
        
        Returns:
            KiwoomRealtimeClient instance
            
        Raises:
            ImportError: If websockets library is not installed
        """
        if not _REALTIME_AVAILABLE:
            raise ImportError(
                "Real-time functionality requires 'websockets' package. "
                "Install with: pip install pyheroapi[realtime]"
            )
        
        if self._realtime_client is None:
            self._realtime_client = create_realtime_client(
                access_token=self._client.access_token,
                is_production=self._client.base_url == self._client.PRODUCTION_URL,
                **kwargs
            )
        
        return self._realtime_client
    
    @property
    def realtime(self) -> "KiwoomRealtimeClient":
        """
        Access real-time market data client.
        
        Returns:
            KiwoomRealtimeClient instance (creates if not exists)
            
        Example:
            ```python
            import asyncio
            
            async def price_callback(data):
                print(f"Price update: {data.symbol} = {data.values.get('10')}")
            
            # Create API connection
            api = pyheroapi.connect("app_key", "secret_key")
            
            # Get real-time client
            rt_client = api.realtime
            
            # Add callback and subscribe
            rt_client.add_callback("0B", price_callback)
            await rt_client.connect()
            await rt_client.subscribe_stock_price("005930")
            ```
        """
        if self._realtime_client is None:
            self._realtime_client = self.create_realtime_client()
        return self._realtime_client

    def disconnect(self):
        """
        Clean up resources and disconnect from the API.

        This method should be called when you're done using the API,
        or you can use the context manager form to automatically clean up.
        """
        try:
            # Disconnect real-time client if exists
            if self._realtime_client:
                import asyncio
                if asyncio.get_event_loop().is_running():
                    # If in async context, schedule disconnect
                    asyncio.create_task(self._realtime_client.disconnect())
                else:
                    # If not in async context, run disconnect
                    asyncio.run(self._realtime_client.disconnect())
            # Could add token revocation here if needed
            logger.info("🔌 Disconnected from Kiwoom API")
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.disconnect()


def connect(app_key: str, secret_key: str, sandbox: bool = True) -> KiwoomAPI:
    """
    Convenience function to connect to Kiwoom API.

    This is equivalent to KiwoomAPI.connect() but shorter to type.

    Args:
        app_key: Your Kiwoom app key
        secret_key: Your Kiwoom secret key
        sandbox: Whether to use sandbox (True) or production (False)

    Returns:
        Connected KiwoomAPI instance

    Example:
        ```python
        import pyheroapi

        # Simple connection
        api = pyheroapi.connect("app_key", "secret_key")

        # With context manager for automatic cleanup
        with pyheroapi.connect("app_key", "secret_key") as api:
            price = api.stock("005930").current_price
            result = api.trading.buy("005930", 10, 75000)
        ```
    """
    return KiwoomAPI.connect(app_key, secret_key, sandbox)
