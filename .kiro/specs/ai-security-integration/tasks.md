# Implementation Plan: AI Security Integration for Bifrost

## Overview

This plan implements OPA-based security middleware for Bifrost as an embedded Go library. The security plugin intercepts HTTP requests, LLM responses, and MCP tool calls to enforce policies, detect PII, prevent prompt injection, and block memory poisoning attacks. Implementation uses the OPA Go SDK (`github.com/open-policy-agent/opa/rego`) for in-process policy evaluation with minimal latency.

## Tasks

- [x] 1. Complete PolicyEngine implementation with OPA Go SDK
  - [x] 1.1 Implement policy reload functionality
    - Add ReloadPolicies() method to PolicyEngine
    - Implement atomic policy cache swap using sync.RWMutex
    - Add filesystem watcher for automatic policy reload (optional)
    - _Requirements: 2.10, 15.1-15.10_
  
  - [ ]* 1.2 Write property test for policy evaluation consistency
    - **Property 4: Policy Consistency**
    - **Validates: Requirements 2.1-2.10**
    - Test that identical inputs produce identical policy decisions
  
  - [x] 1.3 Add policy evaluation error handling improvements
    - Handle context.DeadlineExceeded for timeouts
    - Handle topdown.Error for policy errors
    - Return deny decision on all errors with descriptive reasons
    - _Requirements: 2.7-2.9, 12.3-12.4_
  
  - [x] 1.4 Create example .rego policy files
    - Create policies/request_validation.rego for HTTP request validation
    - Create policies/tool_validation.rego for tool call validation
    - Create policies/memory_validation.rego for memory write validation
    - Include comprehensive examples with comments
    - _Requirements: 2.1-2.10_

- [x] 2. Implement PII detection with Presidio HTTP integration
  - [x] 2.1 Create PIIDetector with HTTP client for Presidio service
    - Implement Analyze() method to call Presidio HTTP API at security/presidio_service.py
    - Parse Presidio JSON response into PIIEntity structs
    - Implement entity type filtering based on config.PIIEntityTypes
    - Add timeout and retry logic for HTTP calls
    - _Requirements: 7.1-7.4, 1.4_
  
  - [x] 2.2 Implement PII redaction logic
    - Implement Redact() method to replace PII with placeholders
    - Process entities in reverse order to preserve indices
    - Use type-specific placeholders ([EMAIL], [SSN], [PHONE], etc.)
    - Preserve text structure (line breaks, formatting)
    - _Requirements: 7.5-7.7, 7.10_
  
  - [x] 2.3 Add overlapping entity resolution
    - Implement resolveOverlaps() to keep highest confidence entity
    - Handle nested and overlapping entity spans
    - _Requirements: 7.3_
  
  - [ ]* 2.4 Write property test for PII redaction completeness
    - **Property 2: PII Redaction Completeness**
    - **Validates: Requirements 7.5-7.7**
    - Test that redacted text contains no detected PII entities
  
  - [x]* 2.5 Write unit tests for PII detector
    - Test detection of EMAIL, PHONE, SSN, CREDIT_CARD entity types
    - Test redaction accuracy and placeholder generation
    - Test error handling for Presidio service failures
    - _Requirements: 7.1-7.10_

- [ ] 3. Implement prompt injection detection
  - [ ] 3.1 Create InjectionDetector with pattern-based detection
    - Define InjectionPattern struct with regex, severity, description
    - Implement pattern library for common injection attacks
    - Implement Classify() method using pattern matching
    - Calculate threat score based on pattern severity
    - _Requirements: 6.1-6.3, 6.9_
  
  - [ ] 3.2 Add ML model integration (optional, with graceful fallback)
    - Add ML model loading from ONNX file (optional)
    - Implement feature extraction from prompts
    - Implement model inference with timeout
    - Combine pattern and ML scores using weighted average
    - Fall back to pattern-only if ML fails
    - _Requirements: 6.4-6.5, 6.8, 6.10, 12.2_
  
  - [ ]* 3.3 Write property test for threat detection monotonicity
    - **Property 1: Threat Detection Monotonicity**
    - **Validates: Requirements 6.1-6.6**
    - Test that adding malicious patterns never decreases threat score
  
  - [ ]* 3.4 Write unit tests for injection detector
    - Test pattern matching for known injection techniques
    - Test threat score calculation and thresholding
    - Test ML model fallback behavior
    - _Requirements: 6.1-6.10_

- [ ] 4. Implement memory monitoring and poisoning detection
  - [ ] 4.1 Create MemoryMonitor with write tracking
    - Implement per-session write counter using sync.Map
    - Implement IncrementWriteCount() with atomic operations
    - Implement GetWriteCount() for rate limit checking
    - Add thread-safe counter access
    - _Requirements: 8.1-8.3, 8.10, 18.2_
  
  - [ ] 4.2 Implement memory poisoning detection logic
    - Implement DetectMemoryPoisoning() method
    - Check write count against MaxMemoryWrites threshold
    - Use InjectionDetector to scan memory content for threats
    - Detect privilege escalation patterns in memory writes
    - Evaluate memory writes against OPA policies
    - _Requirements: 8.4-8.8_
  
  - [ ]* 4.3 Write property test for rate limit enforcement
    - **Property 5: Rate Limit Enforcement**
    - **Validates: Requirements 8.1-8.3**
    - Test that write count never exceeds MaxMemoryWrites
  
  - [ ]* 4.4 Write unit tests for memory monitor
    - Test write counter increment and retrieval
    - Test rate limiting enforcement
    - Test memory poisoning detection
    - Test concurrent access safety
    - _Requirements: 8.1-8.10_

- [ ] 5. Implement audit logging
  - [ ] 5.1 Create AuditLogger with async log writing
    - Implement buffered channel for audit entries
    - Implement background goroutine for log writing
    - Add backpressure handling for full buffer
    - Implement graceful shutdown with entry flushing
    - _Requirements: 10.1-10.10, 12.6_
  
  - [ ] 5.2 Implement AuditEntry creation
    - Create LogDecision() method to build audit entries
    - Include timestamp, request_id, decision, reason
    - Include threat_score, pii_entities, blocked_tools
    - Include policy evaluation results and latency
    - _Requirements: 10.1-10.9_
  
  - [ ]* 5.3 Write unit tests for audit logger
    - Test audit entry creation and formatting
    - Test async log writing
    - Test error handling for write failures
    - _Requirements: 10.1-10.10_

- [ ] 6. Implement metrics collection
  - [ ] 6.1 Create SecurityMetrics with Prometheus counters and histograms
    - Implement counter for requests_total with decision labels
    - Implement counter for threats_detected_total with type labels
    - Implement counter for pii_entities_found_total with entity_type labels
    - Implement counter for tool_calls_blocked_total with tool_name labels
    - Implement histogram for security_latency_seconds with component labels
    - _Requirements: 13.1-13.6_
  
  - [ ] 6.2 Add metrics increment methods
    - Implement IncrementRequestsProcessed(decision string)
    - Implement IncrementThreatsDetected(threatType string)
    - Implement IncrementPIIFound(count int)
    - Implement IncrementToolCallsBlocked(count int)
    - Implement RecordLatency(component string, duration time.Duration)
    - Use atomic operations for thread-safe updates
    - _Requirements: 13.7-13.9_
  
  - [ ]* 6.3 Write unit tests for metrics
    - Test metric increment operations
    - Test concurrent metric updates
    - Test Prometheus format export
    - _Requirements: 13.1-13.10_

- [ ] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement tool call validation in PostLLMHook
  - [ ] 8.1 Add extractToolCalls() helper function
    - Parse tool_calls from BifrostResponse
    - Extract tool name and arguments
    - Return slice of ToolCall structs
    - _Requirements: 4.2_
  
  - [ ] 8.2 Enhance validateToolCalls() method
    - Check tool names against DeniedTools list
    - Check tool names against AllowedTools list (if configured)
    - Evaluate each tool call against OPA tool policies
    - Return list of blocked tool names
    - _Requirements: 4.3-4.7_
  
  - [ ] 8.3 Implement tool argument validation
    - Scan string arguments for PII entities
    - Scan arguments for injection patterns
    - Check file paths for traversal attempts
    - Check commands for shell injection
    - Check URLs for SSRF attempts
    - _Requirements: 20.1-20.6_
  
  - [ ]* 8.4 Write unit tests for tool validation
    - Test denied tools blocking
    - Test allowed tools filtering
    - Test policy-based tool validation
    - Test argument validation
    - _Requirements: 4.1-4.10, 20.1-20.10_

- [ ] 9. Implement streaming response security
  - [ ] 9.1 Implement HTTPTransportStreamChunkHook
    - Scan each chunk for PII entities
    - Redact PII from chunks if enabled
    - Buffer partial tool calls until complete
    - Validate complete tool calls against policies
    - Terminate stream if dangerous tool call detected
    - _Requirements: 16.1-16.7_
  
  - [ ] 9.2 Add streaming state management
    - Maintain per-request streaming state
    - Clean up state on stream completion or error
    - Track chunk count and total bytes for audit
    - _Requirements: 16.7-16.10_
  
  - [ ]* 9.3 Write unit tests for streaming security
    - Test chunk-by-chunk PII detection
    - Test partial tool call buffering
    - Test stream termination on policy violation
    - _Requirements: 16.1-16.10_

- [ ] 10. Add CVE-based attack prevention patterns
  - [ ] 10.1 Add CVE-2025-32711 (EchoLeak) detection
    - Add pattern for indirect prompt injection via tool outputs
    - Validate memory writes from tool results
    - Block malicious instructions in tool responses
    - _Requirements: 17.1_
  
  - [ ] 10.2 Add CVE-2025-53773 (GitHub Copilot RCE) detection
    - Add pattern for command injection in code generation
    - Scan generated code for dangerous patterns
    - _Requirements: 17.2_
  
  - [ ] 10.3 Add CVE-2025-12420 (ServiceNow) detection
    - Add pattern for privilege escalation via memory poisoning
    - Block memory writes that modify roles or permissions
    - _Requirements: 17.3_
  
  - [ ]* 10.4 Write CVE-based attack scenario tests
    - Test EchoLeak indirect injection scenario
    - Test Copilot RCE command injection scenario
    - Test ServiceNow privilege escalation scenario
    - _Requirements: 17.1-17.10_

- [ ] 11. Implement configuration validation enhancements
  - [ ] 11.1 Add comprehensive config validation
    - Verify PolicyPath exists and is readable
    - Verify ThreatScoreThreshold is in [0.0, 1.0]
    - Verify MaxMemoryWrites is positive
    - Verify PIIEntityTypes contains only supported types
    - Verify AuditLogPath is writable
    - Verify no overlap between AllowedTools and DeniedTools
    - _Requirements: 14.1-14.7_
  
  - [ ]* 11.2 Write unit tests for config validation
    - Test validation of all config fields
    - Test error messages for invalid configs
    - Test default value assignment
    - _Requirements: 14.1-14.10_

- [ ] 12. Add performance optimizations
  - [ ] 12.1 Implement object pooling for frequently allocated objects
    - Use sync.Pool for SecurityDecision structs
    - Use sync.Pool for PIIEntity slices
    - Use sync.Pool for byte buffers
    - _Requirements: 11.1, 11.7_
  
  - [ ] 12.2 Add policy evaluation caching
    - Implement cache with TTL (60 seconds)
    - Use request fingerprint as cache key (SHA256 hash)
    - Use sync.Map for concurrent cache access
    - _Requirements: 11.3_
  
  - [ ] 12.3 Pre-compile all regex patterns at initialization
    - Compile injection patterns during InjectionDetector init
    - Compile PII recognizer patterns during PIIDetector init
    - Store compiled patterns for reuse
    - _Requirements: 11.1, 11.6_
  
  - [ ]* 12.4 Write performance benchmarks
    - Benchmark prompt injection detection
    - Benchmark PII detection and redaction
    - Benchmark policy evaluation
    - Benchmark full security pipeline
    - Verify p99 latency < 50ms
    - _Requirements: 11.1-11.10_

- [ ] 13. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Create integration tests
  - [ ]* 14.1 Write end-to-end request flow test
    - Test HTTP request → Security plugin → Provider → Response
    - Verify security checks execute at correct hook points
    - Validate audit logs are created
    - Confirm metrics are updated
    - _Requirements: 1.1-20.10_
  
  - [ ]* 14.2 Write plugin hook execution order test
    - Register multiple plugins including security plugin
    - Verify PreLLMHook executes in registration order
    - Verify PostLLMHook executes in reverse order
    - Confirm security plugin can short-circuit pipeline
    - _Requirements: 3.1-3.10_
  
  - [ ]* 14.3 Write MCP tool execution security test
    - Execute MCP tool calls with security plugin active
    - Verify PreMCPHook validates tool calls
    - Confirm blocked tools are prevented from executing
    - Validate PostMCPHook processes tool results
    - _Requirements: 5.1-5.10_
  
  - [ ]* 14.4 Write concurrent request handling test
    - Send 1000 concurrent requests with security enabled
    - Verify no data races (run with -race flag)
    - Verify no deadlocks
    - Test thread-safety of all shared state
    - _Requirements: 18.1-18.10_

- [ ] 15. Create comprehensive documentation
  - [ ] 15.1 Update README.md with plugin overview
    - Document plugin architecture and components
    - Explain OPA Go SDK integration approach
    - List supported security features
    - Provide quick start guide
    - _Requirements: 1.1-20.10_
  
  - [ ] 15.2 Create configuration guide
    - Document all configuration options
    - Provide configuration examples (basic, high-security, dev)
    - Explain configuration validation rules
    - Document default values
    - _Requirements: 14.1-14.10_
  
  - [ ] 15.3 Create policy writing guide
    - Explain Rego policy structure for Bifrost
    - Document input data structure for policies
    - Provide policy examples (request, tool, memory validation)
    - Explain policy query patterns
    - _Requirements: 2.1-2.10, 9.1-9.10_
  
  - [ ] 15.4 Document Presidio service integration
    - Explain HTTP integration with security/presidio_service.py
    - Document expected API format
    - Provide troubleshooting tips
    - _Requirements: 7.1-7.10_

- [ ] 16. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Implementation uses Go with OPA Go SDK as embedded library
- Presidio service already exists at security/presidio_service.py (HTTP integration)
- Focus on OPA integration first, then add PII detection via HTTP calls
