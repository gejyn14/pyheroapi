#!/usr/bin/env python3
"""
Easy Usage Example for Kiwoom API - User-Friendly Interface

This example shows how much simpler the new API is compared to the basic_usage.py.
No complex token management, minimal error handling needed, and intuitive syntax.
"""

import os
import pyheroapi


def main():
    """Demonstrate the easy-to-use API."""
    
    print("🚀 Kiwoom API - Easy Usage Example")
    print("=" * 50)
    
    # Get credentials from environment
    app_key = os.getenv("KIWOOM_APP_KEY", "your_app_key_here")
    secret_key = os.getenv("KIWOOM_SECRET_KEY", "your_secret_key_here")
    
    # Method 1: Simple connection with automatic token management
    print("🔌 Connecting to Kiwoom API...")
    
    try:
        # One-line connection - handles all the complexity!
        api = pyheroapi.connect(app_key, secret_key, sandbox=True)
        print("✅ Connected successfully!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Tip: Make sure to set your environment variables:")
        print("   export KIWOOM_APP_KEY='your_actual_app_key'")
        print("   export KIWOOM_SECRET_KEY='your_actual_secret_key'")
        return
    
    # Method 2: Context manager for automatic cleanup
    print("\n🔄 Using context manager for automatic cleanup...")
    
    with pyheroapi.connect(app_key, secret_key, sandbox=True) as api:
        
        print("\n📊 Stock Data Examples")
        print("-" * 30)
        
        # Get Samsung Electronics stock data
        samsung = api.stock("005930")
        
        # Simple property access - no complex error handling needed!
        price = samsung.current_price
        print(f"Samsung Current Price: ₩{price:,}" if price else "Samsung: Price unavailable")
        
        # Get full quote with clean data format
        quote = samsung.quote
        if 'error' not in quote:
            print(f"Best Bid: ₩{quote['best_bid']:,}" if quote['best_bid'] else "Best Bid: N/A")
            print(f"Best Ask: ₩{quote['best_ask']:,}" if quote['best_ask'] else "Best Ask: N/A")
        
        # Get historical data - returns clean list of dictionaries
        print(f"\n📈 Last 5 days of Samsung stock:")
        history = samsung.history(days=5)
        for day in history[:3]:  # Show first 3 days
            if day['close']:
                print(f"  {day['date']}: ₩{day['close']:,}")
        
        print("\n💹 ETF Data Examples")
        print("-" * 25)
        
        # Get KODEX 200 ETF data
        kodex = api.etf("069500")
        etf_info = kodex.info
        
        if 'error' not in etf_info:
            print(f"ETF Name: {etf_info['name']}")
            print(f"NAV: ₩{etf_info['nav']:,.2f}" if etf_info['nav'] else "NAV: N/A")
            print(f"Tracking Error: {etf_info['tracking_error']}%" if etf_info['tracking_error'] else "Tracking Error: N/A")
        
        print("\n⚡ ELW Data Examples")
        print("-" * 23)
        
        # Get ELW data
        elw = api.elw("57JBHH")
        elw_info = elw.info
        
        if 'error' not in elw_info:
            print(f"ELW Name: {elw_info['name']}")
            print(f"Underlying: {elw_info['underlying_asset']}")
            print(f"Strike Price: ₩{elw_info['strike_price']:,}" if elw_info['strike_price'] else "Strike: N/A")
            
            # Get Greeks easily
            greeks = elw.greeks
            if greeks:
                print(f"Delta: {greeks.get('delta', 'N/A')}")
                print(f"Gamma: {greeks.get('gamma', 'N/A')}")
        
        print("\n💰 Account Data Examples")
        print("-" * 26)
        
        # Note: Replace with actual account number for real usage
        account = api.account("12345678")  # Demo account number
        
        balance = account.balance
        if 'error' not in balance:
            print(f"Total Balance: ₩{balance['total_balance']:,}" if balance['total_balance'] else "Balance: N/A")
            print(f"Available: ₩{balance['available_balance']:,}" if balance['available_balance'] else "Available: N/A")
        else:
            print("Account data not available (demo account)")
        
        # Get positions
        positions = account.positions
        if positions:
            print(f"\nYou have {len(positions)} positions:")
            for pos in positions[:3]:  # Show first 3 positions
                print(f"  {pos['name']}: {pos['quantity']} shares")
        else:
            print("No positions found (or demo account)")
        
        print("\n🔍 Search Examples")
        print("-" * 18)
        
        # Search for stocks
        results = api.search_stocks("삼성", limit=3)
        if results:
            print("Search results for '삼성':")
            for result in results:
                print(f"  {result}")
        
        # Check market status
        status = api.market_status
        if 'error' not in status:
            print(f"\nMarket Status: {status}")
        
        print("\n✅ Example completed!")
        print("🔒 Connection will be automatically cleaned up")
    
    # Alternative usage without context manager
    print("\n" + "="*50)
    print("📝 Alternative Usage Patterns")
    print("="*50)
    
    # Quick one-liners for specific data
    print("\n🚀 Quick One-Liners:")
    
    try:
        # Get price in one line
        api = pyheroapi.connect(app_key, secret_key, sandbox=True)
        
        samsung_price = api.stock("005930").current_price
        print(f"Samsung price: ₩{samsung_price:,}" if samsung_price else "Samsung price: N/A")
        
        kodex_nav = api.etf("069500").info.get('nav')
        print(f"KODEX 200 NAV: ₩{kodex_nav:,.2f}" if kodex_nav else "KODEX NAV: N/A")
        
        # Clean up manually
        api.disconnect()
        
    except Exception as e:
        print(f"Quick usage failed: {e}")
    
    print("\n🎉 That's how easy it is!")
    print("\nCompare this to basic_usage.py - much simpler!")


def comparison_with_old_api():
    """Show the difference between old and new API."""
    
    print("\n" + "="*60)
    print("📊 COMPARISON: Old vs New API")
    print("="*60)
    
    print("""
OLD WAY (complex):
------------------
from pyheroapi import KiwoomClient, KiwoomAPIError, KiwoomAuthError

# Complex authentication
try:
    client = KiwoomClient.create_with_credentials(
        appkey="your_key",
        secretkey="your_secret", 
        is_production=False,
        timeout=30,
        retry_attempts=3
    )
except Exception as e:
    # Handle authentication errors
    pass

# Complex error handling for every call
try:
    quote = client.get_quote("005930")
    price = float(quote.buy_fpr_bid) if quote.buy_fpr_bid else None
    print(f"Price: {price}")
except KiwoomAuthError:
    # Handle auth error
    pass
except KiwoomAPIError as e:
    # Handle API error
    pass
except Exception as e:
    # Handle other errors
    pass

# Manual token cleanup
try:
    client.revoke_current_token(appkey, secretkey)
except Exception as e:
    pass

NEW WAY (simple):
-----------------
import pyheroapi

# One line connection
with pyheroapi.connect("your_key", "your_secret") as api:
    # Simple property access with automatic error handling
    price = api.stock("005930").current_price
    print(f"Price: ₩{price:,}" if price else "Price: N/A")
    
    # Clean data format, no complex parsing needed
    quote = api.stock("005930").quote
    # Automatic cleanup when done
""")


if __name__ == "__main__":
    main()
    comparison_with_old_api() 