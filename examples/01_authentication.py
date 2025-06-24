"""
PyHero API - Authentication Example

This example demonstrates:
1. Token issuance
2. Creating client with credentials
3. Token revocation
4. Error handling for authentication
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
            is_production=False  # Use sandbox for testing
        )
        
        print(f"✓ Token issued successfully")
        print(f"  Token Type: {token_response.token_type}")
        print(f"  Expires: {token_response.expires_dt}")
        print(f"  Token: {token_response.token[:20]}...")
        
        # 3. Create client with access token
        print("\n2. Creating client with access token...")
        client = KiwoomClient(
            access_token=token_response.token,
            is_production=False,
            timeout=30,
            retry_attempts=3
        )
        print("✓ Client created successfully")
        
        # 4. Alternative: Create client directly with credentials
        print("\n3. Creating client with credentials (auto-token)...")
        auto_client = KiwoomClient.create_with_credentials(
            appkey=appkey,
            secretkey=secretkey,
            is_production=False
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
            is_production=False
        )
        print("✓ Token revoked successfully")
        
        # 7. Alternative revocation using client instance
        print("\n6. Alternative token revocation...")
        auto_client.revoke_current_token(appkey=appkey, secretkey=secretkey)
        print("✓ Current token revoked successfully")
        
    except KiwoomAPIError as e:
        print(f"✗ Kiwoom API Error: {e}")
        print(f"  Return Code: {e.return_code}")
        print(f"  Return Message: {e.return_msg}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

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
            is_production=False,  # Sandbox
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
    production_vs_sandbox()
    
    print("\n=== Authentication Best Practices ===")
    print("1. Always use environment variables for credentials")
    print("2. Start with sandbox environment for testing")
    print("3. Implement proper error handling")
    print("4. Revoke tokens when done")
    print("5. Use appropriate timeouts and retry settings")
    print("6. Be careful with production environment!") 