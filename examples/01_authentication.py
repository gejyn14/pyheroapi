"""
PyHero API - Authentication Example

This example demonstrates:
1. Token issuance
2. Creating client with credentials
3. Token revocation
4. Error handling for authentication
5. Sandbox mode with environment variables
"""

import os
from pyheroapi import KiwoomClient
from pyheroapi.exceptions import KiwoomAPIError

def authentication_example():
    """Comprehensive authentication example"""
    
    # 1. Get credentials from environment variables (recommended for security)
    appkey = os.getenv("KIWOOM_APPKEY", "your_app_key_here")
    secretkey = os.getenv("KIWOOM_SECRETKEY", "your_secret_key_here")
    
    if appkey == "your_app_key_here" or secretkey == "your_secret_key_here":
        print("Please set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables")
        return
    
    print("=== PyHero API Authentication Example ===\n")
    
    try:
        # 2. Issue access token
        print("1. Issuing access token...")
        token_response = KiwoomClient.issue_token(
            appkey=appkey,
            secretkey=secretkey,
            is_production=False  # SANDBOX MODE: set is_production=False explicitly
        )
        
        print(f"✓ Token issued successfully")
        print(f"  Token Type: {token_response.token_type}")
        print(f"  Expires: {token_response.expires_dt}")
        print(f"  Token: {token_response.token[:20]}...")
        
        # 3. Create client with access token
        print("\n2. Creating client with access token...")
        client = KiwoomClient(
            access_token=token_response.token,
            is_production=False,  # SANDBOX MODE: set is_production=False explicitly
            timeout=30,
            retry_attempts=3
        )
        print("✓ Client created successfully")
        
        # 4. Alternative: Create client directly with credentials
        print("\n3. Creating client with credentials (auto-token)...")
        auto_client = KiwoomClient.create_with_credentials(
            appkey=appkey,
            secretkey=secretkey,
            is_production=False  # SANDBOX MODE: set is_production=False explicitly
        )
        print("✓ Auto-client created successfully")
        
        # 5. Test API call to verify authentication
        print("\n4. Testing API authentication...")
        try:
            # Get account balance as a test
            balance = auto_client.get_deposit_details()
            print("✓ Authentication verified - API call successful")
        except Exception as e:
            print(f"⚠ API call failed (might be expected in sandbox): {e}")
        
        # 6. Revoke token when done
        print("\n5. Revoking access token...")
        revoke_response = KiwoomClient.revoke_token(
            appkey=appkey,
            secretkey=secretkey,
            token=token_response.token,
            is_production=False  # SANDBOX MODE: set is_production=False explicitly
        )
        print("✓ Token revoked successfully")
        
        # 7. Alternative revocation using client instance
        print("\n6. Alternative token revocation...")
        try:
            client.revoke_current_token(appkey, secretkey)
            print("✓ Alternative revocation successful")
        except Exception as e:
            print(f"⚠ Alternative revocation failed: {e}")
            
    except KiwoomAuthError as e:
        print(f"❌ Authentication error: {e}")
    except KiwoomAPIError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def sandbox_environment_variables_example():
    """Example demonstrating sandbox environment variables"""
    
    print("\n=== Sandbox Environment Variables Example ===\n")
    
    # Check for sandbox environment variables
    mock_appkey = os.getenv("KIWOOM_MOCK_APPKEY")
    mock_secretkey = os.getenv("KIWOOM_MOCK_SECRETKEY")
    
    print("1. Checking sandbox environment variables...")
    if mock_appkey and mock_secretkey:
        print("✓ KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY are set")
        print(f"  Mock App Key: {'*' * 10}...{mock_appkey[-4:]}")
        print(f"  Mock Secret Key: {'*' * 10}...{mock_secretkey[-4:]}")
        
        print("\n2. Creating client with sandbox environment variables...")
        try:
            # When is_production=False, the client will automatically use
            # KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY if they are set
            client = KiwoomClient.create_with_credentials(
                appkey="dummy_appkey",  # This will be ignored in favor of KIWOOM_MOCK_APPKEY
                secretkey="dummy_secretkey",  # This will be ignored in favor of KIWOOM_MOCK_SECRETKEY
                is_production=False  # SANDBOX MODE: set is_production=False explicitly
            )
            print("✓ Client created successfully using sandbox environment variables")
            print(f"  Base URL: {client.base_url}")
            print(f"  Production Mode: {client.is_production}")
            
        except Exception as e:
            print(f"❌ Failed to create client: {e}")
    else:
        print("⚠ KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY are not set")
        print("  To use sandbox environment variables, set:")
        print("  export KIWOOM_MOCK_APPKEY='your_mock_app_key'")
        print("  export KIWOOM_MOCK_SECRETKEY='your_mock_secret_key'")
        print("  Then run with is_production=False")


def production_vs_sandbox():
    """Example showing production vs sandbox usage"""
    
    print("\n=== Production vs Sandbox Configuration ===\n")
    
    appkey = os.getenv("KIWOOM_APPKEY", "your_app_key_here")
    secretkey = os.getenv("KIWOOM_SECRETKEY", "your_secret_key_here")
    
    # Sandbox client (for testing)
    print("1. Sandbox Client Configuration:")
    try:
        sandbox_client = KiwoomClient.create_with_credentials(
            appkey=appkey,
            secretkey=secretkey,
            is_production=False,  # SANDBOX MODE: set is_production=False explicitly
            timeout=30,
            retry_attempts=3,
            rate_limit_delay=0.1
        )
        print("✓ Sandbox client created")
        print(f"  Base URL: {sandbox_client.SANDBOX_URL}")
    except Exception as e:
        print(f"✗ Sandbox client error: {e}")
    
    # Production client (for live trading)
    print("\n2. Production Client Configuration:")
    try:
        production_client = KiwoomClient.create_with_credentials(
            appkey=appkey,
            secretkey=secretkey,
            is_production=True,   # Production
            timeout=60,           # Longer timeout for production
            retry_attempts=5,     # More retries for production
            rate_limit_delay=0.2  # More conservative rate limiting
        )
        print("✓ Production client created")
        print(f"  Base URL: {production_client.PRODUCTION_URL}")
        print("⚠ WARNING: This is live trading environment!")
    except Exception as e:
        print(f"✗ Production client error: {e}")


if __name__ == "__main__":
    authentication_example()
    sandbox_environment_variables_example()
    production_vs_sandbox()
    
    print("\n=== Authentication Best Practices ===")
    print("1. Always use environment variables for credentials")
    print("2. Start with sandbox environment for testing")
    print("3. Use KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY for sandbox mode")
    print("4. Implement proper error handling")
    print("5. Revoke tokens when done")
    print("6. Use appropriate timeouts and retry settings")
    print("7. Be careful with production environment!") 