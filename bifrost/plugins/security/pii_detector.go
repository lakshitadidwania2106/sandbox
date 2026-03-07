package security

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sort"
	"time"

	"github.com/maximhq/bifrost/core/schemas"
)

// PIIDetector identifies and redacts sensitive data using Presidio service
type PIIDetector struct {
	presidioURL string
	client      *http.Client
	entityTypes []string
	logger      schemas.Logger
}

// NewPIIDetector creates a new PII detector
func NewPIIDetector(config *SecurityConfig, logger schemas.Logger) (*PIIDetector, error) {
	return &PIIDetector{
		presidioURL: config.PresidioURL,
		client: &http.Client{
			Timeout: 5 * time.Second,
		},
		entityTypes: config.PIIEntityTypes,
		logger:      logger,
	}, nil
}

// PresidioAnalyzeRequest represents the request to Presidio analyze endpoint
type PresidioAnalyzeRequest struct {
	Text     string   `json:"text"`
	Language string   `json:"language"`
	Entities []string `json:"entities,omitempty"`
}

// PresidioAnalyzeResponse represents the response from Presidio analyze endpoint
type PresidioAnalyzeResponse struct {
	Entities []PresidioEntity `json:"entities"`
}

// PresidioEntity represents a detected entity from Presidio
type PresidioEntity struct {
	EntityType string  `json:"entity_type"`
	Start      int     `json:"start"`
	End        int     `json:"end"`
	Score      float64 `json:"score"`
}

// PresidioAnonymizeRequest represents the request to Presidio anonymize endpoint
type PresidioAnonymizeRequest struct {
	Text        string                    `json:"text"`
	Anonymizers map[string]map[string]string `json:"anonymizers"`
}

// PresidioAnonymizeResponse represents the response from Presidio anonymize endpoint
type PresidioAnonymizeResponse struct {
	Text string `json:"text"`
}

// Analyze detects PII entities in the given text with retry logic
func (pd *PIIDetector) Analyze(text string) ([]PIIEntity, error) {
	if text == "" {
		return nil, nil
	}

	// Prepare request
	analyzeReq := PresidioAnalyzeRequest{
		Text:     text,
		Language: "en",
		Entities: pd.entityTypes,
	}

	reqBody, err := json.Marshal(analyzeReq)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal analyze request: %w", err)
	}

	// Retry configuration: 3 attempts with exponential backoff
	maxRetries := 3
	backoffDurations := []time.Duration{100 * time.Millisecond, 200 * time.Millisecond, 400 * time.Millisecond}

	var lastErr error
	for attempt := 0; attempt < maxRetries; attempt++ {
		// Create context with timeout for this attempt
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		
		// Create HTTP request with context
		req, err := http.NewRequestWithContext(ctx, "POST", pd.presidioURL+"/analyze", bytes.NewBuffer(reqBody))
		if err != nil {
			cancel()
			return nil, fmt.Errorf("failed to create request: %w", err)
		}
		req.Header.Set("Content-Type", "application/json")

		// Execute request
		resp, err := pd.client.Do(req)
		cancel()

		if err != nil {
			lastErr = err
			if attempt < maxRetries-1 {
				pd.logger.Warn("Presidio analyze request failed, retrying",
					"attempt", attempt+1,
					"max_retries", maxRetries,
					"error", err.Error(),
					"backoff", backoffDurations[attempt])
				time.Sleep(backoffDurations[attempt])
				continue
			}
			// Final failure - log warning and return empty list (graceful degradation)
			pd.logger.Warn("Presidio analyze request failed after all retries, returning empty PII list",
				"attempts", maxRetries,
				"error", err.Error())
			return []PIIEntity{}, nil
		}

		// Check status code
		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			resp.Body.Close()
			lastErr = fmt.Errorf("presidio analyze error %d: %s", resp.StatusCode, body)
			
			if attempt < maxRetries-1 {
				pd.logger.Warn("Presidio analyze returned error status, retrying",
					"attempt", attempt+1,
					"max_retries", maxRetries,
					"status_code", resp.StatusCode,
					"backoff", backoffDurations[attempt])
				time.Sleep(backoffDurations[attempt])
				continue
			}
			// Final failure - log warning and return empty list (graceful degradation)
			pd.logger.Warn("Presidio analyze failed after all retries, returning empty PII list",
				"attempts", maxRetries,
				"status_code", resp.StatusCode)
			return []PIIEntity{}, nil
		}

		// Parse response
		var analyzeResp PresidioAnalyzeResponse
		if err := json.NewDecoder(resp.Body).Decode(&analyzeResp); err != nil {
			resp.Body.Close()
			lastErr = fmt.Errorf("failed to decode analyze response: %w", err)
			
			if attempt < maxRetries-1 {
				pd.logger.Warn("Failed to decode Presidio response, retrying",
					"attempt", attempt+1,
					"max_retries", maxRetries,
					"error", err.Error(),
					"backoff", backoffDurations[attempt])
				time.Sleep(backoffDurations[attempt])
				continue
			}
			// Final failure - log warning and return empty list (graceful degradation)
			pd.logger.Warn("Failed to decode Presidio response after all retries, returning empty PII list",
				"attempts", maxRetries,
				"error", err.Error())
			return []PIIEntity{}, nil
		}
		resp.Body.Close()

		// Success! Convert to PIIEntity
		entities := make([]PIIEntity, 0, len(analyzeResp.Entities))
		for _, result := range analyzeResp.Entities {
			entities = append(entities, PIIEntity{
				Type:  result.EntityType,
				Text:  text[result.Start:result.End],
				Start: result.Start,
				End:   result.End,
				Score: result.Score,
			})
		}

		// Resolve overlapping entities
		entities = resolveOverlaps(entities)

		return entities, nil
	}

	// Should not reach here, but handle gracefully
	pd.logger.Warn("Presidio analyze failed unexpectedly, returning empty PII list", "error", lastErr)
	return []PIIEntity{}, nil
}

// Redact replaces PII entities with placeholders
func (pd *PIIDetector) Redact(text string, entities []PIIEntity) string {
	if len(entities) == 0 {
		return text
	}

	// Sort entities by start position in descending order
	// This allows us to replace from end to start, preserving indices
	sorted := make([]PIIEntity, len(entities))
	copy(sorted, entities)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].Start > sorted[j].Start
	})

	// Build redacted text
	result := text
	for _, entity := range sorted {
		placeholder := fmt.Sprintf("[%s]", entity.Type)
		result = result[:entity.Start] + placeholder + result[entity.End:]
	}

	return result
}

// resolveOverlaps keeps the highest scoring entity when entities overlap
func resolveOverlaps(entities []PIIEntity) []PIIEntity {
	if len(entities) <= 1 {
		return entities
	}

	// Sort by start position
	sorted := make([]PIIEntity, len(entities))
	copy(sorted, entities)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].Start < sorted[j].Start
	})

	// Keep non-overlapping entities with highest scores
	result := []PIIEntity{sorted[0]}
	for i := 1; i < len(sorted); i++ {
		current := sorted[i]
		lastAdded := result[len(result)-1]

		// Check if current overlaps with last added
		if current.Start >= lastAdded.End {
			// No overlap, add current
			result = append(result, current)
		} else {
			// Overlap detected, keep the one with higher score
			if current.Score > lastAdded.Score {
				result[len(result)-1] = current
			}
		}
	}

	return result
}
