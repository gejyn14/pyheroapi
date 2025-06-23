# Real-time Market Data Streaming

PyHero API now supports real-time market data streaming through WebSocket connections to Kiwoom Securities' API. This feature allows you to receive live updates for stock prices, order books, account changes, and more.

## Installation

To use real-time functionality, you need to install the `websockets` library:

```bash
# Install with real-time support
pip install pyheroapi[realtime]

# Or install all optional dependencies
pip install pyheroapi[all]

# Or install websockets separately
pip install websockets
```

## Quick Start

Here's a simple example to get started with real-time data:

```python
import asyncio
import pyheroapi
from pyheroapi import RealtimeDataType

async def price_callback(data):
    """Callback for price updates."""
    symbol = data.symbol
    current_price = data.values.get("10", "N/A")  # Field 10 = current price
    print(f"📈 {symbol}: ₩{current_price}")

async def main():
    # Connect to API
    api = pyheroapi.connect("your_app_key", "your_secret_key", sandbox=True)
    
    # Get real-time client
    rt_client = api.realtime
    
    # Add callback for stock trades
    rt_client.add_callback(RealtimeDataType.STOCK_TRADE, price_callback)
    
    # Connect to WebSocket
    await rt_client.connect()
    
    # Subscribe to Samsung Electronics
    await rt_client.subscribe_stock_price("005930")
    
    # Listen for updates
    print("🎯 Listening for real-time data... (Press Ctrl+C to stop)")
    try:
        await asyncio.sleep(300)  # Run for 5 minutes
    except KeyboardInterrupt:
        print("⏹️ Stopping...")
    
    # Clean up
    await rt_client.disconnect()

# Run the example
asyncio.run(main())
```

## Real-time Data Types

The following real-time data types are supported:

| Data Type | Code | Korean Name | Description |
|-----------|------|-------------|-------------|
| `ORDER_EXECUTION` | `00` | 주문체결 | Order executions for your account |
| `ACCOUNT_BALANCE` | `04` | 잔고 | Account balance changes |
| `STOCK_PRICE` | `0A` | 주식기세 | Stock price updates (non-trade) |
| `STOCK_TRADE` | `0B` | 주식체결 | Stock trade executions |
| `BEST_QUOTE` | `0C` | 주식우선호가 | Best bid/ask prices |
| `ORDER_BOOK` | `0D` | 주식호가잔량 | Full order book data |
| `AFTER_HOURS` | `0E` | 주식시간외호가 | After-hours trading data |
| `DAILY_TRADER` | `0F` | 주식당일거래원 | Daily trader information |
| `ETF_NAV` | `0G` | ETF NAV | ETF Net Asset Value |
| `PRE_MARKET` | `0H` | 주식예상체결 | Pre-market expected trades |
| `SECTOR_INDEX` | `0J` | 업종지수 | Sector index updates |
| `SECTOR_CHANGE` | `0U` | 업종등락 | Sector rise/fall statistics |
| `STOCK_INFO` | `0g` | 주식종목정보 | Stock information changes |
| `ELW_THEORY` | `0m` | ELW 이론가 | ELW theoretical prices |
| `MARKET_TIME` | `0s` | 장시작시간 | Market opening time |
| `ELW_INDICATOR` | `0u` | ELW 지표 | ELW indicators |
| `PROGRAM_TRADING` | `0w` | 종목프로그램매매 | Program trading data |
| `VI_TRIGGER` | `1h` | VI발동/해제 | Volatility Interruption triggers |

## Subscription Methods

### Stock Prices

Subscribe to real-time stock price updates:

```python
# Single stock
await rt_client.subscribe_stock_price("005930")

# Multiple stocks
await rt_client.subscribe_stock_price(["005930", "000660", "035420"])
```

### Order Book

Subscribe to order book (depth) data:

```python
# Single stock order book
await rt_client.subscribe_order_book("005930")

# Multiple stocks
await rt_client.subscribe_order_book(["005930", "000660"])
```

### Account Updates

Subscribe to your account balance and order execution updates:

```python
# Account-wide updates
await rt_client.subscribe_account_updates()
```

### Sector Indices

Subscribe to sector index updates:

```python
# KOSPI index
await rt_client.subscribe_sector_index("001")

# Multiple indices
await rt_client.subscribe_sector_index(["001", "002", "003"])
```

### ETF NAV

Subscribe to ETF Net Asset Value updates:

```python
# Single ETF
await rt_client.subscribe_etf_nav("069500")  # KODEX 200

# Multiple ETFs
await rt_client.subscribe_etf_nav(["069500", "114800"])
```

### ELW Data

Subscribe to ELW theory prices and indicators:

```python
# ELW data
await rt_client.subscribe_elw_data("57JBHH")
```

## Working with Callbacks

Callbacks are functions that get called when real-time data is received. They can be synchronous or asynchronous:

```python
# Synchronous callback
def sync_callback(data):
    print(f"Sync: {data.symbol} = {data.values.get('10')}")

# Asynchronous callback
async def async_callback(data):
    # Can perform async operations
    await some_async_operation(data)
    print(f"Async: {data.symbol} = {data.values.get('10')}")

# Add callbacks
rt_client.add_callback(RealtimeDataType.STOCK_TRADE, sync_callback)
rt_client.add_callback(RealtimeDataType.STOCK_TRADE, async_callback)

# Remove callbacks
rt_client.remove_callback(RealtimeDataType.STOCK_TRADE, sync_callback)
```

## Data Fields

Real-time data contains various fields. Here are some important ones:

### Stock Trade Data (0B)

| Field | Korean Name | Description |
|-------|-------------|-------------|
| `10` | 현재가 | Current price |
| `11` | 전일대비 | Change from previous day |
| `12` | 등락율 | Change percentage |
| `13` | 누적거래량 | Cumulative volume |
| `15` | 거래량 | Trade volume |
| `20` | 체결시간 | Trade time |
| `27` | 매도호가 | Best ask price |
| `28` | 매수호가 | Best bid price |

### Order Book Data (0D)

| Field | Korean Name | Description |
|-------|-------------|-------------|
| `41-45` | 매도호가1-5 | Ask prices (levels 1-5) |
| `51-55` | 매수호가1-5 | Bid prices (levels 1-5) |
| `61-65` | 매도호가잔량1-5 | Ask quantities (levels 1-5) |
| `71-75` | 매수호가잔량1-5 | Bid quantities (levels 1-5) |

### Account Data (00)

| Field | Korean Name | Description |
|-------|-------------|-------------|
| `9201` | 계좌번호 | Account number |
| `9001` | 종목코드 | Stock symbol |
| `913` | 주문상태 | Order status |
| `900` | 주문수량 | Order quantity |
| `901` | 주문가격 | Order price |
| `910` | 체결가 | Execution price |
| `911` | 체결량 | Execution quantity |

## Advanced Usage

### Context Manager

Use the context manager for automatic connection management:

```python
from pyheroapi import RealtimeContext, create_realtime_client

async def main():
    rt_client = create_realtime_client("your_token", is_production=False)
    
    async with RealtimeContext(rt_client) as client:
        # Add callbacks
        client.add_callback("0B", price_callback)
        
        # Subscribe
        await client.subscribe_stock_price("005930")
        
        # Listen
        await asyncio.sleep(60)
        
        # Automatic cleanup when exiting context
```

### Custom Subscription Management

For advanced users who need fine-grained control:

```python
from pyheroapi.realtime import RealtimeSubscription

# Create custom subscription
subscription = RealtimeSubscription(
    symbols=["005930", "000660"],
    data_types=[RealtimeDataType.STOCK_TRADE, RealtimeDataType.ORDER_BOOK],
    group_no="1",
    refresh="0"  # Remove existing subscriptions
)

# Send custom subscription
await rt_client._send_subscription(subscription, "REG")

# Store subscription for later management
rt_client.subscriptions["my_custom"] = subscription
```

### Multiple Callback Handlers

Organize your callbacks by creating separate handler classes:

```python
class PriceHandler:
    def __init__(self):
        self.prices = {}
    
    async def handle_price_update(self, data):
        self.prices[data.symbol] = float(data.values.get("10", 0))
        print(f"Price updated: {data.symbol} = ₩{self.prices[data.symbol]:,.0f}")

class VolumeHandler:
    def __init__(self):
        self.volumes = {}
    
    async def handle_volume_update(self, data):
        self.volumes[data.symbol] = int(data.values.get("13", 0))
        print(f"Volume updated: {data.symbol} = {self.volumes[data.symbol]:,}")

# Usage
price_handler = PriceHandler()
volume_handler = VolumeHandler()

rt_client.add_callback(RealtimeDataType.STOCK_TRADE, price_handler.handle_price_update)
rt_client.add_callback(RealtimeDataType.STOCK_TRADE, volume_handler.handle_volume_update)
```

## Error Handling

The real-time client includes automatic reconnection and error handling:

```python
# Configure auto-reconnection
rt_client = create_realtime_client(
    access_token="your_token",
    auto_reconnect=True,
    max_reconnect_attempts=5,
    reconnect_delay=10  # seconds
)

try:
    await rt_client.connect()
    # Your subscription code here
except Exception as e:
    print(f"Connection failed: {e}")
```

## Performance Tips

1. **Limit Subscriptions**: Only subscribe to data you actually need
2. **Efficient Callbacks**: Keep callback functions lightweight and fast
3. **Batch Processing**: Consider batching updates if you have high-frequency data
4. **Memory Management**: Remove unused callbacks and subscriptions

```python
# Efficient callback example
async def efficient_callback(data):
    # Quick processing
    symbol = data.symbol
    price = data.values.get("10")
    
    # Delegate heavy processing to background task
    if needs_heavy_processing(symbol, price):
        asyncio.create_task(heavy_processing(symbol, price))

# Memory management
async def cleanup():
    # Remove specific subscription
    await rt_client.unsubscribe("price_005930")
    
    # Remove all subscriptions
    await rt_client.unsubscribe_all()
    
    # Disconnect
    await rt_client.disconnect()
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure `websockets` is installed
   ```bash
   pip install websockets
   ```

2. **Connection Failed**: Check your access token and network connection

3. **No Data Received**: Verify your subscriptions and market hours

4. **Memory Usage**: Monitor callback performance and subscription count

### Debug Mode

Enable logging for debugging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('KiwoomRealtimeClient')
```

### Rate Limiting

Be aware of API rate limits:
- Maximum 100 subscriptions per connection
- Subscription requests are rate-limited
- Consider using multiple connections for high-volume applications

## Complete Example

Here's a comprehensive example that demonstrates most features:

```python
import asyncio
import logging
from datetime import datetime
import pyheroapi
from pyheroapi import RealtimeDataType

# Configure logging
logging.basicConfig(level=logging.INFO)

class MarketDataProcessor:
    def __init__(self):
        self.prices = {}
        self.volumes = {}
        self.order_books = {}
    
    async def handle_price_update(self, data):
        symbol = data.symbol
        current_price = data.values.get("10", "N/A")
        change = data.values.get("11", "N/A")
        change_rate = data.values.get("12", "N/A")
        volume = data.values.get("15", "N/A")
        time = data.values.get("20", "N/A")
        
        print(f"📈 {symbol}: ₩{current_price} ({change}, {change_rate}%) Vol: {volume} at {time}")
        
        # Store for later use
        self.prices[symbol] = {
            "price": current_price,
            "change": change,
            "change_rate": change_rate,
            "timestamp": datetime.now()
        }
    
    async def handle_order_book(self, data):
        symbol = data.symbol
        values = data.values
        
        # Extract best 3 levels
        order_book = {
            "asks": [],
            "bids": []
        }
        
        for i in range(1, 4):  # Top 3 levels
            ask_price = values.get(f"4{i}", "")
            ask_qty = values.get(f"6{i}", "")
            bid_price = values.get(f"5{i}", "")
            bid_qty = values.get(f"7{i}", "")
            
            if ask_price and ask_qty:
                order_book["asks"].append({"price": ask_price, "quantity": ask_qty})
            if bid_price and bid_qty:
                order_book["bids"].append({"price": bid_price, "quantity": bid_qty})
        
        self.order_books[symbol] = order_book
        print(f"📊 {symbol} Order Book: {len(order_book['asks'])} asks, {len(order_book['bids'])} bids")
    
    async def handle_account_update(self, data):
        values = data.values
        
        if data.data_type == "00":  # Order execution
            symbol = values.get("9001", "N/A")
            status = values.get("913", "N/A")
            quantity = values.get("900", "N/A")
            price = values.get("901", "N/A")
            
            print(f"🏦 Order: {symbol} - {status} ({quantity} @ ₩{price})")

async def main():
    # Connect to API
    api = pyheroapi.connect("your_app_key", "your_secret_key", sandbox=True)
    
    # Create data processor
    processor = MarketDataProcessor()
    
    # Get real-time client
    rt_client = api.realtime
    
    # Add callbacks
    rt_client.add_callback(RealtimeDataType.STOCK_TRADE, processor.handle_price_update)
    rt_client.add_callback(RealtimeDataType.ORDER_BOOK, processor.handle_order_book)
    rt_client.add_callback(RealtimeDataType.ORDER_EXECUTION, processor.handle_account_update)
    
    try:
        # Connect
        print("🔌 Connecting to real-time data...")
        await rt_client.connect()
        print("✅ Connected!")
        
        # Subscribe to multiple data streams
        symbols = ["005930", "000660", "035420"]  # Samsung, SK Hynix, NAVER
        
        await rt_client.subscribe_stock_price(symbols)
        await rt_client.subscribe_order_book(symbols[0])  # Order book for Samsung only
        await rt_client.subscribe_account_updates()
        
        print(f"📡 Subscribed to {len(symbols)} stocks")
        print("🎯 Listening for real-time data... (Press Ctrl+C to stop)")
        
        # Run for specified time
        await asyncio.sleep(300)  # 5 minutes
        
    except KeyboardInterrupt:
        print("\n⏹️ Stopping real-time data stream...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        print("🧹 Cleaning up...")
        await rt_client.unsubscribe_all()
        await rt_client.disconnect()
        print("✅ Cleanup complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

This real-time functionality provides a powerful way to build trading applications, monitoring dashboards, and algorithmic trading systems with live market data from Kiwoom Securities. 