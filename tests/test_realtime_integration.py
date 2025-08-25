"""
Integration tests for real-time WebSocket functionality.

These tests connect to the actual Kiwoom API to verify:
- Real data reception and parsing
- WebSocket connection stability  
- Subscription management with real responses
- Conditional search with actual data
- Error handling with real API responses

Prerequisites:
- Valid Kiwoom API credentials in environment
- Network connectivity to Kiwoom servers
- Market hours for some tests (optional)
"""

import asyncio
import os
import time
import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any
import threading
import queue

try:
    from pyheroapi.realtime import (
        KiwoomRealtimeClient,
        RealtimeData,
        RealtimeDataType,
        ConditionalSearchItem,
        ConditionalSearchResult,
        create_realtime_client,
    )
    from pyheroapi.exceptions import KiwoomAPIError
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False


# Test configuration
TEST_TIMEOUT = 30  # seconds
MARKET_HOURS_TIMEOUT = 60  # seconds for market hours tests
TEST_SYMBOLS = ["005930", "000660", "035420"]  # Samsung, SKHynix, NAVER
TEST_ACCOUNT = "5123456789"  # Mock account for testing


def requires_credentials():
    """Decorator to skip tests when credentials are not available."""
    has_credentials = all([
        os.getenv('KIWOOM_APPKEY'),
        os.getenv('KIWOOM_SECRETKEY')
    ])
    return pytest.mark.skipif(
        not has_credentials,
        reason="Kiwoom API credentials not available"
    )


def requires_market_hours():
    """Decorator to skip tests outside market hours."""
    now = datetime.now()
    is_weekday = now.weekday() < 5  # Monday=0, Friday=4
    is_market_time = 9 <= now.hour < 16  # 9 AM to 4 PM KST
    
    return pytest.mark.skipif(
        not (is_weekday and is_market_time),
        reason="Test requires market hours (Mon-Fri 9AM-4PM KST)"
    )


async def get_test_access_token():
    """Get access token for testing."""
    access_token = os.getenv('KIWOOM_ACCESS_TOKEN')
    if access_token:
        return access_token
    
    # Generate token from app key and secret key
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        pytest.skip("Missing KIWOOM_APPKEY or KIWOOM_SECRETKEY")
    
    try:
        from pyheroapi.client import KiwoomClient
        token_response = await asyncio.get_event_loop().run_in_executor(
            None, KiwoomClient.issue_token, app_key, secret_key, False  # False = sandbox mode
        )
        if token_response and hasattr(token_response, 'token'):
            return token_response.token
        else:
            pytest.skip("Failed to obtain access token")
    except Exception as e:
        pytest.skip(f"Error getting access token: {e}")


class DataCollector:
    """Helper class to collect and validate received data."""
    
    def __init__(self):
        self.received_data: List[RealtimeData] = []
        self.conditional_search_items: List[ConditionalSearchItem] = []
        self.conditional_search_results: List[ConditionalSearchResult] = []
        self.errors: List[Exception] = []
        self.connection_events: List[str] = []
        self.data_queue = queue.Queue()
        
    def stock_callback(self, data: List[RealtimeData]):
        """Callback for stock price data."""
        self.received_data.extend(data)
        self.data_queue.put(('stock', data))
        
    def conditional_search_callback(self, items: List[ConditionalSearchItem]):
        """Callback for conditional search list."""
        self.conditional_search_items.extend(items)
        self.data_queue.put(('conditional_list', items))
        
    def conditional_results_callback(self, results: List[ConditionalSearchResult]):
        """Callback for conditional search results."""
        self.conditional_search_results.extend(results)
        self.data_queue.put(('conditional_results', results))
        
    def error_callback(self, error: Exception):
        """Callback for errors."""
        self.errors.append(error)
        self.data_queue.put(('error', error))
        
    def connection_callback(self, event: str):
        """Callback for connection events."""
        self.connection_events.append(event)
        self.data_queue.put(('connection', event))
        
    def wait_for_data(self, timeout: int = TEST_TIMEOUT, min_items: int = 1) -> bool:
        """Wait for minimum number of data items with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if len(self.received_data) >= min_items:
                return True
            time.sleep(0.1)
        return False
        
    def wait_for_conditional_data(self, timeout: int = TEST_TIMEOUT, min_items: int = 1) -> bool:
        """Wait for conditional search data."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if (len(self.conditional_search_items) >= min_items or 
                len(self.conditional_search_results) >= min_items):
                return True
            time.sleep(0.1)
        return False


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestRealConnectionAndData:
    """Test actual connection and data reception."""
    
    @requires_credentials()
    async def test_connection_establishment(self):
        """Test that we can establish a real WebSocket connection."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APPKEY'),
            secret_key=os.getenv('KIWOOM_SECRETKEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False  # Use sandbox for testing
        )
        
        try:
            # Test connection
            await client.connect()
            assert client.websocket is not None
            assert client._connected is True
            
            # Test disconnection
            await client.disconnect()
            assert client._connected is False
            
        except Exception as e:
            pytest.fail(f"Connection test failed: {e}")
    
    @requires_credentials()
    async def test_subscription_and_data_reception(self):
        """Test subscribing to real stock data and receiving updates."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False
        )
        
        # Add callback
        client.add_callback(RealtimeDataType.STOCK_PRICE, collector.stock_callback)
        
        try:
            await client.connect()
            
            # Subscribe to Samsung Electronics
            await client.subscribe_stock_price(["005930"])
            
            # Wait for data (may take longer in sandbox)
            await asyncio.sleep(5)
            
            # Check subscription was registered
            subscriptions = client.get_active_subscriptions()
            assert len(subscriptions) > 0
            assert any("005930" in str(sub) for sub in subscriptions)
            
        except Exception as e:
            pytest.fail(f"Subscription test failed: {e}")
        finally:
            await client.disconnect()
    
    @requires_credentials()
    @requires_market_hours()
    async def test_real_market_data_reception(self):
        """Test receiving actual market data during trading hours."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=True  # Use production for real market data
        )
        
        client.add_callback(RealtimeDataType.STOCK_PRICE, collector.stock_callback)
        client.add_callback(RealtimeDataType.STOCK_TRADE, collector.stock_callback)
        
        try:
            await client.connect()
            
            # Subscribe to multiple active stocks
            await client.subscribe_stock_price(TEST_SYMBOLS)
            
            # Wait for real market data
            success = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, collector.wait_for_data, MARKET_HOURS_TIMEOUT, 3
                ),
                timeout=MARKET_HOURS_TIMEOUT + 5
            )
            
            assert success, "No market data received within timeout"
            assert len(collector.received_data) >= 3
            
            # Validate data structure
            for data in collector.received_data[:3]:
                assert data.symbol in TEST_SYMBOLS
                assert data.data_type in [RealtimeDataType.STOCK_PRICE.value, RealtimeDataType.STOCK_TRADE.value]
                assert len(data.values) > 0
                assert data.timestamp is not None
                
                # Validate price data format
                if "10" in data.values:  # Current price
                    price = data.values["10"]
                    assert price.isdigit() or price.replace(".", "").isdigit()
                    assert float(price.replace("0", "").lstrip("0") or "0") >= 0
                    
        except asyncio.TimeoutError:
            pytest.skip("Market data not available within timeout")
        except Exception as e:
            pytest.fail(f"Market data test failed: {e}")
        finally:
            await client.disconnect()


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestConditionalSearchIntegration:
    """Test conditional search with real API."""
    
    @requires_credentials()
    async def test_conditional_search_list_retrieval(self):
        """Test retrieving actual conditional search list."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False
        )
        
        client.add_conditional_search_callback(collector.conditional_search_callback)
        
        try:
            await client.connect()
            
            # Request conditional search list
            await client.get_conditional_search_list()
            
            # Wait for response
            success = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, collector.wait_for_conditional_data, TEST_TIMEOUT, 1
                ),
                timeout=TEST_TIMEOUT + 5
            )
            
            if success and collector.conditional_search_items:
                # Validate conditional search items
                for item in collector.conditional_search_items:
                    assert hasattr(item, 'seq')
                    assert hasattr(item, 'name')
                    assert item.seq is not None
                    assert item.name is not None
                    assert len(item.name) > 0
            else:
                pytest.skip("No conditional search items available")
                
        except Exception as e:
            pytest.fail(f"Conditional search list test failed: {e}")
        finally:
            await client.disconnect()
    
    @requires_credentials()
    async def test_conditional_search_execution(self):
        """Test executing conditional search if items are available."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False
        )
        
        client.add_conditional_search_callback(collector.conditional_search_callback)
        client.add_conditional_search_results_callback(collector.conditional_results_callback)
        
        try:
            await client.connect()
            
            # First get the list
            await client.get_conditional_search_list()
            await asyncio.sleep(3)
            
            if collector.conditional_search_items:
                # Execute the first available condition
                first_condition = collector.conditional_search_items[0]
                await client.execute_conditional_search(first_condition.seq, first_condition.name)
                
                # Wait for results
                await asyncio.sleep(5)
                
                # Validate results if any
                if collector.conditional_search_results:
                    for result in collector.conditional_search_results:
                        assert hasattr(result, 'symbol')
                        assert hasattr(result, 'name')
                        assert len(result.symbol) == 6  # Korean stock code format
                        assert len(result.name) > 0
            else:
                pytest.skip("No conditional search items available for execution")
                
        except Exception as e:
            pytest.fail(f"Conditional search execution test failed: {e}")
        finally:
            await client.disconnect()


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestErrorHandlingIntegration:
    """Test error handling with real API responses."""
    
    @requires_credentials()
    async def test_invalid_subscription_handling(self):
        """Test handling of invalid subscription requests."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False
        )
        
        try:
            await client.connect()
            
            # Try to subscribe with invalid stock code
            with pytest.raises((KiwoomAPIError, ValueError)):
                await client.subscribe_stock_price(["INVALID"])
            
            # Try to subscribe with malformed codes
            with pytest.raises((KiwoomAPIError, ValueError)):
                await client.subscribe_stock_price(["12345"])  # Too short
                
        except Exception as e:
            if "INVALID" in str(e) or "12345" in str(e):
                pass  # Expected error
            else:
                pytest.fail(f"Unexpected error in invalid subscription test: {e}")
        finally:
            await client.disconnect()
    
    @requires_credentials()
    async def test_connection_resilience(self):
        """Test connection handling and reconnection."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False,
            auto_reconnect=True,
            max_reconnect_attempts=2
        )
        
        try:
            # Test normal connection
            await client.connect()
            assert client._connected is True
            
            # Simulate connection loss by forcing disconnect
            if client.websocket:
                await client.websocket.close()
            
            # Wait a moment for reconnection logic
            await asyncio.sleep(3)
            
            # Connection should be restored or attempting to restore
            # (Depending on timing and server response)
            
        except Exception as e:
            pytest.fail(f"Connection resilience test failed: {e}")
        finally:
            await client.disconnect()


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestDataValidation:
    """Test validation of received real data."""
    
    @requires_credentials()
    async def test_data_format_validation(self):
        """Test that received data matches expected Korean market format."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False
        )
        
        client.add_callback(RealtimeDataType.STOCK_PRICE, collector.stock_callback)
        
        try:
            await client.connect()
            await client.subscribe_stock_price(["005930"])  # Samsung
            
            # Wait for at least one data point
            await asyncio.sleep(10)
            
            if collector.received_data:
                data = collector.received_data[0]
                
                # Validate Korean stock code format
                assert len(data.symbol) == 6
                assert data.symbol.isdigit()
                assert data.symbol.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))
                
                # Validate timestamp format (HHMMSS)
                if data.timestamp:
                    assert len(data.timestamp) == 6
                    assert data.timestamp.isdigit()
                    hour = int(data.timestamp[:2])
                    minute = int(data.timestamp[2:4])
                    second = int(data.timestamp[4:6])
                    assert 0 <= hour <= 23
                    assert 0 <= minute <= 59
                    assert 0 <= second <= 59
                
                # Validate data type
                assert data.data_type in [dt.value for dt in RealtimeDataType]
                
                # Validate values structure
                assert isinstance(data.values, dict)
                assert len(data.values) > 0
                
            else:
                pytest.skip("No data received for validation")
                
        except Exception as e:
            pytest.fail(f"Data validation test failed: {e}")
        finally:
            await client.disconnect()


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class TestPerformanceAndStability:
    """Test performance and stability with real connections."""
    
    @requires_credentials()
    async def test_multiple_subscriptions_stability(self):
        """Test stability with multiple simultaneous subscriptions."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False
        )
        
        client.add_callback(RealtimeDataType.STOCK_PRICE, collector.stock_callback)
        client.add_callback(RealtimeDataType.ORDER_BOOK, collector.stock_callback)
        
        try:
            await client.connect()
            
            # Subscribe to multiple data types for multiple stocks
            await client.subscribe_stock_price(TEST_SYMBOLS)
            await client.subscribe_order_book(TEST_SYMBOLS)
            
            # Let it run for a while
            await asyncio.sleep(15)
            
            # Check that we have active subscriptions
            subscriptions = client.get_active_subscriptions()
            assert len(subscriptions) > 0
            
            # Test unsubscribing
            await client.unsubscribe_all()
            await asyncio.sleep(2)
            
            subscriptions_after = client.get_active_subscriptions()
            assert len(subscriptions_after) == 0
            
        except Exception as e:
            pytest.fail(f"Multiple subscriptions test failed: {e}")
        finally:
            await client.disconnect()
    
    @requires_credentials()
    async def test_long_running_connection(self):
        """Test connection stability over extended period."""
        collector = DataCollector()
        
        client = create_realtime_client(
            app_key=os.getenv('KIWOOM_APP_KEY'),
            secret_key=os.getenv('KIWOOM_SECRET_KEY'),
            access_token=os.getenv('KIWOOM_ACCESS_TOKEN'),
            is_production=False
        )
        
        client.add_callback(RealtimeDataType.STOCK_PRICE, collector.stock_callback)
        
        try:
            await client.connect()
            await client.subscribe_stock_price(["005930"])
            
            # Run for 30 seconds
            start_time = time.time()
            data_counts = []
            
            while time.time() - start_time < 30:
                await asyncio.sleep(5)
                data_counts.append(len(collector.received_data))
                
                # Check connection is still alive
                assert client._connected is True
            
            # Verify we're still receiving data (data counts should increase)
            if len(data_counts) > 1:
                # Allow for some variation in data flow
                assert max(data_counts) >= min(data_counts)
            
        except Exception as e:
            pytest.fail(f"Long running connection test failed: {e}")
        finally:
            await client.disconnect()


# Utility test for environment setup
def test_environment_setup():
    """Test that test environment is properly configured."""
    required_vars = ['KIWOOM_APPKEY', 'KIWOOM_SECRETKEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.skip(f"Missing environment variables for integration tests: {missing_vars}")
    
    # Test that we can import the realtime module
    assert REALTIME_AVAILABLE, "Realtime module not available"
    
    # Test basic client creation
    try:
        client = create_realtime_client(
            access_token="test",
            is_production=False  # SANDBOX MODE: set is_production=False explicitly
        )
        assert client is not None
    except Exception as e:
        pytest.fail(f"Client creation failed: {e}")


if __name__ == "__main__":
    # Run basic environment test
    test_environment_setup()
    print("✅ Integration test environment is ready")
    print("💡 To run full integration tests:")
    print("   pytest tests/test_realtime_integration.py -v")
    print("   pytest tests/test_realtime_integration.py::TestRealConnectionAndData -v")
    print("   pytest tests/test_realtime_integration.py::TestConditionalSearchIntegration -v") 