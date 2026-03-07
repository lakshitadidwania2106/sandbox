#!/bin/bash

# Setup Script for Bifrost Proprietary Code Detection Plugin
# ===========================================================

set -e

echo "=========================================="
echo "Bifrost Proprietary Code Detection Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "bifrost" ]; then
    echo -e "${RED}Error: bifrost directory not found${NC}"
    echo "Please run this script from the sandbox directory"
    exit 1
fi

echo ""
echo "Step 1: Creating plugin directory..."
mkdir -p bifrost/plugins/proprietary-detection
echo -e "${GREEN}✓ Plugin directory created${NC}"

echo ""
echo "Step 2: Copying plugin code..."
cp bifrost_plugin_proprietary_detection.go bifrost/plugins/proprietary-detection/main.go
echo -e "${GREEN}✓ Plugin code copied${NC}"

echo ""
echo "Step 3: Building plugin..."
cd bifrost/plugins/proprietary-detection

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo -e "${RED}Error: Go is not installed${NC}"
    echo "Please install Go: https://golang.org/doc/install"
    exit 1
fi

# Build the plugin
go build -buildmode=plugin -o proprietary_detection.so main.go

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Plugin built successfully${NC}"
else
    echo -e "${RED}✗ Plugin build failed${NC}"
    exit 1
fi

cd ../../..

echo ""
echo "Step 4: Setting up proprietary code directory..."
if [ ! -d "proprietary_code" ]; then
    mkdir -p proprietary_code
    echo -e "${GREEN}✓ Proprietary code directory created${NC}"
else
    echo -e "${YELLOW}⚠ Proprietary code directory already exists${NC}"
fi

# Check if there are any code files
CODE_FILES=$(find proprietary_code -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" \) 2>/dev/null | wc -l)
if [ "$CODE_FILES" -eq 0 ]; then
    echo -e "${YELLOW}⚠ No proprietary code files found${NC}"
    echo "  Please add your proprietary code files to: ./proprietary_code/"
else
    echo -e "${GREEN}✓ Found $CODE_FILES proprietary code files${NC}"
fi

echo ""
echo "Step 5: Creating plugin configuration..."

# Create a sample config file
c`````````````````1``1```````````````````````11```````````````````````````````````````````````````````````````````````````````````````````````````1`````````````````````````````````````````````````````````````````````````````1``````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````'EOF'
{
  "plugins": [
    {
      "name": "proprietary-detection",
      "path": "./plugins/proprietary-detection/proprietary_detection.so",
      "enabled": true,
      "config": {
        "proprietary_code_dir": "./proprietary_code",
        "similarity_threshold": 60,
        "block_on_detection": true,
        "log_only": false,
        "monitored_request_types": []
      }
    }
  ]
}
EOF

echo -e "${GREEN}✓ Configuration file created: bifrost_plugin_config.json${NC}"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add your proprietary code:"
echo "   ${YELLOW}cp /path/to/your/code/*.py proprietary_code/${NC}"
echo ""
echo "2. Add the plugin to your Bifrost configuration:"
echo "   ${YELLOW}# Merge bifrost_plugin_config.json into your Bifrost config${NC}"
echo ""
echo "3. Restart Bifrost:"
echo "   ${YELLOW}cd bifrost && ./bifrost restart${NC}"
echo ""
echo "4. Test the plugin:"
echo "   ${YELLOW}python test_bifrost_plugin.py${NC}"
echo ""
echo "For detailed instructions, see: ${GREEN}BIFROST_INTEGRATION_GUIDE.md${NC}"
echo ""
