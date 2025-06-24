"""
PyHero API - Real-time WebSocket Example

This example demonstrates:
1. Real-time stock price streaming
2. Real-time order book updates
3. Real-time account updates
4. Event-driven callbacks
5. WebSocket connection management
6. Multi-symbol subscriptions
"""

import os
import asyncio
from pyheroapi import KiwoomClient
from pyheroapi.realtime import RealtimeClient

def setup_client():
    """Setup API client"""
    appkey = os.getenv("KIWOOM_APPKEY", "your_app_key_here")
    secretkey = os.getenv("KIWOOM_SECRETKEY", "your_secret_key_here")
    
    if appkey == "your_app_key_here":
        print("Please set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables")
        return None
    
    return KiwoomClient.create_with_credentials(
        appkey=appkey,
        secretkey=secretkey,
        is_production=False
    )

class RealTimeEventHandler:
    """Event handler for real-time data"""
    
    def __init__(self):
        self.price_updates = 0
        self.orderbook_updates = 0
        self.account_updates = 0
    
    def on_price_update(self, data):
        """Handle stock price updates"""
        self.price_updates += 1
        symbol = data.get('symbol', 'N/A')
        price = data.get('current_price', 'N/A')
        change = data.get('change_rate', 'N/A')
        
        print(f"📈 Price Update #{self.price_updates}: {symbol} = {price} ({change}%)")
    
    def on_orderbook_update(self, data):
        """Handle order book updates"""
        self.orderbook_updates += 1
        symbol = data.get('symbol', 'N/A')
        bid_price = data.get('bid_price_1', 'N/A')
        ask_price = data.get('ask_price_1', 'N/A')
        
        print(f"📋 OrderBook #{self.orderbook_updates}: {symbol} Bid: {bid_price} Ask: {ask_price}")
    
    def on_account_update(self, data):
        """Handle account updates"""
        self.account_updates += 1
        update_type = data.get('update_type', 'N/A')
        
        print(f"💼 Account Update #{self.account_updates}: {update_type}")
    
    def on_connection_opened(self):
        """Handle connection opened"""
        print("🟢 WebSocket connection opened")
    
    def on_connection_closed(self):
        """Handle connection closed"""
        print("🔴 WebSocket connection closed")
    
    def on_error(self, error):
        """Handle errors"""
        print(f"❌ Error: {error}")

async def realtime_price_streaming_example():
    """Real-time price streaming example"""
    
    print("=== Real-time Price Streaming ===\n")
    
    try:
        # Create event handler
        handler = RealTimeEventHandler()
        
        # Create realtime client
        realtime_client = RealtimeClient(
            appkey=os.getenv("KIWOOM_APPKEY"),
            is_production=False
        )
        
        # Set event handlers
        realtime_client.on_price_update = handler.on_price_update
        realtime_client.on_connection_opened = handler.on_connection_opened
        realtime_client.on_connection_closed = handler.on_connection_closed
        realtime_client.on_error = handler.on_error
        
        print("🚀 Starting real-time price streaming...")
        
        # Connect to WebSocket
        await realtime_client.connect()
        
        # Subscribe to multiple symbols
        symbols = ["005930", "000660", "035420"]  # Samsung, SK Hynix, NAVER
        symbol_names = ["Samsung Electronics", "SK Hynix", "NAVER"]
        
        print(f"📊 Subscribing to {len(symbols)} symbols:")
        for symbol, name in zip(symbols, symbol_names):
            print(f"  - {symbol}: {name}")
            await realtime_client.subscribe_price(symbol)
        
        # Run for 30 seconds
        print("\n⏰ Streaming for 30 seconds...")
        await asyncio.sleep(30)
        
        # Unsubscribe and disconnect
        print("\n📤 Unsubscribing and disconnecting...")
        for symbol in symbols:
            await realtime_client.unsubscribe_price(symbol)
        
        await realtime_client.disconnect()
        
        print(f"\n📊 Streaming Summary:")
        print(f"  Price updates received: {handler.price_updates}")
        print(f"  Duration: 30 seconds")
        print(f"  Avg updates/sec: {handler.price_updates/30:.1f}")
        
    except Exception as e:
        print(f"✗ Error in real-time streaming: {e}")

async def realtime_orderbook_example():
    """Real-time order book example"""
    
    print("\n=== Real-time Order Book ===\n")
    
    try:
        handler = RealTimeEventHandler()
        
        realtime_client = RealtimeClient(
            appkey=os.getenv("KIWOOM_APPKEY"),
            is_production=False
        )
        
        realtime_client.on_orderbook_update = handler.on_orderbook_update
        realtime_client.on_connection_opened = handler.on_connection_opened
        realtime_client.on_error = handler.on_error
        
        print("📋 Starting real-time order book streaming...")
        
        await realtime_client.connect()
        
        # Subscribe to order book for Samsung Electronics
        symbol = "005930"
        print(f"📊 Subscribing to order book: {symbol}")
        await realtime_client.subscribe_orderbook(symbol)
        
        # Stream for 20 seconds
        print("⏰ Streaming order book for 20 seconds...")
        await asyncio.sleep(20)
        
        # Cleanup
        await realtime_client.unsubscribe_orderbook(symbol)
        await realtime_client.disconnect()
        
        print(f"\n📋 Order Book Summary:")
        print(f"  Order book updates: {handler.orderbook_updates}")
        
    except Exception as e:
        print(f"✗ Error in order book streaming: {e}")

async def realtime_account_monitoring_example():
    """Real-time account monitoring example"""
    
    print("\n=== Real-time Account Monitoring ===\n")
    
    try:
        handler = RealTimeEventHandler()
        
        realtime_client = RealtimeClient(
            appkey=os.getenv("KIWOOM_APPKEY"),
            is_production=False
        )
        
        realtime_client.on_account_update = handler.on_account_update
        realtime_client.on_connection_opened = handler.on_connection_opened
        realtime_client.on_error = handler.on_error
        
        print("💼 Starting real-time account monitoring...")
        
        await realtime_client.connect()
        
        # Subscribe to account updates
        print("📊 Subscribing to account updates...")
        await realtime_client.subscribe_account_updates()
        
        # Monitor for 15 seconds
        print("⏰ Monitoring account for 15 seconds...")
        print("  💡 Try placing an order in another application to see updates")
        await asyncio.sleep(15)
        
        # Cleanup
        await realtime_client.unsubscribe_account_updates()
        await realtime_client.disconnect()
        
        print(f"\n💼 Account Monitoring Summary:")
        print(f"  Account updates: {handler.account_updates}")
        
    except Exception as e:
        print(f"✗ Error in account monitoring: {e}")

async def comprehensive_realtime_example():
    """Comprehensive real-time example with multiple subscriptions"""
    
    print("\n=== Comprehensive Real-time Streaming ===\n")
    
    try:
        handler = RealTimeEventHandler()
        
        realtime_client = RealtimeClient(
            appkey=os.getenv("KIWOOM_APPKEY"),
            is_production=False
        )
        
        # Set all handlers
        realtime_client.on_price_update = handler.on_price_update
        realtime_client.on_orderbook_update = handler.on_orderbook_update
        realtime_client.on_account_update = handler.on_account_update
        realtime_client.on_connection_opened = handler.on_connection_opened
        realtime_client.on_connection_closed = handler.on_connection_closed
        realtime_client.on_error = handler.on_error
        
        print("🚀 Starting comprehensive real-time streaming...")
        
        await realtime_client.connect()
        
        # Subscribe to multiple data types
        symbols = ["005930", "000660"]  # Samsung, SK Hynix
        
        print("📊 Setting up subscriptions:")
        for symbol in symbols:
            print(f"  - Price updates: {symbol}")
            await realtime_client.subscribe_price(symbol)
            
            print(f"  - Order book: {symbol}")
            await realtime_client.subscribe_orderbook(symbol)
        
        print("  - Account updates")
        await realtime_client.subscribe_account_updates()
        
        # Stream for 45 seconds
        print("\n⏰ Comprehensive streaming for 45 seconds...")
        print("  💡 This demonstrates multiple simultaneous subscriptions")
        
        # Show progress every 10 seconds
        for i in range(45):
            await asyncio.sleep(1)
            if (i + 1) % 10 == 0:
                print(f"  ⏱️  {i+1}s - Price: {handler.price_updates}, "
                      f"OrderBook: {handler.orderbook_updates}, "
                      f"Account: {handler.account_updates}")
        
        # Cleanup all subscriptions
        print("\n📤 Cleaning up subscriptions...")
        for symbol in symbols:
            await realtime_client.unsubscribe_price(symbol)
            await realtime_client.unsubscribe_orderbook(symbol)
        
        await realtime_client.unsubscribe_account_updates()
        await realtime_client.disconnect()
        
        print(f"\n📊 Comprehensive Streaming Summary:")
        print(f"  Total price updates: {handler.price_updates}")
        print(f"  Total orderbook updates: {handler.orderbook_updates}")
        print(f"  Total account updates: {handler.account_updates}")
        print(f"  Total updates: {handler.price_updates + handler.orderbook_updates + handler.account_updates}")
        print(f"  Duration: 45 seconds")
        
    except Exception as e:
        print(f"✗ Error in comprehensive streaming: {e}")

async def connection_management_example():
    """Connection management and error handling example"""
    
    print("\n=== Connection Management ===\n")
    
    try:
        handler = RealTimeEventHandler()
        
        realtime_client = RealtimeClient(
            appkey=os.getenv("KIWOOM_APPKEY"),
            is_production=False
        )
        
        realtime_client.on_connection_opened = handler.on_connection_opened
        realtime_client.on_connection_closed = handler.on_connection_closed
        realtime_client.on_error = handler.on_error
        
        print("🔧 Testing connection management...")
        
        # Test connection lifecycle
        print("\n1️⃣ Testing connection lifecycle:")
        await realtime_client.connect()
        await asyncio.sleep(2)
        await realtime_client.disconnect()
        await asyncio.sleep(1)
        
        # Test reconnection
        print("\n2️⃣ Testing reconnection:")
        await realtime_client.connect()
        await asyncio.sleep(2)
        await realtime_client.disconnect()
        
        print("\n🔧 Connection management test completed")
        
    except Exception as e:
        print(f"✗ Error in connection management: {e}")

async def main():
    """Main async function"""
    
    print("🚀 PyHero API - Real-time WebSocket Example\n")
    
    # Check credentials
    if os.getenv("KIWOOM_APPKEY") == "your_app_key_here" or not os.getenv("KIWOOM_APPKEY"):
        print("⚠️  Please set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables")
        print("   Real-time examples require valid credentials")
        return
    
    try:
        # Run all real-time examples
        await realtime_price_streaming_example()
        await realtime_orderbook_example()
        await realtime_account_monitoring_example()
        await comprehensive_realtime_example()
        await connection_management_example()
        
        print("\n✓ Real-time WebSocket examples completed!")
        
        print("\n📡 Real-time Features Summary:")
        print("   📈 Price streaming: Live stock price updates")
        print("   📋 Order book: Real-time bid/ask depth")
        print("   💼 Account monitoring: Live account changes")
        print("   🔄 Multi-subscriptions: Multiple symbols simultaneously")
        print("   🔧 Connection management: Robust error handling")
        print("   ⚡ Event-driven: Asynchronous callback system")
        
    except Exception as e:
        print(f"✗ Error in main: {e}")

def sync_main():
    """Synchronous main function"""
    
    # Check if running in an environment with an existing event loop
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            # If we're in a Jupyter notebook or similar, use create_task
            loop = asyncio.get_event_loop()
            loop.create_task(main())
        else:
            raise

if __name__ == "__main__":
    sync_main() 