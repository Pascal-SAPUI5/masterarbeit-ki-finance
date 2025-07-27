"""
Test Configuration and Fixtures
==============================

Shared fixtures and configuration for all tests.
"""

import pytest
import yaml
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Generator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Load test configuration."""
    config_path = Path(__file__).parent.parent / "config" / "ollama_config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Default test configuration
        return {
            "ollama": {
                "base_url": "http://localhost:11434",
                "model": "phi3:mini",
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 512,
                    "num_ctx": 4096
                },
                "timeout": 30,
                "retry_attempts": 3
            },
            "rag_settings": {
                "chunk_size": 512,
                "chunk_overlap": 50,
                "retrieval_top_k": 5
            }
        }


@pytest.fixture(scope="session")
def ollama_client(test_config):
    """Create Ollama client instance."""
    base_url = test_config["ollama"]["base_url"]
    
    class OllamaClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            self.session = requests.Session()
        
        def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
            """Generate text using Ollama."""
            payload = {
                "model": test_config["ollama"]["model"],
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=test_config["ollama"]["timeout"]
            )
            response.raise_for_status()
            return response.json()
        
        def list_models(self) -> Dict[str, Any]:
            """List available models."""
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json()
        
        def pull_model(self, model_name: str) -> Generator[Dict[str, Any], None, None]:
            """Pull a model."""
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    yield json.loads(line)
    
    client = OllamaClient(base_url)
    yield client
    client.session.close()


@pytest.fixture(scope="function")
def performance_monitor():
    """Monitor test performance."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.metrics = {}
        
        def start(self, name: str):
            """Start timing a section."""
            self.start_time = time.time()
            self.current_name = name
        
        def stop(self) -> float:
            """Stop timing and return duration."""
            if self.start_time is None:
                raise ValueError("Timer not started")
            
            duration = time.time() - self.start_time
            self.metrics[self.current_name] = duration
            self.start_time = None
            return duration
        
        def get_metrics(self) -> Dict[str, float]:
            """Get all recorded metrics."""
            return self.metrics.copy()
    
    return PerformanceMonitor()


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data directory."""
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@pytest.fixture(scope="session")
def sample_documents(test_data_dir) -> Dict[str, str]:
    """Sample documents for testing."""
    documents = {
        "financial_report": """
        Annual Financial Report 2024
        
        Revenue: $10.5 million (15% YoY growth)
        Operating Expenses: $7.2 million
        Net Profit: $3.3 million
        
        Key Highlights:
        - Strong growth in AI services division
        - Successful cost optimization initiatives
        - Expanded market presence in EMEA region
        """,
        
        "research_paper": """
        Title: Multi-Agent Systems in Financial Risk Management
        
        Abstract:
        This paper explores the application of multi-agent systems (MAS) 
        in financial risk management. We demonstrate how autonomous agents 
        can collaborate to identify, assess, and mitigate various financial 
        risks in real-time.
        
        Keywords: Multi-agent systems, Risk management, Financial AI
        """,
        
        "market_data": """
        Market Analysis - Q4 2024
        
        Indices Performance:
        - S&P 500: +12.3%
        - NASDAQ: +18.7%
        - FTSE 100: +8.2%
        
        Sector Leaders:
        1. Technology: +22.5%
        2. Healthcare: +15.3%
        3. Financial Services: +11.8%
        """
    }
    
    # Save documents to files
    for name, content in documents.items():
        file_path = test_data_dir / f"{name}.txt"
        file_path.write_text(content)
    
    return documents


@pytest.fixture(scope="function")
def mock_rag_context():
    """Mock RAG context for testing."""
    return [
        {
            "content": "RAG systems combine retrieval and generation for enhanced responses.",
            "metadata": {"source": "research_paper.pdf", "page": 5}
        },
        {
            "content": "Financial applications benefit from contextual information retrieval.",
            "metadata": {"source": "finance_guide.pdf", "page": 12}
        }
    ]


@pytest.fixture(autouse=True)
def cleanup_test_files(test_data_dir):
    """Clean up test files after each test."""
    yield
    # Cleanup temporary test files
    for file in test_data_dir.glob("temp_*"):
        file.unlink()


@pytest.fixture(scope="session")
def docker_available():
    """Check if Docker is available."""
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


@pytest.fixture(scope="session")
def ollama_available(ollama_client):
    """Check if Ollama service is available."""
    try:
        ollama_client.list_models()
        return True
    except:
        return False


# Markers for conditional test execution
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "requires_ollama: mark test as requiring Ollama service"
    )
    config.addinivalue_line(
        "markers", "requires_docker: mark test as requiring Docker"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


# Skip tests if requirements not met
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on available services."""
    skip_ollama = pytest.mark.skip(reason="Ollama service not available")
    skip_docker = pytest.mark.skip(reason="Docker not available")
    
    for item in items:
        if "requires_ollama" in item.keywords and not config.cache.get("ollama_available", False):
            item.add_marker(skip_ollama)
        if "requires_docker" in item.keywords and not config.cache.get("docker_available", False):
            item.add_marker(skip_docker)