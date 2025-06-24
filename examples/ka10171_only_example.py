#!/usr/bin/env python3
"""
ka10171 ONLY Example - Conditional Search Sequence 1 using PyHero API
"""

import asyncio
import json
import os
import sys

# Add the parent directory to Python path to import pyheroapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyheroapi.realtime import create_realtime_client
from pyheroapi.client import KiwoomClient

async def ka10171_only_example():
    """Example testing ONLY ka10171 - conditional search sequence 1."""
    
    print("🔍 ka10171 ONLY Example - Conditional Search Sequence 1")
    print("="*60)
    
    # Get credentials from environment
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        print("❌ Error: Set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables")
        return
    
    try:
        # Get access token
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
        
        # Set up callback ONLY for conditional search results
        def on_conditional_results(data):
            print(f"\n📊 ka10171 Response (Sequence 1 Results):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Parse results if successful
            if data.get('return_code') == 0:
                results = data.get('data', [])
                print(f"\n✅ ka10171 Success: Found {len(results)} stocks matching sequence 1 criteria")
                
                # Show first few results in readable format
                for i, result in enumerate(results[:5]):
                    if isinstance(result, dict):
                        symbol = result.get('9001', 'N/A').replace('A', '')
                        name = result.get('302', 'N/A')
                        price = result.get('10', '0')
                        change_sign = result.get('25', '3')
                        change = result.get('11', '0')
                        
                        price = str(int(price)) if price.isdigit() else price
                        change = str(int(change)) if change.isdigit() else change
                        
                        sign_map = {'1': '↑↑', '2': '↑', '3': '→', '4': '↓', '5': '↓↓'}
                        sign_indicator = sign_map.get(change_sign, '→')
                        
                        print(f"   {i+1}. {symbol} ({name}): {price}원 {sign_indicator} {change}")
                        
            else:
                error_code = data.get('return_code')
                error_msg = data.get('return_msg', 'Unknown error')
                print(f"\n❌ ka10171 Failed: Error {error_code}: {error_msg}")
                
                if error_code == 900004:
                    print("   → This means sequence 1 doesn't exist in your account")
                    print("   → You need to create conditional search items in Hero Trader 4 first")
        
        # Register callback for conditional search results only
        client.add_callback("conditional_search_results", on_conditional_results)
        
        # Connect to WebSocket
        print("🔌 Connecting to Kiwoom WebSocket...")
        await client.connect()
        print("✅ Connected and logged in to Kiwoom!")
        
        # Execute ka10171 ONLY - conditional search sequence 1
        print("\n🎯 Testing ka10171: Conditional search sequence 1...")
        print("   Request: CNSRREQ with seq=1, search_type=0")
        
        await client.execute_conditional_search(
            seq='1',           # ka10171 = sequence 1 specifically
            search_type='0',   # Regular conditional search
            exchange='K',      # KRX exchange
            cont_yn='N',       # New search
            next_key=''        # No pagination
        )
        
        # Wait for ka10171 response
        print("⏱️  Waiting for ka10171 response...")
        await asyncio.sleep(5)
        
        print("\n✅ ka10171 test completed!")
        
    except Exception as e:
        print(f"❌ Error during ka10171 test: {e}")
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
        asyncio.run(ka10171_only_example())
    except KeyboardInterrupt:
        print("\n\n👋 ka10171 test cancelled by user")
    except Exception as e:
        print(f"\n❌ Failed to run ka10171 test: {e}") 