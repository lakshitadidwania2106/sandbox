package middleware

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

type LakeraMiddleware struct {
	apiKey    string
	apiURL    string
	threshold float64
	client    *http.Client
}

func NewLakeraMiddleware() *LakeraMiddleware {
	apiKey := os.Getenv("LAKERA_API_KEY")
	apiURL := os.Getenv("LAKERA_API_URL")
	if apiURL == "" {
		apiURL = "https://api.lakera.ai"
	}
	return &LakeraMiddleware{
		apiKey: apiKey,
		apiURL: apiURL,
		client: &http.Client{},
	}
}

func (l *LakeraMiddleware) CheckPromptInjection(text string) (bool, string) {
	if l.apiKey == "" {
		return false, ""
	}

	reqBody, _ := json.Marshal(map[string]string{"input": text})
	req, _ := http.NewRequest("POST", l.apiURL+"/v1/prompt_injection", bytes.NewBuffer(reqBody))
	req.Header.Set("Authorization", "Bearer "+l.apiKey)
	req.Header.Set("Content-Type", "application/json")

	resp, err := l.client.Do(req)
	if err != nil {
		return false, ""
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	if flagged, ok := result["flagged"].(bool); ok && flagged {
		return true, fmt.Sprintf("prompt injection detected")
	}

	return false, ""
}
