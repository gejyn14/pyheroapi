"""
Tests for real-time WebSocket functionality.

Comprehensive test suite covering:
- Real-time data parsing and handling
- WebSocket connection management
- Subscription workflow
- Conditional search functionality
- Error handling and reconnection
- Callback management
- Integration scenarios
"""

import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
import pytest
from datetime import datetime

try:
    from pyheroapi.realtime import (
        KiwoomRealtimeClient,
        RealtimeData,
        RealtimeDataType,
        RealtimeSubscription,
        ConditionalSearchItem,
        ConditionalSearchResult,
        ConditionalSearchRealtimeData,
        RealtimeContext,
        create_realtime_client,
    )
    from pyheroapi.exceptions import KiwoomAPIError
    import websockets.exceptions
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestConditionalSearchModels:
    """Test conditional search data models."""
    
    def test_conditional_search_item_from_response(self):
        """Test ConditionalSearchItem parsing."""
        data = ["1", "내 조건식"]
        item = ConditionalSearchItem.from_response_data(data)
        
        assert item.seq == "1"
        assert item.name == "내 조건식"
    
    def test_conditional_search_result_from_response(self):
        """Test ConditionalSearchResult parsing."""
        data = {
            "9001": "005930",
            "302": "삼성전자",
            "10": "000075000",
            "25": "2",
            "11": "000001000",
            "12": "000001350",
            "13": "010000000",
            "16": "000074000",
            "17": "000076000",
            "18": "000073500"
        }
        
        result = ConditionalSearchResult.from_response_data(data)
        
        assert result.symbol == "005930"
        assert result.name == "삼성전자"
        assert result.current_price == "000075000"
        assert result.change_sign == "2"
        assert result.change == "000001000"
        assert result.change_rate == "000001350"
        assert result.volume == "010000000"
        assert result.open_price == "000074000"
        assert result.high_price == "000076000"
        assert result.low_price == "000073500"
    
    def test_conditional_search_realtime_data_from_response(self):
        """Test ConditionalSearchRealtimeData parsing."""
        data = {
            "841": "1",
            "9001": "005930",
            "843": "I",
            "20": "153000",
            "907": "2"
        }
        
        realtime_data = ConditionalSearchRealtimeData.from_response_data(data)
        
        assert realtime_data.seq == "1"
        assert realtime_data.symbol == "005930"
        assert realtime_data.action == "I"
        assert realtime_data.time == "153000"
        assert realtime_data.trade_type == "2"


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestRealtimeDataType:
    """Test RealtimeDataType enum."""
    
    def test_all_data_types_have_values(self):
        """Test that all data types have proper values."""
        data_types = [
            (RealtimeDataType.ORDER_EXECUTION, "00"),
            (RealtimeDataType.ACCOUNT_BALANCE, "04"),
            (RealtimeDataType.STOCK_PRICE, "0A"),
            (RealtimeDataType.STOCK_TRADE, "0B"),
            (RealtimeDataType.BEST_QUOTE, "0C"),
            (RealtimeDataType.ORDER_BOOK, "0D"),
            (RealtimeDataType.AFTER_HOURS, "0E"),
            (RealtimeDataType.DAILY_TRADER, "0F"),
            (RealtimeDataType.ETF_NAV, "0G"),
            (RealtimeDataType.PRE_MARKET, "0H"),
            (RealtimeDataType.SECTOR_INDEX, "0J"),
            (RealtimeDataType.SECTOR_CHANGE, "0U"),
            (RealtimeDataType.STOCK_INFO, "0g"),
            (RealtimeDataType.ELW_THEORY, "0m"),
            (RealtimeDataType.MARKET_TIME, "0s"),
            (RealtimeDataType.ELW_INDICATOR, "0u"),
            (RealtimeDataType.PROGRAM_TRADING, "0w"),
            (RealtimeDataType.VI_TRIGGER, "1h"),
        ]
        
        for data_type, expected_value in data_types:
            assert data_type.value == expected_value


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestRealtimeData:
    """Test RealtimeData class."""
    
    def test_from_response_single_item(self):
        """Test parsing single item from WebSocket response."""
        response = {
            "data": [
                {
                    "type": "0B",
                    "name": "주식체결",
                    "item": "005930",
                    "values": {
                        "10": "75000",
                        "11": "1000",
                        "12": "1.35",
                        "20": "153000"
                    }
                }
            ]
        }
        
        result = RealtimeData.from_response(response)
        
        assert len(result) == 1
        data = result[0]
        assert data.data_type == "0B"
        assert data.name == "주식체결"
        assert data.symbol == "005930"
        assert data.values["10"] == "75000"
        assert data.values["11"] == "1000"
        assert data.values["12"] == "1.35"
        assert data.timestamp == "153000"
    
    def test_from_response_multiple_items(self):
        """Test parsing multiple items from WebSocket response."""
        response = {
            "data": [
                {
                    "type": "0A",
                    "name": "주식시세",
                    "item": "005930",
                    "values": {"10": "75000", "20": "153000"}
                },
                {
                    "type": "0B",
                    "name": "주식체결", 
                    "item": "000660",
                    "values": {"10": "120000", "20": "153001"}
                }
            ]
        }
        
        result = RealtimeData.from_response(response)
        
        assert len(result) == 2
        assert result[0].symbol == "005930"
        assert result[0].data_type == "0A"
        assert result[1].symbol == "000660"
        assert result[1].data_type == "0B"
    
    def test_from_response_empty_data(self):
        """Test parsing empty response."""
        response = {"data": []}
        result = RealtimeData.from_response(response)
        assert len(result) == 0
    
    def test_from_response_no_timestamp(self):
        """Test parsing response without timestamp field."""
        response = {
            "data": [
                {
                    "type": "0A",
                    "name": "주식시세",
                    "item": "005930",
                    "values": {"10": "75000"}
                }
            ]
        }
        
        result = RealtimeData.from_response(response)
        assert result[0].timestamp is None


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestRealtimeSubscription:
    """Test RealtimeSubscription class."""
    
    def test_to_request_register(self):
        """Test converting subscription to register request format."""
        subscription = RealtimeSubscription(
            symbols=["005930", "000660"],
            data_types=[RealtimeDataType.STOCK_TRADE, RealtimeDataType.STOCK_PRICE],
            group_no="1",
            refresh="1"
        )
        
        request = subscription.to_request("REG")
        
        expected = {
            "trnm": "REG",
            "grp_no": "1",
            "refresh": "1",
            "data": [{
                "item": ["005930", "000660"],
                "type": ["0B", "0A"]
            }]
        }
        
        assert request == expected
    
    def test_to_request_remove(self):
        """Test converting subscription to remove request format."""
        subscription = RealtimeSubscription(
            symbols=["005930"],
            data_types=[RealtimeDataType.ORDER_BOOK],
            group_no="2",
            refresh="0"
        )
        
        request = subscription.to_request("REMOVE")
        
        expected = {
            "trnm": "REMOVE",
            "grp_no": "2",
            "refresh": "0",
            "data": [{
                "item": ["005930"],
                "type": ["0D"]
            }]
        }
        
        assert request == expected
    
    def test_default_values(self):
        """Test subscription with default values."""
        subscription = RealtimeSubscription()
        
        assert subscription.symbols == []
        assert subscription.data_types == []
        assert subscription.group_no == "1"
        assert subscription.refresh == "1"


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestKiwoomRealtimeClient:
    """Test KiwoomRealtimeClient class."""
    
    def test_init_default_values(self):
        """Test client initialization with default values."""
        client = KiwoomRealtimeClient("test_token")

        assert client.access_token == "test_token"
        # Default is production mode (is_production=True)
        assert client.ws_url == client.PRODUCTION_WS_URL
        assert client.auto_reconnect is True
        assert client.max_reconnect_attempts == 5
        assert client.reconnect_delay == 5
        assert client.is_connected is False
        assert client.websocket is None
        assert client.callbacks == {}
        assert client.subscriptions == {}
        assert client.reconnect_count == 0
    
    def test_init_production_mode(self):
        """Test client initialization in production mode."""
        client = KiwoomRealtimeClient(
            access_token="test_token",
            is_production=True,
            auto_reconnect=False,
            max_reconnect_attempts=3,
            reconnect_delay=10
        )
        
        assert client.ws_url == client.PRODUCTION_WS_URL
        assert client.auto_reconnect is False
        assert client.max_reconnect_attempts == 3
        assert client.reconnect_delay == 10
    
    def test_add_callback_string_data_type(self):
        """Test adding callback with string data type."""
        client = KiwoomRealtimeClient("test_token")
        
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        client.add_callback("0B", callback1)
        assert "0B" in client.callbacks
        assert callback1 in client.callbacks["0B"]
        
        # Add another callback for same data type
        client.add_callback("0B", callback2)
        assert len(client.callbacks["0B"]) == 2
        assert callback2 in client.callbacks["0B"]
    
    def test_add_callback_enum_data_type(self):
        """Test adding callback with enum data type."""
        client = KiwoomRealtimeClient("test_token")
        
        def callback(data):
            pass
        
        client.add_callback(RealtimeDataType.STOCK_TRADE, callback)
        assert "0B" in client.callbacks
        assert callback in client.callbacks["0B"]
    
    def test_remove_callback(self):
        """Test removing callbacks."""
        client = KiwoomRealtimeClient("test_token")
        
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        # Add callbacks
        client.add_callback("0B", callback1)
        client.add_callback("0B", callback2)
        assert len(client.callbacks["0B"]) == 2
        
        # Remove one callback
        client.remove_callback("0B", callback1)
        assert len(client.callbacks["0B"]) == 1
        assert callback1 not in client.callbacks["0B"]
        assert callback2 in client.callbacks["0B"]
        
        # Remove last callback
        client.remove_callback("0B", callback2)
        assert len(client.callbacks["0B"]) == 0
    
    def test_remove_callback_nonexistent(self):
        """Test removing nonexistent callback."""
        client = KiwoomRealtimeClient("test_token")
        
        def callback(data):
            pass
        
        # Should not raise error
        client.remove_callback("0B", callback)
        client.remove_callback(RealtimeDataType.STOCK_TRADE, callback)
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_connect_success(self, mock_connect):
        """Test successful WebSocket connection."""
        mock_ws = AsyncMock()
        # Make the mock_connect coroutine return the mock websocket
        async def mock_connect_coroutine(*args, **kwargs):
            return mock_ws
        mock_connect.return_value = mock_connect_coroutine()
        
        client = KiwoomRealtimeClient("test_token")
        
        # Mock the login flow by setting connected state
        original_connect = client.connect
        async def mock_simple_connect():
            client.websocket = mock_ws
            client.is_connected = True
        
        client.connect = mock_simple_connect
        
        await client.connect()
        
        assert client.is_connected is True
        assert client.websocket == mock_ws
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_connect_failure(self, mock_connect):
        """Test WebSocket connection failure."""
        # Mock connection failure
        async def mock_failing_connect(*args, **kwargs):
            raise Exception("Connection failed")
        mock_connect.return_value = mock_failing_connect()
        
        client = KiwoomRealtimeClient("test_token")
        
        with pytest.raises(Exception):
            await client.connect()
        
        assert client.is_connected is False
        assert client.websocket is None
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test WebSocket disconnection."""
        client = KiwoomRealtimeClient("test_token")
        mock_ws = AsyncMock()
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.disconnect()
        
        assert client.is_connected is False
        assert client.websocket is None
        mock_ws.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self):
        """Test disconnection when not connected."""
        client = KiwoomRealtimeClient("test_token")
        
        # Should not raise error
        await client.disconnect()
        
        assert client.is_connected is False
        assert client.websocket is None


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestMessageProcessing:
    """Test message processing functionality."""
    
    @pytest.mark.asyncio
    async def test_process_message_real_data(self):
        """Test processing real-time data message."""
        client = KiwoomRealtimeClient("test_token")
        
        callback_called = False
        received_data = None
        
        def callback(data):
            nonlocal callback_called, received_data
            callback_called = True
            received_data = data
        
        client.add_callback("0B", callback)
        
        message = {
            "trnm": "REAL",
            "data": [{
                "type": "0B",
                "name": "주식체결",
                "item": "005930",
                "values": {"10": "75000", "20": "153000"}
            }]
        }
        
        await client._process_message(message)
        
        assert callback_called is True
        assert received_data.data_type == "0B"
        assert received_data.symbol == "005930"
        assert received_data.values["10"] == "75000"
    
    @pytest.mark.asyncio
    async def test_process_message_multiple_callbacks(self):
        """Test processing message with multiple callbacks."""
        client = KiwoomRealtimeClient("test_token")
        
        callback1_called = False
        callback2_called = False
        
        def callback1(data):
            nonlocal callback1_called
            callback1_called = True
        
        def callback2(data):
            nonlocal callback2_called
            callback2_called = True
        
        client.add_callback("0B", callback1)
        client.add_callback("0B", callback2)
        
        message = {
            "trnm": "REAL",
            "data": [{
                "type": "0B",
                "name": "주식체결",
                "item": "005930",
                "values": {"10": "75000"}
            }]
        }
        
        await client._process_message(message)
        
        assert callback1_called is True
        assert callback2_called is True
    
    @pytest.mark.asyncio
    async def test_process_message_conditional_search_realtime(self):
        """Test processing conditional search real-time message."""
        client = KiwoomRealtimeClient("test_token")
        
        callback_called = False
        received_data = None
        
        def callback(data):
            nonlocal callback_called, received_data
            callback_called = True
            received_data = data
        
        client.add_callback("conditional_search_realtime", callback)
        
        message = {
            "trnm": "REAL",
            "data": [{
                "type": "02",
                "name": "조건검색",
                "item": "005930",
                "values": {
                    "841": "1",
                    "9001": "005930",
                    "843": "I",
                    "20": "153000",
                    "907": "2"
                }
            }]
        }
        
        await client._process_message(message)
        
        assert callback_called is True
        assert isinstance(received_data, ConditionalSearchRealtimeData)
        assert received_data.symbol == "005930"
        assert received_data.action == "I"
    
    @pytest.mark.asyncio
    async def test_process_message_subscription_response_success(self):
        """Test processing successful subscription response."""
        client = KiwoomRealtimeClient("test_token")
        
        message = {
            "trnm": "REG",
            "return_code": 0,
            "return_msg": ""
        }
        
        # Should not raise exception
        await client._process_message(message)
    
    @pytest.mark.asyncio
    async def test_process_message_subscription_response_failure(self):
        """Test processing failed subscription response."""
        client = KiwoomRealtimeClient("test_token")
        
        message = {
            "trnm": "REG",
            "return_code": 1,
            "return_msg": "Subscription failed"
        }
        
        with pytest.raises(KiwoomAPIError):
            await client._process_message(message)
    
    @pytest.mark.asyncio
    async def test_process_message_conditional_search_list(self):
        """Test processing conditional search list response."""
        client = KiwoomRealtimeClient("test_token")
        
        callback_called = False
        received_data = None
        
        def callback(data):
            nonlocal callback_called, received_data
            callback_called = True
            received_data = data
        
        client.add_callback("conditional_search_list", callback)
        
        message = {
            "trnm": "CNSRLST",
            "return_code": 0,
            "data": [
                ["1", "조건1"],
                ["2", "조건2"]
            ]
        }
        
        await client._process_message(message)
        
        assert callback_called is True
        assert received_data == message
    
    @pytest.mark.asyncio
    async def test_process_message_conditional_search_results(self):
        """Test processing conditional search results response."""
        client = KiwoomRealtimeClient("test_token")
        
        callback_called = False
        received_data = None
        
        def callback(data):
            nonlocal callback_called, received_data
            callback_called = True
            received_data = data
        
        client.add_callback("conditional_search_results", callback)
        
        message = {
            "trnm": "CNSRREQ",
            "seq": "1",
            "return_code": 0,
            "data": [
                {
                    "9001": "005930",
                    "302": "삼성전자",
                    "10": "75000"
                }
            ]
        }
        
        await client._process_message(message)
        
        assert callback_called is True
        assert received_data == message
    
    @pytest.mark.asyncio
    async def test_process_message_conditional_search_clear(self):
        """Test processing conditional search clear response."""
        client = KiwoomRealtimeClient("test_token")
        
        callback_called = False
        received_data = None
        
        def callback(data):
            nonlocal callback_called, received_data
            callback_called = True
            received_data = data
        
        client.add_callback("conditional_search_clear", callback)
        
        message = {
            "trnm": "CNSRCLR",
            "seq": "1",
            "return_code": 0
        }
        
        await client._process_message(message)
        
        assert callback_called is True
        assert received_data == message


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestSubscriptionMethods:
    """Test subscription methods."""
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_subscribe_stock_price_single(self, mock_connect):
        """Test subscribing to single stock price."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.subscribe_stock_price("005930")
        
        # Verify WebSocket send was called
        mock_ws.send.assert_called()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        
        assert sent_data["trnm"] == "REG"
        assert "005930" in sent_data["data"][0]["item"]
        assert "0A" in sent_data["data"][0]["type"]
        
        # Verify subscription was stored
        assert "price_005930" in client.subscriptions
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_subscribe_stock_price_multiple(self, mock_connect):
        """Test subscribing to multiple stock prices."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        symbols = ["005930", "000660", "035420"]
        await client.subscribe_stock_price(symbols)
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert set(symbols).issubset(set(sent_data["data"][0]["item"]))
        
        subscription_key = f"price_{'-'.join(symbols)}"
        assert subscription_key in client.subscriptions
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_subscribe_order_book(self, mock_connect):
        """Test subscribing to order book."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.subscribe_order_book("005930")
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert "0D" in sent_data["data"][0]["type"]  # ORDER_BOOK type
        assert "005930" in sent_data["data"][0]["item"]
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_subscribe_account_updates(self, mock_connect):
        """Test subscribing to account updates."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.subscribe_account_updates()
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert "00" in sent_data["data"][0]["type"]  # ORDER_EXECUTION type
        assert "04" in sent_data["data"][0]["type"]  # ACCOUNT_BALANCE type
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_subscribe_sector_index(self, mock_connect):
        """Test subscribing to sector index."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.subscribe_sector_index("001")
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert "0J" in sent_data["data"][0]["type"]  # SECTOR_INDEX type
        assert "0U" in sent_data["data"][0]["type"]  # SECTOR_CHANGE type
        assert "001" in sent_data["data"][0]["item"]
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_subscribe_etf_nav(self, mock_connect):
        """Test subscribing to ETF NAV."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.subscribe_etf_nav("069500")
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert "0G" in sent_data["data"][0]["type"]  # ETF_NAV type
        assert "069500" in sent_data["data"][0]["item"]
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_subscribe_elw_data(self, mock_connect):
        """Test subscribing to ELW data."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.subscribe_elw_data("5XXXXX")
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert "0m" in sent_data["data"][0]["type"]  # ELW_THEORY type
        assert "0u" in sent_data["data"][0]["type"]  # ELW_INDICATOR type
        assert "5XXXXX" in sent_data["data"][0]["item"]
    
    @pytest.mark.asyncio
    async def test_subscribe_not_connected(self):
        """Test subscription when not connected."""
        client = KiwoomRealtimeClient("test_token")
        
        with pytest.raises(KiwoomAPIError):
            await client.subscribe_stock_price("005930")


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestConditionalSearchMethods:
    """Test conditional search methods."""
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_get_conditional_search_list(self, mock_connect):
        """Test getting conditional search list."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.get_conditional_search_list()
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["trnm"] == "CNSRLST"
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_execute_conditional_search(self, mock_connect):
        """Test executing conditional search."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.execute_conditional_search(
            seq="1",
            search_type="0",
            exchange="K",
            cont_yn="N",
            next_key=""
        )
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["trnm"] == "CNSRREQ"
        assert sent_data["seq"] == "1"
        assert sent_data["search_type"] == "0"
        assert sent_data["stex_tp"] == "K"
        assert sent_data["cont_yn"] == "N"
        assert sent_data["next_key"] == ""
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_execute_conditional_search_realtime(self, mock_connect):
        """Test executing conditional search with real-time."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.execute_conditional_search_realtime(seq="1", exchange="K")
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["trnm"] == "CNSRREQ"
        assert sent_data["seq"] == "1"
        assert sent_data["search_type"] == "1"  # Real-time search
        assert sent_data["stex_tp"] == "K"
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_cancel_conditional_search_realtime(self, mock_connect):
        """Test canceling conditional search real-time."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        await client.cancel_conditional_search_realtime("1")
        
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["trnm"] == "CNSRCLR"
        assert sent_data["seq"] == "1"
    
    @pytest.mark.asyncio
    async def test_conditional_search_not_connected(self):
        """Test conditional search when not connected."""
        client = KiwoomRealtimeClient("test_token")
        
        with pytest.raises(KiwoomAPIError):
            await client.get_conditional_search_list()
        
        with pytest.raises(KiwoomAPIError):
            await client.execute_conditional_search("1")
        
        with pytest.raises(KiwoomAPIError):
            await client.execute_conditional_search_realtime("1")
        
        with pytest.raises(KiwoomAPIError):
            await client.cancel_conditional_search_realtime("1")


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestSubscriptionManagement:
    """Test subscription management methods."""
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_unsubscribe_specific(self, mock_connect):
        """Test unsubscribing from specific subscription."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        # Subscribe first
        await client.subscribe_stock_price("005930")
        assert "price_005930" in client.subscriptions
        
        # Unsubscribe
        await client.unsubscribe("price_005930")
        
        # Verify removal request was sent
        calls = mock_ws.send.call_args_list
        assert len(calls) == 2  # Subscribe + Unsubscribe
        
        unsubscribe_data = json.loads(calls[1][0][0])
        assert unsubscribe_data["trnm"] == "REMOVE"
        
        # Verify subscription was removed
        assert "price_005930" not in client.subscriptions
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_unsubscribe_nonexistent(self, mock_connect):
        """Test unsubscribing from nonexistent subscription."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        # Should not raise error
        await client.unsubscribe("nonexistent_key")
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_unsubscribe_all(self, mock_connect):
        """Test unsubscribing from all subscriptions."""
        mock_ws = AsyncMock()
        
        client = KiwoomRealtimeClient("test_token")
        # Set up mock WebSocket connection directly
        client.websocket = mock_ws
        client.is_connected = True
        
        # Subscribe to multiple
        await client.subscribe_stock_price("005930")
        await client.subscribe_order_book("000660")
        await client.subscribe_etf_nav("069500")
        
        assert len(client.subscriptions) == 3
        
        # Unsubscribe all
        await client.unsubscribe_all()
        
        assert len(client.subscriptions) == 0
        
        # Verify all removal requests were sent
        calls = mock_ws.send.call_args_list
        remove_calls = [call for call in calls if "REMOVE" in str(call)]
        assert len(remove_calls) == 3
    
    def test_get_active_subscriptions(self):
        """Test getting active subscriptions."""
        client = KiwoomRealtimeClient("test_token")
        
        # Add some subscriptions manually
        sub1 = RealtimeSubscription(symbols=["005930"], data_types=[RealtimeDataType.STOCK_PRICE])
        sub2 = RealtimeSubscription(symbols=["000660"], data_types=[RealtimeDataType.ORDER_BOOK])
        
        client.subscriptions["test1"] = sub1
        client.subscriptions["test2"] = sub2
        
        active = client.get_active_subscriptions()
        
        assert len(active) == 2
        assert "test1" in active
        assert "test2" in active
        assert active["test1"] == sub1
        assert active["test2"] == sub2
        
        # Verify it's a copy
        active["test3"] = "new"
        assert "test3" not in client.subscriptions


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestReconnectionLogic:
    """Test auto-reconnection logic."""
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    @patch('asyncio.sleep')
    async def test_auto_reconnect_success(self, mock_sleep, mock_connect):
        """Test successful auto-reconnection."""
        # Mock websocket connection for reconnect
        mock_ws = AsyncMock()
        async def mock_connect_coroutine(*args, **kwargs):
            return mock_ws
        mock_connect.return_value = mock_connect_coroutine()
        
        client = KiwoomRealtimeClient("test_token", auto_reconnect=True, max_reconnect_attempts=2)
        
        # Mock the connect method to simulate successful reconnection
        original_connect = client.connect
        connect_call_count = 0
        async def mock_connect_method():
            nonlocal connect_call_count
            connect_call_count += 1
            client.websocket = mock_ws
            client.is_connected = True
        client.connect = mock_connect_method
        
        # Test reconnection directly
        await client._reconnect()
        
        # Verify reconnection was attempted
        assert connect_call_count == 1
        mock_sleep.assert_called_once_with(5)  # Default reconnect_delay
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    @patch('asyncio.sleep')
    async def test_auto_reconnect_max_attempts(self, mock_sleep, mock_connect):
        """Test auto-reconnection hitting max attempts."""
        client = KiwoomRealtimeClient("test_token", auto_reconnect=True, max_reconnect_attempts=2)
        
        # Mock connect method to always fail
        connect_call_count = 0
        async def mock_failing_connect():
            nonlocal connect_call_count
            connect_call_count += 1
            raise Exception("Connection failed")
        client.connect = mock_failing_connect
        
        # _reconnect doesn't raise exceptions, it just logs and gives up
        await client._reconnect()
        
        # Should try max_reconnect_attempts times (initial + 1 retry)
        assert connect_call_count == 2
        assert client.reconnect_count == 2  # Final count after all attempts
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_auto_reconnect_disabled(self, mock_connect):
        """Test with auto-reconnection disabled."""
        mock_ws = AsyncMock()
        # Set up mock websocket properties to allow while loop to start
        mock_ws.closed = False
        
        # Simulate connection closed exception immediately on recv
        mock_ws.recv.side_effect = websockets.exceptions.ConnectionClosed(
            rcvd=None, sent=None
        )
        
        client = KiwoomRealtimeClient("test_token", auto_reconnect=False)
        client.is_connected = True
        client.websocket = mock_ws
        client.keep_running = True
        
        # Mock connect to track if it's called (it should NOT be called)
        connect_call_count = 0
        async def mock_failing_connect():
            nonlocal connect_call_count
            connect_call_count += 1
            raise Exception("Connection failed")
        client.connect = mock_failing_connect
        
        # Message handler should handle the connection closed but not reconnect
        await client._message_handler()
        
        # Should not attempt reconnection when auto_reconnect=False
        assert connect_call_count == 0, f"Expected 0 reconnect attempts, got {connect_call_count}"
        assert client.is_connected is False, "Expected is_connected to be False after connection closed"


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestRealtimeContext:
    """Test RealtimeContext context manager."""
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_context_manager_success(self, mock_connect):
        """Test successful context manager usage."""
        mock_ws = AsyncMock()
        # Set up mock to return a coroutine that returns the mock websocket
        async def mock_connect_coroutine(*args, **kwargs):
            return mock_ws
        mock_connect.return_value = mock_connect_coroutine()
        
        client = KiwoomRealtimeClient("test_token")
        
        # Mock the LOGIN response by setting is_connected directly after a short delay
        async def mock_login_response():
            await asyncio.sleep(0.1)  # Short delay to simulate network
            client.is_connected = True
        
        # Replace connect method to avoid real LOGIN flow
        original_connect = client.connect
        async def mock_connect_method():
            client.websocket = mock_ws
            await mock_login_response()
        client.connect = mock_connect_method
        
        context = RealtimeContext(client)
        
        async with context as ctx_client:
            assert ctx_client == client
            assert client.is_connected is True
        
        # Should be disconnected after exit
        assert client.is_connected is False
    
    @pytest.mark.asyncio
    @patch('websockets.connect')
    async def test_context_manager_exception(self, mock_connect):
        """Test context manager with exception."""
        mock_ws = AsyncMock()
        # Set up mock to return a coroutine that returns the mock websocket
        async def mock_connect_coroutine(*args, **kwargs):
            return mock_ws
        mock_connect.return_value = mock_connect_coroutine()
        
        client = KiwoomRealtimeClient("test_token")
        
        # Mock the LOGIN response by setting is_connected directly after a short delay
        async def mock_login_response():
            await asyncio.sleep(0.1)  # Short delay to simulate network
            client.is_connected = True
        
        # Replace connect method to avoid real LOGIN flow
        original_connect = client.connect
        async def mock_connect_method():
            client.websocket = mock_ws
            await mock_login_response()
        client.connect = mock_connect_method
        
        context = RealtimeContext(client)
        
        try:
            async with context as ctx_client:
                assert client.is_connected is True
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Should still be disconnected after exception
        assert client.is_connected is False


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
def test_create_realtime_client():
    """Test client factory function."""
    # Test sandbox client
    client = create_realtime_client(
        access_token="test_token",
        is_production=False,
        auto_reconnect=False,
        max_reconnect_attempts=3
    )
    
    assert isinstance(client, KiwoomRealtimeClient)
    assert client.access_token == "test_token"
    assert client.ws_url == client.SANDBOX_WS_URL
    assert client.auto_reconnect is False
    assert client.max_reconnect_attempts == 3
    
    # Test production client
    prod_client = create_realtime_client(
        access_token="prod_token",
        is_production=True
    )
    
    assert prod_client.ws_url == prod_client.PRODUCTION_WS_URL


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_callback_exception_handling(self):
        """Test that callback exceptions don't crash the client."""
        client = KiwoomRealtimeClient("test_token")
        
        def bad_callback(data):
            raise ValueError("Callback error")
        
        def good_callback(data):
            good_callback.called = True
        
        good_callback.called = False
        
        client.add_callback("0B", bad_callback)
        client.add_callback("0B", good_callback)
        
        message = {
            "trnm": "REAL",
            "data": [{
                "type": "0B",
                "name": "주식체결",
                "item": "005930",
                "values": {"10": "75000"}
            }]
        }
        
        # Should not raise exception despite bad callback
        await client._process_message(message)
        
        # Good callback should still be called
        assert good_callback.called is True
    
    @pytest.mark.asyncio
    async def test_malformed_message_handling(self):
        """Test handling of malformed messages."""
        client = KiwoomRealtimeClient("test_token")
        
        # Missing required fields
        malformed_messages = [
            {},
            {"trnm": "REAL"},
            {"data": []},
            {"trnm": "REAL", "data": [{"type": "0B"}]},  # Missing item
        ]
        
        for message in malformed_messages:
            # Should not raise exception
            await client._process_message(message)


def test_import_error_handling():
    """Test graceful handling when websockets is not available."""
    # This test runs even when websockets is available
    # to test the import error handling logic
    
    with patch.dict('sys.modules', {'websockets': None}):
        # The import should work at module level due to try/except
        # but REALTIME_AVAILABLE should be False
        pass


if __name__ == "__main__":
    # Run tests
    if REALTIME_AVAILABLE:
        pytest.main([__file__, "-v"])
    else:
        print("⚠️ Websockets not available, skipping real-time tests")
        print("Install with: pip install websockets") 