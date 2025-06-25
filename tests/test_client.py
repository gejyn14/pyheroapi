"""
Unit tests for KiwoomClient.
"""

from unittest.mock import Mock, patch

import pytest
import responses

from pyheroapi import (
    KiwoomAPIError,
    KiwoomAuthError,
    KiwoomClient,
    KiwoomRequestError,
    TokenResponse,
    TokenRevokeResponse,
)


class TestKiwoomClient:
    """Test cases for KiwoomClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.access_token = "test_token"
        # SANDBOX MODE: set is_production=False explicitly
        self.client = KiwoomClient(access_token=self.access_token, is_production=False)

    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.access_token == self.access_token
        assert self.client.base_url == KiwoomClient.SANDBOX_URL
        assert "Bearer test_token" in self.client.session.headers["Authorization"]

    def test_production_url(self):
        """Test production URL selection."""
        prod_client = KiwoomClient(access_token=self.access_token, is_production=True)
        assert prod_client.base_url == KiwoomClient.PRODUCTION_URL

    @responses.activate
    def test_successful_request(self):
        """Test successful API request."""
        # Mock successful response
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/api/dostk/mrkcond",
            json={
                "return_code": 0,
                "return_msg": "Success",
                "bid_req_base_tm": "162000",
                "sel_fpr_bid": "70000",
                "buy_fpr_bid": "69900",
            },
            status=200,
        )

        result = self.client._make_request(
            "/api/dostk/mrkcond", "ka10004", {"stk_cd": "005930"}
        )

        assert result["return_code"] == 0
        assert result["return_msg"] == "Success"

    @responses.activate
    def test_auth_error(self):
        """Test authentication error handling."""
        responses.add(
            responses.POST, f"{KiwoomClient.SANDBOX_URL}/api/dostk/mrkcond", status=401
        )

        with pytest.raises(KiwoomAuthError):
            self.client._make_request("/api/dostk/mrkcond", "ka10004")

    @responses.activate
    def test_api_error_response(self):
        """Test API error response handling."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/api/dostk/mrkcond",
            json={"return_code": 1001, "return_msg": "Invalid symbol"},
            status=200,
        )

        with pytest.raises(KiwoomRequestError) as exc_info:
            self.client._make_request("/api/dostk/mrkcond", "ka10004")

        assert "1001" in str(exc_info.value)
        assert "Invalid symbol" in str(exc_info.value)

    @responses.activate
    def test_get_quote(self):
        """Test get_quote method."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/api/dostk/mrkcond",
            json={
                "return_code": 0,
                "return_msg": "Success",
                "bid_req_base_tm": "162000",
                "sel_fpr_bid": "70000",
                "buy_fpr_bid": "69900",
                "tot_sel_req": "1000",
                "tot_buy_req": "2000",
            },
            status=200,
        )

        quote = self.client.get_quote("005930")

        assert quote.bid_req_base_tm == "162000"
        assert quote.tot_sel_req == "1000"
        assert quote.tot_buy_req == "2000"

    @responses.activate
    def test_get_etf_info(self):
        """Test get_etf_info method."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/api/dostk/etf",
            json={
                "return_code": 0,
                "return_msg": "Success",
                "stk_nm": "KODEX 200",
                "nav": "25000.50",
                "trace_eor_rt": "0.05",
            },
            status=200,
        )

        etf = self.client.get_etf_info("069500")

        assert etf.symbol == "069500"
        assert etf.name == "KODEX 200"
        assert etf.nav == "25000.50"
        assert etf.tracking_error == "0.05"

    @responses.activate
    def test_get_elw_info(self):
        """Test get_elw_info method."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/api/dostk/elw",
            json={
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
            },
            status=200,
        )

        elw = self.client.get_elw_info("57JBHH")

        assert elw.symbol == "57JBHH"
        assert elw.underlying_asset == "KOSPI200"
        assert elw.strike_price == "400.00"
        assert elw.expiry_date == "20241216"
        assert elw.delta == "0.5"

    def test_request_headers(self):
        """Test request headers are set correctly."""
        headers = self.client.session.headers

        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {self.access_token}"
        assert headers["Content-Type"] == "application/json;charset=UTF-8"

    @patch("time.sleep")
    @responses.activate
    def test_retry_mechanism(self, mock_sleep):
        """Test retry mechanism on failure."""
        # First call fails, second succeeds
        responses.add(
            responses.POST, f"{KiwoomClient.SANDBOX_URL}/api/dostk/mrkcond", status=500
        )
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/api/dostk/mrkcond",
            json={"return_code": 0, "return_msg": "Success"},
            status=200,
        )

        result = self.client._make_request("/api/dostk/mrkcond", "ka10004")

        assert result["return_code"] == 0
        assert mock_sleep.called  # Verify retry delay was used


class TestErrorHandling:
    """Test error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = KiwoomClient(access_token="test_token")

    @responses.activate
    def test_invalid_json_response(self):
        """Test handling of invalid JSON responses."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/api/dostk/mrkcond",
            body="Invalid JSON",
            status=200,
        )

        with pytest.raises(KiwoomAPIError) as exc_info:
            self.client._make_request("/api/dostk/mrkcond", "ka10004")

        assert "Invalid JSON response" in str(exc_info.value)

    @responses.activate
    def test_rate_limit_error(self):
        """Test rate limit error handling."""
        responses.add(
            responses.POST, f"{KiwoomClient.SANDBOX_URL}/api/dostk/mrkcond", status=429
        )

        with pytest.raises(
            KiwoomAPIError
        ):  # Should be converted to generic error after retries
            self.client._make_request("/api/dostk/mrkcond", "ka10004")


class TestTokenManagement:
    """Test cases for token management functionality."""

    @responses.activate
    def test_issue_token_success(self):
        """Test successful token issuance."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/oauth2/token",
            json={
                "return_code": 0,
                "return_msg": "정상적으로 처리되었습니다",
                "expires_dt": "20241107083713",
                "token_type": "bearer",
                "token": "WQJCwyqInphKnR3bSRtB9NE1lv...",
            },
            status=200,
        )

        token_response = KiwoomClient.issue_token(
            appkey="test_app_key", secretkey="test_secret_key", is_production=False
        )

        assert isinstance(token_response, TokenResponse)
        assert token_response.token_type == "bearer"
        assert token_response.expires_dt == "20241107083713"
        assert token_response.token == "WQJCwyqInphKnR3bSRtB9NE1lv..."

    @responses.activate
    def test_issue_token_failure(self):
        """Test token issuance failure."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/oauth2/token",
            json={"return_code": 1001, "return_msg": "Invalid credentials"},
            status=200,
        )

        with pytest.raises(KiwoomAuthError) as exc_info:
            KiwoomClient.issue_token(
                appkey="invalid_key", secretkey="invalid_secret", is_production=False
            )

        assert "Invalid credentials" in str(exc_info.value)

    @responses.activate
    def test_revoke_token_success(self):
        """Test successful token revocation."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/oauth2/revoke",
            json={"return_code": 0, "return_msg": "정상적으로 처리되었습니다"},
            status=200,
        )

        revoke_response = KiwoomClient.revoke_token(
            appkey="test_app_key",
            secretkey="test_secret_key",
            token="test_token",
            is_production=False,
        )

        assert isinstance(revoke_response, TokenRevokeResponse)
        assert revoke_response.return_code == 0
        assert revoke_response.return_msg == "정상적으로 처리되었습니다"

    @responses.activate
    def test_create_with_credentials(self):
        """Test client creation with credentials."""
        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/oauth2/token",
            json={
                "return_code": 0,
                "return_msg": "정상적으로 처리되었습니다",
                "expires_dt": "20241107083713",
                "token_type": "bearer",
                "token": "auto_generated_token",
            },
            status=200,
        )

        client = KiwoomClient.create_with_credentials(
            appkey="test_app_key", secretkey="test_secret_key", is_production=False
        )

        assert client.access_token == "auto_generated_token"
        assert client.base_url == KiwoomClient.SANDBOX_URL

    @responses.activate
    def test_revoke_current_token(self):
        """Test revoking current token."""
        client = KiwoomClient(access_token="current_token", is_production=False)

        responses.add(
            responses.POST,
            f"{KiwoomClient.SANDBOX_URL}/oauth2/revoke",
            json={"return_code": 0, "return_msg": "정상적으로 처리되었습니다"},
            status=200,
        )

        revoke_response = client.revoke_current_token(
            appkey="test_app_key", secretkey="test_secret_key"
        )

        assert revoke_response.return_code == 0

    @responses.activate
    def test_token_http_error(self):
        """Test token operations with HTTP errors."""
        responses.add(
            responses.POST, f"{KiwoomClient.SANDBOX_URL}/oauth2/token", status=401
        )

        with pytest.raises(KiwoomAuthError):
            KiwoomClient.issue_token(
                appkey="test_key", secretkey="test_secret", is_production=False
            )
