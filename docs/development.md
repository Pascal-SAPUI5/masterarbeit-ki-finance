# Development Guide

## Development Environment Setup

### Prerequisites

1. **Python 3.10+** with pip and venv
2. **Docker and Docker Compose** for containerized development
3. **Git** for version control
4. **VS Code or PyCharm** (recommended IDEs)
5. **Linux/WSL2** environment (Ubuntu 22.04+ recommended)

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd masterarbeit-ki-finance

# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Initialize the system
python scripts/setup_dev_environment.py
```

## Project Structure

```
masterarbeit-ki-finance/
├── scripts/                    # Core application modules
│   ├── rag_system.py          # RAG implementation
│   ├── search_literature.py   # Literature search
│   ├── manage_references.py   # Reference management
│   ├── research_assistant.py  # Research assistance
│   └── utils.py               # Utility functions
├── config/                    # Configuration files
│   ├── research-criteria.yaml
│   ├── rag_config.yaml
│   ├── writing-style.yaml
│   └── ollama_config.yaml
├── src/                       # Source code modules
│   ├── rag/                   # RAG system components
│   ├── llm/                   # LLM integration
│   └── utils/                 # Utility modules
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── performance/           # Performance tests
├── docs/                      # Documentation
├── memory/                    # Session persistence
├── literatur/                 # Document storage
├── output/                    # Generated outputs
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── docker-compose.yml         # Production compose
├── docker-compose.dev.yml     # Development compose
├── Dockerfile                 # Container definition
├── .env.example               # Environment template
├── pyproject.toml             # Project metadata
└── README.md                  # Project overview
```

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature-name

# Make changes and test
python -m pytest tests/ -v

# Run code quality checks
pre-commit run --all-files

# Commit changes
git add .
git commit -m "feat: add new feature description"

# Push and create pull request
git push origin feature/new-feature-name
```

### 2. Code Quality Standards

#### Python Code Style
- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting
- **mypy** for type checking
- **docstring** requirements for all functions

#### Example Code Structure
```python
"""Module docstring describing the module purpose."""

from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ExampleClass:
    """Class docstring describing the class purpose.
    
    Attributes:
        attribute_name: Description of the attribute.
    """
    
    def __init__(self, config_path: Path) -> None:
        """Initialize the class with configuration.
        
        Args:
            config_path: Path to configuration file.
            
        Raises:
            ValueError: If configuration is invalid.
        """
        self.config_path = config_path
        self._config = self._load_config()
    
    def process_documents(
        self, 
        documents: List[str], 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a list of documents.
        
        Args:
            documents: List of document paths to process.
            options: Optional processing parameters.
            
        Returns:
            Dictionary containing processing results.
            
        Raises:
            ProcessingError: If document processing fails.
        """
        if options is None:
            options = {}
            
        logger.info(f"Processing {len(documents)} documents")
        
        results = {}
        for doc in documents:
            try:
                result = self._process_single_document(doc, options)
                results[doc] = result
            except Exception as e:
                logger.error(f"Failed to process {doc}: {e}")
                raise ProcessingError(f"Document processing failed: {e}")
        
        return results
    
    def _process_single_document(
        self, 
        document: str, 
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single document (private method)."""
        # Implementation details
        pass
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file (private method)."""
        # Implementation details
        pass
```

### 3. Testing Strategy

#### Unit Tests
```python
# tests/unit/test_rag_system.py
import pytest
from unittest.mock import Mock, patch
from scripts.rag_system import RAGSystem


class TestRAGSystem:
    """Test cases for RAG system functionality."""
    
    @pytest.fixture
    def rag_system(self):
        """Fixture providing a RAG system instance."""
        with patch('scripts.rag_system.SentenceTransformer'):
            return RAGSystem("config/test_rag_config.yaml", cpu_only=True)
    
    def test_initialization(self, rag_system):
        """Test RAG system initialization."""
        assert rag_system is not None
        assert rag_system.cpu_only is True
    
    def test_document_indexing(self, rag_system):
        """Test document indexing functionality."""
        # Mock document processing
        with patch.object(rag_system, '_process_documents') as mock_process:
            mock_process.return_value = ['doc1', 'doc2']
            
            result = rag_system.index_documents('./test_docs/')
            
            assert result['indexed_count'] == 2
            mock_process.assert_called_once()
    
    @pytest.mark.parametrize("query,expected_results", [
        ("AI agents", 5),
        ("machine learning", 3),
        ("blockchain", 0),
    ])
    def test_search_functionality(self, rag_system, query, expected_results):
        """Test search functionality with different queries."""
        with patch.object(rag_system.searcher, 'search') as mock_search:
            mock_search.return_value = [{'doc': f'result_{i}'} for i in range(expected_results)]
            
            results = rag_system.search(query)
            
            assert len(results) == expected_results
            mock_search.assert_called_once_with(query, top_k=5)
```

#### Integration Tests
```python
# tests/integration/test_mcp_integration.py
import pytest
import requests
from docker import DockerClient


class TestMCPIntegration:
    """Integration tests for MCP server functionality."""
    
    @pytest.fixture(scope="module")
    def docker_services(self):
        """Start Docker services for testing."""
        client = DockerClient.from_env()
        # Start test services
        # ... docker service management
        yield
        # Cleanup
    
    def test_health_endpoint(self, docker_services):
        """Test MCP server health endpoint."""
        response = requests.get("http://localhost:3001/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_document_search_endpoint(self, docker_services):
        """Test document search via API."""
        payload = {
            "query": "AI agents in finance",
            "top_k": 5
        }
        response = requests.post("http://localhost:3001/api/search", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) <= 5
```

#### Performance Tests
```python
# tests/performance/test_performance.py
import time
import pytest
from scripts.rag_system import RAGSystem


class TestPerformance:
    """Performance tests for system components."""
    
    def test_search_performance(self):
        """Test search response time."""
        rag = RAGSystem("config/rag_config.yaml", cpu_only=True)
        
        start_time = time.time()
        results = rag.search("AI agents finance", top_k=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0, f"Search took too long: {response_time}s"
        assert len(results) <= 10
    
    def test_memory_usage(self):
        """Test memory consumption during processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        rag = RAGSystem("config/rag_config.yaml", cpu_only=True)
        rag.index_documents("./test_documents/")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 2048, f"Memory usage too high: {memory_increase}MB"
```

### 4. Development Tools Configuration

#### VS Code Settings (`.vscode/settings.json`)
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.associations": {
        "*.yaml": "yaml",
        "*.yml": "yaml"
    },
    "yaml.schemas": {
        "./schemas/config-schema.json": [
            "config/*.yaml",
            "config/*.yml"
        ]
    }
}
```

#### Pre-commit Configuration (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
```

#### PyProject Configuration (`pyproject.toml`)
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "masterarbeit-ki-finance"
version = "1.0.0"
description = "AI-powered research automation for finance master thesis"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "torch>=2.0.0",
    "sentence-transformers>=2.2.0",
    "faiss-cpu>=1.7.0",
    "ollama>=0.1.0",
    "langchain>=0.1.0",
    "PyMuPDF>=1.23.0",
    "pytesseract>=0.3.10",
    "rich>=13.0.0",
    "pyyaml>=6.0",
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]

[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["scripts", "src"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--cov=scripts",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-fail-under=80"
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["scripts", "src"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "setup.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

## Development Services

### Docker Compose for Development (`docker-compose.dev.yml`)

```yaml
version: '3.8'

services:
  # Development MCP server with hot reloading
  mcp-server-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: masterarbeit-mcp-dev
    ports:
      - "3001:3000"
      - "5678:5678"  # Debugger port
    volumes:
      # Hot reloading
      - .:/app
      - ./venv:/app/venv
    environment:
      - PYTHONUNBUFFERED=1
      - DEBUG_MODE=true
      - LOG_LEVEL=DEBUG
      - DEVELOPMENT=true
    command: python -m debugpy --listen 0.0.0.0:5678 --wait-for-client mcp_server.py
    depends_on:
      - ollama-dev
      - redis-dev

  # Development Ollama with debug settings
  ollama-dev:
    image: ollama/ollama:latest
    container_name: masterarbeit-ollama-dev
    ports:
      - "11434:11434"
    volumes:
      - ollama-dev-data:/root/.ollama
    environment:
      - OLLAMA_DEBUG=1
      - OLLAMA_VERBOSE=1
      - OLLAMA_HOST=0.0.0.0

  # Redis for development caching
  redis-dev:
    image: redis:7-alpine
    container_name: masterarbeit-redis-dev
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --appendfsync everysec

  # Development database
  postgres-dev:
    image: postgres:15-alpine
    container_name: masterarbeit-postgres-dev
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=masterarbeit_dev
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=dev123
    volumes:
      - postgres-dev-data:/var/lib/postgresql/data

volumes:
  ollama-dev-data:
  postgres-dev-data:
```

### Development Dockerfile (`Dockerfile.dev`)

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    poppler-utils \
    libpoppler-cpp-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Install debugpy for remote debugging
RUN pip install debugpy

# Copy source code
COPY . .

# Set development environment
ENV PYTHONPATH=/app
ENV DEVELOPMENT=true
ENV DEBUG_MODE=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Default command (can be overridden)
CMD ["python", "mcp_server.py"]
```

## Debugging

### Local Debugging

#### VS Code Debug Configuration (`.vscode/launch.json`)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug MCP Server",
            "type": "python",
            "request": "launch",
            "program": "mcp_server.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "DEBUG_MODE": "true",
                "LOG_LEVEL": "DEBUG"
            }
        },
        {
            "name": "Debug RAG System",
            "type": "python",
            "request": "launch",
            "program": "scripts/rag_system.py",
            "args": ["search", "AI agents finance"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Attach to Docker",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ]
        }
    ]
}
```

### Remote Debugging in Docker

```bash
# Start development container with debugger
docker-compose -f docker-compose.dev.yml up -d

# Attach VS Code debugger to port 5678
# Set breakpoints and debug remotely
```

### Logging Configuration

```python
# scripts/logging_config.py
import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """Configure logging for development and production."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers in development
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("docker").setLevel(logging.WARNING)
```

## Contributing Guidelines

### Code Contribution Process

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Ensure code quality** with pre-commit hooks
4. **Update documentation** for API changes
5. **Submit pull request** with clear description
6. **Address review feedback** promptly

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No console.log or debug statements
```

### Code Review Guidelines

#### For Authors
- Provide clear PR description and context
- Include tests for new functionality
- Update documentation for API changes
- Respond to feedback constructively

#### For Reviewers
- Focus on code correctness and maintainability
- Check test coverage and quality
- Verify documentation accuracy
- Provide constructive feedback

## Performance Optimization

### Profiling Tools

```python
# Profile code performance
import cProfile
import pstats

def profile_function(func):
    """Decorator to profile function performance."""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 functions
        
        return result
    return wrapper

# Usage
@profile_function
def expensive_operation():
    # Your code here
    pass
```

### Memory Profiling

```python
# Monitor memory usage
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Your code here
    pass

# Run with: python -m memory_profiler script.py
```

### Performance Testing

```bash
# Run performance tests
python -m pytest tests/performance/ -v

# Benchmark specific functions
python scripts/benchmark.py --function rag_search --iterations 100

# Monitor system resources
python scripts/monitor_resources.py --duration 300
```

This development guide provides comprehensive instructions for setting up, developing, testing, and contributing to the project while maintaining high code quality standards.