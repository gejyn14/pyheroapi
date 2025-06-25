# PyHero API Examples

This directory contains comprehensive examples demonstrating all features of the PyHero API for Korean securities trading.

## 🚀 Quick Start

1. **Set Environment Variables:**
   ```bash
   export KIWOOM_APPKEY="your_app_key_here"
   export KIWOOM_SECRETKEY="your_secret_key_here"
   ```

2. **Install Dependencies:**
   ```bash
   pip install pyheroapi
   ```

3. **Run Examples:**
   ```bash
   python examples/01_authentication.py
   ```

## 📚 Example Overview

### 01. Authentication (`01_authentication.py`)
**Basic API authentication and token management**

- ✅ Token issuance and validation
- ✅ Client creation with credentials
- ✅ Token revocation
- ✅ Error handling for authentication

```python
from pyheroapi import KiwoomClient

client = KiwoomClient.create_with_credentials(
    appkey="your_key",
    secretkey="your_secret",
    is_production=False
)
```

### 02. Market Data (`02_market_data.py`)
**Comprehensive market data retrieval and analysis**

- 📊 Stock quotes and real-time prices
- 📈 OHLCV historical data
- 📉 Market performance indicators
- ⏰ Intraday and minute data
- 🌙 After-hours trading data
- 🤖 Program trading data

```python
# Get stock quote
quote = client.get_quote("005930")
print(f"Samsung Price: {quote.current_price}")

# Get OHLCV data
ohlcv = client.get_stock_ohlcv("005930", count=100)
```

### 03. Trading & Orders (`03_trading_orders.py`)
**Complete trading operations and order management**

- 🛒 Basic stock trading (buy/sell)
- 💳 Credit trading (margin trading)
- ✏️ Order modifications and cancellations
- 📊 Order status tracking
- 🎯 Different order types
- 💼 Account management
- ⚠️ Trading safety practices

```python
# Buy stock
response = client.buy_stock("005930", 10, 75000)

# Check account balance
balance = client.get_deposit_details()
print(f"Available Cash: {balance.ord_psbl_cash}")
```

### 04. ETF & ELW (`04_etf_elw.py`)
**ETF and ELW analysis and trading**

- 📊 ETF information and NAV analysis
- 📈 ETF market data and trends
- 🎯 ELW information and Greeks
- 📉 ELW rankings and movement tracking
- 💹 ETF/ELW trading data
- 🔍 Advanced analytics

```python
# Get ETF info
etf_info = client.get_etf_info("069500")  # KODEX 200
print(f"NAV: {etf_info.nav}")

# Find active ELWs
elws = client.get_elw_condition_search(underlying_asset_code="201")
```

### 05. Rankings & Analysis (`05_rankings_analysis.py`)
**Market rankings and comprehensive analysis**

- 📊 Volume and trading rankings
- 📈 Price change rankings (gainers/losers)
- 🌍 Foreign and institutional trading
- 📋 Order book rankings
- 🏢 Sector and industry analysis
- 🤖 Program trading analysis
- 💳 Credit trading rankings

```python
# Get top gainers
gainers = client.get_change_rate_ranking(
    market_type="001",  # KOSPI
    sort_type="1"       # Up rate
)

# Foreign trading
foreign = client.get_foreign_period_trading_ranking(
    market_type="001",
    sort_type="1"       # Net buying
)
```

### 06. Charts & Technical Analysis (`06_charts_technical.py`)
**Chart data and technical analysis**

- 📊 Stock charts (tick, minute, daily, weekly, monthly, yearly)
- 🏢 Sector charts and analysis
- 📈 Technical indicators (SMA, volume analysis)
- 🎯 Chart pattern recognition
- 📉 Price action analysis
- 🔍 Support and resistance levels

```python
# Get daily chart
daily_chart = client.get_stock_daily_chart("005930")

# Calculate SMA
prices = [day['close'] for day in daily_chart['daily_data'][:20]]
sma20 = sum(prices) / len(prices)
```

### 07. Real-time WebSocket (`07_realtime_websocket.py`)
**Real-time data streaming via WebSocket**

- 📈 Real-time stock price streaming
- 📋 Real-time order book updates
- 💼 Real-time account updates
- ⚡ Event-driven callbacks
- 🔧 WebSocket connection management
- 🔄 Multi-symbol subscriptions

```python
# Async real-time streaming
realtime_client = RealtimeClient(appkey="your_key")
await realtime_client.connect()
await realtime_client.subscribe_price("005930")
```

## 🛠️ Usage Instructions

### Environment Setup

1. **Get API Credentials:**
   - Register at Kiwoom Securities developer portal
   - Obtain your `appkey` and `secretkey`

2. **Set Environment Variables:**
   ```bash
   # Linux/Mac
   export KIWOOM_APPKEY="your_actual_app_key"
   export KIWOOM_SECRETKEY="your_actual_secret_key"
   
   # Windows
   set KIWOOM_APPKEY=your_actual_app_key
   set KIWOOM_SECRETKEY=your_actual_secret_key
   ```

3. **Python Environment:**
   ```bash
   pip install pyheroapi asyncio
   ```

### Running Examples

**Individual Examples:**
```bash
# Run specific example
python examples/01_authentication.py
python examples/02_market_data.py
python examples/03_trading_orders.py
```

**All Examples:**
```bash
# Run all examples sequentially
for file in examples/*.py; do
    echo "Running $file..."
    python "$file"
    echo "---"
done
```

### Testing vs Production

**⚠️ IMPORTANT: All examples use SANDBOX mode by default**

```python
# Sandbox mode (safe for testing)
client = KiwoomClient.create_with_credentials(
    appkey=appkey,
    secretkey=secretkey,
    is_production=False  # SANDBOX MODE: set is_production=False explicitly
)

# Production mode (real money!)
client = KiwoomClient.create_with_credentials(
    appkey=appkey,
    secretkey=secretkey,
    is_production=True   # ← PRODUCTION MODE
)
```

## 📊 Feature Coverage

| Category | Features Covered | Example File |
|----------|-----------------|--------------|
| **Authentication** | Token management, client setup | `01_authentication.py` |
| **Market Data** | Quotes, OHLCV, performance indicators | `02_market_data.py` |
| **Trading** | Buy/sell, credit trading, order management | `03_trading_orders.py` |
| **ETF/ELW** | ETF analysis, ELW Greeks, rankings | `04_etf_elw.py` |
| **Rankings** | Volume, price, foreign/institutional | `05_rankings_analysis.py` |
| **Charts** | All timeframes, technical analysis | `06_charts_technical.py` |
| **Real-time** | WebSocket streaming, event handling | `07_realtime_websocket.py` |

## 🔧 Advanced Usage

### Custom Error Handling
```python
from pyheroapi.exceptions import KiwoomAPIError

try:
    result = client.get_quote("005930")
except KiwoomAPIError as e:
    print(f"API Error: {e.error_code} - {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Async/Await with Real-time
```python
import asyncio

async def my_trading_bot():
    realtime = RealtimeClient(appkey="your_key")
    await realtime.connect()
    
    def on_price_update(data):
        symbol = data['symbol']
        price = data['current_price']
        print(f"{symbol}: {price}")
    
    realtime.on_price_update = on_price_update
    await realtime.subscribe_price("005930")
    
    # Keep running
    await asyncio.sleep(3600)  # 1 hour

# Run the bot
asyncio.run(my_trading_bot())
```

### Batch Operations
```python
# Get multiple stock quotes
symbols = ["005930", "000660", "035420", "005380"]
quotes = {}

for symbol in symbols:
    try:
        quote = client.get_quote(symbol)
        quotes[symbol] = quote.current_price
    except Exception as e:
        print(f"Error getting {symbol}: {e}")

print("Current Prices:", quotes)
```

## 💡 Tips & Best Practices

### 1. **Rate Limiting**
- The API has rate limits
- Add delays between requests when processing many symbols
- Use real-time WebSocket for continuous updates

### 2. **Error Handling**
- Always wrap API calls in try-catch blocks
- Check for `KiwoomAPIError` specifically
- Log errors for debugging

### 3. **Real-time Best Practices**
- Use async/await for real-time features
- Properly handle connection lifecycle
- Unsubscribe when done to free resources

### 4. **Trading Safety**
- Always test in sandbox mode first
- Use small quantities for testing
- Implement proper risk management
- Never trade money you can't afford to lose

### 5. **Performance Optimization**
- Cache frequently used data
- Batch similar requests
- Use appropriate timeframes for charts
- Limit real-time subscriptions to what you need

## 🐛 Troubleshooting

### Common Issues

**1. Authentication Errors**
```bash
Error: Invalid credentials
```
- Check your `appkey` and `secretkey`
- Ensure environment variables are set correctly
- Verify credentials are for the correct environment (sandbox/production)

**2. Rate Limit Exceeded**
```bash
Error: Rate limit exceeded
```
- Add delays between requests: `time.sleep(0.1)`
- Reduce the frequency of API calls
- Use real-time WebSocket for live data

**3. Real-time Connection Issues**
```bash
Error: WebSocket connection failed
```
- Check internet connection
- Verify credentials support real-time access
- Ensure no firewall blocking WebSocket connections

**4. No Data Returned**
```bash
Error: No data available
```
- Check if market is open
- Verify symbol codes are correct
- Some data may not be available on weekends/holidays

### Getting Help

1. **Check Documentation:** Review the API documentation
2. **Enable Debug Logging:** Add debug prints to see API responses
3. **Test with Known Symbols:** Use major stocks like "005930" (Samsung)
4. **Verify Environment:** Ensure you're using the correct environment (sandbox/production)

## 📝 Example Outputs

### Market Data Example Output:
```
🚀 PyHero API - Market Data Example

=== Stock Quotes ===
📊 Samsung Electronics (005930):
  Current Price: 75,000
  Change: +1,000 (+1.35%)
  Volume: 15,234,567
  
📊 SK Hynix (000660):
  Current Price: 132,500
  Change: -2,500 (-1.85%)
  Volume: 8,456,123
```

### Trading Example Output:
```
💰 Account Balance:
  Total Evaluation Amount: 10,000,000
  Order Possible Cash: 5,000,000
  
🛒 Market Buy Order:
✓ Order placed successfully
  Order Number: 202412060001
  Symbol: 005930
  Quantity: 1
```

## 🔗 Related Resources

- **PyHero API Documentation:** [API Docs](https://docs.pyheroapi.com)
- **Kiwoom Securities:** [Developer Portal](https://developers.kiwoom.com)
- **Korean Stock Market:** [KRX](https://www.krx.co.kr)

## ⚖️ Disclaimer

These examples are for educational purposes only. Always:

- ✅ Test thoroughly in sandbox mode
- ✅ Understand the risks of trading
- ✅ Use proper risk management
- ✅ Comply with all applicable regulations
- ❌ Never trade money you cannot afford to lose

---

**Happy Trading! 🚀📈** 