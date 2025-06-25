# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2025-06-25

### Changed
- **Production Default**: Changed `is_production` parameter default from `False` (sandbox) to `True` (production) across all client constructors and methods
  - This prevents accidental sandbox usage in production environments
  - Sandbox mode now requires explicitly passing `is_production=False`
  - All examples and documentation updated to reflect this change

### Added
- **Sandbox Environment Variables**: Added support for `KIWOOM_MOCK_APPKEY` and `KIWOOM_MOCK_SECRETKEY` environment variables
  - When `is_production=False`, these variables are automatically used if set
  - Allows separate credentials for sandbox testing without code changes
  - Supported in all client types: main client, realtime client, and easy API wrapper
  - New function `create_realtime_client_with_credentials()` for realtime client with automatic token generation

### Security
- **Safer Defaults**: Production mode is now the default, reducing risk of accidental sandbox usage in live trading
- **Explicit Sandbox**: All sandbox usage now requires explicit `is_production=False` parameter

### Documentation
- **Updated Examples**: All examples now explicitly show `is_production=False` for sandbox mode
- **Environment Setup**: Added documentation for new sandbox environment variables
- **Testing**: Updated test suite to reflect new defaults and sandbox environment variable support

## [0.3.2]
### Added
- Clarified usage and distinction between ka10171 (조건검색 목록조회), ka10172 (조건검색 요청 일반), and ka10173 (조건검색 요청 실시간) in code and documentation.
- Improved asyncio usage examples for all conditional search TRs.
- Added new example scripts for correct ka10171, ka10172, and ka10173 usage.

### Fixed
- Documentation and code comments for accuracy regarding required request fields for each TR.

## [0.3.1]

### Added
- **Comprehensive Testing Infrastructure** for real data reception validation
- **Interactive Test Script** (`tests/test_real_data_reception.py`) with real-time feedback
- **Integration Tests** (`tests/test_realtime_integration.py`) for actual API connections
- **Environment Setup Guide** (`tests/ENVIRONMENT_SETUP.md`) with detailed instructions
- **Testing Documentation** (`tests/README_TESTING.md`) with troubleshooting guide

### Fixed
- **Environment Variable Names**: Updated to correct `KIWOOM_APPKEY`/`KIWOOM_SECRETKEY` format
- **Automatic Token Generation**: Access tokens now generated automatically from app key/secret key
- **Test Dependencies**: Proper handling of optional websockets dependency

### Changed
- **Testing Approach**: Three-tier testing (unit, integration, interactive)
- **Token Management**: Simplified credential setup - only app key and secret key required
- **Error Messages**: More helpful guidance for missing dependencies and credentials

### Documentation
- **Complete Testing Guide**: How to verify real data reception
- **Environment Setup**: Correct variable names and setup procedures
- **Troubleshooting**: Common issues and solutions for testing

## [0.3.0]

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

## [0.2.3]

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