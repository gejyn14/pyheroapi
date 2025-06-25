"""
PyHero API - Charts & Technical Analysis Example

This example demonstrates:
1. Stock charts (tick, minute, daily, weekly, monthly, yearly)
2. Sector charts and analysis
3. Technical indicators and analysis
4. Chart pattern recognition
5. Volume analysis
6. Price action analysis
"""

import os
from pyheroapi import KiwoomClient

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

def stock_charts_example(client):
    """Stock charts analysis example"""
    
    print("=== Stock Charts Analysis ===\n")
    
    symbol = "005930"  # Samsung Electronics
    
    try:
        # Daily chart
        print("📅 Daily Chart Analysis:")
        daily_chart = client.get_stock_daily_chart(
            symbol=symbol,
            base_date="",
            adjusted_price_type="1"
        )
        
        if daily_chart:
            daily_data = daily_chart.get('daily_data', [])
            print(f"  Daily data points: {len(daily_data)}")
            
            if daily_data:
                print("  📈 Recent 3 Days:")
                for i, day in enumerate(daily_data[:3]):
                    print(f"    Day {i+1}: {day.get('date', 'N/A')} "
                          f"Close: {day.get('close', 'N/A')}")
        
        # Weekly chart
        print("\n📊 Weekly Chart:")
        weekly_chart = client.get_stock_weekly_chart(symbol=symbol)
        if weekly_chart:
            weekly_data = weekly_chart.get('weekly_data', [])
            print(f"  Weekly data points: {len(weekly_data)}")
        
        # Monthly chart
        print("\n📆 Monthly Chart:")
        monthly_chart = client.get_stock_monthly_chart(symbol=symbol)
        if monthly_chart:
            monthly_data = monthly_chart.get('monthly_data', [])
            print(f"  Monthly data points: {len(monthly_data)}")
        
        # Minute chart
        print("\n⏰ Minute Chart (5-min):")
        minute_chart = client.get_stock_minute_chart(
            symbol=symbol,
            minute_type="5"
        )
        if minute_chart:
            minute_data = minute_chart.get('minute_data', [])
            print(f"  5-minute data points: {len(minute_data)}")
        
    except Exception as e:
        print(f"✗ Error in stock charts: {e}")

def sector_charts_example(client):
    """Sector charts example"""
    
    print("\n=== Sector Charts ===\n")
    
    sector_code = "001"  # Electronics sector
    
    try:
        # Sector daily chart
        print("🏢 Sector Daily Chart:")
        sector_daily = client.get_sector_daily_chart(
            sector_code=sector_code,
            base_date=""
        )
        
        if sector_daily:
            daily_data = sector_daily.get('daily_data', [])
            print(f"  Sector daily data: {len(daily_data)} points")
            
            if daily_data:
                latest = daily_data[0]
                print(f"  Latest sector price: {latest.get('close', 'N/A')}")
        
        # Sector weekly chart
        print("\n📊 Sector Weekly Chart:")
        sector_weekly = client.get_sector_weekly_chart(
            sector_code=sector_code
        )
        if sector_weekly:
            weekly_data = sector_weekly.get('weekly_data', [])
            print(f"  Sector weekly data: {len(weekly_data)} points")
        
    except Exception as e:
        print(f"✗ Error in sector charts: {e}")

def technical_analysis_example(client):
    """Basic technical analysis"""
    
    print("\n=== Technical Analysis ===\n")
    
    symbol = "005930"
    
    try:
        # Get daily data
        daily_chart = client.get_stock_daily_chart(symbol=symbol)
        
        if daily_chart and daily_chart.get('daily_data'):
            daily_data = daily_chart['daily_data']
            print(f"📊 Technical Analysis for {symbol}:")
            print(f"  Data points: {len(daily_data)} days")
            
            # Simple moving average calculation
            if len(daily_data) >= 5:
                prices = []
                for day in daily_data[:5]:
                    try:
                        price = float(day.get('close', 0) or 0)
                        if price > 0:
                            prices.append(price)
                    except:
                        continue
                
                if prices:
                    sma5 = sum(prices) / len(prices)
                    current_price = prices[0]
                    print(f"  Current Price: {current_price:,.0f}")
                    print(f"  5-Day SMA: {sma5:,.0f}")
                    
                    trend = "🟢 Above SMA" if current_price > sma5 else "🔴 Below SMA"
                    print(f"  Trend: {trend}")
            
            # Volume analysis
            if len(daily_data) >= 10:
                volumes = []
                for day in daily_data[:10]:
                    try:
                        volume = int(day.get('volume', 0) or 0)
                        if volume > 0:
                            volumes.append(volume)
                    except:
                        continue
                
                if volumes:
                    avg_volume = sum(volumes) / len(volumes)
                    latest_volume = volumes[0]
                    print(f"\n📊 Volume Analysis:")
                    print(f"  Average Volume (10d): {avg_volume:,.0f}")
                    print(f"  Latest Volume: {latest_volume:,.0f}")
                    
                    ratio = latest_volume / avg_volume if avg_volume > 0 else 0
                    vol_status = "🟢 High" if ratio > 1.5 else "🟡 Normal"
                    print(f"  Volume Status: {vol_status}")
        
    except Exception as e:
        print(f"✗ Error in technical analysis: {e}")

def main():
    """Main function"""
    
    print("🚀 PyHero API - Charts & Technical Analysis\n")
    
    client = setup_client()
    if not client:
        return
    
    try:
        stock_charts_example(client)
        sector_charts_example(client)
        technical_analysis_example(client)
        
        print("\n✓ Charts & technical analysis completed!")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main() 