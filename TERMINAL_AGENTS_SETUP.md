# Terminal Agents & AI IDEs Setup Guide

This guide shows how to protect proprietary code when using terminal agents (Claude Code, Aider, etc.) and AI IDEs (Cursor, Windsurf, etc.).

## 🎯 Overview

**Problem**: Terminal agents and AI IDEs send code directly to LLM APIs, bypassing browser-based protections.

**Solution**: Use the Bifrost plugin to intercept ALL LLM API calls at the gateway level.

## 🚀 Quick Setup

### Step 1: Install Bifrost Plugin

```bash
# Build and install the plugin
./setup_bifrost_plugin.sh

# Add your proprietary code
cp /path/to/your/code/*.py proprietary_code/
```

### Step 2: Configure Bifrost

Add the plugin to your Bifrost config (`bifrost/config.json`):

```json
{
  "plugins": [
    {
      "name": "proprietary-detection",
      "path": "./proprietary_detection.so",
      "enabled": true,
      "config": {
        "proprietary_code_dir": "./proprietary_code",
        "similarity_threshold": 60,
        "block_on_detection": true
      }
    }
  ]
}
```

### Step 3: Start Bifrost

```bash
cd bifrost
./bifrost start
```

Bifrost will now run on `http://localhost:8000` and intercept all LLM requests.

## 🛠️ Tool-Specific Configuration

### Claude Desktop / Claude Code

**Method 1: Environment Variables**
```bash
export ANTHROPIC_BASE_URL="http://localhost:8000"
export ANTHROPIC_API_KEY="your-api-key"

# Now run Claude
claude-code
```

**Method 2: Config File**

Edit `~/.config/claude/config.json`:
```json
{
  "api_base_url": "http://localhost:8000",
  "api_key": "your-api-key"
}
```

### Cursor IDE

1. Open Cursor Settings
2. Go to "Advanced" → "API Configuration"
3. Set Base URL: `http://localhost:8000`
4. Enter your API key

### Windsurf IDE

1. Open Settings → Extensions → Windsurf
2. Set API Endpoint: `http://localhost:8000`
3. Enter your API key

### Aider (Terminal Agent)

```bash
# Set environment variable
export OPENAI_BASE_URL="http://localhost:8000"
export OPENAI_API_KEY="your-api-key"

# Run aider
aider
```

### Continue.dev (VS Code Extension)

Edit `~/.continue/config.json`:
```json
{
  "models": [
    {
      "title": "Claude via Bifrost",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "apiBase": "http://localhost:8000",
      "apiKey": "your-api-key"
    }
  ]
}
```

### Cline (VS Code Extension)

1. Open Cline settings in VS Code
2. Set API Base URL: `http://localhost:8000`
3. Enter your API key

### Custom Python Scripts

```python
import anthropic

# Configure to use Bifrost
client = anthropic.Anthropic(
    api_key="your-api-key",
    base_url="http://localhost:8000"
)

# All requests now go through Bifrost
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Your code here"}]
)
```

### OpenAI-Compatible Tools

```bash
# Set environment variable
export OPENAI_BASE_URL="http://localhost:8000"
export OPENAI_API_KEY="your-api-key"

# Any tool using OpenAI SDK will now use Bifrost
python your_script.py
```

## 🔍 How It Works

```
┌─────────────────┐
│  Terminal Agent │
│   (Claude Code, │
│   Aider, etc.)  │
└────────┬────────┘
         │
         │ API Request with code
         ▼
┌─────────────────┐
│ Bifrost Gateway │
│   (localhost:   │
│      8000)      │
└────────┬────────┘
         │
         │ PreLLMHook checks code
         ▼
┌─────────────────┐
│ Proprietary     │
│ Detection       │
│ Plugin          │
└────────┬────────┘
         │
         ├─ If proprietary code detected → Block (403)
         │
         └─ If clean → Forward to LLM
                       ▼
              ┌─────────────────┐
              │   LLM Provider  │
              │ (Anthropic,     │
              │  OpenAI, etc.)  │
              └─────────────────┘
```

## ✅ Testing

### Test 1: Verify Bifrost is Running

```bash
curl http://localhost:8000/health
# Should return: {"status": "ok"}
```

### Test 2: Test Detection

```bash
# This should be BLOCKED
python test_bifrost_plugin.py
```

### Test 3: Test with Your Tool

```bash
# Set environment variable
export ANTHROPIC_BASE_URL="http://localhost:8000"

# Try to send proprietary code
echo "def calculate_secret_score(data, weights): ..." | your-tool
# Should be blocked with 403 error
```

## 🎛️ Configuration Options

Edit the plugin config in Bifrost:

```json
{
  "proprietary_code_dir": "./proprietary_code",  // Where your code is
  "similarity_threshold": 60,                     // 0-100 (60 = 60% similar)
  "block_on_detection": true,                     // Block or just log
  "log_only": false,                              // Set true to test without blocking
  "monitored_request_types": []                   // Empty = monitor all
}
```

**Threshold Guide:**
- `50` - Very strict (may have false positives)
- `60` - Balanced (recommended)
- `70` - Lenient (fewer false positives, may miss some)

## 🚨 What Gets Blocked

The plugin checks ALL text content in requests:
- ✅ Code in messages
- ✅ Code in prompts
- ✅ Code in system messages
- ✅ Code in function calls
- ✅ Code in tool inputs

**Example blocked request:**
```python
# User tries to send this to Claude
"""
def calculate_secret_score(data, weights):
    score = 0
    for i, value in enumerate(data):
        score += value * weights[i]
    return score
"""

# Result: 403 Forbidden
# Message: "Request blocked: Proprietary code detected (84.3% similarity)"
```

## 🔧 Troubleshooting

### Plugin not loading?

```bash
# Check Bifrost logs
cd bifrost
./bifrost logs

# Should see: "Loaded plugin: proprietary-detection"
```

### Detection not working?

```bash
# Verify proprietary code directory
ls -la proprietary_code/

# Should have .py files with your code
```

### Tool not using Bifrost?

```bash
# Check environment variables
echo $ANTHROPIC_BASE_URL
echo $OPENAI_BASE_URL

# Should be: http://localhost:8000
```

### Too many false positives?

```bash
# Increase threshold in Bifrost config
"similarity_threshold": 70  # Was 60
```

## 🎯 Advantages Over MITM Proxy

**Bifrost Plugin:**
- ✅ Works with terminal agents
- ✅ Works with AI IDEs
- ✅ No certificate installation
- ✅ No proxy configuration
- ✅ Better performance
- ✅ Centralized control

**MITM Proxy:**
- ❌ Only works with browsers
- ❌ Requires certificate installation
- ❌ Requires proxy configuration per tool
- ❌ Doesn't work with terminal agents

## 📊 Monitoring

View blocked requests in Bifrost logs:

```bash
cd bifrost
./bifrost logs | grep "PROPRIETARY CODE DETECTED"
```

Output:
```
🚨 PROPRIETARY CODE DETECTED!
   Request ID: req_abc123
   File: secret_algorithm.py
   Lines: 11-18
   Similarity: 84.3%
   Action: BLOCKED
```

## 🔐 Security Best Practices

1. **Keep proprietary code secure**: Only authorized users should access `proprietary_code/`
2. **Monitor logs**: Regularly check for detection events
3. **Test threshold**: Start with 60, adjust based on false positives/negatives
4. **Use log_only mode first**: Test without blocking to tune settings
5. **Rotate API keys**: Use Bifrost's key rotation features

## 🚀 Production Deployment

For production use:

1. **Run Bifrost as a service**:
```bash
cd bifrost
./bifrost install-service
systemctl start bifrost
```

2. **Configure all tools** to use Bifrost endpoint

3. **Set up monitoring** for detection events

4. **Create alerts** for repeated detection attempts

5. **Document for your team** which tools are protected

## 📝 Summary

✅ **Bifrost plugin** is the best solution for terminal agents and AI IDEs  
✅ **One-time setup** protects all tools  
✅ **No per-tool configuration** needed  
✅ **Centralized monitoring** and control  
✅ **Production-ready** and performant  

**Next steps:**
1. Run `./setup_bifrost_plugin.sh`
2. Configure your tools to use `http://localhost:8000`
3. Test with `python test_bifrost_plugin.py`
4. Start using your tools - they're now protected!
