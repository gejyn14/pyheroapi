"""
Test sandbox environment variable functionality.

This test verifies that KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY
are properly used when is_production=False.
"""

import os
import pytest
from unittest.mock import patch, Mock

from pyheroapi.client import KiwoomClient
from pyheroapi.easy_api import KiwoomAPI, connect


class TestSandboxEnvironmentVariables:
    """Test sandbox environment variable functionality."""

    def test_sandbox_environment_variables_not_set(self):
        """Test behavior when sandbox environment variables are not set."""
        # Clear any existing environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Should use provided credentials
            appkey = "test_appkey"
            secretkey = "test_secretkey"
            
            with patch.object(KiwoomClient, 'issue_token') as mock_issue_token:
                mock_response = Mock()
                mock_response.token = "test_token"
                mock_issue_token.return_value = mock_response
                
                client = KiwoomClient.create_with_credentials(
                    appkey=appkey,
                    secretkey=secretkey,
                    is_production=False
                )
                
                # Verify that the original credentials were used
                mock_issue_token.assert_called_once_with(appkey, secretkey, False)

    def test_sandbox_environment_variables_set(self):
        """Test behavior when sandbox environment variables are set."""
        # Set sandbox environment variables
        mock_appkey = "mock_appkey"
        mock_secretkey = "mock_secretkey"
        
        with patch.dict(os.environ, {
            'KIWOOM_MOCK_APPKEY': mock_appkey,
            'KIWOOM_MOCK_SECRETKEY': mock_secretkey
        }):
            # Provide dummy credentials that should be ignored
            dummy_appkey = "dummy_appkey"
            dummy_secretkey = "dummy_secretkey"
            
            with patch.object(KiwoomClient, 'issue_token') as mock_issue_token:
                mock_response = Mock()
                mock_response.token = "test_token"
                mock_issue_token.return_value = mock_response
                
                client = KiwoomClient.create_with_credentials(
                    appkey=dummy_appkey,
                    secretkey=dummy_secretkey,
                    is_production=False
                )
                
                # Verify that the mock credentials were used instead
                mock_issue_token.assert_called_once_with(mock_appkey, mock_secretkey, False)

    def test_production_mode_ignores_sandbox_variables(self):
        """Test that production mode ignores sandbox environment variables."""
        # Set sandbox environment variables
        mock_appkey = "mock_appkey"
        mock_secretkey = "mock_secretkey"
        
        with patch.dict(os.environ, {
            'KIWOOM_MOCK_APPKEY': mock_appkey,
            'KIWOOM_MOCK_SECRETKEY': mock_secretkey
        }):
            # Provide production credentials
            prod_appkey = "prod_appkey"
            prod_secretkey = "prod_secretkey"
            
            with patch.object(KiwoomClient, 'issue_token') as mock_issue_token:
                mock_response = Mock()
                mock_response.token = "test_token"
                mock_issue_token.return_value = mock_response
                
                client = KiwoomClient.create_with_credentials(
                    appkey=prod_appkey,
                    secretkey=prod_secretkey,
                    is_production=True
                )
                
                # Verify that production credentials were used (not mock)
                mock_issue_token.assert_called_once_with(prod_appkey, prod_secretkey, True)

    def test_easy_api_sandbox_environment_variables(self):
        """Test that easy API respects sandbox environment variables."""
        # Set sandbox environment variables
        mock_appkey = "mock_appkey"
        mock_secretkey = "mock_secretkey"
        
        with patch.dict(os.environ, {
            'KIWOOM_MOCK_APPKEY': mock_appkey,
            'KIWOOM_MOCK_SECRETKEY': mock_secretkey
        }):
            # Provide dummy credentials
            dummy_appkey = "dummy_appkey"
            dummy_secretkey = "dummy_secretkey"
            
            with patch.object(KiwoomClient, 'create_with_credentials') as mock_create:
                mock_client = Mock()
                mock_create.return_value = mock_client
                
                api = KiwoomAPI.connect(
                    app_key=dummy_appkey,
                    secret_key=dummy_secretkey,
                    sandbox=True
                )
                
                # Verify that the mock credentials were used
                mock_create.assert_called_once()
                call_args = mock_create.call_args
                assert call_args[1]['appkey'] == mock_appkey
                assert call_args[1]['secretkey'] == mock_secretkey
                assert call_args[1]['is_production'] == False

    def test_connect_function_sandbox_environment_variables(self):
        """Test that connect function respects sandbox environment variables."""
        # Set sandbox environment variables
        mock_appkey = "mock_appkey"
        mock_secretkey = "mock_secretkey"
        
        with patch.dict(os.environ, {
            'KIWOOM_MOCK_APPKEY': mock_appkey,
            'KIWOOM_MOCK_SECRETKEY': mock_secretkey
        }):
            # Provide dummy credentials
            dummy_appkey = "dummy_appkey"
            dummy_secretkey = "dummy_secretkey"
            
            with patch.object(KiwoomClient, 'create_with_credentials') as mock_create:
                mock_client = Mock()
                mock_create.return_value = mock_client
                
                api = connect(
                    app_key=dummy_appkey,
                    secret_key=dummy_secretkey,
                    sandbox=True
                )
                
                # Verify that the mock credentials were used
                mock_create.assert_called_once()
                call_args = mock_create.call_args
                assert call_args[1]['appkey'] == mock_appkey
                assert call_args[1]['secretkey'] == mock_secretkey
                assert call_args[1]['is_production'] == False

    def test_token_revocation_sandbox_environment_variables(self):
        """Test that token revocation respects sandbox environment variables."""
        # Set sandbox environment variables
        mock_appkey = "mock_appkey"
        mock_secretkey = "mock_secretkey"
        
        with patch.dict(os.environ, {
            'KIWOOM_MOCK_APPKEY': mock_appkey,
            'KIWOOM_MOCK_SECRETKEY': mock_secretkey
        }):
            # Provide dummy credentials
            dummy_appkey = "dummy_appkey"
            dummy_secretkey = "dummy_secretkey"
            token = "test_token"
            
            # Mock the requests.post call to avoid actual HTTP requests
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"return_code": 0, "return_msg": "success"}
                mock_post.return_value = mock_response
                
                result = KiwoomClient.revoke_token(
                    appkey=dummy_appkey,
                    secretkey=dummy_secretkey,
                    token=token,
                    is_production=False
                )
                
                # Verify that the mock credentials were used in the request
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                request_data = call_args[1]['json']
                assert request_data['appkey'] == mock_appkey
                assert request_data['secretkey'] == mock_secretkey


if __name__ == "__main__":
    pytest.main([__file__]) 