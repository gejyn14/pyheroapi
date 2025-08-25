# Samsung Stock Data Test - Production Environment

This directory contains test scripts to verify if the pyheroapi correctly retrieves Samsung Electronics (005930) stock information using **PRODUCTION** API credentials.

## Test Scripts

### 1. Quick Test (`quick_samsung_test.py`)
A simple, fast test to quickly verify basic Samsung stock data retrieval using production environment.

**Features:**
- Tests connection to production API
- Retrieves real current price
- Gets live quote data (bid/ask)
- Fetches recent historical data
- Clean, easy-to-read output

### 2. Production-Specific Test (`quick_samsung_test_production.py`)
Enhanced production test with market context and detailed analysis.

**Features:**
- Production environment warnings and info
- Market hours detection
- Detailed price analysis with context
- Bid-ask spread calculation
- Trading volume information
- Enhanced error handling for production

### 3. Comprehensive Test (`test_samsung_stock.py`)
A thorough test suite that validates all aspects of Samsung stock data retrieval in production.

**Features:**
- Tests both basic client and easy API
- Production environment connection testing
- Real market data retrieval
- Quote data validation
- Historical data testing
- Stock search functionality
- Detailed error reporting
- Success rate calculation

## Usage

### Prerequisites

1. **API Credentials**: You need valid Kiwoom Securities API credentials
   - App Key (`KIWOOM_APP_KEY`)
   - Secret Key (`KIWOOM_SECRET_KEY`)

2. **Python Environment**: Make sure pyheroapi is available
   ```bash
   # If running from project directory
   export PYTHONPATH=$PWD:$PYTHONPATH
   
   # Or install the package
   pip install -e .
   ```

### Running the Tests

#### Method 1: Environment Variables (Recommended)
```bash
# Set your PRODUCTION credentials
export KIWOOM_APP_KEY="your_production_app_key"
export KIWOOM_SECRET_KEY="your_production_secret_key"

# Run quick test (uses production environment)
python quick_samsung_test.py

# Run production-specific test with enhanced features
python quick_samsung_test_production.py

# Run comprehensive test (uses production environment)
python test_samsung_stock.py
```

#### Method 2: Command Line Arguments
```bash
# Quick test with production credentials
python quick_samsung_test.py your_app_key your_secret_key

# Enhanced production test
python quick_samsung_test_production.py your_app_key your_secret_key

# Comprehensive test with production credentials
python test_samsung_stock.py your_app_key your_secret_key

# Use sandbox environment (if you have sandbox credentials)
python test_samsung_stock.py your_app_key your_secret_key sandbox
```

### Expected Output

#### Quick Test Success (Production):
```
✅ Successfully imported pyheroapi
🚀 Quick Samsung Stock Test
========================================
📋 Using production credentials from command line
⚠️  Using PRODUCTION environment with real market data

📊 Testing Samsung Electronics (005930)...
✅ Successfully connected to API
✅ Created stock object for 005930
📈 Current Price: ₩74,500
✅ Successfully retrieved quote data
💵 Best Bid: ₩74,400
💵 Best Ask: ₩74,500
📅 Retrieved 3 days of historical data
📊 Latest close: ₩74,500 on 2024-01-15

🎉 Quick test completed successfully!
✅ Samsung stock data retrieval appears to be working!
```

#### Production-Specific Test Success:
```
============================================================
📋 PRODUCTION ENVIRONMENT INFORMATION
============================================================
🏭 Environment: Kiwoom Securities Production API
🌐 Endpoint: https://api.kiwoom.com
📊 Data: Real, live market data
⏰ Updates: Real-time during market hours
💰 Stock: Samsung Electronics (005930)
📈 Market: KOSPI (Korea Exchange)

🏭 Samsung Stock Test - PRODUCTION ENVIRONMENT
==================================================
⚠️  WARNING: This will use REAL market data and production API limits
==================================================
📋 Using production credentials from environment variables

🎯 About to test Samsung Electronics (005930) using production API
   📊 This will retrieve real market data
   ⏰ Current time: 2024-01-15 14:30:00
   🟢 Current time suggests market may be open (9 AM - 3 PM)

📡 Connecting to Kiwoom PRODUCTION API...
✅ Successfully connected to PRODUCTION API
🔗 Connected to: https://api.kiwoom.com

💰 Retrieving current Samsung stock price...
📈 Current Price: ₩74,500
   📊 Price is above ₩70,000 (typical range)

📋 Retrieving quote data (order book)...
✅ Successfully retrieved real-time quote data
💵 Best Bid: ₩74,400
💵 Best Ask: ₩74,500
📊 Bid-Ask Spread: ₩100 (0.134%)
📦 Total Bid Quantity: 15,420 shares
📦 Total Ask Quantity: 12,890 shares

🏆 SUCCESS: Samsung stock data retrieval is working correctly!
📊 Your production API credentials are valid and functional
✅ You can proceed with confidence to build your application
```

#### Comprehensive Test Success:
```
============================================================
🧪 SAMSUNG ELECTRONICS STOCK DATA TEST
============================================================
📊 Testing stock code: 005930
🏢 Company: 삼성전자
🔧 Environment: Production
⏰ Test started: 2024-01-15T10:30:00.123456

🔌 Testing Basic Client Connection...
✅ Basic Client Connection: PASSED

🚀 Testing Easy API Connection...
✅ Easy API Connection: PASSED

📊 Testing Samsung Quote (Basic Client) - Code: 005930...
   📈 Buy Price: ₩74,400
   📉 Sell Price: ₩74,500
✅ Samsung Quote (Basic Client): PASSED

... (more tests)

============================================================
📋 TEST SUMMARY
============================================================
✅ Tests Passed: 6
❌ Tests Failed: 0
📊 Success Rate: 100.0%

📦 Data successfully retrieved from:
   ✓ Basic Client Connection
   ✓ Easy API Connection
   ✓ Samsung Quote (Basic Client)
   ✓ Samsung Quote (Easy API)
   ✓ Samsung Historical Data
   ✓ Samsung Search

🎯 Samsung Stock Test Complete!
🎉 All tests passed! Samsung stock data retrieval is working correctly.
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   ❌ Basic Client Connection: FAILED
   Error: Token issuance failed: 401
   ```
   - Check your API credentials
   - Ensure they're valid and not expired
   - Verify you're using the correct environment (sandbox/production)

2. **Import Error**
   ```
   ❌ Failed to import pyheroapi: No module named 'pyheroapi'
   ```
   - Make sure you're in the project directory
   - Run `export PYTHONPATH=$PWD:$PYTHONPATH`
   - Or install the package: `pip install -e .`

3. **No Data Returned**
   ```
   ⚠️ Current price not available
   ⚠️ No historical data available
   ```
   - Check if the market is open
   - Verify Samsung's stock code (005930) is correct
   - Try with a different time period

4. **Rate Limiting**
   ```
   ❌ API call failed: Rate limit exceeded
   ```
   - Wait a few seconds and try again
   - The API has built-in rate limiting protection

### Testing with Different Stocks

You can modify the scripts to test other Korean stocks:

```python
# In the scripts, change:
SAMSUNG_CODE = "005930"  # Samsung Electronics

# To test other stocks:
# "000660"  # SK Hynix
# "035420"  # NAVER
# "005380"  # Hyundai Motor
# "068270"  # Celltrion
```

## Samsung Electronics (005930) Information

- **Company Name**: 삼성전자 (Samsung Electronics)
- **Stock Code**: 005930
- **Market**: KOSPI
- **Sector**: Technology/Semiconductors
- **Currency**: KRW (Korean Won)

This is one of the most liquid and actively traded stocks on the Korean market, making it an excellent test case for API functionality.

## Next Steps

If the Samsung stock tests pass:
1. ✅ Your API connection is working
2. ✅ Authentication is successful
3. ✅ Data retrieval functions are operational
4. ✅ You can safely proceed to test other stocks or implement your application

If tests fail, check the error messages and refer to the troubleshooting section above. 