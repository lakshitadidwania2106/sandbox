# Bifrost Integration Guide: Proprietary Code Detection

## Overview

Instead of using an MITM proxy (like SigmaShield), we've integrated proprietary code detection **directly into the Bifrost gateway** as a plugin. This is a much better approach!

## Why Bifrost Plugin > MITM Proxy

### Advantages

1. **No System Configuration**
   - No proxy settings to configure
   - No certificate installation
   - Works immediately

2. **Better Performance**
   - No extra network hop
   - Detection happens at gateway level
   - Lower latency

3. **Centralized Control**
   - All traffic goes through Bifrost
   - Single point of enforcement
   - Easier to manage

4. **More Reliable**
   - No proxy connection issues
   - No certificate expiration
   - No browser-specific setup

5. **Better Integration**
   - Access to full request context
   - Can use Bifrost's logging
   - Can integrate with other plugins

## How It Works

```
User Request → Bifrost Gateway → Plugin PreLLMHook → Detection
                                        ↓
                                  Proprietary?
                                   ↙        ↘
                              YES: Block    NO: Allow
                                   ↓             ↓
                            403 Error      LLM Provider
```

### Detection Flow

1. **Request arrives** at Bifrost gateway
2. **PreLLMHook** is called (BEFORE reaching LLM)
3. **Extract text** from request (chat messages, prompts, etc.)
4. **Fuzzy search** against proprietary code files
5. **If match found** (similarity >= threshold):
   - Log detection
   - Block request (403 Forbidden)
6. **If no match**: Continue to LLM provider

## Installation

### Step 1: Build the Plugin

```bash
# Navigate to your Bifrost directory
cd /path/to/bifrost

# Copy the plugin file
cp /path/to/bifrost_plugin_proprietary_detection.go plugins/proprietary-detection/main.go

# Build the plugin
cd plugins/proprietary-detection
go build -buildmode=plugin -o proprietary_detection.so main.go
```

### Step 2: Add Proprietary Code

```bash
# Create proprietary code directory
mkdir -p proprietary_code

# Add your company's proprietary code
cp /path/to/your/secret/*.py proprietary_code/
cp /path/to/your/internal/*.js proprietary_code/
# ... add more files
```

### Step 3: Configure Bifrost

Add the plugin to your Bifrost configuration:

```json
{
  "plugins": [
    {
      "name": "proprietary-detection",
      "path": "./plugins/proprietary-detection/proprietary_detection.so",
      "enabled": true,
      "config": {
        "proprietary_code_dir": "./proprietary_code",
        "similarity_threshold": 60,
        "block_on_detection": true,
        "log_only": false,
        "monitored_request_types": []
      }
    }
  ]
}
```

### Step 4: Restart Bifrost

```bash
# Restart Bifrost to load the plugin
./bifrost restart
```

## Configuration Options

### `proprietary_code_dir` (string)
- **Default**: `"./proprietary_code"`
- **Description**: Directory containing your proprietary code files
- **Example**: `"/opt/company/proprietary_code"`

### `similarity_threshold` (int)
- **Default**: `60`
- **Range**: `0-100`
- **Description**: Minimum similarity percentage to trigger detection
- **Recommendations**:
  - `50`: More strict (catches more, may have false positives)
  - `60`: Balanced (recommended)
  - `70`: More lenient (fewer false positives, may miss some)

### `block_on_detection` (bool)
- **Default**: `true`
- **Description**: Whether to block requests when proprietary code is detected
- **Options**:
  - `true`: Block requests (403 Forbidden)
  - `false`: Allow requests to proceed

### `log_only` (bool)
- **Default**: `false`
- **Description**: If true, only log detections without blocking
- **Use case**: Testing/monitoring mode before enforcing

### `monitored_request_types` (array of strings)
- **Default**: `[]` (empty = monitor all)
- **Description**: Specific request types to monitor
- **Options**:
  - `"chat_completion"`
  - `"chat_completion_stream"`
  - `"text_completion"`
  - `"text_completion_stream"`
  - `"responses"`
  - `"responses_stream"`
- **Example**: `["chat_completion", "chat_completion_stream"]`

## Usage Examples

### Example 1: Basic Setup (Block Everything)

```json
{
  "config": {
    "proprietary_code_dir": "./proprietary_code",
    "similarity_threshold": 60,
    "block_on_detection": true
  }
}
```

### Example 2: Monitoring Mode (Log Only)

```json
{
  "config": {
    "proprietary_code_dir": "./proprietary_code",
    "similarity_threshold": 60,
    "block_on_detection": false,
    "log_only": true
  }
}
```

### Example 3: Strict Detection

```json
{
  "config": {
    "proprietary_code_dir": "./proprietary_code",
    "similarity_threshold": 50,
    "block_on_detection": true
  }
}
```

### Example 4: Monitor Only Chat Requests

```json
{
  "config": {
    "proprietary_code_dir": "./proprietary_code",
    "similarity_threshold": 60,
    "block_on_detection": true,
    "monitored_request_types": ["chat_completion", "chat_completion_stream"]
  }
}
```

## Testing

### Test 1: Verify Plugin Loaded

```bash
# Check Bifrost logs
tail -f /var/log/bifrost/bifrost.log | grep "proprietary-detection"

# You should see:
# [INFO] Plugin loaded: proprietary-detection
# [INFO] Indexed 5 proprietary code files
```

### Test 2: Test with Proprietary Code

```bash
# Send a request with proprietary code
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "def calculate_secret_score(data, weights):\n    score = 0\n    for i, value in enumerate(data):\n        score += value * weights[i]\n    return score"
      }
    ]
  }'

# Expected response:
# HTTP 403 Forbidden
# {
#   "error": {
#     "message": "Request blocked: Proprietary code detected (84.3% similarity with secret_algorithm.py, lines 11-18)",
#     "type": "proprietary_code_detected"
#   }
# }
```

### Test 3: Test with Generic Code

```bash
# Send a request with generic code
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "def add(a, b):\n    return a + b"
      }
    ]
  }'

# Expected response:
# HTTP 200 OK
# (Normal ChatGPT response)
```

## Monitoring

### Check Detection Logs

```bash
# View detection logs
tail -f /var/log/bifrost/bifrost.log | grep "PROPRIETARY CODE DETECTED"

# Example output:
# 🚨 PROPRIETARY CODE DETECTED!
#    Request ID: req-abc123
#    File: secret_algorithm.py
#    Lines: 11-18
#    Similarity: 84.3%
#    Action: BLOCKED
```

### Metrics

The plugin logs the following for each detection:
- Request ID
- Matched file
- Line numbers
- Similarity percentage
- Action taken (BLOCKED or LOGGED ONLY)

## Troubleshooting

### Plugin Not Loading

**Problem**: Plugin doesn't appear in logs

**Solutions**:
1. Check plugin path is correct
2. Verify plugin was built successfully
3. Check file permissions: `chmod +x proprietary_detection.so`
4. Check Bifrost logs for errors

### No Detections

**Problem**: Proprietary code not being detected

**Solutions**:
1. Verify proprietary code files exist: `ls -la proprietary_code/`
2. Lower threshold: Set `similarity_threshold` to 50
3. Check file extensions are supported (`.py`, `.js`, `.ts`, etc.)
4. Enable debug logging

### Too Many False Positives

**Problem**: Generic code being blocked

**Solutions**:
1. Increase threshold: Set `similarity_threshold` to 70
2. Review proprietary code files - remove generic patterns
3. Use `log_only` mode to analyze detections first

### Performance Issues

**Problem**: Requests are slow

**Solutions**:
1. Reduce number of proprietary code files
2. Increase threshold (fewer comparisons needed)
3. Use `monitored_request_types` to limit scope

## Advanced Configuration

### Multiple Proprietary Code Directories

```json
{
  "plugins": [
    {
      "name": "proprietary-detection-backend",
      "path": "./plugins/proprietary-detection/proprietary_detection.so",
      "enabled": true,
      "config": {
        "proprietary_code_dir": "./proprietary_code/backend",
        "similarity_threshold": 60
      }
    },
    {
      "name": "proprietary-detection-frontend",
      "path": "./plugins/proprietary-detection/proprietary_detection.so",
      "enabled": true,
      "config": {
        "proprietary_code_dir": "./proprietary_code/frontend",
        "similarity_threshold": 60
      }
    }
  ]
}
```

### Integration with Other Plugins

The proprietary detection plugin works seamlessly with other Bifrost plugins:

```json
{
  "plugins": [
    {
      "name": "governance",
      "enabled": true
    },
    {
      "name": "proprietary-detection",
      "enabled": true
    },
    {
      "name": "semantic-cache",
      "enabled": true
    }
  ]
}
```

**Execution order**:
1. Governance plugin (rate limiting, budgets)
2. Proprietary detection (code leak prevention)
3. Semantic cache (response caching)
4. LLM provider call

## Comparison: MITM Proxy vs Bifrost Plugin

| Feature | MITM Proxy | Bifrost Plugin |
|---------|------------|----------------|
| Setup Complexity | High (proxy + cert) | Low (just config) |
| Performance | Slower (extra hop) | Faster (native) |
| Reliability | Medium (proxy issues) | High (native) |
| Centralized | No (per-client) | Yes (gateway) |
| Integration | External | Native |
| Maintenance | High | Low |
| Monitoring | Separate logs | Bifrost logs |
| Fallback Support | No | Yes |

## Migration from MITM Proxy

If you're currently using the MITM proxy approach:

1. **Keep proprietary code directory** - Same files work!
2. **Build and configure plugin** - Follow installation steps
3. **Test in parallel** - Run both for a while
4. **Disable MITM proxy** - Once confident, remove proxy
5. **Remove proxy config** - Clean up browser/system settings

## Security Considerations

1. **Proprietary Code Storage**
   - Keep `proprietary_code/` directory secure
   - Use appropriate file permissions
   - Don't commit to public repos

2. **Plugin Security**
   - Plugin runs in Bifrost process
   - Has access to all requests
   - Review code before deployment

3. **Logging**
   - Detections are logged
   - May contain sensitive info
   - Secure log files appropriately

## Performance Optimization

1. **File Organization**
   - Keep only essential proprietary files
   - Remove duplicates
   - Organize by project/module

2. **Threshold Tuning**
   - Start with 60
   - Adjust based on false positive rate
   - Higher threshold = faster (fewer matches)

3. **Request Type Filtering**
   - Use `monitored_request_types` to limit scope
   - Focus on high-risk request types

## Support

For issues or questions:
1. Check Bifrost logs: `/var/log/bifrost/bifrost.log`
2. Enable debug logging in Bifrost config
3. Review this guide's troubleshooting section
4. Check Bifrost documentation

## Summary

✅ **Bifrost plugin approach is superior to MITM proxy**

**Benefits**:
- Easier setup (no proxy configuration)
- Better performance (native integration)
- More reliable (no proxy issues)
- Centralized control (gateway level)
- Better monitoring (Bifrost logs)

**Next Steps**:
1. Build the plugin
2. Add your proprietary code
3. Configure Bifrost
4. Test and monitor
5. Adjust threshold as needed

The system will now protect your proprietary code at the gateway level!
