#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIFROST_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}=== Bifrost Build and Run Script ===${NC}"
echo -e "${BLUE}Building Go binary only (skipping UI)${NC}\n"

# Create tmp directory if it doesn't exist
echo -e "${YELLOW}Creating tmp directory...${NC}"
mkdir -p "$BIFROST_ROOT/tmp"

# Build the Go binary
echo -e "${YELLOW}Building Bifrost HTTP binary...${NC}"
cd "$BIFROST_ROOT/transports/bifrost-http" || exit 1

if go build -o ../../tmp/bifrost-http .; then
    echo -e "${GREEN}✓ Build successful${NC}\n"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Run Bifrost with mocker config
echo -e "${BLUE}Starting Bifrost with mocker configuration...${NC}"
cd "$SCRIPT_DIR" || exit 1

CONFIG_FILE="$SCRIPT_DIR/config-with-mocker.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}✗ Config file not found: $CONFIG_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}Using config: $CONFIG_FILE${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop Bifrost${NC}\n"

"$BIFROST_ROOT/tmp/bifrost-http" -config "$CONFIG_FILE"
