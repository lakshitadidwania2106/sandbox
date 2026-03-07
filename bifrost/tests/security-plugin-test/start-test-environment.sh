#!/bin/bash

# Bifrost Security Plugin Test Environment Setup Script
# This script sets up and starts the complete test environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
    else
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker compose &> /dev/null || docker compose version &> /dev/null; then
        print_success "Docker Compose is available"
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Go
    if command -v go &> /dev/null; then
        GO_VERSION=$(go version | awk '{print $3}')
        print_success "Go is installed ($GO_VERSION)"
    else
        print_warning "Go is not installed. You'll need it to build Bifrost."
    fi
    
    # Check for OpenAI API key
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "OPENAI_API_KEY is not set"
        echo "Please set your OpenAI API key:"
        echo "  export OPENAI_API_KEY=sk-your-key-here"
        echo ""
        read -p "Do you want to continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "OPENAI_API_KEY is set"
    fi
}

# Start Presidio services
start_presidio() {
    print_header "Starting Presidio Services"
    
    print_info "Starting Presidio Analyzer and Anonymizer..."
    docker compose up -d
    
    print_info "Waiting for Presidio services to be healthy..."
    sleep 5
    
    # Wait for analyzer
    MAX_RETRIES=30
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s -f http://localhost:5000/health > /dev/null 2>&1; then
            print_success "Presidio Analyzer is healthy"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -n "."
        sleep 2
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        print_error "Presidio Analyzer failed to start"
        docker compose logs presidio-analyzer
        exit 1
    fi
    
    # Wait for anonymizer
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s -f http://localhost:5001/health > /dev/null 2>&1; then
            print_success "Presidio Anonymizer is healthy"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -n "."
        sleep 2
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        print_error "Presidio Anonymizer failed to start"
        docker compose logs presidio-anonymizer
        exit 1
    fi
}

# Test Presidio
test_presidio() {
    print_header "Testing Presidio"
    
    print_info "Sending test request to Presidio..."
    RESPONSE=$(curl -s -X POST http://localhost:5000/analyze \
        -H "Content-Type: application/json" \
        -d '{
            "text": "My email is test@example.com and my phone is 555-1234",
            "language": "en"
        }')
    
    if echo "$RESPONSE" | grep -q "EMAIL"; then
        print_success "Presidio is working correctly (detected EMAIL)"
    else
        print_warning "Presidio response: $RESPONSE"
    fi
}

# Build Bifrost
build_bifrost() {
    print_header "Building Bifrost"
    
    # Check if we're in the right directory
    if [ ! -f "../../plugins/security/security.go" ]; then
        print_error "Cannot find security plugin. Are you in the right directory?"
        exit 1
    fi
    
    print_info "Building Bifrost from source..."
    # Correct path to repo root relative to script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR/../.."
    
    # Ensure Go is in PATH if we just installed it
    if [ -d "/home/unichronic/go-dist/go/bin" ]; then
        export GOROOT="/home/unichronic/go-dist/go"
        export PATH="$GOROOT/bin:$PATH"
    fi

    if [ -f "Makefile" ]; then
        make build-api-only
    else
        print_info "No Makefile found, building manually..."
        if [ -d "transports/bifrost-http" ]; then
            cd transports/bifrost-http
            go build -o ../../tmp/bifrost-http .
            cd ../..
        else
            print_error "Could not find transports/bifrost-http"
            exit 1
        fi
    fi
    
    if [ -f "bifrost" ]; then
        print_success "Bifrost built successfully"
    else
        print_error "Failed to build Bifrost"
        exit 1
    fi
    
    cd tests/security-plugin-test
}

# Create log directories
setup_logs() {
    print_header "Setting Up Log Directories"
    
    mkdir -p logs
    print_success "Log directories created"
}

# Display next steps
show_next_steps() {
    print_header "Setup Complete!"
    
    echo -e "${GREEN}Environment is ready for testing!${NC}\n"
    
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Start Bifrost in one terminal:"
    echo -e "   ${YELLOW}cd ../.. && ./bifrost --config tests/security-plugin-test/config.json${NC}\n"
    
    echo -e "2. Run tests in another terminal:"
    echo -e "   ${YELLOW}cd tests/security-plugin-test && ./test-security.sh${NC}\n"
    
    echo -e "${BLUE}Useful commands:${NC}"
    echo -e "  View Bifrost logs:    ${YELLOW}tail -f logs/bifrost.log${NC}"
    echo -e "  View security logs:   ${YELLOW}tail -f logs/security-audit.log${NC}"
    echo -e "  View Presidio logs:   ${YELLOW}docker compose logs -f${NC}"
    echo -e "  Stop Presidio:        ${YELLOW}docker compose down${NC}"
    echo -e "  Restart Presidio:     ${YELLOW}docker compose restart${NC}\n"
}

# Main execution
main() {
    print_header "Bifrost Security Plugin Test Environment Setup"
    
    check_prerequisites
    start_presidio
    test_presidio
    setup_logs
    
    # Ask if user wants to build Bifrost
    echo ""
    read -p "Do you want to build Bifrost now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_bifrost
    else
        print_info "Skipping Bifrost build. Make sure to build it before running tests."
    fi
    
    show_next_steps
}

# Run main function
main
