# Quick Start Guide

## 1. Setup (One-time)

```bash
# Install dependencies
pip install -r requirements.txt

# Create proprietary code directory (already done)
mkdir proprietary_code

# Add YOUR proprietary code
cp /path/to/your/secret/*.py ./proprietary_code/
```

## 2. Test Detection

```bash
# Run system test
python test_detection_working.py

# Or test specific code
python check_code.py "def my_function(): pass"

# Or run complete demo
python demo_complete_system.py
```

## 3. Start Protection

```bash
# Start MITM proxy
python security/start_proxy.py

# You should see:
# ✅ Proprietary code directory found
# Proxy server listening at http://0.0.0.0:8080
```

## 4. Configure Browser

### Option A: System Proxy (Automatic)
The `start_proxy.py` script automatically configures system proxy.
Just start the proxy and you're done!

### Option B: Manual Configuration
1. Open browser settings
2. Search for "proxy"
3. Set manual proxy:
   - HTTP Proxy: `localhost`
   - Port: `8080`
   - Use for all protocols: Yes

## 5. Install Certificate (for HTTPS)

1. With proxy running, visit: http://mitm.it
2. Click your OS (Windows/Mac/Linux)
3. Download and install certificate
4. Restart browser

## 6. Test It!

1. Go to ChatGPT (https://chat.openai.com)
2. Try to paste your proprietary code
3. Watch the proxy console - you should see:
   ```
   🚨 PROPRIETARY CODE DETECTED!
   ```
4. The request will be blocked with 403 Forbidden

## Common Commands

```bash
# Test detection
python test_detection_working.py

# Check specific code
python check_code.py "your code here"

# Check file
python check_code.py --file mycode.py

# Start proxy
python security/start_proxy.py

# Stop proxy
# Press Ctrl+C
```

## Troubleshooting

### "No matches found" when testing proprietary code
- Check files exist: `ls proprietary_code/`
- Try lower threshold: Edit `security/sigmashield_detector.py`, set `MIN_SIMILARITY_SCORE = 50`

### Proxy not intercepting
- Check proxy is running (should see "Proxy server listening")
- Check browser proxy settings (localhost:8080)
- For HTTPS: Install certificate from http://mitm.it

### Too many false positives
- Increase threshold: Edit `security/sigmashield_detector.py`, set `MIN_SIMILARITY_SCORE = 70`

## Files You Need to Know

- `security/sigmashield_detector.py` - Detection engine
- `security/mitm_proxy.py` - MITM proxy
- `proprietary_code/` - Your proprietary code
- `check_code.py` - CLI tool

## What Gets Blocked?

The system monitors and blocks proprietary code on:
- ChatGPT (chat.openai.com, api.openai.com)
- Twitter/X (twitter.com, x.com)
- StackOverflow (stackoverflow.com)
- Any LLM API (Anthropic, Cohere, etc.)

## How It Works

```
User pastes code → MITM intercepts → Fuzzy search → Block if match
```

Detection uses:
- RapidFuzz fuzzy matching
- Sliding window approach
- 60% similarity threshold (configurable)

## Next Steps

1. Add your proprietary code to `./proprietary_code/`
2. Run `python test_detection_working.py`
3. Start proxy: `python security/start_proxy.py`
4. Configure browser to use localhost:8080
5. Install certificate from http://mitm.it
6. Try pasting code into ChatGPT - it should be blocked!

## Support

- Full guide: `WORKING_DETECTION_GUIDE.md`
- Complete docs: `IMPLEMENTATION_COMPLETE.md`
- Demo: `python demo_complete_system.py`
