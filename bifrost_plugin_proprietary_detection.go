package main

/*
Bifrost Plugin: Proprietary Code Detection
==========================================

This plugin integrates proprietary code detection directly into the Bifrost gateway.
It intercepts requests BEFORE they reach LLM providers and blocks any requests
containing proprietary code.

Advantages over MITM proxy:
- No need to configure system proxy
- No certificate installation
- Works at the gateway level (all traffic)
- Better performance (no extra network hop)
- Centralized control

Usage:
1. Build the plugin:
   go build -buildmode=plugin -o proprietary_detection.so bifrost_plugin_proprietary_detection.go

2. Configure in Bifrost:
   {
     "plugins": [
       {
         "name": "proprietary-detection",
         "path": "./proprietary_detection.so",
         "enabled": true,
         "config": {
           "proprietary_code_dir": "./proprietary_code",
           "similarity_threshold": 60,
           "block_on_detection": true
         }
       }
     ]
   }

3. Add your proprietary code to ./proprietary_code/

The plugin will automatically block any requests containing proprietary code!
*/

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/maximhq/bifrost/core/schemas"
	"github.com/rapidfuzz/go-rapidfuzz"
)

// Config for the plugin
type ProprietaryDetectionConfig struct {
	ProprietaryCodeDir   string  `json:"proprietary_code_dir"`   // Directory containing proprietary code
	SimilarityThreshold  int     `json:"similarity_threshold"`   // 0-100, default 60
	BlockOnDetection     bool    `json:"block_on_detection"`     // If true, block requests with proprietary code
	LogOnly              bool    `json:"log_only"`               // If true, only log detections without blocking
	MonitoredRequestTypes []string `json:"monitored_request_types"` // Request types to monitor (empty = all)
}

// ProprietaryDetectionPlugin implements the LLMPlugin interface
type ProprietaryDetectionPlugin struct {
	name              string
	config            ProprietaryDetectionConfig
	proprietaryFiles  []string // List of proprietary code files
	logger            schemas.Logger
}

// Init initializes the plugin (called by Bifrost)
func Init(config map[string]interface{}) (schemas.LLMPlugin, error) {
	// Parse config
	configBytes, err := json.Marshal(config)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal config: %w", err)
	}

	var pluginConfig ProprietaryDetectionConfig
	if err := json.Unmarshal(configBytes, &pluginConfig); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	// Set defaults
	if pluginConfig.ProprietaryCodeDir == "" {
		pluginConfig.ProprietaryCodeDir = "./proprietary_code"
	}
	if pluginConfig.SimilarityThreshold == 0 {
		pluginConfig.SimilarityThreshold = 60
	}
	if pluginConfig.BlockOnDetection == false && pluginConfig.LogOnly == false {
		pluginConfig.BlockOnDetection = true // Default to blocking
	}

	plugin := &ProprietaryDetectionPlugin{
		name:   "proprietary-detection",
		config: pluginConfig,
	}

	// Index proprietary code files
	if err := plugin.indexProprietaryCode(); err != nil {
		return nil, fmt.Errorf("failed to index proprietary code: %w", err)
	}

	return plugin, nil
}

// GetName returns the plugin name
func (p *ProprietaryDetectionPlugin) GetName() string {
	return p.name
}

// Cleanup is called on shutdown
func (p *ProprietaryDetectionPlugin) Cleanup() error {
	return nil
}

// indexProprietaryCode scans the proprietary code directory and indexes all code files
func (p *ProprietaryDetectionPlugin) indexProprietaryCode() error {
	if _, err := os.Stat(p.config.ProprietaryCodeDir); os.IsNotExist(err) {
		return fmt.Errorf("proprietary code directory not found: %s", p.config.ProprietaryCodeDir)
	}

	p.proprietaryFiles = []string{}

	err := filepath.Walk(p.config.ProprietaryCodeDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Only index code files
		if !info.IsDir() && isCodeFile(path) {
			p.proprietaryFiles = append(p.proprietaryFiles, path)
		}

		return nil
	})

	if err != nil {
		return err
	}

	if len(p.proprietaryFiles) == 0 {
		return fmt.Errorf("no proprietary code files found in %s", p.config.ProprietaryCodeDir)
	}

	return nil
}

// isCodeFile checks if a file is a code file based on extension
func isCodeFile(path string) bool {
	codeExtensions := []string{".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php"}
	ext := strings.ToLower(filepath.Ext(path))
	for _, codeExt := range codeExtensions {
		if ext == codeExt {
			return true
		}
	}
	return false
}

// PreLLMHook is called BEFORE the request is sent to the LLM provider
// This is where we check for proprietary code
func (p *ProprietaryDetectionPlugin) PreLLMHook(
	ctx *schemas.BifrostContext,
	req *schemas.BifrostRequest,
) (*schemas.BifrostRequest, *schemas.LLMPluginShortCircuit, error) {
	
	// Check if we should monitor this request type
	if !p.shouldMonitorRequest(req.RequestType) {
		return req, nil, nil
	}

	// Extract text content from the request
	textContent := p.extractTextFromRequest(req)
	if textContent == "" || len(textContent) < 20 {
		return req, nil, nil // Skip short content
	}

	// Check for proprietary code
	isProprietaryCode, matchInfo := p.checkIfProprietaryCode(textContent)

	if isProprietaryCode {
		// Log the detection
		requestID := ctx.Value(schemas.BifrostContextKeyRequestID)
		p.logDetection(requestID, matchInfo)

		if p.config.BlockOnDetection && !p.config.LogOnly {
			// Block the request by returning a short-circuit response
			return req, p.createBlockedResponse(matchInfo), nil
		}
	}

	return req, nil, nil
}

// PostLLMHook is called AFTER the response is received from the LLM provider
// We don't need to do anything here for proprietary code detection
func (p *ProprietaryDetectionPlugin) PostLLMHook(
	ctx *schemas.BifrostContext,
	resp *schemas.BifrostResponse,
	bifrostErr *schemas.BifrostError,
) (*schemas.BifrostResponse, *schemas.BifrostError, error) {
	return resp, bifrostErr, nil
}

// shouldMonitorRequest checks if we should monitor this request type
func (p *ProprietaryDetectionPlugin) shouldMonitorRequest(requestType schemas.RequestType) bool {
	// If no specific types configured, monitor all
	if len(p.config.MonitoredRequestTypes) == 0 {
		return true
	}

	// Check if this request type is in the monitored list
	for _, monitoredType := range p.config.MonitoredRequestTypes {
		if string(requestType) == monitoredType {
			return true
		}
	}

	return false
}

// extractTextFromRequest extracts text content from various request types
func (p *ProprietaryDetectionPlugin) extractTextFromRequest(req *schemas.BifrostRequest) string {
	var textParts []string

	switch req.RequestType {
	case schemas.ChatCompletionRequest, schemas.ChatCompletionStreamRequest:
		if req.ChatRequest != nil && req.ChatRequest.Input != nil {
			for _, msg := range req.ChatRequest.Input {
				if msg.Content != nil {
					if msg.Content.ContentStr != nil {
						textParts = append(textParts, *msg.Content.ContentStr)
					}
					if msg.Content.ContentBlocks != nil {
						for _, block := range msg.Content.ContentBlocks {
							if block.Text != nil {
								textParts = append(textParts, *block.Text)
							}
						}
					}
				}
			}
		}

	case schemas.TextCompletionRequest, schemas.TextCompletionStreamRequest:
		if req.TextCompletionRequest != nil && req.TextCompletionRequest.Input != nil {
			if req.TextCompletionRequest.Input.PromptStr != nil {
				textParts = append(textParts, *req.TextCompletionRequest.Input.PromptStr)
			}
			if req.TextCompletionRequest.Input.PromptArray != nil {
				textParts = append(textParts, *req.TextCompletionRequest.Input.PromptArray...)
			}
		}

	case schemas.ResponsesRequest, schemas.ResponsesStreamRequest:
		if req.ResponsesRequest != nil && req.ResponsesRequest.Input != nil {
			for _, msg := range req.ResponsesRequest.Input {
				if msg.Content != nil {
					if msg.Content.ContentStr != nil {
						textParts = append(textParts, *msg.Content.ContentStr)
					}
					if msg.Content.ContentBlocks != nil {
						for _, block := range msg.Content.ContentBlocks {
							if block.Text != nil {
								textParts = append(textParts, *block.Text)
							}
						}
					}
				}
			}
		}
	}

	return strings.Join(textParts, "\n")
}

// MatchInfo contains information about a proprietary code match
type MatchInfo struct {
	FilePath   string
	Similarity float64
	StartLine  int
	EndLine    int
}

// checkIfProprietaryCode checks if the text contains proprietary code
// Returns true if proprietary code is detected, along with match information
func (p *ProprietaryDetectionPlugin) checkIfProprietaryCode(text string) (bool, *MatchInfo) {
	text = strings.TrimSpace(text)

	// Search in all proprietary files
	for _, filePath := range p.proprietaryFiles {
		match := p.fuzzySearchInFile(filePath, text)
		if match != nil {
			return true, match
		}
	}

	return false, nil
}

// normalizeCode normalizes code for comparison - handles both formatted and minified code
func normalizeCode(code string) string {
	// Remove extra whitespace but keep single spaces
	re := regexp.MustCompile(`\s+`)
	normalized := re.ReplaceAllString(code, " ")
	
	// Remove spaces around operators and punctuation
	re2 := regexp.MustCompile(`\s*([=+\-*/<>!,(){}[\]:;])\s*`)
	normalized = re2.ReplaceAllString(normalized, "$1")
	
	return strings.TrimSpace(normalized)
}

// fuzzySearchInFile performs fuzzy search in a single file
// Enhanced to detect both formatted and minified code
func (p *ProprietaryDetectionPlugin) fuzzySearchInFile(filePath string, targetSnippet string) *MatchInfo {
	// Read file content
	content, err := os.ReadFile(filePath)
	if err != nil {
		return nil
	}

	fullCode := string(content)
	targetSnippet = strings.TrimSpace(targetSnippet)

	// Split into lines
	codeLines := strings.Split(fullCode, "\n")
	snippetLines := strings.Split(targetSnippet, "\n")
	snippetLen := len(snippetLines)

	if snippetLen == 0 {
		return nil
	}

	bestScore := 0.0
	bestIndex := -1
	matchType := "formatted"

	// Method 1: Original sliding window (for formatted code)
	for i := 0; i <= len(codeLines)-snippetLen; i++ {
		window := strings.Join(codeLines[i:i+snippetLen], "\n")
		windowTrimmed := strings.TrimSpace(window)

		// Calculate fuzzy similarity using RapidFuzz
		score := rapidfuzz.Ratio(windowTrimmed, targetSnippet)

		if score > bestScore {
			bestScore = score
			bestIndex = i
			matchType = "formatted"
		}
	}

	// Method 2: Normalized comparison (for minified/unformatted code)
	targetNormalized := normalizeCode(targetSnippet)
	fullCodeNormalized := normalizeCode(fullCode)
	
	// Check if normalized target appears in normalized full code
	normalizedScore := rapidfuzz.PartialRatio(targetNormalized, fullCodeNormalized)
	
	if normalizedScore > bestScore {
		bestScore = normalizedScore
		bestIndex = 0
		matchType = "normalized"
	}

	// If score exceeds threshold, return match
	if bestScore >= float64(p.config.SimilarityThreshold) {
		return &MatchInfo{
			FilePath:   filePath,
			Similarity: bestScore,
			StartLine:  bestIndex + 1,
			EndLine:    bestIndex + snippetLen,
		}
	}

	return nil
}

// logDetection logs a proprietary code detection
func (p *ProprietaryDetectionPlugin) logDetection(requestID interface{}, match *MatchInfo) {
	fmt.Printf("\n🚨 PROPRIETARY CODE DETECTED!\n")
	fmt.Printf("   Request ID: %v\n", requestID)
	fmt.Printf("   File: %s\n", filepath.Base(match.FilePath))
	fmt.Printf("   Lines: %d-%d\n", match.StartLine, match.EndLine)
	fmt.Printf("   Similarity: %.1f%%\n", match.Similarity)
	fmt.Printf("   Action: %s\n", func() string {
		if p.config.BlockOnDetection && !p.config.LogOnly {
			return "BLOCKED"
		}
		return "LOGGED ONLY"
	}())
}

// createBlockedResponse creates a short-circuit response that blocks the request
func (p *ProprietaryDetectionPlugin) createBlockedResponse(match *MatchInfo) *schemas.LLMPluginShortCircuit {
	errorMessage := fmt.Sprintf(
		"Request blocked: Proprietary code detected (%.1f%% similarity with %s, lines %d-%d)",
		match.Similarity,
		filepath.Base(match.FilePath),
		match.StartLine,
		match.EndLine,
	)

	// Create a BifrostError
	bifrostError := &schemas.BifrostError{
		IsBifrostError: true,
		Error: &schemas.ErrorField{
			Message: errorMessage,
			Type:    "proprietary_code_detected",
		},
		StatusCode: 403, // Forbidden
		ExtraFields: schemas.BifrostErrorExtraFields{
			RequestType: schemas.UnknownRequest,
		},
	}

	// Set AllowFallbacks to false to prevent trying other providers
	allowFallbacks := false
	bifrostError.AllowFallbacks = &allowFallbacks

	return &schemas.LLMPluginShortCircuit{
		Response: nil,
		Error:    bifrostError,
	}
}

// Export the Init function for the plugin system
var Plugin ProprietaryDetectionPlugin
