package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"

	"bifrost/middleware"
)

func main() {
	targetURL := os.Getenv("AI_AGENT_URL")
	if targetURL == "" {
		log.Fatal("AI_AGENT_URL environment variable required")
	}

	target, err := url.Parse(targetURL)
	if err != nil {
		log.Fatal(err)
	}

	// Initialize all security layers
	lakera := middleware.NewLakeraMiddleware()
	opa := middleware.NewOPAMiddleware()
	presidioInput := middleware.NewPresidioMiddleware()
	presidioOutput := middleware.NewPresidioMiddleware()

	gateway := &BifrostGateway{
		target:         target,
		lakera:         lakera,
		opa:            opa,
		presidioInput:  presidioInput,
		presidioOutput: presidioOutput,
	}

	http.HandleFunc("/", gateway.Handle)
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🌈 Bifrost Gateway listening on :%s", port)
	log.Printf("   → AI Agent: %s", targetURL)
	log.Printf("   → Security Layers: Lakera ✓ | OPA ✓ | Presidio ✓")
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

type BifrostGateway struct {
	target         *url.URL
	lakera         *middleware.LakeraMiddleware
	opa            *middleware.OPAMiddleware
	presidioInput  *middleware.PresidioMiddleware
	presidioOutput *middleware.PresidioMiddleware
}

func (g *BifrostGateway) Handle(w http.ResponseWriter, r *http.Request) {
	// Read request
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

	// Extract text for security checks
	text := g.extractText(payload)

	// ═══ INPUT PIPELINE ═══
	
	// Layer 1: Lakera Prompt Injection Detection
	if blocked, reason := g.lakera.CheckPromptInjection(text); blocked {
		log.Printf("🚫 Lakera blocked: %s", reason)
		http.Error(w, "Security threat detected: "+reason, http.StatusForbidden)
		return
	}

	// Layer 2: OPA Policy Check
	if allowed, reason := g.opa.CheckPolicy(r, payload); !allowed {
		log.Printf("🚫 OPA blocked: %s", reason)
		http.Error(w, "Policy violation: "+reason, http.StatusForbidden)
		return
	}

	// Layer 3: Presidio Input PII Scrubbing
	scrubbedText, err := g.presidioInput.ScrubPII(text)
	if err != nil {
		log.Printf("⚠️  Presidio input scrubbing failed: %v", err)
	} else {
		g.replaceText(payload, scrubbedText)
	}

	// Forward to AI agent
	scrubbedBody, _ := json.Marshal(payload)
	proxyReq, _ := http.NewRequest(r.Method, g.target.String()+r.URL.Path, bytes.NewBuffer(scrubbedBody))
	proxyReq.Header = r.Header.Clone()

	client := &http.Client{}
	resp, err := client.Do(proxyReq)
	if err != nil {
		http.Error(w, "agent request failed", http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	// Read response
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "failed to read response", http.StatusInternalServerError)
		return
	}

	// ═══ OUTPUT PIPELINE ═══
	
	// Layer 4: Presidio Output PII Scrubbing
	var respPayload map[string]interface{}
	if json.Unmarshal(respBody, &respPayload) == nil {
		responseText := g.extractResponseText(respPayload)
		scrubbedResponse, err := g.presidioOutput.ScrubPII(responseText)
		if err != nil {
			log.Printf("⚠️  Presidio output scrubbing failed: %v", err)
		} else {
			g.replaceResponseText(respPayload, scrubbedResponse)
		}
		respBody, _ = json.Marshal(respPayload)
	}

	// Return scrubbed response
	for k, v := range resp.Header {
		w.Header()[k] = v
	}
	w.WriteHeader(resp.StatusCode)
	w.Write(respBody)
	
	log.Printf("✅ Request processed through all security layers")
}

func (g *BifrostGateway) extractText(payload map[string]interface{}) string {
	// OpenAI/Anthropic messages format
	if messages, ok := payload["messages"].([]interface{}); ok {
		for _, msg := range messages {
			if m, ok := msg.(map[string]interface{}); ok {
				if content, ok := m["content"].(string); ok {
					return content
				}
			}
		}
	}
	// Legacy prompt format
	if prompt, ok := payload["prompt"].(string); ok {
		return prompt
	}
	return ""
}

func (g *BifrostGateway) replaceText(payload map[string]interface{}, newText string) {
	if messages, ok := payload["messages"].([]interface{}); ok {
		for _, msg := range messages {
			if m, ok := msg.(map[string]interface{}); ok {
				if _, ok := m["content"].(string); ok {
					m["content"] = newText
					return
				}
			}
		}
	}
	if _, ok := payload["prompt"].(string); ok {
		payload["prompt"] = newText
	}
}

func (g *BifrostGateway) extractResponseText(payload map[string]interface{}) string {
	// OpenAI format
	if choices, ok := payload["choices"].([]interface{}); ok {
		for _, choice := range choices {
			if c, ok := choice.(map[string]interface{}); ok {
				if message, ok := c["message"].(map[string]interface{}); ok {
					if content, ok := message["content"].(string); ok {
						return content
					}
				}
				if text, ok := c["text"].(string); ok {
					return text
				}
			}
		}
	}
	// Anthropic format
	if content, ok := payload["content"].([]interface{}); ok {
		for _, item := range content {
			if c, ok := item.(map[string]interface{}); ok {
				if text, ok := c["text"].(string); ok {
					return text
				}
			}
		}
	}
	return ""
}

func (g *BifrostGateway) replaceResponseText(payload map[string]interface{}, newText string) {
	if choices, ok := payload["choices"].([]interface{}); ok {
		for _, choice := range choices {
			if c, ok := choice.(map[string]interface{}); ok {
				if message, ok := c["message"].(map[string]interface{}); ok {
					if _, ok := message["content"].(string); ok {
						message["content"] = newText
						return
					}
				}
				if _, ok := c["text"].(string); ok {
					c["text"] = newText
					return
				}
			}
		}
	}
	if content, ok := payload["content"].([]interface{}); ok {
		for _, item := range content {
			if c, ok := item.(map[string]interface{}); ok {
				if _, ok := c["text"].(string); ok {
					c["text"] = newText
					return
				}
			}
		}
	}
}
