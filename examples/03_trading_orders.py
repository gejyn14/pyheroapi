"""
PyHero API - Trading & Order Management Example

This example demonstrates:
1. Basic stock trading (buy/sell)
2. Credit trading (margin trading)
3. Order modifications and cancellations
4. Order status tracking
5. Different order types
6. Account management
7. Trading safety practices
"""

import os
import time
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

def account_status_example(client):
    """Check account status and balances before trading"""
    
    print("=== Account Status & Balance Check ===\n")
    
    try:
        # Get deposit details (available balance)
        print("💰 Account Balance:")
        deposit_details = client.get_deposit_details()
        print(f"  Total Evaluation Amount: {deposit_details.tot_evla_amt}")
        print(f"  Securities Evaluation Amount: {deposit_details.scts_evla_amt}")
        print(f"  Total Deposit Amount: {deposit_details.tot_dncl_amt}")
        print(f"  Order Possible Cash: {deposit_details.ord_psbl_cash}")
        
        # Get estimated assets
        print("\n📊 Asset Evaluation:")
        assets = client.get_estimated_assets()
        print(f"  Evaluation Amount: {assets.evla_amt}")
        print(f"  Previous Day Evaluation: {assets.bfdy_evla_amt}")
        print(f"  Profit/Loss Amount: {assets.evla_pfls_amt}")
        print(f"  Profit/Loss Rate: {assets.evla_pfls_rt}%")
        
        # Get current positions
        print("\n📈 Current Positions:")
        positions = client.get_execution_balance()
        
        if positions:
            print("  Symbol | Name | Quantity | Avg Price | Current | P&L")
            print("  " + "-" * 55)
            for pos in positions[:5]:  # Show first 5 positions
                print(f"  {pos.symbol:<6} | {pos.name[:8]:<8} | {pos.quantity:<8} | "
                      f"{pos.average_price:<9} | {pos.current_price:<7} | {pos.profit_loss}")
        else:
            print("  No current positions")
        
        # Get account evaluation status
        print("\n📋 Account Evaluation Status:")
        evaluation = client.get_account_evaluation_status()
        print(f"  Account evaluation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"✗ Error getting account status: {e}")

def basic_trading_example(client):
    """Basic buy and sell operations"""
    
    print("\n=== Basic Trading Operations ===\n")
    
    # Example with a stable, liquid stock
    symbol = "005930"  # Samsung Electronics
    test_quantity = 1  # Small quantity for testing
    
    print("🛒 Basic Stock Trading:")
    print("⚠️  NOTE: This is a SANDBOX example - no real money involved!")
    print(f"   Trading symbol: {symbol} (Samsung Electronics)")
    print(f"   Test quantity: {test_quantity} shares\n")
    
    try:
        # Get current price first
        quote = client.get_quote(symbol)
        current_price = quote.sel_fpr_bid  # Use ask price for buying
        print(f"📊 Current Ask Price: {current_price}")
        
        # Example 1: Market Buy Order
        print("\n1️⃣ Market Buy Order:")
        try:
            buy_response = client.buy_stock(
                symbol=symbol,
                quantity=test_quantity,
                order_type="3",  # Market order
                market="KRX"
            )
            
            order_number = buy_response.get('ord_no')
            print(f"✓ Market buy order placed successfully")
            print(f"  Order Number: {order_number}")
            print(f"  Symbol: {symbol}")
            print(f"  Quantity: {test_quantity}")
            print(f"  Order Type: Market")
            
            # Wait a moment and check order status
            time.sleep(2)
            unfilled_orders = client.get_unfilled_orders(symbol=symbol)
            print(f"  Unfilled orders for {symbol}: {len(unfilled_orders) if unfilled_orders else 0}")
            
        except Exception as e:
            print(f"✗ Market buy order failed: {e}")
        
        # Example 2: Limit Buy Order
        print("\n2️⃣ Limit Buy Order:")
        try:
            # Place limit order below current price
            limit_price = int(float(current_price) * 0.95)  # 5% below market
            
            limit_buy_response = client.buy_stock(
                symbol=symbol,
                quantity=test_quantity,
                price=limit_price,
                order_type="0",  # Limit order
                market="KRX"
            )
            
            limit_order_number = limit_buy_response.get('ord_no')
            print(f"✓ Limit buy order placed successfully")
            print(f"  Order Number: {limit_order_number}")
            print(f"  Limit Price: {limit_price}")
            print(f"  Current Price: {current_price}")
            print(f"  Order Type: Limit")
            
        except Exception as e:
            print(f"✗ Limit buy order failed: {e}")
        
        # Example 3: Market Sell Order (if we have positions)
        print("\n3️⃣ Market Sell Order:")
        try:
            positions = client.get_execution_balance()
            
            # Check if we have the stock to sell
            target_position = None
            if positions:
                for pos in positions:
                    if pos.symbol == symbol and int(pos.available_quantity or 0) > 0:
                        target_position = pos
                        break
            
            if target_position:
                sell_quantity = min(1, int(target_position.available_quantity))
                
                sell_response = client.sell_stock(
                    symbol=symbol,
                    quantity=sell_quantity,
                    order_type="3",  # Market order
                    market="KRX"
                )
                
                sell_order_number = sell_response.get('ord_no')
                print(f"✓ Market sell order placed successfully")
                print(f"  Order Number: {sell_order_number}")
                print(f"  Quantity: {sell_quantity}")
                print(f"  Order Type: Market")
                
            else:
                print("⚠ No available shares to sell for demonstration")
                
        except Exception as e:
            print(f"✗ Market sell order failed: {e}")
        
    except Exception as e:
        print(f"✗ Error in basic trading example: {e}")

def credit_trading_example(client):
    """Credit (margin) trading example"""
    
    print("\n=== Credit Trading (Margin Trading) ===\n")
    
    symbol = "005930"  # Samsung Electronics
    test_quantity = 1
    
    print("💳 Credit Trading Operations:")
    print("⚠️  NOTE: Credit trading involves borrowing - use with extreme caution!")
    print(f"   Symbol: {symbol}")
    print(f"   Quantity: {test_quantity}\n")
    
    try:
        # Example 1: Credit Buy (Margin Buy)
        print("1️⃣ Credit Buy Order:")
        try:
            credit_buy_response = client.credit_buy_stock(
                symbol=symbol,
                quantity=test_quantity,
                order_type="3",  # Market order
                market="KRX"
            )
            
            credit_order_number = credit_buy_response.get('ord_no')
            print(f"✓ Credit buy order placed successfully")
            print(f"  Order Number: {credit_order_number}")
            print(f"  Type: Credit (Margin) Buy")
            
        except Exception as e:
            print(f"✗ Credit buy order failed: {e}")
        
        # Example 2: Credit Sell (Short Sell)
        print("\n2️⃣ Credit Sell Order:")
        try:
            credit_sell_response = client.credit_sell_stock(
                symbol=symbol,
                quantity=test_quantity,
                order_type="3",  # Market order
                market="KRX",
                credit_deal_type="99"  # Margin combined
            )
            
            credit_sell_order_number = credit_sell_response.get('ord_no')
            print(f"✓ Credit sell order placed successfully")
            print(f"  Order Number: {credit_sell_order_number}")
            print(f"  Type: Credit (Short) Sell")
            
        except Exception as e:
            print(f"✗ Credit sell order failed: {e}")
        
        # Check margin requirements
        print("\n3️⃣ Margin Requirements:")
        try:
            margin_info = client.get_margin_rate_order_quantity(
                symbol=symbol,
                margin_rate="40"  # 40% margin rate
            )
            print(f"  Available quantity at 40% margin: {margin_info.get('ord_psbl_qty', 'N/A')}")
            
        except Exception as e:
            print(f"✗ Error getting margin info: {e}")
        
        # Check credit guarantee requirements
        print("\n4️⃣ Credit Guarantee:")
        try:
            guarantee_info = client.get_credit_guarantee_rate_order_quantity(
                symbol=symbol,
                guarantee_rate="40"  # 40% guarantee rate
            )
            print(f"  Available quantity at 40% guarantee: {guarantee_info.get('ord_psbl_qty', 'N/A')}")
            
        except Exception as e:
            print(f"✗ Error getting guarantee info: {e}")
        
    except Exception as e:
        print(f"✗ Error in credit trading example: {e}")

def order_management_example(client):
    """Order modification and cancellation example"""
    
    print("\n=== Order Management (Modify & Cancel) ===\n")
    
    symbol = "005930"
    test_quantity = 1
    
    try:
        # First, place a limit order that won't execute immediately
        print("1️⃣ Placing Limit Order for Modification:")
        
        # Get current price and place order well below market
        quote = client.get_quote(symbol)
        current_price = float(quote.sel_fpr_bid)
        limit_price = int(current_price * 0.8)  # 20% below market - unlikely to execute
        
        original_order = client.buy_stock(
            symbol=symbol,
            quantity=test_quantity,
            price=limit_price,
            order_type="0",  # Limit order
            market="KRX"
        )
        
        original_order_number = original_order.get('ord_no')
        print(f"✓ Original limit order placed")
        print(f"  Order Number: {original_order_number}")
        print(f"  Original Price: {limit_price}")
        print(f"  Quantity: {test_quantity}")
        
        # Wait a moment
        time.sleep(1)
        
        # Example 1: Modify Order (change price and quantity)
        print("\n2️⃣ Modifying Order:")
        try:
            new_price = int(current_price * 0.85)  # Slightly higher price
            new_quantity = 2  # Increase quantity
            
            modify_response = client.modify_order(
                original_order_number=original_order_number,
                symbol=symbol,
                new_quantity=new_quantity,
                new_price=new_price,
                market="KRX"
            )
            
            modified_order_number = modify_response.get('ord_no')
            print(f"✓ Order modified successfully")
            print(f"  New Order Number: {modified_order_number}")
            print(f"  New Price: {new_price} (was {limit_price})")
            print(f"  New Quantity: {new_quantity} (was {test_quantity})")
            
            # Update order number for cancellation
            order_to_cancel = modified_order_number or original_order_number
            
        except Exception as e:
            print(f"✗ Order modification failed: {e}")
            order_to_cancel = original_order_number
        
        # Wait a moment
        time.sleep(1)
        
        # Example 2: Cancel Order
        print("\n3️⃣ Cancelling Order:")
        try:
            cancel_response = client.cancel_order(
                original_order_number=order_to_cancel,
                symbol=symbol,
                cancel_quantity=new_quantity if 'new_quantity' in locals() else test_quantity,
                market="KRX"
            )
            
            cancelled_order_number = cancel_response.get('ord_no')
            print(f"✓ Order cancelled successfully")
            print(f"  Cancelled Order Number: {cancelled_order_number}")
            
        except Exception as e:
            print(f"✗ Order cancellation failed: {e}")
        
        # Example 3: Check unfilled orders
        print("\n4️⃣ Checking Unfilled Orders:")
        try:
            unfilled_orders = client.get_unfilled_orders(symbol=symbol)
            
            if unfilled_orders:
                print(f"  Found {len(unfilled_orders)} unfilled orders for {symbol}:")
                for order in unfilled_orders[:3]:  # Show first 3
                    print(f"    Order #{order.ord_no}: {order.ord_qty} shares at {order.ord_uv}")
            else:
                print(f"  No unfilled orders for {symbol}")
                
        except Exception as e:
            print(f"✗ Error checking unfilled orders: {e}")
        
        # Example 4: Check filled orders
        print("\n5️⃣ Checking Filled Orders:")
        try:
            filled_orders = client.get_filled_orders(symbol=symbol)
            
            if filled_orders:
                print(f"  Found {len(filled_orders)} filled orders for {symbol}:")
                for order in filled_orders[:3]:  # Show first 3
                    print(f"    Order #{order.ord_no}: {order.cntr_qty} shares at {order.cntr_uv}")
            else:
                print(f"  No filled orders for {symbol}")
                
        except Exception as e:
            print(f"✗ Error checking filled orders: {e}")
        
    except Exception as e:
        print(f"✗ Error in order management example: {e}")

def main():
    """Main function demonstrating all trading features"""
    
    print("🚀 PyHero API - Comprehensive Trading Example")
    print("⚠️  IMPORTANT: This example uses SANDBOX environment!")
    print("⚠️  Always test thoroughly before using in production!\n")
    
    # Setup client
    client = setup_client()
    if not client:
        return
    
    try:
        # Run all trading examples
        account_status_example(client)
        basic_trading_example(client)
        credit_trading_example(client)
        order_management_example(client)
        
        print("\n" + "="*60)
        print("✓ Trading examples completed successfully!")
        print("\n🔴 REMEMBER:")
        print("   - This was SANDBOX trading (no real money)")
        print("   - Always use proper risk management")
        print("   - Test extensively before live trading")
        print("   - Never trade money you can't afford to lose")
        
    except KiwoomAPIError as e:
        print(f"✗ Kiwoom API Error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    main() 