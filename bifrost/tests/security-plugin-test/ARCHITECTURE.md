# Security Plugin Test Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Test Environment                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  Test Script    │  Sends HTTP requests with various security scenarios
│ test-security.sh│  - Normal requests
└────────┬────────┘  - PII-containing requests
         │           - Prompt injection attempts
         │           - Tool execution requests
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Bifrost Gateway                             │
│                         (Port 8080)                                 │
└────────┬────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Security Plugin                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Request Processing Flow                    │  │
│  │                                                               │  │
│  │  1. Pre-Request Hook                                         │  │
│  │     ├─▶ PII Detection (Presidio)                            │  │
│  │     ├─▶ Prompt Injection Detection (Lakera/Built-in)        │  │
│  │     └─▶ Policy Evaluation (OPA)                             │  │
│  │                                                               │  │
│  │  2. Request Validation                                       │  │
│  │     ├─▶ Check threat score                                   │  │
│  │     ├─▶ Check PII entities                                   │  │
│  │     ├─▶ Validate provider/model                             │  │
│  │     └─▶ Check user role/permissions                         │  │
│  │                                                               │  │
│  │  3. Tool Validation (if tools requested)                     │  │
│  │     ├─▶ Check tool whitelist/blacklist                      │  │
│  │     ├─▶ Validate tool arguments                             │  │
│  │     ├─▶ Check for dangerous patterns                        │  │
│  │     └─▶ Enforce path restrictions                           │  │
│  │                                                               │  │
│  │  4. Decision                                                  │  │
│  │     ├─▶ ALLOW: Forward to LLM provider                      │  │
│  │     └─▶ DENY: Return 403 with reason                        │  │
│  │                                                               │  │
│  │  5. Post-Request Hook                                        │  │
│  │     ├─▶ Audit logging                                        │  │
│  │     ├─▶ Metrics collection                                   │  │
│  │     └─▶ Response validation                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────┬────────────────────────┬────────────────────────┬─────────────┘
     │                        │                        │
     ▼                        ▼                        ▼
┌─────────────┐      ┌──────────────┐      ┌──────────────────┐
│  Presidio   │      │ OPA Engine   │      │  Lakera Guard    │
│  Analyzer   │      │              │      │   (Optional)     │
│             │      │ Loads .rego  │      │                  │
│ Port 5000   │      │ policies     │      │  API Service     │
└─────────────┘      └──────────────┘      └──────────────────┘
     │                        │
     │                        │
     ▼                        ▼
┌─────────────┐      ┌──────────────┐
│  Presidio   │      │   Policies   │
│ Anonymizer  │      │              │
│             │      │ request_     │
│ Port 5001   │      │ validation   │
└─────────────┘      │              │
                     │ tool_        │
                     │ validation   │
                     └──────────────┘
```

## Request Flow Diagram

### Normal Request (Allowed)

```
User Request
    │
    ▼
┌─────────────────────┐
│ "What is 2+2?"      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Security Plugin     │
│ - Threat: 0.05      │ ✓ Low threat
│ - PII: None         │ ✓ No PII
│ - Provider: OpenAI  │ ✓ Approved
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ OPA Policy Check    │
│ allow = true        │ ✓ Allowed
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Forward to OpenAI   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Return Response     │
│ HTTP 200            │
└─────────────────────┘
```

### PII Request (Blocked)

```
User Request
    │
    ▼
┌─────────────────────┐
│ "My SSN is          │
│  123-45-6789"       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Security Plugin     │
│ - Threat: 0.15      │ ✓ Low threat
│ - PII: SSN detected │ ✗ Critical PII!
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Presidio Analysis   │
│ Entity: SSN         │
│ Score: 0.95         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ OPA Policy Check    │
│ deny[msg] matched   │ ✗ Denied
│ allow = false       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Block Request       │
│ HTTP 403            │
│ "SSN detected"      │
└─────────────────────┘
```

### Prompt Injection (Blocked)

```
User Request
    │
    ▼
┌─────────────────────┐
│ "Ignore previous    │
│  instructions..."   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Security Plugin     │
│ - Threat: 0.92      │ ✗ High threat!
│ - PII: None         │ ✓ No PII
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Injection Detection │
│ Pattern: "ignore"   │
│ Pattern: "previous" │
│ Score: 0.92         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ OPA Policy Check    │
│ threat_score > 0.75 │ ✗ Denied
│ allow = false       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Block Request       │
│ HTTP 403            │
│ "Threat score 0.92" │
└─────────────────────┘
```

### Tool Execution (Validated)

```
Tool Request
    │
    ▼
┌─────────────────────┐
│ Tool: execute_cmd   │
│ Args: "rm -rf /"    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Security Plugin     │
│ - Tool Validation   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Check Tool List     │
│ execute_cmd in      │ ✗ Denied tool!
│ denied_tools        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Check Patterns      │
│ "rm -rf" detected   │ ✗ Dangerous!
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ OPA Policy Check    │
│ deny[msg] matched   │ ✗ Denied
│ allow = false       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Block Tool          │
│ HTTP 403            │
│ "Dangerous pattern" │
└─────────────────────┘
```

## Component Interactions

### PII Detection Flow

```
┌──────────────┐
│ User Input   │
│ "test@ex.com"│
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│ Security Plugin                  │
│ if enable_pii_detection:         │
│   send_to_presidio()             │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Presidio Analyzer                │
│ POST /analyze                    │
│ {                                │
│   "text": "test@ex.com",         │
│   "language": "en"               │
│ }                                │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Presidio Response                │
│ [                                │
│   {                              │
│     "entity_type": "EMAIL",      │
│     "start": 0,                  │
│     "end": 11,                   │
│     "score": 0.98                │
│   }                              │
│ ]                                │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Security Plugin                  │
│ if redact_pii:                   │
│   text = "<EMAIL>"               │
│ else:                            │
│   check_policy()                 │
└──────────────────────────────────┘
```

### Policy Evaluation Flow

```
┌──────────────┐
│ Request Data │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│ Build OPA Input                  │
│ {                                │
│   "request": {...},              │
│   "context": {...},              │
│   "security": {...}              │
│ }                                │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ OPA Engine                       │
│ Load policies/*.rego             │
│ Evaluate rules                   │
└──────┬───────────────────────────┘
       │
       ├─▶ Check deny rules
       │   ├─▶ threat_score > 0.75?
       │   ├─▶ PII detected?
       │   ├─▶ Unapproved provider?
       │   └─▶ ...
       │
       ├─▶ If any deny rule matches:
       │   └─▶ allow = false
       │
       └─▶ If no deny rules match:
           └─▶ allow = true
       │
       ▼
┌──────────────────────────────────┐
│ Policy Decision                  │
│ {                                │
│   "allow": false,                │
│   "reason": "SSN detected",      │
│   "status_code": 403             │
│ }                                │
└──────────────────────────────────┘
```

## Data Flow

### Request Data Structure

```json
{
  "request": {
    "prompt": "User's prompt text",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "tools": ["read_file", "search"],
    "max_tokens": 100
  },
  "context": {
    "user_id": "user-123",
    "user_role": "user",
    "session_id": "session-456",
    "timestamp": 1704067200,
    "ip_address": "192.168.1.1"
  },
  "security": {
    "threat_score": 0.15,
    "pii_detected": true,
    "pii_entities": [
      {
        "type": "EMAIL",
        "text": "test@example.com",
        "start": 10,
        "end": 26,
        "score": 0.98
      }
    ]
  }
}
```

### Tool Validation Data Structure

```json
{
  "tool_name": "read_file",
  "tool_arguments": {
    "path": "/workspace/data.txt"
  },
  "context": {
    "user_id": "user-123",
    "user_role": "developer"
  }
}
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Network Security                                   │
│ - HTTPS/TLS                                                 │
│ - Rate limiting                                             │
│ - IP whitelisting                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Authentication & Authorization                     │
│ - API key validation                                        │
│ - User role verification                                    │
│ - Session management                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Input Validation (Security Plugin)                │
│ - PII detection                                             │
│ - Prompt injection detection                                │
│ - Input sanitization                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Policy Enforcement (OPA)                          │
│ - Request validation                                        │
│ - Tool validation                                           │
│ - Resource access control                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: Audit & Monitoring                                │
│ - Security event logging                                    │
│ - Metrics collection                                        │
│ - Alerting                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Test Coverage Map

```
┌─────────────────────────────────────────────────────────────┐
│                     Security Features                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PII Detection                                              │
│  ├─▶ Test 2: Email detection          ✓                   │
│  ├─▶ Test 3: SSN blocking             ✓                   │
│  └─▶ Test 4: Multiple PII             ✓                   │
│                                                             │
│  Prompt Injection                                           │
│  └─▶ Test 5: Injection attempt        ✓                   │
│                                                             │
│  Tool Validation                                            │
│  ├─▶ Test 6: Allowed tool             ✓                   │
│  ├─▶ Test 7: Denied tool              ✓                   │
│  ├─▶ Test 8: Dangerous command        ✓                   │
│  └─▶ Test 9: Path traversal           ✓                   │
│                                                             │
│  Policy Enforcement                                         │
│  ├─▶ Test 1: Normal request           ✓                   │
│  └─▶ Test 10: Unapproved provider     ✓                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Performance Characteristics

```
Request Latency Breakdown:

Normal Request (no security issues):
├─ Network: 5-10ms
├─ Security Plugin: 50-100ms
│  ├─ PII Detection: 20-40ms
│  ├─ Injection Detection: 10-20ms
│  └─ Policy Evaluation: 5-10ms
├─ LLM Provider: 500-2000ms
└─ Total: ~600-2100ms

Blocked Request (security issue detected):
├─ Network: 5-10ms
├─ Security Plugin: 50-100ms
│  ├─ PII Detection: 20-40ms (if PII found, stop here)
│  ├─ Injection Detection: 10-20ms (if threat found, stop here)
│  └─ Policy Evaluation: 5-10ms
└─ Total: ~60-110ms (no LLM call)

Security overhead: ~50-100ms per request (2-5% of total latency)
```

## Deployment Architecture

```
Production Deployment:

┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Bifrost  │  │ Bifrost  │  │ Bifrost  │
│ Instance │  │ Instance │  │ Instance │
│    1     │  │    2     │  │    3     │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Presidio │  │ Presidio │  │ Presidio │
│ Analyzer │  │ Analyzer │  │ Analyzer │
│    1     │  │    2     │  │    3     │
└──────────┘  └──────────┘  └──────────┘

Shared Services:
├─ Redis (session cache)
├─ PostgreSQL (audit logs)
└─ Prometheus (metrics)
```

---

This architecture provides:
- ✅ Defense in depth
- ✅ Minimal latency overhead
- ✅ Horizontal scalability
- ✅ Comprehensive audit trail
- ✅ Policy-based security
