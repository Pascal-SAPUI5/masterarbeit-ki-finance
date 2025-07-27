#!/bin/bash
#
# Ollama Integration Test Runner
# =============================
# Run comprehensive tests for Ollama integration
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$TEST_DIR")"
VENV_PATH="$PROJECT_ROOT/venv"
RESULTS_DIR="$TEST_DIR/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        print_success "Python 3 installed: $(python3 --version)"
    else
        print_error "Python 3 not found"
        exit 1
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker installed: $(docker --version)"
    else
        print_error "Docker not found"
        exit 1
    fi
    
    # Check Ollama container
    if docker ps | grep -q ollama; then
        print_success "Ollama container running"
    else
        print_warning "Ollama container not running"
        echo "Starting Ollama container..."
        docker start ollama || docker run -d --name ollama -p 11434:11434 ollama/ollama
        sleep 5
    fi
    
    # Check Ollama API
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        print_success "Ollama API accessible"
    else
        print_error "Ollama API not accessible"
        exit 1
    fi
    
    # Check phi3:mini model
    if curl -s http://localhost:11434/api/tags | grep -q "phi3:mini"; then
        print_success "phi3:mini model available"
    else
        print_warning "phi3:mini model not found, pulling..."
        docker exec ollama ollama pull phi3:mini
    fi
}

setup_environment() {
    print_header "Setting Up Test Environment"
    
    # Activate virtual environment
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
        print_success "Virtual environment activated"
    else
        print_warning "Virtual environment not found, using system Python"
    fi
    
    # Install test dependencies
    pip install -q pytest pytest-cov pytest-benchmark pytest-timeout pytest-xdist matplotlib psutil
    print_success "Test dependencies installed"
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    print_success "Results directory created: $RESULTS_DIR"
}

run_infrastructure_tests() {
    print_header "Running Infrastructure Tests"
    
    pytest "$TEST_DIR/test_infrastructure.py" -v \
        --tb=short \
        --junit-xml="$RESULTS_DIR/infrastructure_$TIMESTAMP.xml" \
        2>&1 | tee "$RESULTS_DIR/infrastructure_$TIMESTAMP.log"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_success "Infrastructure tests passed"
    else
        print_error "Infrastructure tests failed"
        return 1
    fi
}

run_functional_tests() {
    print_header "Running Functional Tests"
    
    pytest "$TEST_DIR/test_functional.py" -v \
        --tb=short \
        --junit-xml="$RESULTS_DIR/functional_$TIMESTAMP.xml" \
        2>&1 | tee "$RESULTS_DIR/functional_$TIMESTAMP.log"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_success "Functional tests passed"
    else
        print_error "Functional tests failed"
        return 1
    fi
}

run_integration_tests() {
    print_header "Running Integration Tests"
    
    pytest "$TEST_DIR/test_integration.py" -v \
        -m integration \
        --tb=short \
        --junit-xml="$RESULTS_DIR/integration_$TIMESTAMP.xml" \
        2>&1 | tee "$RESULTS_DIR/integration_$TIMESTAMP.log"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_success "Integration tests passed"
    else
        print_error "Integration tests failed"
        return 1
    fi
}

run_performance_tests() {
    print_header "Running Performance Tests"
    
    pytest "$TEST_DIR/test_performance.py" -v \
        -m slow \
        --tb=short \
        --benchmark-only \
        --junit-xml="$RESULTS_DIR/performance_$TIMESTAMP.xml" \
        2>&1 | tee "$RESULTS_DIR/performance_$TIMESTAMP.log"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_success "Performance tests passed"
    else
        print_error "Performance tests failed"
        return 1
    fi
}

run_all_tests() {
    print_header "Running All Tests"
    
    pytest "$TEST_DIR" -v \
        --tb=short \
        --cov=src \
        --cov-report=html:"$RESULTS_DIR/coverage_$TIMESTAMP" \
        --cov-report=term \
        --junit-xml="$RESULTS_DIR/all_tests_$TIMESTAMP.xml" \
        2>&1 | tee "$RESULTS_DIR/all_tests_$TIMESTAMP.log"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_success "All tests passed"
        echo -e "\n${GREEN}Coverage report available at: $RESULTS_DIR/coverage_$TIMESTAMP/index.html${NC}"
    else
        print_error "Some tests failed"
        return 1
    fi
}

generate_report() {
    print_header "Generating Test Report"
    
    REPORT_FILE="$RESULTS_DIR/test_report_$TIMESTAMP.md"
    
    cat > "$REPORT_FILE" << EOF
# Ollama Integration Test Report
**Generated**: $(date)

## Test Summary

### Infrastructure Tests
$(grep -c "PASSED" "$RESULTS_DIR/infrastructure_$TIMESTAMP.log" 2>/dev/null || echo "0") passed
$(grep -c "FAILED" "$RESULTS_DIR/infrastructure_$TIMESTAMP.log" 2>/dev/null || echo "0") failed

### Functional Tests
$(grep -c "PASSED" "$RESULTS_DIR/functional_$TIMESTAMP.log" 2>/dev/null || echo "0") passed
$(grep -c "FAILED" "$RESULTS_DIR/functional_$TIMESTAMP.log" 2>/dev/null || echo "0") failed

### Integration Tests
$(grep -c "PASSED" "$RESULTS_DIR/integration_$TIMESTAMP.log" 2>/dev/null || echo "0") passed
$(grep -c "FAILED" "$RESULTS_DIR/integration_$TIMESTAMP.log" 2>/dev/null || echo "0") failed

### Performance Tests
$(grep -c "PASSED" "$RESULTS_DIR/performance_$TIMESTAMP.log" 2>/dev/null || echo "0") passed
$(grep -c "FAILED" "$RESULTS_DIR/performance_$TIMESTAMP.log" 2>/dev/null || echo "0") failed

## System Information
- Python: $(python3 --version)
- Docker: $(docker --version)
- Ollama Model: phi3:mini

## Test Artifacts
- Logs: $RESULTS_DIR/*_$TIMESTAMP.log
- Coverage: $RESULTS_DIR/coverage_$TIMESTAMP/index.html
- JUnit XML: $RESULTS_DIR/*_$TIMESTAMP.xml
EOF
    
    print_success "Test report generated: $REPORT_FILE"
}

# Main execution
main() {
    echo -e "${BLUE}Ollama Integration Test Suite${NC}"
    echo -e "${BLUE}=============================${NC}\n"
    
    # Parse command line arguments
    TEST_TYPE="${1:-all}"
    
    # Always check prerequisites
    check_prerequisites
    setup_environment
    
    # Run requested tests
    case "$TEST_TYPE" in
        infrastructure)
            run_infrastructure_tests
            ;;
        functional)
            run_functional_tests
            ;;
        integration)
            run_integration_tests
            ;;
        performance)
            run_performance_tests
            ;;
        all)
            run_all_tests
            ;;
        *)
            echo "Usage: $0 [infrastructure|functional|integration|performance|all]"
            exit 1
            ;;
    esac
    
    # Generate report
    generate_report
    
    print_header "Test Execution Complete"
    echo -e "Results saved to: ${BLUE}$RESULTS_DIR${NC}"
}

# Run main function
main "$@"