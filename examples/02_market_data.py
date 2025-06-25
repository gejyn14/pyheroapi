"""
PyHero API - Market Data Example

This example demonstrates:
1. Stock quotes and order book data
2. OHLCV historical data
3. Market performance indicators
4. Intraday and minute data
5. After-hours trading data
6. Program trading data
"""

import os
from datetime import datetime, timedelta
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

def stock_quotes_example(client):
    """Comprehensive stock quotes and order book example"""
    
    print("=== Stock Quotes & Order Book Data ===\n")
    
    # Major Korean stocks for examples
    symbols = ["005930", "000660", "035420", "005380", "051910"]  # Samsung, SK Hynix, NAVER, LG Chem, LG Electronics
    symbol_names = ["Samsung Electronics", "SK Hynix", "NAVER", "LG Chem", "LG Electronics"]
    
    for symbol, name in zip(symbols, symbol_names):
        try:
            print(f"📊 {name} ({symbol}):")
            
            # Get current quote/order book
            quote = client.get_quote(symbol)
            print(f"  Best Bid: {quote.buy_fpr_bid} (Qty: {quote.buy_fpr_req})")
            print(f"  Best Ask: {quote.sel_fpr_bid} (Qty: {quote.sel_fpr_req})")
            print(f"  Total Buy Orders: {quote.tot_buy_req}")
            print(f"  Total Sell Orders: {quote.tot_sel_req}")
            
            # Get basic market data
            market_data = client.get_market_data(symbol)
            print(f"  Current Price: {market_data.current_price}")
            print(f"  Change: {market_data.change_amount} ({market_data.change_rate}%)")
            print(f"  Volume: {market_data.volume}")
            print(f"  Value: {market_data.value}")
            
        except Exception as e:
            print(f"  ✗ Error getting data for {symbol}: {e}")
        
        print()

def historical_data_example(client):
    """OHLCV historical data example"""
    
    print("=== Historical OHLCV Data ===\n")
    
    symbol = "005930"  # Samsung Electronics
    
    try:
        # Daily OHLCV data
        print("📈 Daily OHLCV (Last 30 days):")
        daily_data = client.get_stock_ohlcv(
            symbol=symbol,
            time_type="D",  # Daily
            count=30
        )
        
        if daily_data:
            print("  Date       | Open    | High    | Low     | Close   | Volume")
            print("  " + "-" * 65)
            for day in daily_data[:5]:  # Show first 5 days
                print(f"  {day.get('date', 'N/A'):<10} | {day.get('open_pric', 'N/A'):<7} | "
                      f"{day.get('high_pric', 'N/A'):<7} | {day.get('low_pric', 'N/A'):<7} | "
                      f"{day.get('close_pric', 'N/A'):<7} | {day.get('trde_qty', 'N/A')}")
            print(f"  ... and {len(daily_data) - 5} more days")
        
        # Weekly OHLCV data
        print("\n📈 Weekly OHLCV (Last 12 weeks):")
        weekly_data = client.get_stock_ohlcv(
            symbol=symbol,
            time_type="W",  # Weekly
            count=12
        )
        print(f"  Retrieved {len(weekly_data) if weekly_data else 0} weeks of data")
        
        # Monthly OHLCV data
        print("\n📈 Monthly OHLCV (Last 6 months):")
        monthly_data = client.get_stock_ohlcv(
            symbol=symbol,
            time_type="M",  # Monthly
            count=6
        )
        print(f"  Retrieved {len(monthly_data) if monthly_data else 0} months of data")
        
    except Exception as e:
        print(f"✗ Error getting historical data: {e}")

def intraday_data_example(client):
    """Intraday and minute data example"""
    
    print("\n=== Intraday & Minute Data ===\n")
    
    symbol = "005930"  # Samsung Electronics
    
    try:
        # Minute data
        print("⏰ Minute Data (1-minute intervals):")
        minute_data = client.get_stock_minute_data(
            symbol=symbol,
            minute_type="1"  # 1-minute
        )
        
        if minute_data:
            print("  Time   | Price   | Volume | Change")
            print("  " + "-" * 35)
            for minute in minute_data[:5]:  # Show first 5 minutes
                print(f"  {minute.get('time', 'N/A'):<6} | {minute.get('close_pric', 'N/A'):<7} | "
                      f"{minute.get('trde_qty', 'N/A'):<6} | {minute.get('flu_rt', 'N/A')}")
        
        # Different minute intervals
        for interval in ["5", "15", "30", "60"]:
            try:
                interval_data = client.get_stock_minute_data(symbol=symbol, minute_type=interval)
                print(f"  {interval}-minute data: {len(interval_data) if interval_data else 0} records")
            except Exception as e:
                print(f"  {interval}-minute data: Error - {e}")
        
    except Exception as e:
        print(f"✗ Error getting intraday data: {e}")

def market_performance_example(client):
    """Market performance indicators example"""
    
    print("\n=== Market Performance Indicators ===\n")
    
    symbol = "005930"  # Samsung Electronics
    
    try:
        # Market performance info
        print("📊 Market Performance Info:")
        performance = client.get_market_performance_info(symbol)
        print(f"  Current Price: {performance.get('cur_prc', 'N/A')}")
        print(f"  Opening Price: {performance.get('open_pric', 'N/A')}")
        print(f"  High Price: {performance.get('high_pric', 'N/A')}")
        print(f"  Low Price: {performance.get('low_pric', 'N/A')}")
        print(f"  Trading Volume: {performance.get('trde_qty', 'N/A')}")
        print(f"  Trading Value: {performance.get('trde_prica', 'N/A')}")
        
        # Daily stock prices
        print("\n📅 Daily Stock Prices (Last 7 days):")
        daily_prices = client.get_daily_stock_prices(symbol=symbol, days=7)
        
        if daily_prices:
            for day in daily_prices[:3]:  # Show first 3 days
                print(f"  Date: {day.get('date', 'N/A')}, "
                      f"Close: {day.get('close_pric', 'N/A')}, "
                      f"Change: {day.get('flu_rt', 'N/A')}%")
        
        # After-hours single price
        print("\n🌙 After-Hours Single Price:")
        after_hours = client.get_after_hours_single_price(symbol)
        print(f"  After-hours price: {after_hours.get('pred_close_pric', 'N/A')}")
        print(f"  Expected volume: {after_hours.get('pred_trde_qty', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Error getting market performance: {e}")

def program_trading_example(client):
    """Program trading data example"""
    
    print("\n=== Program Trading Data ===\n")
    
    try:
        # Program trading hourly
        print("🤖 Program Trading (Hourly):")
        hourly_program = client.get_program_trading_hourly()
        
        if hourly_program:
            print(f"  Retrieved {len(hourly_program)} hourly records")
            if hourly_program:
                latest = hourly_program[0]
                print(f"  Latest hour trading value: {latest.get('trde_prica', 'N/A')}")
        
        # Program trading daily
        print("\n🤖 Program Trading (Daily):")
        daily_program = client.get_program_trading_daily()
        
        if daily_program:
            print(f"  Retrieved {len(daily_program)} daily records")
        
        # Program trading arbitrage
        print("\n🤖 Program Trading (Arbitrage):")
        arbitrage = client.get_program_trading_arbitrage()
        
        if arbitrage:
            print(f"  Retrieved {len(arbitrage)} arbitrage records")
        
        # Symbol-specific program trading
        symbol = "005930"
        print(f"\n🤖 Program Trading for {symbol}:")
        symbol_program = client.get_symbol_program_trading_hourly(symbol)
        
        if symbol_program:
            print(f"  Retrieved {len(symbol_program)} symbol-specific records")
        
    except Exception as e:
        print(f"✗ Error getting program trading data: {e}")

def institutional_trading_example(client):
    """Institutional trading data example"""
    
    print("\n=== Institutional Trading Data ===\n")
    
    symbol = "005930"  # Samsung Electronics
    
    try:
        # Daily institutional trading
        print("🏛️ Daily Institutional Trading:")
        institutional = client.get_daily_institutional_trading_stocks(symbol)
        
        if institutional:
            print(f"  Retrieved {len(institutional)} institutional trading records")
            if institutional:
                latest = institutional[0]
                print(f"  Latest institutional net buying: {latest.get('net_buy_qty', 'N/A')}")
        
        # Institutional trading trends
        print("\n📈 Institutional Trading Trends:")
        trends = client.get_institutional_trading_trends(symbol)
        
        if trends:
            print(f"  Retrieved {len(trends)} trend records")
        
        # Trading intensity (hourly)
        print("\n⚡ Trading Intensity (Hourly):")
        intensity_hourly = client.get_trading_intensity_hourly(symbol)
        
        if intensity_hourly:
            print(f"  Retrieved {len(intensity_hourly)} hourly intensity records")
        
        # Trading intensity (daily)
        print("\n⚡ Trading Intensity (Daily):")
        intensity_daily = client.get_trading_intensity_daily(symbol)
        
        if intensity_daily:
            print(f"  Retrieved {len(intensity_daily)} daily intensity records")
        
        # Intraday investor trading
        print("\n👥 Intraday Investor Trading:")
        intraday_investor = client.get_intraday_investor_trading(symbol)
        
        if intraday_investor:
            print(f"  Retrieved {len(intraday_investor)} intraday investor records")
        
        # After-hours investor trading
        print("\n🌙 After-Hours Investor Trading:")
        afterhours_investor = client.get_after_hours_investor_trading(symbol)
        
        if afterhours_investor:
            print(f"  Retrieved {len(afterhours_investor)} after-hours investor records")
        
    except Exception as e:
        print(f"✗ Error getting institutional trading data: {e}")

def main():
    """Main function demonstrating all market data features"""
    
    print("🚀 PyHero API - Comprehensive Market Data Example\n")
    
    # Setup client
    client = setup_client()
    if not client:
        return
    
    try:
        # Run all examples
        stock_quotes_example(client)
        historical_data_example(client)
        intraday_data_example(client)
        market_performance_example(client)
        program_trading_example(client)
        institutional_trading_example(client)
        
        print("\n✓ Market data examples completed successfully!")
        
    except KiwoomAPIError as e:
        print(f"✗ Kiwoom API Error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    main() 