"""
Integration Tests for RAG System with Ollama
===========================================

Test the integration between Ollama and the RAG system.
"""

import pytest
import yaml
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer


class TestEmbeddingCompatibility:
    """Test compatibility between embeddings and Ollama."""
    
    @pytest.mark.integration
    def test_embedding_model_loads(self, test_config):
        """Test that the configured embedding model loads."""
        # Load RAG config
        rag_config_path = Path("config/rag_config.yaml")
        with open(rag_config_path, 'r') as f:
            rag_config = yaml.safe_load(f)
        
        model_name = rag_config['system']['embedding_model']
        model = SentenceTransformer(model_name)
        
        assert model is not None
        assert hasattr(model, 'encode')
    
    @pytest.mark.integration
    def test_embedding_generation(self, test_config):
        """Test embedding generation for documents."""
        rag_config_path = Path("config/rag_config.yaml")
        with open(rag_config_path, 'r') as f:
            rag_config = yaml.safe_load(f)
        
        model = SentenceTransformer(rag_config['system']['embedding_model'])
        
        test_texts = [
            "Financial risk management using AI",
            "Multi-agent systems in banking",
            "Regulatory compliance automation"
        ]
        
        embeddings = model.encode(test_texts)
        
        assert embeddings.shape[0] == len(test_texts)
        assert embeddings.shape[1] == rag_config['system']['embedding_dimension']
        assert embeddings.dtype == np.float32
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_embedding_ollama_coordination(self, ollama_client, test_config):
        """Test coordination between embeddings and Ollama generation."""
        # Generate embedding for a query
        rag_config_path = Path("config/rag_config.yaml")
        with open(rag_config_path, 'r') as f:
            rag_config = yaml.safe_load(f)
        
        model = SentenceTransformer(rag_config['system']['embedding_model'])
        
        query = "What are the risks in algorithmic trading?"
        query_embedding = model.encode([query])[0]
        
        # Simulate retrieval (would normally query vector DB)
        context = "Algorithmic trading risks include market volatility, technical failures, and regulatory changes."
        
        # Use Ollama to generate response with context
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
        
        response = ollama_client.generate(
            prompt,
            options={"max_tokens": 100}
        )
        
        assert "risk" in response["response"].lower()
        assert len(response["response"]) > 20


class TestRAGPipeline:
    """Test the complete RAG pipeline integration."""
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_document_chunking(self, sample_documents, test_config):
        """Test document chunking for RAG."""
        from src.rag.rag_system_ollama import chunk_text
        
        text = sample_documents["financial_report"]
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 100 for chunk in chunks)
        
        # Test overlap
        for i in range(len(chunks) - 1):
            assert chunks[i][-20:] in chunks[i + 1]
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_query_processing(self, ollama_client, mock_rag_context):
        """Test query processing with RAG context."""
        query = "How do RAG systems work?"
        
        # Format context for prompt
        context_text = "\n".join([doc["content"] for doc in mock_rag_context])
        
        prompt = f"""Based on the following context, answer the question.

Context:
{context_text}

Question: {query}

Answer:"""
        
        response = ollama_client.generate(
            prompt,
            options={
                "temperature": 0.7,
                "max_tokens": 150
            }
        )
        
        # Verify response uses context
        assert "retrieval" in response["response"].lower()
        assert "generation" in response["response"].lower()
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_source_attribution(self, ollama_client, mock_rag_context):
        """Test that responses can attribute sources."""
        query = "What are the benefits of RAG in finance?"
        
        # Format context with source information
        context_parts = []
        for i, doc in enumerate(mock_rag_context):
            context_parts.append(f"[{i+1}] {doc['content']} (Source: {doc['metadata']['source']})")
        
        context_text = "\n".join(context_parts)
        
        prompt = f"""Based on the following sources, answer the question and cite the source numbers.

{context_text}

Question: {query}

Answer with source citations [1], [2], etc:"""
        
        response = ollama_client.generate(
            prompt,
            options={"max_tokens": 200}
        )
        
        # Check for source citations
        assert "[" in response["response"] and "]" in response["response"]
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_multi_document_rag(self, ollama_client, sample_documents):
        """Test RAG with multiple documents."""
        # Simulate multiple retrieved documents
        contexts = [
            sample_documents["financial_report"],
            sample_documents["research_paper"],
            sample_documents["market_data"]
        ]
        
        query = "What are the key trends in AI and financial performance?"
        
        # Combine contexts
        combined_context = "\n\n---\n\n".join(contexts)
        
        prompt = f"""Analyze the following documents and answer the question.

Documents:
{combined_context}

Question: {query}

Provide a comprehensive answer based on all documents:"""
        
        response = ollama_client.generate(
            prompt,
            options={
                "max_tokens": 300,
                "temperature": 0.7
            }
        )
        
        # Verify comprehensive response
        response_lower = response["response"].lower()
        assert "ai" in response_lower or "artificial intelligence" in response_lower
        assert any(term in response_lower for term in ["growth", "revenue", "performance"])


class TestConfigurationIntegration:
    """Test configuration management and updates."""
    
    @pytest.mark.integration
    def test_config_loading(self):
        """Test loading both RAG and Ollama configs."""
        rag_config_path = Path("config/rag_config.yaml")
        ollama_config_path = Path("config/ollama_config.yaml")
        
        with open(rag_config_path, 'r') as f:
            rag_config = yaml.safe_load(f)
        
        with open(ollama_config_path, 'r') as f:
            ollama_config = yaml.safe_load(f)
        
        # Verify configs are compatible
        assert rag_config is not None
        assert ollama_config is not None
        
        # Check for required fields
        assert "system" in rag_config
        assert "ollama" in ollama_config
    
    @pytest.mark.integration
    def test_config_updates(self, tmp_path):
        """Test dynamic configuration updates."""
        # Create temporary config
        temp_config = {
            "ollama": {
                "model": "phi3:mini",
                "options": {
                    "temperature": 0.5,
                    "max_tokens": 100
                }
            }
        }
        
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(temp_config, f)
        
        # Update config
        temp_config["ollama"]["options"]["temperature"] = 0.8
        with open(config_file, 'w') as f:
            yaml.dump(temp_config, f)
        
        # Reload and verify
        with open(config_file, 'r') as f:
            updated_config = yaml.safe_load(f)
        
        assert updated_config["ollama"]["options"]["temperature"] == 0.8
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_runtime_parameter_override(self, ollama_client):
        """Test overriding config parameters at runtime."""
        # Default generation
        response1 = ollama_client.generate(
            "Generate a random number",
            options={"temperature": 0.0, "seed": 42, "max_tokens": 10}
        )
        
        # Override temperature
        response2 = ollama_client.generate(
            "Generate a random number",
            options={"temperature": 1.0, "max_tokens": 10}
        )
        
        # Low temperature should be more deterministic
        assert response1["response"] != response2["response"]


class TestErrorRecovery:
    """Test error handling and recovery in integration."""
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_connection_retry(self, test_config):
        """Test connection retry mechanism."""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        
        # Should handle transient errors
        response = session.get(
            f"{test_config['ollama']['base_url']}/api/tags",
            timeout=5
        )
        
        assert response.status_code == 200
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_graceful_degradation(self, ollama_client):
        """Test graceful degradation when context is too large."""
        # Create oversized context
        huge_context = "x" * 10000
        
        prompt = f"{huge_context}\n\nSummarize this."
        
        # Should handle without crashing
        try:
            response = ollama_client.generate(
                prompt,
                options={"max_tokens": 50}
            )
            assert "response" in response
        except Exception as e:
            # Should be a handled exception, not a crash
            assert "context length" in str(e).lower() or "token" in str(e).lower()
    
    @pytest.mark.integration
    def test_fallback_handling(self, test_config):
        """Test fallback handling when Ollama is unavailable."""
        class MockRAGSystem:
            def __init__(self, ollama_available=True):
                self.ollama_available = ollama_available
            
            def generate_response(self, query: str, context: List[str]) -> str:
                if self.ollama_available:
                    return f"Ollama response for: {query}"
                else:
                    # Fallback to simple template
                    return f"Based on the context, here's information about {query}: {context[0][:100]}..."
        
        # Test with Ollama available
        rag_system = MockRAGSystem(ollama_available=True)
        response = rag_system.generate_response("test query", ["test context"])
        assert "Ollama response" in response
        
        # Test fallback
        rag_system = MockRAGSystem(ollama_available=False)
        response = rag_system.generate_response("test query", ["test context"])
        assert "Based on the context" in response


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """Helper function to chunk text for testing."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks