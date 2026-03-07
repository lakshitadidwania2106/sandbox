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
	serviceURL string
	client     *http.Client
}

type LakeraResponse struct {
	Flagged     bool   `json:"flagged"`
	RequestUUID string `json:"request_uuid"`
	Error       string `json:"error"`
}

func NewLakeraMiddleware() *LakeraMiddleware {
	serviceURL := os.Getenv("SECURITY_SERVICE_URL")
	if serviceURL == "" {
		serviceURL = "http://localhost:5000"
	}
	return &LakeraMiddleware{
		serviceURL: serviceURL,
		client:     &http.Client{},
	}
}

func (l *LakeraMiddleware) CheckPromptInjection(text string) (bool, string) {
	reqBody, _ := json.Marshal(map[string]string{"text": text})
	
	resp, err := l.client.Post(
		l.serviceURL+"/lakera/scan",
		"application/json",
		bytes.NewBuffer(reqBody),
	)
	if err != nil {
		return false, ""
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return false, ""
	}

	body, _ := io.ReadAll(resp.Body)
	var result LakeraResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return false, ""
	}

	if result.Flagged {
		return true, fmt.Sprintf("prompt injection detected (ID: %s)", result.RequestUUID)
	}

	return false, ""
}

