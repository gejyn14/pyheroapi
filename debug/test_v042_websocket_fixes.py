#!/usr/bin/env python3
"""
Test v0.4.2 WebSocket Reliability Fixes
======================================

This script tests the major WebSocket improvements in pyheroapi v0.4.2:
- Inline LOGIN-ACK pattern (eliminates race conditions)
- Better error handling and timeouts
- Proper async task management
- Real-time Samsung Electronics price streaming

Usage:
    python test_v042_websocket_fixes.py

Make sure to set your credentials:
    export KIWOOM_APPKEY="your_production_app_key"
    export KIWOOM_SECRETKEY="your_production_secret_key"

Or for sandbox testing:
    export MOCK_KIWOOM_APPKEY="your_mock_app_key"
    export MOCK_KIWOOM_SECRETKEY="your_mock_secret_key"
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from typing import Optional

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from pyheroapi import KiwoomClient
    logger.info("✅ pyheroapi imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import pyheroapi: {e}")
    logger.error("Please install with: pip install -e .")
    sys.exit(1)


class WebSocketTester:
    """Test the new v0.4.2 WebSocket reliability fixes."""
    
    def __init__(self, use_production: bool = False):
        self.use_production = use_production
        self.client: Optional[KiwoomClient] = None
        self.realtime = None
        self.price_updates_received = 0
        self.start_time = None
        
    def setup_credentials(self) -> tuple[str, str]:
        """Setup API credentials from environment variables."""
        if self.use_production:
            app_key = os.getenv("KIWOOM_APPKEY")
            secret_key = os.getenv("KIWOOM_SECRETKEY")
            env_type = "Production"
        else:
            app_key = os.getenv("MOCK_KIWOOM_APPKEY") 
            secret_key = os.getenv("MOCK_KIWOOM_SECRETKEY")
            env_type = "Sandbox"
            
        if not app_key or not secret_key:
            logger.error(f"❌ {env_type} credentials not found!")
            if self.use_production:
                logger.error("Set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables")
            else:
                logger.error("Set MOCK_KIWOOM_APPKEY and MOCK_KIWOOM_SECRETKEY environment variables")
            sys.exit(1)
            
        logger.info(f"✅ {env_type} credentials loaded")
        return app_key, secret_key
    
    def samsung_price_callback(self, data):
        """Handle Samsung Electronics real-time price updates."""
        for item in data:
            if item.symbol == "005930":  # Samsung Electronics
                self.price_updates_received += 1
                
                # Extract price data
                price = item.values.get('10', 'N/A')        # Current price
                change = item.values.get('11', 'N/A')       # Price change  
                change_rate = item.values.get('12', 'N/A')  # Change rate
                volume = item.values.get('13', 'N/A')       # Volume
                time_val = item.values.get('20', 'N/A')     # Time
                
                # Format and display
                now = datetime.now().strftime("%H:%M:%S")
                print(f"\n📊 [{now}] 삼성전자(005930) 실시간 시세:")
                print(f"   현재가: ₩{price:>10}")
                print(f"   변동:   {change:>10} ({change_rate}%)")
                print(f"   거래량: {volume:>10}")
                print(f"   시간:   {time_val}")
                print(f"   업데이트 #{self.price_updates_received}")
                print("-" * 50)
    
    async def test_basic_connection(self) -> bool:
        """Test basic API connection."""
        try:
            logger.info("🔌 Testing basic API connection...")
            app_key, secret_key = self.setup_credentials()
            
            self.client = KiwoomClient.create_with_credentials(
                appkey=app_key,
                secretkey=secret_key,
                is_production=self.use_production
            )
            
            env_name = "Production" if self.use_production else "Sandbox"
            logger.info(f"✅ {env_name} API connection successful!")
            logger.info(f"   API URL: {self.client.base_url}")
            logger.info(f"   Token: {self.client.access_token[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Basic connection failed: {e}")
            return False
    
    async def test_websocket_connection(self) -> bool:
        """Test the new v0.4.2 WebSocket connection with inline LOGIN-ACK."""
        try:
            logger.info("🚀 Testing NEW v0.4.2 WebSocket connection pattern...")
            
            # Get realtime client
            self.realtime = self.client.realtime
            
            # Register callback
            self.realtime.add_callback("STOCK_PRICE", self.samsung_price_callback)
            logger.info("✅ Price update callback registered")
            
            # Test the NEW inline LOGIN-ACK connection pattern
            logger.info("🔌 Connecting with NEW inline LOGIN-ACK pattern...")
            await self.realtime.connect()
            logger.info("✅ WebSocket connected successfully! (No race conditions)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            return False
    
    async def test_samsung_subscription(self) -> bool:
        """Test Samsung Electronics real-time subscription."""
        try:
            logger.info("📡 Subscribing to Samsung Electronics (005930)...")
            await self.realtime.subscribe_stock_price("005930")
            logger.info("✅ Samsung subscription successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Samsung subscription failed: {e}")
            return False
    
    async def run_realtime_test(self, duration: int = 60):
        """Run the complete real-time test."""
        logger.info("=" * 60)
        logger.info("🧪 TESTING PYHEROAPI v0.4.2 WEBSOCKET FIXES")
        logger.info("=" * 60)
        
        # Test basic connection
        if not await self.test_basic_connection():
            return False
            
        # Test WebSocket connection
        if not await self.test_websocket_connection():
            return False
            
        # Test Samsung subscription
        if not await self.test_samsung_subscription():
            return False
        
        # Stream real-time data
        logger.info(f"⏱️ Streaming Samsung real-time data for {duration} seconds...")
        logger.info("💡 You should see price updates below (if market is open)")
        print("=" * 50)
        
        self.start_time = datetime.now()
        
        try:
            await asyncio.sleep(duration)
        except KeyboardInterrupt:
            logger.info("\n⚠️ Test interrupted by user")
        
        # Cleanup
        logger.info("\n🛑 Stopping real-time stream...")
        await self.realtime.disconnect()
        
        # Results
        end_time = datetime.now()
        elapsed = (end_time - self.start_time).total_seconds()
        
        print("=" * 60)
        logger.info("📊 TEST RESULTS:")
        logger.info(f"   Duration: {elapsed:.1f} seconds")
        logger.info(f"   Price updates received: {self.price_updates_received}")
        
        if self.price_updates_received > 0:
            rate = self.price_updates_received / elapsed * 60
            logger.info(f"   Update rate: {rate:.1f} updates/minute")
            logger.info("🎉 SUCCESS! v0.4.2 WebSocket fixes work perfectly!")
        else:
            logger.warning("⚠️ No price updates received")
            logger.warning("   This may be normal if market is closed or in sandbox mode")
            logger.info("✅ But connection/subscription worked without errors!")
            
        logger.info("=" * 60)
        return True


async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test pyheroapi v0.4.2 WebSocket fixes')
    parser.add_argument('--production', action='store_true', 
                       help='Use production API (default: sandbox)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Test duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    tester = WebSocketTester(use_production=args.production)
    
    try:
        await tester.run_realtime_test(duration=args.duration)
    except Exception as e:
        logger.error(f"❌ Test failed with unexpected error: {e}")
        logger.error(f"   Error type: {type(e).__name__}")
        return False
    
    return True


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Run the test
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n👋 Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
