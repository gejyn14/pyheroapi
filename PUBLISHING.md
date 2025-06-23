# Publishing Guide for PyHero API Python Client

This guide will help you publish the `pyheroapi` package to PyPI.

## Prerequisites

1. **Python 3.8+** installed
2. **PyPI account** at https://pypi.org/account/register/
3. **Test PyPI account** at https://test.pypi.org/account/register/
4. **API tokens** from both PyPI and Test PyPI

## Setup Instructions

### 1. Install Required Tools

```bash
pip install --upgrade pip
pip install build twine keyring
```

### 2. Configure API Tokens

#### For Test PyPI:
```bash
python -m keyring set https://test.pypi.org/legacy/ __token__
# Enter your Test PyPI API token when prompted
```

#### For Production PyPI:
```bash
python -m keyring set https://upload.pypi.org/legacy/ __token__
# Enter your PyPI API token when prompted
```

### 3. Install Development Dependencies

```bash
pip install -e .[dev]
```

## Publishing Process

### Option 1: Using the Build Script (Recommended)

We've provided a convenient script to handle the entire process:

```bash
# Run all checks, tests, and build the package
python scripts/build_and_publish.py all

# Publish to Test PyPI first
python scripts/build_and_publish.py test-pypi

# After testing, publish to production PyPI
python scripts/build_and_publish.py pypi
```

### Option 2: Manual Steps

#### Step 1: Code Quality Checks

```bash
# Format code
black pyheroapi/ tests/ examples/
isort pyheroapi/ tests/ examples/

# Type checking
mypy pyheroapi/
```

#### Step 2: Run Tests

```bash
pytest tests/ -v --cov=pyheroapi
```

#### Step 3: Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Check the package
twine check dist/*
```

#### Step 4: Publish to Test PyPI

```bash
twine upload --repository testpypi dist/*
```

#### Step 5: Test Installation from Test PyPI

```bash
# Create a new virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ pyheroapi

# Test the installation
python -c "from pyheroapi import KiwoomClient; print('✅ Import successful')"
```

#### Step 6: Publish to Production PyPI

```bash
twine upload dist/*
```

## Version Management

Before publishing a new version:

1. Update the version in `pyproject.toml`
2. Update the changelog in `README.md`
3. Create a git tag for the release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Release Checklist

- [ ] All tests pass
- [ ] Code is formatted and linted
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Documentation is up to date
- [ ] Examples work correctly
- [ ] Package builds without errors
- [ ] Published to Test PyPI and tested
- [ ] Git tag created for release

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Make sure your API tokens are correctly configured
   - Check that you're using the right repository URL

2. **Package Already Exists**
   - PyPI doesn't allow overwriting existing versions
   - Increment the version number in `pyproject.toml`

3. **Import Errors After Installation**
   - Check that all dependencies are correctly specified
   - Verify the package structure is correct

4. **Build Failures**
   - Ensure all required files are included in `MANIFEST.in`
   - Check that `pyproject.toml` is correctly configured

### Getting Help

- Check the [PyPI documentation](https://packaging.python.org/)
- Visit the [Python Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- Ask questions on [Stack Overflow](https://stackoverflow.com/questions/tagged/python-packaging)

## Security Notes

- Never commit API tokens to version control
- Use environment variables or keyring for sensitive credentials
- Consider using GitHub Actions for automated publishing
- Regularly rotate your PyPI API tokens

## Automated Publishing (Future Enhancement)

Consider setting up GitHub Actions for automated testing and publishing:

1. Create `.github/workflows/publish.yml`
2. Set up PyPI API tokens as GitHub secrets
3. Automatically publish on git tags

This will ensure consistent releases and reduce manual errors. 