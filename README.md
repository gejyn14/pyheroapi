# Kiwoom API Python Client

[![PyPI version](https://badge.fury.io/py/kiwoom-api.svg)](https://badge.fury.io/py/kiwoom-api)
[![Python versions](https://img.shields.io/pypi/pyversions/kiwoom-api.svg)](https://pypi.org/project/kiwoom-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for interacting with the Kiwoom Securities REST API. This library provides easy-to-use interfaces for market data retrieval, trading operations, and account management.

## Features

- 🚀 **Easy to use**: Simple and intuitive API interface
- 📊 **Market Data**: Real-time quotes, historical data, and market information
- 💹 **ETF & ELW Support**: Specialized support for ETFs and ELWs (Equity Linked Warrants)
- 🔒 **Error Handling**: Comprehensive error handling and retry mechanisms
- 📝 **Type Safety**: Full type hints for better development experience
- ⚡ **Async Support**: Built-in rate limiting and request optimization
- 🛡️ **Production Ready**: Supports both sandbox and production environments

## Installation

Install the package using pip:

```bash
pip install kiwoom-api
```

For development dependencies:

```bash
pip install kiwoom-api[dev]
```

## Quick Start

### Basic Usage

```python
from kiwoom_api import KiwoomClient

# Initialize the client
client = KiwoomClient(
    access_token="your_access_token",
    is_production=False  # Use sandbox for testing
)

# Get stock quote data
quote = client.get_quote("005930")  # Samsung Electronics
print(f"Best bid: {quote.buy_fpr_bid}")
print(f"Best ask: {quote.sel_fpr_bid}")

# Get ETF information
etf_info = client.get_etf_info("069500")  # KODEX 200
print(f"ETF Name: {etf_info.name}")
print(f"NAV: {etf_info.nav}")

# Get ELW information
elw_info = client.get_elw_info("57JBHH")
print(f"Strike Price: {elw_info.strike_price}")
print(f"Expiry Date: {elw_info.expiry_date}")
```

### Advanced Usage

```python
# Get historical price data
daily_prices = client.get_daily_prices(
    symbol="005930",
    period="D",  # Daily data
    count=30     # Last 30 days
)

# Get ETF returns over different periods
etf_returns = client.get_etf_returns(
    symbol="069500",
    etf_index_code="207",
    period="3"  # 1 year
)

# Get ELW sensitivity data (Greeks)
elw_sensitivity = client.get_elw_sensitivity("57JBHH")
for data in elw_sensitivity:
    print(f"Delta: {data.get('delta')}")
    print(f"Gamma: {data.get('gam')}")
    print(f"Theta: {data.get('theta')}")
    print(f"Vega: {data.get('vega')}")
```

### Error Handling

```python
from kiwoom_api import KiwoomClient, KiwoomAPIError, KiwoomAuthError

client = KiwoomClient(access_token="your_token")

try:
    quote = client.get_quote("005930")
except KiwoomAuthError:
    print("Authentication failed. Check your access token.")
except KiwoomAPIError as e:
    print(f"API error: {e}")
    if e.response_data:
        print(f"Error details: {e.response_data}")
```

## API Reference

### KiwoomClient

The main client class for interacting with the Kiwoom API.

#### Constructor

```python
KiwoomClient(
    access_token: str,
    is_production: bool = False,
    timeout: int = 30,
    retry_attempts: int = 3,
    rate_limit_delay: float = 0.1
)
```

**Parameters:**
- `access_token`: Your Kiwoom API access token
- `is_production`: Whether to use production or sandbox environment
- `timeout`: Request timeout in seconds
- `retry_attempts`: Number of retry attempts on failure
- `rate_limit_delay`: Delay between requests to avoid rate limiting

### Market Data Methods

#### get_quote(symbol: str) → QuoteData

Get real-time quote/order book data for a stock.

```python
quote = client.get_quote("005930")
```

#### get_daily_prices(symbol: str, period: str = "D", count: Optional[int] = None) → List[Dict]

Get historical daily price data.

```python
prices = client.get_daily_prices("005930", period="D", count=30)
```

### ETF Methods

#### get_etf_info(symbol: str) → ETFData

Get ETF information including NAV and tracking error.

```python
etf = client.get_etf_info("069500")
```

#### get_etf_returns(symbol: str, etf_index_code: str, period: str = "3") → Dict

Get ETF return data for different periods.

```python
returns = client.get_etf_returns("069500", "207", "3")
```

### ELW Methods

#### get_elw_info(symbol: str) → ELWData

Get ELW detailed information including Greeks.

```python
elw = client.get_elw_info("57JBHH")
```

#### get_elw_sensitivity(symbol: str) → List[Dict]

Get ELW sensitivity indicators (Greeks).

```python
sensitivity = client.get_elw_sensitivity("57JBHH")
```

## Data Models

The library includes comprehensive data models for type safety:

### QuoteData
- Order book data with bid/ask prices and quantities
- Total order quantities
- After-hours trading data

### MarketData
- Basic market information (price, volume, change)
- Symbol and name information

### ETFData
- ETF-specific data (NAV, tracking error, discount/premium)
- Index information

### ELWData
- ELW-specific data (strike price, expiry, conversion ratio)
- Greeks (Delta, Gamma, Theta, Vega)

## Error Handling

The library provides specific exception types for different error scenarios:

- `KiwoomAPIError`: Base exception for all API errors
- `KiwoomAuthError`: Authentication failures
- `KiwoomRequestError`: Request failures (4xx errors)
- `KiwoomRateLimitError`: Rate limit exceeded
- `KiwoomServerError`: Server errors (5xx)

## API Coverage

This library currently supports the following Kiwoom API endpoints:

### Market Data (시세)
- ✅ Stock quotes (주식호가요청 - ka10004)
- ✅ Daily/Weekly/Monthly data (주식일주월시분요청 - ka10005)
- 🔄 More endpoints coming soon...

### ETF
- ✅ ETF returns (ETF수익율요청 - ka40001)
- ✅ ETF information (ETF종목정보요청 - ka40002)
- ✅ ETF daily trends (ETF일별추이요청 - ka40003)
- 🔄 More endpoints coming soon...

### ELW
- ✅ ELW sensitivity (ELW민감도지표요청 - ka10050)
- ✅ ELW details (ELW종목상세정보요청 - ka30012)
- 🔄 More endpoints coming soon...

### Account & Trading
- 🔄 Coming soon...

## Rate Limiting

The client includes built-in rate limiting to prevent API limits from being exceeded:

- Automatic retry with exponential backoff
- Configurable delay between requests
- Proper error handling for rate limit responses

## Development

### Setup

```bash
git clone https://github.com/yourusername/kiwoom-api.git
cd kiwoom-api
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black kiwoom_api/
isort kiwoom_api/
```

### Type Checking

```bash
mypy kiwoom_api/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Guidelines

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This library is not officially affiliated with Kiwoom Securities. Use at your own risk and ensure compliance with Kiwoom's API terms of service.

## Support

- 📖 [Documentation](https://github.com/yourusername/kiwoom-api#readme)
- 🐛 [Issue Tracker](https://github.com/yourusername/kiwoom-api/issues)
- 💬 [Discussions](https://github.com/yourusername/kiwoom-api/discussions)

## Changelog

### v0.1.0
- Initial release
- Basic market data support
- ETF and ELW functionality
- Comprehensive error handling
- Type safety with Pydantic models
