"""
Performance testing framework for PyHero API.

This module provides:
- Response time benchmarking
- Throughput testing
- Memory usage monitoring
- Stress testing scenarios
- Performance regression detection
"""

import asyncio
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Callable, Any
from unittest.mock import patch

import pytest
import responses

from pyheroapi import KiwoomClient, KiwoomAPI
from .base import BaseTestCase
from .conftest import TestConfig, MockDataGenerator

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PerformanceMetrics:
    """Container for performance metrics."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.error_count: int = 0
        self.success_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
    
    @property
    def total_requests(self) -> int:
        return self.success_count + self.error_count
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.success_count / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[index]
    
    @property
    def throughput(self) -> float:
        duration = self.end_time - self.start_time
        return self.total_requests / duration if duration > 0 else 0.0
    
    def add_response_time(self, response_time: float):
        self.response_times.append(response_time)
    
    def add_success(self):
        self.success_count += 1
    
    def add_error(self):
        self.error_count += 1
    
    def start_timing(self):
        self.start_time = time.time()
    
    def end_timing(self):
        self.end_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_rate,
            "avg_response_time": self.avg_response_time,
            "p95_response_time": self.p95_response_time,
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "throughput": self.throughput,
            "duration": self.end_time - self.start_time,
        }


class PerformanceTester:
    """Performance testing utility class."""
    
    def __init__(self, client: KiwoomClient):
        self.client = client
        self.metrics = PerformanceMetrics()
    
    def benchmark_single_request(self, operation: Callable, *args, **kwargs) -> float:
        """Benchmark a single API request."""
        start_time = time.time()
        try:
            operation(*args, **kwargs)
            self.metrics.add_success()
        except Exception:
            self.metrics.add_error()
        
        response_time = time.time() - start_time
        self.metrics.add_response_time(response_time)
        return response_time
    
    def load_test(self, operation: Callable, duration: float = 30.0, 
                  concurrent_users: int = 10, *args, **kwargs) -> PerformanceMetrics:
        """Perform load testing with multiple concurrent users."""
        self.metrics = PerformanceMetrics()
        self.metrics.start_timing()
        
        end_time = time.time() + duration
        
        def user_simulation():
            while time.time() < end_time:
                self.benchmark_single_request(operation, *args, **kwargs)
                time.sleep(0.1)  # Small delay between requests
        
        # Start concurrent user threads
        threads = []
        for _ in range(concurrent_users):
            thread = threading.Thread(target=user_simulation)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        self.metrics.end_timing()
        return self.metrics
    
    def stress_test(self, operation: Callable, max_requests: int = 1000,
                   ramp_up_time: float = 60.0, *args, **kwargs) -> PerformanceMetrics:
        """Perform stress testing with gradually increasing load."""
        self.metrics = PerformanceMetrics()
        self.metrics.start_timing()
        
        requests_per_second = max_requests / ramp_up_time
        request_interval = 1.0 / requests_per_second
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            
            for i in range(max_requests):
                future = executor.submit(self.benchmark_single_request, operation, *args, **kwargs)
                futures.append(future)
                
                # Gradual ramp-up
                time.sleep(request_interval * (1 - i / max_requests))
            
            # Wait for all requests to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass
        
        self.metrics.end_timing()
        return self.metrics


@pytest.mark.performance
class TestAPIPerformance(BaseTestCase):
    """API performance tests."""
    
    def setup_method(self):
        super().setup_method()
        self.client = KiwoomClient(access_token="test_token", is_production=False)
        self.tester = PerformanceTester(self.client)
    
    @pytest.mark.parametrize("iterations", [10, 50, 100])
    def test_quote_request_performance(self, mock_responses, mock_data_generator, iterations):
        """Test quote request performance across different load levels."""
        # Mock response
        mock_responses.add(
            responses.POST,
            f"{TestConfig.SANDBOX_URL}/api/dostk/mrkcond",
            json=mock_data_generator.create_stock_quote_response(),
            status=200
        )
        
        # Benchmark multiple requests
        response_times = []
        for _ in range(iterations):
            response_time = self.tester.benchmark_single_request(
                self.client.get_quote, "005930"
            )
            response_times.append(response_time)
        
        # Performance assertions
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        assert avg_time <= 0.5, f"Average response time too slow: {avg_time:.3f}s"
        assert max_time <= 1.0, f"Maximum response time too slow: {max_time:.3f}s"
        
        print(f"✅ Performance test passed for {iterations} iterations:")
        print(f"   Average: {avg_time:.3f}s")
        print(f"   Maximum: {max_time:.3f}s")
        print(f"   P95: {statistics.quantiles(response_times, n=20)[18]:.3f}s")
    
    def test_concurrent_request_performance(self, mock_responses, mock_data_generator):
        """Test performance under concurrent load."""
        # Mock response
        mock_responses.add(
            responses.POST,
            f"{TestConfig.SANDBOX_URL}/api/dostk/mrkcond",
            json=mock_data_generator.create_stock_quote_response(),
            status=200
        )
        
        # Load test with 5 concurrent users for 10 seconds
        metrics = self.tester.load_test(
            self.client.get_quote,
            duration=10.0,
            concurrent_users=5,
            symbol="005930"
        )
        
        # Performance assertions
        assert metrics.success_rate >= 95.0, f"Success rate too low: {metrics.success_rate:.2f}%"
        assert metrics.avg_response_time <= 1.0, f"Average response time too slow: {metrics.avg_response_time:.3f}s"
        assert metrics.throughput >= 10.0, f"Throughput too low: {metrics.throughput:.2f} req/s"
        
        print(f"✅ Concurrent performance test passed:")
        print(f"   Success rate: {metrics.success_rate:.2f}%")
        print(f"   Average response: {metrics.avg_response_time:.3f}s")
        print(f"   Throughput: {metrics.throughput:.2f} req/s")
        print(f"   Total requests: {metrics.total_requests}")
    
    @pytest.mark.slow
    def test_stress_test_limits(self, mock_responses, mock_data_generator):
        """Test system behavior under stress conditions."""
        # Mock response
        mock_responses.add(
            responses.POST,
            f"{TestConfig.SANDBOX_URL}/api/dostk/mrkcond",
            json=mock_data_generator.create_stock_quote_response(),
            status=200
        )
        
        # Stress test with 500 requests over 30 seconds
        metrics = self.tester.stress_test(
            self.client.get_quote,
            max_requests=500,
            ramp_up_time=30.0,
            symbol="005930"
        )
        
        # Stress test assertions (more lenient)
        assert metrics.success_rate >= 90.0, f"Success rate under stress: {metrics.success_rate:.2f}%"
        assert metrics.avg_response_time <= 2.0, f"Response time under stress: {metrics.avg_response_time:.3f}s"
        
        print(f"✅ Stress test passed:")
        print(f"   Processed {metrics.total_requests} requests")
        print(f"   Success rate: {metrics.success_rate:.2f}%")
        print(f"   Average response: {metrics.avg_response_time:.3f}s")
        print(f"   P95 response: {metrics.p95_response_time:.3f}s")
    
    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
    def test_memory_usage_monitoring(self, mock_responses, mock_data_generator):
        """Test memory usage during API operations."""
        import psutil
        process = psutil.Process()
        
        # Mock response
        mock_responses.add(
            responses.POST,
            f"{TestConfig.SANDBOX_URL}/api/dostk/mrkcond",
            json=mock_data_generator.create_stock_quote_response(),
            status=200
        )
        
        # Measure memory before
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple requests
        for _ in range(100):
            self.client.get_quote("005930")
        
        # Measure memory after
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage assertions
        assert memory_increase <= 50.0, f"Memory usage increased too much: {memory_increase:.2f}MB"
        
        print(f"✅ Memory usage test passed:")
        print(f"   Initial memory: {initial_memory:.2f}MB")
        print(f"   Final memory: {final_memory:.2f}MB")
        print(f"   Memory increase: {memory_increase:.2f}MB")


@pytest.mark.performance
class TestEasyAPIPerformance(BaseTestCase):
    """Performance tests for the easy API wrapper."""
    
    def test_stock_wrapper_performance(self, mock_responses, mock_data_generator):
        """Test performance of Stock wrapper operations."""
        # Setup
        client = KiwoomClient(access_token="test_token", is_production=False)
        api = KiwoomAPI(client)
        stock = api.stock("005930")
        
        # Mock response
        mock_responses.add(
            responses.POST,
            f"{TestConfig.SANDBOX_URL}/api/dostk/mrkcond",
            json=mock_data_generator.create_stock_quote_response(),
            status=200
        )
        
        # Benchmark wrapper operations
        times = []
        for _ in range(20):
            start = time.time()
            quote = stock.quote
            end = time.time()
            times.append(end - start)
        
        avg_time = statistics.mean(times)
        assert avg_time <= 0.1, f"Stock wrapper too slow: {avg_time:.3f}s"
        
        print(f"✅ Stock wrapper performance: {avg_time:.3f}s average")


class PerformanceReporter:
    """Generate performance test reports."""
    
    @staticmethod
    def generate_report(metrics: Dict[str, PerformanceMetrics], output_file: str = "performance_report.txt"):
        """Generate a comprehensive performance report."""
        with open(output_file, 'w') as f:
            f.write("🚀 PyHero API Performance Test Report\n")
            f.write("=" * 50 + "\n\n")
            
            for test_name, metric in metrics.items():
                f.write(f"📊 {test_name}\n")
                f.write("-" * 30 + "\n")
                for key, value in metric.to_dict().items():
                    if isinstance(value, float):
                        f.write(f"{key}: {value:.3f}\n")
                    else:
                        f.write(f"{key}: {value}\n")
                f.write("\n")
        
        print(f"📄 Performance report generated: {output_file}")
    
    @staticmethod
    def performance_regression_check(current_metrics: PerformanceMetrics, 
                                   baseline_metrics: PerformanceMetrics,
                                   tolerance: float = 0.1) -> bool:
        """Check for performance regression compared to baseline."""
        current_avg = current_metrics.avg_response_time
        baseline_avg = baseline_metrics.avg_response_time
        
        if baseline_avg == 0:
            return True  # No baseline to compare
        
        regression_threshold = baseline_avg * (1 + tolerance)
        
        if current_avg > regression_threshold:
            print(f"❌ Performance regression detected!")
            print(f"   Current average: {current_avg:.3f}s")
            print(f"   Baseline average: {baseline_avg:.3f}s")
            print(f"   Threshold: {regression_threshold:.3f}s")
            return False
        
        print(f"✅ No performance regression detected")
        return True


# Utility functions for performance testing
def benchmark_function(func: Callable, iterations: int = 100) -> Dict[str, float]:
    """Simple function benchmarking utility."""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        func()
        end = time.time()
        times.append(end - start)
    
    return {
        "min": min(times),
        "max": max(times),
        "avg": statistics.mean(times),
        "median": statistics.median(times),
        "p95": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times)
    }


def run_performance_suite():
    """Run the complete performance test suite."""
    print("🚀 Starting PyHero API Performance Test Suite")
    print("=" * 60)
    
    # This would integrate with pytest to run all performance tests
    # For now, it's a placeholder for the test orchestration
    
    return {
        "status": "completed",
        "total_tests": 0,
        "passed_tests": 0,
        "performance_score": 0.0
    }


if __name__ == "__main__":
    # Allow running performance tests directly
    results = run_performance_suite()
    print(f"\n📊 Performance Suite Results: {results}") 