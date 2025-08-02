#!/bin/bash
"""
Docker Container Entrypoint Script
==================================

This script handles the startup sequence for the Docker container with
Chrome/Chromium browser support and research automation capabilities.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to start virtual display
start_virtual_display() {
    echo_info "Starting virtual display server..."
    
    # Kill any existing Xvfb processes
    pkill Xvfb || true
    
    # Start Xvfb
    Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    export XVFB_PID=$!
    
    # Set display environment
    export DISPLAY=:99
    
    # Wait for display to be ready
    sleep 3
    
    # Verify display is working
    if xdpyinfo -display :99 >/dev/null 2>&1; then
        echo_success "Virtual display started successfully (PID: $XVFB_PID)"
    else
        echo_error "Failed to start virtual display"
        return 1
    fi
}

# Function to check Chrome installation
check_chrome() {
    echo_info "Checking Chrome/Chromium installation..."
    
    CHROME_BIN=${CHROME_BIN:-/usr/bin/chromium-browser}
    
    if [ ! -f "$CHROME_BIN" ]; then
        echo_error "Chrome binary not found at $CHROME_BIN"
        return 1
    fi
    
    # Test Chrome version
    if $CHROME_BIN --version >/dev/null 2>&1; then
        VERSION=$($CHROME_BIN --version)
        echo_success "Chrome available: $VERSION"
    else
        echo_error "Chrome binary exists but cannot execute"
        return 1
    fi
    
    # Test ChromeDriver
    if [ -f "/usr/bin/chromedriver" ]; then
        DRIVER_VERSION=$(chromedriver --version 2>/dev/null || echo "Unknown")
        echo_success "ChromeDriver available: $DRIVER_VERSION"
    else
        echo_warning "ChromeDriver not found at /usr/bin/chromedriver"
    fi
}

# Function to setup directories
setup_directories() {
    echo_info "Setting up application directories..."
    
    # Create required directories
    mkdir -p /app/.claude_memory
    mkdir -p /app/research/q1-sources
    mkdir -p /app/research/search-results
    mkdir -p /app/output
    mkdir -p /app/writing/chapters
    mkdir -p /app/browser_data
    mkdir -p /app/cookies
    
    # Set permissions
    chmod -R 755 /app/browser_data
    chmod -R 755 /app/cookies
    
    echo_success "Directories created and configured"
}

# Function to run browser health check
run_browser_health_check() {
    echo_info "Running browser health check..."
    
    if python3 /app/scripts/test_browser_docker.py --quick-check; then
        echo_success "Browser health check passed"
        return 0
    else
        echo_warning "Browser health check failed - continuing anyway"
        return 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo_info "Cleaning up..."
    
    # Kill Xvfb if we started it
    if [ ! -z "$XVFB_PID" ]; then
        kill $XVFB_PID 2>/dev/null || true
        echo_success "Virtual display stopped"
    fi
    
    # Kill any remaining Chrome processes
    pkill -f chromium-browser || true
    pkill -f chrome || true
    
    echo_success "Cleanup completed"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Main startup sequence
main() {
    echo_info "=== Docker Container Startup ==="
    echo_info "Container: Master Thesis AI Finance"
    echo_info "Python: $(python3 --version)"
    echo_info "Working Directory: $(pwd)"
    echo_info "User: $(whoami)"
    
    # Step 1: Setup directories
    setup_directories
    
    # Step 2: Start virtual display
    if ! start_virtual_display; then
        echo_error "Failed to start virtual display"
        exit 1
    fi
    
    # Step 3: Check Chrome installation
    if ! check_chrome; then
        echo_error "Chrome check failed"
        exit 1
    fi
    
    # Step 4: Run health check (optional)
    run_browser_health_check || true
    
    echo_success "=== Startup Complete ==="
    echo_info "Starting main application..."
    
    # Execute the main command
    exec "$@"
}

# Special handling for health checks
if [ "$1" = "healthcheck" ]; then
    echo_info "Running health check..."
    
    # Check if main process is running
    if pgrep -f "python.*mcp_server" >/dev/null; then
        echo_success "MCP server is running"
        exit 0
    else
        echo_error "MCP server is not running"
        exit 1
    fi
fi

# Special handling for browser tests
if [ "$1" = "test-browser" ]; then
    setup_directories
    start_virtual_display
    check_chrome
    
    echo_info "Running comprehensive browser tests..."
    python3 /app/scripts/test_browser_docker.py
    exit $?
fi

# Run main startup sequence
main "$@"