#!/bin/bash

# Start secured MCP chat with Bifrost security layers

cd "$(dirname "$0")"

echo "🛡️  Starting Secured Notion MCP Chat"
echo "Security Layers: OPA → Lakera → Presidio"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Copy .env.example to .env and add your keys"
    exit 1
fi

# Check dependencies
python3 -c "import mcp" 2>/dev/null || {
    echo "❌ MCP not installed. Installing..."
    pip install mcp
}

python3 -c "import sys; sys.path.insert(0, '..'); from security.lakera_guard import scan_prompt" 2>/dev/null || {
    echo "❌ Security modules not found"
    echo "Make sure security/ directory exists in parent folder"
    exit 1
}

# Run secured chat
python3 chat_app_secured.py
