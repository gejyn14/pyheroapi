# Samsung Stock Test Scripts

This directory contains test scripts specifically created to verify Samsung Electronics (005930) stock data retrieval using the pyheroapi with production credentials.

## Files

- **`quick_samsung_test.py`** - Simple, fast test for basic Samsung stock data
- **`quick_samsung_test_production.py`** - Enhanced production test with detailed analysis
- **`test_samsung_stock.py`** - Comprehensive test suite for all Samsung data functions
- **`debug_samsung_api.py`** - Debug script to inspect raw API responses
- **`SAMSUNG_TEST_README.md`** - Detailed documentation and usage instructions

## Usage

From the project root directory:

```bash
# Quick test
python samsung_stock_tests/quick_samsung_test.py your_app_key your_secret_key

# Production test with enhanced features
python samsung_stock_tests/quick_samsung_test_production.py your_app_key your_secret_key

# Comprehensive test suite
python samsung_stock_tests/test_samsung_stock.py your_app_key your_secret_key

# Debug API responses
python samsung_stock_tests/debug_samsung_api.py your_app_key your_secret_key
```

## Note

These are temporary testing scripts for development and debugging purposes. They are excluded from version control via .gitignore. 