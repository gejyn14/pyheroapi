#!/usr/bin/env python3
"""
Test for Conditional Search functionality (ka10173)

This test specifically checks if conditional search sequence 4 works correctly,
following the official Kiwoom WebSocket pattern for conditional search.
"""

import asyncio
import os
import sys
import pytest
import json

# Add the parent directory to Python path to import pyheroapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from pyheroapi.realtime import create_realtime_client
    from pyheroapi.client import KiwoomClient
    print("✅ PyHero API modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PyHero API: {e}")
    sys.exit(1)


class ConditionalSearchTester:
    """Test class for conditional search functionality."""
    
    def __init__(self):
        self.conditional_list_received = False
        self.conditional_search_results = []
        self.conditional_search_items = []
        self.raw_messages = []
        
    def on_conditional_search_list(self, data):
        """Callback for conditional search list (CNSRLST)."""
        print(f"\n🔍 [CONDITIONAL LIST] Received:")
        print(f"    {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.raw_messages.append(data)
        
        # Check for error codes
        return_code = data.get('return_code')
        if return_code and return_code != 0:
            print(f"    ❌ Error code: {return_code}")
            print(f"    ❌ Error message: {data.get('return_msg', 'Unknown error')}")
            return
            
        # Parse successful response
        self.conditional_list_received = True
        if isinstance(data, dict) and 'data' in data:
            items_data = data.get('data', [])
            print(f"    📋 Found {len(items_data)} conditional search items")
            for item_data in items_data:
                if isinstance(item_data, list) and len(item_data) >= 2:
                    seq = item_data[0]
                    name = item_data[1]
                    self.conditional_search_items.append({'seq': seq, 'name': name})
                    print(f"      {seq}: {name}")
                    
    def on_conditional_search_results(self, data):
        """Callback for conditional search results (CNSRREQ)."""
        print(f"\n📋 [CONDITIONAL RESULTS] Received:")
        print(f"    {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        self.raw_messages.append(data)
        self.conditional_search_results.append(data)
        
        # Check for error codes
        return_code = data.get('return_code')
        if return_code and return_code != 0:
            print(f"    ❌ Error code: {return_code}")
            print(f"    ❌ Error message: {data.get('return_msg', 'Unknown error')}")
            return
            
        # Parse results
        if isinstance(data, dict) and 'data' in data:
            results_data = data.get('data', [])
            print(f"    📈 Found {len(results_data)} search results")
            for result in results_data[:5]:  # Show first 5 results
                if isinstance(result, dict):
                    symbol = result.get('9001', 'N/A')
                    name = result.get('302', 'N/A')
                    price = result.get('10', 'N/A')
                    print(f"      {symbol} ({name}): {price}")
                    
    def print_summary(self):
        """Print test summary."""
        print(f"\n" + "="*60)
        print(f"📊 CONDITIONAL SEARCH TEST SUMMARY")
        print(f"="*60)
        print(f"🔍 Conditional list received: {self.conditional_list_received}")
        print(f"📋 Conditional search items: {len(self.conditional_search_items)}")
        print(f"📈 Search results received: {len(self.conditional_search_results)}")
        print(f"📝 Total raw messages: {len(self.raw_messages)}")
        print(f"="*60)


async def get_access_token():
    """Get access token for testing."""
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        return None
    
    print("🔑 Getting access token...")
    try:
        token_response = await asyncio.get_event_loop().run_in_executor(
            None, KiwoomClient.issue_token, app_key, secret_key, True
        )
        
        if token_response and hasattr(token_response, 'token'):
            access_token = token_response.token
            print(f"✅ Access token obtained")
            return access_token
        else:
            print(f"❌ Failed to get access token")
            return None
            
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return None


@pytest.mark.asyncio
async def test_conditional_search_ka10173():
    """Test conditional search functionality, specifically sequence 4."""
    print("🔍 Starting Conditional Search Test (ka10173)")
    print("="*60)
    
    # Get access token
    access_token = await get_access_token()
    if not access_token:
        print("❌ Failed to obtain access token")
        return False
    
    # Create tester
    tester = ConditionalSearchTester()
    
    # Create client
    print(f"\n🔧 Creating Kiwoom realtime client...")
    client = create_realtime_client(
        access_token=access_token,
        is_production=True
    )
    
    # Set up callbacks
    client.add_callback("conditional_search_list", tester.on_conditional_search_list)
    client.add_callback("conditional_search_results", tester.on_conditional_search_results)
    
    try:
        # Connect and login
        print("🔌 Connecting to Kiwoom WebSocket...")
        await client.connect()
        print("✅ Connected and logged in successfully!")
        
        # Step 1: Get conditional search list
        print("\n📋 Step 1: Requesting conditional search list...")
        await client.get_conditional_search_list()
        print("✅ Conditional search list request sent")
        
        # Wait for list response
        print("⏱️  Waiting for conditional search list response...")
        await asyncio.sleep(3)
        
        if not tester.conditional_list_received:
            print("❌ No conditional search list received")
            return False
        
        # Step 2: Test conditional search with sequence 4
        print(f"\n🔍 Step 2: Testing conditional search with sequence 4...")
        
        # Check if sequence 4 exists in the list
        seq_4_found = any(item['seq'] == '4' for item in tester.conditional_search_items)
        if seq_4_found:
            print("✅ Sequence 4 found in conditional search list")
        else:
            print("⚠️  Sequence 4 not found in list, but proceeding with test...")
            # Show available sequences
            if tester.conditional_search_items:
                print("Available sequences:")
                for item in tester.conditional_search_items[:10]:
                    print(f"  {item['seq']}: {item['name']}")
        
        # Execute conditional search with sequence 4 (search_type=1 for real-time)
        print(f"🚀 Executing conditional search with seq=4, search_type=1...")
        await client.execute_conditional_search_realtime(seq='4', exchange='K')
        print("✅ Conditional search request sent")
        
        # Wait for results
        print("⏱️  Waiting for conditional search results...")
        await asyncio.sleep(5)
        
        # Show results
        if tester.conditional_search_results:
            print(f"✅ Received {len(tester.conditional_search_results)} conditional search responses")
        else:
            print("⚠️  No conditional search results received")
        
        # Extended wait to see if real-time updates come
        print("\n⏱️  Waiting for potential real-time updates (10 seconds)...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n🔌 Disconnecting...")
        await client.disconnect()
        print("✅ Disconnected successfully")
    
    # Print summary
    tester.print_summary()
    
    # Determine success
    success = tester.conditional_list_received and len(tester.conditional_search_results) > 0
    
    if success:
        print("\n✅ SUCCESS: Conditional search functionality is working!")
        print("   - Conditional search list was retrieved")
        print("   - Conditional search execution returned results")
    else:
        print("\n⚠️  PARTIAL SUCCESS:")
        if tester.conditional_list_received:
            print("   ✅ Conditional search list retrieval works")
        else:
            print("   ❌ Conditional search list retrieval failed")
            
        if tester.conditional_search_results:
            print("   ✅ Conditional search execution works")
        else:
            print("   ❌ Conditional search execution failed or no results")
    
    return success


async def main():
    """Main function for standalone execution."""
    print("🔥 PyHero API - Conditional Search Test (ka10173)")
    print("="*60)
    print("Testing conditional search functionality with sequence 4")
    print("="*60)
    
    success = await test_conditional_search_ka10173()
    
    print(f"\n🎯 Conditional search test completed!")
    print(f"Result: {'✅ SUCCESS' if success else '⚠️  PARTIAL SUCCESS'}")
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
        sys.exit(1) 