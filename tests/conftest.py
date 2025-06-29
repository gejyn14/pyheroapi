"""
Pytest configuration and shared fixtures for PyHero API tests.

This module provides:
- Shared test fixtures for client instances, mock data, and common test scenarios
- Test utilities for data generation and validation
- Configuration management for different test environments
- Custom pytest markers and plugins
"""

import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from unittest.mock import AsyncMock, Mock

import pytest
import responses

from pyheroapi import (
    KiwoomClient,
    KiwoomAPI,
    ELW,
    ETF,
    Stock,
    Account,
)
from pyheroapi.exceptions import KiwoomAPIError, KiwoomAuthError, KiwoomRequestError

try:
    from pyheroapi.realtime import (
        KiwoomRealtimeClient,
        RealtimeDataType,
        RealtimeData,
        RealtimeSubscription,
        ConditionalSearchItem,
        ConditionalSearchResult,
    )
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False


# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TestConfig:
    """Test configuration management."""
    
    # Test environment settings
    DEFAULT_ACCESS_TOKEN = "test_access_token_12345"
    DEFAULT_APP_KEY = "test_app_key_67890"
    DEFAULT_SECRET_KEY = "test_secret_key_abcdef"
    DEFAULT_ACCOUNT_NUMBER = "12345678901"
    
    # Test symbols for different asset types
    TEST_STOCK_SYMBOLS = ["005930", "000660", "035420"]  # Samsung, SKHynix, NAVER
    TEST_ETF_SYMBOLS = ["069500", "114800", "251340"]  # KODEX 200, KODEX Inverse, KODEX KOSDAQ150
    TEST_ELW_SYMBOLS = ["57JBHH", "58ABCD", "59EFGH"]  # Mock ELW symbols
    
    # API URLs for testing (must match actual client URLs)
    SANDBOX_URL = "https://mockapi.kiwoom.com"
    PRODUCTION_URL = "https://api.kiwoom.com"
    
    @classmethod
    def get_test_credentials(cls) -> Dict[str, str]:
        """Get test credentials from environment or defaults."""
        return {
            "access_token": os.getenv("TEST_ACCESS_TOKEN", cls.DEFAULT_ACCESS_TOKEN),
            "app_key": os.getenv("TEST_APP_KEY", cls.DEFAULT_APP_KEY),
            "secret_key": os.getenv("TEST_SECRET_KEY", cls.DEFAULT_SECRET_KEY),
            "account_number": os.getenv("TEST_ACCOUNT_NUMBER", cls.DEFAULT_ACCOUNT_NUMBER),
        }
    
    @classmethod
    def get_mock_credentials(cls) -> Dict[str, str]:
        """Get real mock environment credentials for integration tests."""
        return {
            "app_key": os.getenv("MOCK_KIWOOM_APPKEY"),
            "secret_key": os.getenv("MOCK_KIWOOM_SECRETKEY"),
        }
    
    @classmethod
    def is_integration_test_enabled(cls) -> bool:
        """Check if integration tests should run."""
        return os.getenv("RUN_INTEGRATION_TESTS", "false").lower() in ("true", "1", "yes")
    
    @classmethod
    def is_performance_test_enabled(cls) -> bool:
        """Check if performance tests should run."""
        return os.getenv("RUN_PERFORMANCE_TESTS", "false").lower() in ("true", "1", "yes")


class MockDataGenerator:
    """Generate realistic mock data for testing."""
    
    @staticmethod
    def create_stock_quote_response(symbol: str = "005930", **overrides) -> Dict[str, Any]:
        """Create a realistic stock quote API response."""
        base_data = {
            "return_code": 0,
            "return_msg": "Success",
            "bid_req_base_tm": "162000",
            "sel_fpr_bid": "75000",
            "buy_fpr_bid": "74900",
            "tot_sel_req": "1500",
            "tot_buy_req": "2000",
        }
        base_data.update(overrides)
        return base_data
    
    @staticmethod
    def create_etf_info_response(symbol: str = "069500", **overrides) -> Dict[str, Any]:
        """Create a realistic ETF info API response."""
        base_data = {
            "return_code": 0,
            "return_msg": "Success",
            "stk_nm": "KODEX 200",
            "nav": "25000.50",
            "trace_eor_rt": "0.05",
            "prm_rt": "0.02",
            "tot_stk_aset": "500000000000",
        }
        base_data.update(overrides)
        return base_data
    
    @staticmethod
    def create_elw_info_response(symbol: str = "57JBHH", **overrides) -> Dict[str, Any]:
        """Create a realistic ELW info API response."""
        base_data = {
            "return_code": 0,
            "return_msg": "Success",
            "bsis_aset_1": "KOSPI200",
            "elwexec_pric": "400.00",
            "expr_dt": "20241216",
            "elwcnvt_rt": "100.0000",
            "delta": "0.5",
            "gam": "0.1",
            "theta": "-0.02",
            "vega": "0.3",
        }
        base_data.update(overrides)
        return base_data
    
    @staticmethod
    def create_realtime_stock_data(symbol: str = "005930", **overrides) -> Dict[str, Any]:
        """Create realistic real-time stock data."""
        base_data = {
            "data": [
                {
                    "type": "0A",
                    "name": "주식시세",
                    "item": symbol,
                    "values": {
                        "10": "75000",  # Current price
                        "11": "1000",   # Change
                        "12": "1.35",   # Change rate
                        "20": "153000", # Time
                        "13": "10000000", # Volume
                        "16": "74000",  # Open
                        "17": "76000",  # High
                        "18": "73500",  # Low
                    }
                }
            ]
        }
        if overrides:
            base_data["data"][0]["values"].update(overrides)
        return base_data
    
    @staticmethod
    def create_error_response(error_code: int = 1001, error_msg: str = "Invalid request") -> Dict[str, Any]:
        """Create an error response."""
        return {
            "return_code": error_code,
            "return_msg": error_msg,
        }


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (fast, uses mocks)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (requires API credentials)"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test (may take time)"
    )
    config.addinivalue_line(
        "markers", "realtime: mark test as requiring real-time WebSocket functionality"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Pytest collection and skipping logic
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle conditional skipping."""
    for item in items:
        # Skip integration tests unless explicitly enabled
        if "integration" in item.keywords and not TestConfig.is_integration_test_enabled():
            item.add_marker(pytest.mark.skip(reason="Integration tests disabled"))
        
        # Skip performance tests unless explicitly enabled
        if "performance" in item.keywords and not TestConfig.is_performance_test_enabled():
            item.add_marker(pytest.mark.skip(reason="Performance tests disabled"))
        
        # Skip real-time tests if websockets not available
        if "realtime" in item.keywords and not REALTIME_AVAILABLE:
            item.add_marker(pytest.mark.skip(reason="websockets not available"))


# ============================================================================
# CLIENT FIXTURES
# ============================================================================

@pytest.fixture
def test_credentials():
    """Provide test credentials."""
    return TestConfig.get_test_credentials()


@pytest.fixture
def mock_kiwoom_client(test_credentials):
    """Create a mocked KiwoomClient for unit tests."""
    client = KiwoomClient(
        access_token=test_credentials["access_token"],
        is_production=False
    )
    return client


@pytest.fixture
def kiwoom_api_client(mock_kiwoom_client):
    """Create a KiwoomAPI client for testing."""
    return KiwoomAPI(mock_kiwoom_client)


@pytest.fixture
def integration_client():
    """Create a real client for integration tests using mock credentials."""
    if not TestConfig.is_integration_test_enabled():
        pytest.skip("Integration tests disabled - set RUN_INTEGRATION_TESTS=true")
    
    # Use real mock credentials
    mock_credentials = TestConfig.get_mock_credentials()
    
    if not mock_credentials["app_key"] or not mock_credentials["secret_key"]:
        pytest.skip("Mock credentials not available - set MOCK_KIWOOM_APPKEY and MOCK_KIWOOM_SECRETKEY")
    
    try:
        # Create client with credentials (this will get a real token)
        return KiwoomClient.create_with_credentials(
            appkey=mock_credentials["app_key"],
            secretkey=mock_credentials["secret_key"],
            is_production=False  # Use sandbox environment
        )
    except Exception as e:
        pytest.skip(f"Failed to create integration client: {e}")


@pytest.fixture
def mock_realtime_client():
    """Create a mocked realtime client for unit tests."""
    if not REALTIME_AVAILABLE:
        pytest.skip("websockets not available")
    
    client = KiwoomRealtimeClient(
        access_token=TestConfig.DEFAULT_ACCESS_TOKEN,
        is_production=False
    )
    return client


@pytest.fixture
def integration_realtime_client():
    """Create a real realtime client for integration tests."""
    if not REALTIME_AVAILABLE:
        pytest.skip("websockets not available")
    
    if not TestConfig.is_integration_test_enabled():
        pytest.skip("Integration tests disabled")
    
    access_token = os.getenv("KIWOOM_ACCESS_TOKEN")
    if not access_token:
        pytest.skip("Real access token not available")
    
    return KiwoomRealtimeClient(
        access_token=access_token,
        is_production=False
    )


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================

@pytest.fixture
def mock_data_generator():
    """Provide mock data generator."""
    return MockDataGenerator()


@pytest.fixture
def sample_stock_quote():
    """Provide sample stock quote data."""
    return MockDataGenerator.create_stock_quote_response()


@pytest.fixture
def sample_etf_info():
    """Provide sample ETF info data."""
    return MockDataGenerator.create_etf_info_response()


@pytest.fixture
def sample_elw_info():
    """Provide sample ELW info data."""
    return MockDataGenerator.create_elw_info_response()


@pytest.fixture
def sample_realtime_data():
    """Provide sample real-time data."""
    return MockDataGenerator.create_realtime_stock_data()


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def temp_directory():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_responses():
    """Provide responses mock for HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for real-time testing."""
    if not REALTIME_AVAILABLE:
        pytest.skip("websockets not available")
    
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws


# ============================================================================
# ASSET-SPECIFIC FIXTURES
# ============================================================================

@pytest.fixture
def test_stock(kiwoom_api_client):
    """Create a test Stock instance."""
    return Stock(kiwoom_api_client._client, TestConfig.TEST_STOCK_SYMBOLS[0])


@pytest.fixture
def test_etf(kiwoom_api_client):
    """Create a test ETF instance."""
    return ETF(kiwoom_api_client._client, TestConfig.TEST_ETF_SYMBOLS[0])


@pytest.fixture
def test_elw(kiwoom_api_client):
    """Create a test ELW instance."""
    return ELW(kiwoom_api_client._client, TestConfig.TEST_ELW_SYMBOLS[0])


@pytest.fixture
def test_account(kiwoom_api_client, test_credentials):
    """Create a test Account instance."""
    return Account(kiwoom_api_client._client, test_credentials["account_number"])


# ============================================================================
# PERFORMANCE TESTING FIXTURES
# ============================================================================

@pytest.fixture
def performance_metrics():
    """Track performance metrics during tests."""
    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.metrics = {}
        
        def start(self):
            self.start_time = datetime.now()
        
        def end(self):
            self.end_time = datetime.now()
            return self.duration
        
        @property
        def duration(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time).total_seconds()
            return None
        
        def add_metric(self, name: str, value: float):
            self.metrics[name] = value
        
        def get_metrics(self):
            metrics = self.metrics.copy()
            if self.duration:
                metrics["total_duration"] = self.duration
            return metrics
    
    return PerformanceTracker()


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

class TestValidators:
    """Validation utilities for test assertions."""
    
    @staticmethod
    def validate_korean_stock_symbol(symbol: str) -> bool:
        """Validate Korean stock symbol format."""
        return symbol.isdigit() and len(symbol) == 6
    
    @staticmethod
    def validate_timestamp_format(timestamp: str) -> bool:
        """Validate timestamp format (HHMMSS)."""
        if len(timestamp) != 6 or not timestamp.isdigit():
            return False
        hour = int(timestamp[:2])
        minute = int(timestamp[2:4])
        second = int(timestamp[4:6])
        return 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59
    
    @staticmethod
    def validate_price_format(price: str) -> bool:
        """Validate price format (numeric string)."""
        try:
            float(price)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_api_response_structure(response: Dict[str, Any]) -> bool:
        """Validate basic API response structure."""
        required_fields = ["return_code", "return_msg"]
        return all(field in response for field in required_fields)


@pytest.fixture
def validators():
    """Provide validation utilities."""
    return TestValidators()


# ============================================================================
# ERROR SIMULATION FIXTURES
# ============================================================================

@pytest.fixture
def error_scenarios():
    """Provide common error scenarios for testing."""
    return {
        "auth_error": {
            "status_code": 401,
            "response": {"error": "Unauthorized", "message": "Invalid token"}
        },
        "rate_limit": {
            "status_code": 429,
            "response": {"error": "Rate limit exceeded", "retry_after": 60}
        },
        "server_error": {
            "status_code": 500,
            "response": {"error": "Internal server error"}
        },
        "invalid_symbol": {
            "status_code": 200,
            "response": MockDataGenerator.create_error_response(1001, "Invalid symbol")
        },
        "market_closed": {
            "status_code": 200,
            "response": MockDataGenerator.create_error_response(2001, "Market is closed")
        },
    } 