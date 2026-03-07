#!/bin/bash

# Cleanup script for Bifrost Security Plugin Test Environment
# This script stops all services and cleans up test artifacts

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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Stop Presidio services
stop_presidio() {
    print_header "Stopping Presidio Services"
    
    if [ -f "docker-compose.yml" ]; then
        print_info "Stopping Docker containers..."
        docker-compose down
        print_success "Presidio services stopped"
    else
        print_warning "docker-compose.yml not found, skipping"
    fi
}

# Stop Bifrost
stop_bifrost() {
    print_header "Stopping Bifrost"
    
    print_info "Looking for Bifrost processes..."
    BIFROST_PIDS=$(pgrep -f "bifrost.*config.*security-plugin-test" || true)
    
    if [ -n "$BIFROST_PIDS" ]; then
        print_info "Found Bifrost process(es): $BIFROST_PIDS"
        echo "$BIFROST_PIDS" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        print_success "Bifrost stopped"
    else
        print_info "No Bifrost processes found"
    fi
}

# Clean logs
clean_logs() {
    print_header "Cleaning Logs"
    
    if [ -d "logs" ]; then
        read -p "Do you want to delete log files? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf logs/*
            print_success "Logs cleaned"
        else
            print_info "Keeping logs"
        fi
    else
        print_info "No logs directory found"
    fi
}

# Clean Docker volumes
clean_docker() {
    print_header "Cleaning Docker Resources"
    
    read -p "Do you want to remove Docker volumes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v 2>/dev/null || true
        print_success "Docker volumes removed"
    else
        print_info "Keeping Docker volumes"
    fi
}

# Display status
show_status() {
    print_header "Cleanup Complete"
    
    echo -e "${GREEN}Test environment cleaned up!${NC}\n"
    
    echo -e "${BLUE}Status:${NC}"
    
    # Check Presidio
    if docker ps | grep -q presidio; then
        echo -e "  Presidio: ${YELLOW}Still running${NC}"
    else
        echo -e "  Presidio: ${GREEN}Stopped${NC}"
    fi
    
    # Check Bifrost
    if pgrep -f "bifrost.*config.*security-plugin-test" > /dev/null; then
        echo -e "  Bifrost: ${YELLOW}Still running${NC}"
    else
        echo -e "  Bifrost: ${GREEN}Stopped${NC}"
    fi
    
    # Check logs
    if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
        echo -e "  Logs: ${BLUE}Present${NC}"
    else
        echo -e "  Logs: ${GREEN}Cleaned${NC}"
    fi
    
    echo ""
}

# Main execution
main() {
    print_header "Bifrost Security Plugin Test Cleanup"
    
    stop_bifrost
    stop_presidio
    clean_logs
    clean_docker
    show_status
    
    echo -e "${BLUE}To restart the test environment, run:${NC}"
    echo -e "  ${YELLOW}./start-test-environment.sh${NC}\n"
}

# Run main function
main
