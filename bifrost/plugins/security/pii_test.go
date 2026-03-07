package security

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/maximhq/bifrost/core/schemas"
)

// SimpleMockLogger implements schemas.Logger for testing
type SimpleMockLogger struct{}

func (m *SimpleMockLogger) Debug(msg string, args ...interface{})                                  {}
func (m *SimpleMockLogger) Info(msg string, args ...interface{})                                   {}
func (m *SimpleMockLogger) Warn(msg string, args ...interface{})                                   {}
func (m *SimpleMockLogger) Error(msg string, args ...interface{})                                  {}
func (m *SimpleMockLogger) Fatal(msg string, args ...interface{})                                  {}
func (m *SimpleMockLogger) SetLevel(level schemas.LogLevel)                                        {}
func (m *SimpleMockLogger) SetOutputType(outputType schemas.LoggerOutputType)                      {}
func (m *SimpleMockLogger) LogHTTPRequest(level schemas.LogLevel, msg string) schemas.LogEventBuilder {
	return schemas.NoopLogEvent
}

// TestPIIDetector_Analyze_EmailAndPhone tests detection of EMAIL and PHONE entities
func TestPIIDetector_Analyze_EmailAndPhone(t *testing.T) {
	// Create mock Presidio server
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp := PresidioAnalyzeResponse{
			Entities: []PresidioEntity{
				{EntityType: "EMAIL", Start: 12, End: 32, Score: 0.95},
				{EntityType: "PHONE", Start: 41, End: 53, Score: 0.90},
			},
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))
	defer server.Close()

	config := &SecurityConfig{
		PresidioURL:    server.URL,
		PIIEntityTypes: []string{"EMAIL", "PHONE"},
	}
	detector, _ := NewPIIDetector(config, &SimpleMockLogger{})

	text := "Contact me: john.doe@example.com or call 555-123-4567"
	entities, err := detector.Analyze(text)
	
	if err != nil {
		t.Fatalf("Analyze failed: %v", err)
	}
	if len(entities) != 2 {
		t.Errorf("Expected 2 entities, got %d", len(entities))
	}
	if entities[0].Type != "EMAIL" {
		t.Errorf("Expected EMAIL, got %s", entities[0].Type)
	}
	if entities[1].Type != "PHONE" {
		t.Errorf("Expected PHONE, got %s", entities[1].Type)
	}
}

// TestPIIDetector_Analyze_SSN tests detection of SSN entities
func TestPIIDetector_Analyze_SSN(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp := PresidioAnalyzeResponse{
			Entities: []PresidioEntity{
				{EntityType: "SSN", Start: 11, End: 22, Score: 0.98},
			},
		}
		json.NewEncoder(w).Encode(resp)
	}))
	defer server.Close()

	config := &SecurityConfig{
		PresidioURL:    server.URL,
		PIIEntityTypes: []string{"SSN"},
	}
	detector, _ := NewPIIDetector(config, &SimpleMockLogger{})

	text := "My SSN is 123-45-6789"
	entities, _ := detector.Analyze(text)
	
	if len(entities) != 1 {
		t.Errorf("Expected 1 entity, got %d", len(entities))
	}
	if entities[0].Type != "SSN" {
		t.Errorf("Expected SSN, got %s", entities[0].Type)
	}
}

// TestPIIDetector_Analyze_CreditCard tests detection of CREDIT_CARD entities
func TestPIIDetector_Analyze_CreditCard(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp := PresidioAnalyzeResponse{
			Entities: []PresidioEntity{
				{EntityType: "CREDIT_CARD", Start: 8, End: 27, Score: 0.99},
			},
		}
		json.NewEncoder(w).Encode(resp)
	}))
	defer server.Close()

	config := &SecurityConfig{
		PresidioURL:    server.URL,
		PIIEntityTypes: []string{"CREDIT_CARD"},
	}
	detector, _ := NewPIIDetector(config, &SimpleMockLogger{})

	text := "Card: 4532-1234-5678-9010"
	entities, _ := detector.Analyze(text)
	
	if len(entities) != 1 {
		t.Errorf("Expected 1 entity, got %d", len(entities))
	}
	if entities[0].Type != "CREDIT_CARD" {
		t.Errorf("Expected CREDIT_CARD, got %s", entities[0].Type)
	}
}

// TestPIIDetector_Analyze_EmptyText tests handling of empty text
func TestPIIDetector_Analyze_EmptyText(t *testing.T) {
	config := &SecurityConfig{
		PresidioURL:    "http://localhost:5000",
		PIIEntityTypes: []string{"EMAIL"},
	}
	detector, _ := NewPIIDetector(config, &SimpleMockLogger{})

	entities, err := detector.Analyze("")
	if err != nil {
		t.Errorf("Expected no error for empty text, got %v", err)
	}
	if entities != nil {
		t.Errorf("Expected nil entities for empty text")
	}
}

// TestPIIDetector_Analyze_ServerError tests graceful degradation on server errors
func TestPIIDetector_Analyze_ServerError(t *testing.T) {
	attempts := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		attempts++
		w.WriteHeader(http.StatusInternalServerError)
	}))
	defer server.Close()

	config := &SecurityConfig{
		PresidioURL:    server.URL,
		PIIEntityTypes: []string{"EMAIL"},
	}
	detector, _ := NewPIIDetector(config, &SimpleMockLogger{})

	entities, err := detector.Analyze("test text")
	if err != nil {
		t.Errorf("Expected graceful degradation (no error), got %v", err)
	}
	if len(entities) != 0 {
		t.Errorf("Expected empty entities list on error")
	}
	if attempts != 3 {
		t.Errorf("Expected 3 retry attempts, got %d", attempts)
	}
}

// TestPIIDetector_Redact tests basic redaction
func TestPIIDetector_Redact(t *testing.T) {
	config := &SecurityConfig{PresidioURL: "http://localhost:5000"}
	detector, _ := NewPIIDetector(config, &SimpleMockLogger{})

	text := "Contact me: john.doe@example.com or call 555-123-4567"
	entities := []PIIEntity{
		{Type: "EMAIL", Start: 12, End: 32, Score: 0.95},
		{Type: "PHONE", Start: 41, End: 53, Score: 0.90},
	}

	redacted := detector.Redact(text, entities)
	expected := "Contact me: [EMAIL] or call [PHONE]"
	if redacted != expected {
		t.Errorf("Expected '%s', got '%s'", expected, redacted)
	}
}

// TestPIIDetector_Redact_EmptyEntities tests redaction with no entities
func TestPIIDetector_Redact_EmptyEntities(t *testing.T) {
	config := &SecurityConfig{PresidioURL: "http://localhost:5000"}
	detector, _ := NewPIIDetector(config, &SimpleMockLogger{})

	text := "No PII here"
	redacted := detector.Redact(text, []PIIEntity{})
	if redacted != text {
		t.Errorf("Expected unchanged text")
	}
}

// TestPIIDetector_Redact_PreservesLineBreaks tests structure preservation
func TestPIIDetector_Redact_PreservesLineBreaks(t *testing.T) {
	config := &SecurityConfig{PresidioURL: "http://localhost:5000"}
	detector, _ := NewPIIDetector(config, &SimpleMockLogger{})

	text := "Line 1: john@example.com\nLine 2: More text\nLine 3: jane@example.com"
	entities := []PIIEntity{
		{Type: "EMAIL", Start: 8, End: 24, Score: 0.95},
		{Type: "EMAIL", Start: 54, End: 70, Score: 0.95},
	}

	redacted := detector.Redact(text, entities)
	expected := "Line 1: [EMAIL]\nLine 2: More text\nLine 3: [EMAIL]"
	if redacted != expected {
		t.Errorf("Expected '%s', got '%s'", expected, redacted)
	}
}

// TestResolveOverlaps_NoOverlap tests non-overlapping entities
func TestResolveOverlaps_NoOverlap(t *testing.T) {
	entities := []PIIEntity{
		{Type: "EMAIL", Start: 0, End: 10, Score: 0.9},
		{Type: "PHONE", Start: 20, End: 30, Score: 0.8},
	}
	result := resolveOverlaps(entities)
	if len(result) != 2 {
		t.Errorf("Expected 2 entities, got %d", len(result))
	}
}

// TestResolveOverlaps_WithOverlap tests overlapping entities
func TestResolveOverlaps_WithOverlap(t *testing.T) {
	entities := []PIIEntity{
		{Type: "EMAIL", Start: 0, End: 20, Score: 0.9},
		{Type: "PERSON", Start: 5, End: 15, Score: 0.7},
	}
	result := resolveOverlaps(entities)
	if len(result) != 1 {
		t.Errorf("Expected 1 entity after overlap resolution, got %d", len(result))
	}
	if result[0].Type != "EMAIL" {
		t.Errorf("Expected EMAIL (higher score), got %s", result[0].Type)
	}
}

// TestResolveOverlaps_KeepsHighestScore tests that highest score is kept
func TestResolveOverlaps_KeepsHighestScore(t *testing.T) {
	entities := []PIIEntity{
		{Type: "PERSON", Start: 0, End: 20, Score: 0.7},
		{Type: "EMAIL", Start: 5, End: 25, Score: 0.9},
	}
	result := resolveOverlaps(entities)
	if len(result) != 1 {
		t.Fatalf("Expected 1 entity, got %d", len(result))
	}
	if result[0].Type != "EMAIL" {
		t.Errorf("Expected EMAIL (higher score), got %s", result[0].Type)
	}
	if result[0].Score != 0.9 {
		t.Errorf("Expected score 0.9, got %f", result[0].Score)
	}
}

// TestResolveOverlaps_Empty tests empty input
func TestResolveOverlaps_Empty(t *testing.T) {
	result := resolveOverlaps([]PIIEntity{})
	if len(result) != 0 {
		t.Errorf("Expected 0 entities, got %d", len(result))
	}
}

// TestResolveOverlaps_Single tests single entity
func TestResolveOverlaps_Single(t *testing.T) {
	entities := []PIIEntity{
		{Type: "EMAIL", Start: 0, End: 10, Score: 0.9},
	}
	result := resolveOverlaps(entities)
	if len(result) != 1 {
		t.Errorf("Expected 1 entity, got %d", len(result))
	}
}
