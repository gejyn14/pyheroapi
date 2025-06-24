# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-11-25

### Added
- **Comprehensive Examples Suite**: Complete rewrite of all example files with 7 focused modules
  - `01_authentication.py` - Token management and client setup
  - `02_market_data.py` - Stock quotes, OHLCV data, and market performance
  - `03_trading_orders.py` - Order management and account operations
  - `04_etf_elw.py` - ETF and ELW analysis with Greeks and sensitivity indicators
  - `05_rankings_analysis.py` - Market rankings and institutional trading analysis
  - `06_charts_technical.py` - Chart data and technical analysis
  - `07_realtime_websocket.py` - Real-time streaming with WebSocket support

### Enhanced
- **Production-Ready Code**: All examples now include proper error handling and safety measures
- **Comprehensive Documentation**: Updated README.md with detailed usage instructions and feature coverage
- **Safety Features**: Sandbox mode enabled by default across all examples
- **Environment Configuration**: Improved environment variable setup and management
- **Real-time Capabilities**: Full WebSocket implementation for live market data streaming

### Changed
- **Example Structure**: Reorganized from simple examples to comprehensive, educational modules
- **Code Quality**: Enhanced code patterns with async/await support and proper exception handling
- **Documentation**: Improved inline documentation and usage examples throughout

### Coverage
- **163 API Methods**: Complete coverage of all available Kiwoom Securities API endpoints
- **All Major Features**: ETF, ELW, rankings, charts, real-time data, trading, and market analysis
- **Educational Value**: Progressive complexity from basic authentication to advanced trading strategies

## [0.2.3] - 2024-01-15

### Fixed
- **QuoteData Model**: Added missing `buy_fpr_bid` and `sel_fpr_bid` attributes to match actual API response structure
- **Market Status API**: Fixed "API ID is null" error by updating get_market_status() implementation
- **Quote Data Parsing**: Improved price data validation and error handling in Stock.current_price and Stock.quote properties
- **Error Handling**: Enhanced error detection to properly identify when meaningful data is not retrieved

### Added
- **Order Book Support**: Added support for multiple order book levels (buy_2th_pre_bid through buy_5th_pre_bid, etc.)
- **Production Environment**: Updated default configuration for production API usage

### Changed
- **Test Error Handling**: Improved test accuracy to only report success when actual price data is retrieved
- **Version Synchronization**: Aligned version numbers between pyproject.toml and __init__.py

### Technical Details
- Fixed AttributeError: 'QuoteData' object has no attribute 'buy_fpr_bid'
- Enhanced Samsung Electronics (005930) stock data retrieval compatibility
- Improved production API endpoint handling

## [0.2.2] - Previous Release
- Prior functionality and features

## [0.2.1] - Previous Release  
- Prior functionality and features 