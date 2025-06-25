"""
Tests for the easy API wrapper.
"""

from unittest.mock import Mock, patch

import pytest

from pyheroapi import ELW, ETF, Account, KiwoomAPI, Stock, connect
from pyheroapi.exceptions import KiwoomAPIError


class TestEasyAPI:
    """Test the easy API interface."""

    def test_imports(self):
        """Test that all easy API components can be imported."""
        # This test ensures the basic structure works
        assert KiwoomAPI is not None
        assert Stock is not None
        assert ETF is not None
        assert ELW is not None
        assert Account is not None
        assert connect is not None

    @patch("pyheroapi.easy_api.KiwoomClient.create_with_credentials")
    def test_connect_function(self, mock_create):
        """Test the connect convenience function."""
        mock_client = Mock()
        mock_create.return_value = mock_client

        api = connect("test_key", "test_secret", sandbox=True)

        assert isinstance(api, KiwoomAPI)
        mock_create.assert_called_once_with(
            appkey="test_key",
            secretkey="test_secret",
            is_production=False,  # SANDBOX MODE: set is_production=False explicitly
            retry_attempts=3,
            rate_limit_delay=0.1,
        )

    @patch("pyheroapi.easy_api.KiwoomClient.create_with_credentials")
    def test_pyheroapi_connect(self, mock_create):
        """Test KiwoomAPI.connect class method."""
        mock_client = Mock()
        mock_create.return_value = mock_client

        api = KiwoomAPI.connect("test_key", "test_secret", sandbox=True)

        assert isinstance(api, KiwoomAPI)
        assert hasattr(api, "_app_key")
        assert hasattr(api, "_secret_key")
        assert hasattr(api, "_sandbox")
        assert api._app_key == "test_key"
        assert api._secret_key == "test_secret"
        assert api._sandbox == True  # SANDBOX MODE: set is_production=False explicitly

    def test_stock_creation(self):
        """Test Stock object creation."""
        mock_client = Mock()
        api = KiwoomAPI(mock_client)

        stock = api.stock("005930")

        assert isinstance(stock, Stock)
        assert stock.symbol == "005930"
        assert stock._client == mock_client

    def test_etf_creation(self):
        """Test ETF object creation."""
        mock_client = Mock()
        api = KiwoomAPI(mock_client)

        etf = api.etf("069500")

        assert isinstance(etf, ETF)
        assert etf.symbol == "069500"
        assert etf._client == mock_client

    def test_elw_creation(self):
        """Test ELW object creation."""
        mock_client = Mock()
        api = KiwoomAPI(mock_client)

        elw = api.elw("57JBHH")

        assert isinstance(elw, ELW)
        assert elw.symbol == "57JBHH"
        assert elw._client == mock_client

    def test_account_creation(self):
        """Test Account object creation."""
        mock_client = Mock()
        api = KiwoomAPI(mock_client)

        account = api.account("12345678")

        assert isinstance(account, Account)
        assert account.account_number == "12345678"
        assert account._client == mock_client

    def test_context_manager(self):
        """Test that KiwoomAPI works as context manager."""
        mock_client = Mock()
        api = KiwoomAPI(mock_client)
        api._app_key = "test_key"
        api._secret_key = "test_secret"

        # Mock the disconnect method
        api.disconnect = Mock()

        with api as ctx_api:
            assert ctx_api == api

        # disconnect should be called on exit
        api.disconnect.assert_called_once()


class TestStock:
    """Test Stock wrapper class."""

    def test_stock_current_price_error_handling(self):
        """Test that Stock.current_price handles errors gracefully."""
        mock_client = Mock()
        mock_client.get_quote.side_effect = Exception("API Error")

        stock = Stock(mock_client, "005930")
        price = stock.current_price

        # Should return None instead of raising exception
        assert price is None

    def test_stock_quote_error_handling(self):
        """Test that Stock.quote handles errors gracefully."""
        mock_client = Mock()
        mock_client.get_quote.side_effect = Exception("API Error")

        stock = Stock(mock_client, "005930")
        quote = stock.quote

        # Should return error dict instead of raising exception
        assert "error" in quote
        assert quote["symbol"] == "005930"

    def test_stock_history_error_handling(self):
        """Test that Stock.history handles errors gracefully."""
        mock_client = Mock()
        mock_client.get_daily_prices.side_effect = Exception("API Error")

        stock = Stock(mock_client, "005930")
        history = stock.history(days=5)

        # Should return empty list instead of raising exception
        assert history == []


class TestETF:
    """Test ETF wrapper class."""

    def test_etf_info_error_handling(self):
        """Test that ETF.info handles errors gracefully."""
        mock_client = Mock()
        mock_client.get_etf_info.side_effect = Exception("API Error")

        etf = ETF(mock_client, "069500")
        info = etf.info

        # Should return error dict instead of raising exception
        assert "error" in info
        assert info["symbol"] == "069500"


class TestELW:
    """Test ELW wrapper class."""

    def test_elw_info_error_handling(self):
        """Test that ELW.info handles errors gracefully."""
        mock_client = Mock()
        mock_client.get_elw_info.side_effect = Exception("API Error")

        elw = ELW(mock_client, "57JBHH")
        info = elw.info

        # Should return error dict instead of raising exception
        assert "error" in info
        assert info["symbol"] == "57JBHH"

    def test_elw_greeks_error_handling(self):
        """Test that ELW.greeks handles errors gracefully."""
        mock_client = Mock()
        mock_client.get_elw_sensitivity.side_effect = Exception("API Error")

        elw = ELW(mock_client, "57JBHH")
        greeks = elw.greeks

        # Should return empty dict instead of raising exception
        assert greeks == {}


class TestAccount:
    """Test Account wrapper class."""

    def test_account_balance_error_handling(self):
        """Test that Account.balance handles errors gracefully."""
        mock_client = Mock()
        mock_client.get_account_balance.side_effect = Exception("API Error")

        account = Account(mock_client, "12345678")
        balance = account.balance

        # Should return error dict instead of raising exception
        assert "error" in balance
        assert balance["account_number"] == "12345678"

    def test_account_positions_error_handling(self):
        """Test that Account.positions handles errors gracefully."""
        mock_client = Mock()
        mock_client.get_positions.side_effect = Exception("API Error")

        account = Account(mock_client, "12345678")
        positions = account.positions

        # Should return empty list instead of raising exception
        assert positions == []
