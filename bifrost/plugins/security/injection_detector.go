package security

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/maximhq/bifrost/core/schemas"
)

// InjectionDetector detects malicious prompt injection attempts
type InjectionDetector struct {
	patterns    []InjectionPattern
	lakeraURL   string
	lakeraKey   string
	client      *http.Client
	logger      schemas.Logger
}

// InjectionPattern represents a prompt injection pattern
type InjectionPattern struct {
	Pattern     string
	Severity    string // "LOW", "MEDIUM", "HIGH", "CRITICAL"
	Description string
	Regex       *regexp.Regexp
}

// NewInjectionDetector creates a new injection detector
func NewInjectionDetector(config *SecurityConfig, logger schemas.Logger) (*InjectionDetector, error) {
	id := &InjectionDetector{
		patterns:  buildInjectionPatterns(),
		lakeraURL: "https://api.lakera.ai/v1/prompt_injection",
		lakeraKey: config.LakeraAPIKey,
		client: &http.Client{
			Timeout: 5 * time.Second,
		},
		logger: logger,
	}

	return id, nil
}

// Classify calculates a threat score for the given prompt
func (id *InjectionDetector) Classify(prompt string) (float64, error) {
	if prompt == "" {
		return 0.0, nil
	}

	// Step 1: Pattern-based detection (fast path)
	patternScore := id.classifyWithPatterns(prompt)

	// Step 2: If Lakera API key is configured, use ML-based detection
	if id.lakeraKey != "" {
		mlScore, err := id.classifyWithLakera(prompt)
		if err != nil {
			id.logger.Warn("Lakera API call failed, using pattern-based score only", "error", err)
			return patternScore, nil
		}

		// Combine scores (weighted average: 40% pattern, 60% ML)
		return (0.4 * patternScore) + (0.6 * mlScore), nil
	}

	return patternScore, nil
}

// classifyWithPatterns performs pattern-based threat detection
func (id *InjectionDetector) classifyWithPatterns(prompt string) float64 {
	maxScore := 0.0
	lowerPrompt := strings.ToLower(prompt)

	for _, pattern := range id.patterns {
		if pattern.Regex.MatchString(lowerPrompt) {
			score := getSeverityScore(pattern.Severity)
			if score > maxScore {
				maxScore = score
			}
		}
	}

	return maxScore
}

// classifyWithLakera performs ML-based threat detection using Lakera API
func (id *InjectionDetector) classifyWithLakera(prompt string) (float64, error) {
	reqBody, err := json.Marshal(map[string]string{
		"input": prompt,
	})
	if err != nil {
		return 0.0, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequest("POST", id.lakeraURL, bytes.NewBuffer(reqBody))
	if err != nil {
		return 0.0, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+id.lakeraKey)

	resp, err := id.client.Do(req)
	if err != nil {
		return 0.0, fmt.Errorf("lakera API request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return 0.0, fmt.Errorf("lakera API error %d: %s", resp.StatusCode, body)
	}

	var result struct {
		Results []struct {
			Flagged bool    `json:"flagged"`
			Score   float64 `json:"score"`
		} `json:"results"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return 0.0, fmt.Errorf("failed to decode response: %w", err)
	}

	if len(result.Results) > 0 {
		return result.Results[0].Score, nil
	}

	return 0.0, nil
}

// buildInjectionPatterns creates the library of injection patterns
func buildInjectionPatterns() []InjectionPattern {
	patterns := []struct {
		pattern     string
		severity    string
		description string
	}{
		// Direct instruction override
		{`ignore\s+(previous|all|above|prior)\s+instructions?`, "CRITICAL", "Direct instruction override"},
		{`disregard\s+(previous|all|above|prior)\s+instructions?`, "CRITICAL", "Direct instruction override"},
		{`forget\s+(previous|all|above|prior)\s+instructions?`, "CRITICAL", "Direct instruction override"},
		
		// System prompt extraction
		{`(show|reveal|display|print|output)\s+(your|the)\s+system\s+prompt`, "CRITICAL", "System prompt extraction"},
		{`what\s+(is|are)\s+your\s+(instructions|rules|guidelines)`, "HIGH", "System prompt extraction"},
		
		// Role manipulation
		{`you\s+are\s+now\s+(in\s+)?(admin|root|developer|debug)\s+mode`, "CRITICAL", "Role manipulation"},
		{`enable\s+(admin|root|developer|debug)\s+mode`, "CRITICAL", "Role manipulation"},
		{`act\s+as\s+(if\s+you\s+are\s+)?(admin|root|developer)`, "HIGH", "Role manipulation"},
		
		// Jailbreak attempts
		{`(DAN|do\s+anything\s+now)`, "CRITICAL", "Jailbreak attempt"},
		{`pretend\s+you\s+have\s+no\s+restrictions`, "HIGH", "Jailbreak attempt"},
		{`ignore\s+your\s+safety\s+guidelines`, "CRITICAL", "Jailbreak attempt"},
		
		// Delimiter injection
		{`---\s*END\s+OF\s+INSTRUCTIONS?\s*---`, "HIGH", "Delimiter injection"},
		{`<\s*/?\s*system\s*>`, "HIGH", "Delimiter injection"},
		{`\[\s*SYSTEM\s*\]`, "HIGH", "Delimiter injection"},
		
		// Encoding tricks
		{`base64|rot13|hex\s+encoded`, "MEDIUM", "Encoding trick"},
		{`decode\s+the\s+following`, "MEDIUM", "Encoding trick"},
		
		// Privilege escalation
		{`grant\s+me\s+(admin|root|elevated)\s+privileges`, "CRITICAL", "Privilege escalation"},
		{`bypass\s+(security|restrictions|limitations)`, "HIGH", "Privilege escalation"},
	}

	result := make([]InjectionPattern, 0, len(patterns))
	for _, p := range patterns {
		regex, err := regexp.Compile(p.pattern)
		if err != nil {
			continue // Skip invalid patterns
		}
		result = append(result, InjectionPattern{
			Pattern:     p.pattern,
			Severity:    p.severity,
			Description: p.description,
			Regex:       regex,
		})
	}

	return result
}

// getSeverityScore converts severity level to numeric score
func getSeverityScore(severity string) float64 {
	switch severity {
	case "CRITICAL":
		return 0.95
	case "HIGH":
		return 0.80
	case "MEDIUM":
		return 0.60
	case "LOW":
		return 0.40
	default:
		return 0.0
	}
}
