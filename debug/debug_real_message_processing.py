#!/usr/bin/env python3
"""
Debug REAL message processing step by step
"""

import asyncio
import os
import json
from pyheroapi import KiwoomClient

async def debug_real_processing():
    print("🔍 Debugging REAL message processing...")
    
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
    
    # Monkey-patch the _process_message method to add debug logging
    original_process_message = realtime._process_message
    
    async def debug_process_message(data):
        print(f"\n🔍 _process_message called with:")
        print(f"   trnm: {data.get('trnm')}")
        
        if data.get('trnm') == 'REAL':
            print(f"   📡 REAL message detected!")
            print(f"   Raw data: {json.dumps(data, indent=2)[:500]}...")
            
            # Test RealtimeData.from_response
            try:
                from pyheroapi.realtime import RealtimeData
                realtime_data_list = RealtimeData.from_response(data)
                print(f"   ✅ Parsed {len(realtime_data_list)} RealtimeData objects:")
                
                for i, realtime_data in enumerate(realtime_data_list):
                    print(f"      Item {i+1}:")
                    print(f"        data_type: '{realtime_data.data_type}'")
                    print(f"        symbol: '{realtime_data.symbol}'")
                    print(f"        name: '{realtime_data.name}'")
                    print(f"        values keys: {list(realtime_data.values.keys())}")
                    
                    # Check callbacks
                    callbacks = realtime.callbacks.get(realtime_data.data_type, [])
                    print(f"        callbacks for '{realtime_data.data_type}': {len(callbacks)}")
                    
                    if realtime_data.data_type != "02":
                        print(f"        🔥 About to trigger callbacks for '{realtime_data.data_type}'...")
                        
            except Exception as e:
                print(f"   ❌ Error parsing RealtimeData: {e}")
                import traceback
                traceback.print_exc()
        
        # Call original method
        await original_process_message(data)
    
    # Apply the patch
    realtime._process_message = debug_process_message
    
    # Register callback
    def samsung_callback(data):
        print(f"\n🎉 CALLBACK TRIGGERED! Got: {data}")
        if hasattr(data, 'symbol'):
            print(f"   Symbol: {data.symbol}")
            print(f"   Values: {data.values}")
    
    realtime.add_callback("0A", samsung_callback)  # Use raw type code
    print(f"✅ Callback registered. Current callbacks: {dict(realtime.callbacks)}")
    
    # Connect and test
    await realtime.connect()
    await realtime.subscribe_stock_price("005930")
    
    print("⏱️ Debugging for 10 seconds...")
    await asyncio.sleep(10)
    
    await realtime.disconnect()
    print("✅ Debug complete!")

if __name__ == "__main__":
    asyncio.run(debug_real_processing())
