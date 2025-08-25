"""
Easy-to-use wrapper for Kiwoom API - User-friendly interface.

This module provides a simplified, intuitive interface for the Kiwoom API
that handles authentication, retries, and data parsing automatically.
"""

import logging
import os
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
                "success": result.get("return_code") == 0,
                "order_number": result.get("ord_no"),
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "order_type": order_type,
                "market": market,
                "message": result.get("return_msg"),
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
                "success": result.get("return_code") == 0,
                "order_number": result.get("ord_no"),
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "order_type": order_type,
                "market": market,
                "message": result.get("return_msg"),
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
                "success": result.get("return_code") == 0,
                "new_order_number": result.get("ord_no"),
                "original_order_number": order_number,
                "symbol": symbol,
                "new_quantity": new_quantity,
                "new_price": new_price,
                "message": result.get("return_msg"),
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
                "success": result.get("return_code") == 0,
                "cancelled_order_number": result.get("ord_no"),
                "original_order_number": order_number,
                "symbol": symbol,
                "cancelled_quantity": quantity,
                "message": result.get("return_msg"),
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

    def credit_buy(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "market",
        market: str = "KRX",
    ) -> Dict[str, Any]:
        """
        Place a credit buy order (margin trading).

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

            result = self._client.credit_buy_stock(
                symbol=symbol,
                quantity=quantity,
                price=price,
                order_type=api_order_type,
                market=market,
            )

            return {
                "success": result.get("return_code") == 0,
                "order_number": result.get("ord_no"),
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "order_type": order_type,
                "market": market,
                "trade_type": "credit_buy",
                "message": result.get("return_msg"),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to place credit buy order for {symbol}: {e}")
            return {
                "success": False,
                "symbol": symbol,
                "trade_type": "credit_buy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def credit_sell(
        self,
        symbol: str,
        quantity: int,
        price: Optional[float] = None,
        order_type: str = "market",
        market: str = "KRX",
        credit_deal_type: str = "margin_combined",
        credit_loan_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Place a credit sell order (short selling).

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price per share (None for market orders)
            order_type: "market", "limit", "stop", etc.
            market: Market type
            credit_deal_type: "margin", "margin_combined"
            credit_loan_date: Loan date in YYYYMMDD format (required for margin)

        Returns:
            Order result with order number
        """
        try:
            # Convert user-friendly order type to API format
            order_type_map = {"market": "3", "limit": "0", "stop": "28", "best": "6"}
            api_order_type = order_type_map.get(order_type.lower(), "3")

            # Convert credit deal type
            credit_type_map = {"margin": "33", "margin_combined": "99"}
            api_credit_type = credit_type_map.get(credit_deal_type, "99")

            result = self._client.credit_sell_stock(
                symbol=symbol,
                quantity=quantity,
                price=price,
                order_type=api_order_type,
                market=market,
                credit_deal_type=api_credit_type,
                credit_loan_date=credit_loan_date,
            )

            return {
                "success": result.get("return_code") == 0,
                "order_number": result.get("ord_no"),
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "order_type": order_type,
                "market": market,
                "trade_type": "credit_sell",
                "credit_deal_type": credit_deal_type,
                "message": result.get("return_msg"),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to place credit sell order for {symbol}: {e}")
            return {
                "success": False,
                "symbol": symbol,
                "trade_type": "credit_sell",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def credit_modify_order(
        self,
        order_number: str,
        symbol: str,
        new_quantity: int,
        new_price: float,
        market: str = "KRX",
    ) -> Dict[str, Any]:
        """
        Modify an existing credit order.

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
            result = self._client.credit_modify_order(
                original_order_number=order_number,
                symbol=symbol,
                new_quantity=new_quantity,
                new_price=new_price,
                market=market,
            )

            return {
                "success": result.get("return_code") == 0,
                "new_order_number": result.get("ord_no"),
                "original_order_number": order_number,
                "symbol": symbol,
                "new_quantity": new_quantity,
                "new_price": new_price,
                "trade_type": "credit_modify",
                "message": result.get("return_msg"),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to modify credit order {order_number}: {e}")
            return {
                "success": False,
                "order_number": order_number,
                "trade_type": "credit_modify",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def credit_cancel_order(
        self, order_number: str, symbol: str, quantity: int, market: str = "KRX"
    ) -> Dict[str, Any]:
        """
        Cancel an existing credit order.

        Args:
            order_number: Order number to cancel
            symbol: Stock symbol
            quantity: Quantity to cancel
            market: Market type

        Returns:
            Cancellation result
        """
        try:
            result = self._client.credit_cancel_order(
                original_order_number=order_number,
                symbol=symbol,
                cancel_quantity=quantity,
                market=market,
            )

            return {
                "success": result.get("return_code") == 0,
                "cancelled_order_number": result.get("ord_no"),
                "original_order_number": order_number,
                "symbol": symbol,
                "cancelled_quantity": quantity,
                "trade_type": "credit_cancel",
                "message": result.get("return_msg"),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to cancel credit order {order_number}: {e}")
            return {
                "success": False,
                "order_number": order_number,
                "trade_type": "credit_cancel",
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
        self.chart = Chart(client)
        self.theme = Theme(client)
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
            # For sandbox mode, check if mock environment variables are set
            if sandbox:
                mock_appkey = os.getenv("MOCK_KIWOOM_APPKEY")
                mock_secretkey = os.getenv("MOCK_KIWOOM_SECRETKEY")
                
                if mock_appkey and mock_secretkey:
                    app_key = mock_appkey
                    secret_key = mock_secretkey
            
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


class Chart:
    """User-friendly chart data interface"""
    
    def __init__(self, client):
        self.client = client
    
    def stock_investor_institution(
        self,
        symbol: str,
        date: str = "",
        amount_or_quantity: str = "amount",  # "amount" or "quantity"
        trade_type: str = "net_buy",         # "net_buy", "buy", "sell"
        unit: str = "thousand"               # "thousand" or "single"
    ) -> List[Dict[str, Any]]:
        """
        Get stock investor/institution chart data.
        종목별 투자자/기관별 차트 데이터
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            date: Date in YYYYMMDD format (empty for today)
            amount_or_quantity: "amount" for 금액, "quantity" for 수량
            trade_type: "net_buy", "buy", or "sell"
            unit: "thousand" for 천주, "single" for 단주
            
        Returns:
            List of investor/institution chart data
        """
        # Convert user-friendly parameters
        amt_qty_map = {"amount": "1", "quantity": "2"}
        trade_map = {"net_buy": "0", "buy": "1", "sell": "2"}
        unit_map = {"thousand": "1000", "single": "1"}
        
        return self.client.get_stock_investor_institution_chart(
            date=date or "",
            symbol=symbol,
            amount_quantity_type=amt_qty_map.get(amount_or_quantity, "1"),
            trade_type=trade_map.get(trade_type, "0"),
            unit_type=unit_map.get(unit, "1000")
        )
    
    def intraday_investor_trading(
        self,
        symbol: str = "005930",
        market: str = "all",               # "all", "kospi", "kosdaq"
        amount_or_quantity: str = "amount", # "amount" or "quantity"
        trade_type: str = "net_buy"        # "net_buy", "buy", "sell"
    ) -> List[Dict[str, Any]]:
        """
        Get intraday investor trading chart data.
        장중 투자자별 매매 차트 데이터
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            market: "all", "kospi", or "kosdaq"
            amount_or_quantity: "amount" for 금액, "quantity" for 수량
            trade_type: "net_buy", "buy", or "sell"
            
        Returns:
            List of intraday investor trading chart data
        """
        # Convert user-friendly parameters
        market_map = {"all": "000", "kospi": "001", "kosdaq": "101"}
        amt_qty_map = {"amount": "1", "quantity": "2"}
        trade_map = {"net_buy": "0", "buy": "1", "sell": "2"}
        
        return self.client.get_intraday_investor_trading_chart(
            market_type=market_map.get(market, "000"),
            amount_quantity_type=amt_qty_map.get(amount_or_quantity, "1"),
            trade_type=trade_map.get(trade_type, "0"),
            symbol=symbol
        )
    
    def stock_tick(
        self,
        symbol: str,
        scope: str = "all",              # "all" for 전체
        adjusted: bool = True            # True for 수정주가
    ) -> Dict[str, Any]:
        """
        Get stock tick chart data.
        주식 틱 차트 데이터
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            scope: "all" for 전체
            adjusted: True for adjusted prices
            
        Returns:
            Dictionary with tick chart data including symbol and tick data list
        """
        return self.client.get_stock_tick_chart(
            symbol=symbol,
            tick_scope="1" if scope == "all" else "1",
            adjusted_price_type="1" if adjusted else "0"
        )
    
    def stock_minute(
        self,
        symbol: str,
        minutes: int = 1,               # 1, 3, 5, 10, 15, 30, 60
        adjusted: bool = True           # True for 수정주가
    ) -> Dict[str, Any]:
        """
        Get stock minute chart data.
        주식 분봉 차트 데이터
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            minutes: Time interval (1, 3, 5, 10, 15, 30, 60)
            adjusted: True for adjusted prices
            
        Returns:
            Dictionary with minute chart data including symbol and minute data list
        """
        return self.client.get_stock_minute_chart(
            symbol=symbol,
            minute_type=str(minutes),
            adjusted_price_type="1" if adjusted else "0"
        )
    
    def stock_daily(
        self,
        symbol: str,
        base_date: str = "",            # YYYYMMDD format, empty for today
        adjusted: bool = True           # True for 수정주가
    ) -> Dict[str, Any]:
        """
        Get stock daily chart data.
        주식 일봉 차트 데이터
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            base_date: Base date in YYYYMMDD format (empty for today)
            adjusted: True for adjusted prices
            
        Returns:
            Dictionary with daily chart data including symbol and daily data list
        """
        return self.client.get_stock_daily_chart(
            symbol=symbol,
            base_date=base_date,
            adjusted_price_type="1" if adjusted else "0"
        )
    
    def stock_weekly(
        self,
        symbol: str,
        base_date: str = "",            # YYYYMMDD format, empty for today
        adjusted: bool = True           # True for 수정주가
    ) -> Dict[str, Any]:
        """
        Get stock weekly chart data.
        주식 주봉 차트 데이터
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            base_date: Base date in YYYYMMDD format (empty for today)
            adjusted: True for adjusted prices
            
        Returns:
            Dictionary with weekly chart data including symbol and weekly data list
        """
        return self.client.get_stock_weekly_chart(
            symbol=symbol,
            base_date=base_date,
            adjusted_price_type="1" if adjusted else "0"
        )
    
    def stock_monthly(
        self,
        symbol: str,
        base_date: str = "",            # YYYYMMDD format, empty for today
        adjusted: bool = True           # True for 수정주가
    ) -> Dict[str, Any]:
        """
        Get stock monthly chart data.
        주식 월봉 차트 데이터
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            base_date: Base date in YYYYMMDD format (empty for today)
            adjusted: True for adjusted prices
            
        Returns:
            Dictionary with monthly chart data including symbol and monthly data list
        """
        return self.client.get_stock_monthly_chart(
            symbol=symbol,
            base_date=base_date,
            adjusted_price_type="1" if adjusted else "0"
        )
    
    def stock_yearly(
        self,
        symbol: str,
        base_date: str = "",            # YYYYMMDD format, empty for today
        adjusted: bool = True           # True for 수정주가
    ) -> Dict[str, Any]:
        """
        Get stock yearly chart data.
        주식 년봉 차트 데이터
        
        Args:
            symbol: Stock symbol (e.g., "005930")
            base_date: Base date in YYYYMMDD format (empty for today)
            adjusted: True for adjusted prices
            
        Returns:
            Dictionary with yearly chart data including symbol and yearly data list
        """
        return self.client.get_stock_yearly_chart(
            symbol=symbol,
            base_date=base_date,
            adjusted_price_type="1" if adjusted else "0"
        )
    
    def sector_tick(
        self,
        sector_code: str = "001",       # 업종코드 (001 for KOSPI)
        scope: str = "all"              # "all" for 전체
    ) -> Dict[str, Any]:
        """
        Get sector tick chart data.
        업종 틱 차트 데이터
        
        Args:
            sector_code: Sector code (e.g., "001" for KOSPI)
            scope: "all" for 전체
            
        Returns:
            Dictionary with sector tick chart data
        """
        return self.client.get_sector_tick_chart(
            sector_code=sector_code,
            tick_scope="1" if scope == "all" else "1"
        )
    
    def sector_minute(
        self,
        sector_code: str = "001",       # 업종코드 (001 for KOSPI)
        minutes: int = 1                # 1, 3, 5, 10, 15, 30, 60
    ) -> Dict[str, Any]:
        """
        Get sector minute chart data.
        업종 분봉 차트 데이터
        
        Args:
            sector_code: Sector code (e.g., "001" for KOSPI)
            minutes: Time interval (1, 3, 5, 10, 15, 30, 60)
            
        Returns:
            Dictionary with sector minute chart data
        """
        return self.client.get_sector_minute_chart(
            sector_code=sector_code,
            minute_type=str(minutes)
        )
    
    def sector_daily(
        self,
        sector_code: str = "001",       # 업종코드 (001 for KOSPI)
        base_date: str = ""             # YYYYMMDD format, empty for today
    ) -> Dict[str, Any]:
        """
        Get sector daily chart data.
        업종 일봉 차트 데이터
        
        Args:
            sector_code: Sector code (e.g., "001" for KOSPI)
            base_date: Base date in YYYYMMDD format (empty for today)
            
        Returns:
            Dictionary with sector daily chart data
        """
        return self.client.get_sector_daily_chart(
            sector_code=sector_code,
            base_date=base_date
        )
    
    def sector_weekly(
        self,
        sector_code: str = "001",       # 업종코드 (001 for KOSPI)
        base_date: str = ""             # YYYYMMDD format, empty for today
    ) -> Dict[str, Any]:
        """
        Get sector weekly chart data.
        업종 주봉 차트 데이터
        
        Args:
            sector_code: Sector code (e.g., "001" for KOSPI)
            base_date: Base date in YYYYMMDD format (empty for today)
            
        Returns:
            Dictionary with sector weekly chart data
        """
        return self.client.get_sector_weekly_chart(
            sector_code=sector_code,
            base_date=base_date
        )
    
    def sector_monthly(
        self,
        sector_code: str = "002",       # 업종코드 (002 for example)
        base_date: str = ""             # YYYYMMDD format, empty for today
    ) -> Dict[str, Any]:
        """
        Get sector monthly chart data.
        업종 월봉 차트 데이터
        
        Args:
            sector_code: Sector code (e.g., "002")
            base_date: Base date in YYYYMMDD format (empty for today)
            
        Returns:
            Dictionary with sector monthly chart data
        """
        return self.client.get_sector_monthly_chart(
            sector_code=sector_code,
            base_date=base_date
        )
    
    def sector_yearly(
        self,
        sector_code: str = "001",       # 업종코드 (001 for KOSPI)
        base_date: str = ""             # YYYYMMDD format, empty for today
    ) -> Dict[str, Any]:
        """
        Get sector yearly chart data.
        업종 년봉 차트 데이터
        
        Args:
            sector_code: Sector code (e.g., "001" for KOSPI)
            base_date: Base date in YYYYMMDD format (empty for today)
            
        Returns:
            Dictionary with sector yearly chart data
        """
        return self.client.get_sector_yearly_chart(
            sector_code=sector_code,
            base_date=base_date
        )


class Theme:
    """
    Theme analysis wrapper providing easy access to theme group information and component stocks.
    테마 분석 관련 기능을 제공하는 래퍼 클래스
    """

    def __init__(self, client: KiwoomClient):
        self.client = client

    def get_all_themes(
        self,
        search_type: str = "all",       # "all", "theme", "stock"
        days_back: int = 1,             # 1~99 days
        sort_by: str = "top_period_return",  # "top_period_return", "bottom_period_return", "top_change_rate", "bottom_change_rate"
        exchange: str = "all"           # "krx", "nxt", "all"
    ) -> List[Dict[str, Any]]:
        """
        Get all theme groups with their statistics.
        모든 테마 그룹과 통계 정보를 조회

        Args:
            search_type: Search type ("all", "theme", "stock")
            days_back: Number of days back to analyze (1-99)
            sort_by: Sort criteria
            exchange: Exchange type ("krx", "nxt", "all")

        Returns:
            List of theme groups with statistics

        Example:
            ```python
            # Get top performing themes in the last 5 days
            themes = api.theme.get_all_themes(
                days_back=5,
                sort_by="top_period_return"
            )
            
            for theme in themes:
                print(f"{theme['name']}: {theme['period_return']}%")
            ```
        """
        try:
            # Map user-friendly parameters to API parameters
            qry_tp_map = {
                "all": "0",
                "theme": "1", 
                "stock": "2"
            }
            
            flu_pl_amt_tp_map = {
                "top_period_return": "1",
                "bottom_period_return": "2",
                "top_change_rate": "3",
                "bottom_change_rate": "4"
            }
            
            stex_tp_map = {
                "krx": "1",
                "nxt": "2",
                "all": "3"
            }

            response = self.client.get_theme_groups(
                qry_tp=qry_tp_map.get(search_type, "0"),
                date_tp=str(days_back),
                flu_pl_amt_tp=flu_pl_amt_tp_map.get(sort_by, "1"),
                stex_tp=stex_tp_map.get(exchange, "3")
            )

            themes = []
            for theme_data in response.get("thema_grp", []):
                themes.append({
                    "theme_code": theme_data.get("thema_grp_cd", ""),
                    "name": theme_data.get("thema_grp_nm", ""),
                    "stock_count": int(theme_data.get("stk_cnt", 0)),
                    "rise_count": int(theme_data.get("rise_cnt", 0)),
                    "fall_count": int(theme_data.get("fall_cnt", 0)),
                    "unchanged_count": int(theme_data.get("unchg_cnt", 0)),
                    "period_return": float(theme_data.get("dt_prft_rt", 0)),
                    "change_rate": float(theme_data.get("flu_rt", 0)),
                    "timestamp": datetime.now().isoformat()
                })

            return themes

        except Exception as e:
            logger.error(f"Failed to get theme groups: {e}")
            return []

    def get_theme_stocks(
        self,
        theme_code: str,
        exchange: str = "all",          # "krx", "nxt", "all"
        days_back: int = 1              # 1~99 days (optional)
    ) -> Dict[str, Any]:
        """
        Get stocks in a specific theme group.
        특정 테마 그룹의 구성 종목들을 조회

        Args:
            theme_code: Theme group code (6-digit code)
            exchange: Exchange type ("krx", "nxt", "all")
            days_back: Number of days back for analysis (optional)

        Returns:
            Dictionary containing theme info and component stocks

        Example:
            ```python
            # Get stocks in AI theme (assuming theme code "AI001")
            ai_theme = api.theme.get_theme_stocks("AI001")
            
            print(f"Theme return: {ai_theme['theme_return']}%")
            for stock in ai_theme['stocks']:
                print(f"{stock['name']} ({stock['symbol']}): {stock['change_rate']}%")
            ```
        """
        try:
            stex_tp_map = {
                "krx": "1",
                "nxt": "2", 
                "all": "3"
            }

            response = self.client.get_theme_component_stocks(
                thema_grp_cd=theme_code,
                stex_tp=stex_tp_map.get(exchange, "3"),
                date_tp=str(days_back) if days_back > 0 else ""
            )

            stocks = []
            for stock_data in response.get("thema_comp_stk", []):
                stocks.append({
                    "symbol": stock_data.get("stk_cd", ""),
                    "name": stock_data.get("stk_nm", ""),
                    "current_price": int(stock_data.get("cur_prc", 0)),
                    "change_amount": int(stock_data.get("pred_pre", 0)),
                    "change_rate": float(stock_data.get("flu_rt", 0)),
                    "volume": int(stock_data.get("trde_qty", 0)),
                    "trading_value": int(stock_data.get("trde_prica", 0)),
                    "market_cap": int(stock_data.get("stk_cap", 0)),
                    "timestamp": datetime.now().isoformat()
                })

            return {
                "theme_code": theme_code,
                "theme_return": float(response.get("flu_rt", 0)),
                "period_return": float(response.get("dt_prft_rt", 0)),
                "stock_count": len(stocks),
                "stocks": stocks,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get theme component stocks for {theme_code}: {e}")
            return {
                "theme_code": theme_code,
                "error": str(e),
                "stocks": [],
                "timestamp": datetime.now().isoformat()
            }

    def search_themes(
        self,
        query: str,
        search_type: str = "theme",     # "theme" or "stock"
        days_back: int = 5,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for themes by name or find themes containing a specific stock.
        테마 이름으로 검색하거나 특정 종목이 포함된 테마를 찾기

        Args:
            query: Search query (theme name or stock symbol)
            search_type: "theme" to search by theme name, "stock" to find themes containing stock
            days_back: Number of days back for performance data
            limit: Maximum number of results

        Returns:
            List of matching themes

        Example:
            ```python
            # Search for AI-related themes
            ai_themes = api.theme.search_themes("AI", search_type="theme")
            
            # Find themes containing Samsung Electronics
            samsung_themes = api.theme.search_themes("005930", search_type="stock")
            ```
        """
        try:
            if search_type == "theme":
                # Search by theme name
                themes = self.get_all_themes(
                    search_type="theme",
                    days_back=days_back
                )
                # Filter by query in theme name
                matching_themes = [
                    theme for theme in themes
                    if query.lower() in theme["name"].lower()
                ][:limit]
                
            else:  # search_type == "stock"
                # Search for themes containing the stock
                themes = self.get_all_themes(
                    search_type="stock",
                    days_back=days_back
                )
                matching_themes = []
                
                # Check each theme for the stock
                for theme in themes:
                    theme_stocks = self.get_theme_stocks(theme["theme_code"])
                    if any(stock["symbol"] == query for stock in theme_stocks["stocks"]):
                        matching_themes.append(theme)
                        if len(matching_themes) >= limit:
                            break

            return matching_themes

        except Exception as e:
            logger.error(f"Failed to search themes for '{query}': {e}")
            return []

    def get_top_performing_themes(
        self,
        days_back: int = 5,
        limit: int = 10,
        sort_by: str = "period_return"   # "period_return" or "change_rate"
    ) -> List[Dict[str, Any]]:
        """
        Get top performing themes.
        상위 수익률 테마 조회

        Args:
            days_back: Number of days back for analysis
            limit: Number of top themes to return
            sort_by: Sort criteria ("period_return" or "change_rate")

        Returns:
            List of top performing themes

        Example:
            ```python
            # Get top 5 performing themes in the last week
            top_themes = api.theme.get_top_performing_themes(
                days_back=7,
                limit=5
            )
            
            for i, theme in enumerate(top_themes, 1):
                print(f"{i}. {theme['name']}: +{theme['period_return']:.2f}%")
            ```
        """
        try:
            sort_type = "top_period_return" if sort_by == "period_return" else "top_change_rate"
            
            themes = self.get_all_themes(
                days_back=days_back,
                sort_by=sort_type
            )
            
            # Sort by the requested metric and return top N
            if sort_by == "period_return":
                themes.sort(key=lambda x: x["period_return"], reverse=True)
            else:
                themes.sort(key=lambda x: x["change_rate"], reverse=True)
                
            return themes[:limit]

        except Exception as e:
            logger.error(f"Failed to get top performing themes: {e}")
            return []
