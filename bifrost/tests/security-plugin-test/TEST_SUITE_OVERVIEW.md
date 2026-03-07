# Bifrost Security Plugin Test Suite - Overview

## What This Test Suite Does

This comprehensive test suite validates the Bifrost security plugin's ability to:

1. **Detect and Redact PII** - Identifies sensitive information like SSNs, emails, phone numbers, and credit cards
2. **Prevent Prompt Injection** - Blocks malicious prompts attempting to manipulate the LLM
3. **Validate Tool Execution** - Enforces policies on which tools can be executed and with what parameters
4. **Enforce Security Policies** - Uses OPA (Open Policy Agent) to enforce custom security rules
5. **Audit Security Events** - Logs all security-related events for compliance and monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Test Suite                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ Test Script  │─────▶│   Bifrost    │                   │
│  │ (curl tests) │      │   Gateway    │                   │
│  └──────────────┘      └──────┬───────┘                   │
│                               │                             │
│                               ▼                             │
│                    ┌──────────────────┐                    │
│                    │ Security Plugin  │                    │
│                    └────────┬─────────┘                    │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │  Presidio   │   │ OPA Policies │   │ Lakera Guard │   │
│  │ (PII Detect)│   │  (Rego)      │   │ (Optional)   │   │
│  └─────────────┘   └──────────────┘   └──────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Configuration (`config.json`)
- Configures Bifrost with the security plugin
- Sets up OpenAI provider
- Enables all security features
- Points to local Presidio service

### 2. OPA Policies (`policies/`)
- **request_validation.rego**: Validates incoming LLM requests
  - Checks threat scores
  - Validates PII presence
  - Enforces provider restrictions
  - Validates user roles
  
- **tool_validation.rego**: Validates tool execution
  - Whitelists safe tools
  - Blocks dangerous commands
  - Prevents path traversal
  - Enforces role-based access

### 3. Test Script (`test-security.sh`)
Automated test suite with 10 test scenarios:
- ✅ Normal request (baseline)
- 🔍 PII detection (email)
- 🚫 PII blocking (SSN)
- 🚫 Multiple PII entities
- 🚫 Prompt injection
- ✅ Allowed tool call
- 🚫 Denied tool call
- 🚫 Dangerous command pattern
- 🚫 Path traversal attempt
- 🚫 Unapproved provider

### 4. Environment Setup (`start-test-environment.sh`)
- Checks prerequisites
- Starts Presidio services
- Tests Presidio connectivity
- Optionally builds Bifrost
- Creates log directories

### 5. Cleanup Script (`cleanup.sh`)
- Stops Bifrost
- Stops Presidio
- Cleans logs
- Removes Docker volumes

### 6. Sample Inputs (`sample-inputs/`)
JSON files for manual OPA policy testing:
- Normal requests
- PII-containing requests
- Injection attempts
- Tool validation scenarios

## Security Features Tested

### PII Detection & Redaction

**Entity Types Detected:**
- EMAIL (email addresses)
- PHONE (phone numbers)
- SSN (Social Security Numbers)
- CREDIT_CARD (credit card numbers)
- IP_ADDRESS (IP addresses)
- PERSON (person names)
- LOCATION (geographic locations)

**Behavior:**
- Low-risk PII (email, phone): Redacted but request allowed
- High-risk PII (SSN, credit card): Request blocked
- Multiple PII entities: Request blocked

**Technology:** Microsoft Presidio (open-source)

### Prompt Injection Prevention

**Detection Methods:**
- Threat score calculation (0.0 - 1.0)
- Pattern matching for common injection techniques
- Context-aware analysis

**Thresholds:**
- Score > 0.75: Always blocked
- Score > 0.5: Blocked for guest users
- Score < 0.5: Allowed with logging

**Technology:** Lakera Guard (optional) or built-in detection

### Tool Validation

**Safe Tools (Always Allowed):**
- read_file
- list_directory
- search
- get_weather
- calculate
- get_time

**Dangerous Tools (Blocked):**
- execute_command
- delete_file
- write_database

**Dangerous Patterns Blocked:**
- `rm -rf` (recursive delete)
- `curl | sh` (download and execute)
- `eval` (code evaluation)
- `../` (path traversal)
- Access to sensitive files (.ssh/, .env, etc.)

### Policy Enforcement

**Request Policies:**
- Provider whitelist (OpenAI, Anthropic, Google, Azure)
- Model restrictions (GPT-4 requires elevated role)
- Prompt length limits (max 50,000 characters)
- Tool combination safety (prevent dangerous combos)
- Time-based access control (maintenance windows)

**Tool Policies:**
- Role-based access control
- Path restrictions (workspace, home directory only)
- Command injection prevention (CVE-2025-53773)
- SSRF prevention (block internal IPs)
- SQL injection prevention

## Test Results Interpretation

### Expected Pass/Fail Matrix

| Test # | Scenario | Expected HTTP | Expected Behavior |
|--------|----------|---------------|-------------------|
| 1 | Normal request | 200 | Request succeeds |
| 2 | Email PII | 200 | Email redacted |
| 3 | SSN PII | 403 | Request blocked |
| 4 | Multiple PII | 403 | Request blocked |
| 5 | Prompt injection | 403 | Request blocked |
| 6 | Allowed tool | 200 | Tool executes |
| 7 | Denied tool | 403 | Tool blocked |
| 8 | Dangerous command | 403 | Command blocked |
| 9 | Path traversal | 403 | Path blocked |
| 10 | Unapproved provider | 403/400 | Provider blocked |

### Success Criteria

A successful test run should show:
- ✅ 10/10 tests passed
- All security blocks working correctly
- No false positives (normal requests allowed)
- No false negatives (attacks blocked)
- Audit logs generated

### Common Failure Modes

1. **All tests fail with connection errors**
   - Bifrost not running
   - Wrong port/URL

2. **PII tests fail**
   - Presidio not running
   - Presidio URL misconfigured

3. **Injection tests fail**
   - Lakera API key missing (if using Lakera)
   - Threat score threshold too high

4. **Tool tests fail**
   - Policy files missing
   - OPA not initialized

## Performance Considerations

### Resource Usage

**Presidio:**
- RAM: ~2GB per service (analyzer + anonymizer)
- CPU: Moderate (depends on request volume)
- Startup time: ~30 seconds

**Bifrost + Security Plugin:**
- RAM: ~100-200MB
- CPU: Low (OPA is very efficient)
- Latency added: ~50-100ms per request

### Scalability

The security plugin is designed for production use:
- OPA policies are compiled and cached
- Presidio can be scaled horizontally
- Audit logging is asynchronous
- Minimal impact on request throughput

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Security Plugin Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start Presidio
        run: |
          cd bifrost/tests/security-plugin-test
          docker-compose up -d
          sleep 30
      
      - name: Build Bifrost
        run: |
          cd bifrost
          make build
      
      - name: Start Bifrost
        run: |
          cd bifrost
          ./bifrost --config tests/security-plugin-test/config.json &
          sleep 10
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      
      - name: Run Tests
        run: |
          cd bifrost/tests/security-plugin-test
          ./test-security.sh
      
      - name: Upload Logs
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-logs
          path: bifrost/tests/security-plugin-test/logs/
```

## Extending the Test Suite

### Adding New Tests

1. **Add test function to `test-security.sh`:**
```bash
test_my_new_scenario() {
    print_header "TEST 11: My New Test"
    print_test "Testing new scenario"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_ENDPOINT}" \
        -H "Content-Type: application/json" \
        -d '{ ... }')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "Test passed"
    else
        print_failure "Test failed"
    fi
}
```

2. **Add to main() function:**
```bash
main() {
    # ... existing tests ...
    test_my_new_scenario
    print_summary
}
```

### Adding New Policies

1. **Create new .rego file in `policies/`:**
```rego
package bifrost.security

# My custom policy
deny[msg] {
    # Your policy logic
    msg := "Custom policy violation"
}
```

2. **Update `config.json` to reference new policy:**
```json
{
  "plugins": [{
    "config": {
      "policy_path": "./policies"
    }
  }]
}
```

### Adding New PII Types

1. **Update `config.json`:**
```json
{
  "pii_entity_types": [
    "EMAIL",
    "PHONE",
    "SSN",
    "MY_CUSTOM_TYPE"
  ]
}
```

2. **Configure Presidio recognizer** (if needed)

## Security Best Practices

### Production Deployment

1. **Use HTTPS**: Always use TLS in production
2. **Rotate API Keys**: Regularly rotate LLM provider keys
3. **Monitor Audit Logs**: Set up log aggregation and alerting
4. **Update Policies**: Regularly review and update OPA policies
5. **Scale Presidio**: Run multiple Presidio instances for HA
6. **Rate Limiting**: Implement rate limiting at the gateway level
7. **Network Isolation**: Run Presidio in isolated network

### Compliance

The security plugin helps with:
- **GDPR**: PII detection and redaction
- **HIPAA**: PHI protection
- **PCI DSS**: Credit card number detection
- **SOC 2**: Audit logging and access control

### Threat Model

**Threats Mitigated:**
- Prompt injection attacks
- PII leakage
- Unauthorized tool execution
- Command injection (CVE-2025-53773)
- Path traversal attacks
- SSRF attacks
- SQL injection
- Data exfiltration

**Threats NOT Mitigated:**
- DDoS attacks (use rate limiting)
- Model poisoning (use trusted models)
- Side-channel attacks
- Physical security

## Troubleshooting Guide

### Quick Diagnostics

```bash
# Check all services
./start-test-environment.sh

# Run health checks
curl http://localhost:8080/health
curl http://localhost:5000/health
curl http://localhost:5001/health

# Check logs
tail -f logs/bifrost.log
tail -f logs/security-audit.log
docker-compose logs -f

# Test Presidio directly
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"test@example.com","language":"en"}'
```

### Debug Mode

Enable debug logging in `config.json`:
```json
{
  "logging": {
    "level": "debug"
  }
}
```

## Support and Resources

### Documentation
- [Main README](README.md) - Full setup guide
- [Quick Reference](QUICK_REFERENCE.md) - Command cheatsheet
- [Sample Inputs](sample-inputs/README.md) - OPA testing guide

### External Resources
- [OPA Documentation](https://www.openpolicyagent.org/docs/)
- [Presidio Documentation](https://microsoft.github.io/presidio/)
- [Bifrost Documentation](../../docs/)

### Getting Help
1. Check logs first
2. Review troubleshooting section
3. Test components individually
4. Open GitHub issue with logs

## License

This test suite is part of the Bifrost project and follows the same license.

---

**Last Updated:** 2025-01-01
**Version:** 1.0.0
**Maintainer:** Bifrost Security Team
