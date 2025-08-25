#!/usr/bin/env python3
"""
Samsung Stock Data Test

This script tests if the pyheroapi correctly retrieves Samsung Electronics (005930) stock information.
It tests both the basic client API and the easy API wrapper.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

import pyheroapi
from pyheroapi import KiwoomClient
from pyheroapi.exceptions import KiwoomAPIError, KiwoomAuthError


class SamsungStockTester:
    """Test class for Samsung stock data retrieval."""
    
    SAMSUNG_CODE = "005930"  # Samsung Electronics stock code
    SAMSUNG_NAME = "삼성전자"  # Samsung Electronics in Korean
    
    def __init__(self, app_key: str, secret_key: str, use_sandbox: bool = False):
        """Initialize the tester with API credentials."""
        self.app_key = app_key
        self.secret_key = secret_key
        self.use_sandbox = use_sandbox
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "samsung_code": self.SAMSUNG_CODE,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "data_retrieved": {}
        }
    
    def log_result(self, test_name: str, success: bool, data: Any = None, error: str = None):
        """Log test results."""
        if success:
            self.results["tests_passed"] += 1
            print(f"✅ {test_name}: PASSED")
            if data:
                self.results["data_retrieved"][test_name] = data
        else:
            self.results["tests_failed"] += 1
            print(f"❌ {test_name}: FAILED")
            if error:
                self.results["errors"].append(f"{test_name}: {error}")
                print(f"   Error: {error}")
    
    def test_basic_client_connection(self) -> bool:
        """Test basic client connection and authentication."""
        print("\n🔌 Testing Basic Client Connection...")
        try:
            client = KiwoomClient.create_with_credentials(
                appkey=self.app_key,
                secretkey=self.secret_key,
                is_production=not self.use_sandbox
            )
            self.log_result("Basic Client Connection", True)
            return True
        except Exception as e:
            self.log_result("Basic Client Connection", False, error=str(e))
            return False
    
    def test_easy_api_connection(self) -> bool:
        """Test easy API connection."""
        print("\n🚀 Testing Easy API Connection...")
        try:
            api = pyheroapi.connect(
                self.app_key, 
                self.secret_key, 
                sandbox=self.use_sandbox
            )
            api.disconnect()  # Clean up
            self.log_result("Easy API Connection", True)
            return True
        except Exception as e:
            self.log_result("Easy API Connection", False, error=str(e))
            return False
    
    def test_samsung_quote_basic_client(self) -> Dict[str, Any]:
        """Test Samsung quote retrieval using basic client."""
        print(f"\n📊 Testing Samsung Quote (Basic Client) - Code: {self.SAMSUNG_CODE}...")
        
        try:
            client = KiwoomClient.create_with_credentials(
                appkey=self.app_key,
                secretkey=self.secret_key,
                is_production=not self.use_sandbox
            )
            
            quote = client.get_quote(self.SAMSUNG_CODE)
            
            # Check if we got valid data and if attributes exist
            if hasattr(quote, 'buy_fpr_bid') or hasattr(quote, 'sel_fpr_bid'):
                buy_price = getattr(quote, 'buy_fpr_bid', None)
                sell_price = getattr(quote, 'sel_fpr_bid', None)
                
                # Convert string prices to numbers if they exist and are not "0"
                buy_price_num = None
                sell_price_num = None
                
                if buy_price and buy_price != "0":
                    try:
                        buy_price_num = float(buy_price)
                    except ValueError:
                        pass
                        
                if sell_price and sell_price != "0":
                    try:
                        sell_price_num = float(sell_price)
                    except ValueError:
                        pass
                
                quote_data = {
                    "buy_price": buy_price_num,
                    "sell_price": sell_price_num,
                    "total_buy_req": getattr(quote, 'tot_buy_req', None),
                    "total_sell_req": getattr(quote, 'tot_sel_req', None),
                }
                
                # Only consider it successful if we got meaningful price data
                if buy_price_num or sell_price_num:
                    self.log_result("Samsung Quote (Basic Client)", True, quote_data)
                    
                    # Print detailed quote information
                    print(f"   📈 Buy Price: ₩{buy_price_num:,}" if buy_price_num else "   📈 Buy Price: N/A")
                    print(f"   📉 Sell Price: ₩{sell_price_num:,}" if sell_price_num else "   📉 Sell Price: N/A")
                    
                    return quote_data
                else:
                    self.log_result("Samsung Quote (Basic Client)", False, error="Quote data exists but prices are zero or invalid")
                    return {}
            else:
                self.log_result("Samsung Quote (Basic Client)", False, error="QuoteData object missing expected price attributes")
                return {}
                
        except Exception as e:
            self.log_result("Samsung Quote (Basic Client)", False, error=str(e))
            return {}
    
    def test_samsung_quote_easy_api(self) -> Dict[str, Any]:
        """Test Samsung quote retrieval using easy API."""
        print(f"\n🎯 Testing Samsung Quote (Easy API) - Code: {self.SAMSUNG_CODE}...")
        
        try:
            with pyheroapi.connect(self.app_key, self.secret_key, sandbox=self.use_sandbox) as api:
                samsung = api.stock(self.SAMSUNG_CODE)
                
                # Test current price
                current_price = samsung.current_price
                print(f"   💰 Current Price: ₩{current_price:,}" if current_price else "   💰 Current Price: N/A")
                
                # Test quote data
                quote = samsung.quote
                
                if "error" not in quote:
                    self.log_result("Samsung Quote (Easy API)", True, quote)
                    
                    print(f"   📊 Quote Data:")
                    print(f"      Best Bid: ₩{quote.get('best_bid', 'N/A'):,}" if quote.get('best_bid') else "      Best Bid: N/A")
                    print(f"      Best Ask: ₩{quote.get('best_ask', 'N/A'):,}" if quote.get('best_ask') else "      Best Ask: N/A")
                    print(f"      Bid Quantity: {quote.get('total_bid_quantity', 'N/A'):,}" if quote.get('total_bid_quantity') else "      Bid Quantity: N/A")
                    print(f"      Ask Quantity: {quote.get('total_ask_quantity', 'N/A'):,}" if quote.get('total_ask_quantity') else "      Ask Quantity: N/A")
                    
                    return quote
                else:
                    self.log_result("Samsung Quote (Easy API)", False, error=quote.get("error", "Unknown error"))
                    return {}
                    
        except Exception as e:
            self.log_result("Samsung Quote (Easy API)", False, error=str(e))
            return {}
    
    def test_samsung_market_data(self) -> Dict[str, Any]:
        """Test Samsung market data retrieval."""
        print(f"\n📈 Testing Samsung Market Data - Code: {self.SAMSUNG_CODE}...")
        
        try:
            client = KiwoomClient.create_with_credentials(
                appkey=self.app_key,
                secretkey=self.secret_key,
                is_production=not self.use_sandbox
            )
            
            market_data = client.get_market_data(self.SAMSUNG_CODE)
            
            if market_data:
                # Extract relevant data
                market_info = {
                    "data_received": True,
                    "data_type": type(market_data).__name__,
                    "has_price_data": hasattr(market_data, 'stk_prpr') if hasattr(market_data, 'stk_prpr') else False,
                }
                
                self.log_result("Samsung Market Data", True, market_info)
                print(f"   📊 Market data retrieved successfully")
                print(f"   📋 Data type: {market_info['data_type']}")
                
                return market_info
            else:
                self.log_result("Samsung Market Data", False, error="No market data received")
                return {}
                
        except Exception as e:
            self.log_result("Samsung Market Data", False, error=str(e))
            return {}
    
    def test_samsung_historical_data(self) -> Dict[str, Any]:
        """Test Samsung historical price data retrieval."""
        print(f"\n📅 Testing Samsung Historical Data - Code: {self.SAMSUNG_CODE}...")
        
        try:
            with pyheroapi.connect(self.app_key, self.secret_key, sandbox=self.use_sandbox) as api:
                samsung = api.stock(self.SAMSUNG_CODE)
                
                # Get last 5 days of data
                history = samsung.history(days=5)
                
                if history and len(history) > 0:
                    self.log_result("Samsung Historical Data", True, {"days_retrieved": len(history)})
                    
                    print(f"   📊 Retrieved {len(history)} days of historical data:")
                    for i, day in enumerate(history[:3]):  # Show first 3 days
                        date = day.get('date', 'N/A')
                        close = day.get('close')
                        volume = day.get('volume')
                        
                        print(f"   📅 {date}: ₩{close:,}" if close else f"   📅 {date}: Price N/A")
                        if volume:
                            print(f"      Volume: {volume:,}")
                    
                    if len(history) > 3:
                        print(f"   ... and {len(history) - 3} more days")
                    
                    return {"days_retrieved": len(history), "sample_data": history[:3]}
                else:
                    self.log_result("Samsung Historical Data", False, error="No historical data received")
                    return {}
                    
        except Exception as e:
            self.log_result("Samsung Historical Data", False, error=str(e))
            return {}
    
    def test_search_samsung(self) -> bool:
        """Test searching for Samsung stock."""
        print(f"\n🔍 Testing Samsung Stock Search...")
        
        try:
            with pyheroapi.connect(self.app_key, self.secret_key, sandbox=self.use_sandbox) as api:
                # Search for Samsung using Korean name
                results = api.search_stocks("삼성", limit=5)
                
                if results and len(results) > 0:
                    # Check if Samsung Electronics is in the results
                    samsung_found = any(
                        result.get('symbol') == self.SAMSUNG_CODE or 
                        self.SAMSUNG_CODE in str(result) for result in results
                    )
                    
                    self.log_result("Samsung Search", True, {"results_count": len(results), "samsung_found": samsung_found})
                    
                    print(f"   🔍 Found {len(results)} search results:")
                    for result in results[:3]:  # Show first 3 results
                        print(f"      {result}")
                    
                    if samsung_found:
                        print(f"   ✅ Samsung Electronics ({self.SAMSUNG_CODE}) found in results!")
                    else:
                        print(f"   ⚠️ Samsung Electronics ({self.SAMSUNG_CODE}) not found in search results")
                    
                    return samsung_found
                else:
                    self.log_result("Samsung Search", False, error="No search results")
                    return False
                    
        except Exception as e:
            self.log_result("Samsung Search", False, error=str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Samsung stock tests."""
        print("=" * 60)
        print("🧪 SAMSUNG ELECTRONICS STOCK DATA TEST")
        print("=" * 60)
        print(f"📊 Testing stock code: {self.SAMSUNG_CODE}")
        print(f"🏢 Company: {self.SAMSUNG_NAME}")
        print(f"🔧 Environment: {'Sandbox' if self.use_sandbox else 'Production'}")
        print(f"⏰ Test started: {self.results['timestamp']}")
        
        # Run connection tests
        basic_connected = self.test_basic_client_connection()
        easy_connected = self.test_easy_api_connection()
        
        if not basic_connected and not easy_connected:
            print("\n❌ CRITICAL: Both connection methods failed!")
            print("   Please check your API credentials and network connection.")
            return self.results
        
        # Run data retrieval tests
        if basic_connected:
            self.test_samsung_quote_basic_client()
            self.test_samsung_market_data()
        
        if easy_connected:
            self.test_samsung_quote_easy_api()
            self.test_samsung_historical_data()
            self.test_search_samsung()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.results['tests_passed']}")
        print(f"❌ Tests Failed: {self.results['tests_failed']}")
        print(f"📊 Success Rate: {(self.results['tests_passed'] / (self.results['tests_passed'] + self.results['tests_failed']) * 100):.1f}%" if (self.results['tests_passed'] + self.results['tests_failed']) > 0 else "0.0%")
        
        if self.results['errors']:
            print(f"\n❌ Errors encountered:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        if self.results['data_retrieved']:
            print(f"\n📦 Data successfully retrieved from:")
            for test_name in self.results['data_retrieved']:
                print(f"   ✓ {test_name}")
        
        print("\n🎯 Samsung Stock Test Complete!")
        
        return self.results


def main():
    """Main function to run the Samsung stock test."""
    
    # Get credentials from environment variables
    app_key = os.getenv("KIWOOM_APP_KEY")
    secret_key = os.getenv("KIWOOM_SECRET_KEY")
    
    if not app_key or not secret_key:
        print("❌ ERROR: Missing API credentials!")
        print("\nPlease set the following environment variables:")
        print("   export KIWOOM_APP_KEY='your_app_key_here'")
        print("   export KIWOOM_SECRET_KEY='your_secret_key_here'")
        print("\nOr pass them as arguments:")
        print("   python test_samsung_stock.py your_app_key your_secret_key")
        
        # Check if credentials were passed as arguments
        if len(sys.argv) >= 3:
            app_key = sys.argv[1]
            secret_key = sys.argv[2]
            print(f"\n✓ Using credentials from command line arguments")
        else:
            return
    
    # Determine environment (default to production since user has production keys)
    use_sandbox = False
    if len(sys.argv) >= 4 and sys.argv[3].lower() in ['sandbox', 'test', 'true']:
        use_sandbox = True
        print("ℹ️  Using SANDBOX environment for testing")
    else:
        print("🏭 Using PRODUCTION environment with real market data")
        print("   This will retrieve actual Samsung stock prices and data")
    
    # Run the tests
    tester = SamsungStockTester(app_key, secret_key, use_sandbox)
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results['tests_failed'] == 0:
        print("\n🎉 All tests passed! Samsung stock data retrieval is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {results['tests_failed']} test(s) failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 