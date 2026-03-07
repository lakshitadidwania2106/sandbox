package middleware

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

type PresidioAnalyzeRequest struct {
	Text     string  `json:"text"`
	Language string  `json:"language"`
}

type PresidioAnalyzeResponse struct {
	HasPII      bool     `json:"has_pii"`
	EntityCount int      `json:"entity_count"`
	EntityTypes []string `json:"entity_types"`
}

type PresidioAnonymizeRequest struct {
	Text string `json:"text"`
}

type PresidioAnonymizeResponse struct {
	Text string `json:"text"`
}

type PresidioMiddleware struct {
	serviceURL string
	client     *http.Client
}

func NewPresidioMiddleware() *PresidioMiddleware {
	serviceURL := os.Getenv("SECURITY_SERVICE_URL")
	if serviceURL == "" {
		serviceURL = "http://localhost:5000"
	}
	return &PresidioMiddleware{
		serviceURL: serviceURL,
		client:     &http.Client{},
	}
}

func (p *PresidioMiddleware) ScrubPII(prompt string) (string, error) {
	// Analyze for PII
	analyzeReq := PresidioAnalyzeRequest{
		Text:     prompt,
		Language: "en",
	}
	analyzeBody, _ := json.Marshal(analyzeReq)
	
	resp, err := p.client.Post(
		p.serviceURL+"/analyze",
		"application/json",
		bytes.NewBuffer(analyzeBody),
	)
	if err != nil {
		return "", fmt.Errorf("presidio analyze failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("presidio analyze error %d: %s", resp.StatusCode, body)
	}

	var analyzeResp PresidioAnalyzeResponse
	if err := json.NewDecoder(resp.Body).Decode(&analyzeResp); err != nil {
		return "", fmt.Errorf("decode analyze response: %w", err)
	}

	// If no PII found, return original
	if !analyzeResp.HasPII {
		return prompt, nil
	}

	// Anonymize
	anonymizeReq := PresidioAnonymizeRequest{
		Text: prompt,
	}
	anonymizeBody, _ := json.Marshal(anonymizeReq)
	
	resp, err = p.client.Post(
		p.serviceURL+"/anonymize",
		"application/json",
		bytes.NewBuffer(anonymizeBody),
	)
	if err != nil {
		return "", fmt.Errorf("presidio anonymize failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("presidio anonymize error %d: %s", resp.StatusCode, body)
	}

	var anonymizeResp PresidioAnonymizeResponse
	if err := json.NewDecoder(resp.Body).Decode(&anonymizeResp); err != nil {
		return "", fmt.Errorf("decode anonymize response: %w", err)
	}

	return anonymizeResp.Text, nil
}

func (p *PresidioMiddleware) Handle(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "failed to read request", http.StatusBadRequest)
			return
		}
		r.Body.Close()

		var payload map[string]interface{}
		if err := json.Unmarshal(body, &payload); err != nil {
			http.Error(w, "invalid json", http.StatusBadRequest)
			return
		}

		if prompt, ok := payload["prompt"].(string); ok {
			scrubbedPrompt, err := p.ScrubPII(prompt)
			if err != nil {
				http.Error(w, fmt.Sprintf("PII scrubbing failed: %v", err), http.StatusInternalServerError)
				return
			}
			payload["prompt"] = scrubbedPrompt
		}

		scrubbedBody, _ := json.Marshal(payload)
		r.Body = io.NopCloser(bytes.NewBuffer(scrubbedBody))
		r.ContentLength = int64(len(scrubbedBody))

		next.ServeHTTP(w, r)
	})
}
