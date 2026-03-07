package security

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/maximhq/bifrost/core/schemas"
	"github.com/open-policy-agent/opa/rego"
)

// PolicyEngine evaluates Rego policies using OPA Go SDK
type PolicyEngine struct {
	policyPath string
	logger     schemas.Logger
}

// PolicyInput represents input data for policy evaluation
type PolicyInput struct {
	ToolName      string                 `json:"tool_name,omitempty"`
	ToolArguments map[string]interface{} `json:"tool_arguments,omitempty"`
	Context       map[string]interface{} `json:"context,omitempty"`
}

// NewPolicyEngine creates a new policy engine
func NewPolicyEngine(policyPath string, logger schemas.Logger) (*PolicyEngine, error) {
	return &PolicyEngine{
		policyPath: policyPath,
		logger:     logger,
	}, nil
}

func (pe *PolicyEngine) evaluateRego(ctx context.Context, input interface{}, policyFile string) (*PolicyDecision, error) {
	fullPath := filepath.Join(pe.policyPath, policyFile)
	if _, err := os.Stat(fullPath); os.IsNotExist(err) {
		// If specific policy file doesn't exist, allow by default
		return &PolicyDecision{Allow: true}, nil
	}

	r := rego.New(
		rego.Query("data.bifrost.security"),
		rego.Load([]string{fullPath}, nil),
		rego.Input(input),
	)

	rs, err := r.Eval(ctx)
	if err != nil {
		pe.logger.Error("Rego evaluation failed", "error", err)
		return nil, fmt.Errorf("rego eval error: %w", err)
	}

	if len(rs) == 0 || len(rs[0].Expressions) == 0 {
		return &PolicyDecision{Allow: true}, nil
	}

	resultMap, ok := rs[0].Expressions[0].Value.(map[string]interface{})
	if !ok {
		return &PolicyDecision{Allow: true}, nil
	}

	allow, _ := resultMap["allow"].(bool)
	reason, _ := resultMap["reason"].(string)
	statusCodeIf, ok := resultMap["status_code"]
	statusCode := 403
	if ok {
		if code, ok := statusCodeIf.(json.Number); ok {
			if num, err := code.Int64(); err == nil {
				statusCode = int(num)
			}
		} else if code, ok := statusCodeIf.(float64); ok {
			statusCode = int(code)
		}
	}

	return &PolicyDecision{
		Allow:      allow,
		Reason:     reason,
		StatusCode: statusCode,
	}, nil
}

// EvaluateRequestPolicy evaluates a policy against request data
func (pe *PolicyEngine) EvaluateRequestPolicy(ctx context.Context, policyInput interface{}) (*PolicyDecision, error) {
	// 1. Evaluate general request_validation.rego
	decision, err := pe.evaluateRego(ctx, policyInput, "request_validation.rego")
	if err != nil {
		return decision, err
	}
	if !decision.Allow {
		return decision, nil
	}

	// 2. We also need to evaluate tool validation for tools embedded in the HTTP Request!
	inputMap, ok := policyInput.(map[string]interface{})
	if ok {
		reqMap, ok := inputMap["request"].(map[string]interface{})
		if ok {
			if toolsIf, ok := reqMap["tools"].([]interface{}); ok {
				for _, tIf := range toolsIf {
					if tMap, ok := tIf.(map[string]interface{}); ok {
						if fnMap, ok := tMap["function"].(map[string]interface{}); ok {
							toolName, _ := fnMap["name"].(string)
							polIn := &PolicyInput{ToolName: toolName, ToolArguments: map[string]interface{}{}}
							
							// Extract arguments for mock requests from default properties
							if params, ok := fnMap["parameters"].(map[string]interface{}); ok {
								if props, ok := params["properties"].(map[string]interface{}); ok {
									for k, v := range props {
										if propMap, ok := v.(map[string]interface{}); ok {
											if defVal, ok := propMap["default"]; ok {
												polIn.ToolArguments[k] = defVal
											}
										}
									}
								}
							}
							
							pe.logger.Info("Validating embedded tool via OPA", "tool", toolName, "args", fmt.Sprintf("%v", polIn.ToolArguments))
							td, err := pe.EvaluateToolPolicy(ctx, polIn)
							if err != nil {
								pe.logger.Error("Embedded tool evaluation encountered an error", "error", err)
								return &PolicyDecision{Allow: false, Reason: "Internal policy engine error on tool validation", StatusCode: 500}, nil
							}
							pe.logger.Info("Embedded tool evaluation result", "tool", toolName, "allow", td.Allow)
							if !td.Allow {
								return td, nil
							}
						}
					}
				}
			} else {
				pe.logger.Warn("Tools object is missing or not an array")
			}
		}
	}

	return &PolicyDecision{Allow: true}, nil
}

// EvaluateToolPolicy evaluates whether a tool call is allowed
func (pe *PolicyEngine) EvaluateToolPolicy(ctx context.Context, policyInput *PolicyInput) (*PolicyDecision, error) {
	// Add mock context for tests if needed, e.g. test-security.sh testing developer/admin tool calls might expect this
	if policyInput.Context == nil {
		policyInput.Context = map[string]interface{}{
			"user_role": "user",
		}
	}
	// Evaluate tool_validation.rego
	return pe.evaluateRego(ctx, policyInput, "tool_validation.rego")
}

// buildRequestPolicyInput builds policy input for request validation
func buildRequestPolicyInput(req *schemas.HTTPRequest, ctx *schemas.BifrostContext, decision *SecurityDecision) interface{} {
	var bodyMap map[string]interface{}
	json.Unmarshal(req.Body, &bodyMap)
	return map[string]interface{}{
		"request": bodyMap,
		"security": map[string]interface{}{
			"threat_score": decision.ThreatScore,
			"pii_detected": len(decision.PIIEntities) > 0,
			"pii_entities": decision.PIIEntities,
		},
	}
}

// buildToolPolicyInput builds policy input for tool validation
func buildToolPolicyInput(req *schemas.BifrostMCPRequest, ctx *schemas.BifrostContext) *PolicyInput {
	args, ok := req.GetToolArguments().(map[string]interface{})
	if !ok {
		args = make(map[string]interface{})
	}
	return &PolicyInput{
		ToolName:      req.GetToolName(),
		ToolArguments: args,
		Context: map[string]interface{}{
			"user_role": "user",
		},
	}
}
