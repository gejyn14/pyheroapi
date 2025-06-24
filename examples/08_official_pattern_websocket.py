#!/usr/bin/env python3
"""
PyHero API - Official Pattern WebSocket Example

This example follows the official Kiwoom WebSocket pattern more closely,
demonstrating the proper sequence of operations for real-time data streaming.

Based on the official Kiwoom WebSocket example pattern.
"""

import os
import asyncio
import json
from pyheroapi import KiwoomClient
from pyheroapi.realtime import create_realtime_client, RealtimeDataType


async def main():
    """Main WebSocket client following official pattern."""
    
    # Get credentials
    app_key = os.getenv("KIWOOM_APPKEY")
    secret_key = os.getenv("KIWOOM_SECRETKEY")
    
    if not app_key or not secret_key:
        print("Please set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables")
        return
    
    print("🔥 PyHero API - Official Pattern WebSocket Example")
    print("=" * 60)
    
    # Get access token
    print("🔑 Getting access token...")
    try:
        token_response = await asyncio.get_event_loop().run_in_executor(
            None, KiwoomClient.issue_token, app_key, secret_key, True  # Production mode
        )
        
        if not (token_response and hasattr(token_response, 'token')):
            print("❌ Failed to get access token")
            return
            
        access_token = token_response.token
        print(f"✅ Access token obtained")
        
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return
    
    # Create WebSocket client
    client = create_realtime_client(
        access_token=access_token,
        is_production=True
    )
    
    # Set up callbacks for real-time data
    def on_stock_trade(data):
        """Handle stock trade data."""
        print(f"📈 Trade - {data.symbol}: {data.values.get('10', 'N/A')} KRW "
              f"({data.values.get('11', 'N/A')} change) at {data.timestamp}")
    
    def on_stock_price(data):
        """Handle stock price data."""
        print(f"💰 Price - {data.symbol}: {data.values.get('10', 'N/A')} KRW")
    
    def on_order_book(data):
        """Handle order book data."""
        print(f"📊 OrderBook - {data.symbol}: Best Ask {data.values.get('41', 'N/A')}, "
              f"Best Bid {data.values.get('51', 'N/A')}")
    
    # Register callbacks
    client.add_callback(RealtimeDataType.STOCK_TRADE, on_stock_trade)
    client.add_callback(RealtimeDataType.STOCK_PRICE, on_stock_price)
    client.add_callback(RealtimeDataType.ORDER_BOOK, on_order_book)
    
    try:
        # Connect and login (this now follows the official pattern)
        print("\n🔌 Connecting to Kiwoom WebSocket server...")
        await client.connect()
        print("✅ Connected and logged in successfully!")
        
        # Subscribe to real-time data
        print("\n📈 Subscribing to real-time stock data...")
        symbols = ["005930", "000660", "035420"]  # Samsung, SK Hynix, NAVER
        
        # Subscribe to stock trades and prices
        await client.subscribe_stock_price(symbols)
        print(f"✅ Subscribed to stock prices for: {symbols}")
        
        # Subscribe to order book
        await client.subscribe_order_book(symbols)
        print(f"✅ Subscribed to order book for: {symbols}")
        
        # Run for specified duration
        print(f"\n⏱️  Collecting real-time data for 30 seconds...")
        print("   Press Ctrl+C to stop early")
        
        await asyncio.sleep(30)
        
        print(f"\n⏹️  Data collection completed")
        
        # Show active subscriptions
        subscriptions = client.get_active_subscriptions()
        print(f"\n📋 Active subscriptions: {len(subscriptions)}")
        for key, sub in subscriptions.items():
            print(f"  📌 {key}: {sub.symbols}")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n🔌 Disconnecting from WebSocket server...")
        await client.disconnect()
        print("✅ Disconnected successfully")
    
    print(f"\n🎯 WebSocket session completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Example cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}") 