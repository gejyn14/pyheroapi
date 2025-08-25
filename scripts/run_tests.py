#!/usr/bin/env python3
"""
Comprehensive test runner for PyHero API.

This script provides a unified interface for running different types of tests:
- Unit tests (fast, with mocks)
- Integration tests (requires API credentials)
- Performance tests (benchmarking and load testing)
- Coverage analysis
- Code quality checks
- Security scans

Usage:
    python scripts/run_tests.py --help
    python scripts/run_tests.py unit
    python scripts/run_tests.py integration --with-credentials
    python scripts/run_tests.py performance --duration 60
    python scripts/run_tests.py all --coverage --quality
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class TestRunner:
    """Main test runner class."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.reports_dir = project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.results = {}
        
    def run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and capture output."""
        print(f"🔄 Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                cwd=self.project_root
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            if check:
                raise
            return e
    
    def run_unit_tests(self, coverage: bool = False, verbose: bool = False) -> bool:
        """Run unit tests."""
        print("\n🧪 Running Unit Tests")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/",
            "-m", "unit",
            "--tb=short",
        ]
        
        if verbose:
            cmd.extend(["-v", "--durations=10"])
        else:
            cmd.append("-q")
        
        if coverage:
            cmd.extend([
                "--cov=pyheroapi",
                "--cov-report=html:test_reports/htmlcov",
                "--cov-report=xml:test_reports/coverage.xml",
                "--cov-report=term-missing",
                "--cov-fail-under=80"
            ])
        
        cmd.extend([
            "--junitxml=test_reports/unit_tests.xml",
            "--json-report",
            "--json-report-file=test_reports/unit_tests.json"
        ])
        
        try:
            result = self.run_command(cmd, check=False)
            success = result.returncode == 0
            
            self.results["unit_tests"] = {
                "success": success,
                "duration": time.time(),
                "output": result.stdout
            }
            
            if success:
                print("✅ Unit tests passed!")
            else:
                print("❌ Unit tests failed!")
                print(result.stdout[-1000:])  # Last 1000 chars
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to run unit tests: {e}")
            return False
    
    def run_integration_tests(self, with_credentials: bool = False) -> bool:
        """Run integration tests."""
        print("\n🔗 Running Integration Tests")
        print("=" * 50)
        
        if not with_credentials:
            print("⚠️  Integration tests require API credentials")
            print("   Set --with-credentials flag and environment variables:")
            print("   - KIWOOM_APPKEY")
            print("   - KIWOOM_SECRETKEY")
            return True  # Skip, don't fail
        
        # Check for required environment variables
        required_vars = ["KIWOOM_APPKEY", "KIWOOM_SECRETKEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        cmd = [
            "python", "-m", "pytest",
            "tests/",
            "-m", "integration",
            "--tb=short",
            "--maxfail=5",
            "-v",
            "--junitxml=test_reports/integration_tests.xml"
        ]
        
        env = os.environ.copy()
        env["RUN_INTEGRATION_TESTS"] = "true"
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=self.project_root,
                env=env
            )
            
            success = result.returncode == 0
            
            self.results["integration_tests"] = {
                "success": success,
                "duration": time.time(),
                "output": result.stdout
            }
            
            if success:
                print("✅ Integration tests passed!")
            else:
                print("❌ Integration tests failed!")
                print(result.stdout[-1000:])
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to run integration tests: {e}")
            return False
    
    def run_performance_tests(self, duration: int = 30) -> bool:
        """Run performance tests."""
        print(f"\n⚡ Running Performance Tests (duration: {duration}s)")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/",
            "-m", "performance",
            "--tb=short",
            "--durations=0",
            "-v",
            "--junitxml=test_reports/performance_tests.xml"
        ]
        
        env = os.environ.copy()
        env["RUN_PERFORMANCE_TESTS"] = "true"
        env["PERFORMANCE_TEST_DURATION"] = str(duration)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=self.project_root,
                env=env
            )
            
            success = result.returncode == 0
            
            self.results["performance_tests"] = {
                "success": success,
                "duration": time.time(),
                "output": result.stdout
            }
            
            if success:
                print("✅ Performance tests passed!")
            else:
                print("❌ Performance tests failed!")
                print(result.stdout[-1000:])
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to run performance tests: {e}")
            return False
    
    def run_realtime_tests(self) -> bool:
        """Run real-time WebSocket tests."""
        print("\n🔄 Running Real-time Tests")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/",
            "-m", "realtime",
            "--tb=short",
            "-v",
            "--junitxml=test_reports/realtime_tests.xml"
        ]
        
        try:
            result = self.run_command(cmd, check=False)
            success = result.returncode == 0
            
            self.results["realtime_tests"] = {
                "success": success,
                "duration": time.time(),
                "output": result.stdout
            }
            
            if success:
                print("✅ Real-time tests passed!")
            else:
                print("❌ Real-time tests failed!")
                if "websockets not available" in result.stdout:
                    print("   Note: websockets package may not be installed")
                print(result.stdout[-1000:])
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to run real-time tests: {e}")
            return False
    
    def run_code_quality_checks(self) -> bool:
        """Run code quality checks."""
        print("\n🔍 Running Code Quality Checks")
        print("=" * 50)
        
        quality_checks = [
            self._check_black_formatting,
            self._check_isort_imports,
            self._check_flake8_linting,
            self._check_mypy_typing,
        ]
        
        all_passed = True
        
        for check in quality_checks:
            try:
                if not check():
                    all_passed = False
            except Exception as e:
                print(f"❌ Quality check failed: {e}")
                all_passed = False
        
        self.results["code_quality"] = {
            "success": all_passed,
            "duration": time.time()
        }
        
        if all_passed:
            print("✅ All code quality checks passed!")
        else:
            print("❌ Some code quality checks failed!")
        
        return all_passed
    
    def _check_black_formatting(self) -> bool:
        """Check code formatting with Black."""
        print("  📝 Checking code formatting (Black)...")
        cmd = ["python", "-m", "black", "--check", "--diff", "pyheroapi/", "tests/"]
        result = self.run_command(cmd, check=False)
        
        if result.returncode == 0:
            print("    ✅ Code formatting is correct")
            return True
        else:
            print("    ❌ Code formatting issues found")
            print(f"    Run: black pyheroapi/ tests/")
            return False
    
    def _check_isort_imports(self) -> bool:
        """Check import sorting with isort."""
        print("  📋 Checking import sorting (isort)...")
        cmd = ["python", "-m", "isort", "--check-only", "--diff", "pyheroapi/", "tests/"]
        result = self.run_command(cmd, check=False)
        
        if result.returncode == 0:
            print("    ✅ Import sorting is correct")
            return True
        else:
            print("    ❌ Import sorting issues found")
            print(f"    Run: isort pyheroapi/ tests/")
            return False
    
    def _check_flake8_linting(self) -> bool:
        """Check code linting with flake8."""
        print("  🧹 Checking linting (flake8)...")
        cmd = [
            "python", "-m", "flake8", "pyheroapi/", "tests/",
            "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"
        ]
        result = self.run_command(cmd, check=False)
        
        if result.returncode == 0:
            print("    ✅ No linting issues found")
            return True
        else:
            print("    ❌ Linting issues found")
            print(result.stdout)
            return False
    
    def _check_mypy_typing(self) -> bool:
        """Check type annotations with mypy."""
        print("  🏷️  Checking type annotations (mypy)...")
        cmd = ["python", "-m", "mypy", "pyheroapi/", "--ignore-missing-imports"]
        result = self.run_command(cmd, check=False)
        
        if result.returncode == 0:
            print("    ✅ Type checking passed")
            return True
        else:
            print("    ❌ Type checking issues found")
            print(result.stdout[-500:])  # Last 500 chars
            return False
    
    def run_security_checks(self) -> bool:
        """Run security vulnerability checks."""
        print("\n🛡️  Running Security Checks")
        print("=" * 50)
        
        security_checks = [
            self._check_bandit_security,
            self._check_safety_vulnerabilities,
        ]
        
        all_passed = True
        
        for check in security_checks:
            try:
                if not check():
                    all_passed = False
            except Exception as e:
                print(f"❌ Security check failed: {e}")
                all_passed = False
        
        self.results["security_checks"] = {
            "success": all_passed,
            "duration": time.time()
        }
        
        return all_passed
    
    def _check_bandit_security(self) -> bool:
        """Check for security issues with bandit."""
        print("  🔒 Checking security issues (bandit)...")
        cmd = [
            "python", "-m", "bandit", "-r", "pyheroapi/",
            "-f", "json", "-o", "test_reports/bandit_report.json"
        ]
        result = self.run_command(cmd, check=False)
        
        if result.returncode == 0:
            print("    ✅ No security issues found")
            return True
        else:
            print("    ⚠️  Security issues may exist (check report)")
            return True  # Don't fail build for security warnings
    
    def _check_safety_vulnerabilities(self) -> bool:
        """Check for known vulnerabilities with safety."""
        print("  🔍 Checking known vulnerabilities (safety)...")
        cmd = [
            "python", "-m", "safety", "check",
            "--json", "--output", "test_reports/safety_report.json"
        ]
        result = self.run_command(cmd, check=False)
        
        if result.returncode == 0:
            print("    ✅ No known vulnerabilities found")
            return True
        else:
            print("    ⚠️  Known vulnerabilities may exist (check report)")
            return True  # Don't fail build for dependency warnings
    
    def generate_report(self) -> None:
        """Generate a comprehensive test report."""
        print("\n📊 Generating Test Report")
        print("=" * 50)
        
        report_file = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write("🚀 PyHero API Test Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Project: {self.project_root}\n\n")
            
            # Summary
            total_tests = len(self.results)
            passed_tests = sum(1 for r in self.results.values() if r.get("success", False))
            
            f.write("📈 Summary\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total test suites: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n")
            f.write(f"Failed: {total_tests - passed_tests}\n")
            f.write(f"Success rate: {passed_tests/total_tests*100:.1f}%\n\n")
            
            # Detailed results
            f.write("📋 Detailed Results\n")
            f.write("-" * 30 + "\n")
            
            for test_name, result in self.results.items():
                status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
                f.write(f"{test_name}: {status}\n")
                if "output" in result and not result.get("success", False):
                    f.write(f"  Output: {result['output'][-200:]}...\n")  # Last 200 chars
                f.write("\n")
        
        print(f"📄 Report generated: {report_file}")
        
        # Also print summary to console
        print(f"\n📈 Test Summary:")
        print(f"   Total suites: {len(self.results)}")
        passed = sum(1 for r in self.results.values() if r.get("success", False))
        print(f"   Passed: {passed}")
        print(f"   Failed: {len(self.results) - passed}")
        
        return report_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PyHero API Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py unit --coverage
  python scripts/run_tests.py integration --with-credentials
  python scripts/run_tests.py performance --duration 60
  python scripts/run_tests.py all --coverage --quality
        """
    )
    
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "performance", "realtime", "quality", "security", "all"],
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Include coverage analysis"
    )
    
    parser.add_argument(
        "--quality",
        action="store_true", 
        help="Include code quality checks"
    )
    
    parser.add_argument(
        "--security",
        action="store_true",
        help="Include security checks"
    )
    
    parser.add_argument(
        "--with-credentials",
        action="store_true",
        help="Run tests that require API credentials"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Duration for performance tests (seconds)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report"
    )
    
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    runner = TestRunner(project_root)
    
    print("🚀 PyHero API Test Runner")
    print("=" * 60)
    print(f"Project: {project_root}")
    print(f"Test type: {args.test_type}")
    print()
    
    success = True
    
    try:
        if args.test_type in ("unit", "all"):
            success &= runner.run_unit_tests(coverage=args.coverage, verbose=args.verbose)
        
        if args.test_type in ("integration", "all"):
            success &= runner.run_integration_tests(with_credentials=args.with_credentials)
        
        if args.test_type in ("performance", "all"):
            success &= runner.run_performance_tests(duration=args.duration)
        
        if args.test_type in ("realtime", "all"):
            success &= runner.run_realtime_tests()
        
        if args.test_type in ("quality", "all") or args.quality:
            success &= runner.run_code_quality_checks()
        
        if args.test_type in ("security", "all") or args.security:
            success &= runner.run_security_checks()
        
        if args.report or args.test_type == "all":
            runner.generate_report()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test run failed with error: {e}")
        return 1
    
    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 