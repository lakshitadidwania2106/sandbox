#!/bin/bash

echo "=========================================="
echo "🌈 Starting Bifrost-Protected Application"
echo "=========================================="
echo ""

# Check dependencies
echo "Checking dependencies..."
python3 -c "from security.lakera_guard import scan_prompt; from security.presidio_scanner import scan_output" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Security modules loaded"
else
    echo "❌ Security modules not found"
    exit 1
fi

echo ""
echo "Starting Flask application with Bifrost security..."
echo "  → URL: http://localhost:5000"
echo "  → Security Layers:"
echo "    • Layer 1: Lakera Guard (Prompt Injection Detection)"
echo "    • Layer 2: OPA Policy (Access Control)"
echo "    • Layer 3: Presidio Input (PII Scrubbing)"
echo "    • Layer 4: Presidio Output (Response Protection)"
echo ""
echo "=========================================="
echo ""

cd /home/unichronic/sandbox
python3 app.py
