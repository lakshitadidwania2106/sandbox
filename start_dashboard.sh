#!/bin/bash

echo "=========================================="
echo "🛡️ Bifrost Security Testing Dashboard"
echo "=========================================="
echo ""

cd /home/unichronic/sandbox

echo "Starting Flask application..."
echo ""
echo "Available URLs:"
echo "  → Original App:  http://localhost:5000"
echo "  → Dashboard:     http://localhost:5000/dashboard"
echo ""
echo "=========================================="
echo ""

python3 app.py
