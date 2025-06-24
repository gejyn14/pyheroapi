#!/usr/bin/env python3
"""
Simple example using PyHero API's built-in asyncio support for conditional search
"""

import asyncio
import json
from pyheroapi.realtime import create_realtime_client
from pyheroapi.client import KiwoomClient

async def simple_conditional_search_test():
    """Simple test using PyHero API's built-in asyncio."""
    
    # Get access token
    token_response = KiwoomClient.issue_token(
        app_key="your_app_key",
        secret_key="your_secret_key", 
        is_production=True
    )
    
    # Create async client
    client = create_realtime_client(
        access_token=token_response.token,
        is_production=True
    )
    
    # Set up callbacks for results
    def on_conditional_list(data):
        print(f"Conditional List: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    def on_conditional_results(data):
        print(f"Conditional Results: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    client.add_callback("conditional_search_list", on_conditional_list)
    client.add_callback("conditional_search_results", on_conditional_results)
    
    try:
        # Connect (async)
        await client.connect()
        print("✅ Connected and logged in!")
        
        # Get conditional search list (async)
        await client.get_conditional_search_list()
        await asyncio.sleep(2)
        
        # Execute conditional search (async)
        await client.execute_conditional_search(
            seq='1', 
            search_type='0',  # ka10172 mode
            exchange='K'
        )
        await asyncio.sleep(3)
        
    finally:
        # Disconnect (async)
        await client.disconnect()

# Run with asyncio
if __name__ == "__main__":
    asyncio.run(simple_conditional_search_test()) 