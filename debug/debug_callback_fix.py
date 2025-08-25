#!/usr/bin/env python3
"""
Fix the callback key mismatch
"""

import asyncio
import os
from pyheroapi import KiwoomClient

async def test_callback_fix():
    print("🔧 Testing callback key fix...")
    
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
    
    # FIX: Register callback with raw type code "0A" instead of "STOCK_PRICE"
    def samsung_callback(data):
        print(f"\n🎉 CALLBACK WORKS! Received {len(data)} items:")
        for item in data:
            if item.symbol == "005930":
                price = item.values.get('10', 'N/A')
                time_val = item.values.get('20', 'N/A')
                print(f"📊 Samsung: ₩{price} at {time_val}")
    
    # ✅ CORRECT: Use raw type code "0A" 
    realtime.add_callback("0A", samsung_callback)
    print("✅ Callback registered with correct key: '0A'")
    
    # Connect and test
    await realtime.connect()
    await realtime.subscribe_stock_price("005930")
    
    print("⏱️ Testing for 10 seconds...")
    await asyncio.sleep(10)
    
    await realtime.disconnect()
    print("✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_callback_fix())
