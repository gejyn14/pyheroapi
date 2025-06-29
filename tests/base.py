"""
Base test classes and utilities for PyHero API testing.

This module provides:
- Base test classes with common testing patterns
- Custom assertions for API testing
- Test utilities and helper methods
- Performance testing infrastructure
- Error simulation and validation
"""

import asyncio
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import Mock, patch

import pytest
import responses

from pyheroapi import KiwoomClient, KiwoomAPI
from pyheroapi.exceptions import KiwoomAPIError, KiwoomAuthError, KiwoomRequestError

try:
    from pyheroapi.realtime import KiwoomRealtimeClient, RealtimeDataType
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False


class BaseTestCase:
    """Base test case with common testing utilities."""
    
    def setup_method(self):
        """Set up common test fixtures."""
        self.start_time = datetime.now()
        self.test_metrics = {}
    
    def teardown_method(self):
        """Clean up after test."""
        end_time = datetime.now()
        self.test_duration = (end_time - self.start_time).total_seconds()
        
        if self.test_duration > 5.0:
            print(f"⚠️  Slow test: {self.__class__.__name__} took {self.test_duration:.2f}s")
    
    def assert_valid_korean_stock_symbol(self, symbol: str):
        """Assert that a symbol is a valid Korean stock code."""
        assert isinstance(symbol, str), f"Symbol must be string, got {type(symbol)}"
        assert len(symbol) == 6, f"Korean stock symbol must be 6 digits, got: {symbol}"
        assert symbol.isdigit(), f"Korean stock symbol must be numeric, got: {symbol}"
    
    def assert_valid_price(self, price: Union[str, float], allow_negative: bool = False):
        """Assert that a price value is valid."""
        if isinstance(price, str):
            price_float = float(price)
        else:
            price_float = float(price)
        
        if not allow_negative:
            assert price_float >= 0, f"Price cannot be negative: {price_float}"
        assert 0 <= price_float <= 10_000_000, f"Price outside reasonable range: {price_float}"
    
    def assert_valid_timestamp(self, timestamp: str, format_type: str = "HHMMSS"):
        """Assert that a timestamp is in valid format."""
        if format_type == "HHMMSS":
            assert len(timestamp) == 6, f"HHMMSS timestamp must be 6 digits, got: {timestamp}"
            assert timestamp.isdigit(), f"Timestamp must be numeric, got: {timestamp}"
            
            hour = int(timestamp[:2])
            minute = int(timestamp[2:4])
            second = int(timestamp[4:6])
            
            assert 0 <= hour <= 23, f"Invalid hour: {hour}"
            assert 0 <= minute <= 59, f"Invalid minute: {minute}"
            assert 0 <= second <= 59, f"Invalid second: {second}"
    
    def assert_api_response_success(self, response: Dict[str, Any]):
        """Assert that an API response indicates success."""
        assert "return_code" in response, "Response missing return_code"
        assert response["return_code"] == 0, f"API error: {response.get('return_msg', 'Unknown')}"
    
    def assert_api_response_error(self, response: Dict[str, Any], expected_code: int = None):
        """Assert that an API response indicates an error."""
        assert "return_code" in response, "Response missing return_code"
        assert response["return_code"] != 0, "Expected error response but got success"
        
        if expected_code:
            assert response["return_code"] == expected_code, \
                f"Expected error code {expected_code}, got {response['return_code']}"
    
    @contextmanager
    def assert_performance_within(self, max_seconds: float):
        """Context manager to assert that code executes within time limit."""
        start = time.time()
        yield
        duration = time.time() - start
        assert duration <= max_seconds, \
            f"Operation took {duration:.2f}s, expected <= {max_seconds}s"
    
    @contextmanager
    def capture_performance_metrics(self):
        """Context manager to capture performance metrics."""
        start = time.time()
        start_memory = self._get_memory_usage()
        
        yield
        
        end = time.time()
        end_memory = self._get_memory_usage()
        
        self.test_metrics.update({
            "execution_time": end - start,
            "memory_delta": end_memory - start_memory,
            "timestamp": datetime.now().isoformat()
        })
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0  # Graceful fallback if psutil not available
    
    def mock_successful_api_response(self, url_path: str, response_data: Dict[str, Any]):
        """Helper to mock a successful API response."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"https://openapivts.kiwoom.com:9443{url_path}",
                json=response_data,
                status=200
            )
            yield rsps
    
    def mock_api_error(self, url_path: str, error_code: int, error_message: str, status_code: int = 200):
        """Helper to mock an API error response."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"https://openapivts.kiwoom.com:9443{url_path}",
                json={
                    "return_code": error_code,
                    "return_msg": error_message
                },
                status=status_code
            )
            yield rsps


class BaseUnitTest(BaseTestCase):
    """Base class for unit tests with mocking support."""
    
    def setup_method(self):
        """Set up unit test fixtures."""
        super().setup_method()
        self.mock_client = None
        self.patches = []
    
    def teardown_method(self):
        """Clean up unit test fixtures."""
        # Stop all patches
        for patcher in self.patches:
            patcher.stop()
        self.patches.clear()
        super().teardown_method()
    
    def create_mock_client(self, access_token: str = "test_token") -> KiwoomClient:
        """Create a mocked client for testing."""
        client = KiwoomClient(access_token=access_token, is_production=False)
        self.mock_client = client
        return client
    
    def patch_method(self, target: str, return_value: Any = None, side_effect: Any = None):
        """Patch a method and track it for cleanup."""
        patcher = patch(target, return_value=return_value, side_effect=side_effect)
        mock = patcher.start()
        self.patches.append(patcher)
        return mock
    
    def assert_method_called_with(self, mock_method: Mock, *args, **kwargs):
        """Assert that a mocked method was called with specific arguments."""
        mock_method.assert_called_with(*args, **kwargs)
    
    def assert_method_called_once(self, mock_method: Mock):
        """Assert that a mocked method was called exactly once."""
        mock_method.assert_called_once()


class BaseIntegrationTest(BaseTestCase):
    """Base class for integration tests with real API connections."""
    
    @pytest.fixture(autouse=True)
    def skip_if_not_enabled(self):
        """Skip integration tests if not explicitly enabled."""
        import os
        if not os.getenv("RUN_INTEGRATION_TESTS", "false").lower() in ("true", "1", "yes"):
            pytest.skip("Integration tests disabled")
    
    def setup_method(self):
        """Set up integration test fixtures."""
        super().setup_method()
        self.real_client = None
        self.cleanup_actions = []
    
    def teardown_method(self):
        """Clean up integration test fixtures."""
        # Perform cleanup actions in reverse order
        for cleanup_action in reversed(self.cleanup_actions):
            try:
                cleanup_action()
            except Exception as e:
                print(f"Warning: Cleanup action failed: {e}")
        
        self.cleanup_actions.clear()
        super().teardown_method()
    
    def create_real_client(self) -> KiwoomClient:
        """Create a real client for integration testing."""
        import os
        
        access_token = os.getenv("KIWOOM_ACCESS_TOKEN")
        if not access_token:
            pytest.skip("Real API credentials not available")
        
        return KiwoomClient(access_token=access_token, is_production=False)
    
    def add_cleanup(self, cleanup_action: Callable):
        """Add a cleanup action to be performed after the test."""
        self.cleanup_actions.append(cleanup_action)
    
    def wait_for_market_hours(self):
        """Skip test if not during market hours."""
        import os
        if os.getenv("FORCE_MARKET_HOURS_TEST") != "true":
            pytest.skip("Skipping market hours test - set FORCE_MARKET_HOURS_TEST=true to override")


@pytest.mark.skipif(not REALTIME_AVAILABLE, reason="websockets not available")
class BaseRealtimeTest(BaseTestCase):
    """Base class for real-time WebSocket tests."""
    
    def setup_method(self):
        """Set up real-time test fixtures."""
        super().setup_method()
        self.realtime_client = None
        self.connected_clients = []
        self.received_data = []
    
    def teardown_method(self):
        """Clean up real-time test fixtures."""
        # Disconnect all clients
        for client in self.connected_clients:
            try:
                if hasattr(client, 'disconnect'):
                    asyncio.create_task(client.disconnect())
            except Exception as e:
                print(f"Warning: Failed to disconnect realtime client: {e}")
        
        self.connected_clients.clear()
        super().teardown_method()
    
    def create_realtime_client(self, access_token: str = "test_token") -> KiwoomRealtimeClient:
        """Create a real-time client for testing."""
        client = KiwoomRealtimeClient(access_token=access_token, is_production=False)
        self.realtime_client = client
        self.connected_clients.append(client)
        return client
    
    def add_data_callback(self, data_type: RealtimeDataType, callback: Callable = None):
        """Add a callback to collect received data."""
        if callback is None:
            def default_callback(data):
                self.received_data.append({
                    "type": data_type,
                    "data": data,
                    "timestamp": datetime.now()
                })
            callback = default_callback
        
        self.realtime_client.add_callback(data_type, callback)
        return callback
    
    def assert_data_received(self, data_type: RealtimeDataType = None, timeout: float = 10.0):
        """Assert that data was received within timeout period."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if data_type is None:
                if self.received_data:
                    return True
            else:
                for data_item in self.received_data:
                    if data_item["type"] == data_type:
                        return True
            time.sleep(0.1)
        
        pytest.fail(f"No data received for {data_type} within {timeout}s")


class BasePerformanceTest(BaseTestCase):
    """Base class for performance tests."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        super().setup_method()
        self.performance_data = {
            "test_name": self.__class__.__name__,
            "start_time": datetime.now(),
            "metrics": {}
        }
    
    def teardown_method(self):
        """Clean up and report performance metrics."""
        self.performance_data["end_time"] = datetime.now()
        self.performance_data["duration"] = (
            self.performance_data["end_time"] - self.performance_data["start_time"]
        ).total_seconds()
        
        # Report performance metrics
        self._report_performance_metrics()
        super().teardown_method()
    
    def benchmark_operation(self, operation: Callable, iterations: int = 100) -> Dict[str, float]:
        """Benchmark an operation over multiple iterations."""
        times = []
        
        for _ in range(iterations):
            start = time.time()
            operation()
            end = time.time()
            times.append(end - start)
        
        return {
            "min_time": min(times),
            "max_time": max(times),
            "avg_time": sum(times) / len(times),
            "total_time": sum(times),
            "iterations": iterations
        }
    
    def assert_performance_benchmark(self, operation: Callable, max_avg_time: float, iterations: int = 50):
        """Assert that an operation meets performance benchmarks."""
        metrics = self.benchmark_operation(operation, iterations)
        
        assert metrics["avg_time"] <= max_avg_time, \
            f"Average time {metrics['avg_time']:.3f}s exceeds benchmark {max_avg_time}s"
        
        self.performance_data["metrics"].update(metrics)
        return metrics
    
    def _report_performance_metrics(self):
        """Report performance metrics."""
        if self.performance_data["metrics"]:
            print(f"\n📊 Performance Report for {self.performance_data['test_name']}:")
            print(f"   Duration: {self.performance_data['duration']:.2f}s")
            for key, value in self.performance_data["metrics"].items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.3f}s")
                else:
                    print(f"   {key}: {value}")


class APITestSuite:
    """Comprehensive API test suite utilities."""
    
    @staticmethod
    def test_all_endpoints(client: KiwoomClient, test_symbols: Dict[str, List[str]]):
        """Test all available API endpoints."""
        results = {
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        # Test stock-related endpoints
        for symbol in test_symbols.get("stocks", ["005930"]):
            try:
                client.get_quote(symbol)
                results["passed"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"get_quote({symbol}): {e}")
            finally:
                results["tested"] += 1
        
        # Test ETF endpoints
        for symbol in test_symbols.get("etfs", ["069500"]):
            try:
                client.get_etf_info(symbol)
                results["passed"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"get_etf_info({symbol}): {e}")
            finally:
                results["tested"] += 1
        
        return results
    
    @staticmethod
    def validate_response_schemas(responses: List[Dict[str, Any]]) -> List[str]:
        """Validate that API responses conform to expected schemas."""
        errors = []
        
        for i, response in enumerate(responses):
            if not isinstance(response, dict):
                errors.append(f"Response {i}: Not a dictionary")
                continue
            
            if "return_code" not in response:
                errors.append(f"Response {i}: Missing return_code")
            
            if "return_msg" not in response:
                errors.append(f"Response {i}: Missing return_msg")
        
        return errors


# Utility decorators for test management
def requires_real_credentials(func):
    """Decorator to skip test if real credentials are not available."""
    def wrapper(*args, **kwargs):
        import os
        if not (os.getenv("KIWOOM_APPKEY") and os.getenv("KIWOOM_SECRETKEY")):
            pytest.skip("Real API credentials required")
        return func(*args, **kwargs)
    return wrapper


def requires_market_hours(func):
    """Decorator to skip test if not during market hours."""
    def wrapper(*args, **kwargs):
        import os
        from datetime import datetime
        
        if os.getenv("FORCE_MARKET_HOURS_TEST") == "true":
            return func(*args, **kwargs)
        
        # Simple market hours check (9 AM - 4 PM KST, Mon-Fri)
        now = datetime.now()
        if now.weekday() >= 5:  # Weekend
            pytest.skip("Market closed - weekend")
        
        if not (9 <= now.hour < 16):  # Not market hours
            pytest.skip("Market closed - outside trading hours")
        
        return func(*args, **kwargs)
    return wrapper


def timeout(seconds: float):
    """Decorator to add timeout to test functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                pytest.fail(f"Test timed out after {seconds} seconds")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                return result
            except:
                signal.alarm(0)  # Cancel alarm
                raise
        
        return wrapper
    return decorator 