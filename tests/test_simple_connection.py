#!/usr/bin/env python3
"""
Simple WebSocket connection test without subscriptions.

This test verifies that the basic WebSocket connection works
without attempting any data subscriptions that might require
special account permissions.
"""

import asyncio
import os
import sys
import pytest

# Add the parent directory to Python path to import pyheroapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from pyheroapi.realtime import create_realtime_client
    from pyheroapi.client import KiwoomClient
    print("✅ PyHero API modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PyHero API: {e}")
    sys.exit(1)


@pytest.mark.asyncio
async def test_simple_connection():
    """Test basic WebSocket connection without subscriptions."""
    print("🔍 Testing Simple WebSocket Connection")
    print("="*50)
    
    # Get access token
    app_key = os.getenv('KIWOOM_APPKEY')
    secret_key = os.getenv('KIWOOM_SECRETKEY')
    
    if not app_key or not secret_key:
        print("❌ Missing KIWOOM_APPKEY or KIWOOM_SECRETKEY")
        return False
    
    print("🔑 Getting access token...")
    try:
        token_response = await asyncio.get_event_loop().run_in_executor(
            None, KiwoomClient.issue_token, app_key, secret_key, True
        )
        
        if not (token_response and hasattr(token_response, 'token')):
            print("❌ Failed to get access token")
            return False
            
        access_token = token_response.token
        print(f"✅ Access token obtained")
        
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return False
    
    # Test basic connection
    print("\n🔌 Testing WebSocket connection...")
    client = create_realtime_client(
        access_token=access_token,
        is_production=True
    )
    
    try:
        # Connect
        await client.connect()
        print(f"✅ Connected successfully: {client.is_connected}")
        
        # Hold connection for a few seconds without subscribing
        print("⏱️  Holding connection for 5 seconds...")
        await asyncio.sleep(5)
        print("✅ Connection held successfully")
        
        # Test basic ping/pong or keep-alive
        print("🏓 Testing connection stability...")
        await asyncio.sleep(3)
        
        if client.is_connected:
            print("✅ Connection is stable")
            result = True
        else:
            print("❌ Connection lost during test")
            result = False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        result = False
    finally:
        print("\n🔌 Disconnecting...")
        await client.disconnect()
        print("✅ Disconnected successfully")
    
    return result


async def main():
    """Main function."""
    print("🔥 PyHero API - Simple Connection Test")
    print("="*50)
    print("This test checks basic WebSocket connectivity")
    print("without attempting any data subscriptions.")
    print("="*50)
    
    success = await test_simple_connection()
    
    if success:
        print("\n✅ SUCCESS: Basic WebSocket connection works!")
        print("\n💡 Next steps:")
        print("   1. Contact Kiwoom Securities to enable real-time data permissions")
        print("   2. Ask about API subscription level for market data streaming")
        print("   3. Verify account type supports real-time API access")
        print("   4. Request documentation for required permissions")
    else:
        print("\n❌ FAILED: Basic WebSocket connection issues")
        print("\n🔧 Troubleshooting:")
        print("   1. Check internet connectivity")
        print("   2. Verify API credentials are correct")
        print("   3. Try during different market hours")
        print("   4. Check if API endpoint is accessible from your network")
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
        sys.exit(1) 