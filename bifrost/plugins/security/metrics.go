package security

import (
	"sync/atomic"
)

// SecurityMetrics tracks security-related metrics
type SecurityMetrics struct {
	requestsProcessed  atomic.Uint64
	requestsBlocked    atomic.Uint64
	threatsDetected    map[string]*atomic.Uint64
	piiFound           atomic.Uint64
	toolCallsBlocked   atomic.Uint64
}

// NewSecurityMetrics creates a new metrics tracker
func NewSecurityMetrics() *SecurityMetrics {
	return &SecurityMetrics{
		threatsDetected: map[string]*atomic.Uint64{
			"prompt_injection":  {},
			"memory_poisoning":  {},
			"tool_misuse":       {},
		},
	}
}

// IncrementRequestsProcessed increments the requests processed counter
func (sm *SecurityMetrics) IncrementRequestsProcessed(decision string) {
	sm.requestsProcessed.Add(1)
}

// IncrementRequestsBlocked increments the requests blocked counter
func (sm *SecurityMetrics) IncrementRequestsBlocked() {
	sm.requestsBlocked.Add(1)
}

// IncrementThreatsDetected increments the threats detected counter for a specific type
func (sm *SecurityMetrics) IncrementThreatsDetected(threatType string) {
	if counter, ok := sm.threatsDetected[threatType]; ok {
		counter.Add(1)
	}
}

// IncrementPIIFound increments the PII found counter
func (sm *SecurityMetrics) IncrementPIIFound(count int) {
	sm.piiFound.Add(uint64(count))
}

// IncrementToolCallsBlocked increments the tool calls blocked counter
func (sm *SecurityMetrics) IncrementToolCallsBlocked(count int) {
	sm.toolCallsBlocked.Add(uint64(count))
}

// GetMetrics returns current metric values
func (sm *SecurityMetrics) GetMetrics() map[string]uint64 {
	metrics := map[string]uint64{
		"requests_processed": sm.requestsProcessed.Load(),
		"requests_blocked":   sm.requestsBlocked.Load(),
		"pii_found":          sm.piiFound.Load(),
		"tool_calls_blocked": sm.toolCallsBlocked.Load(),
	}

	for threatType, counter := range sm.threatsDetected {
		metrics["threats_"+threatType] = counter.Load()
	}

	return metrics
}
