# Bifrost Security Plugin

OPA-based security plugin for Bifrost LLM Gateway that provides comprehensive AI security capabilities including prompt injection detection, PII redaction, tool validation, and memory poisoning prevention.

## Features

- **Policy Enforcement**: Uses OPA Go SDK for flexible, policy-based access control
- **Prompt Injection Detection**: Pattern-based and ML-based (Lakera) threat detection
- **PII Detection & Redaction**: Integrates with Presidio for sensitive data protection
- **Tool Validation**: Validates LLM tool calls against security policies
- **Memory Poisoning Prevention**: Detects and blocks malicious memory writes
- **Audit Logging**: Comprehensive security event logging
- **Metrics**: Prometheus-compatible security metrics

## Architecture

The security plugin implements all Bifrost plugin interfaces:
- `HTTPTransportPlugin`: Intercepts HTTP requests before they enter Bifrost
- `LLMPlugin`: Validates LLM requests and responses
- `MCPPlugin`: Validates MCP tool executions

### Components

1. **PolicyEngine**: Evaluates Rego policies using OPA Go SDK
2. **PIIDetector**: Detects and redacts PII using Presidio service
3. **InjectionDetector**: Detects prompt injection attempts
4. **MemoryMonitor**: Tracks and validates memory operations
5. **AuditLogger**: Logs all security decisions
6. **SecurityMetrics**: Tracks security-related metrics

## Installation

### 1. Add OPA Dependency

The OPA Go SDK is already added to `bifrost/core/go.mod`:

```bash
cd bifrost/core
go get github.com/open-policy-agent/opa@v0.71.0
go mod tidy
```

### 2. Set Up Presidio (Optional)

If you want PII detection, run Presidio service:

```bash
docker run -d -p 5000:5000 mcr.microsoft.com/presidio-analyzer
```

### 3. Create Policy Directory

```bash
mkdir -p /etc/bifrost/policies
```

## Configuration

```go
config := &security.SecurityConfig{
    // Policy enforcement
    EnablePolicyEnforcement: true,
    PolicyPath:              "/etc/bifrost/policies",
    
    // PII detection
    EnablePIIDetection:      true,
    RedactPII:               true,
    PIIEntityTypes:          []string{"EMAIL", "PHONE", "SSN", "CREDIT_CARD"},
    PresidioURL:             "http://localhost:5000",
    
    // Prompt injection detection
    EnablePromptInjection:   true,
    ThreatScoreThreshold:    0.75,
    LakeraAPIKey:            "", // Optional: for ML-based detection
    
    // Memory poisoning detection
    EnableMemoryPoisoning:   true,
    MaxMemoryWrites:         100,
    MemoryThreatThreshold:   0.70,
    
    // Tool validation
    EnableToolValidation:    true,
    AllowedTools:            []string{"read_file", "search_web"},
    DeniedTools:             []string{"execute_shell", "delete_file"},
    
    // Behavior
    BlockOnHighThreat:       true,
    
    // Audit logging
    AuditLogPath:            "/var/log/bifrost/security.log",
    
    // Hook enablement
    EnableHTTPHooks:         true,
    EnableLLMHooks:          true,
    EnableMCPHooks:          true,
}
```

## Usage

### Initialize Plugin

```go
import (
    "github.com/maximhq/bifrost/core"
    "github.com/maximhq/bifrost/core/schemas"
    "github.com/maximhq/bifrost/plugins/security"
)

// Create security plugin
securityPlugin, err := security.NewSecurityPlugin(config, logger)
if err != nil {
    log.Fatal(err)
}

// Register with Bifrost
bifrostConfig := &schemas.BifrostConfig{
    Account:    account,
    LLMPlugins: []schemas.LLMPlugin{securityPlugin},
    MCPPlugins: []schemas.MCPPlugin{securityPlugin},
    HTTPTransportPlugins: []schemas.HTTPTransportPlugin{securityPlugin},
    Logger:     logger,
}

bifrost, err := bifrost.NewBifrost(bifrostConfig)
if err != nil {
    log.Fatal(err)
}
```

### Example Policies

#### Request Validation Policy

Create `/etc/bifrost/policies/request_validation.rego`:

```rego
package bifrost.security

default allow = false

# Allow requests with low threat scores
allow {
    input.security.threat_score < 0.75
    not has_critical_pii
}

# Deny if critical PII is detected
has_critical_pii {
    some entity in input.security.pii_entities
    entity.type == "SSN"
}

# Allow admin users
allow {
    input.context.user_role == "admin"
}
```

#### Tool Validation Policy

Create `/etc/bifrost/policies/tool_validation.rego`:

```rego
package bifrost.security

default allow = false

# Allow safe read-only tools
allow {
    input.tool_name == "read_file"
}

# Allow write tools for admin users only
allow {
    input.tool_name == "write_file"
    input.context.user_role == "admin"
}

# Deny dangerous tools
deny {
    input.tool_name == "execute_shell"
}
```

## Policy Input Structure

The plugin provides the following input data to policies:

```json
{
  "request": {
    "prompt": "User prompt text",
    "provider": "openai",
    "model": "gpt-4",
    "tools": ["read_file", "search_web"]
  },
  "context": {
    "user_id": "user123",
    "session_id": "session456",
    "user_role": "admin",
    "timestamp": 1234567890
  },
  "security": {
    "threat_score": 0.85,
    "pii_detected": true,
    "pii_entities": [
      {
        "type": "EMAIL",
        "text": "user@example.com",
        "start": 10,
        "end": 27,
        "score": 0.95
      }
    ]
  },
  "tool_name": "write_file",
  "tool_arguments": {
    "path": "/tmp/file.txt",
    "content": "data"
  }
}
```

## Testing

Run tests:

```bash
cd bifrost/plugins/security
go test -v
```

Run tests with race detection:

```bash
go test -race -v
```

## Security Considerations

### Threat Model

The plugin protects against:
- **Direct Prompt Injection**: Malicious instructions in user input
- **Indirect Prompt Injection**: Malicious content in tool outputs/memory
- **Tool Misuse**: Unauthorized tool execution
- **Memory Poisoning**: Persistent malicious instructions
- **Privilege Escalation**: Attempts to gain elevated permissions
- **Data Exfiltration**: PII leakage to LLM providers

### Defense in Depth

The plugin implements multiple layers of security:
1. Pattern-based detection (fast, high precision)
2. ML-based detection (slower, high recall)
3. Policy-based enforcement (flexible, auditable)
4. Rate limiting (prevents abuse)
5. Audit logging (forensics and compliance)

### Performance

- Pattern-based detection: < 10ms
- PII detection: < 15ms (for prompts < 1000 chars)
- Policy evaluation: < 100ms (with timeout)
- Total overhead: < 50ms at p99

## Troubleshooting

### Policy Compilation Errors

If policies fail to load:
1. Check policy syntax with `opa check`
2. Verify policy path exists and is readable
3. Check logs for compilation errors

### PII Detection Not Working

If PII is not being detected:
1. Verify Presidio service is running: `curl http://localhost:5000/health`
2. Check PresidioURL configuration
3. Verify entity types are supported

### High Latency

If security checks are slow:
1. Disable ML-based detection (remove LakeraAPIKey)
2. Reduce number of PII entity types
3. Simplify policy rules
4. Check network latency to external services

## License

Same as Bifrost core.
