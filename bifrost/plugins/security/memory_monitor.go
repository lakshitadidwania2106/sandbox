package security

import (
	"fmt"
	"strings"
	"sync"

	"github.com/maximhq/bifrost/core/schemas"
)

// MemoryMonitor tracks and validates memory operations
type MemoryMonitor struct {
	writeCounts map[string]int
	mu          sync.RWMutex
	config      *SecurityConfig
	logger      schemas.Logger
}

// NewMemoryMonitor creates a new memory monitor
func NewMemoryMonitor(config *SecurityConfig, logger schemas.Logger) *MemoryMonitor {
	return &MemoryMonitor{
		writeCounts: make(map[string]int),
		config:      config,
		logger:      logger,
	}
}

// DetectMemoryPoisoning validates a memory write operation
func (mm *MemoryMonitor) DetectMemoryPoisoning(ctx *schemas.BifrostContext, req *schemas.BifrostMCPRequest, sessionID string) (bool, string) {
	// Step 1: Check write frequency (rate limiting)
	mm.mu.Lock()
	writeCount := mm.writeCounts[sessionID]
	if writeCount >= mm.config.MaxMemoryWrites {
		mm.mu.Unlock()
		return true, fmt.Sprintf("Memory write rate limit exceeded (%d/%d)", writeCount, mm.config.MaxMemoryWrites)
	}
	mm.writeCounts[sessionID]++
	mm.mu.Unlock()

	// Step 2: Extract memory content from arguments
	var argsMap map[string]interface{}
	if args := req.GetToolArguments(); args != nil {
		if m, ok := args.(map[string]interface{}); ok {
			argsMap = m
		}
	}
	content := extractMemoryContent(argsMap)
	if content == "" {
		return false, ""
	}

	// Step 3: Check for privilege escalation patterns
	if containsPrivilegeEscalation(content) {
		return true, "Privilege escalation attempt detected in memory write"
	}

	// Step 4: Check for malicious instruction patterns
	if containsMaliciousInstructions(content) {
		return true, "Malicious instructions detected in memory write"
	}

	return false, ""
}

// GetWriteCount returns the current write count for a session
func (mm *MemoryMonitor) GetWriteCount(sessionID string) int {
	mm.mu.RLock()
	defer mm.mu.RUnlock()
	return mm.writeCounts[sessionID]
}

// ResetWriteCount resets the write count for a session
func (mm *MemoryMonitor) ResetWriteCount(sessionID string) {
	mm.mu.Lock()
	defer mm.mu.Unlock()
	delete(mm.writeCounts, sessionID)
}

// extractMemoryContent extracts the content being written to memory
func extractMemoryContent(arguments map[string]interface{}) string {
	// Try common memory write argument names
	for _, key := range []string{"value", "content", "data", "text"} {
		if val, ok := arguments[key].(string); ok {
			return val
		}
	}
	return ""
}

// containsPrivilegeEscalation checks for privilege escalation patterns
func containsPrivilegeEscalation(content string) bool {
	lowerContent := strings.ToLower(content)
	
	escalationPatterns := []string{
		"you are now admin",
		"you are now root",
		"grant admin",
		"grant root",
		"elevate privileges",
		"bypass restrictions",
		"ignore security",
		"disable security",
		"role: admin",
		"role: root",
		"permission: admin",
		"permission: root",
	}

	for _, pattern := range escalationPatterns {
		if strings.Contains(lowerContent, pattern) {
			return true
		}
	}

	return false
}

// containsMaliciousInstructions checks for malicious instruction patterns
func containsMaliciousInstructions(content string) bool {
	lowerContent := strings.ToLower(content)
	
	maliciousPatterns := []string{
		"ignore previous instructions",
		"disregard previous instructions",
		"forget previous instructions",
		"new instructions:",
		"system instructions:",
		"override instructions",
		"execute the following",
		"run the following",
		"eval(",
		"exec(",
	}

	for _, pattern := range maliciousPatterns {
		if strings.Contains(lowerContent, pattern) {
			return true
		}
	}

	return false
}
