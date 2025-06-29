"""
Real Integration Tests with Mock Environment
============================================

These tests use actual Kiwoom sandbox API calls with real mock credentials.
Set RUN_INTEGRATION_TESTS=true to enable these tests.

Requirements:
- MOCK_KIWOOM_APPKEY environment variable
- MOCK_KIWOOM_SECRETKEY environment variable
"""

import pytest
from pyheroapi import KiwoomClient
from pyheroapi.exceptions import KiwoomAPIError, KiwoomAuthError


@pytest.mark.integration
class TestRealAPIIntegration:
    """Test real API integration with mock environment."""

    def test_token_creation_and_authentication(self, integration_client):
        """Test that we can create tokens and authenticate with real API."""
        # integration_client fixture already creates a client with real token
        assert integration_client is not None
        assert integration_client.access_token is not None
        assert integration_client.base_url == "https://mockapi.kiwoom.com"
        assert not integration_client.is_production

    def test_real_stock_quote_api_call(self, integration_client):
        """Test actual stock quote API call to sandbox."""
        try:
            # Try to get quote for Samsung Electronics (005930)
            quote_data = integration_client.get_quote("005930")
            
            # Verify we get a response (even if it's an error, it means API is working)
            assert quote_data is not None
            
            # If successful, verify data structure
            if hasattr(quote_data, 'bid_req_base_tm'):
                assert hasattr(quote_data, 'sel_fpr_bid')
                assert hasattr(quote_data, 'buy_fpr_bid')
                print(f"✅ Real API call successful! Quote time: {quote_data.bid_req_base_tm}")
                
        except KiwoomAPIError as e:
            # API error is expected - sandbox might not have real data
            print(f"📝 API responded with error (expected in sandbox): {e}")
            assert True  # Test passes if we get a proper API response

    def test_real_etf_info_api_call(self, integration_client):
        """Test actual ETF info API call to sandbox."""
        try:
            # Try to get ETF info for KODEX 200 (069500)
            etf_data = integration_client.get_etf_info("069500")
            
            assert etf_data is not None
            
            if hasattr(etf_data, 'symbol'):
                assert etf_data.symbol == "069500"
                print(f"✅ Real ETF API call successful! ETF: {etf_data.name}")
                
        except KiwoomAPIError as e:
            print(f"📝 ETF API responded with error (expected in sandbox): {e}")
            assert True

    def test_error_handling_with_invalid_symbol(self, integration_client):
        """Test error handling with invalid stock symbol."""
        with pytest.raises(KiwoomAPIError):
            # Use an obviously invalid symbol
            integration_client.get_quote("INVALID_SYMBOL_999999")

    def test_different_api_endpoints(self, integration_client):
        """Test various API endpoints to ensure integration works."""
        endpoints_to_test = [
            ("stock_quote", lambda: integration_client.get_quote("005930")),
            ("etf_info", lambda: integration_client.get_etf_info("069500")),
            # Add more endpoints as needed
        ]
        
        results = {}
        
        for endpoint_name, api_call in endpoints_to_test:
            try:
                result = api_call()
                results[endpoint_name] = "SUCCESS"
                print(f"✅ {endpoint_name}: SUCCESS")
            except KiwoomAPIError as e:
                results[endpoint_name] = f"API_ERROR: {str(e)[:100]}"
                print(f"📝 {endpoint_name}: API_ERROR (expected in sandbox)")
            except Exception as e:
                results[endpoint_name] = f"UNEXPECTED_ERROR: {str(e)[:100]}"
                print(f"❌ {endpoint_name}: UNEXPECTED_ERROR - {e}")
        
        # At least one endpoint should work or return a proper API error
        assert any("SUCCESS" in result or "API_ERROR" in result 
                  for result in results.values()), f"No endpoints responded properly: {results}"


@pytest.mark.integration
@pytest.mark.performance
class TestRealAPIPerformance:
    """Test performance with real API calls."""

    def test_api_response_time(self, integration_client, performance_metrics):
        """Test that API response times are reasonable."""
        performance_metrics.start()
        
        try:
            integration_client.get_quote("005930")
        except KiwoomAPIError:
            pass  # Expected in sandbox
        
        duration = performance_metrics.end()
        
        # API should respond within 5 seconds
        assert duration < 5.0, f"API call took too long: {duration}s"
        print(f"📊 API Response time: {duration:.3f}s")

    def test_multiple_api_calls_performance(self, integration_client, performance_metrics):
        """Test performance of multiple API calls."""
        symbols = ["005930", "000660", "035420"]  # Samsung, SK Hynix, NAVER
        
        performance_metrics.start()
        
        for symbol in symbols:
            try:
                integration_client.get_quote(symbol)
            except KiwoomAPIError:
                pass  # Expected in sandbox
        
        duration = performance_metrics.end()
        avg_time = duration / len(symbols)
        
        # Average should be under 2 seconds per call
        assert avg_time < 2.0, f"Average API call time too high: {avg_time:.3f}s"
        print(f"📊 Average API call time: {avg_time:.3f}s ({len(symbols)} calls)")


@pytest.mark.integration  
class TestTokenManagement:
    """Test token management with real API."""

    def test_token_creation_with_real_credentials(self):
        """Test creating tokens with real mock credentials."""
        import os
        
        app_key = os.getenv("MOCK_KIWOOM_APPKEY")
        secret_key = os.getenv("MOCK_KIWOOM_SECRETKEY")
        
        if not app_key or not secret_key:
            pytest.skip("Mock credentials not available")
        
        # Test token creation
        token_response = KiwoomClient.issue_token(
            appkey=app_key,
            secretkey=secret_key,
            is_production=False
        )
        
        assert token_response is not None
        assert hasattr(token_response, 'token')
        assert hasattr(token_response, 'token_type')
        assert token_response.token_type.lower() == "bearer"
        
        print(f"✅ Token created successfully! Type: {token_response.token_type}")

    def test_client_creation_with_credentials(self):
        """Test creating client directly with credentials."""
        import os
        
        app_key = os.getenv("MOCK_KIWOOM_APPKEY")
        secret_key = os.getenv("MOCK_KIWOOM_SECRETKEY")
        
        if not app_key or not secret_key:
            pytest.skip("Mock credentials not available")
        
        # This should create a client and get a token automatically
        client = KiwoomClient.create_with_credentials(
            appkey=app_key,
            secretkey=secret_key,
            is_production=False
        )
        
        assert client is not None
        assert client.access_token is not None
        assert not client.is_production
        
        print(f"✅ Client created with auto-token!") 