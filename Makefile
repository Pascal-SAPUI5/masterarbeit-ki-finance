# Master Thesis AI Finance - Docker Management
# ============================================

# Variables
DOCKER_IMAGE = masterarbeit-ai-finance
DOCKER_TAG = latest
CONTAINER_NAME = masterarbeit-mcp-server
NETWORK_NAME = masterarbeit-net

# Colors for output
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help build run stop clean test logs browser-test health-check dev-build

# Default target
help:
	@echo "$(BLUE)Master Thesis AI Finance - Docker Commands$(NC)"
	@echo "================================================"
	@echo ""
	@echo "$(GREEN)Build Commands:$(NC)"
	@echo "  build         - Build Docker image"
	@echo "  dev-build     - Build with development optimizations"
	@echo "  rebuild       - Clean build (no cache)"
	@echo ""
	@echo "$(GREEN)Run Commands:$(NC)"
	@echo "  run           - Run the full application stack"
	@echo "  run-dev       - Run in development mode with live reload"
	@echo "  run-browser   - Run with browser testing enabled"
	@echo ""
	@echo "$(GREEN)Management Commands:$(NC)"
	@echo "  stop          - Stop all containers"
	@echo "  restart       - Restart the application"
	@echo "  clean         - Remove containers and images"
	@echo "  logs          - Show container logs"
	@echo ""
	@echo "$(GREEN)Testing Commands:$(NC)"
	@echo "  test          - Run comprehensive tests"
	@echo "  browser-test  - Test browser functionality"
	@echo "  health-check  - Check container health"
	@echo ""
	@echo "$(GREEN)Utility Commands:$(NC)"
	@echo "  shell         - Open shell in running container"
	@echo "  setup         - Initial setup and dependency check"

# Build Commands
build:
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)Build completed!$(NC)"

dev-build:
	@echo "$(BLUE)Building development Docker image...$(NC)"
	docker build \
		--build-arg BUILDKIT_INLINE_CACHE=1 \
		--target development \
		-t $(DOCKER_IMAGE):dev .
	@echo "$(GREEN)Development build completed!$(NC)"

rebuild:
	@echo "$(BLUE)Clean building Docker image (no cache)...$(NC)"
	docker build --no-cache -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)Clean build completed!$(NC)"

# Run Commands
run:
	@echo "$(BLUE)Starting application stack...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Application started!$(NC)"
	@echo "$(YELLOW)MCP Server: http://localhost:3001$(NC)"
	@echo "$(YELLOW)Ollama: http://localhost:11435$(NC)"

run-dev:
	@echo "$(BLUE)Starting development stack...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "$(GREEN)Development environment started!$(NC)"

run-browser:
	@echo "$(BLUE)Starting stack with browser testing...$(NC)"
	docker-compose up -d
	@echo "$(YELLOW)Running browser tests...$(NC)"
	docker exec $(CONTAINER_NAME) /app/entrypoint.sh test-browser

# Management Commands
stop:
	@echo "$(BLUE)Stopping containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)Containers stopped!$(NC)"

restart: stop run

clean:
	@echo "$(BLUE)Cleaning up containers and images...$(NC)"
	docker-compose down --volumes --remove-orphans
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	docker rmi $(DOCKER_IMAGE):dev 2>/dev/null || true
	docker system prune -f
	@echo "$(GREEN)Cleanup completed!$(NC)"

logs:
	@echo "$(BLUE)Showing container logs...$(NC)"
	docker-compose logs -f

# Testing Commands
test:
	@echo "$(BLUE)Running comprehensive tests...$(NC)"
	docker-compose exec mcp-server python -m pytest tests/ -v
	@echo "$(GREEN)Tests completed!$(NC)"

browser-test:
	@echo "$(BLUE)Testing browser functionality...$(NC)"
	docker-compose exec mcp-server python /app/scripts/test_browser_docker.py
	@echo "$(GREEN)Browser tests completed!$(NC)"

health-check:
	@echo "$(BLUE)Checking container health...$(NC)"
	docker-compose exec mcp-server /app/entrypoint.sh healthcheck

# Utility Commands
shell:
	@echo "$(BLUE)Opening shell in container...$(NC)"
	docker-compose exec mcp-server /bin/bash

setup:
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@echo "$(YELLOW)Checking Docker installation...$(NC)"
	@docker --version || (echo "$(RED)Docker not installed!$(NC)" && exit 1)
	@docker-compose --version || (echo "$(RED)Docker Compose not installed!$(NC)" && exit 1)
	@echo "$(GREEN)Docker environment ready!$(NC)"
	@echo ""
	@echo "$(YELLOW)Creating required directories...$(NC)"
	mkdir -p .claude_memory research/q1-sources output writing/chapters
	@echo "$(GREEN)Setup completed!$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Run 'make build' to build the Docker image"
	@echo "  2. Run 'make run' to start the application"
	@echo "  3. Run 'make browser-test' to verify browser functionality"

# Docker Compose Shortcuts
up: run
down: stop
build-up: build run

# Advanced Commands
debug:
	@echo "$(BLUE)Starting debug session...$(NC)"
	docker-compose exec mcp-server python -c "import sys; print('Python:', sys.version); import selenium; print('Selenium:', selenium.__version__)"

monitor:
	@echo "$(BLUE)Monitoring container resources...$(NC)"
	docker stats $(CONTAINER_NAME)

backup:
	@echo "$(BLUE)Creating backup of research data...$(NC)"
	docker run --rm -v $(PWD):/backup -v masterarbeit-browser-data:/data alpine tar czf /backup/browser_data_backup.tar.gz -C /data .
	docker run --rm -v $(PWD):/backup -v masterarbeit-cookies:/data alpine tar czf /backup/cookies_backup.tar.gz -C /data .
	@echo "$(GREEN)Backup created!$(NC)"

restore:
	@echo "$(BLUE)Restoring data from backup...$(NC)"
	@if [ -f browser_data_backup.tar.gz ]; then \
		docker run --rm -v $(PWD):/backup -v masterarbeit-browser-data:/data alpine tar xzf /backup/browser_data_backup.tar.gz -C /data; \
		echo "$(GREEN)Browser data restored!$(NC)"; \
	fi
	@if [ -f cookies_backup.tar.gz ]; then \
		docker run --rm -v $(PWD):/backup -v masterarbeit-cookies:/data alpine tar xzf /backup/cookies_backup.tar.gz -C /data; \
		echo "$(GREEN)Cookies restored!$(NC)"; \
	fi