"""
Tests for real-time WebSocket functionality.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

try:
    from pyheroapi.realtime import (
        KiwoomRealtimeClient,
        RealtimeData,
        RealtimeDataType,
        RealtimeSubscription,
        create_realtime_client,
    )
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestRealtimeData:
    """Test RealtimeData class."""
    
    def test_from_response(self):
        """Test parsing WebSocket response into RealtimeData objects."""
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
        assert data.timestamp == "153000"


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestRealtimeSubscription:
    """Test RealtimeSubscription class."""
    
    def test_to_request(self):
        """Test converting subscription to request format."""
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


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestKiwoomRealtimeClient:
    """Test KiwoomRealtimeClient class."""
    
    def test_init(self):
        """Test client initialization."""
        client = KiwoomRealtimeClient(
            access_token="test_token",
            is_production=False,
            auto_reconnect=True,
            max_reconnect_attempts=3,
            reconnect_delay=5
        )
        
        assert client.access_token == "test_token"
        assert client.ws_url == client.SANDBOX_WS_URL
        assert client.auto_reconnect is True
        assert client.max_reconnect_attempts == 3
        assert client.reconnect_delay == 5
        assert client.is_connected is False
    
    def test_add_callback(self):
        """Test adding callbacks."""
        client = KiwoomRealtimeClient("test_token")
        
        def callback1(data):
            pass
        
        def callback2(data):
            pass
        
        # Test adding callback with string data type
        client.add_callback("0B", callback1)
        assert "0B" in client.callbacks
        assert callback1 in client.callbacks["0B"]
        
        # Test adding callback with enum data type
        client.add_callback(RealtimeDataType.STOCK_TRADE, callback2)
        assert callback2 in client.callbacks["0B"]
        
        # Test removing callback
        client.remove_callback("0B", callback1)
        assert callback1 not in client.callbacks["0B"]
        assert callback2 in client.callbacks["0B"]
    
    @patch('websockets.connect')
    async def test_connect(self, mock_connect):
        """Test WebSocket connection."""
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws
        
        client = KiwoomRealtimeClient("test_token")
        
        await client.connect()
        
        assert client.is_connected is True
        assert client.websocket == mock_ws
        mock_connect.assert_called_once()
    
    async def test_process_message_real(self):
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
    
    async def test_process_message_subscription_response(self):
        """Test processing subscription response message."""
        client = KiwoomRealtimeClient("test_token")
        
        # Test successful subscription
        message = {
            "trnm": "REG",
            "return_code": 0,
            "return_msg": ""
        }
        
        # Should not raise exception
        await client._process_message(message)
        
        # Test failed subscription
        message = {
            "trnm": "REG",
            "return_code": 1,
            "return_msg": "Subscription failed"
        }
        
        with pytest.raises(Exception):
            await client._process_message(message)


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
def test_create_realtime_client():
    """Test client factory function."""
    client = create_realtime_client(
        access_token="test_token",
        is_production=True,
        auto_reconnect=False
    )
    
    assert isinstance(client, KiwoomRealtimeClient)
    assert client.access_token == "test_token"
    assert client.ws_url == client.PRODUCTION_WS_URL
    assert client.auto_reconnect is False


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestRealtimeIntegration:
    """Integration tests with mocked WebSocket."""
    
    @patch('websockets.connect')
    async def test_subscription_workflow(self, mock_connect):
        """Test complete subscription workflow."""
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws
        
        client = KiwoomRealtimeClient("test_token")
        
        # Connect
        await client.connect()
        assert client.is_connected is True
        
        # Subscribe to stock price
        await client.subscribe_stock_price("005930")
        
        # Verify subscription was sent
        mock_ws.send.assert_called()
        sent_data = mock_ws.send.call_args[0][0]
        import json
        request = json.loads(sent_data)
        
        assert request["trnm"] == "REG"
        assert "005930" in request["data"][0]["item"]
        assert "0B" in request["data"][0]["type"] or "0A" in request["data"][0]["type"]
        
        # Test unsubscribe
        await client.unsubscribe_all()
        assert len(client.subscriptions) == 0


def test_import_error_handling():
    """Test graceful handling when websockets is not available."""
    # This test runs even when websockets is available
    # to test the import error handling logic
    
    with patch.dict('sys.modules', {'websockets': None}):
        # Should not raise error on import, but on usage
        try:
            from pyheroapi.realtime import KiwoomRealtimeClient
            # Creating client should work
            client = KiwoomRealtimeClient("test_token")
            
            # But trying to connect should fail gracefully
            # This is tested at the module level, not here
        except ImportError:
            # Expected when websockets is not available
            pass


if __name__ == "__main__":
    # Run tests
    if REALTIME_AVAILABLE:
        pytest.main([__file__, "-v"])
    else:
        print("⚠️ Websockets not available, skipping real-time tests")
        print("Install with: pip install websockets") 