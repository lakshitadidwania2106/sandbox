package security

import (
	"github.com/maximhq/bifrost/core/schemas"
)

// SecurityDecision represents the result of security evaluation
type SecurityDecision struct {
	Allow        bool
	Reason       string
	ThreatScore  float64
	PIIEntities  []PIIEntity
	BlockedTools []string
}

// PIIEntity represents detected PII
type PIIEntity struct {
	Type  string  `json:"type"`  // "EMAIL", "PHONE", "SSN", "CREDIT_CARD", etc.
	Text  string  `json:"text"`
	Start int     `json:"start"`
	End   int     `json:"end"`
	Score float64 `json:"score"`
}

// ToolCall represents a tool invocation from an LLM
type ToolCall struct {
	Name      string                 `json:"name"`
	Arguments map[string]interface{} `json:"arguments"`
}

// extractToolCalls extracts tool calls from a Bifrost response
func extractToolCalls(resp *schemas.BifrostResponse) []ToolCall {
	return nil
}
