#!/usr/bin/env python3
"""
ka10171 Correct Example - Conditional Search List (only requires trnm)
"""

import asyncio
import json
import os
import sys

# Add the parent directory to Python path to import pyheroapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyheroapi.realtime import create_realtime_client
from pyheroapi.client import KiwoomClient

async def ka10171_correct_example():
    """Correct ka10171 example - only get conditional search list."""
    
    print("🔍 ka10171 Correct Example - Conditional Search List")
    print("="*60)
    print("Request: { 'trnm': 'CNSRLST' }")
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
        
        # Set up callback for ka10171 response
        def on_conditional_list(data):
            print(f"\n📋 ka10171 Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Parse the conditional search list
            if data.get('return_code') == 0:
                items = data.get('data', [])
                if items:
                    print(f"\n✅ ka10171 Success: Found {len(items)} conditional search items:")
                    for item in items:
                        if isinstance(item, list) and len(item) >= 2:
                            seq, name = item[0], item[1]
                            print(f"   seq={seq}: {name}")
                else:
                    print("\n⚠️  ka10171 Success: No conditional search items in account")
                    print("   → Create conditional searches in Hero Trader 4 to see items here")
            else:
                error_code = data.get('return_code')
                error_msg = data.get('return_msg', 'Unknown error')
                print(f"\n❌ ka10171 Failed: Error {error_code}: {error_msg}")
        
        # Register callback for conditional search list
        client.add_callback("conditional_search_list", on_conditional_list)
        
        # Connect to WebSocket
        print("🔌 Connecting to Kiwoom WebSocket...")
        await client.connect()
        print("✅ Connected and logged in to Kiwoom!")
        
        # Execute ka10171 - get conditional search list
        print("\n🎯 Executing ka10171: Get conditional search list...")
        print("   Sending: { 'trnm': 'CNSRLST' }")
        
        await client.get_conditional_search_list()
        
        # Wait for ka10171 response
        print("⏱️  Waiting for ka10171 response...")
        await asyncio.sleep(3)
        
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
        asyncio.run(ka10171_correct_example())
    except KeyboardInterrupt:
        print("\n\n👋 ka10171 test cancelled by user")
    except Exception as e:
        print(f"\n❌ Failed to run ka10171 test: {e}") 