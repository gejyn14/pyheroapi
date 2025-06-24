#!/usr/bin/env python3
"""
ka10171 Example - Conditional Search using PyHero API's built-in asyncio
"""

import asyncio
import json
import os
import sys

# Add the parent directory to Python path to import pyheroapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyheroapi.realtime import create_realtime_client
from pyheroapi.client import KiwoomClient

async def ka10171_example():
    """Example using ka10171 conditional search with PyHero API asyncio."""
    
    print("🔍 ka10171 Example - Conditional Search with PyHero API")
    print("="*60)
    
    # Get credentials from environment
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        print("❌ Error: Set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables")
        return
    
    try:
        # Get access token (sync operation)
        print("🔑 Getting access token...")
        token_response = await asyncio.get_event_loop().run_in_executor(
            None, KiwoomClient.issue_token, app_key, secret_key, True
        )
        
        if not token_response or not hasattr(token_response, 'token'):
            print("❌ Failed to get access token")
            return
            
        print("✅ Access token obtained")
        
        # Create async realtime client
        print("🔧 Creating PyHero API realtime client...")
        client = create_realtime_client(
            access_token=token_response.token,
            is_production=True
        )
        
        # Set up callbacks for conditional search responses
        def on_conditional_list(data):
            print(f"\n📋 Conditional Search List Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Parse the list to show available sequences
            if data.get('return_code') == 0:
                items = data.get('data', [])
                if items:
                    print(f"\n📝 Available conditional search items:")
                    for item in items:
                        if isinstance(item, list) and len(item) >= 2:
                            seq, name = item[0], item[1]
                            print(f"   seq={seq}: {name}")
                else:
                    print("⚠️  No conditional search items found in account")
            else:
                print(f"❌ Error: {data.get('return_msg', 'Unknown error')}")
        
        def on_conditional_results(data):
            print(f"\n📊 Conditional Search Results (ka10171):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Parse and display results in a readable format
            if data.get('return_code') == 0:
                results = data.get('data', [])
                print(f"\n✅ Found {len(results)} matching stocks:")
                
                for i, result in enumerate(results[:10]):  # Show first 10 results
                    if isinstance(result, dict):
                        symbol = result.get('9001', 'N/A').replace('A', '')  # Remove 'A' prefix
                        name = result.get('302', 'N/A')
                        price = result.get('10', '0')
                        change_sign = result.get('25', '3')
                        change = result.get('11', '0')
                        volume = result.get('13', '0')
                        
                        # Format price (remove leading zeros)
                        price = str(int(price)) if price.isdigit() else price
                        change = str(int(change)) if change.isdigit() else change
                        volume = str(int(volume)) if volume.isdigit() else volume
                        
                        # Change sign indicators
                        sign_map = {'1': '↑↑', '2': '↑', '3': '→', '4': '↓', '5': '↓↓'}
                        sign_indicator = sign_map.get(change_sign, '→')
                        
                        print(f"   {i+1:2d}. {symbol} ({name}): {price}원 {sign_indicator} {change} [거래량: {volume}]")
                        
                if len(results) > 10:
                    print(f"   ... and {len(results) - 10} more results")
                    
            else:
                error_code = data.get('return_code')
                error_msg = data.get('return_msg', 'Unknown error')
                print(f"❌ Error {error_code}: {error_msg}")
        
        def on_conditional_realtime(data):
            print(f"\n🔴 Real-time Conditional Search Update:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Register callbacks
        client.add_callback("conditional_search_list", on_conditional_list)
        client.add_callback("conditional_search_results", on_conditional_results)
        client.add_callback("conditional_search_realtime", on_conditional_realtime)
        
        # Connect to WebSocket
        print("🔌 Connecting to Kiwoom WebSocket...")
        await client.connect()
        print("✅ Connected and logged in to Kiwoom!")
        
        # Step 1: Get conditional search list
        print("\n📋 Step 1: Getting conditional search list...")
        await client.get_conditional_search_list()
        await asyncio.sleep(3)  # Wait for response
        
        # Step 2: Execute conditional search with sequence 1 (ka10171)
        print("\n🔍 Step 2: Executing conditional search seq=1, search_type=0 (ka10171)...")
        await client.execute_conditional_search(
            seq='1',           # Sequence 1
            search_type='0',   # Regular search (ka10172 format)
            exchange='K',      # KRX exchange
            cont_yn='N',       # New search (not continuation)
            next_key=''        # No pagination key
        )
        await asyncio.sleep(5)  # Wait for results
        
        # Step 3: Try real-time conditional search (ka10173)
        print("\n🔴 Step 3: Trying real-time conditional search seq=1, search_type=1 (ka10173)...")
        await client.execute_conditional_search(
            seq='1',           # Sequence 1  
            search_type='1',   # Real-time search (ka10173 format)
            exchange='K'       # KRX exchange
        )
        await asyncio.sleep(5)  # Wait for results
        
        print("\n✅ ka10171 example completed!")
        
    except Exception as e:
        print(f"❌ Error during ka10171 example: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Disconnect
        print("\n🔌 Disconnecting from WebSocket...")
        await client.disconnect()
        print("✅ Disconnected successfully")

# Run the example
if __name__ == "__main__":
    try:
        asyncio.run(ka10171_example())
    except KeyboardInterrupt:
        print("\n\n👋 Example cancelled by user")
    except Exception as e:
        print(f"\n❌ Failed to run example: {e}") 