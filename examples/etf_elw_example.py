#!/usr/bin/env python3
"""
ETF and ELW example for Kiwoom API Python client.

This example demonstrates advanced features for:
1. ETF analysis and tracking
2. ELW Greeks and sensitivity analysis
3. Comparative analysis
"""

import os
from typing import List, Dict, Any
from pyheroapi import KiwoomClient, KiwoomAPIError


def analyze_etf(client: KiwoomClient, symbol: str, name: str):
    """Analyze an ETF with comprehensive data."""
    print(f"\n📊 Analyzing ETF: {name} ({symbol})")
    print("-" * 50)
    
    try:
        # Get basic ETF info
        etf_info = client.get_etf_info(symbol)
        print(f"Name: {etf_info.name}")
        print(f"NAV: {etf_info.nav}")
        print(f"Tracking Error: {etf_info.tracking_error}")
        print(f"Discount/Premium: {etf_info.discount_premium}")
        
        # Get returns for different periods
        periods = {
            "0": "1 Week",
            "1": "1 Month", 
            "2": "6 Months",
            "3": "1 Year"
        }
        
        print(f"\n📈 Returns Analysis:")
        for period_code, period_name in periods.items():
            try:
                returns = client.get_etf_returns(symbol, "207", period_code)
                if returns:
                    return_data = returns[0]
                    etf_return = return_data.get("etfprft_rt", "N/A")
                    benchmark_return = return_data.get("cntr_prft_rt", "N/A")
                    print(f"  {period_name}: ETF {etf_return}% | Benchmark {benchmark_return}%")
            except Exception as e:
                print(f"  {period_name}: Error - {e}")
                
    except Exception as e:
        print(f"Error analyzing ETF {symbol}: {e}")


def analyze_elw(client: KiwoomClient, symbol: str):
    """Analyze an ELW with Greeks and sensitivity data."""
    print(f"\n⚡ Analyzing ELW: {symbol}")
    print("-" * 40)
    
    try:
        # Get basic ELW info
        elw_info = client.get_elw_info(symbol)
        print(f"Underlying Asset: {elw_info.underlying_asset}")
        print(f"Strike Price: {elw_info.strike_price}")
        print(f"Expiry Date: {elw_info.expiry_date}")
        print(f"Conversion Ratio: {elw_info.conversion_ratio}")
        
        # Get current Greeks
        print(f"\n🔢 Current Greeks:")
        print(f"  Delta: {elw_info.delta}")
        print(f"  Gamma: {elw_info.gamma}")
        print(f"  Theta: {elw_info.theta}")
        print(f"  Vega: {elw_info.vega}")
        
        # Get sensitivity data (time series)
        print(f"\n📉 Recent Sensitivity Data:")
        try:
            sensitivity_data = client.get_elw_sensitivity(symbol)
            for i, data in enumerate(sensitivity_data[:5]):  # Show latest 5 entries
                time = data.get("cntr_tm", "N/A")
                current_price = data.get("cur_prc", "N/A")
                delta = data.get("delta", "N/A")
                gamma = data.get("gam", "N/A")
                print(f"  {time}: Price {current_price} | Δ {delta} | Γ {gamma}")
        except Exception as e:
            print(f"  Error getting sensitivity data: {e}")
            
    except Exception as e:
        print(f"Error analyzing ELW {symbol}: {e}")


def compare_etfs(client: KiwoomClient, etf_symbols: List[str]):
    """Compare multiple ETFs side by side."""
    print(f"\n🔄 ETF Comparison")
    print("=" * 60)
    
    etf_data = []
    
    for symbol in etf_symbols:
        try:
            info = client.get_etf_info(symbol)
            returns = client.get_etf_returns(symbol, "207", "3")  # 1 year
            
            etf_return = "N/A"
            if returns:
                etf_return = returns[0].get("etfprft_rt", "N/A")
            
            etf_data.append({
                "symbol": symbol,
                "name": info.name,
                "nav": info.nav,
                "tracking_error": info.tracking_error,
                "return_1y": etf_return
            })
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
    
    # Display comparison table
    if etf_data:
        print(f"{'Symbol':<10} {'Name':<20} {'NAV':<12} {'Track Err':<10} {'1Y Return':<10}")
        print("-" * 70)
        for etf in etf_data:
            print(f"{etf['symbol']:<10} {etf['name'][:19]:<20} {etf['nav']:<12} "
                  f"{etf['tracking_error']:<10} {etf['return_1y']:<10}")


def main():
    """Main example function for ETF and ELW analysis."""
    
    # Get API token from environment variable
    access_token = os.getenv("KIWOOM_ACCESS_TOKEN")
    
    if not access_token:
        print("Please set KIWOOM_ACCESS_TOKEN environment variable")
        return
    
    # Initialize client
    client = KiwoomClient(
        access_token=access_token,
        is_production=False,
        rate_limit_delay=0.2  # Slightly slower for multiple requests
    )
    
    try:
        print("🚀 Kiwoom API - ETF & ELW Analysis")
        print("=" * 50)
        
        # Analyze popular Korean ETFs
        popular_etfs = [
            ("069500", "KODEX 200"),
            ("069660", "KOSEF 200"), 
            ("102110", "TIGER 200"),
        ]
        
        for symbol, name in popular_etfs:
            analyze_etf(client, symbol, name)
        
        # Compare ETFs
        etf_symbols = [etf[0] for etf in popular_etfs]
        compare_etfs(client, etf_symbols)
        
        # Analyze ELW examples
        elw_symbols = ["57JBHH"]  # Add more ELW symbols as needed
        
        for elw_symbol in elw_symbols:
            analyze_elw(client, elw_symbol)
        
        print("\n✅ Analysis completed!")
        
    except KiwoomAPIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main() 