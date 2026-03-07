package bifrost.security

# Basic Request Validation Policy for Testing
# This is a simplified version for manual testing

default allow = false

# Block requests with high threat scores
deny[msg] {
    input.security.threat_score > 0.75
    msg := sprintf("Request blocked: threat score %.2f exceeds threshold", [input.security.threat_score])
}

# Block requests with SSN detected
deny[msg] {
    input.security.pii_detected
    count(input.security.pii_entities) > 0
    entity := input.security.pii_entities[_]
    entity.type == "SSN"
    msg := "Request blocked: SSN detected in prompt"
}

# Block requests with credit card information
deny[msg] {
    input.security.pii_detected
    entity := input.security.pii_entities[_]
    entity.type == "CREDIT_CARD"
    msg := "Request blocked: credit card number detected in prompt"
}

# Block requests with multiple PII entities
deny[msg] {
    input.security.pii_detected
    count(input.security.pii_entities) >= 3
    msg := sprintf("Request blocked: multiple PII entities detected (%d)", [count(input.security.pii_entities)])
}

# Block unapproved providers
deny[msg] {
    input.request.provider
    approved_providers := {"openai", "anthropic", "google", "azure"}
    not approved_providers[input.request.provider]
    msg := sprintf("Request blocked: provider '%s' not in approved list", [input.request.provider])
}

# Allow if no deny rules matched
allow {
    count(deny) == 0
}

# Provide reason for decision
reason = msg {
    count(deny) > 0
    msg := concat("; ", deny)
} else = "Request allowed by policy"

# Set HTTP status code for blocked requests
status_code = 403 {
    count(deny) > 0
}
