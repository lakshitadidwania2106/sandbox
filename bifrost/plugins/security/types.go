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
// TODO: Fix this function - ChatCompletion field doesn't exist on BifrostResponse
/*
func extractToolCalls(resp *schemas.BifrostResponse) []ToolCall {
	var toolCalls []ToolCall

	// Handle different response types
	if resp.ChatCompletion != nil {
		for _, choice := range resp.ChatCompletion.Choices {
			if choice.Message.ToolCalls != nil {
				for _, tc := range choice.Message.ToolCalls {
					toolCalls = append(toolCalls, ToolCall{
						Name:      tc.Function.Name,
						Arguments: tc.Function.Arguments,
					})
				}
			}
		}
	}

	return toolCalls
}
*/
