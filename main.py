#!/usr/bin/env python3
"""
Simple CLI interface for testing Kiwoom API client.
"""

import os
import sys
from kiwoom_api import KiwoomClient, KiwoomAPIError


def main():
    """Main CLI function."""
    print("🚀 Kiwoom API Client CLI")
    print("=" * 30)
    
    # Check for access token
    access_token = os.getenv("KIWOOM_ACCESS_TOKEN")
    if not access_token:
        print("❌ Please set KIWOOM_ACCESS_TOKEN environment variable")
        print("   export KIWOOM_ACCESS_TOKEN='your_token_here'")
        return 1
    
    # Initialize client
    try:
        client = KiwoomClient(
            access_token=access_token,
            is_production=False  # Always use sandbox for CLI testing
        )
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return 1
    
    # Simple interactive menu
    while True:
        print("\n📋 Available commands:")
        print("1. Get stock quote (Samsung Electronics)")
        print("2. Get ETF info (KODEX 200)")
        print("3. Get ELW info")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
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
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
