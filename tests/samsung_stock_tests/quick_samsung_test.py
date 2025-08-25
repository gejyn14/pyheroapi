#!/usr/bin/env python3
"""
Quick Samsung Stock Test

A simple script to quickly test if Samsung Electronics stock data can be retrieved.
"""

import os
import sys

# Try to import the pyheroapi
try:
    import pyheroapi
    print("✅ Successfully imported pyheroapi")
except ImportError as e:
    print(f"❌ Failed to import pyheroapi: {e}")
    print("Make sure you have pyheroapi installed or run from the project directory")
    sys.exit(1)


def quick_test():
    """Quick test of Samsung stock data retrieval."""
    
    print("🚀 Quick Samsung Stock Test")
    print("=" * 40)
    
    # Get credentials
    app_key = os.getenv("KIWOOM_APP_KEY")
    secret_key = os.getenv("KIWOOM_SECRET_KEY")
    
    # Check if credentials are provided via command line
    if len(sys.argv) >= 3:
        app_key = sys.argv[1]
        secret_key = sys.argv[2]
        print("📋 Using credentials from command line")
    elif not app_key or not secret_key:
        print("❌ No credentials found!")
        print("Usage: python quick_samsung_test.py [app_key] [secret_key]")
        print("Or set KIWOOM_APP_KEY and KIWOOM_SECRET_KEY environment variables")
        return False
    
    samsung_code = "005930"  # Samsung Electronics
    
    try:
        print(f"\n📊 Testing Samsung Electronics ({samsung_code})...")
        
        # Connect using easy API (production environment)
        print("⚠️  Using PRODUCTION environment with real market data")
        with pyheroapi.connect(app_key, secret_key, sandbox=False) as api:
            print("✅ Successfully connected to API")
            
            # Get Samsung stock object
            samsung = api.stock(samsung_code)
            print(f"✅ Created stock object for {samsung_code}")
            
            # Test current price
            price = samsung.current_price
            if price:
                print(f"📈 Current Price: ₩{price:,}")
            else:
                print("⚠️ Current price not available")
            
            # Test quote data
            quote = samsung.quote
            if "error" not in quote:
                print("✅ Successfully retrieved quote data")
                if quote.get('best_bid'):
                    print(f"💵 Best Bid: ₩{quote['best_bid']:,}")
                if quote.get('best_ask'):
                    print(f"💵 Best Ask: ₩{quote['best_ask']:,}")
            else:
                print(f"⚠️ Quote error: {quote.get('error', 'Unknown')}")
            
            # Test historical data
            history = samsung.history(days=3)
            if history:
                print(f"📅 Retrieved {len(history)} days of historical data")
                if len(history) > 0 and history[0].get('close'):
                    latest = history[0]
                    print(f"📊 Latest close: ₩{latest['close']:,} on {latest.get('date', 'N/A')}")
            else:
                print("⚠️ No historical data available")
        
        print("\n🎉 Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n✅ Samsung stock data retrieval appears to be working!")
    else:
        print("\n❌ Samsung stock data retrieval test failed.")
        sys.exit(1) 