#!/usr/bin/env python3
"""
Test with correct callback type '0B' for stock trades/prices
"""

import asyncio
import os
from pyheroapi import KiwoomClient

async def test_0B_callback():
    print("🎯 Testing with CORRECT callback type '0B' (Stock Trade)")
    
    # Setup
    app_key = os.getenv("KIWOOM_APPKEY")
    secret_key = os.getenv("KIWOOM_SECRETKEY")
    
    if not app_key or not secret_key:
        print("❌ Missing credentials")
        return
    
    client = KiwoomClient.create_with_credentials(
        appkey=app_key,
        secretkey=secret_key,
        is_production=True
    )
    
    realtime = client.realtime
    
    # ✅ CORRECT: Register callback for '0B' (Stock Trade)
    def samsung_callback(data):
        print(f"\n🎉 SAMSUNG PRICE UPDATE!")
        print(f"   Symbol: {data.symbol}")
        print(f"   Name: {data.name}")
        
        # Extract key price data
        price = data.values.get('10', 'N/A')        # Current price
        change = data.values.get('11', 'N/A')       # Price change  
        change_rate = data.values.get('12', 'N/A')  # Change rate
        volume = data.values.get('13', 'N/A')       # Total volume
        time_val = data.values.get('20', 'N/A')     # Time
        
        print(f"   📊 현재가: ₩{price}")
        print(f"   📈 변동: {change} ({change_rate}%)")
        print(f"   📦 거래량: {volume}")
        print(f"   ⏰ 시간: {time_val}")
        print("-" * 50)
    
    # Register for '0B' (Stock Trade) - this is what actually comes from server
    realtime.add_callback("0B", samsung_callback)
    print("✅ Callback registered for '0B' (Stock Trade)")
    
    # Connect and subscribe
    await realtime.connect()
    print("✅ WebSocket connected")
    
    await realtime.subscribe_stock_price("005930")
    print("✅ Samsung subscription sent")
    
    print("\n🎯 Watching Samsung real-time prices for 15 seconds...")
    print("   (Should see callbacks now!)")
    print("=" * 60)
    
    await asyncio.sleep(15)
    
    print("\n🛑 Stopping...")
    await realtime.disconnect()
    print("✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_0B_callback())
