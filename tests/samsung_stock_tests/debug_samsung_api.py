#!/usr/bin/env python3
"""
Debug Samsung API Response

This script helps debug what exactly the Kiwoom API returns for Samsung stock.
It shows the raw response structure to help fix the data parsing issues.
"""

import json
import os
import sys
from pprint import pprint

try:
    import pyheroapi
    from pyheroapi import KiwoomClient
    print("✅ Successfully imported pyheroapi")
except ImportError as e:
    print(f"❌ Failed to import pyheroapi: {e}")
    sys.exit(1)


def debug_samsung_api():
    """Debug Samsung API responses."""
    
    print("🔍 Samsung API Debug Session")
    print("=" * 50)
    
    # Get credentials
    app_key = os.getenv("KIWOOM_APP_KEY")
    secret_key = os.getenv("KIWOOM_SECRET_KEY")
    
    if len(sys.argv) >= 3:
        app_key = sys.argv[1]
        secret_key = sys.argv[2]
        print("📋 Using credentials from command line")
    elif not app_key or not secret_key:
        print("❌ No credentials found!")
        print("Usage: python debug_samsung_api.py [app_key] [secret_key]")
        return False
    
    samsung_code = "005930"
    
    try:
        print(f"\n🔗 Connecting to production API...")
        client = KiwoomClient.create_with_credentials(
            appkey=app_key,
            secretkey=secret_key,
            is_production=True
        )
        print("✅ Connected successfully")
        
        print(f"\n📊 Getting raw quote data for Samsung ({samsung_code})...")
        try:
            quote = client.get_quote(samsung_code)
            print(f"✅ Quote retrieved successfully")
            print(f"📋 Quote object type: {type(quote)}")
            
            # Print all attributes of the quote object
            print(f"\n📝 Quote object attributes:")
            if hasattr(quote, '__dict__'):
                for attr, value in quote.__dict__.items():
                    print(f"   {attr}: {value} (type: {type(value).__name__})")
            else:
                print("   No __dict__ attribute found")
                
            # Print dir() output to see all available methods/attributes
            print(f"\n🔍 All quote object attributes (dir()):")
            attrs = [attr for attr in dir(quote) if not attr.startswith('_')]
            for attr in attrs[:20]:  # Limit to first 20 to avoid spam
                try:
                    value = getattr(quote, attr)
                    if not callable(value):
                        print(f"   {attr}: {value}")
                except:
                    print(f"   {attr}: <could not access>")
            
            # Try to convert to dict if possible
            print(f"\n📋 Attempting to serialize quote data...")
            try:
                if hasattr(quote, 'model_dump'):
                    quote_dict = quote.model_dump()
                    print("✅ Using model_dump():")
                    pprint(quote_dict)
                elif hasattr(quote, 'dict'):
                    quote_dict = quote.dict()
                    print("✅ Using dict():")
                    pprint(quote_dict)
                else:
                    print("⚠️ No serialization method found")
            except Exception as e:
                print(f"❌ Serialization failed: {e}")
                
        except Exception as e:
            print(f"❌ Quote retrieval failed: {e}")
            
        # Try with easy API
        print(f"\n🚀 Testing with Easy API...")
        try:
            with pyheroapi.connect(app_key, secret_key, sandbox=False) as api:
                samsung = api.stock(samsung_code)
                print(f"✅ Created stock object")
                
                # Try current_price
                print(f"\n💰 Testing current_price property...")
                try:
                    price = samsung.current_price
                    print(f"✅ Current price: {price}")
                except Exception as e:
                    print(f"❌ Current price failed: {e}")
                
                # Try quote
                print(f"\n📊 Testing quote property...")
                try:
                    quote = samsung.quote
                    print(f"✅ Quote type: {type(quote)}")
                    if isinstance(quote, dict):
                        print("📋 Quote contents:")
                        pprint(quote)
                    else:
                        print(f"📋 Quote value: {quote}")
                except Exception as e:
                    print(f"❌ Quote failed: {e}")
                    
        except Exception as e:
            print(f"❌ Easy API failed: {e}")
        
        print(f"\n🔍 Debug session completed")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    debug_samsung_api() 