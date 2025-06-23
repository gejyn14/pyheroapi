#!/usr/bin/env python3
"""
Token Management Example

This example demonstrates how to:
1. Issue access tokens using app credentials
2. Use tokens with the Kiwoom API client
3. Revoke tokens when done

Based on the Kiwoom API documentation for OAuth authentication.
"""

import os
from pyheroapi import KiwoomClient, TokenRequest, TokenResponse, TokenRevokeRequest

def token_management_example():
    """Demonstrate token issuance and revocation."""
    
    # You would get these from environment variables or secure storage
    # These are dummy values - replace with your actual credentials
    appkey = os.getenv("KIWOOM_APP_KEY", "AxserEsdcredca.....")
    secretkey = os.getenv("KIWOOM_SECRET_KEY", "SEefdcwcforehDre2fdvc....")
    
    print("=== Kiwoom API Token Management Example ===\n")
    
    # Method 1: Issue token manually then create client
    print("1. Manual Token Issuance")
    print("-" * 30)
    
    try:
        # Issue a new access token (au10001)
        print("Issuing access token...")
        token_response = KiwoomClient.issue_token(
            appkey=appkey,
            secretkey=secretkey,
            is_production=False  # Use sandbox for testing
        )
        
        print(f"✓ Token issued successfully!")
        print(f"  Token Type: {token_response.token_type}")
        print(f"  Expires: {token_response.expires_dt}")
        print(f"  Token: {token_response.token[:20]}...")
        
        # Create client with the issued token
        client = KiwoomClient(
            access_token=token_response.token,
            is_production=False
        )
        
        print("✓ Client created with issued token\n")
        
    except Exception as e:
        print(f"✗ Token issuance failed: {e}\n")
        return
    
    # Method 2: Create client with automatic token issuance
    print("2. Automatic Token Issuance")
    print("-" * 30)
    
    try:
        # Create client that automatically issues token
        auto_client = KiwoomClient.create_with_credentials(
            appkey=appkey,
            secretkey=secretkey,
            is_production=False
        )
        
        print("✓ Client created with automatic token issuance\n")
        
    except Exception as e:
        print(f"✗ Automatic client creation failed: {e}\n")
    
    # Method 3: Use the client for API calls
    print("3. Using Client for API Calls")
    print("-" * 30)
    
    try:
        # Example API call - get quote data
        # Note: This would need a valid stock symbol
        # quote = client.get_quote("005930")  # Samsung Electronics
        # print(f"✓ Successfully retrieved quote data")
        
        print("✓ Client is ready for API calls")
        print("  (Actual API calls would go here)\n")
        
    except Exception as e:
        print(f"✗ API call failed: {e}\n")
    
    # Method 4: Token revocation
    print("4. Token Revocation")
    print("-" * 30)
    
    try:
        # Revoke the current token (au10002)
        print("Revoking access token...")
        revoke_response = client.revoke_current_token(
            appkey=appkey,
            secretkey=secretkey
        )
        
        print("✓ Token revoked successfully!")
        print(f"  Response: {revoke_response.return_msg}\n")
        
    except Exception as e:
        print(f"✗ Token revocation failed: {e}\n")
    
    # Method 5: Manual token revocation
    print("5. Manual Token Revocation")
    print("-" * 30)
    
    try:
        # Issue another token to revoke
        new_token = KiwoomClient.issue_token(appkey, secretkey, False)
        
        # Revoke it manually
        KiwoomClient.revoke_token(
            appkey=appkey,
            secretkey=secretkey,
            token=new_token.token,
            is_production=False
        )
        
        print("✓ Manual token revocation successful!\n")
        
    except Exception as e:
        print(f"✗ Manual token revocation failed: {e}\n")


def token_lifecycle_example():
    """Demonstrate complete token lifecycle."""
    
    print("=== Token Lifecycle Example ===\n")
    
    appkey = os.getenv("KIWOOM_APP_KEY", "AxserEsdcredca.....")
    secretkey = os.getenv("KIWOOM_SECRET_KEY", "SEefdcwcforehDre2fdvc....")
    
    try:
        # 1. Issue token
        print("Step 1: Issuing token...")
        token_response = KiwoomClient.issue_token(appkey, secretkey, False)
        print(f"✓ Token issued, expires: {token_response.expires_dt}")
        
        # 2. Use token
        print("Step 2: Creating client with token...")
        with KiwoomClient(token_response.token, is_production=False) as client:
            print("✓ Client created and ready for use")
            
            # Simulate some API usage
            print("Step 3: Using client for API calls...")
            # This is where you would make actual API calls
            print("✓ API calls completed")
        
        # 3. Clean up - revoke token  
        print("Step 4: Cleaning up - revoking token...")
        KiwoomClient.revoke_token(appkey, secretkey, token_response.token, False)
        print("✓ Token revoked successfully")
        
    except Exception as e:
        print(f"✗ Error in token lifecycle: {e}")


def usage_patterns():
    """Show different usage patterns for token management."""
    
    print("=== Token Usage Patterns ===\n")
    
    appkey = os.getenv("KIWOOM_APP_KEY", "AxserEsdcredca.....")
    secretkey = os.getenv("KIWOOM_SECRET_KEY", "SEefdcwcforehDre2fdvc....")
    
    # Pattern 1: Long-running application
    print("Pattern 1: Long-running Application")
    print("-" * 40)
    
    try:
        client = KiwoomClient.create_with_credentials(appkey, secretkey, False)
        
        # In a real application, you might:
        # 1. Check token expiration periodically
        # 2. Refresh token before it expires
        # 3. Handle token expiration gracefully
        
        print("✓ Client created for long-running app")
        print("  - Monitor token expiration")
        print("  - Refresh before expiry")
        print("  - Handle auth errors gracefully\n")
        
    except Exception as e:
        print(f"✗ Long-running app setup failed: {e}\n")
    
    # Pattern 2: Short-lived script
    print("Pattern 2: Short-lived Script")
    print("-" * 40)
    
    try:
        # Issue token, use it, then revoke immediately
        token = KiwoomClient.issue_token(appkey, secretkey, False)
        client = KiwoomClient(token.token, False)
        
        # Do your work here
        print("✓ Quick script pattern")
        print("  - Issue token at start")
        print("  - Use for API calls")
        print("  - Revoke at exit")
        
        # Clean up
        client.revoke_current_token(appkey, secretkey)
        print("  ✓ Token revoked\n")
        
    except Exception as e:
        print(f"✗ Short-lived script failed: {e}\n")


if __name__ == "__main__":
    # Set up credentials (you would use environment variables or secure storage)
    print("Note: Make sure to set KIWOOM_APP_KEY and KIWOOM_SECRET_KEY environment variables")
    print("or update the appkey/secretkey variables with your actual credentials.\n")
    
    # Run examples
    token_management_example()
    print("\n" + "="*60 + "\n")
    
    token_lifecycle_example()
    print("\n" + "="*60 + "\n")
    
    usage_patterns()
    
    print("\n=== Example Complete ===")
    print("Remember to:")
    print("- Keep your app credentials secure")
    print("- Monitor token expiration")
    print("- Revoke tokens when done")
    print("- Use HTTPS in production") 