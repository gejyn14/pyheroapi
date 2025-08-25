#!/usr/bin/env python3
"""
Simple WebSocket Debug Test
===========================
Debug the v0.4.2 WebSocket step by step to see where it fails.
"""

import asyncio
import os
import logging
from pyheroapi import KiwoomClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def simple_debug_test():
    print("🔍 Simple WebSocket Debug Test")
    print("=" * 40)
    
    try:
        # Step 1: Check credentials
        print("1️⃣ Checking credentials...")
        app_key = os.getenv("KIWOOM_APPKEY")
        secret_key = os.getenv("KIWOOM_SECRETKEY") 
        
        if not app_key or not secret_key:
            print("❌ Missing production credentials!")
            print("Set KIWOOM_APPKEY and KIWOOM_SECRETKEY")
            return
        
        print(f"✅ App Key: {app_key[:10]}...")
        print(f"✅ Secret Key: {secret_key[:10]}...")
        
        # Step 2: Basic connection
        print("\n2️⃣ Testing basic API connection...")
        client = KiwoomClient.create_with_credentials(
            appkey=app_key,
            secretkey=secret_key,
            is_production=True
        )
        print(f"✅ Connected to: {client.base_url}")
        print(f"✅ Token: {client.access_token[:20]}...")
        
        # Step 3: Get realtime client
        print("\n3️⃣ Getting realtime client...")
        realtime = client.realtime
        print(f"✅ Realtime client created")
        print(f"   WS URL: {realtime.ws_url}")
        
        # Step 4: Simple callback with debug
        def debug_callback(data):
            print(f"\n📡 CALLBACK TRIGGERED! Received {len(data)} items:")
            for i, item in enumerate(data):
                print(f"   Item {i+1}: {item.symbol} = {item.values}")
        
        realtime.add_callback("STOCK_PRICE", debug_callback)
        print("✅ Callback registered")
        
        # Step 5: WebSocket connection with NEW pattern
        print("\n4️⃣ Testing NEW WebSocket connection...")
        try:
            await realtime.connect()
            print("✅ WebSocket connected successfully!")
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return
            
        # Step 6: Subscribe to Samsung
        print("\n5️⃣ Subscribing to Samsung (005930)...")
        try:
            await realtime.subscribe_stock_price("005930")
            print("✅ Samsung subscription sent")
        except Exception as e:
            print(f"❌ Subscription failed: {e}")
            return
            
        # Step 7: Wait and see what happens
        print("\n6️⃣ Waiting 15 seconds for price updates...")
        print("💡 If no updates appear, there's still an issue...")
        
        for i in range(15):
            await asyncio.sleep(1)
            print(f"⏰ {i+1}/15 seconds...", end='\r')
            
        print("\n\n7️⃣ Cleanup...")
        await realtime.disconnect()
        print("✅ Disconnected")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_debug_test())
