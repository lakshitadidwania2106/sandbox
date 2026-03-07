#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIFROST_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BIFROST_BIN="$BIFROST_ROOT/tmp/bifrost-http"
CONFIG_FILE="$SCRIPT_DIR/config-with-mocker.json"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Bifrost Security Plugin Test Runner               ║${NC}"
echo -e "${BLUE}║              (with Mocker Backend)                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}✗ Error: Configuration file not found${NC}"
    echo -e "  Expected: $CONFIG_FILE"
    exit 1
fi

# Check if Bifrost is already built
if [ -f "$BIFROST_BIN" ]; then
    echo -e "${GREEN}✓ Bifrost binary found${NC}"
    echo -e "  Location: $BIFROST_BIN"
else
    echo -e "${YELLOW}⚠ Bifrost binary not found, building now...${NC}"
    echo ""
    
    # Change to bifrost directory and build
    cd "$BIFROST_ROOT" || exit 1
    
    echo -e "${BLUE}→ Running 'make build' in $BIFROST_ROOT${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if make build; then
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✓ Build completed successfully${NC}"
        echo ""
    else
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}✗ Build failed${NC}"
        echo -e "  Please check the error messages above and try again."
        exit 1
    fi
    
    # Verify binary was created
    if [ ! -f "$BIFROST_BIN" ]; then
        echo -e "${RED}✗ Build succeeded but binary not found at expected location${NC}"
        echo -e "  Expected: $BIFROST_BIN"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                Starting Bifrost Server                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo -e "  • Config file: config-with-mocker.json"
echo -e "  • Backend: Mocker (simulated AI responses)"
echo -e "  • Security plugin: Enabled"
echo -e "  • Server URL: ${GREEN}http://localhost:8080${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Start Bifrost with the mocker configuration
cd "$SCRIPT_DIR" || exit 1
# Create a temporary app directory since bifrost-http expects a directory with config.json
TMP_APP_DIR="$SCRIPT_DIR/tmp_app_data"
mkdir -p "$TMP_APP_DIR"
cp "$CONFIG_FILE" "$TMP_APP_DIR/config.json"

exec "$BIFROST_BIN" -app-dir "$TMP_APP_DIR"
