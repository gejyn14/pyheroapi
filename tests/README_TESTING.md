# Testing Real Data Reception - PyHero API

This directory contains comprehensive tests for verifying that your PyHero API setup can receive actual data from the Kiwoom Securities API.

## Test Types

### 1. Unit Tests (`test_realtime.py`)
- **Purpose**: Test internal logic and data parsing
- **Method**: Uses mocks and simulated data
- **Run**: `pytest tests/test_realtime.py -v`
- **Status**: ✅ All 63 tests pass (skipped when websockets unavailable)

### 2. Integration Tests (`test_realtime_integration.py`)
- **Purpose**: Test actual API connections and real data reception
- **Method**: Connects to real Kiwoom servers
- **Run**: `pytest tests/test_realtime_integration.py -v`
- **Requirements**: Valid API credentials, network connectivity

### 3. Quick Data Reception Test (`test_real_data_reception.py`)
- **Purpose**: Simple verification that data is being received
- **Method**: Interactive test with real-time feedback
- **Run**: `python tests/test_real_data_reception.py`
- **Best for**: Quick verification and debugging

## Prerequisites

### Environment Variables
Set these before running integration tests:
```bash
export KIWOOM_APPKEY="your_app_key_here"
export KIWOOM_SECRETKEY="your_secret_key_here"

# Optional - if not set, will be generated from app key and secret key
export KIWOOM_ACCESS_TOKEN="your_access_token_here"
```

### Dependencies
```bash
pip install websockets pytest pytest-asyncio
```

## How to Test Real Data Reception

### Option 1: Quick Interactive Test ⚡
```bash
# Simple test with real-time feedback
python tests/test_real_data_reception.py
```
**What this does:**
- ✅ Checks environment variables
- 🔌 Tests WebSocket connection
- 📈 Subscribes to stock data (Samsung, SKHynix, NAVER)
- 🔍 Requests conditional search list
- ⏱️ Collects data for 15 seconds
- 📊 Shows real-time statistics
- 📋 Displays summary of received data

### Option 2: Comprehensive Integration Tests 🧪
```bash
# Run all integration tests
pytest tests/test_realtime_integration.py -v

# Run specific test categories
pytest tests/test_realtime_integration.py::TestRealConnectionAndData -v
pytest tests/test_realtime_integration.py::TestConditionalSearchIntegration -v
pytest tests/test_realtime_integration.py::TestDataValidation -v
```

### Option 3: Unit Tests (Mocked) 🔧
```bash
# Run unit tests (don't require API credentials)
pytest tests/test_realtime.py -v
```

## What to Expect

### Successful Data Reception ✅
When everything is working, you should see:
```
📈 Received 5 stock data updates:
  📊 005930 (삼성전자): 0A
      Values: {'10': '75000', '11': '1000', '12': '1.35'}...
      Timestamp: 153045
  
🔍 Received conditional search list with 12 items:
  1: 대형주 상승
  2: 거래량 급증
  
✅ SUCCESS: Real stock data was received!
   Your API connection is working correctly.
```

### Common Issues and Solutions ❌

#### No Data Received
```
⚠️ WARNING: No stock data received.
   This might be normal if markets are closed or in sandbox mode.
```
**Solutions:**
- ✅ Check if markets are open (Mon-Fri 9AM-4PM KST)
- ✅ Try production mode during market hours
- ✅ Verify API credentials are correct
- ✅ Check network connectivity

#### Connection Failed
```
❌ Connection test failed: Authentication failed
```
**Solutions:**
- ✅ Verify `KIWOOM_APPKEY`, `KIWOOM_SECRETKEY`, and `KIWOOM_ACCESS_TOKEN` (if set)
- ✅ Check if token has expired
- ✅ Ensure credentials have real-time data permissions
- ✅ Let the system generate token from app key and secret key if not provided

#### Module Import Error
```
❌ Failed to import PyHero API: No module named 'websockets'
```
**Solutions:**
- ✅ Install missing dependencies: `pip install websockets`
- ✅ Run from correct directory: `cd /path/to/pyheroapi`

## Test Scenarios

### 1. Market Hours vs. After Hours
- **Market Hours**: Real stock price updates, high data volume
- **After Hours**: Limited or no price updates, but connection should work
- **Weekends**: Minimal data, connection testing only

### 2. Sandbox vs. Production
- **Sandbox Mode** (`is_production=False`): Safe testing, simulated data
  - SANDBOX MODE: set is_production=False explicitly
- **Production Mode** (`is_production=True`): Real market data, real money implications

### 3. Data Types Tested
- 📈 **Stock Prices**: Real-time price updates
- 📊 **Stock Trades**: Transaction data
- 📋 **Order Book**: Bid/ask levels
- 🔍 **Conditional Search**: Custom screening results
- 💰 **Account Updates**: Portfolio changes (requires account permissions)

## Advanced Testing

### Long-Running Test
```python
# Test connection stability over 30 minutes
pytest tests/test_realtime_integration.py::TestPerformanceAndStability::test_long_running_connection -v -s
```

### Multiple Subscriptions Test
```python
# Test handling multiple simultaneous data streams
pytest tests/test_realtime_integration.py::TestPerformanceAndStability::test_multiple_subscriptions_stability -v
```

### Production Mode Test
```python
# Test with real market data (market hours only)
pytest tests/test_realtime_integration.py::TestRealConnectionAndData::test_real_market_data_reception -v
```

## Debugging Tips

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check WebSocket Messages
```python
# Add this to your client callbacks to see raw messages
def debug_callback(data):
    print(f"Raw data: {data}")
    
client.add_callback(RealtimeDataType.STOCK_PRICE, debug_callback)
```

### Monitor Network Traffic
```bash
# Check if requests are reaching Kiwoom servers
netstat -an | grep :443  # HTTPS connections
```

## Interpreting Results

### Data Volume Expectations
- **High Activity Stocks** (Samsung, SKHynix): 10-100 updates/minute during market hours
- **Low Activity Stocks**: 1-10 updates/minute
- **After Hours**: 0-5 updates/minute

### Data Quality Checks
The tests automatically verify:
- ✅ Korean stock code format (6 digits)
- ✅ Timestamp format (HHMMSS)
- ✅ Price data is numeric and positive
- ✅ Data types match expected values
- ✅ Required fields are present

## Getting Help

If your tests are failing:

1. **Check the basics**: Environment variables, network, market hours
2. **Run the simple test first**: `python tests/test_real_data_reception.py`
3. **Check examples**: Look at `examples/07_realtime_websocket.py`
4. **Review API docs**: Check your Kiwoom API permissions
5. **Test with minimal code**: Start with just connection testing

Remember: Real data reception depends on external factors (market hours, network, API status), so some variation in results is normal! 