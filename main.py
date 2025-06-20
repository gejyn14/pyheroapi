#!/usr/bin/env python3
"""
Interactive CLI for testing Kiwoom API functionality including token management.
"""

import os
import sys
from kiwoom_api import KiwoomClient, KiwoomAPIError, TokenResponse


def main():
    """Main CLI function."""
    print("🚀 Kiwoom API Client CLI")
    print("=" * 30)
    
    # Check for access token
    access_token = os.getenv("KIWOOM_ACCESS_TOKEN")
    appkey = os.getenv("KIWOOM_APP_KEY")
    secretkey = os.getenv("KIWOOM_SECRET_KEY")
    
    client = None
    token_generated = False
    
    if access_token:
        print("🔑 Using existing access token...")
        try:
            client = KiwoomClient(
                access_token=access_token,
                is_production=False  # Always use sandbox for CLI testing
            )
            print("✅ Client initialized with existing token")
        except Exception as e:
            print(f"❌ Failed to initialize client: {e}")
            return 1
    elif appkey and secretkey:
        print("🔑 Generating new access token from credentials...")
        try:
            client = KiwoomClient.create_with_credentials(
                appkey=appkey,
                secretkey=secretkey,
                is_production=False
            )
            token_generated = True
            print("✅ Client initialized with new token")
        except Exception as e:
            print(f"❌ Failed to generate token: {e}")
            return 1
    else:
        print("❌ Please set either:")
        print("   - KIWOOM_ACCESS_TOKEN environment variable, OR")
        print("   - Both KIWOOM_APP_KEY and KIWOOM_SECRET_KEY environment variables")
        print("   Example: export KIWOOM_APP_KEY='your_app_key'")
        print("           export KIWOOM_SECRET_KEY='your_secret_key'")
        return 1
    
    # Simple interactive menu
    while True:
        print("\n📋 Available commands:")
        print("1. Get stock quote (Samsung Electronics)")
        print("2. Get ETF info (KODEX 200)")
        print("3. Get ELW info")
        print("4. Issue new token (if credentials available)")
        print("5. Revoke current token (if generated)")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            try:
                print("📊 Getting quote for Samsung Electronics (005930)...")
                quote = client.get_quote("005930")
                print(f"✅ Quote time: {quote.bid_req_base_tm}")
                print(f"   Total sell orders: {quote.tot_sel_req}")
                print(f"   Total buy orders: {quote.tot_buy_req}")
            except KiwoomAPIError as e:
                print(f"❌ API Error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "2":
            try:
                print("💹 Getting ETF info for KODEX 200 (069500)...")
                etf = client.get_etf_info("069500")
                print(f"✅ ETF Name: {etf.name}")
                print(f"   NAV: {etf.nav}")
                print(f"   Tracking Error: {etf.tracking_error}")
            except KiwoomAPIError as e:
                print(f"❌ API Error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "3":
            try:
                print("⚡ Getting ELW info for 57JBHH...")
                elw = client.get_elw_info("57JBHH")
                print(f"✅ Underlying Asset: {elw.underlying_asset}")
                print(f"   Strike Price: {elw.strike_price}")
                print(f"   Expiry Date: {elw.expiry_date}")
                print(f"   Delta: {elw.delta}")
            except KiwoomAPIError as e:
                print(f"❌ API Error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "4":
            if appkey and secretkey:
                try:
                    print("🔑 Issuing new access token...")
                    token_response = KiwoomClient.issue_token(appkey, secretkey, False)
                    print(f"✅ New token issued!")
                    print(f"   Token Type: {token_response.token_type}")
                    print(f"   Expires: {token_response.expires_dt}")
                    print(f"   Token: {token_response.token[:20]}...")
                except Exception as e:
                    print(f"❌ Failed to issue token: {e}")
            else:
                print("❌ App credentials not available")
        
        elif choice == "5":
            if token_generated and appkey and secretkey:
                try:
                    print("🔒 Revoking current token...")
                    client.revoke_current_token(appkey, secretkey)
                    print("✅ Token revoked successfully!")
                    print("⚠️ Client will no longer work after token revocation")
                except Exception as e:
                    print(f"❌ Failed to revoke token: {e}")
            else:
                print("❌ Can only revoke auto-generated tokens")
        
        elif choice == "6":
            # Clean up - revoke token if we generated it
            if token_generated and appkey and secretkey:
                try:
                    print("🔒 Cleaning up - revoking generated token...")
                    client.revoke_current_token(appkey, secretkey)
                    print("✅ Token revoked")
                except Exception as e:
                    print(f"⚠️ Warning: Failed to revoke token: {e}")
            
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-6.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
