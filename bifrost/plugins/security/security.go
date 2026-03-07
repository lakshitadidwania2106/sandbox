// Package security provides OPA-based security policy enforcement for Bifrost
package security

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/maximhq/bifrost/core/schemas"
)

// SecurityPlugin implements all plugin interfaces for comprehensive security interception
type SecurityPlugin struct {
	config                  *SecurityConfig
	policyEngine            *PolicyEngine
	piiDetector             *PIIDetector
	injectionDetector       *InjectionDetector
	memoryMonitor           *MemoryMonitor
	metrics                 *SecurityMetrics
	auditLogger             *AuditLogger
	logger                  schemas.Logger
}

// NewSecurityPlugin creates a new security plugin instance
func NewSecurityPlugin(config *SecurityConfig, logger schemas.Logger) (*SecurityPlugin, error) {
	if config == nil {
		config = DefaultSecurityConfig()
	}

	if logger == nil {
		return nil, fmt.Errorf("logger is required")
	}

	// Validate configuration
	if err := config.Validate(); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	sp := &SecurityPlugin{
		config: config,
		logger: logger,
	}

	// Initialize policy engine
	if config.EnablePolicyEnforcement {
		policyEngine, err := NewPolicyEngine(config.PolicyPath, logger)
		if err != nil {
			return nil, fmt.Errorf("failed to initialize policy engine: %w", err)
		}
		sp.policyEngine = policyEngine
	}

	// Initialize PII detector
	if config.EnablePIIDetection {
		piiDetector, err := NewPIIDetector(config, logger)
		if err != nil {
			return nil, fmt.Errorf("failed to initialize PII detector: %w", err)
		}
		sp.piiDetector = piiDetector
	}

	// Initialize injection detector
	if config.EnablePromptInjection {
		injectionDetector, err := NewInjectionDetector(config, logger)
		if err != nil {
			return nil, fmt.Errorf("failed to initialize injection detector: %w", err)
		}
		sp.injectionDetector = injectionDetector
	}

	// Initialize memory monitor
	if config.EnableMemoryPoisoning {
		sp.memoryMonitor = NewMemoryMonitor(config, logger)
	}

	// Initialize metrics
	sp.metrics = NewSecurityMetrics()

	// Initialize audit logger
	auditLogger, err := NewAuditLogger(config.AuditLogPath, logger)
	if err != nil {
		return nil, fmt.Errorf("failed to initialize audit logger: %w", err)
	}
	sp.auditLogger = auditLogger

	logger.Info("Security plugin initialized", "config", config)
	return sp, nil
}

// GetName returns the plugin name
func (sp *SecurityPlugin) GetName() string {
	return "security"
}

// Cleanup releases resources
func (sp *SecurityPlugin) Cleanup() error {
	if sp.auditLogger != nil {
		if err := sp.auditLogger.Close(); err != nil {
			sp.logger.Warn("Failed to close audit logger", "error", err)
		}
	}
	return nil
}

// HTTPTransportPreHook intercepts HTTP requests before they enter Bifrost core
func (sp *SecurityPlugin) HTTPTransportPreHook(ctx *schemas.BifrostContext, req *schemas.HTTPRequest) (*schemas.HTTPResponse, error) {
	if !sp.config.EnableHTTPHooks {
		return nil, nil
	}

	// Extract prompt from request body
	prompt, err := extractPromptFromRequest(req.Body)
	if err != nil {
		sp.logger.Warn("Failed to extract prompt from request", "error", err)
		return nil, nil // Continue processing
	}

	if prompt == "" {
		return nil, nil // No prompt to analyze
	}

	// Create security decision
	decision := &SecurityDecision{
		Allow: true,
	}

	// Step 1: Prompt injection detection
	if sp.config.EnablePromptInjection && sp.injectionDetector != nil {
		threatScore, err := sp.injectionDetector.Classify(prompt)
		if err != nil {
			sp.logger.Warn("Prompt injection detection failed", "error", err)
		} else {
			decision.ThreatScore = threatScore
			if threatScore > sp.config.ThreatScoreThreshold {
				decision.Allow = false
				decision.Reason = fmt.Sprintf("Prompt injection detected (score: %.2f)", threatScore)
				sp.metrics.IncrementThreatsDetected("prompt_injection")
				sp.metrics.IncrementRequestsBlocked()
				
				// Create audit entry
				sp.auditLogger.LogDecision(ctx, decision, req)
				
				// Return 403 response
				return &schemas.HTTPResponse{
					StatusCode: http.StatusForbidden,
					Headers:    map[string]string{"Content-Type": "application/json"},
					Body:       []byte(fmt.Sprintf(`{"error": "%s"}`, decision.Reason)),
				}, nil
			}
		}
	}

	// Step 2: PII detection and redaction
	if sp.config.EnablePIIDetection && sp.piiDetector != nil {
		sp.logger.Debug("Starting PII detection", "prompt_len", len(prompt))
		entities, err := sp.piiDetector.Analyze(prompt)
		if err != nil {
			sp.logger.Warn("PII detection failed", "error", err)
		} else {
			sp.logger.Debug("PII detection finished", "entities_found", len(entities))
			decision.PIIEntities = entities
			if len(entities) > 0 {
				sp.metrics.IncrementPIIFound(len(entities))
				
				if sp.config.RedactPII {
					redactedPrompt := sp.piiDetector.Redact(prompt, entities)
					sp.logger.Debug("PII redacted", "redacted_prompt", redactedPrompt)
					// Update request body with redacted prompt
					if err := updateRequestPrompt(req, redactedPrompt); err != nil {
						sp.logger.Warn("Failed to update request with redacted prompt", "error", err)
					}
				}
			}
		}
	} else {
		sp.logger.Info("PII detection skipped", "enabled", sp.config.EnablePIIDetection, "detector_nil", sp.piiDetector == nil)
	}

	// Step 3: Policy evaluation
	if sp.config.EnablePolicyEnforcement && sp.policyEngine != nil {
		policyInput := buildRequestPolicyInput(req, ctx, decision)
		policyDecision, err := sp.policyEngine.EvaluateRequestPolicy(ctx.GetParentCtxWithUserValues(), policyInput)
		if err != nil {
			sp.logger.Error("Policy evaluation failed", "error", err)
			decision.Allow = false
			decision.Reason = "Policy evaluation error"
		} else if !policyDecision.Allow {
			decision.Allow = false
			decision.Reason = policyDecision.Reason
			sp.metrics.IncrementRequestsBlocked()
			
			// Create audit entry
			sp.auditLogger.LogDecision(ctx, decision, req)
			
			// Return 403 response
			statusCode := policyDecision.StatusCode
			if statusCode == 0 {
				statusCode = http.StatusForbidden
			}
			return &schemas.HTTPResponse{
				StatusCode: statusCode,
				Headers:    map[string]string{"Content-Type": "application/json"},
				Body:       []byte(fmt.Sprintf(`{"error": "%s"}`, decision.Reason)),
			}, nil
		}
	}

	// Create audit entry for allowed requests
	sp.auditLogger.LogDecision(ctx, decision, req)
	sp.metrics.IncrementRequestsProcessed("allow")

	return nil, nil // Continue processing
}

// HTTPTransportPostHook intercepts HTTP responses after they exit Bifrost core
func (sp *SecurityPlugin) HTTPTransportPostHook(ctx *schemas.BifrostContext, req *schemas.HTTPRequest, resp *schemas.HTTPResponse) error {
	// Currently no post-processing needed
	return nil
}

// HTTPTransportStreamChunkHook intercepts streaming response chunks
func (sp *SecurityPlugin) HTTPTransportStreamChunkHook(ctx *schemas.BifrostContext, req *schemas.HTTPRequest, chunk *schemas.BifrostStreamChunk) (*schemas.BifrostStreamChunk, error) {
	// Currently no streaming chunk processing needed
	return chunk, nil
}

// PreLLMHook intercepts LLM requests before provider call
func (sp *SecurityPlugin) PreLLMHook(ctx *schemas.BifrostContext, req *schemas.BifrostRequest) (*schemas.BifrostRequest, *schemas.LLMPluginShortCircuit, error) {
	if !sp.config.EnableLLMHooks {
		return req, nil, nil
	}

	// LLM-level security checks can be added here
	return req, nil, nil
}

// PostLLMHook intercepts LLM responses after provider call
func (sp *SecurityPlugin) PostLLMHook(ctx *schemas.BifrostContext, resp *schemas.BifrostResponse, bifrostErr *schemas.BifrostError) (*schemas.BifrostResponse, *schemas.BifrostError, error) {
	if !sp.config.EnableLLMHooks {
		return resp, bifrostErr, nil
	}

	// Skip if response is nil or error already exists
	if resp == nil || bifrostErr != nil {
		return resp, bifrostErr, nil
	}

	// Tool call validation
	if sp.config.EnableToolValidation {
		toolCalls := extractToolCalls(resp)
		if len(toolCalls) > 0 {
			blockedTools, err := sp.validateToolCalls(ctx, toolCalls)
			if err != nil {
				sp.logger.Error("Tool validation failed", "error", err)
			}
			
			if len(blockedTools) > 0 {
				sp.metrics.IncrementToolCallsBlocked(len(blockedTools))
				
				// Create error to block tool execution
				errorType := "security_violation"
				statusCode := http.StatusForbidden
				bifrostErr = &schemas.BifrostError{
					Error: &schemas.ErrorField{
						Message: "Tool execution blocked by security policy",
						Type:    &errorType,
					},
					StatusCode: &statusCode,
					Type:       &errorType,
				}
				allowFallbacks := false
				bifrostErr.AllowFallbacks = &allowFallbacks
				
				return nil, bifrostErr, nil
			}
		}
	}

	return resp, bifrostErr, nil
}

// PreMCPHook intercepts MCP tool execution requests
func (sp *SecurityPlugin) PreMCPHook(ctx *schemas.BifrostContext, req *schemas.BifrostMCPRequest) (*schemas.BifrostMCPRequest, *schemas.MCPPluginShortCircuit, error) {
	if !sp.config.EnableMCPHooks {
		return req, nil, nil
	}

	toolName := req.GetToolName()

	// Check denied tools list
	if contains(sp.config.DeniedTools, toolName) {
		sp.metrics.IncrementToolCallsBlocked(1)
		return nil, &schemas.MCPPluginShortCircuit{
Error: createSecurityError(fmt.Sprintf("Tool '%s' is denied by security policy", toolName)),
}, nil
	}

	// Check allowed tools list
	if len(sp.config.AllowedTools) > 0 && !contains(sp.config.AllowedTools, toolName) {
		sp.metrics.IncrementToolCallsBlocked(1)
		return nil, &schemas.MCPPluginShortCircuit{
Error: createSecurityError(fmt.Sprintf("Tool '%s' is not in allowed tools list", toolName)),
}, nil
	}

	// Memory poisoning detection for memory write operations
	if sp.config.EnableMemoryPoisoning && sp.memoryMonitor != nil {
		if isMemoryWriteOperation(toolName) {
			sessionID := getSessionID(ctx)
			isPoisoned, reason := sp.memoryMonitor.DetectMemoryPoisoning(ctx, req, sessionID)
			if isPoisoned {
				sp.metrics.IncrementThreatsDetected("memory_poisoning")
				return nil, &schemas.MCPPluginShortCircuit{
Error: createSecurityError(reason),
}, nil
			}
		}
	}

	// Policy evaluation for tool execution
	if sp.config.EnablePolicyEnforcement && sp.policyEngine != nil {
		policyInput := buildToolPolicyInput(req, ctx)
		policyDecision, err := sp.policyEngine.EvaluateToolPolicy(ctx.GetParentCtxWithUserValues(), policyInput)
		if err != nil {
			sp.logger.Error("Tool policy evaluation failed", "error", err)
		} else if !policyDecision.Allow {
			sp.metrics.IncrementToolCallsBlocked(1)
			return nil, &schemas.MCPPluginShortCircuit{
Error: createSecurityError(policyDecision.Reason),
}, nil
		}
	}

	return req, nil, nil
}

// PostMCPHook intercepts MCP tool execution responses
func (sp *SecurityPlugin) PostMCPHook(ctx *schemas.BifrostContext, resp *schemas.BifrostMCPResponse, bifrostErr *schemas.BifrostError) (*schemas.BifrostMCPResponse, *schemas.BifrostError, error) {
	// Currently no post-processing needed
	return resp, bifrostErr, nil
}

// validateToolCalls validates tool calls against security policies
func (sp *SecurityPlugin) validateToolCalls(ctx *schemas.BifrostContext, toolCalls []ToolCall) ([]string, error) {
	var blockedTools []string

	for _, toolCall := range toolCalls {
		// Check denied tools
		if contains(sp.config.DeniedTools, toolCall.Name) {
			blockedTools = append(blockedTools, toolCall.Name)
			continue
		}

		// Check allowed tools
		if len(sp.config.AllowedTools) > 0 && !contains(sp.config.AllowedTools, toolCall.Name) {
			blockedTools = append(blockedTools, toolCall.Name)
			continue
		}

		// Policy evaluation
		if sp.policyEngine != nil {
			policyInput := &PolicyInput{
				ToolName:      toolCall.Name,
				ToolArguments: toolCall.Arguments,
			}
			policyDecision, err := sp.policyEngine.EvaluateToolPolicy(ctx.GetParentCtxWithUserValues(), policyInput)
			if err != nil {
				sp.logger.Error("Tool policy evaluation failed", "tool", toolCall.Name, "error", err)
				continue
			}
			if !policyDecision.Allow {
				blockedTools = append(blockedTools, toolCall.Name)
			}
		}
	}

	return blockedTools, nil
}

// Helper functions

func extractPromptFromRequest(body []byte) (string, error) {
	if len(body) == 0 {
		return "", nil
	}

	var payload map[string]interface{}
	if err := json.Unmarshal(body, &payload); err != nil {
		return "", err
	}

	// Try different prompt fields
	if prompt, ok := payload["prompt"].(string); ok {
		return prompt, nil
	}

	// Try messages array (chat completion format)
	if messages, ok := payload["messages"].([]interface{}); ok && len(messages) > 0 {
		if lastMsg, ok := messages[len(messages)-1].(map[string]interface{}); ok {
			if content, ok := lastMsg["content"].(string); ok {
				return content, nil
			}
		}
	}

	return "", nil
}

func updateRequestPrompt(req *schemas.HTTPRequest, redactedPrompt string) error {
	if len(req.Body) == 0 {
		return nil
	}

	var payload map[string]interface{}
	if err := json.Unmarshal(req.Body, &payload); err != nil {
		return err
	}

	// Update prompt field
	if _, ok := payload["prompt"]; ok {
		payload["prompt"] = redactedPrompt
	}

	// Update messages array
	if messages, ok := payload["messages"].([]interface{}); ok && len(messages) > 0 {
		if lastMsg, ok := messages[len(messages)-1].(map[string]interface{}); ok {
			lastMsg["content"] = redactedPrompt
		}
	}

	updatedBody, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	req.Body = updatedBody
	return nil
}

func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

func isMemoryWriteOperation(toolName string) bool {
	memoryWriteTools := []string{"write_memory", "update_memory", "set_memory", "store_memory"}
	return contains(memoryWriteTools, toolName)
}

func getSessionID(ctx *schemas.BifrostContext) string {
	if sessionID, ok := ctx.Value("session-id").(string); ok {
		return sessionID
	}
	return "unknown"
}

// createSecurityError creates a BifrostError for security violations
func createSecurityError(message string) *schemas.BifrostError {
errorType := "security_violation"
statusCode := http.StatusForbidden
allowFallbacks := false

return &schemas.BifrostError{
Error: &schemas.ErrorField{
Message: message,
Type:    &errorType,
},
StatusCode:     &statusCode,
Type:           &errorType,
AllowFallbacks: &allowFallbacks,
}
}
