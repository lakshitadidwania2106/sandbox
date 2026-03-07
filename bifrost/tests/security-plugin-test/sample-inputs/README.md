# Sample Input Files for Policy Testing

This directory contains sample JSON input files that can be used to test OPA policies directly without running the full Bifrost server.

## Usage

### Prerequisites

Install OPA CLI:
```bash
# macOS
brew install opa

# Linux
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/

# Windows
# Download from https://www.openpolicyagent.org/docs/latest/#running-opa
```

### Test Request Validation Policy

```bash
# Test normal request (should allow)
opa eval -d ../policies/request_validation.rego \
  -i normal-request.json \
  "data.bifrost.security.allow"

# Expected output: true

# Test PII request (should deny)
opa eval -d ../policies/request_validation.rego \
  -i pii-request.json \
  "data.bifrost.security"

# Expected output: allow = false, reason = "Request blocked: SSN detected in prompt"

# Test injection request (should deny)
opa eval -d ../policies/request_validation.rego \
  -i injection-request.json \
  "data.bifrost.security"

# Expected output: allow = false, reason = "Request blocked: threat score 0.92 exceeds threshold"
```

### Test Tool Validation Policy

```bash
# Test allowed tool (should allow)
opa eval -d ../policies/tool_validation.rego \
  -i allowed-tool.json \
  "data.bifrost.security.allow"

# Expected output: true

# Test denied tool (should deny)
opa eval -d ../policies/tool_validation.rego \
  -i denied-tool.json \
  "data.bifrost.security"

# Expected output: allow = false, reason = "Tool execution blocked: dangerous command pattern 'rm -rf' detected"

# Test path traversal (should deny)
opa eval -d ../policies/tool_validation.rego \
  -i path-traversal-tool.json \
  "data.bifrost.security"

# Expected output: allow = false, reason = "Tool execution blocked: path traversal attempt detected (../)"
```

### Interactive Testing

You can also use OPA's REPL for interactive testing:

```bash
# Start OPA REPL with policies loaded
opa run ../policies/

# In the REPL, load an input file and test
> input := json.unmarshal(read_file("normal-request.json"))
> data.bifrost.security.allow
true

> input := json.unmarshal(read_file("pii-request.json"))
> data.bifrost.security.allow
false

> data.bifrost.security.reason
"Request blocked: SSN detected in prompt"
```

## Sample Files

### Request Validation Samples

1. **normal-request.json**
   - Clean request with no security issues
   - Expected: Allow

2. **pii-request.json**
   - Contains SSN and email
   - Expected: Deny (SSN detected)

3. **injection-request.json**
   - High threat score (0.92)
   - Expected: Deny (threat score exceeds threshold)

### Tool Validation Samples

1. **allowed-tool.json**
   - Safe read_file tool
   - Expected: Allow

2. **denied-tool.json**
   - Dangerous execute_command with rm -rf
   - Expected: Deny (dangerous command pattern)

3. **path-traversal-tool.json**
   - Path traversal attempt with ../
   - Expected: Deny (path traversal detected)

## Creating Custom Test Cases

You can create your own test cases by copying and modifying these files:

```bash
# Copy a template
cp normal-request.json my-test.json

# Edit the file
vim my-test.json

# Test it
opa eval -d ../policies/request_validation.rego \
  -i my-test.json \
  "data.bifrost.security"
```

## Batch Testing

Test all request validation samples:

```bash
for file in *-request.json; do
  echo "Testing $file:"
  opa eval -d ../policies/request_validation.rego \
    -i "$file" \
    "data.bifrost.security.allow"
  echo ""
done
```

Test all tool validation samples:

```bash
for file in *-tool.json; do
  echo "Testing $file:"
  opa eval -d ../policies/tool_validation.rego \
    -i "$file" \
    "data.bifrost.security.allow"
  echo ""
done
```

## Understanding Policy Output

When testing policies, you'll see output like:

```json
{
  "allow": false,
  "reason": "Request blocked: SSN detected in prompt",
  "status_code": 403
}
```

- **allow**: Boolean indicating if the request is allowed
- **reason**: Human-readable explanation of the decision
- **status_code**: HTTP status code to return (403 for blocked requests)

## Debugging Policies

To see all deny rules that matched:

```bash
opa eval -d ../policies/request_validation.rego \
  -i pii-request.json \
  "data.bifrost.security.deny"
```

To see detailed evaluation trace:

```bash
opa eval --explain=full \
  -d ../policies/request_validation.rego \
  -i pii-request.json \
  "data.bifrost.security.allow"
```

## Tips

1. **Use jq for pretty output**:
   ```bash
   opa eval -d ../policies/request_validation.rego \
     -i normal-request.json \
     "data.bifrost.security" | jq
   ```

2. **Test specific rules**:
   ```bash
   # Test only the threat score rule
   opa eval -d ../policies/request_validation.rego \
     -i injection-request.json \
     "data.bifrost.security.deny[_]" | grep threat
   ```

3. **Modify inputs on the fly**:
   ```bash
   # Change threat score and test
   jq '.security.threat_score = 0.5' pii-request.json | \
     opa eval -d ../policies/request_validation.rego \
     -I - "data.bifrost.security.allow"
   ```
