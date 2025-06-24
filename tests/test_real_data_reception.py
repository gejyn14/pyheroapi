#!/usr/bin/env python3
"""
Simple test for verifying real data reception from Kiwoom API.

This script provides a straightforward way to test whether your PyHero API
setup is working and receiving actual market data.

Usage:
    python tests/test_real_data_reception.py

Environment Variables Required:
    KIWOOM_APPKEY - Your Kiwoom API key
    KIWOOM_SECRETKEY - Your Kiwoom secret key
    
Environment Variables Optional:
    KIWOOM_ACCESS_TOKEN - Your access token (will be generated if not provided)
"""

import asyncio
import os
import sys
import time
import pytest
from datetime import datetime
from typing import List

# Add the parent directory to Python path to import pyheroapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from pyheroapi.realtime import (
        KiwoomRealtimeClient,
        RealtimeData, 
        RealtimeDataType,
        ConditionalSearchItem,
        ConditionalSearchResult,
        create_realtime_client
    )
    print("✅ PyHero API modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PyHero API: {e}")
    print("Make sure you have installed the package or are running from the correct directory")
    sys.exit(1)


class RealDataTester:
    """Test class for verifying real data reception."""
    
    def __init__(self):
        self.received_stock_data = []
        self.received_conditional_items = []
        self.received_conditional_results = []
        self.start_time = time.time()
        
    def on_stock_data(self, data: RealtimeData):
        """Callback for stock price updates."""
        print(f"\n📈 Received stock data update:")
        self.received_stock_data.append(data)
        print(f"  📊 {data.symbol} ({data.name}): {data.data_type}")
        values_sample = dict(list(data.values.items())[:3]) if data.values else {}
        print(f"      Values: {values_sample}...")  # Show first 3 values
        print(f"      Timestamp: {data.timestamp}")
            
    def on_conditional_search_list(self, data):
        """Callback for conditional search list."""
        print(f"\n🔍 Received conditional search list data:")
        print(f"  Raw data: {data}")
        # Parse the data if it contains list items
        if isinstance(data, dict) and 'data' in data:
            items_data = data.get('data', [])
            for item_data in items_data:
                if isinstance(item_data, list) and len(item_data) >= 2:
                    item = ConditionalSearchItem.from_response_data(item_data)
                    self.received_conditional_items.append(item)
                    print(f"  {item.seq}: {item.name}")
            
    def on_conditional_search_results(self, data):
        """Callback for conditional search results."""
        print(f"\n📋 Received conditional search results:")
        print(f"  Raw data: {data}")
        # Parse the data if it contains result items
        if isinstance(data, dict) and 'data' in data:
            results_data = data.get('data', [])
            for result_data in results_data:
                if isinstance(result_data, dict):
                    result = ConditionalSearchResult.from_response_data(result_data)
                    self.received_conditional_results.append(result)
                    print(f"  📈 {result.symbol} ({result.name}): {result.current_price}")
            
    def print_summary(self):
        """Print test summary."""
        elapsed = time.time() - self.start_time
        print(f"\n" + "="*60)
        print(f"📊 TEST SUMMARY (Duration: {elapsed:.1f}s)")
        print(f"="*60)
        print(f"📈 Stock data updates: {len(self.received_stock_data)}")
        print(f"🔍 Conditional search items: {len(self.received_conditional_items)}")
        print(f"📋 Conditional search results: {len(self.received_conditional_results)}")
        print(f"="*60)
        
        if self.received_stock_data:
            print("✅ SUCCESS: Real stock data was received!")
            print("   Your API connection is working correctly.")
        else:
            print("⚠️  WARNING: No stock data received.")
            print("   This might be normal if markets are closed or in sandbox mode.")
            
        if self.received_conditional_items:
            print("✅ SUCCESS: Conditional search list was received!")
        else:
            print("ℹ️  INFO: No conditional search items received.")


async def get_access_token():
    """Get access token from app key and secret key."""
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        return None
    
    try:
        # Import the client to get access token
        from pyheroapi.client import KiwoomClient
        
        print("🔑 Getting access token from app key and secret key...")
        # Try production mode first (since error suggests app key is for production)
        try:
            token_response = await asyncio.get_event_loop().run_in_executor(
                None, KiwoomClient.issue_token, app_key, secret_key, True  # True = production mode
            )
            print("✅ Using production mode credentials")
            is_production = True
        except Exception as prod_error:
            print(f"⚠️  Production mode failed: {prod_error}")
            print("🔄 Trying sandbox mode...")
            token_response = await asyncio.get_event_loop().run_in_executor(
                None, KiwoomClient.issue_token, app_key, secret_key, False  # False = sandbox mode
            )
            print("✅ Using sandbox mode credentials")
            is_production = False
        
        if token_response and hasattr(token_response, 'token'):
            access_token = token_response.token
            print(f"✅ Access token obtained: {'*' * 10}...{access_token[-4:] if len(access_token) > 4 else '****'}")
            return (access_token, is_production)
        else:
            print(f"❌ Failed to get access token from response: {token_response}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None


def check_environment():
    """Check if environment variables are set."""
    # Only require app key and secret key - we'll get the token from these
    required_vars = ['KIWOOM_APPKEY', 'KIWOOM_SECRETKEY']
    optional_vars = ['KIWOOM_ACCESS_TOKEN']
    missing_vars = []
    
    print("🔍 Checking environment variables...")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * 10}...{value[-4:] if len(value) > 4 else '****'}")
        else:
            missing_vars.append(var)
            print(f"  ❌ {var}: Not set")
    
    # Check optional access token
    access_token = os.getenv('KIWOOM_ACCESS_TOKEN')
    if access_token:
        print(f"  ✅ KIWOOM_ACCESS_TOKEN: {'*' * 10}...{access_token[-4:] if len(access_token) > 4 else '****'}")
        print("  ℹ️  Using provided access token")
    else:
        print("  ⚠️  KIWOOM_ACCESS_TOKEN: Not set (will generate from app key/secret)")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {missing_vars}")
        print("\nPlease set them using:")
        for var in missing_vars:
            print(f"export {var}='your_value_here'")
        print("\nNote: You can either set KIWOOM_ACCESS_TOKEN directly or let the")
        print("      system generate it from KIWOOM_APPKEY and KIWOOM_SECRETKEY")
        return False
    
    print("✅ Required environment variables are set")
    return True


@pytest.mark.asyncio
async def test_real_data_reception():
    """Main test function for real data reception."""
    print("🚀 Starting Real Data Reception Test")
    print("="*60)
    
    # Check environment
    if not check_environment():
        return False
    
    # Get or generate access token
    access_token = os.getenv('KIWOOM_ACCESS_TOKEN')
    is_production_mode = False  # Default to sandbox
    
    if not access_token:
        result = await get_access_token()
        if isinstance(result, tuple):
            access_token, is_production_mode = result
        else:
            access_token = result
            
        if not access_token:
            print("❌ Failed to obtain access token")
            return False
    else:
        print("ℹ️  Using provided access token (assuming production mode)")
        is_production_mode = True  # Assume provided tokens are for production
    
    # Create tester instance
    tester = RealDataTester()
    
    # Create client
    print(f"\n🔧 Creating Kiwoom realtime client...")
    print(f"🏭 Mode: {'Production' if is_production_mode else 'Sandbox'}")
    
    client = create_realtime_client(
        access_token=access_token,
        is_production=is_production_mode
    )
    
    # Set up callbacks
    client.add_callback(RealtimeDataType.STOCK_PRICE, tester.on_stock_data)
    client.add_callback(RealtimeDataType.STOCK_TRADE, tester.on_stock_data)
    client.add_callback("conditional_search_list", tester.on_conditional_search_list)
    client.add_callback("conditional_search_results", tester.on_conditional_search_results)
    
    try:
        # Test connection
        print("🔌 Connecting to Kiwoom WebSocket...")
        await client.connect()
        print(f"✅ Connected successfully! WebSocket state: {client.is_connected}")
        
        # Test stock subscription
        print("\n📈 Subscribing to stock data...")
        test_symbols = ["005930", "000660", "035420"]  # Samsung, SKHynix, NAVER
        await client.subscribe_stock_price(test_symbols)
        print(f"✅ Subscribed to stock prices for: {test_symbols}")
        
        # Test conditional search list
        print("\n🔍 Requesting conditional search list...")
        await client.get_conditional_search_list()
        print("✅ Conditional search list request sent")
        
        # Wait and collect data
        print(f"\n⏱️  Collecting data for 15 seconds...")
        print("   (Press Ctrl+C to stop early)")
        
        for i in range(15):
            await asyncio.sleep(1)
            print(f"  📊 {i+1:2d}/15 - Stock data: {len(tester.received_stock_data):3d}, "
                  f"Conditional items: {len(tester.received_conditional_items):3d}", 
                  end='\r')
        
        print("\n\n⏹️  Data collection completed")
        
        # Show active subscriptions
        subscriptions = client.get_active_subscriptions()
        print(f"\n📋 Active subscriptions: {len(subscriptions)}")
        for key, sub in list(subscriptions.items())[:3]:  # Show first 3
            print(f"  📌 {key}: {sub.symbols[:3] if sub.symbols else []}")
        
        # Test conditional search execution if we have items
        if tester.received_conditional_items:
            print(f"\n🧪 Testing conditional search execution...")
            first_item = tester.received_conditional_items[0]
            await client.execute_conditional_search(first_item.seq, first_item.name)
            print("✅ Conditional search execution request sent")
            await asyncio.sleep(3)  # Wait for results
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    finally:
        print("\n🔌 Disconnecting...")
        await client.disconnect()
        print("✅ Disconnected successfully")
    
    # Print summary
    tester.print_summary()
    return True


async def test_production_mode():
    """Test with production mode (only during market hours)."""
    now = datetime.now()
    is_market_hours = (now.weekday() < 5 and 9 <= now.hour < 16)
    
    if not is_market_hours:
        print("\n⚠️  Skipping production mode test (outside market hours)")
        print("   Production mode test requires market hours: Mon-Fri 9AM-4PM KST")
        return
    
    print(f"\n🏢 Testing production mode (market hours detected)...")
    
    # Get access token
    access_token = os.getenv('KIWOOM_ACCESS_TOKEN')
    if not access_token:
        access_token = await get_access_token()
        if not access_token:
            print("❌ Failed to obtain access token for production test")
            return
    
    tester = RealDataTester()
    client = create_realtime_client(
        access_token=access_token,
        is_production=True  # Use production for real market data
    )
    
    client.add_callback(RealtimeDataType.STOCK_PRICE, tester.on_stock_data)
    
    try:
        await client.connect()
        await client.subscribe_stock_price(["005930"])  # Samsung
        
        print("⏱️  Collecting production data for 10 seconds...")
        await asyncio.sleep(10)
        
        if tester.received_stock_data:
            print("✅ SUCCESS: Production mode is working!")
            print(f"   Received {len(tester.received_stock_data)} real market data updates")
        else:
            print("⚠️  No production data received (this might be normal)")
            
    except Exception as e:
        print(f"❌ Production mode test failed: {e}")
    finally:
        await client.disconnect()


async def main():
    """Main function."""
    print("🔥 PyHero API - Real Data Reception Test")
    print("="*60)
    print("This test verifies that your PyHero API setup can receive")
    print("actual data from the Kiwoom Securities API.")
    print("="*60)
    
    # Run sandbox test
    success = await test_real_data_reception()
    
    if success:
        # Optionally test production mode
        print(f"\n" + "="*60)
        user_input = input("🤔 Test production mode too? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            await test_production_mode()
    
    print(f"\n🎯 Real data reception test completed!")
    print("\n📚 Next steps:")
    print("  1. Run full integration tests: pytest tests/test_realtime_integration.py -v")
    print("  2. Check examples/07_realtime_websocket.py for usage patterns")
    print("  3. Review the received data to understand the format")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 