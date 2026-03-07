package bifrost.security

# Tool Validation Policy for Testing
# This policy validates tool execution requests

default allow = false

# Allow safe read-only tools
is_allowed_tool {
    safe_tools := [
        "read_file",
        "list_directory", 
        "search",
        "get_weather",
        "calculate",
        "get_time"
    ]
    input.tool_name
    input.tool_name == safe_tools[_]
}

# Allow file write for admin users
is_allowed_tool {
    input.tool_name == "write_file"
    input.context.user_role == "admin"
}

# Allow file write for developers in workspace directory
is_allowed_tool {
    input.tool_name == "write_file"
    input.context.user_role == "developer"
    input.tool_arguments.path
    startswith(input.tool_arguments.path, "/workspace/")
}

# Deny dangerous command patterns
deny[msg] {
    input.tool_name == "execute_command"
    input.tool_arguments.command
    dangerous_patterns := [
        "rm -rf",
        "dd if=",
        "mkfs",
        "curl | sh",
        "wget | bash",
        "eval",
        "exec"
    ]
    pattern := dangerous_patterns[_]
    contains(input.tool_arguments.command, pattern)
    msg := sprintf("Tool execution blocked: dangerous command pattern '%s' detected", [pattern])
}

# Deny path traversal attempts
deny[msg] {
    input.tool_arguments.path
    contains(input.tool_arguments.path, "../")
    msg := "Tool execution blocked: path traversal attempt detected (../)"
}

# Deny access to sensitive files
deny[msg] {
    input.tool_arguments.path
    sensitive_patterns := [
        "/etc/passwd",
        "/etc/shadow",
        ".ssh/",
        ".aws/credentials",
        ".env",
        "id_rsa"
    ]
    pattern := sensitive_patterns[_]
    contains(input.tool_arguments.path, pattern)
    msg := sprintf("Tool execution blocked: access to sensitive file pattern '%s'", [pattern])
}

# Deny database writes for non-admins
deny[msg] {
    db_write_tools := ["write_database", "update_database", "delete_from_database"]
    input.tool_name == db_write_tools[_]
    input.context.user_role != "admin"
    msg := sprintf("Tool execution blocked: '%s' requires admin role", [input.tool_name])
}

# Final allow check - must pass all deny rules
allow {
    is_allowed_tool
    count(deny) == 0
}

# Provide reason for decision
reason = msg {
    count(deny) > 0
    msg := concat("; ", deny)
} else = msg {
    allow
    msg := sprintf("Tool '%s' allowed by policy", [input.tool_name])
} else = msg {
    msg := sprintf("Tool '%s' not in allowed list", [input.tool_name])
}

# Set HTTP status code for blocked requests
status_code = 403 {
    not allow
}
