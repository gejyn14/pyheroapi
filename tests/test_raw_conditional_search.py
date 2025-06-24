#!/usr/bin/env python3
"""
Raw Conditional Search Test - Shows only raw WebSocket messages
"""

import asyncio
import os
import sys
import json

# Add the parent directory to Python path to import pyheroapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyheroapi.realtime import create_realtime_client
from pyheroapi.client import KiwoomClient


async def get_access_token():
    """Get access token for testing."""
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        print("Error: KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables required")
        return None
    
    try:
        token_response = await asyncio.get_event_loop().run_in_executor(
            None, KiwoomClient.issue_token, app_key, secret_key, True
        )
        
        if token_response and hasattr(token_response, 'token'):
            return token_response.token
        else:
            print("Failed to get access token")
            return None
            
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None


def raw_message_callback(data):
    """Callback that just prints raw messages."""
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-" * 50)


async def main():
    """Main function."""
    print("Raw Conditional Search WebSocket Messages:")
    print("=" * 60)
    
    # Get access token
    access_token = await get_access_token()
    if not access_token:
        return
    
    # Create client
    client = create_realtime_client(
        access_token=access_token,
        is_production=True
    )
    
    # Set up callbacks for all conditional search message types
    client.add_callback("conditional_search_list", raw_message_callback)
    client.add_callback("conditional_search_results", raw_message_callback)
    client.add_callback("conditional_search_realtime", raw_message_callback)
    client.add_callback("conditional_search_clear", raw_message_callback)
    
    try:
        # Connect
        await client.connect()
        
        # Request conditional search list
        print("Requesting conditional search list...")
        await client.get_conditional_search_list()
        await asyncio.sleep(2)
        
        # Try conditional search with seq=1, search_type=0
        print("Executing conditional search seq=1, search_type=0...")
        await client.execute_conditional_search(seq='1', search_type='0')
        await asyncio.sleep(3)
        
        # Try conditional search with seq=1, search_type=1
        print("Executing conditional search seq=1, search_type=1...")
        await client.execute_conditional_search(seq='1', search_type='1')
        await asyncio.sleep(3)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 