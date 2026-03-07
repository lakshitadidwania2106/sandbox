# Getting Started - 5 Minute Quick Start

This guide will get you testing the Bifrost security plugin in 5 minutes.

## Choose Your Testing Method

### Option 1: Testing Without API Keys (Recommended for Quick Start)

**No API keys needed!** Use the mocker plugin to test all security features without any external API calls.

👉 **[Follow the 3-Minute Mocker Guide](GETTING_STARTED_MOCKER.md)**

Perfect for:
- ✅ Quick testing and learning
- ✅ CI/CD pipelines
- ✅ Development without API costs
- ✅ Security feature validation

### Option 2: Testing With Real OpenAI API (Full Integration)

Use real OpenAI API calls to test with actual LLM responses.

👉 **Continue with this guide below**

Perfect for:
- ✅ End-to-end integration testing
- ✅ Response quality validation
- ✅ Production-like testing

---

## Prerequisites Check

Before starting, make sure you have:

- [ ] Docker installed (`docker --version`)
- [ ] OpenAI API key (get one at https://platform.openai.com/)
- [ ] Terminal/command line access

That's it! The setup script will handle the rest.

## Step 1: Set Your API Key (30 seconds)

```bash
export OPENAI_API_KEY=sk-your-actual-key-here
```

💡 **Tip**: Replace `sk-your-actual-key-here` with your real OpenAI API key.

## Step 2: Run the Setup Script (2 minutes)

```bash
cd bifrost/tests/security-plugin-test
chmod +x start-test-environment.sh
./start-test-environment.sh
```

This script will:
- ✅ Check your system
- ✅ Start Presidio (PII detection service)
- ✅ Test Presidio is working
- ✅ Ask if you want to build Bifrost (say yes)

**Expected output:**
```
========================================
Bifrost Security Plugin Test Environment Setup
========================================

✓ Docker is installed
✓ Docker Compose is available
✓ Go is installed (go1.21.5)
✓ OPENAI_API_KEY is set

Starting Presidio services...
✓ Presidio Analyzer is healthy
✓ Presidio Anonymizer is healthy
```

## Step 3: Start Bifrost (30 seconds)

In the same terminal:

```bash
cd ../../..
./bifrost --config tests/security-plugin-test/config.json
```

**Expected output:**
```
INFO: Loading security plugin...
INFO: Presidio PII detection enabled
INFO: OPA policy engine initialized
INFO: Server listening on :8080
```

✅ **Success!** Bifrost is now running with the security plugin.

## Step 4: Run Tests (1 minute)

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

🎉 **Congratulations!** All tests passed. The security plugin is working correctly.

## What Just Happened?

You just tested:

1. ✅ **Normal requests** - Legitimate requests work fine
2. 🔍 **PII detection** - Emails, phone numbers detected
3. 🚫 **SSN blocking** - Social Security Numbers blocked
4. 🚫 **Prompt injection** - Malicious prompts blocked
5. ✅ **Safe tools** - Read-only tools allowed
6. 🚫 **Dangerous tools** - Command execution blocked
7. 🚫 **Path traversal** - File system attacks blocked

## Alternative: Testing Without API Keys

Want to test without spending money on API calls? Check out the mocker-based setup:

👉 **[GETTING_STARTED_MOCKER.md](GETTING_STARTED_MOCKER.md)** - 3-minute setup with no API keys required

The mocker plugin provides mock LLM responses while still running all security validations. Perfect for:
- Development and testing
- CI/CD pipelines
- Learning the security features
- Policy development

## Next Steps

### View the Logs

```bash
# Bifrost logs
tail -f logs/bifrost.log

# Security audit logs
tail -f logs/security-audit.log
```

### Try Manual Tests

```bash
# Test a normal request
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "What is 2+2?"}]
  }'

# Test PII detection (should block or redact)
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "My SSN is 123-45-6789"}]
  }'
```

### Explore the Configuration

```bash
# View the security configuration
cat config.json | jq '.plugins[] | select(.name=="security")'

# View the policies
cat policies/request_validation.rego
cat policies/tool_validation.rego
```

### Read the Documentation

- [README.md](README.md) - Full documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Command cheatsheet
- [TEST_SUITE_OVERVIEW.md](TEST_SUITE_OVERVIEW.md) - Detailed overview

## Cleanup

When you're done testing:

```bash
# Stop Bifrost (Ctrl+C in the Bifrost terminal)

# Run cleanup script
./cleanup.sh
```

## Troubleshooting

### "Bifrost is not running"

Make sure Bifrost is started:
```bash
cd bifrost
./bifrost --config tests/security-plugin-test/config.json
```

### "Connection refused to Presidio"

Restart Presidio:
```bash
docker-compose restart
sleep 10
curl http://localhost:5000/health
```

### "Invalid API key"

Check your API key is set:
```bash
echo $OPENAI_API_KEY
```

If empty, set it:
```bash
export OPENAI_API_KEY=sk-your-key-here
```

### Tests are failing

1. Check Bifrost is running: `curl http://localhost:8080/health`
2. Check Presidio is running: `curl http://localhost:5000/health`
3. Check logs: `tail -f logs/bifrost.log`
4. See [README.md](README.md) troubleshooting section

## Common Questions

**Q: Do I need Lakera Guard?**
A: No, it's optional. The plugin works without it using built-in detection.

**Q: Can I use a different LLM provider?**
A: Yes! Edit `config.json` and add your provider configuration.

**Q: Is this production-ready?**
A: Yes! The security plugin is designed for production use. See [TEST_SUITE_OVERVIEW.md](TEST_SUITE_OVERVIEW.md) for details.

**Q: How do I customize the policies?**
A: Edit the `.rego` files in the `policies/` directory. See [OPA documentation](https://www.openpolicyagent.org/docs/).

**Q: Can I add more PII types?**
A: Yes! Edit `config.json` and add to `pii_entity_types` array.

## What's Next?

Now that you have the security plugin working, you can:

1. **Customize policies** - Edit `.rego` files to match your security requirements
2. **Add more tests** - Extend `test-security.sh` with your own scenarios
3. **Integrate with CI/CD** - See [TEST_SUITE_OVERVIEW.md](TEST_SUITE_OVERVIEW.md) for examples
4. **Deploy to production** - See [README.md](README.md) for production best practices
5. **Monitor security events** - Set up log aggregation for audit logs

## Need Help?

- 📖 Read the [full README](README.md)
- 🔍 Check the [troubleshooting guide](README.md#troubleshooting)
- 💬 Open a GitHub issue
- 📧 Contact the Bifrost team

---

**Estimated time to complete:** 5 minutes
**Difficulty:** Beginner
**Last updated:** 2025-01-01
