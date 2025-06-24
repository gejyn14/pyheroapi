#!/usr/bin/env python3
"""
Detailed diagnostic test for real-time data reception issues.

This test provides extensive debugging information to help identify
why real-time stock data is not being received during market hours.
"""

import asyncio
import os
import sys
import time
import json
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
    from pyheroapi.client import KiwoomClient
    print("✅ PyHero API modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PyHero API: {e}")
    sys.exit(1)


class DetailedRealtimeTester:
    """Enhanced test class with detailed debugging."""
    
    def __init__(self):
        self.received_stock_data = []
        self.received_conditional_items = []
        self.received_conditional_results = []
        self.raw_messages = []
        self.subscription_responses = []
        self.start_time = time.time()
        
    def on_stock_data(self, data):
        """Callback for stock price updates with detailed logging."""
        print(f"\n📈 [STOCK DATA] Received: {type(data)}")
        print(f"    Raw data: {data}")
        
        if isinstance(data, RealtimeData):
            self.received_stock_data.append(data)
            print(f"    📊 Symbol: {data.symbol}")
            print(f"    📊 Name: {data.name}")
            print(f"    📊 Type: {data.data_type}")
            print(f"    📊 Values: {data.values}")
            print(f"    📊 Timestamp: {data.timestamp}")
        else:
            print(f"    ⚠️  Unexpected data type: {type(data)}")
            
    def on_subscription_response(self, data):
        """Callback for subscription responses."""
        print(f"\n📝 [SUBSCRIPTION] Response received:")
        print(f"    {json.dumps(data, indent=2, ensure_ascii=False)}")
        self.subscription_responses.append(data)
        
    def on_raw_message(self, data):
        """Callback for all raw messages."""
        print(f"\n🔍 [RAW MESSAGE] Type: {data.get('trnm', 'Unknown')}")
        print(f"    {json.dumps(data, indent=2, ensure_ascii=False)}")
        self.raw_messages.append(data)
        
    def on_conditional_search_list(self, data):
        """Enhanced conditional search list callback."""
        print(f"\n🔍 [CONDITIONAL LIST] Received:")
        print(f"    {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Check for error codes
        return_code = data.get('return_code')
        if return_code and return_code != 0:
            print(f"    ❌ Error code: {return_code}")
            print(f"    ❌ Error message: {data.get('return_msg', 'Unknown error')}")
            return
            
        # Parse successful response
        if isinstance(data, dict) and 'data' in data:
            items_data = data.get('data', [])
            print(f"    📋 Found {len(items_data)} conditional search items")
            for item_data in items_data:
                if isinstance(item_data, list) and len(item_data) >= 2:
                    item = ConditionalSearchItem.from_response_data(item_data)
                    self.received_conditional_items.append(item)
                    print(f"      {item.seq}: {item.name}")
    
    def print_summary(self):
        """Print detailed test summary."""
        elapsed = time.time() - self.start_time
        print(f"\n" + "="*70)
        print(f"📊 DETAILED TEST SUMMARY (Duration: {elapsed:.1f}s)")
        print(f"="*70)
        print(f"📈 Stock data updates: {len(self.received_stock_data)}")
        print(f"📝 Subscription responses: {len(self.subscription_responses)}")
        print(f"🔍 Raw messages: {len(self.raw_messages)}")
        print(f"📋 Conditional search items: {len(self.received_conditional_items)}")
        print(f"="*70)
        
        if self.subscription_responses:
            print("\n📝 Subscription Response Analysis:")
            for resp in self.subscription_responses:
                return_code = resp.get('return_code', 0)
                status = "✅ SUCCESS" if return_code == 0 else f"❌ ERROR ({return_code})"
                print(f"    {status}: {resp.get('return_msg', 'No message')}")
        
        if self.raw_messages:
            print(f"\n🔍 Message Types Received:")
            msg_types = {}
            for msg in self.raw_messages:
                msg_type = msg.get('trnm', 'Unknown')
                msg_types[msg_type] = msg_types.get(msg_type, 0) + 1
            for msg_type, count in msg_types.items():
                print(f"    {msg_type}: {count} messages")


async def get_access_token():
    """Get access token with detailed error reporting."""
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        return None
    
    print("🔑 Getting access token...")
    print(f"    App Key: {'*' * 10}...{app_key[-4:]}")
    print(f"    Secret Key: {'*' * 10}...{secret_key[-4:]}")
    
    try:
        # Try production mode first
        print("🔄 Attempting production mode...")
        token_response = await asyncio.get_event_loop().run_in_executor(
            None, KiwoomClient.issue_token, app_key, secret_key, True
        )
        
        if token_response and hasattr(token_response, 'token'):
            access_token = token_response.token
            print(f"✅ Access token obtained: {'*' * 10}...{access_token[-4:]}")
            return (access_token, True)
        else:
            print(f"❌ Failed to get access token: {token_response}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None


@pytest.mark.asyncio
async def test_realtime_debug():
    """Detailed diagnostic test for real-time data issues."""
    print("🔍 Starting Detailed Real-time Diagnostic Test")
    print("="*70)
    
    # Get access token
    result = await get_access_token()
    if not result:
        print("❌ Failed to obtain access token")
        return False
    
    access_token, is_production = result
    
    # Create enhanced tester
    tester = DetailedRealtimeTester()
    
    # Create client with debug logging
    print(f"\n🔧 Creating Kiwoom realtime client...")
    print(f"🏭 Mode: {'Production' if is_production else 'Sandbox'}")
    print(f"🔗 WebSocket URL: {KiwoomRealtimeClient.PRODUCTION_WS_URL if is_production else KiwoomRealtimeClient.SANDBOX_WS_URL}")
    
    client = create_realtime_client(
        access_token=access_token,
        is_production=is_production
    )
    
    # Set up all possible callbacks
    print("\n📡 Setting up callbacks...")
    client.add_callback(RealtimeDataType.STOCK_PRICE, tester.on_stock_data)
    client.add_callback(RealtimeDataType.STOCK_TRADE, tester.on_stock_data)
    client.add_callback(RealtimeDataType.BEST_QUOTE, tester.on_stock_data)
    client.add_callback(RealtimeDataType.ORDER_BOOK, tester.on_stock_data)
    client.add_callback("conditional_search_list", tester.on_conditional_search_list)
    client.add_callback("REG", tester.on_subscription_response)
    client.add_callback("REMOVE", tester.on_subscription_response)
    print("✅ Callbacks registered")
    
    try:
        # Test connection with detailed logging
        print("\n🔌 Connecting to Kiwoom WebSocket...")
        await client.connect()
        print(f"✅ Connected! WebSocket state: {client.is_connected}")
        
        # Wait a moment for connection to stabilize
        print("⏱️  Waiting 2 seconds for connection to stabilize...")
        await asyncio.sleep(2)
        
        # Test different subscription approaches
        print(f"\n📈 Testing various subscription approaches...")
        
        # Approach 1: Individual stock subscription
        print("📊 Approach 1: Individual stock subscription")
        test_symbols = ["005930"]  # Just Samsung for now
        await client.subscribe_stock_price(test_symbols)
        print(f"✅ Subscribed to stock prices for: {test_symbols}")
        await asyncio.sleep(3)  # Wait for subscription response
        
        # Approach 2: Order book subscription
        print("📊 Approach 2: Order book subscription")
        await client.subscribe_order_book(test_symbols)
        print(f"✅ Subscribed to order book for: {test_symbols}")
        await asyncio.sleep(3)
        
        # Check subscription status
        subscriptions = client.get_active_subscriptions()
        print(f"\n📋 Active subscriptions: {len(subscriptions)}")
        for key, sub in subscriptions.items():
            print(f"    📌 {key}: {sub.symbols} (types: {[dt.value for dt in sub.data_types]})")
        
        # Extended data collection with progress
        print(f"\n⏱️  Extended data collection for 20 seconds...")
        print("    Press Ctrl+C to stop early")
        
        for i in range(20):
            await asyncio.sleep(1)
            stock_count = len(tester.received_stock_data)
            msg_count = len(tester.raw_messages)
            sub_count = len(tester.subscription_responses)
            
            print(f"    📊 {i+1:2d}/20 - Stock: {stock_count:3d}, Messages: {msg_count:3d}, Subs: {sub_count:3d}", end='\r')
            
            # If we get some data, show it immediately
            if stock_count > 0 and i % 5 == 0:
                print(f"\n    🎉 Received {stock_count} stock updates so far!")
        
        print(f"\n\n⏹️  Data collection completed")
        
        # Test account balance subscription if no stock data
        if not tester.received_stock_data:
            print(f"\n🔄 No stock data received. Trying account balance subscription...")
            await client.subscribe_account_updates()
            await asyncio.sleep(5)
            print(f"Account subscription test completed")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        print("\n🔌 Disconnecting...")
        await client.disconnect()
        print("✅ Disconnected successfully")
    
    # Print detailed summary
    tester.print_summary()
    
    # Provide recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if not tester.received_stock_data:
        print("❌ No stock data received. Possible issues:")
        print("   1. WebSocket connection established but no data flowing")
        print("   2. Subscription requests may be failing silently")
        print("   3. Authentication issues preventing data delivery")
        print("   4. Market data permissions not enabled for your account")
        print("\n🔧 Try these steps:")
        print("   1. Check your Kiwoom account permissions for real-time data")
        print("   2. Verify your API subscription includes market data")
        print("   3. Test with a different stock symbol")
        print("   4. Contact Kiwoom support to verify account settings")
    else:
        print("✅ Stock data is flowing correctly!")
    
    return len(tester.received_stock_data) > 0


if __name__ == "__main__":
    try:
        result = asyncio.run(test_realtime_debug())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
        sys.exit(1) 