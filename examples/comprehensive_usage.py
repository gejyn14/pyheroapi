#!/usr/bin/env python3
"""
Comprehensive example showcasing all PyHero API functionality.

This example demonstrates all the implemented features including:
- Trading operations (buy, sell, modify, cancel)
- Enhanced market data
- Complete account management
- ETF and ELW operations
- Profit/loss tracking

Run this example to see the full capabilities of the API.
"""

import pyheroapi
from datetime import datetime, timedelta
import time


def main():
    """
    Comprehensive demonstration of PyHero API functionality.
    """
    print("🚀 PyHero API - Comprehensive Example")
    print("=" * 50)
    
    # Replace with your actual credentials
    APP_KEY = "your_app_key_here"
    SECRET_KEY = "your_secret_key_here"
    ACCOUNT_NUMBER = "your_account_number"
    
    # Connect to API with context manager for automatic cleanup
    with pyheroapi.connect(APP_KEY, SECRET_KEY, sandbox=True) as api:
        
        # ===========================================
        # 🏛️ ACCOUNT OPERATIONS
        # ===========================================
        print("\n🏛️ ACCOUNT OPERATIONS")
        print("-" * 30)
        
        account = api.account(ACCOUNT_NUMBER)
        
        # Get account balance
        balance = account.balance
        print(f"💰 Account Balance:")
        print(f"  Total: ₩{balance['total_balance']:,.0f}")
        print(f"  Available: ₩{balance['available_balance']:,.0f}")
        print(f"  Securities: ₩{balance['securities_balance']:,.0f}")
        
        # Get current positions
        positions = account.positions
        print(f"\n📊 Current Positions ({len(positions)}):")
        for pos in positions[:5]:  # Show first 5
            print(f"  {pos['symbol']}: {pos['quantity']:,} shares @ ₩{pos['current_price']:,.0f}")
            print(f"    P&L: ₩{pos['unrealized_pnl']:,.0f} ({pos['unrealized_pnl_rate']:.2f}%)")
        
        # Get unfilled orders
        unfilled = account.unfilled_orders
        print(f"\n⏳ Unfilled Orders ({len(unfilled)}):")
        for order in unfilled[:3]:  # Show first 3
            print(f"  #{order['order_number']}: {order['symbol']} {order['order_quantity']:,} @ ₩{order['order_price']:,.0f}")
        
        # Get filled orders
        filled = account.filled_orders
        print(f"\n✅ Today's Filled Orders ({len(filled)}):")
        for order in filled[:3]:  # Show first 3
            print(f"  #{order['order_number']}: {order['symbol']} {order['filled_quantity']:,} @ ₩{order['filled_price']:,.0f}")
        
        # Get account return rate
        return_rate = account.get_return_rate(period="1")  # 1 month
        print(f"\n📈 Account Performance (1 month):")
        print(f"  Return Rate: {return_rate.get('return_rate', 0):.2f}%")
        print(f"  P&L: ₩{return_rate.get('profit_loss', 0):,.0f}")
        
        # ===========================================
        # 📊 STOCK OPERATIONS
        # ===========================================
        print("\n\n📊 STOCK OPERATIONS")
        print("-" * 30)
        
        # Samsung Electronics analysis
        samsung = api.stock("005930")
        
        # Current price and quote
        price = samsung.current_price
        quote = samsung.quote
        print(f"📈 Samsung Electronics (005930):")
        print(f"  Current Price: ₩{price:,.0f}")
        print(f"  Best Bid: ₩{quote['best_bid']:,.0f} (Qty: {quote['total_bid_quantity']:,})")
        print(f"  Best Ask: ₩{quote['best_ask']:,.0f} (Qty: {quote['total_ask_quantity']:,})")
        
        # Historical data
        history = samsung.history(days=10)
        print(f"\n📉 Recent History (10 days):")
        for day in history[:5]:  # Show first 5 days
            print(f"  {day['date']}: ₩{day['close']:,.0f} (Vol: {day['volume']:,})")
        
        # ===========================================
        # 💹 ETF OPERATIONS
        # ===========================================
        print("\n\n💹 ETF OPERATIONS")
        print("-" * 30)
        
        # KODEX 200 analysis
        kodex = api.etf("069500")
        etf_info = kodex.info
        
        print(f"🏢 KODEX 200 (069500):")
        print(f"  Name: {etf_info['name']}")
        print(f"  NAV: ₩{etf_info['nav']:,.2f}")
        print(f"  Tracking Error: {etf_info['tracking_error']:.4f}")
        print(f"  Discount/Premium: {etf_info['discount_premium']:.2f}%")
        
        # ETF returns
        etf_returns = kodex.returns(period="3")  # 3 months
        print(f"  3-Month Returns: {etf_returns}")
        
        # ===========================================
        # ⚡ ELW OPERATIONS
        # ===========================================
        print("\n\n⚡ ELW OPERATIONS")
        print("-" * 30)
        
        # Example ELW analysis (replace with actual ELW symbol)
        try:
            elw = api.elw("57JBHH")  # Replace with actual ELW symbol
            elw_info = elw.info
            
            print(f"🎯 ELW Analysis:")
            print(f"  Name: {elw_info['name']}")
            print(f"  Underlying: {elw_info['underlying_asset']}")
            print(f"  Strike Price: ₩{elw_info['strike_price']:,.0f}")
            print(f"  Expiry: {elw_info['expiry_date']}")
            print(f"  Conversion Ratio: {elw_info['conversion_ratio']}")
            
            # Greeks analysis
            greeks = elw.greeks
            print(f"  Greeks:")
            print(f"    Delta: {greeks.get('delta', 0):.4f}")
            print(f"    Gamma: {greeks.get('gamma', 0):.4f}")
            print(f"    Theta: {greeks.get('theta', 0):.4f}")
            print(f"    Vega: {greeks.get('vega', 0):.4f}")
            
        except Exception as e:
            print(f"⚠️ ELW example skipped (symbol may not exist): {e}")
        
        # ===========================================
        # 📈 TRADING OPERATIONS
        # ===========================================
        print("\n\n📈 TRADING OPERATIONS")
        print("-" * 30)
        
        print("🛡️ DEMO MODE: Trading operations shown but not executed")
        
        # Example buy order (not executed in demo)
        demo_buy_order = {
            'symbol': '005930',
            'quantity': 10,
            'price': 75000,
            'order_type': 'limit'
        }
        
        print(f"📋 Example Buy Order:")
        print(f"  Symbol: {demo_buy_order['symbol']}")
        print(f"  Quantity: {demo_buy_order['quantity']:,} shares")
        print(f"  Price: ₩{demo_buy_order['price']:,.0f}")
        print(f"  Type: {demo_buy_order['order_type']}")
        
        # To actually place orders, uncomment and modify:
        # result = api.trading.buy("005930", 10, 75000, "limit")
        # print(f"Order Result: {result}")
        
        # Example sell order
        demo_sell_order = {
            'symbol': '005930',
            'quantity': 5,
            'price': 77000,
            'order_type': 'limit'
        }
        
        print(f"\n📋 Example Sell Order:")
        print(f"  Symbol: {demo_sell_order['symbol']}")
        print(f"  Quantity: {demo_sell_order['quantity']:,} shares")
        print(f"  Price: ₩{demo_sell_order['price']:,.0f}")
        print(f"  Type: {demo_sell_order['order_type']}")
        
        # To actually place orders, uncomment and modify:
        # result = api.trading.sell("005930", 5, 77000, "limit")
        # print(f"Sell Result: {result}")
        
        # ===========================================
        # 🔍 MARKET RESEARCH
        # ===========================================
        print("\n\n🔍 MARKET RESEARCH")
        print("-" * 30)
        
        # Stock search
        search_results = api.search_stocks("삼성", limit=5)
        print(f"🔎 Search Results for '삼성':")
        for result in search_results:
            print(f"  {result['symbol']}: {result['name']} ({result['market']})")
        
        # Market status
        market_status = api.market_status
        print(f"\n🏢 Market Status:")
        print(f"  Open: {market_status.get('is_open', 'Unknown')}")
        print(f"  Time: {market_status.get('market_time', 'Unknown')}")
        
        # ===========================================
        # 📊 PROFIT/LOSS ANALYSIS
        # ===========================================
        print("\n\n📊 PROFIT/LOSS ANALYSIS")
        print("-" * 30)
        
        # Get P&L for specific stock over period
        today = datetime.now().strftime("%Y%m%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        
        try:
            pnl_data = account.get_profit_loss("005930", week_ago, today)
            print(f"💰 Samsung P&L (Last 7 days):")
            
            total_pnl = 0
            total_commission = 0
            total_tax = 0
            
            for pnl in pnl_data:
                realized_pnl = pnl['realized_pnl']
                commission = pnl['commission']
                tax = pnl['tax']
                
                total_pnl += realized_pnl
                total_commission += commission
                total_tax += tax
                
                print(f"  Trade: {pnl['quantity']:,} shares @ ₩{pnl['sell_price']:,.0f}")
                print(f"    P&L: ₩{realized_pnl:,.0f} ({pnl['pnl_rate']:.2f}%)")
            
            print(f"\n📈 Summary:")
            print(f"  Total P&L: ₩{total_pnl:,.0f}")
            print(f"  Total Commission: ₩{total_commission:,.0f}")
            print(f"  Total Tax: ₩{total_tax:,.0f}")
            print(f"  Net P&L: ₩{total_pnl - total_commission - total_tax:,.0f}")
            
        except Exception as e:
            print(f"⚠️ P&L analysis skipped: {e}")
        
        # ===========================================
        # 🎯 ADVANCED MARKET DATA
        # ===========================================
        print("\n\n🎯 ADVANCED MARKET DATA")
        print("-" * 30)
        
        try:
            # Enhanced market data examples
            print("📊 Advanced market data features available:")
            print("  • Intraday minute-by-minute prices")
            print("  • Market performance indicators")
            print("  • Institutional trading data")
            print("  • Program trading trends")
            print("  • Trading intensity analysis")
            print("  • Securities firm trading trends")
            print("  • After-hours trading data")
            
            # These would be actual API calls:
            # intraday = api._client.get_intraday_prices("005930")
            # institutional = api._client.get_daily_institutional_trading("005930")
            # program_trading = api._client.get_program_trading_hourly()
            
        except Exception as e:
            print(f"⚠️ Advanced market data example: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Comprehensive example completed!")
        print("🎉 All major API features demonstrated")
        print("\n💡 Next Steps:")
        print("  1. Replace demo credentials with your real API keys")
        print("  2. Uncomment trading operations for live trading")
        print("  3. Implement your trading strategy using these building blocks")
        print("  4. Add error handling and logging for production use")


def trading_example():
    """
    Focused example showing trading operations.
    """
    print("\n🚀 TRADING OPERATIONS EXAMPLE")
    print("=" * 40)
    
    APP_KEY = "your_app_key_here"
    SECRET_KEY = "your_secret_key_here"
    
    with pyheroapi.connect(APP_KEY, SECRET_KEY, sandbox=True) as api:
        
        # Buy order example
        print("💰 Buy Order Example:")
        buy_result = api.trading.buy(
            symbol="005930",      # Samsung Electronics
            quantity=10,          # 10 shares
            price=75000,          # ₩75,000 per share
            order_type="limit",   # Limit order
            market="KRX"          # Korean Exchange
        )
        
        if buy_result['success']:
            print(f"✅ Buy order placed successfully!")
            print(f"   Order Number: {buy_result['order_number']}")
            print(f"   Message: {buy_result['message']}")
            
            # Wait a moment then check order status
            time.sleep(2)
            
            # Get unfilled orders to check status
            account = api.account("your_account_number")
            unfilled = account.unfilled_orders
            
            print(f"\n📋 Current unfilled orders: {len(unfilled)}")
            for order in unfilled:
                if order['order_number'] == buy_result['order_number']:
                    print(f"   Found our order: {order['remaining_quantity']} shares remaining")
                    
                    # Example: Modify the order
                    modify_result = api.trading.modify_order(
                        order_number=order['order_number'],
                        symbol=order['symbol'],
                        new_quantity=5,    # Reduce to 5 shares
                        new_price=74000    # Lower price to ₩74,000
                    )
                    
                    if modify_result['success']:
                        print(f"✅ Order modified successfully!")
                        print(f"   New Order Number: {modify_result['new_order_number']}")
                    
                    # Example: Cancel the order
                    cancel_result = api.trading.cancel_order(
                        order_number=modify_result['new_order_number'],
                        symbol=order['symbol'],
                        quantity=5
                    )
                    
                    if cancel_result['success']:
                        print(f"✅ Order cancelled successfully!")
                        print(f"   Cancelled Order Number: {cancel_result['cancelled_order_number']}")
                    
                    break
        else:
            print(f"❌ Buy order failed: {buy_result['error']}")


if __name__ == "__main__":
    # Run comprehensive example
    main()
    
    # Uncomment to run trading-focused example
    # trading_example() 