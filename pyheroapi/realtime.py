"""
Real-time market data client for Kiwoom Securities WebSocket API.

This module provides WebSocket-based real-time market data streaming
including stock prices, order book, trades, and account updates.
"""

import asyncio
import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

try:
    import websockets
except ImportError:
    raise ImportError("websockets library is required for real-time data. Install with: pip install websockets")

from .exceptions import KiwoomAPIError, KiwoomAuthError


@dataclass
class ConditionalSearchItem:
    """Conditional search item data."""
    seq: str
    name: str
    
    @classmethod
    def from_response_data(cls, data: List) -> "ConditionalSearchItem":
        """Create from response data array."""
        return cls(seq=data[0], name=data[1])


@dataclass 
class ConditionalSearchResult:
    """Conditional search result data."""
    symbol: str
    name: str
    current_price: str
    change_sign: str
    change: str
    change_rate: str
    volume: str
    open_price: str
    high_price: str
    low_price: str
    
    @classmethod
    def from_response_data(cls, data: Dict[str, str]) -> "ConditionalSearchResult":
        """Create from response data dictionary."""
        return cls(
            symbol=data.get("9001", ""),
            name=data.get("302", ""),
            current_price=data.get("10", ""),
            change_sign=data.get("25", ""),
            change=data.get("11", ""),
            change_rate=data.get("12", ""),
            volume=data.get("13", ""),
            open_price=data.get("16", ""),
            high_price=data.get("17", ""),
            low_price=data.get("18", "")
        )


@dataclass
class ConditionalSearchRealtimeData:
    """Conditional search real-time data."""
    seq: str
    symbol: str
    action: str  # I: 삽입, D: 삭제
    time: str
    trade_type: str
    
    @classmethod
    def from_response_data(cls, data: Dict[str, str]) -> "ConditionalSearchRealtimeData":
        """Create from response data dictionary."""
        return cls(
            seq=data.get("841", ""),
            symbol=data.get("9001", ""),
            action=data.get("843", ""),
            time=data.get("20", ""),
            trade_type=data.get("907", "")
        )


class RealtimeDataType(Enum):
    """Real-time data types (TR codes)."""
    ORDER_EXECUTION = "00"  # 주문체결
    ACCOUNT_BALANCE = "04"  # 잔고
    STOCK_PRICE = "0A"      # 주식기세
    STOCK_TRADE = "0B"      # 주식체결
    BEST_QUOTE = "0C"       # 주식우선호가
    ORDER_BOOK = "0D"       # 주식호가잔량
    AFTER_HOURS = "0E"      # 주식시간외호가
    DAILY_TRADER = "0F"     # 주식당일거래원
    ETF_NAV = "0G"          # ETF NAV
    PRE_MARKET = "0H"       # 주식예상체결
    SECTOR_INDEX = "0J"     # 업종지수
    SECTOR_CHANGE = "0U"    # 업종등락
    STOCK_INFO = "0g"       # 주식종목정보
    ELW_THEORY = "0m"       # ELW 이론가
    MARKET_TIME = "0s"      # 장시작시간
    ELW_INDICATOR = "0u"    # ELW 지표
    PROGRAM_TRADING = "0w"  # 종목프로그램매매
    VI_TRIGGER = "1h"       # VI발동/해제


@dataclass
class RealtimeSubscription:
    """Real-time data subscription configuration."""
    symbols: List[str] = field(default_factory=list)
    data_types: List[RealtimeDataType] = field(default_factory=list)
    group_no: str = "1"
    refresh: str = "1"  # 1: keep existing, 0: remove existing
    
    def to_request(self, action: str = "REG") -> Dict[str, Any]:
        """Convert to WebSocket request format."""
        return {
            "trnm": action,  # REG or REMOVE
            "grp_no": self.group_no,
            "refresh": self.refresh,
            "data": [{
                "item": self.symbols,
                "type": [dt.value for dt in self.data_types]
            }]
        }


@dataclass
class RealtimeData:
    """Real-time market data container."""
    data_type: str
    name: str
    symbol: str
    values: Dict[str, str]
    timestamp: Optional[str] = None
    
    @classmethod
    def from_response(cls, response_data: Dict[str, Any]) -> List["RealtimeData"]:
        """Parse WebSocket response into RealtimeData objects."""
        result = []
        for item in response_data.get("data", []):
            result.append(cls(
                data_type=item.get("type", ""),
                name=item.get("name", ""),
                symbol=item.get("item", ""),
                values=item.get("values", {}),
                timestamp=item.get("values", {}).get("20")  # 체결시간 field
            ))
        return result


class KiwoomRealtimeClient:
    """
    WebSocket client for Kiwoom Securities real-time market data and conditional search.
    
    Provides asynchronous streaming of real-time market data including:
    - Stock prices and trades
    - Order book updates
    - Account balance changes
    - Order execution updates
    - Conditional search functionality
    """
    
    PRODUCTION_WS_URL = "wss://api.kiwoom.com:10000/api/dostk/websocket"
    SANDBOX_WS_URL = "wss://mockapi.kiwoom.com:10000/api/dostk/websocket"
    
    def __init__(
        self,
        access_token: str,
        is_production: bool = True,
        auto_reconnect: bool = True,
        max_reconnect_attempts: int = 5,
        reconnect_delay: int = 5
    ):
        """
        Initialize the real-time client.
        
        Args:
            access_token: Kiwoom API access token
            is_production: Whether to use production (default) or sandbox environment
            auto_reconnect: Whether to automatically reconnect on connection loss
            max_reconnect_attempts: Maximum number of reconnection attempts
            reconnect_delay: Delay between reconnection attempts (seconds)
        """
        self.access_token = access_token
        self.ws_url = self.PRODUCTION_WS_URL if is_production else self.SANDBOX_WS_URL
        self.auto_reconnect = auto_reconnect
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.keep_running = True
        self.subscriptions: Dict[str, RealtimeSubscription] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.reconnect_count = 0
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def connect(self) -> None:
        """Establish WebSocket connection and perform login."""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.logger.info("WebSocket connection established, attempting login...")
            
            # Start message handling loop
            asyncio.create_task(self._message_handler())
            
            # Send LOGIN message as required by Kiwoom API
            login_message = {
                'trnm': 'LOGIN',
                'token': self.access_token
            }
            
            await self.websocket.send(json.dumps(login_message))
            self.logger.info("LOGIN message sent to WebSocket server")
            
            # Wait for login response
            login_timeout = 5  # 5 second timeout for login
            for _ in range(login_timeout * 10):  # Check every 100ms
                if self.is_connected:
                    break
                await asyncio.sleep(0.1)
            else:
                raise KiwoomAuthError("LOGIN timeout - no response from server")
            
            self.reconnect_count = 0
            self.logger.info("WebSocket connection and login successful")
            
        except Exception as e:
            self.is_connected = False
            self.logger.error(f"Failed to connect to WebSocket: {e}")
            raise KiwoomAuthError(f"WebSocket connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        self.keep_running = False
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.logger.info("WebSocket connection closed")
    
    async def _message_handler(self) -> None:
        """Handle incoming WebSocket messages."""
        try:
            while self.keep_running and self.websocket and not self.websocket.closed:
                try:
                    # Receive message with timeout
                    message = await asyncio.wait_for(
                        self.websocket.recv(), 
                        timeout=60  # 60 second timeout
                    )
                    
                    data = json.loads(message)
                    await self._process_message(data)
                    
                except asyncio.TimeoutError:
                    self.logger.warning("WebSocket receive timeout - connection may be dead")
                    break
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse message: {e}")
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed as e:
            self.logger.warning(f"WebSocket connection closed: {e}")
            self.is_connected = False
            
            if self.auto_reconnect and self.reconnect_count < self.max_reconnect_attempts:
                await self._reconnect()
        except Exception as e:
            self.logger.error(f"Message handler error: {e}")
            self.is_connected = False
    
    async def _reconnect(self) -> None:
        """Attempt to reconnect to WebSocket."""
        self.reconnect_count += 1
        self.logger.info(f"Attempting to reconnect ({self.reconnect_count}/{self.max_reconnect_attempts})")
        
        await asyncio.sleep(self.reconnect_delay)
        
        try:
            await self.connect()
            # Re-subscribe to all previous subscriptions
            for subscription in self.subscriptions.values():
                await self._send_subscription(subscription, "REG")
                
        except Exception as e:
            self.logger.error(f"Reconnection attempt {self.reconnect_count} failed: {e}")
            if self.reconnect_count < self.max_reconnect_attempts:
                await self._reconnect()
    
    async def _process_message(self, data: Dict[str, Any]) -> None:
        """Process incoming message and trigger callbacks."""
        trnm = data.get("trnm")
        
        if trnm == "LOGIN":
            # Handle LOGIN response
            return_code = data.get("return_code", 1)
            return_msg = data.get("return_msg", "")
            
            if return_code == 0:
                self.is_connected = True
                self.logger.info("LOGIN successful")
            else:
                self.is_connected = False
                self.logger.error(f"LOGIN failed: {return_msg}")
                raise KiwoomAuthError(f"LOGIN failed: {return_msg}")
                
        elif trnm == "PING":
            # Handle PING - echo back the same message (keep-alive)
            await self.websocket.send(json.dumps(data))
            self.logger.debug("PING response sent")
            
        elif trnm == "REAL":
            # Real-time data update
            realtime_data_list = RealtimeData.from_response(data)
            for realtime_data in realtime_data_list:
                # Handle conditional search real-time data
                if realtime_data.data_type == "02":  # 조건검색 real-time
                    conditional_data = ConditionalSearchRealtimeData.from_response_data(realtime_data.values)
                    await self._trigger_callbacks("conditional_search_realtime", conditional_data)
                else:
                    await self._trigger_callbacks(realtime_data.data_type, realtime_data)
                
        elif trnm in ["REG", "REMOVE"]:
            # Subscription response
            return_code = data.get("return_code", 1)
            return_msg = data.get("return_msg", "")
            
            if return_code == 0:
                self.logger.info(f"Subscription {trnm} successful")
            else:
                self.logger.error(f"Subscription {trnm} failed: {return_msg}")
                raise KiwoomAPIError(f"Subscription failed: {return_msg}")
                
        elif trnm == "CNSRLST":
            # Conditional search list response
            await self._trigger_callbacks("conditional_search_list", data)
            
        elif trnm == "CNSRREQ":
            # Conditional search results response
            await self._trigger_callbacks("conditional_search_results", data)
            
        elif trnm == "CNSRCLR":
            # Conditional search clear response
            await self._trigger_callbacks("conditional_search_clear", data)
    
    async def _trigger_callbacks(self, data_type: str, data: Any) -> None:
        """Trigger registered callbacks for the data type."""
        callbacks = self.callbacks.get(data_type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
    
    async def _send_subscription(self, subscription: RealtimeSubscription, action: str) -> None:
        """Send subscription request to WebSocket."""
        if not self.is_connected or not self.websocket:
            raise KiwoomAPIError("WebSocket not connected")
        
        request = subscription.to_request(action)
        await self.websocket.send(json.dumps(request))
    
    def add_callback(self, data_type: Union[str, RealtimeDataType], callback: Callable) -> None:
        """
        Add callback function for specific data type.
        
        Args:
            data_type: Real-time data type to listen for
            callback: Function to call when data is received
        """
        if isinstance(data_type, RealtimeDataType):
            data_type = data_type.value
            
        if data_type not in self.callbacks:
            self.callbacks[data_type] = []
        self.callbacks[data_type].append(callback)
    
    def remove_callback(self, data_type: Union[str, RealtimeDataType], callback: Callable) -> None:
        """Remove callback function for specific data type."""
        if isinstance(data_type, RealtimeDataType):
            data_type = data_type.value
            
        if data_type in self.callbacks:
            try:
                self.callbacks[data_type].remove(callback)
            except ValueError:
                pass
    
    async def subscribe_stock_price(self, symbols: Union[str, List[str]]) -> None:
        """
        Subscribe to real-time stock price updates.
        
        Args:
            symbols: Stock symbol(s) to subscribe to
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        subscription = RealtimeSubscription(
            symbols=symbols,
            data_types=[RealtimeDataType.STOCK_TRADE, RealtimeDataType.STOCK_PRICE]
        )
        
        await self._send_subscription(subscription, "REG")
        self.subscriptions[f"price_{'-'.join(symbols)}"] = subscription
    
    async def subscribe_order_book(self, symbols: Union[str, List[str]]) -> None:
        """
        Subscribe to real-time order book updates.
        
        Args:
            symbols: Stock symbol(s) to subscribe to
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        subscription = RealtimeSubscription(
            symbols=symbols,
            data_types=[RealtimeDataType.ORDER_BOOK, RealtimeDataType.BEST_QUOTE]
        )
        
        await self._send_subscription(subscription, "REG")
        self.subscriptions[f"orderbook_{'-'.join(symbols)}"] = subscription
    
    async def subscribe_account_updates(self) -> None:
        """Subscribe to account balance and order execution updates."""
        subscription = RealtimeSubscription(
            symbols=[""],  # Empty for account-wide updates
            data_types=[RealtimeDataType.ORDER_EXECUTION, RealtimeDataType.ACCOUNT_BALANCE]
        )
        
        await self._send_subscription(subscription, "REG")
        self.subscriptions["account"] = subscription
    
    async def subscribe_sector_index(self, sector_codes: Union[str, List[str]]) -> None:
        """
        Subscribe to sector index updates.
        
        Args:
            sector_codes: Sector code(s) to subscribe to (e.g., "001" for KOSPI)
        """
        if isinstance(sector_codes, str):
            sector_codes = [sector_codes]
        
        subscription = RealtimeSubscription(
            symbols=sector_codes,
            data_types=[RealtimeDataType.SECTOR_INDEX, RealtimeDataType.SECTOR_CHANGE]
        )
        
        await self._send_subscription(subscription, "REG")
        self.subscriptions[f"sector_{'-'.join(sector_codes)}"] = subscription
    
    async def subscribe_etf_nav(self, etf_symbols: Union[str, List[str]]) -> None:
        """
        Subscribe to ETF NAV updates.
        
        Args:
            etf_symbols: ETF symbol(s) to subscribe to
        """
        if isinstance(etf_symbols, str):
            etf_symbols = [etf_symbols]
        
        subscription = RealtimeSubscription(
            symbols=etf_symbols,
            data_types=[RealtimeDataType.ETF_NAV]
        )
        
        await self._send_subscription(subscription, "REG")
        self.subscriptions[f"etf_{'-'.join(etf_symbols)}"] = subscription
    
    async def subscribe_elw_data(self, elw_symbols: Union[str, List[str]]) -> None:
        """
        Subscribe to ELW theory price and indicators.
        
        Args:
            elw_symbols: ELW symbol(s) to subscribe to
        """
        if isinstance(elw_symbols, str):
            elw_symbols = [elw_symbols]
        
        subscription = RealtimeSubscription(
            symbols=elw_symbols,
            data_types=[RealtimeDataType.ELW_THEORY, RealtimeDataType.ELW_INDICATOR]
        )
        
        await self._send_subscription(subscription, "REG")
        self.subscriptions[f"elw_{'-'.join(elw_symbols)}"] = subscription

    # Conditional Search Methods
    
    async def _send_conditional_search_request(self, request: Dict[str, Any]) -> None:
        """Send conditional search request to WebSocket."""
        if not self.is_connected or not self.websocket:
            raise KiwoomAPIError("WebSocket not connected")
        
        await self.websocket.send(json.dumps(request))
    
    async def get_conditional_search_list(self) -> None:
        """
        Get list of conditional search conditions.
        
        Results will be delivered to callbacks registered for 'conditional_search_list'.
        """
        request = {
            "trnm": "CNSRLST"
        }
        await self._send_conditional_search_request(request)
    
    async def execute_conditional_search(
        self, 
        seq: str, 
        search_type: str = "0", 
        exchange: str = "K",
        cont_yn: str = "N",
        next_key: str = ""
    ) -> None:
        """
        Execute conditional search.
        
        Args:
            seq: Conditional search sequence number (must exist in conditional search list)
            search_type: Search type options:
                        - "0": Regular conditional search (ka10172) - returns snapshot results
                        - "1": Real-time conditional search (ka10173) - returns results + real-time updates
            exchange: Exchange type (K: KRX, D: KOSDAQ)
            cont_yn: Continuation flag (Y: continue, N: new search)
            next_key: Continuation key for paging (used when cont_yn="Y")
            
        Results will be delivered to callbacks registered for 'conditional_search_results'.
        For search_type="1", real-time updates will also be sent to 'conditional_search_realtime'.
        
        Note: The conditional search sequence (seq) must be previously created and exist
              in your account. Use get_conditional_search_list() to see available sequences.
              
        Error responses:
        - return_code 900004: "존재하지 않는 일련번호입니다.(seq=X)" - Sequence doesn't exist
        """
        request = {
            "trnm": "CNSRREQ",
            "seq": seq,
            "search_type": search_type,
            "stex_tp": exchange,
            "cont_yn": cont_yn,
            "next_key": next_key
        }
        await self._send_conditional_search_request(request)
    
    async def execute_conditional_search_realtime(
        self, 
        seq: str, 
        exchange: str = "K"
    ) -> None:
        """
        Execute conditional search with real-time updates.
        
        Args:
            seq: Conditional search sequence number
            exchange: Exchange type (K: KRX)
            
        Results will be delivered to callbacks registered for 'conditional_search_results'
        and real-time updates to 'conditional_search_realtime'.
        """
        request = {
            "trnm": "CNSRREQ",
            "seq": seq,
            "search_type": "1",  # 1: conditional search + real-time
            "stex_tp": exchange
        }
        await self._send_conditional_search_request(request)
    
    async def cancel_conditional_search_realtime(self, seq: str) -> None:
        """
        Cancel real-time conditional search.
        
        Args:
            seq: Conditional search sequence number to cancel
            
        Results will be delivered to callbacks registered for 'conditional_search_clear'.
        """
        request = {
            "trnm": "CNSRCLR",
            "seq": seq
        }
        await self._send_conditional_search_request(request)
    
    async def unsubscribe(self, subscription_key: str) -> None:
        """
        Unsubscribe from specific real-time data.
        
        Args:
            subscription_key: Key of the subscription to remove
        """
        if subscription_key in self.subscriptions:
            subscription = self.subscriptions[subscription_key]
            await self._send_subscription(subscription, "REMOVE")
            del self.subscriptions[subscription_key]
    
    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all real-time data."""
        for key in list(self.subscriptions.keys()):
            await self.unsubscribe(key)
    
    def get_active_subscriptions(self) -> Dict[str, RealtimeSubscription]:
        """Get all active subscriptions."""
        return self.subscriptions.copy()


# Convenience context manager
class RealtimeContext:
    """Context manager for real-time data client."""
    
    def __init__(self, client: KiwoomRealtimeClient):
        self.client = client
    
    async def __aenter__(self):
        await self.client.connect()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()


def create_realtime_client(
    access_token: str, 
    is_production: bool = True, 
    **kwargs
) -> KiwoomRealtimeClient:
    """
    Create a real-time client instance.
    
    Args:
        access_token: Kiwoom API access token
        is_production: Whether to use production (default) or sandbox environment
        **kwargs: Additional arguments for KiwoomRealtimeClient constructor
        
    Returns:
        Configured KiwoomRealtimeClient instance
    """
    return KiwoomRealtimeClient(
        access_token=access_token,
        is_production=is_production,
        **kwargs
    )


def create_realtime_client_with_credentials(
    appkey: str,
    secretkey: str,
    is_production: bool = True,
    **kwargs
) -> KiwoomRealtimeClient:
    """
    Create a real-time client instance by automatically obtaining an access token.
    
    Args:
        appkey: App key from Kiwoom Securities
        secretkey: Secret key from Kiwoom Securities
        is_production: Whether to use production (default) or sandbox environment
        **kwargs: Additional arguments for KiwoomRealtimeClient constructor
        
    Returns:
        Configured KiwoomRealtimeClient instance
    """
    # For sandbox mode, check if mock environment variables are set
    if not is_production:
        mock_appkey = os.getenv("MOCK_KIWOOM_APPKEY")
        mock_secretkey = os.getenv("MOCK_KIWOOM_SECRETKEY")
        
        if mock_appkey and mock_secretkey:
            appkey = mock_appkey
            secretkey = mock_secretkey
    
    # Import here to avoid circular imports
    from .client import KiwoomClient
    
    # Get access token
    token_response = KiwoomClient.issue_token(appkey, secretkey, is_production)
    
    # Create realtime client
    return KiwoomRealtimeClient(
        access_token=token_response.token,
        is_production=is_production,
        **kwargs
    ) 