# Requirements Document: AI Security Integration for Bifrost LLM Gateway

## Introduction

This document specifies the requirements for integrating AI security capabilities into Bifrost's LLM Gateway as a middleware plugin. The security layer uses Open Policy Agent (OPA) Go SDK as an embedded library, along with PII detection (Presidio-inspired) and prompt injection detection (Lakera-inspired). The security plugin intercepts all AI traffic to prevent privilege escalation, tool misuse, prompt injection, memory poisoning, and other agentic vulnerabilities.

## Glossary

- **SecurityPlugin**: The Bifrost plugin that implements all security functionality
- **PolicyEngine**: Component that evaluates Rego policies using OPA Go SDK
- **PIIDetector**: Component that identifies and redacts personally identifiable information
- **PromptInjectionDetector**: Component that detects malicious prompt injection attempts
- **MemoryMonitor**: Component that tracks and validates memory operations
- **BifrostContext**: Request context object passed through Bifrost's plugin pipeline
- **HTTPRequest**: HTTP request object containing LLM request data
- **BifrostResponse**: Response object containing LLM response data
- **MCPRequest**: Request object for MCP tool execution
- **ToolCall**: Object representing a tool invocation from an LLM
- **PIIEntity**: Detected personally identifiable information with type, location, and confidence score
- **ThreatScore**: Float value between 0.0 and 1.0 indicating probability of malicious content
- **PolicyDecision**: Result of policy evaluation indicating allow/deny with reason
- **AuditEntry**: Log record of security decision with full context
- **PreparedEvalQuery**: Compiled OPA policy ready for evaluation
- **RegoPolicy**: Policy written in Rego language loaded from .rego files

## Requirements

### Requirement 1: Plugin Initialization and Configuration

**User Story:** As a system administrator, I want to configure the security plugin with appropriate settings, so that I can control security enforcement behavior.

#### Acceptance Criteria

1. WHEN the SecurityPlugin is initialized, THE SecurityPlugin SHALL load configuration from SecurityConfig
2. WHEN configuration specifies a PolicyPath, THE SecurityPlugin SHALL load all .rego policy files from that directory
3. WHEN configuration enables PII detection, THE SecurityPlugin SHALL initialize the PIIDetector with specified entity types
4. WHEN configuration enables prompt injection detection, THE SecurityPlugin SHALL initialize the PromptInjectionDetector
5. WHEN configuration enables memory poisoning detection, THE SecurityPlugin SHALL initialize the MemoryMonitor
6. WHEN configuration is invalid, THE SecurityPlugin SHALL return a descriptive error and refuse to initialize
7. THE SecurityPlugin SHALL validate that all required configuration fields are present and within valid ranges

### Requirement 2: OPA Policy Engine Integration

**User Story:** As a security engineer, I want to define security policies in Rego, so that I can enforce custom access control rules.

#### Acceptance Criteria

1. THE PolicyEngine SHALL use the OPA Go SDK (github.com/open-policy-agent/opa/rego) as an embedded library
2. WHEN loading a policy file, THE PolicyEngine SHALL read .rego files from the local filesystem
3. WHEN loading a policy file, THE PolicyEngine SHALL compile it using rego.New() and rego.PrepareForEval()
4. WHEN a policy is compiled, THE PolicyEngine SHALL cache the PreparedEvalQuery for reuse
5. WHEN evaluating a policy, THE PolicyEngine SHALL use rego.Eval() with input data
6. WHEN policy evaluation completes, THE PolicyEngine SHALL parse the ResultSet into a PolicyDecision
7. WHEN policy evaluation exceeds 100ms, THE PolicyEngine SHALL timeout and return a deny decision
8. WHEN policy compilation fails, THE PolicyEngine SHALL log the error and return a deny decision
9. WHEN policy evaluation fails, THE PolicyEngine SHALL log the error and return a deny decision
10. THE PolicyEngine SHALL support reloading policies without restarting the process

### Requirement 3: HTTP Transport Request Interception

**User Story:** As a security operator, I want all incoming HTTP requests to be scanned for threats, so that malicious requests are blocked before reaching the LLM.

#### Acceptance Criteria

1. WHEN an HTTP request arrives, THE SecurityPlugin SHALL execute HTTPTransportPreHook before any other processing
2. WHEN prompt injection detection is enabled, THE SecurityPlugin SHALL extract the prompt and calculate a ThreatScore
3. WHEN the ThreatScore exceeds the configured threshold, THE SecurityPlugin SHALL return an HTTP 403 response and block the request
4. WHEN PII detection is enabled, THE SecurityPlugin SHALL scan the prompt for PIIEntity instances
5. WHEN PII is detected and redaction is enabled, THE SecurityPlugin SHALL replace PIIEntity text with placeholders
6. WHEN policy enforcement is enabled, THE SecurityPlugin SHALL evaluate the request against loaded policies
7. WHEN a policy denies the request, THE SecurityPlugin SHALL return an HTTP 403 response with the policy reason
8. WHEN all security checks pass, THE SecurityPlugin SHALL return nil to continue the request pipeline
9. WHEN security processing encounters an error, THE SecurityPlugin SHALL log the error and block the request
10. THE SecurityPlugin SHALL create an AuditEntry for every security decision

### Requirement 4: LLM Response Validation

**User Story:** As a security operator, I want LLM responses to be validated for dangerous tool calls, so that the LLM cannot execute unauthorized operations.

#### Acceptance Criteria

1. WHEN an LLM response is received, THE SecurityPlugin SHALL execute PostLLMHook
2. WHEN the response contains tool calls, THE SecurityPlugin SHALL extract all ToolCall instances
3. WHEN a ToolCall name is in the DeniedTools list, THE SecurityPlugin SHALL block that tool call
4. WHEN AllowedTools is configured and a ToolCall name is not in the list, THE SecurityPlugin SHALL block that tool call
5. WHEN tool validation is enabled, THE SecurityPlugin SHALL evaluate each ToolCall against tool policies
6. WHEN a tool policy denies a ToolCall, THE SecurityPlugin SHALL add it to the blocked tools list
7. WHEN any tools are blocked, THE SecurityPlugin SHALL return a BifrostError with AllowFallbacks set to false
8. WHEN the response contains PII and redaction is enabled, THE SecurityPlugin SHALL redact the PII from the response
9. WHEN all tool calls are allowed, THE SecurityPlugin SHALL return the original response unmodified
10. THE SecurityPlugin SHALL create an AuditEntry with tool validation results

### Requirement 5: MCP Tool Execution Security

**User Story:** As a security operator, I want MCP tool executions to be validated, so that agents cannot execute dangerous operations.

#### Acceptance Criteria

1. WHEN an MCP tool execution is requested, THE SecurityPlugin SHALL execute PreMCPHook
2. WHEN the tool name is in the DeniedTools list, THE SecurityPlugin SHALL return an MCPPluginShortCircuit to block execution
3. WHEN AllowedTools is configured and the tool name is not in the list, THE SecurityPlugin SHALL block execution
4. WHEN tool arguments contain PII and redaction is enabled, THE SecurityPlugin SHALL redact the PII from arguments
5. WHEN the tool is a memory write operation, THE MemoryMonitor SHALL increment the write counter for the session
6. WHEN the write counter exceeds MaxMemoryWrites, THE SecurityPlugin SHALL block the memory write
7. WHEN policy enforcement is enabled, THE SecurityPlugin SHALL evaluate the tool execution against tool policies
8. WHEN a policy denies the tool execution, THE SecurityPlugin SHALL return an MCPPluginShortCircuit with the policy reason
9. WHEN all security checks pass, THE SecurityPlugin SHALL return the original request to continue execution
10. THE SecurityPlugin SHALL create an AuditEntry for every tool execution decision

### Requirement 6: Prompt Injection Detection

**User Story:** As a security operator, I want malicious prompt injection attempts to be detected and blocked, so that attackers cannot manipulate the LLM's behavior.

#### Acceptance Criteria

1. WHEN analyzing a prompt, THE PromptInjectionDetector SHALL scan for known injection patterns using compiled regex
2. WHEN a pattern matches, THE PromptInjectionDetector SHALL assign a severity score based on the pattern type
3. WHEN ML model inference is enabled, THE PromptInjectionDetector SHALL tokenize the prompt and extract features
4. WHEN ML features are extracted, THE PromptInjectionDetector SHALL run model inference to calculate an ML score
5. WHEN both pattern and ML scores are available, THE PromptInjectionDetector SHALL combine them using weighted average
6. THE PromptInjectionDetector SHALL return a ThreatScore between 0.0 and 1.0
7. WHEN the ThreatScore is calculated, THE PromptInjectionDetector SHALL complete processing in under 10ms for pattern-only mode
8. WHEN ML inference is used, THE PromptInjectionDetector SHALL complete processing in under 20ms
9. THE PromptInjectionDetector SHALL maintain a library of injection patterns covering common attack vectors
10. WHEN ML model loading fails, THE PromptInjectionDetector SHALL fall back to pattern-based detection only

### Requirement 7: PII Detection and Redaction

**User Story:** As a compliance officer, I want personally identifiable information to be detected and redacted, so that sensitive data is not sent to LLM providers.

#### Acceptance Criteria

1. WHEN analyzing text, THE PIIDetector SHALL run all enabled entity recognizers in parallel
2. WHEN a recognizer matches an entity, THE PIIDetector SHALL create a PIIEntity with type, text, position, and confidence score
3. WHEN multiple recognizers detect overlapping entities, THE PIIDetector SHALL keep the entity with the highest confidence score
4. THE PIIDetector SHALL support detection of EMAIL, PHONE, SSN, CREDIT_CARD, IP_ADDRESS, and LOCATION entity types
5. WHEN redacting PII, THE PIIDetector SHALL replace entity text with type-specific placeholders (e.g., [EMAIL], [SSN])
6. WHEN redacting PII, THE PIIDetector SHALL process entities in reverse order to preserve text indices
7. THE PIIDetector SHALL return both the redacted text and the list of detected entities
8. WHEN PII detection encounters an error, THE PIIDetector SHALL log a warning and return an empty entity list
9. THE PIIDetector SHALL complete detection and redaction in under 15ms for typical prompts (< 1000 characters)
10. THE PIIDetector SHALL preserve text structure (line breaks, formatting) during redaction

### Requirement 8: Memory Poisoning Detection

**User Story:** As a security operator, I want memory write operations to be validated for malicious content, so that attackers cannot persist malicious instructions.

#### Acceptance Criteria

1. WHEN a memory write is requested, THE MemoryMonitor SHALL retrieve the write count for the session
2. WHEN the write count exceeds MaxMemoryWrites, THE MemoryMonitor SHALL block the write and return a rate limit error
3. WHEN a memory write is allowed, THE MemoryMonitor SHALL increment the write counter atomically
4. WHEN analyzing memory content, THE MemoryMonitor SHALL use the PromptInjectionDetector to calculate a ThreatScore
5. WHEN the ThreatScore exceeds the memory threat threshold, THE MemoryMonitor SHALL block the write
6. WHEN memory content contains privilege escalation patterns, THE MemoryMonitor SHALL block the write
7. WHEN policy enforcement is enabled, THE MemoryMonitor SHALL evaluate the memory write against memory policies
8. WHEN a policy denies the memory write, THE MemoryMonitor SHALL return the policy reason
9. WHEN all checks pass, THE MemoryMonitor SHALL return false for isPoisoned
10. THE MemoryMonitor SHALL maintain per-session write counters with thread-safe access

### Requirement 9: Policy Input Data Construction

**User Story:** As a security engineer, I want comprehensive context passed to policies, so that policies can make informed decisions.

#### Acceptance Criteria

1. WHEN building policy input for a request, THE PolicyEngine SHALL include the prompt text
2. WHEN building policy input for a request, THE PolicyEngine SHALL include the provider and model names
3. WHEN building policy input for a request, THE PolicyEngine SHALL include the list of requested tools
4. WHEN building policy input for a request, THE PolicyEngine SHALL include user_id, session_id, and user_role from BifrostContext
5. WHEN building policy input for a request, THE PolicyEngine SHALL include the current timestamp
6. WHEN building policy input for a request, THE PolicyEngine SHALL include the calculated ThreatScore
7. WHEN building policy input for a request, THE PolicyEngine SHALL include the list of detected PIIEntity instances
8. WHEN building policy input for a tool call, THE PolicyEngine SHALL include the tool name and arguments
9. WHEN building policy input for a memory operation, THE PolicyEngine SHALL include the operation type, key, value, and write count
10. THE PolicyEngine SHALL serialize policy input to JSON format compatible with OPA evaluation

### Requirement 10: Audit Logging

**User Story:** As a security auditor, I want comprehensive logs of all security decisions, so that I can investigate incidents and ensure compliance.

#### Acceptance Criteria

1. WHEN a security decision is made, THE SecurityPlugin SHALL create an AuditEntry with timestamp and request_id
2. WHEN creating an AuditEntry, THE SecurityPlugin SHALL include the decision (allow/block) and reason
3. WHEN creating an AuditEntry, THE SecurityPlugin SHALL include the ThreatScore if calculated
4. WHEN creating an AuditEntry, THE SecurityPlugin SHALL include the list of detected PIIEntity instances
5. WHEN creating an AuditEntry, THE SecurityPlugin SHALL include the list of blocked tools if any
6. WHEN creating an AuditEntry, THE SecurityPlugin SHALL include all policy evaluation results
7. WHEN creating an AuditEntry, THE SecurityPlugin SHALL include the processing latency in milliseconds
8. WHEN creating an AuditEntry, THE SecurityPlugin SHALL include the provider and model names
9. THE SecurityPlugin SHALL write AuditEntry instances to the configured audit log path
10. THE SecurityPlugin SHALL write audit logs asynchronously to avoid blocking the request path

### Requirement 11: Performance and Latency

**User Story:** As a system operator, I want security processing to have minimal latency impact, so that user experience is not degraded.

#### Acceptance Criteria

1. THE SecurityPlugin SHALL complete all security processing in under 50ms at p99
2. WHEN pattern-based prompt injection detection is used, THE PromptInjectionDetector SHALL complete in under 10ms
3. WHEN ML-based prompt injection detection is used, THE PromptInjectionDetector SHALL complete in under 20ms
4. WHEN detecting PII, THE PIIDetector SHALL complete in under 15ms for prompts under 1000 characters
5. WHEN evaluating a policy, THE PolicyEngine SHALL complete in under 100ms or timeout
6. THE SecurityPlugin SHALL pre-compile all regex patterns at initialization to avoid runtime compilation
7. THE SecurityPlugin SHALL cache compiled PreparedEvalQuery instances to avoid recompilation
8. THE SecurityPlugin SHALL use object pooling for frequently allocated objects to reduce GC pressure
9. THE SecurityPlugin SHALL run independent security checks in parallel where possible
10. THE SecurityPlugin SHALL expose latency metrics for each security component

### Requirement 12: Error Handling and Graceful Degradation

**User Story:** As a system operator, I want the security plugin to handle errors gracefully, so that transient failures don't cause complete service outages.

#### Acceptance Criteria

1. WHEN PII detection fails, THE SecurityPlugin SHALL log a warning and continue without redaction
2. WHEN ML model inference fails, THE PromptInjectionDetector SHALL fall back to pattern-based detection
3. WHEN policy evaluation times out, THE PolicyEngine SHALL return a deny decision
4. WHEN policy compilation fails, THE PolicyEngine SHALL log the error and return a deny decision
5. WHEN a security check encounters an unexpected error, THE SecurityPlugin SHALL log the error and block the request
6. WHEN audit log writing fails, THE SecurityPlugin SHALL log the error but continue processing the request
7. WHEN metrics collection fails, THE SecurityPlugin SHALL log the error but continue processing the request
8. THE SecurityPlugin SHALL never panic in production code
9. THE SecurityPlugin SHALL use defer blocks to ensure resource cleanup on errors
10. THE SecurityPlugin SHALL set AllowFallbacks to false for all security-related errors

### Requirement 13: Metrics and Observability

**User Story:** As a system operator, I want comprehensive metrics on security operations, so that I can monitor system health and detect anomalies.

#### Acceptance Criteria

1. THE SecurityPlugin SHALL expose a counter metric for total requests processed with decision labels (allow/block)
2. THE SecurityPlugin SHALL expose a counter metric for threats detected with type labels (prompt_injection, tool_misuse, memory_poisoning)
3. THE SecurityPlugin SHALL expose a counter metric for PII entities found with entity_type labels
4. THE SecurityPlugin SHALL expose a counter metric for tool calls blocked with tool_name labels
5. THE SecurityPlugin SHALL expose a histogram metric for security processing latency with component labels
6. THE SecurityPlugin SHALL expose a counter metric for policy evaluations with policy and decision labels
7. THE SecurityPlugin SHALL increment metrics atomically to ensure accuracy under concurrent load
8. THE SecurityPlugin SHALL expose metrics in Prometheus format
9. THE SecurityPlugin SHALL update metrics for every request regardless of decision
10. THE SecurityPlugin SHALL expose metrics for policy evaluation errors and timeouts

### Requirement 14: Configuration Validation

**User Story:** As a system administrator, I want configuration errors to be detected early, so that I don't deploy a misconfigured system.

#### Acceptance Criteria

1. WHEN validating configuration, THE SecurityPlugin SHALL verify that PolicyPath exists and is readable
2. WHEN validating configuration, THE SecurityPlugin SHALL verify that ThreatScoreThreshold is between 0.0 and 1.0
3. WHEN validating configuration, THE SecurityPlugin SHALL verify that MaxMemoryWrites is a positive integer
4. WHEN validating configuration, THE SecurityPlugin SHALL verify that PIIEntityTypes contains only supported types
5. WHEN validating configuration, THE SecurityPlugin SHALL verify that AuditLogPath is writable
6. WHEN validating configuration, THE SecurityPlugin SHALL verify that AllowedTools and DeniedTools do not overlap
7. WHEN configuration is invalid, THE SecurityPlugin SHALL return a descriptive error listing all validation failures
8. WHEN configuration is valid, THE SecurityPlugin SHALL log the active configuration settings
9. THE SecurityPlugin SHALL provide default values for optional configuration fields
10. THE SecurityPlugin SHALL document all configuration fields with examples

### Requirement 15: Policy Reload Without Restart

**User Story:** As a security engineer, I want to update policies without restarting Bifrost, so that I can respond quickly to new threats.

#### Acceptance Criteria

1. THE PolicyEngine SHALL support reloading policies via an API call or signal
2. WHEN reloading policies, THE PolicyEngine SHALL scan the PolicyPath for .rego files
3. WHEN reloading policies, THE PolicyEngine SHALL compile new policies without blocking active requests
4. WHEN new policies are compiled, THE PolicyEngine SHALL atomically swap the policy cache
5. WHEN policy reload fails, THE PolicyEngine SHALL keep the existing policies active and log the error
6. WHEN policy reload succeeds, THE PolicyEngine SHALL log the number of policies loaded
7. THE PolicyEngine SHALL detect file changes using filesystem watchers (optional)
8. THE PolicyEngine SHALL validate new policies before activating them
9. THE PolicyEngine SHALL expose a metric for policy reload attempts and successes
10. THE PolicyEngine SHALL complete policy reload in under 1 second for typical policy sets

### Requirement 16: Streaming Response Security

**User Story:** As a security operator, I want streaming LLM responses to be scanned for threats, so that malicious content is not streamed to users.

#### Acceptance Criteria

1. WHEN a streaming response chunk is received, THE SecurityPlugin SHALL execute HTTPTransportStreamChunkHook
2. WHEN scanning a chunk, THE SecurityPlugin SHALL check for PII entities
3. WHEN PII is detected in a chunk and redaction is enabled, THE SecurityPlugin SHALL redact the PII before streaming
4. WHEN a chunk contains a partial tool call, THE SecurityPlugin SHALL buffer it until the complete tool call is received
5. WHEN a complete tool call is received, THE SecurityPlugin SHALL validate it against tool policies
6. WHEN a tool call is blocked, THE SecurityPlugin SHALL terminate the stream and return an error
7. THE SecurityPlugin SHALL maintain streaming state across chunks for the same request
8. THE SecurityPlugin SHALL clean up streaming state when the stream completes or errors
9. THE SecurityPlugin SHALL process streaming chunks with minimal latency to avoid buffering delays
10. THE SecurityPlugin SHALL create an AuditEntry for streaming requests with chunk count and total bytes

### Requirement 17: CVE-Based Attack Prevention

**User Story:** As a security operator, I want protection against known CVE attack patterns, so that the system is resilient to documented vulnerabilities.

#### Acceptance Criteria

1. WHEN detecting indirect prompt injection (CVE-2025-32711 EchoLeak), THE SecurityPlugin SHALL validate memory writes from tool outputs
2. WHEN detecting command injection (CVE-2025-53773 GitHub Copilot RCE), THE SecurityPlugin SHALL scan generated code for dangerous patterns
3. WHEN detecting privilege escalation (CVE-2025-12420 ServiceNow), THE SecurityPlugin SHALL block memory writes that modify roles or permissions
4. THE SecurityPlugin SHALL maintain a pattern library for known CVE attack signatures
5. WHEN a CVE pattern is detected, THE SecurityPlugin SHALL log the CVE identifier in the AuditEntry
6. THE SecurityPlugin SHALL support adding new CVE patterns without code changes
7. THE SecurityPlugin SHALL test CVE prevention using realistic attack scenarios
8. THE SecurityPlugin SHALL document which CVEs are covered by the security controls
9. THE SecurityPlugin SHALL expose metrics for CVE-specific detections
10. THE SecurityPlugin SHALL allow security engineers to tune CVE detection sensitivity

### Requirement 18: Concurrent Request Handling

**User Story:** As a system operator, I want the security plugin to handle concurrent requests safely, so that race conditions don't cause security bypasses.

#### Acceptance Criteria

1. THE SecurityPlugin SHALL use mutexes or atomic operations for all shared state access
2. THE MemoryMonitor SHALL use thread-safe data structures for write counters
3. THE PolicyEngine SHALL use sync.Map or RWMutex for policy cache access
4. THE SecurityPlugin SHALL avoid data races verified by running tests with -race flag
5. THE SecurityPlugin SHALL support at least 5000 concurrent requests without deadlocks
6. THE SecurityPlugin SHALL use goroutine pools to limit concurrent goroutine creation
7. THE SecurityPlugin SHALL use buffered channels for async operations with backpressure handling
8. THE SecurityPlugin SHALL document thread-safety guarantees for all public methods
9. THE SecurityPlugin SHALL use context cancellation to clean up abandoned requests
10. THE SecurityPlugin SHALL test concurrent behavior with property-based tests

### Requirement 19: Security Plugin Lifecycle

**User Story:** As a system operator, I want the security plugin to initialize and shutdown cleanly, so that resources are properly managed.

#### Acceptance Criteria

1. WHEN initializing, THE SecurityPlugin SHALL load all policies before accepting requests
2. WHEN initializing, THE SecurityPlugin SHALL validate configuration before loading components
3. WHEN initializing, THE SecurityPlugin SHALL pre-compile all regex patterns
4. WHEN initializing, THE SecurityPlugin SHALL load ML models if enabled
5. WHEN initializing fails, THE SecurityPlugin SHALL return a descriptive error and clean up partial state
6. WHEN shutting down, THE SecurityPlugin SHALL flush all pending audit log entries
7. WHEN shutting down, THE SecurityPlugin SHALL close all open file handles
8. WHEN shutting down, THE SecurityPlugin SHALL wait for in-flight requests to complete with timeout
9. WHEN shutting down, THE SecurityPlugin SHALL unregister metrics collectors
10. THE SecurityPlugin SHALL expose health check endpoints indicating readiness

### Requirement 20: Tool Argument Validation

**User Story:** As a security operator, I want tool arguments to be validated for malicious content, so that attackers cannot inject commands via tool parameters.

#### Acceptance Criteria

1. WHEN validating tool arguments, THE SecurityPlugin SHALL scan string arguments for PII
2. WHEN validating tool arguments, THE SecurityPlugin SHALL scan string arguments for injection patterns
3. WHEN validating file path arguments, THE SecurityPlugin SHALL check for path traversal attempts
4. WHEN validating command arguments, THE SecurityPlugin SHALL check for shell injection patterns
5. WHEN validating URL arguments, THE SecurityPlugin SHALL check for SSRF attempts
6. WHEN dangerous content is detected in arguments, THE SecurityPlugin SHALL block the tool execution
7. THE SecurityPlugin SHALL support custom validation rules per tool type
8. THE SecurityPlugin SHALL redact PII from tool arguments if redaction is enabled
9. THE SecurityPlugin SHALL log all argument validation failures in the AuditEntry
10. THE SecurityPlugin SHALL complete argument validation in under 5ms per tool call
