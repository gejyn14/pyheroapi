#!/usr/bin/env python3
"""
Basic usage example for Kiwoom API Python client.

This example demonstrates how to:
1. Initialize the client
2. Get stock quote data
3. Retrieve ETF information
4. Handle errors properly
"""

import os
from kiwoom_api import KiwoomClient, KiwoomAPIError, KiwoomAuthError


def main():
    """Main example function."""
    
    # Get API token from environment variable
    # You should set this in your environment: export KIWOOM_ACCESS_TOKEN="your_token"
    access_token = os.getenv("KIWOOM_ACCESS_TOKEN")
    
    if not access_token:
        print("Please set KIWOOM_ACCESS_TOKEN environment variable")
        return
    
    # Initialize the client (using sandbox by default)
    client = KiwoomClient(
        access_token=access_token,
        is_production=False,  # Use sandbox for testing
        timeout=30,
        retry_attempts=3
    )
    
    try:
        print("🚀 Kiwoom API Client Example")
        print("=" * 40)
        
        # Example 1: Get stock quote data
        print("\n📊 Getting stock quote for Samsung Electronics (005930)...")
        try:
            quote = client.get_quote("005930")
            print(f"Best Ask: {quote.sel_fpr_bid}")
            print(f"Best Bid: {quote.buy_fpr_bid}")
            print(f"Total Sell Quantity: {quote.tot_sel_req}")
            print(f"Total Buy Quantity: {quote.tot_buy_req}")
        except Exception as e:
            print(f"Error getting quote: {e}")
        
        # Example 2: Get ETF information
        print("\n💹 Getting ETF info for KODEX 200 (069500)...")
        try:
            etf = client.get_etf_info("069500")
            print(f"ETF Name: {etf.name}")
            print(f"NAV: {etf.nav}")
            print(f"Tracking Error: {etf.tracking_error}")
        except Exception as e:
            print(f"Error getting ETF info: {e}")
        
        # Example 3: Get ELW information
        print("\n⚡ Getting ELW info for sample ELW (57JBHH)...")
        try:
            elw = client.get_elw_info("57JBHH")
            print(f"Underlying Asset: {elw.underlying_asset}")
            print(f"Strike Price: {elw.strike_price}")
            print(f"Expiry Date: {elw.expiry_date}")
            print(f"Delta: {elw.delta}")
        except Exception as e:
            print(f"Error getting ELW info: {e}")
        
        # Example 4: Get historical data
        print("\n📈 Getting historical data...")
        try:
            daily_prices = client.get_daily_prices("005930", period="D", count=5)
            print(f"Retrieved {len(daily_prices)} days of data")
            for price_data in daily_prices[:3]:  # Show first 3 entries
                print(f"  Date: {price_data.get('date', 'N/A')}")
        except Exception as e:
            print(f"Error getting historical data: {e}")
            
        print("\n✅ Example completed successfully!")
        
    except KiwoomAuthError:
        print("❌ Authentication failed. Please check your access token.")
    except KiwoomAPIError as e:
        print(f"❌ API Error: {e}")
        if e.response_data:
            print(f"Error details: {e.response_data}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main() 