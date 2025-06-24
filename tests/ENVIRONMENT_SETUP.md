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

## Access Token Generation

The PyHero API now automatically generates access tokens using your app key and secret key:

1. **If you have KIWOOM_ACCESS_TOKEN set**: Uses the provided token
2. **If you don't have KIWOOM_ACCESS_TOKEN set**: Generates token from KIWOOM_APPKEY and KIWOOM_SECRETKEY

### Example Output:
```
🔍 Checking environment variables...
  ✅ KIWOOM_APPKEY: **********...1234
  ✅ KIWOOM_SECRETKEY: **********...5678
  ⚠️  KIWOOM_ACCESS_TOKEN: Not set (will generate from app key/secret)

🔑 Getting access token from app key and secret key...
✅ Access token obtained: **********...9012

🔧 Creating Kiwoom realtime client...
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
"
```

### Full Test:
```bash
# Install dependencies if needed
pip install websockets pytest pytest-asyncio

# Run the real data reception test
python tests/test_real_data_reception.py
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
source ~/.bashrc
```

### Or create a .env file:
```bash
# Create .env file in project root
cat > .env << EOF
KIWOOM_APPKEY=your_app_key_here
KIWOOM_SECRETKEY=your_secret_key_here
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