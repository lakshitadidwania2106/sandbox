// Package security provides OPA-based security policy enforcement for Bifrost
package security

import (
	"fmt"
	"os"
)

// SecurityConfig holds all security configuration
type SecurityConfig struct {
	// Policy enforcement
	EnablePolicyEnforcement bool   `json:"enable_policy_enforcement"`
	PolicyPath              string `json:"policy_path"`

	// PII detection
	EnablePIIDetection bool     `json:"enable_pii_detection"`
	RedactPII          bool     `json:"redact_pii"`
	PIIEntityTypes     []string `json:"pii_entity_types"`
	PresidioURL        string   `json:"presidio_url"`

	// Prompt injection detection
	EnablePromptInjection bool    `json:"enable_prompt_injection"`
	ThreatScoreThreshold  float64 `json:"threat_score_threshold"`
	LakeraAPIKey          string  `json:"lakera_api_key"`

	// Memory poisoning detection
	EnableMemoryPoisoning  bool `json:"enable_memory_poisoning"`
	MaxMemoryWrites        int  `json:"max_memory_writes"`
	MemoryThreatThreshold  float64 `json:"memory_threat_threshold"`

	// Tool validation
	EnableToolValidation bool     `json:"enable_tool_validation"`
	AllowedTools         []string `json:"allowed_tools"`
	DeniedTools          []string `json:"denied_tools"`

	// Behavior
	BlockOnHighThreat bool `json:"block_on_high_threat"`

	// Audit logging
	AuditLogPath string `json:"audit_log_path"`

	// Hook enablement
	EnableHTTPHooks bool `json:"enable_http_hooks"`
	EnableLLMHooks  bool `json:"enable_llm_hooks"`
	EnableMCPHooks  bool `json:"enable_mcp_hooks"`
}

// DefaultSecurityConfig returns a SecurityConfig with sensible defaults
func DefaultSecurityConfig() *SecurityConfig {
	return &SecurityConfig{
		EnablePolicyEnforcement: true,
		PolicyPath:              "./policies",
		EnablePIIDetection:      true,
		RedactPII:               true,
		PIIEntityTypes:          []string{"EMAIL", "PHONE", "SSN", "CREDIT_CARD", "IP_ADDRESS"},
		PresidioURL:             "http://localhost:5000",
		EnablePromptInjection:   true,
		ThreatScoreThreshold:    0.75,
		EnableMemoryPoisoning:   true,
		MaxMemoryWrites:         100,
		MemoryThreatThreshold:   0.70,
		EnableToolValidation:    true,
		AllowedTools:            []string{},
		DeniedTools:             []string{},
		BlockOnHighThreat:       true,
		AuditLogPath:            "/var/log/bifrost/security.log",
		EnableHTTPHooks:         true,
		EnableLLMHooks:          true,
		EnableMCPHooks:          true,
	}
}

// Validate checks if the configuration is valid
func (c *SecurityConfig) Validate() error {
	if c.EnablePolicyEnforcement {
		if c.PolicyPath == "" {
			return fmt.Errorf("policy_path is required when policy enforcement is enabled")
		}
		if _, err := os.Stat(c.PolicyPath); os.IsNotExist(err) {
			return fmt.Errorf("policy_path does not exist: %s", c.PolicyPath)
		}
	}

	if c.ThreatScoreThreshold < 0.0 || c.ThreatScoreThreshold > 1.0 {
		return fmt.Errorf("threat_score_threshold must be between 0.0 and 1.0")
	}

	if c.MemoryThreatThreshold < 0.0 || c.MemoryThreatThreshold > 1.0 {
		return fmt.Errorf("memory_threat_threshold must be between 0.0 and 1.0")
	}

	if c.MaxMemoryWrites < 0 {
		return fmt.Errorf("max_memory_writes must be non-negative")
	}

	// Check for overlapping allowed/denied tools
	for _, allowed := range c.AllowedTools {
		for _, denied := range c.DeniedTools {
			if allowed == denied {
				return fmt.Errorf("tool '%s' appears in both allowed and denied lists", allowed)
			}
		}
	}

	return nil
}

// PolicyDecision represents the result of a policy evaluation
type PolicyDecision struct {
	Allow      bool   `json:"allow"`
	Reason     string `json:"reason,omitempty"`
	StatusCode int    `json:"status_code,omitempty"`
	ErrorType  string `json:"error_type,omitempty"`
}
