#!/usr/bin/env python3
"""
Quick Samsung Stock Test - Production Environment

A simple script to quickly test Samsung Electronics stock data retrieval using PRODUCTION API keys.
This will retrieve real, live market data from Kiwoom Securities.
"""

import os
import sys
from datetime import datetime

# Try to import the pyheroapi
try:
    import pyheroapi
    print("✅ Successfully imported pyheroapi")
except ImportError as e:
    print(f"❌ Failed to import pyheroapi: {e}")
    print("Make sure you have pyheroapi installed or run from the project directory")
    sys.exit(1)


def production_samsung_test():
    """Production test of Samsung stock data retrieval with real market data."""
    
    print("🏭 Samsung Stock Test - PRODUCTION ENVIRONMENT")
    print("=" * 50)
    print("⚠️  WARNING: This will use REAL market data and production API limits")
    print("=" * 50)
    
    # Get credentials
    app_key = os.getenv("KIWOOM_APP_KEY")
    secret_key = os.getenv("KIWOOM_SECRET_KEY")
    
    # Check if credentials are provided via command line
    if len(sys.argv) >= 3:
        app_key = sys.argv[1]
        secret_key = sys.argv[2]
        print("📋 Using production credentials from command line")
    elif not app_key or not secret_key:
        print("❌ No production credentials found!")
        print("Usage: python quick_samsung_test_production.py [app_key] [secret_key]")
        print("Or set KIWOOM_APP_KEY and KIWOOM_SECRET_KEY environment variables")
        return False
    else:
        print("📋 Using production credentials from environment variables")
    
    samsung_code = "005930"  # Samsung Electronics
    
    # Add safety confirmation for production use
    print(f"\n🎯 About to test Samsung Electronics ({samsung_code}) using production API")
    print("   📊 This will retrieve real market data")
    print("   ⏰ Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Check if market is likely open (rough check for Korean market hours)
    current_hour = datetime.now().hour
    is_likely_market_hours = 9 <= current_hour <= 15  # Approximate KST market hours
    
    if is_likely_market_hours:
        print("   🟢 Current time suggests market may be open (9 AM - 3 PM)")
    else:
        print("   🟡 Current time suggests market may be closed")
        print("   📝 You may see previous day's closing data")
    
    try:
        print(f"\n📡 Connecting to Kiwoom PRODUCTION API...")
        
        # Connect using production environment
        with pyheroapi.connect(app_key, secret_key, sandbox=False) as api:
            print("✅ Successfully connected to PRODUCTION API")
            print("🔗 Connected to: https://api.kiwoom.com")
            
            # Get Samsung stock object
            samsung = api.stock(samsung_code)
            print(f"✅ Created stock object for Samsung Electronics ({samsung_code})")
            
            # Test current price
            print(f"\n💰 Retrieving current Samsung stock price...")
            price = samsung.current_price
            if price:
                print(f"📈 Current Price: ₩{price:,}")
                
                # Add some context about the price
                if price > 70000:
                    print("   📊 Price is above ₩70,000 (typical range)")
                elif price > 50000:
                    print("   📊 Price is in normal trading range")
                else:
                    print("   ⚠️  Price seems unusually low - please verify")
            else:
                print("⚠️ Current price not available")
                print("   This might be normal if market is closed")
            
            # Test quote data
            print(f"\n📋 Retrieving quote data (order book)...")
            quote = samsung.quote
            if "error" not in quote:
                print("✅ Successfully retrieved real-time quote data")
                
                if quote.get('best_bid'):
                    print(f"💵 Best Bid: ₩{quote['best_bid']:,}")
                else:
                    print("💵 Best Bid: Not available")
                    
                if quote.get('best_ask'):
                    print(f"💵 Best Ask: ₩{quote['best_ask']:,}")
                else:
                    print("💵 Best Ask: Not available")
                    
                # Calculate spread if both bid and ask are available
                if quote.get('best_bid') and quote.get('best_ask'):
                    spread = quote['best_ask'] - quote['best_bid']
                    spread_pct = (spread / quote['best_bid']) * 100
                    print(f"📊 Bid-Ask Spread: ₩{spread:,} ({spread_pct:.3f}%)")
                
                # Show quantities if available
                if quote.get('total_bid_quantity'):
                    print(f"📦 Total Bid Quantity: {quote['total_bid_quantity']:,} shares")
                if quote.get('total_ask_quantity'):
                    print(f"📦 Total Ask Quantity: {quote['total_ask_quantity']:,} shares")
                    
            else:
                print(f"⚠️ Quote error: {quote.get('error', 'Unknown')}")
            
            # Test historical data
            print(f"\n📅 Retrieving recent historical data...")
            history = samsung.history(days=5)
            if history:
                print(f"📊 Retrieved {len(history)} days of historical data")
                
                print("📈 Recent trading history:")
                for i, day in enumerate(history[:3]):  # Show last 3 days
                    date = day.get('date', 'N/A')
                    open_price = day.get('open')
                    close = day.get('close')
                    high = day.get('high')
                    low = day.get('low')
                    volume = day.get('volume')
                    
                    print(f"   📅 {date}:")
                    if close:
                        print(f"      Close: ₩{close:,}")
                    if open_price and close:
                        change = close - open_price
                        change_pct = (change / open_price) * 100
                        change_dir = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                        print(f"      Daily Change: {change_dir} ₩{change:,} ({change_pct:+.2f}%)")
                    if high and low:
                        print(f"      Range: ₩{low:,} - ₩{high:,}")
                    if volume:
                        print(f"      Volume: {volume:,} shares")
                    print()
                    
            else:
                print("⚠️ No historical data available")
                print("   This might happen if market data is not accessible")
            
            # Test market status if available
            print(f"🏢 Checking market status...")
            try:
                market_status = api.market_status
                if market_status and "error" not in market_status:
                    print(f"📊 Market Status: {market_status}")
                else:
                    print("ℹ️  Market status not available or accessible")
            except:
                print("ℹ️  Market status check not available")
        
        # Check if we actually got meaningful data
        if price or ("error" not in quote and quote.get('best_bid') or quote.get('best_ask')) or (history and len(history) > 0):
            print("\n🎉 Production test completed successfully!")
            print("✅ Samsung stock data retrieval is working with real market data!")
            return True
        else:
            print("\n⚠️ Production test completed but no meaningful data was retrieved")
            print("🔍 This might be due to market hours, API limitations, or data access issues")
            return False
        
    except Exception as e:
        print(f"\n❌ Production test failed with error: {e}")
        print("\n🔍 Troubleshooting tips:")
        print("   • Verify your production API credentials are correct")
        print("   • Check if your API subscription is active")
        print("   • Ensure you have permission to access stock data")
        print("   • Try again during Korean market hours (9 AM - 3 PM KST)")
        return False


def show_production_info():
    """Display important information about production testing."""
    print("\n" + "=" * 60)
    print("📋 PRODUCTION ENVIRONMENT INFORMATION")
    print("=" * 60)
    print("🏭 Environment: Kiwoom Securities Production API")
    print("🌐 Endpoint: https://api.kiwoom.com")
    print("📊 Data: Real, live market data")
    print("⏰ Updates: Real-time during market hours")
    print("💰 Stock: Samsung Electronics (005930)")
    print("📈 Market: KOSPI (Korea Exchange)")
    print("\n⚠️  Important Notes:")
    print("   • This uses real API quota/limits")
    print("   • Data reflects actual market conditions")
    print("   • Results may vary based on market hours")
    print("   • Weekend/holiday data may show previous trading day")
    print("=" * 60)


if __name__ == "__main__":
    show_production_info()
    
    success = production_samsung_test()
    
    if success:
        print("\n🏆 SUCCESS: Samsung stock data retrieval is working correctly!")
        print("📊 Your production API credentials are valid and functional")
        print("✅ You can proceed with confidence to build your application")
    else:
        print("\n💥 FAILED: Samsung stock data retrieval test failed")
        print("🔧 Please check the error messages and troubleshooting tips above")
        sys.exit(1) 