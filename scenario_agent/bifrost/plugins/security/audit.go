package security

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/maximhq/bifrost/core/schemas"
)

// AuditLogger logs security decisions to a file
type AuditLogger struct {
	file   *os.File
	mu     sync.Mutex
	logger schemas.Logger
}

// AuditEntry represents a security audit log entry
type AuditEntry struct {
	Timestamp   time.Time       `json:"timestamp"`
	RequestID   string          `json:"request_id,omitempty"`
	SessionID   string          `json:"session_id,omitempty"`
	UserID      string          `json:"user_id,omitempty"`
	Decision    string          `json:"decision"` // "allow" or "block"
	Reason      string          `json:"reason,omitempty"`
	ThreatScore float64         `json:"threat_score,omitempty"`
	PIIEntities []PIIEntity     `json:"pii_entities,omitempty"`
	BlockedTools []string       `json:"blocked_tools,omitempty"`
	Path        string          `json:"path,omitempty"`
	Method      string          `json:"method,omitempty"`
}

// NewAuditLogger creates a new audit logger
func NewAuditLogger(logPath string, logger schemas.Logger) (*AuditLogger, error) {
	// Create directory if it doesn't exist
	dir := filepath.Dir(logPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create audit log directory: %w", err)
	}

	// Open log file in append mode
	file, err := os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return nil, fmt.Errorf("failed to open audit log file: %w", err)
	}

	return &AuditLogger{
		file:   file,
		logger: logger,
	}, nil
}

// LogDecision logs a security decision
func (al *AuditLogger) LogDecision(ctx *schemas.BifrostContext, decision *SecurityDecision, req *schemas.HTTPRequest) {
	entry := AuditEntry{
		Timestamp:   time.Now(),
		ThreatScore: decision.ThreatScore,
		PIIEntities: decision.PIIEntities,
		BlockedTools: decision.BlockedTools,
	}

	if decision.Allow {
		entry.Decision = "allow"
	} else {
		entry.Decision = "block"
		entry.Reason = decision.Reason
	}

	// Extract context information
	if requestID, ok := ctx.Value("request-id").(string); ok {
		entry.RequestID = requestID
	}
	if sessionID, ok := ctx.Value("session-id").(string); ok {
		entry.SessionID = sessionID
	}
	if userID, ok := ctx.Value("user-id").(string); ok {
		entry.UserID = userID
	}

	// Extract request information
	if req != nil {
		entry.Path = req.Path
		entry.Method = req.Method
	}

	// Write to log file
	al.mu.Lock()
	defer al.mu.Unlock()

	data, err := json.Marshal(entry)
	if err != nil {
		al.logger.Warn("Failed to marshal audit entry", "error", err)
		return
	}

	if _, err := al.file.Write(append(data, '\n')); err != nil {
		al.logger.Warn("Failed to write audit entry", "error", err)
	}
}

// Close closes the audit log file
func (al *AuditLogger) Close() error {
	al.mu.Lock()
	defer al.mu.Unlock()

	if al.file != nil {
		return al.file.Close()
	}
	return nil
}
