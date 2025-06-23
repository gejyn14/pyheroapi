#!/usr/bin/env python3
"""
Real-time Market Data Example for Kiwoom API Python client.

This example demonstrates how to:
1. Connect to WebSocket for real-time data
2. Subscribe to different types of market data
3. Handle real-time price updates
4. Monitor account changes and order executions
5. Use callbacks for data processing
"""

import asyncio
import logging
import os
from datetime import datetime

import pyheroapi
from pyheroapi import (
    KiwoomRealtimeClient,
    RealtimeData,
    RealtimeDataType,
    create_realtime_client,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def price_callback(data: RealtimeData):
    """Callback function for stock price updates."""
    values = data.values
    symbol = data.symbol
    
    if data.data_type == "0B":  # Stock trade
        current_price = values.get("10", "N/A")
        volume = values.get("15", "N/A")
        time = values.get("20", "N/A")
        
        print(f"📈 {symbol} Trade: ₩{current_price} (Vol: {volume}) at {time}")
        
    elif data.data_type == "0A":  # Stock price (기세)
        current_price = values.get("10", "N/A")
        change = values.get("11", "N/A")
        change_rate = values.get("12", "N/A")
        
        print(f"💰 {symbol} Price: ₩{current_price} ({change}, {change_rate}%)")


async def order_book_callback(data: RealtimeData):
    """Callback function for order book updates."""
    values = data.values
    symbol = data.symbol
    
    if data.data_type == "0C":  # Best quote
        best_ask = values.get("27", "N/A")
        best_bid = values.get("28", "N/A")
        
        print(f"📊 {symbol} Best Quote: Ask ₩{best_ask} / Bid ₩{best_bid}")
        
    elif data.data_type == "0D":  # Order book
        # Show top 5 levels of order book
        print(f"📋 {symbol} Order Book Update:")
        for i in range(1, 6):
            ask_price = values.get(f"4{i}", "")
            ask_qty = values.get(f"6{i}", "")
            bid_price = values.get(f"5{i}", "")
            bid_qty = values.get(f"7{i}", "")
            
            if ask_price and bid_price:
                print(f"  Level {i}: Ask ₩{ask_price}({ask_qty}) | Bid ₩{bid_price}({bid_qty})")


async def account_callback(data: RealtimeData):
    """Callback function for account updates."""
    values = data.values
    
    if data.data_type == "00":  # Order execution
        symbol = values.get("9001", "N/A")
        order_status = values.get("913", "N/A")
        quantity = values.get("900", "N/A")
        price = values.get("901", "N/A")
        
        print(f"🏦 Order Update: {symbol} - {order_status} ({quantity} @ ₩{price})")
        
    elif data.data_type == "04":  # Account balance
        symbol = values.get("9001", "N/A")
        current_price = values.get("10", "N/A")
        quantity = values.get("930", "N/A")
        
        print(f"💼 Position Update: {symbol} - {quantity} shares @ ₩{current_price}")


async def sector_callback(data: RealtimeData):
    """Callback function for sector index updates."""
    values = data.values
    sector = data.symbol
    
    if data.data_type == "0J":  # Sector index
        current_value = values.get("10", "N/A")
        change = values.get("11", "N/A")
        change_rate = values.get("12", "N/A")
        volume = values.get("13", "N/A")
        
        print(f"🏭 Sector {sector}: {current_value} ({change}, {change_rate}%) Vol: {volume}")


async def etf_callback(data: RealtimeData):
    """Callback function for ETF NAV updates."""
    values = data.values
    symbol = data.symbol
    
    if data.data_type == "0G":  # ETF NAV
        nav = values.get("36", "N/A")
        current_price = values.get("10", "N/A")
        premium = values.get("265", "N/A")
        
        print(f"🏢 ETF {symbol}: NAV ₩{nav} | Price ₩{current_price} | Premium {premium}%")


async def main():
    """Main example function demonstrating real-time data streaming."""
    print("🚀 Kiwoom Real-time Market Data Example")
    print("=" * 50)
    
    # Get credentials from environment
    access_token = os.getenv("KIWOOM_ACCESS_TOKEN")
    appkey = os.getenv("KIWOOM_APP_KEY")
    secretkey = os.getenv("KIWOOM_SECRET_KEY")
    
    if not access_token and not (appkey and secretkey):
        print("❌ Please set either:")
        print("   - KIWOOM_ACCESS_TOKEN environment variable, OR")
        print("   - Both KIWOOM_APP_KEY and KIWOOM_SECRET_KEY environment variables")
        return
    
    # Create access token if needed
    if not access_token:
        try:
            print("🔑 Generating access token...")
            token_response = pyheroapi.KiwoomClient.issue_token(
                appkey, secretkey, is_production=False
            )
            access_token = token_response.token
            print("✅ Token generated successfully!")
        except Exception as e:
            print(f"❌ Failed to generate token: {e}")
            return
    
    # Create real-time client
    rt_client = create_realtime_client(
        access_token=access_token,
        is_production=False,  # Use sandbox for testing
        auto_reconnect=True,
        max_reconnect_attempts=3,
        reconnect_delay=5
    )
    
    try:
        print("🔌 Connecting to WebSocket...")
        await rt_client.connect()
        print("✅ Connected successfully!")
        
        # Add callbacks for different data types
        rt_client.add_callback(RealtimeDataType.STOCK_TRADE, price_callback)
        rt_client.add_callback(RealtimeDataType.STOCK_PRICE, price_callback)
        rt_client.add_callback(RealtimeDataType.BEST_QUOTE, order_book_callback)
        rt_client.add_callback(RealtimeDataType.ORDER_BOOK, order_book_callback)
        rt_client.add_callback(RealtimeDataType.ORDER_EXECUTION, account_callback)
        rt_client.add_callback(RealtimeDataType.ACCOUNT_BALANCE, account_callback)
        rt_client.add_callback(RealtimeDataType.SECTOR_INDEX, sector_callback)
        rt_client.add_callback(RealtimeDataType.ETF_NAV, etf_callback)
        
        print("\n📊 Subscribing to market data...")
        
        # Subscribe to stock prices for major stocks
        await rt_client.subscribe_stock_price(["005930", "000660", "035420"])  # Samsung, SK, NAVER
        print("✅ Subscribed to stock prices")
        
        # Subscribe to order book for Samsung
        await rt_client.subscribe_order_book("005930")
        print("✅ Subscribed to order book")
        
        # Subscribe to account updates
        await rt_client.subscribe_account_updates()
        print("✅ Subscribed to account updates")
        
        # Subscribe to KOSPI index
        await rt_client.subscribe_sector_index("001")
        print("✅ Subscribed to KOSPI index")
        
        # Subscribe to ETF NAV (KODEX 200)
        await rt_client.subscribe_etf_nav("069500")
        print("✅ Subscribed to ETF NAV")
        
        print(f"\n🎯 Listening for real-time data... (Press Ctrl+C to stop)")
        print(f"Active subscriptions: {len(rt_client.get_active_subscriptions())}")
        print("-" * 60)
        
        # Run for a specified duration or until interrupted
        try:
            await asyncio.sleep(300)  # Run for 5 minutes
        except KeyboardInterrupt:
            print("\n⏹️ Stopping real-time data stream...")
        
        # Clean up subscriptions
        print("🧹 Cleaning up subscriptions...")
        await rt_client.unsubscribe_all()
        print("✅ All subscriptions removed")
        
    except Exception as e:
        print(f"❌ Error during real-time streaming: {e}")
        
    finally:
        # Disconnect
        print("🔌 Disconnecting...")
        await rt_client.disconnect()
        print("✅ Disconnected successfully!")


async def advanced_example():
    """Advanced example with custom subscription management."""
    print("\n🔬 Advanced Real-time Example")
    print("-" * 40)
    
    access_token = os.getenv("KIWOOM_ACCESS_TOKEN")
    if not access_token:
        print("❌ Access token required for advanced example")
        return
    
    # Use context manager for automatic connection management
    rt_client = create_realtime_client(access_token, is_production=False)
    
    async with pyheroapi.RealtimeContext(rt_client) as client:
        
        # Custom callback that logs all data
        async def logger_callback(data: RealtimeData):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {data.name} ({data.symbol}): {data.data_type}")
        
        # Add logger to all data types
        for data_type in RealtimeDataType:
            client.add_callback(data_type, logger_callback)
        
        # Subscribe to multiple data types at once
        symbols = ["005930", "000660", "035420", "051910", "068270"]  # Major tech stocks
        
        await client.subscribe_stock_price(symbols)
        await client.subscribe_order_book(symbols[:2])  # Order book for first 2 stocks
        
        print(f"📡 Monitoring {len(symbols)} stocks...")
        print("🔍 All data will be logged...")
        
        # Run for shorter duration
        await asyncio.sleep(60)  # 1 minute
        
        print("📊 Subscription summary:")
        subscriptions = client.get_active_subscriptions()
        for key, sub in subscriptions.items():
            print(f"  - {key}: {len(sub.symbols)} symbols, {len(sub.data_types)} data types")


if __name__ == "__main__":
    try:
        # Run main example
        asyncio.run(main())
        
        # Run advanced example
        # asyncio.run(advanced_example())
        
    except KeyboardInterrupt:
        print("\n👋 Real-time streaming stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}") 