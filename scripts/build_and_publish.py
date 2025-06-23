#!/usr/bin/env python3
"""
Build and publish script for pyheroapi package.

This script helps with:
1. Building the package
2. Running tests
3. Publishing to PyPI (test and production)
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"🔄 Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {command}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    if result.stdout:
        print(result.stdout)
    
    return result


def check_requirements():
    """Check if required tools are installed."""
    print("📋 Checking requirements...")
    
    required_tools = ["python", "pip"]
    for tool in required_tools:
        result = run_command(f"which {tool}", check=False)
        if result.returncode != 0:
            print(f"❌ {tool} not found. Please install it first.")
            sys.exit(1)
    
    print("✅ All requirements satisfied")


def install_build_tools():
    """Install build tools."""
    print("🔧 Installing build tools...")
    run_command("pip install --upgrade pip")
    run_command("pip install build twine")


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    
    # Install dev dependencies
    run_command("pip install -e .[dev]")
    
    # Run tests
    run_command("pytest tests/ -v --cov=pyheroapi")
    
    print("✅ All tests passed")


def lint_code():
    """Run code quality checks."""
    print("🔍 Running code quality checks...")
    
    # Format with black
    run_command("black pyheroapi/ tests/ examples/")
    
    # Sort imports
    run_command("isort pyheroapi/ tests/ examples/")
    
    # Type checking
    run_command("mypy pyheroapi/", check=False)  # Don't fail on mypy errors
    
    print("✅ Code quality checks completed")


def build_package():
    """Build the package."""
    print("📦 Building package...")
    
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/", check=False)
    
    # Build package
    run_command("python -m build")
    
    # Check package
    run_command("twine check dist/*")
    
    print("✅ Package built successfully")


def publish_to_test_pypi():
    """Publish to Test PyPI."""
    print("🚀 Publishing to Test PyPI...")
    
    print("Please make sure you have configured your Test PyPI credentials:")
    print("pip install keyring")
    print("python -m keyring set https://test.pypi.org/legacy/ __token__")
    
    input("Press Enter to continue...")
    
    run_command("twine upload --repository testpypi dist/*")
    
    print("✅ Published to Test PyPI")
    print("You can install with: pip install --index-url https://test.pypi.org/simple/ pyheroapi")


def publish_to_pypi():
    """Publish to production PyPI."""
    print("🚀 Publishing to production PyPI...")
    
    print("⚠️  WARNING: This will publish to production PyPI!")
    print("Make sure you have:")
    print("1. Tested the package thoroughly")
    print("2. Updated the version number")
    print("3. Updated the changelog")
    
    confirm = input("Are you sure you want to publish to production PyPI? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Cancelled")
        return
    
    print("Please make sure you have configured your PyPI credentials:")
    print("python -m keyring set https://upload.pypi.org/legacy/ __token__")
    
    input("Press Enter to continue...")
    
    run_command("twine upload dist/*")
    
    print("✅ Published to PyPI")
    print("You can install with: pip install pyheroapi")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python build_and_publish.py <command>")
        print("\nAvailable commands:")
        print("  check      - Check requirements")
        print("  install    - Install build tools") 
        print("  test       - Run tests")
        print("  lint       - Run code quality checks")
        print("  build      - Build package")
        print("  test-pypi  - Publish to Test PyPI")
        print("  pypi       - Publish to production PyPI")
        print("  all        - Run all steps (except publish)")
        return
    
    command = sys.argv[1]
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    if command == "check":
        check_requirements()
    elif command == "install":
        install_build_tools()
    elif command == "test":
        run_tests()
    elif command == "lint":
        lint_code()
    elif command == "build":
        build_package()
    elif command == "test-pypi":
        publish_to_test_pypi()
    elif command == "pypi":
        publish_to_pypi()
    elif command == "all":
        check_requirements()
        install_build_tools()
        lint_code()
        run_tests()
        build_package()
        print("\n🎉 All steps completed successfully!")
        print("Ready to publish with: python scripts/build_and_publish.py test-pypi")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main() 