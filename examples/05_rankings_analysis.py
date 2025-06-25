"""
PyHero API - Rankings & Market Analysis Example

This example demonstrates:
1. Stock rankings (volume, price change, etc.)
2. Foreign and institutional trading rankings
3. Order book and market rankings
4. Sector and theme analysis
5. Program trading rankings
6. Market performance indicators
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

def volume_rankings_example(client):
    """Volume and trading activity rankings"""
    
    print("=== Volume & Trading Rankings ===\n")
    
    try:
        # Current day volume ranking
        print("📊 Current Day Volume Rankings:")
        volume_ranking = client.get_current_day_volume_ranking(
            market_type="001",  # KOSPI
            sort_type="1",      # Volume top
            volume_type="0000", # All volumes
            stock_condition="0", # All stocks
            credit_condition="0" # All credit conditions
        )
        
        if volume_ranking:
            print(f"  Found {len(volume_ranking)} stocks")
            print("  🔥 Top 5 by Volume:")
            print("     Rank | Symbol | Name | Volume | Price | Change%")
            print("     " + "-" * 55)
            
            for i, stock in enumerate(volume_ranking[:5]):
                print(f"     #{i+1:<3} | {stock.get('stk_cd', 'N/A'):<6} | "
                      f"{stock.get('stk_nm', 'N/A')[:10]:<10} | "
                      f"{stock.get('trde_qty', 'N/A'):<8} | "
                      f"{stock.get('cur_prc', 'N/A'):<5} | "
                      f"{stock.get('flu_rt', 'N/A')}")
        
        # Trading value ranking
        print("\n💰 Trading Value Rankings:")
        value_ranking = client.get_trading_value_ranking(
            market_type="001",
            sort_type="1"
        )
        
        if value_ranking:
            print(f"  Top trading value stocks: {len(value_ranking)}")
            for i, stock in enumerate(value_ranking[:3]):
                print(f"    #{i+1}: {stock.get('stk_nm', 'N/A')} "
                      f"Value: {stock.get('trde_prica', 'N/A')}")
        
        # Volume surge ranking
        print("\n🚀 Volume Surge Rankings:")
        surge_ranking = client.get_volume_surge_ranking(
            market_type="001",
            sort_type="1"  # Volume surge
        )
        
        if surge_ranking:
            print(f"  Volume surge stocks: {len(surge_ranking)}")
            for i, stock in enumerate(surge_ranking[:3]):
                print(f"    #{i+1}: {stock.get('stk_nm', 'N/A')} "
                      f"Surge Rate: {stock.get('surge_rate', 'N/A')}%")
        
    except Exception as e:
        print(f"✗ Error in volume rankings: {e}")

def price_change_rankings_example(client):
    """Price change and movement rankings"""
    
    print("\n=== Price Change Rankings ===\n")
    
    try:
        # Change rate ranking (gainers)
        print("📈 Top Gainers (KOSPI):")
        gainers = client.get_change_rate_ranking(
            market_type="001",  # KOSPI
            sort_type="1",      # Up rate
            volume_type="0010", # 10k+ volume
            stock_condition="1" # Exclude managed stocks
        )
        
        if gainers:
            print("  🚀 Top 5 Gainers:")
            print("     Symbol | Name | Price | Change | Change%")
            print("     " + "-" * 50)
            
            for i, stock in enumerate(gainers[:5]):
                print(f"     {stock.get('stk_cd', 'N/A'):<6} | "
                      f"{stock.get('stk_nm', 'N/A')[:10]:<10} | "
                      f"{stock.get('cur_prc', 'N/A'):<5} | "
                      f"{stock.get('flu_amt', 'N/A'):<6} | "
                      f"{stock.get('flu_rt', 'N/A')}")
        
        # Losers
        print("\n📉 Top Losers (KOSPI):")
        losers = client.get_change_rate_ranking(
            market_type="001",  # KOSPI
            sort_type="2",      # Down rate
            volume_type="0010"
        )
        
        if losers:
            print("  📉 Top 5 Losers:")
            for i, stock in enumerate(losers[:5]):
                print(f"     {stock.get('stk_cd', 'N/A'):<6} | "
                      f"{stock.get('stk_nm', 'N/A')[:10]:<10} | "
                      f"{stock.get('cur_prc', 'N/A'):<5} | "
                      f"{stock.get('flu_rt', 'N/A')}")
        
        # KOSDAQ rankings
        print("\n💎 KOSDAQ Top Gainers:")
        kosdaq_gainers = client.get_change_rate_ranking(
            market_type="101",  # KOSDAQ
            sort_type="1"
        )
        
        if kosdaq_gainers:
            print(f"  KOSDAQ gainers: {len(kosdaq_gainers)}")
            for i, stock in enumerate(kosdaq_gainers[:3]):
                print(f"    #{i+1}: {stock.get('stk_nm', 'N/A')} "
                      f"({stock.get('flu_rt', 'N/A')}%)")
        
    except Exception as e:
        print(f"✗ Error in price change rankings: {e}")

def foreign_institutional_rankings_example(client):
    """Foreign and institutional trading rankings"""
    
    print("\n=== Foreign & Institutional Rankings ===\n")
    
    try:
        # Foreign trading rankings
        print("🌍 Foreign Trading Rankings:")
        foreign_ranking = client.get_foreign_period_trading_ranking(
            market_type="001",  # KOSPI
            sort_type="1",      # Net buying
            period_type="1",    # 1 day
            volume_type="0010"  # 10k+ volume
        )
        
        if foreign_ranking:
            print(f"  🌍 Top Foreign Net Buying (1-day):")
            print("     Symbol | Name | Net Buy Amount")
            print("     " + "-" * 40)
            
            for i, stock in enumerate(foreign_ranking[:5]):
                print(f"     {stock.get('stk_cd', 'N/A'):<6} | "
                      f"{stock.get('stk_nm', 'N/A')[:15]:<15} | "
                      f"{stock.get('net_buy_amt', 'N/A')}")
        
        # Foreign consecutive trading
        print("\n🔄 Foreign Consecutive Trading:")
        foreign_consecutive = client.get_foreign_consecutive_trading_ranking(
            market_type="001",
            sort_type="1",  # Net buying consecutive
            volume_type="0010"
        )
        
        if foreign_consecutive:
            print(f"  Consecutive foreign buying: {len(foreign_consecutive)}")
            for i, stock in enumerate(foreign_consecutive[:3]):
                print(f"    #{i+1}: {stock.get('stk_nm', 'N/A')} "
                      f"Days: {stock.get('consecutive_days', 'N/A')}")
        
        # Institutional rankings
        print("\n🏛️ Institutional Trading Rankings:")
        institutional_ranking = client.get_foreign_institutional_trading_ranking(
            market_type="001",
            sort_type="1",  # Net buying
            volume_type="0010"
        )
        
        if institutional_ranking:
            print(f"  Institutional net buying: {len(institutional_ranking)}")
            for i, stock in enumerate(institutional_ranking[:3]):
                print(f"    #{i+1}: {stock.get('stk_nm', 'N/A')} "
                      f"Net: {stock.get('net_buy_amt', 'N/A')}")
        
        # Securities firm ranking
        print("\n🏦 Securities Firm Rankings:")
        securities_ranking = client.get_securities_firm_trading_ranking(
            market_type="001",
            sort_type="1"  # Net buying
        )
        
        if securities_ranking:
            print(f"  Securities firm trading: {len(securities_ranking)}")
            for i, record in enumerate(securities_ranking[:3]):
                print(f"    #{i+1}: {record.get('stk_nm', 'N/A')} "
                      f"Firm: {record.get('scrt_nm', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Error in foreign/institutional rankings: {e}")

def order_book_rankings_example(client):
    """Order book and market depth rankings"""
    
    print("\n=== Order Book Rankings ===\n")
    
    try:
        # Order book rankings
        print("📋 Order Book Rankings:")
        order_book_ranking = client.get_order_book_ranking(
            market_type="001",  # KOSPI
            sort_type="1",      # Net buy order quantity
            volume_type="0010", # 10k+ volume
            stock_condition="1" # Exclude managed stocks
        )
        
        if order_book_ranking:
            print(f"  📊 Order Book Leaders:")
            print("     Symbol | Name | Buy Orders | Sell Orders | Ratio")
            print("     " + "-" * 55)
            
            for i, stock in enumerate(order_book_ranking[:5]):
                print(f"     {stock.get('stk_cd', 'N/A'):<6} | "
                      f"{stock.get('stk_nm', 'N/A')[:10]:<10} | "
                      f"{stock.get('buy_ord_qty', 'N/A'):<10} | "
                      f"{stock.get('sel_ord_qty', 'N/A'):<11} | "
                      f"{stock.get('ord_ratio', 'N/A')}")
        
        # Order book surge ranking
        print("\n⚡ Order Book Surge Rankings:")
        order_surge = client.get_order_book_surge_ranking(
            market_type="001",
            sort_type="1"  # Buy order surge
        )
        
        if order_surge:
            print(f"  Order surge stocks: {len(order_surge)}")
            for i, stock in enumerate(order_surge[:3]):
                print(f"    #{i+1}: {stock.get('stk_nm', 'N/A')} "
                      f"Surge: {stock.get('surge_rate', 'N/A')}%")
        
        # Remaining volume rate surge
        print("\n📊 Remaining Volume Rate Surge:")
        volume_rate_surge = client.get_remaining_volume_rate_surge_ranking(
            market_type="001",
            sort_type="1"  # Buy volume rate surge
        )
        
        if volume_rate_surge:
            print(f"  Volume rate surge: {len(volume_rate_surge)}")
            for i, stock in enumerate(volume_rate_surge[:3]):
                print(f"    #{i+1}: {stock.get('stk_nm', 'N/A')} "
                      f"Rate: {stock.get('vol_rate', 'N/A')}%")
        
    except Exception as e:
        print(f"✗ Error in order book rankings: {e}")

def credit_trading_rankings_example(client):
    """Credit trading and margin rankings"""
    
    print("\n=== Credit Trading Rankings ===\n")
    
    try:
        # Credit ratio ranking
        print("💳 Credit Ratio Rankings:")
        credit_ranking = client.get_credit_ratio_ranking(
            market_type="001",  # KOSPI
            sort_type="1",      # High credit ratio
            volume_type="0010"  # 10k+ volume
        )
        
        if credit_ranking:
            print(f"  💳 High Credit Ratio Stocks:")
            print("     Symbol | Name | Price | Credit Ratio")
            print("     " + "-" * 45)
            
            for i, stock in enumerate(credit_ranking[:5]):
                print(f"     {stock.get('stk_cd', 'N/A'):<6} | "
                      f"{stock.get('stk_nm', 'N/A')[:12]:<12} | "
                      f"{stock.get('cur_prc', 'N/A'):<5} | "
                      f"{stock.get('credit_ratio', 'N/A')}%")
        
        # After-hours single price change ranking
        print("\n🌙 After-Hours Rankings:")
        after_hours = client.get_after_hours_single_price_change_ranking(
            market_type="001",
            sort_type="1"  # Up rate
        )
        
        if after_hours:
            print(f"  After-hours leaders: {len(after_hours)}")
            for i, stock in enumerate(after_hours[:3]):
                print(f"    #{i+1}: {stock.get('stk_nm', 'N/A')} "
                      f"Change: {stock.get('flu_rt', 'N/A')}%")
        
    except Exception as e:
        print(f"✗ Error in credit trading rankings: {e}")

def sector_analysis_example(client):
    """Sector and industry analysis"""
    
    print("\n=== Sector Analysis ===\n")
    
    try:
        # All sector indices
        print("🏢 Sector Index Overview:")
        sector_indices = client.get_all_sector_indices(market_type="0")  # All markets
        
        if sector_indices:
            print(f"  📊 Found {len(sector_indices)} sector indices")
            print("     Code | Name | Current | Change%")
            print("     " + "-" * 45)
            
            for i, sector in enumerate(sector_indices[:8]):  # Show first 8 sectors
                print(f"     {sector.get('sector_cd', 'N/A'):<4} | "
                      f"{sector.get('sector_nm', 'N/A')[:15]:<15} | "
                      f"{sector.get('cur_prc', 'N/A'):<7} | "
                      f"{sector.get('flu_rt', 'N/A')}")
        
        # Sector investor analysis
        print("\n👥 Sector Investor Analysis:")
        sector_investor = client.get_sector_investor_net_buying(
            market_type="0",         # All markets
            amount_quantity_type="0", # Amount basis
            base_date="",            # Today
            exchange_type="3"        # Integrated exchange
        )
        
        if sector_investor:
            print(f"  Sector investor data: {len(sector_investor)} records")
            for i, record in enumerate(sector_investor[:3]):
                print(f"    #{i+1}: {record.get('sector_nm', 'N/A')} "
                      f"Net: {record.get('net_buy_amt', 'N/A')}")
        
        # Individual sector analysis
        print("\n🔍 Individual Sector Analysis:")
        try:
            # Analyze a specific sector (e.g., semiconductor - code 001)
            sector_detail = client.get_sector_current_price("001")  # General electric/electronics
            if sector_detail:
                print(f"  Sector Current Price: {sector_detail.get('cur_prc', 'N/A')}")
                print(f"  Sector Change: {sector_detail.get('flu_rt', 'N/A')}%")
            
            # Get stocks in the sector
            sector_stocks = client.get_sector_stock_prices("001")
            if sector_stocks:
                print(f"  Stocks in sector: {len(sector_stocks)}")
                print("    Top 3 stocks:")
                for i, stock in enumerate(sector_stocks[:3]):
                    print(f"      {stock.get('stk_nm', 'N/A')} "
                          f"({stock.get('flu_rt', 'N/A')}%)")
            
        except Exception as e:
            print(f"  Error in sector detail analysis: {e}")
        
    except Exception as e:
        print(f"✗ Error in sector analysis: {e}")

def program_trading_analysis_example(client):
    """Program trading analysis"""
    
    print("\n=== Program Trading Analysis ===\n")
    
    try:
        # Program trading net buy top 50
        print("🤖 Program Trading Leaders:")
        today = datetime.now().strftime("%Y%m%d")
        
        program_top50 = client.get_program_net_buy_top50(today)
        
        if program_top50:
            print(f"  📊 Program Trading Top 50:")
            print("     Symbol | Name | Program Net Buy")
            print("     " + "-" * 40)
            
            for i, stock in enumerate(program_top50[:5]):
                print(f"     {stock.get('stk_cd', 'N/A'):<6} | "
                      f"{stock.get('stk_nm', 'N/A')[:15]:<15} | "
                      f"{stock.get('prog_net_buy', 'N/A')}")
        
        # Program trading hourly
        print("\n⏰ Program Trading (Hourly):")
        program_hourly = client.get_program_trading_hourly()
        
        if program_hourly:
            print(f"  Hourly program data: {len(program_hourly)} records")
            if program_hourly:
                latest = program_hourly[0]
                print(f"  Latest hour value: {latest.get('trde_prica', 'N/A')}")
        
        # Program trading daily
        print("\n📅 Program Trading (Daily):")
        program_daily = client.get_program_trading_daily()
        
        if program_daily:
            print(f"  Daily program data: {len(program_daily)} records")
        
    except Exception as e:
        print(f"✗ Error in program trading analysis: {e}")

def main():
    """Main function demonstrating all ranking features"""
    
    print("🚀 PyHero API - Comprehensive Rankings & Analysis Example\n")
    
    client = setup_client()
    if not client:
        return
    
    try:
        volume_rankings_example(client)
        price_change_rankings_example(client)
        foreign_institutional_rankings_example(client)
        order_book_rankings_example(client)
        credit_trading_rankings_example(client)
        sector_analysis_example(client)
        program_trading_analysis_example(client)
        
        print("\n✓ Rankings & analysis examples completed!")
        
        print("\n📊 Analysis Summary:")
        print("   📈 Market rankings help identify trends and opportunities")
        print("   🌍 Foreign/institutional flows indicate market sentiment")
        print("   📋 Order book analysis reveals supply/demand dynamics")
        print("   🏢 Sector analysis shows industry performance")
        print("   🤖 Program trading data indicates algorithmic activity")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main() 