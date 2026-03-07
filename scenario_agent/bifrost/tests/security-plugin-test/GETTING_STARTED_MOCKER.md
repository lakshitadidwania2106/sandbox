# Getting Started with Mocker - 3 Minute Quick Start

This ultra-simple guide gets you testing the Bifrost security plugin **without any API keys** using the mocker plugin.

## What You Need

- [ ] Docker installed (`docker --version`)
- [ ] Terminal/command line access

**That's it!** No OpenAI API key, no Lakera Guard, no external services except Docker for Presidio.

## Step 1: Start Presidio (1 minute)

```bash
cd bifrost/tests/security-plugin-test
chmod +x start-test-environment.sh
./start-test-environment.sh
```

When asked "Do you want to build Bifrost now?", say **yes**.

**Expected output:**
```
✓ Docker is installed
✓ Presidio Analyzer is healthy
✓ Presidio Anonymizer is healthy
✓ Bifrost built successfully
```

## Step 2: Start Bifrost with Mocker (30 seconds)

```bash
cd ../../..
./bifrost --config tests/security-plugin-test/config-with-mocker.json
```

**Expected output:**
```
INFO: Loading mocker plugin...
INFO: Loading security plugin...
INFO: Presidio PII detection enabled
INFO: OPA policy engine initialized
INFO: Server listening on :8080
```

✅ **Success!** Bifrost is running with mock responses.

## Step 3: Run Tests (1 minute)

Open a **NEW terminal** and run:

```bash
cd bifrost/tests/security-plugin-test
./test-security.sh
```

**Expected output:**
```
========================================
Bifrost Security Plugin Test Suite
========================================

✓ PASSED: Bifrost is running

========================================
TEST 1: Normal Request
========================================
Response: "This is a mock LLM response from Bifrost..."
✓ PASSED: Normal request succeeded as expected

[... 9 more tests ...]

========================================
Test Summary
========================================
Total Tests: 10
Passed: 10
Failed: 0
========================================
```

🎉 **Done!** All security features tested without any API keys.

## How It Works

The mocker plugin intercepts all LLM requests and returns mock responses **before** they reach OpenAI. The security plugin still validates everything:

1. **Request comes in** → Security plugin checks it
2. **Security validates** → PII detection, prompt injection checks, policy enforcement
3. **Mocker responds** → Returns mock response (no API call)
4. **Response goes out** → Client receives mock data

This lets you test all security features without spending money on API calls!

## Quick Test Examples

### Test Normal Request
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**Response:**
```json
{
  "choices": [{
    "message": {
      "content": "This is a mock LLM response from Bifrost..."
    }
  }]
}
```

### Test PII Detection (Should Block)
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "My SSN is 123-45-6789"}]
  }'
```

**Response:**
```json
{
  "error": {
    "message": "Request blocked: PII detected (SSN)",
    "type": "security_violation"
  }
}
```

### Test Dangerous Tool (Should Block)
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Use execute_command tool"}],
    "tools": [{"type": "function", "function": {"name": "execute_command"}}]
  }'
```

**Response:**
```json
{
  "error": {
    "message": "Tool 'execute_command' is not allowed",
    "type": "policy_violation"
  }
}
```

## View Security Logs

```bash
# Real-time security audit log
tail -f logs/security-audit.log

# Bifrost main log
tail -f logs/bifrost.log
```

## Cleanup

```bash
# Stop Bifrost (Ctrl+C in the Bifrost terminal)

# Stop Presidio
./cleanup.sh
```

## What's Different from Real API?

| Feature | With Mocker | With Real API |
|---------|-------------|---------------|
| API Key Required | ❌ No | ✅ Yes |
| Costs Money | ❌ No | ✅ Yes |
| Security Validation | ✅ Full | ✅ Full |
| Response Content | 🔄 Mock | 🤖 Real AI |
| Response Speed | ⚡ Fast (10-50ms) | 🐌 Slower (500-2000ms) |
| PII Detection | ✅ Works | ✅ Works |
| Policy Enforcement | ✅ Works | ✅ Works |
| Tool Validation | ✅ Works | ✅ Works |

## When to Use Mocker vs Real API

### Use Mocker For:
- ✅ Testing security features
- ✅ CI/CD pipelines
- ✅ Development without API costs
- ✅ Learning how Bifrost works
- ✅ Policy development and testing

### Use Real API For:
- ✅ Testing actual LLM responses
- ✅ End-to-end integration tests
- ✅ Production deployments
- ✅ Response quality validation

## Next Steps

### Switch to Real API

When you're ready to test with real LLM responses:

1. Get an OpenAI API key
2. Set it: `export OPENAI_API_KEY=sk-your-key`
3. Use the regular config: `./bifrost --config tests/security-plugin-test/config.json`

### Customize Mock Responses

Edit `config-with-mocker.json` to change mock responses:

```json
{
  "plugins": [
    {
      "name": "mocker",
      "config": {
        "rules": [
          {
            "name": "custom-mock",
            "responses": [
              {
                "content": {
                  "message": "Your custom mock response here!"
                }
              }
            ]
          }
        ]
      }
    }
  ]
}
```

### Explore More

- [GETTING_STARTED.md](GETTING_STARTED.md) - Full guide with real API
- [README.md](README.md) - Complete documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command cheatsheet
- [Mocker Plugin](../../plugins/mocker/README.md) - Advanced mocker features

## Troubleshooting

### "Connection refused to Presidio"

Restart Presidio:
```bash
docker-compose restart
sleep 10
curl http://localhost:5000/health
```

### "Bifrost is not running"

Check if it's running:
```bash
curl http://localhost:8080/health
```

If not, start it:
```bash
./bifrost --config tests/security-plugin-test/config-with-mocker.json
```

### Tests are failing

1. Check Bifrost: `curl http://localhost:8080/health`
2. Check Presidio: `curl http://localhost:5000/health`
3. Check logs: `tail -f logs/bifrost.log`

## Common Questions

**Q: Do mock responses go through security validation?**
A: Yes! The mocker plugin runs AFTER the security plugin, so all security checks still happen.

**Q: Can I test prompt injection without Lakera Guard?**
A: Yes! The security plugin has built-in prompt injection detection that works without Lakera.

**Q: Is this suitable for CI/CD?**
A: Absolutely! No API keys means no secrets management and no API costs in CI.

**Q: Can I mix mock and real responses?**
A: Yes! Configure the mocker plugin with conditions to mock only specific requests.

---

**Estimated time:** 3 minutes
**Difficulty:** Beginner
**API Keys Required:** None
**Cost:** Free

