#!/bin/bash

echo "🛡️  Starting Bifrost Security Dashboard..."
echo ""

# Kill any existing Flask processes
pkill -9 -f "dashboard_app.py" 2>/dev/null
sleep 1

cd /home/unichronic/sandbox
python3 dashboard_app.py
