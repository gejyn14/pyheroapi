# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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