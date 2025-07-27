"""
Infrastructure Tests
===================

Test infrastructure components and dependencies.
"""

import pytest
import requests
import subprocess
import time
from pathlib import Path


class TestDockerInfrastructure:
    """Test Docker infrastructure."""
    
    @pytest.mark.requires_docker
    def test_docker_installed(self):
        """Test that Docker is installed and accessible."""
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Docker version" in result.stdout
    
    @pytest.mark.requires_docker
    def test_ollama_container_exists(self):
        """Test that Ollama container exists."""
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=ollama", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        assert "ollama" in result.stdout, "Ollama container not found"
    
    @pytest.mark.requires_docker
    def test_ollama_container_running(self):
        """Test that Ollama container is running."""
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", "ollama"],
            capture_output=True,
            text=True
        )
        assert result.stdout.strip() == "running", f"Container status: {result.stdout.strip()}"
    
    @pytest.mark.requires_docker
    def test_container_port_mapping(self):
        """Test that container port is properly mapped."""
        result = subprocess.run(
            ["docker", "port", "ollama", "11434"],
            capture_output=True,
            text=True
        )
        assert "11434" in result.stdout, "Port 11434 not mapped"


class TestNetworkConnectivity:
    """Test network connectivity to Ollama service."""
    
    @pytest.mark.requires_ollama
    def test_ollama_api_accessible(self):
        """Test that Ollama API is accessible."""
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        assert response.status_code == 200
    
    @pytest.mark.requires_ollama
    def test_api_response_time(self):
        """Test API response time is acceptable."""
        start_time = time.time()
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 0.1, f"API response took {duration:.3f}s (>100ms)"
    
    @pytest.mark.requires_ollama
    def test_api_endpoints(self):
        """Test that all required API endpoints are available."""
        endpoints = [
            "/api/tags",
            "/api/generate",
            "/api/pull",
            "/api/embeddings"
        ]
        
        base_url = "http://localhost:11434"
        
        for endpoint in endpoints:
            response = requests.options(f"{base_url}{endpoint}")
            assert response.status_code in [200, 204, 405], \
                f"Endpoint {endpoint} not accessible"


class TestModelAvailability:
    """Test model availability and configuration."""
    
    @pytest.mark.requires_ollama
    def test_phi3_mini_available(self, ollama_client):
        """Test that phi3:mini model is available."""
        models = ollama_client.list_models()
        model_names = [m["name"] for m in models["models"]]
        
        assert "phi3:mini" in model_names, "phi3:mini model not available"
    
    @pytest.mark.requires_ollama
    def test_model_details(self, ollama_client):
        """Test model details and parameters."""
        models = ollama_client.list_models()
        
        phi3_model = None
        for model in models["models"]:
            if model["name"] == "phi3:mini":
                phi3_model = model
                break
        
        assert phi3_model is not None
        assert "size" in phi3_model
        assert phi3_model["size"] > 0
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_model_loading_time(self, ollama_client, performance_monitor):
        """Test model loading time."""
        performance_monitor.start("model_loading")
        
        response = ollama_client.generate(
            "Hello",
            options={"num_predict": 1}
        )
        
        loading_time = performance_monitor.stop()
        
        assert response["response"] is not None
        assert loading_time < 5.0, f"Model loading took {loading_time:.2f}s (>5s)"


class TestSystemResources:
    """Test system resource availability."""
    
    def test_memory_available(self):
        """Test that sufficient memory is available."""
        import psutil
        
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024 ** 3)
        
        assert available_gb >= 2.0, f"Only {available_gb:.1f}GB RAM available (need 2GB+)"
    
    def test_disk_space_available(self):
        """Test that sufficient disk space is available."""
        import shutil
        
        usage = shutil.disk_usage("/")
        free_gb = usage.free / (1024 ** 3)
        
        assert free_gb >= 5.0, f"Only {free_gb:.1f}GB disk space available (need 5GB+)"
    
    def test_cpu_cores(self):
        """Test CPU core availability."""
        import multiprocessing
        
        cores = multiprocessing.cpu_count()
        assert cores >= 2, f"Only {cores} CPU cores available (recommend 2+)"


class TestConfiguration:
    """Test configuration files and settings."""
    
    def test_ollama_config_exists(self):
        """Test that Ollama configuration file exists."""
        config_path = Path("config/ollama_config.yaml")
        assert config_path.exists(), "Ollama configuration file not found"
    
    def test_rag_config_exists(self):
        """Test that RAG configuration file exists."""
        config_path = Path("config/rag_config.yaml")
        assert config_path.exists(), "RAG configuration file not found"
    
    def test_config_valid_yaml(self):
        """Test that configuration files are valid YAML."""
        import yaml
        
        configs = ["config/ollama_config.yaml", "config/rag_config.yaml"]
        
        for config_file in configs:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"Invalid YAML in {config_file}: {e}")
    
    def test_required_config_keys(self, test_config):
        """Test that required configuration keys are present."""
        required_keys = [
            "ollama.base_url",
            "ollama.model",
            "ollama.options",
            "rag_settings.chunk_size"
        ]
        
        def check_nested_key(config, key_path):
            keys = key_path.split('.')
            value = config
            for key in keys:
                if key not in value:
                    return False
                value = value[key]
            return True
        
        for key in required_keys:
            assert check_nested_key(test_config, key), f"Missing config key: {key}"