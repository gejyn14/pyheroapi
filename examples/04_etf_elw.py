"""
PyHero API - ETF & ELW Example

This example demonstrates:
1. ETF information and analysis
2. ETF market data and trends
3. ELW information and sensitivity analysis
4. ELW rankings and movement tracking
5. ETF/ELW trading data
6. Advanced ETF/ELW analytics
"""

import os
from datetime import datetime
from pyheroapi import KiwoomClient
from pyheroapi.exceptions import KiwoomAPIError

def setup_client():
    """Setup API client"""
    appkey = os.getenv("KIWOOM_APPKEY", "your_app_key_here")
    secretkey = os.getenv("KIWOOM_SECRETKEY", "your_secret_key_here")
    
    if appkey == "your_app_key_here":
        print("Please set KIWOOM_APPKEY and KIWOOM_SECRETKEY environment variables")
        return None
    
    return KiwoomClient.create_with_credentials(
        appkey=appkey,
        secretkey=secretkey,
        is_production=False  # SANDBOX MODE: set is_production=False explicitly
    )

def etf_basic_info_example(client):
    """ETF basic information and data example"""
    
    print("=== ETF Basic Information ===\n")
    
    # Popular Korean ETFs
    etf_symbols = ["069500", "114800", "122630", "102110", "238720"]
    etf_names = ["KODEX 200", "KODEX 인버스", "KODEX 레버리지", "KODEX 중국본토대형주", "KODEX 코스닥150선물인버스"]
    
    for symbol, name in zip(etf_symbols, etf_names):
        try:
            print(f"📊 {name} ({symbol}):")
            
            etf_info = client.get_etf_info(symbol)
            print(f"  Name: {etf_info.name}")
            print(f"  NAV: {etf_info.nav}")
            print(f"  Tracking Error: {etf_info.tracking_error}%")
            print(f"  Premium/Discount: {etf_info.discount_premium}%")
            
            daily_trend = client.get_etf_daily_trend(symbol)
            if daily_trend:
                latest = daily_trend[0] if daily_trend else {}
                print(f"  Latest Price: {latest.get('cur_prc', 'N/A')}")
                print(f"  Change Rate: {latest.get('flu_rt', 'N/A')}%")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()

def elw_analysis_example(client):
    """ELW analysis example"""
    
    print("=== ELW Analysis ===\n")
    
    try:
        # Find active ELWs
        print("🔍 Active ELW Search:")
        elw_search = client.get_elw_condition_search(
            underlying_asset_code="201",  # KOSPI 200
            right_type="1",  # Call options
            sort_type="1"
        )
        
        if elw_search:
            print(f"  Found {len(elw_search)} ELWs")
            
            # Analyze first ELW
            for elw in elw_search[:2]:
                symbol = elw.get('stk_cd')
                if not symbol:
                    continue
                    
                print(f"\n📈 ELW Analysis ({symbol}):")
                
                try:
                    elw_info = client.get_elw_info(symbol)
                    print(f"  Name: {elw_info.name}")
                    print(f"  Strike Price: {elw_info.strike_price}")
                    print(f"  Expiry: {elw_info.expiry_date}")
                    print(f"  Delta: {elw_info.delta}")
                    
                    # ELW rankings
                    fluctuation = client.get_elw_fluctuation_rate_ranking(
                        sort_type="1",
                        right_type="001"
                    )
                    if fluctuation:
                        print(f"  Fluctuation ranking: {len(fluctuation)} records")
                
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                break
        
    except Exception as e:
        print(f"✗ Error in ELW analysis: {e}")

def main():
    """Main function"""
    
    print("🚀 PyHero API - ETF & ELW Example\n")
    
    client = setup_client()
    if not client:
        return
    
    try:
        etf_basic_info_example(client)
        elw_analysis_example(client)
        
        print("\n✓ ETF & ELW examples completed!")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main() 