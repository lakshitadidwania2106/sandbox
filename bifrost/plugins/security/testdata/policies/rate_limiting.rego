package bifrost.security

# Rate limiting policy
# This policy enforces rate limits based on user roles and request patterns

default allow = true

# Define rate limits per role (requests per minute)
rate_limits := {
    "admin": 1000,
    "power_user": 500,
    "developer": 200,
    "user": 100,
    "guest": 20
}

# Get rate limit for user role
user_rate_limit = limit {
    input.context.user_role
    limit := rate_limits[input.context.user_role]
} else = 50  # Default limit

# Deny if rate limit exceeded (this would need external state tracking in production)
deny[msg] {
    # In a real implementation, this would check against a rate limiting service
    # For now, this is a placeholder showing the policy structure
    input.context.request_count
    input.context.request_count > user_rate_limit
    msg := sprintf("Rate limit exceeded: %d requests (limit: %d)", [input.context.request_count, user_rate_limit])
}

# Deny expensive operations for low-tier users
deny[msg] {
    expensive_models := ["gpt-4", "claude-3-opus", "gemini-ultra"]
    input.request.model
    model := expensive_models[_]
    contains(input.request.model, model)
    
    low_tier_roles := ["guest", "user"]
    input.context.user_role == low_tier_roles[_]
    
    msg := sprintf("Request blocked: model '%s' not available for role '%s'", [input.request.model, input.context.user_role])
}

# Allow if no deny rules matched
allow {
    count(deny) == 0
}

# Provide reason
reason = msg {
    count(deny) > 0
    msg := deny[_]
} else = "Request within rate limits"
