package middleware

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"os"
)

type OPAMiddleware struct {
	opaURL string
	client *http.Client
}

func NewOPAMiddleware() *OPAMiddleware {
	opaURL := os.Getenv("OPA_URL")
	if opaURL == "" {
		opaURL = "http://localhost:8181"
	}
	return &OPAMiddleware{
		opaURL: opaURL,
		client: &http.Client{},
	}
}

func (o *OPAMiddleware) CheckPolicy(r *http.Request, payload map[string]interface{}) (bool, string) {
	input := map[string]interface{}{
		"method": r.Method,
		"path":   r.URL.Path,
		"user":   r.Header.Get("X-User-ID"),
		"payload": payload,
	}

	reqBody, _ := json.Marshal(map[string]interface{}{"input": input})
	resp, err := o.client.Post(o.opaURL+"/v1/data/bifrost/allow", "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return true, ""
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	if resultData, ok := result["result"].(map[string]interface{}); ok {
		if allow, ok := resultData["allow"].(bool); ok && !allow {
			reason := "policy violation"
			if r, ok := resultData["reason"].(string); ok {
				reason = r
			}
			return false, reason
		}
	}

	return true, ""
}
