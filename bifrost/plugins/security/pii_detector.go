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

// PIIDetector identifies and redacts sensitive data using the Presidio service
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

// PresidioAnalyzeRequest is the request body for the Presidio /analyze endpoint
type PresidioAnalyzeRequest struct {
	Text     string   `json:"text"`
	Language string   `json:"language"`
	Entities []string `json:"entities,omitempty"`
}

// PresidioEntity is a single detected entity from Presidio's response array
type PresidioEntity struct {
	EntityType string  `json:"entity_type"`
	Start      int     `json:"start"`
	End        int     `json:"end"`
	Score      float64 `json:"score"`
}

// PresidioAnonymizeRequest represents the request to Presidio anonymize endpoint
type PresidioAnonymizeRequest struct {
	Text        string                       `json:"text"`
	Anonymizers map[string]map[string]string `json:"anonymizers"`
}

// PresidioAnonymizeResponse represents the response from Presidio anonymize endpoint
type PresidioAnonymizeResponse struct {
	Text string `json:"text"`
}

// presidioEntityToType maps Presidio entity types to our internal type names.
// This normalizes names like US_SSN -> SSN so OPA policies can refer to "SSN".
func presidioEntityToType(presidioType string) string {
	switch presidioType {
	case "US_SSN":
		return "SSN"
	case "EMAIL_ADDRESS":
		return "EMAIL"
	default:
		return presidioType
	}
}

// Analyze detects PII entities in the given text using Presidio, with retry logic.
func (pd *PIIDetector) Analyze(text string) ([]PIIEntity, error) {
	if text == "" {
		return nil, nil
	}

	// Translate our internal entity type names to the names Presidio knows.
	// e.g. "SSN" -> "US_SSN", since that's what the UsSsnRecognizer reports.
	presidioEntities := make([]string, 0, len(pd.entityTypes))
	for _, e := range pd.entityTypes {
		switch e {
		case "SSN":
			presidioEntities = append(presidioEntities, "US_SSN")
		case "EMAIL":
			presidioEntities = append(presidioEntities, "EMAIL_ADDRESS")
		default:
			presidioEntities = append(presidioEntities, e)
		}
	}

	analyzeReq := PresidioAnalyzeRequest{
		Text:     text,
		Language: "en",
		Entities: presidioEntities,
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
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)

		req, err := http.NewRequestWithContext(ctx, "POST", pd.presidioURL+"/analyze", bytes.NewBuffer(reqBody))
		if err != nil {
			cancel()
			return nil, fmt.Errorf("failed to create request: %w", err)
		}
		req.Header.Set("Content-Type", "application/json")

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
			pd.logger.Warn("Presidio analyze request failed after all retries, returning empty PII list",
				"attempts", maxRetries,
				"error", err.Error())
			return []PIIEntity{}, nil
		}

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
			pd.logger.Warn("Presidio analyze failed after all retries, returning empty PII list",
				"attempts", maxRetries,
				"status_code", resp.StatusCode)
			return []PIIEntity{}, nil
		}

		body, err := io.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			lastErr = fmt.Errorf("failed to read analyze response body: %w", err)
			if attempt < maxRetries-1 {
				time.Sleep(backoffDurations[attempt])
				continue
			}
			return []PIIEntity{}, lastErr
		}

		pd.logger.Debug("Presidio analyze raw response", "body", string(body))

		// Presidio returns a raw JSON array, not a wrapped object.
		var analyzeResp []PresidioEntity
		if err := json.Unmarshal(body, &analyzeResp); err != nil {
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
			pd.logger.Warn("Failed to decode Presidio response after all retries, returning empty PII list",
				"attempts", maxRetries,
				"error", err.Error())
			return []PIIEntity{}, nil
		}

		// Convert Presidio results to our internal PIIEntity format
		entities := make([]PIIEntity, 0, len(analyzeResp))
		for _, result := range analyzeResp {
			entities = append(entities, PIIEntity{
				Type:  presidioEntityToType(result.EntityType),
				Text:  text[result.Start:result.End],
				Start: result.Start,
				End:   result.End,
				Score: result.Score,
			})
		}

		// Resolve overlapping entities (keeps highest score)
		entities = resolveOverlaps(entities)
		pd.logger.Debug("PII detection complete", "entities_found", len(entities))

		return entities, nil
	}

	pd.logger.Warn("Presidio analyze failed unexpectedly", "error", lastErr)
	return []PIIEntity{}, nil
}

// Redact replaces PII entities with type-labelled placeholders
func (pd *PIIDetector) Redact(text string, entities []PIIEntity) string {
	if len(entities) == 0 {
		return text
	}

	// Sort entities by start position descending so we replace from the end,
	// preserving all other indices.
	sorted := make([]PIIEntity, len(entities))
	copy(sorted, entities)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].Start > sorted[j].Start
	})

	result := text
	for _, entity := range sorted {
		placeholder := fmt.Sprintf("[%s]", entity.Type)
		result = result[:entity.Start] + placeholder + result[entity.End:]
	}

	return result
}

// resolveOverlaps keeps the highest scoring entity when detected spans overlap
func resolveOverlaps(entities []PIIEntity) []PIIEntity {
	if len(entities) <= 1 {
		return entities
	}

	sort.Slice(entities, func(i, j int) bool {
		return entities[i].Start < entities[j].Start
	})

	result := []PIIEntity{entities[0]}
	for i := 1; i < len(entities); i++ {
		current := entities[i]
		last := result[len(result)-1]

		if current.Start >= last.End {
			// No overlap, add current
			result = append(result, current)
		} else if current.Score > last.Score {
			// Overlap: keep the higher-scoring one
			result[len(result)-1] = current
		}
	}

	return result
}
