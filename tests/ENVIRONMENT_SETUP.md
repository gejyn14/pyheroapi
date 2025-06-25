# Environment Setup for PyHero API Testing

## Correct Environment Variables

### Required Variables ✅
```bash
export KIWOOM_APPKEY="your_app_key_here"
export KIWOOM_SECRETKEY="your_secret_key_here"
```

### Optional Variables ⚠️
```bash
# If not set, will be automatically generated from APPKEY and SECRETKEY
export KIWOOM_ACCESS_TOKEN="your_access_token_here"
```

### Sandbox Environment Variables (New!) 🆕
```bash
# For sandbox mode testing - these will be used automatically when is_production=False
# SANDBOX MODE: set is_production=False explicitly
export KIWOOM_MOCK_APPKEY="your_mock_app_key_here"
export KIWOOM_MOCK_SECRETKEY="your_mock_secret_key_here"
```

## How to Set Up

### Option 1: Manual Token Generation (Recommended)
```bash
# Set your app key and secret key
export KIWOOM_APPKEY="KOA12345678901234567"
export KIWOOM_SECRETKEY="your_secret_key_value"

# Run the test - it will automatically get the access token
python tests/test_real_data_reception.py
```

### Option 2: Pre-generated Token
```bash
# Set all three variables
export KIWOOM_APPKEY="KOA12345678901234567"
export KIWOOM_SECRETKEY="your_secret_key_value"
export KIWOOM_ACCESS_TOKEN="your_access_token_value"

# Run the test
python tests/test_real_data_reception.py
```

### Option 3: Sandbox Environment Variables (New!)
```bash
# Set sandbox-specific credentials
export KIWOOM_MOCK_APPKEY="your_mock_app_key_here"
export KIWOOM_MOCK_SECRETKEY="your_mock_secret_key_here"

# The client will automatically use these when is_production=False
# SANDBOX MODE: set is_production=False explicitly
python examples/01_authentication.py
```

## What Changed from Previous Versions

### ❌ Old (Incorrect) Variable Names:
```bash
KIWOOM_APP_KEY      # Wrong
KIWOOM_SECRET_KEY   # Wrong
```

### ✅ New (Correct) Variable Names:
```bash
KIWOOM_APPKEY       # Correct
KIWOOM_SECRETKEY    # Correct
```

### 🆕 New Sandbox Variables:
```bash
KIWOOM_MOCK_APPKEY    # For sandbox mode
KIWOOM_MOCK_SECRETKEY # For sandbox mode
```

## Access Token Generation

The PyHero API now automatically generates access tokens using your app key and secret key:

1. **If you have KIWOOM_ACCESS_TOKEN set**: Uses the provided token
2. **If you don't have KIWOOM_ACCESS_TOKEN set**: Generates token from KIWOOM_APPKEY and KIWOOM_SECRETKEY
3. **For sandbox mode**: If KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY are set, these will be used instead

### Example Output:
```
🔍 Checking environment variables...
  ✅ KIWOOM_APPKEY: **********...1234
  ✅ KIWOOM_SECRETKEY: **********...5678
  ⚠️  KIWOOM_ACCESS_TOKEN: Not set (will generate from app key/secret)
  ✅ KIWOOM_MOCK_APPKEY: **********...9012 (sandbox mode)
  ✅ KIWOOM_MOCK_SECRETKEY: **********...3456 (sandbox mode)

🔑 Getting access token from app key and secret key...
✅ Access token obtained: **********...9012

🔧 Creating Kiwoom realtime client...
```

## Sandbox Mode Behavior

When using sandbox mode (`is_production=False`), the client will:
SANDBOX MODE: set is_production=False explicitly
1. **Check for KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY first**
2. **If found**: Use these credentials for sandbox authentication
3. **If not found**: Fall back to KIWOOM_APPKEY and KIWOOM_SECRETKEY

### Example Usage:
```python
# This will use KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY if set
client = KiwoomClient.create_with_credentials(
    appkey="dummy",  # Ignored if KIWOOM_MOCK_APPKEY is set
    secretkey="dummy",  # Ignored if KIWOOM_MOCK_SECRETKEY is set
    is_production=False  # SANDBOX MODE: set is_production=False explicitly
)
```

## Testing Your Setup

### Quick Test:
```bash
# Test environment variable detection
python -c "
import os
print('KIWOOM_APPKEY:', '✅' if os.getenv('KIWOOM_APPKEY') else '❌')
print('KIWOOM_SECRETKEY:', '✅' if os.getenv('KIWOOM_SECRETKEY') else '❌')
print('KIWOOM_ACCESS_TOKEN:', '✅' if os.getenv('KIWOOM_ACCESS_TOKEN') else '⚠️ (will generate)')
print('KIWOOM_MOCK_APPKEY:', '✅' if os.getenv('KIWOOM_MOCK_APPKEY') else '⚠️ (not set)')
print('KIWOOM_MOCK_SECRETKEY:', '✅' if os.getenv('KIWOOM_MOCK_SECRETKEY') else '⚠️ (not set)')
"
```

### Full Test:
```bash
# Install dependencies if needed
pip install websockets pytest pytest-asyncio

# Run the real data reception test
python tests/test_real_data_reception.py
```

### Sandbox Test:
```bash
# Test sandbox environment variables
python examples/01_authentication.py
```

## Common Issues

### Missing Environment Variables
```
❌ Missing required environment variables: ['KIWOOM_APPKEY']
```
**Solution**: Set the missing variables using `export`

### Token Generation Failed
```
❌ Error getting access token: Authentication failed
```
**Solutions**:
- Check that KIWOOM_APPKEY and KIWOOM_SECRETKEY are correct
- For sandbox mode, check KIWOOM_MOCK_APPKEY and KIWOOM_MOCK_SECRETKEY
- Verify your Kiwoom API account is active
- Check network connectivity

### Import Error
```
❌ Failed to import PyHero API: websockets library is required
```
**Solution**: Install websockets: `pip install websockets`

## Persistent Environment Variables

To make environment variables persistent across terminal sessions:

### Add to ~/.bashrc:
```bash
echo 'export KIWOOM_APPKEY="your_app_key_here"' >> ~/.bashrc
echo 'export KIWOOM_SECRETKEY="your_secret_key_here"' >> ~/.bashrc
echo 'export KIWOOM_MOCK_APPKEY="your_mock_app_key_here"' >> ~/.bashrc
echo 'export KIWOOM_MOCK_SECRETKEY="your_mock_secret_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Or create a .env file:
```bash
# Create .env file in project root
cat > .env << EOF
KIWOOM_APPKEY=your_app_key_here
KIWOOM_SECRETKEY=your_secret_key_here
KIWOOM_MOCK_APPKEY=your_mock_app_key_here
KIWOOM_MOCK_SECRETKEY=your_mock_secret_key_here
EOF

# Load it before testing
set -a; source .env; set +a
python tests/test_real_data_reception.py
```

## Security Note

Never commit your actual API keys to version control. Always use:
- Environment variables
- .env files (add to .gitignore)
- Secure secret management systems 