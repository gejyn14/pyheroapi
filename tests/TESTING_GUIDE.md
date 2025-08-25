# 🧪 Professional Testing Guide for PyHero API

This guide explains how to use the comprehensive testing framework for PyHero API. Our testing suite is designed to be professional, thorough, and easy to use.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Test Types](#test-types)
- [Running Tests](#running-tests)
- [Configuration](#configuration)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)
- [Performance Testing](#performance-testing)
- [Best Practices](#best-practices)

## 🚀 Quick Start

### Install Dependencies

```bash
# Install with all testing dependencies
pip install -e ".[dev]"

# Or install specific test dependencies
pip install pytest pytest-cov responses black isort
```

### Run Basic Tests

```bash
# Run all unit tests
pytest tests/ -m unit

# Run with coverage
pytest tests/ -m unit --cov=pyheroapi --cov-report=html

# Use the test runner script
python scripts/run_tests.py unit --coverage
```

## 🔬 Test Types

Our testing framework includes several types of tests:

### 1. Unit Tests (`@pytest.mark.unit`)

- **Purpose**: Test individual components in isolation
- **Speed**: Fast (< 1 second per test)
- **Dependencies**: Uses mocks, no external API calls
- **When to run**: Always, on every commit

```bash
pytest tests/ -m unit -v
```

### 2. Integration Tests (`@pytest.mark.integration`)

- **Purpose**: Test real API interactions
- **Speed**: Moderate (1-10 seconds per test)
- **Dependencies**: Requires API credentials
- **When to run**: Before releases, scheduled runs

```bash
# Set environment variables first
export KIWOOM_APPKEY="your_app_key"
export KIWOOM_SECRETKEY="your_secret_key"
export RUN_INTEGRATION_TESTS=true

pytest tests/ -m integration -v
```

### 3. Performance Tests (`@pytest.mark.performance`)

- **Purpose**: Benchmark response times and resource usage
- **Speed**: Slow (10-60 seconds per test)
- **Dependencies**: May require psutil for memory monitoring
- **When to run**: Before releases, performance regression testing

```bash
export RUN_PERFORMANCE_TESTS=true
pytest tests/ -m performance -v
```

### 4. Real-time Tests (`@pytest.mark.realtime`)

- **Purpose**: Test WebSocket functionality
- **Speed**: Moderate (2-10 seconds per test)
- **Dependencies**: Requires websockets package
- **When to run**: When WebSocket features change

```bash
pytest tests/ -m realtime -v
```

### 5. Smoke Tests (`@pytest.mark.smoke`)

- **Purpose**: Quick validation of core functionality
- **Speed**: Very fast (< 0.5 seconds per test)
- **Dependencies**: Minimal
- **When to run**: On every build, as a sanity check

```bash
pytest tests/ -m smoke -q
```

## 🏃‍♂️ Running Tests

### Using pytest directly

```bash
# Run all tests
pytest tests/

# Run specific test types
pytest tests/ -m "unit"
pytest tests/ -m "unit or smoke"
pytest tests/ -m "not integration"

# Run specific test files
pytest tests/test_client.py
pytest tests/test_api_coverage.py

# Run with coverage
pytest tests/ --cov=pyheroapi --cov-report=html --cov-report=term-missing

# Run in parallel (if you have pytest-xdist)
pytest tests/ -n auto

# Run with detailed output
pytest tests/ -v --tb=short --durations=10
```

### Using the Test Runner Script

Our custom test runner provides a more user-friendly interface:

```bash
# Run unit tests
python scripts/run_tests.py unit

# Run unit tests with coverage
python scripts/run_tests.py unit --coverage

# Run integration tests (requires credentials)
python scripts/run_tests.py integration --with-credentials

# Run performance tests
python scripts/run_tests.py performance --duration 60

# Run all tests with reports
python scripts/run_tests.py all --coverage --quality --report

# Run code quality checks
python scripts/run_tests.py quality
```

## ⚙️ Configuration

### Environment Variables

```bash
# Test execution control
export RUN_INTEGRATION_TESTS=true          # Enable integration tests
export RUN_PERFORMANCE_TESTS=true          # Enable performance tests
export FORCE_MARKET_HOURS_TEST=true        # Override market hours check

# API credentials (for integration tests)
export KIWOOM_APPKEY="your_app_key"
export KIWOOM_SECRETKEY="your_secret_key"
export KIWOOM_ACCESS_TOKEN="your_access_token"  # Optional

# Test configuration
export TEST_ACCESS_TOKEN="custom_test_token"
export TEST_TIMEOUT=30                          # Test timeout in seconds
export PERFORMANCE_TEST_DURATION=60            # Performance test duration
```

### pytest.ini Configuration

Our `pytest.ini` file is already configured with:

- Test discovery patterns
- Custom markers
- Coverage settings
- Warning filters
- Report generation

## ✍️ Writing Tests

### Test Structure

Use our base test classes for consistent patterns:

```python
from tests.base import BaseUnitTest, BaseIntegrationTest, BasePerformanceTest
import pytest

class TestMyFeature(BaseUnitTest):
    """Unit tests for my feature."""

    @pytest.mark.unit
    def test_my_function(self):
        """Test my function with mocked dependencies."""
        client = self.create_mock_client()

        # Test implementation
        result = client.my_function()

        # Assertions
        assert result is not None
        self.assert_api_response_success(result)

class TestMyFeatureIntegration(BaseIntegrationTest):
    """Integration tests for my feature."""

    @pytest.mark.integration
    def test_real_api_call(self):
        """Test with real API call."""
        client = self.create_real_client()

        # Test with real API
        result = client.my_function()

        # Validate real response
        self.assert_api_response_success(result)
        self.assert_valid_korean_stock_symbol(result.get('symbol'))
```

### Using Fixtures

We provide comprehensive fixtures in `conftest.py`:

```python
def test_stock_operations(test_stock, sample_stock_quote, mock_responses):
    """Test using our pre-configured fixtures."""
    # mock_responses and sample_stock_quote are ready to use
    mock_responses.add(
        responses.POST,
        "https://openapivts.kiwoom.com:9443/api/dostk/mrkcond",
        json=sample_stock_quote,
        status=200
    )

    # test_stock is a pre-configured Stock instance
    quote = test_stock.quote
    assert quote is not None
```

### Custom Assertions

Use our custom assertions for better error messages:

```python
def test_price_validation(self):
    """Test using custom assertions."""
    self.assert_valid_korean_stock_symbol("005930")
    self.assert_valid_price("75000")
    self.assert_valid_timestamp("153000")
```

## 🔄 CI/CD Integration

### GitHub Actions

Our `.github/workflows/test.yml` provides comprehensive CI/CD:

- **Unit Tests**: Run on all Python versions (3.8-3.12)
- **Integration Tests**: Run on schedule or with `[integration]` in commit message
- **Performance Tests**: Monitor for regressions
- **Code Quality**: Black, isort, flake8, mypy
- **Security**: Bandit, safety checks
- **Coverage**: Upload to Codecov

### Running Locally Like CI

```bash
# Simulate CI environment
python scripts/run_tests.py all --coverage --quality --security
```

### Commit Message Triggers

- `[integration]` - Triggers integration tests in CI
- `[performance]` - Triggers performance tests in CI
- `[skip ci]` - Skips CI entirely

## ⚡ Performance Testing

### Benchmarking

```python
@pytest.mark.performance
def test_api_performance(self, performance_metrics):
    """Example performance test."""

    def operation():
        client.get_quote("005930")

    # Benchmark the operation
    with performance_metrics.capture_performance_metrics():
        for _ in range(100):
            operation()

    # Check performance metrics
    metrics = performance_metrics.get_metrics()
    assert metrics["execution_time"] < 5.0  # Should complete in < 5 seconds
```

### Load Testing

```python
def test_concurrent_load():
    """Test concurrent request handling."""
    tester = PerformanceTester(client)

    # Load test: 5 users for 30 seconds
    metrics = tester.load_test(
        client.get_quote,
        duration=30.0,
        concurrent_users=5,
        symbol="005930"
    )

    assert metrics.success_rate >= 95.0
    assert metrics.avg_response_time <= 1.0
```

## 📊 Test Reports and Coverage

### Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=pyheroapi --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Performance Reports

Performance tests automatically generate reports in `test_reports/`:

- `performance_report.txt` - Summary of performance metrics
- `unit_tests.xml` - JUnit XML for CI integration
- `coverage.xml` - Coverage data for external tools

## 🎯 Best Practices

### 1. Test Organization

- **Group related tests** in the same class
- **Use descriptive names** that explain what's being tested
- **Follow the AAA pattern**: Arrange, Act, Assert

### 2. Mocking Strategy

- **Mock external dependencies** in unit tests
- **Use real APIs sparingly** in integration tests
- **Provide realistic mock data** using our MockDataGenerator

### 3. Assertion Guidelines

- **Use specific assertions** rather than generic ones
- **Include helpful error messages** in assertions
- **Test both success and failure cases**

### 4. Performance Considerations

- **Set realistic benchmarks** based on actual usage
- **Test under different load conditions**
- **Monitor for performance regressions** in CI

### 5. Maintenance

- **Keep tests simple and focused**
- **Update tests when APIs change**
- **Remove obsolete tests** when features are deprecated
- **Review test coverage** regularly

## 🚨 Troubleshooting

### Common Issues

#### "No module named 'websockets'"

```bash
pip install websockets
# or
pip install -e ".[realtime]"
```

#### "Integration tests disabled"

```bash
export RUN_INTEGRATION_TESTS=true
export KIWOOM_APPKEY="your_key"
export KIWOOM_SECRETKEY="your_secret"
```

#### "Performance tests too slow"

```bash
# Reduce test duration
export PERFORMANCE_TEST_DURATION=30
```

#### Coverage below threshold

```bash
# Run with coverage to see what's missing
pytest tests/ --cov=pyheroapi --cov-report=term-missing
```

### Getting Help

- Check test output for specific error messages
- Review the test documentation in individual test files
- Use `pytest --collect-only` to see available tests
- Run tests with `-v` for verbose output
- Check the CI logs for examples of successful runs

## 📈 Metrics and KPIs

Our testing framework tracks several key metrics:

- **Test Coverage**: Target 80%+ line coverage
- **Test Reliability**: Target 99%+ success rate
- **Performance**: API responses < 1 second average
- **Security**: Zero high-severity vulnerabilities
- **Code Quality**: Zero linting errors

## 🔄 Continuous Improvement

We continuously improve our testing framework by:

- Adding new test scenarios based on user feedback
- Updating performance benchmarks as the API evolves
- Incorporating new testing tools and techniques
- Monitoring test execution times and optimizing slow tests
- Reviewing and updating test data to match real-world usage

---

**Happy Testing! 🎉**

For questions or suggestions about the testing framework, please open an issue or contribute to the discussion in our repository.
