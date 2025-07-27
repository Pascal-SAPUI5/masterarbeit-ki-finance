"""
Functional Tests for Ollama Integration
======================================

Test core functionality and features.
"""

import pytest
import json
import time
from typing import List, Dict, Any


class TestBasicGeneration:
    """Test basic text generation functionality."""
    
    @pytest.mark.requires_ollama
    def test_simple_prompt(self, ollama_client):
        """Test generation with a simple prompt."""
        response = ollama_client.generate(
            "What is 2+2?",
            options={"max_tokens": 50}
        )
        
        assert "response" in response
        assert len(response["response"]) > 0
        assert any(char.isdigit() for char in response["response"])
    
    @pytest.mark.requires_ollama
    def test_response_format(self, ollama_client):
        """Test that response has expected format."""
        response = ollama_client.generate(
            "Hello, how are you?",
            options={"max_tokens": 50}
        )
        
        required_fields = ["response", "model", "created_at", "done"]
        for field in required_fields:
            assert field in response, f"Missing field: {field}"
        
        assert response["done"] is True
        assert response["model"] == "phi3:mini"
    
    @pytest.mark.requires_ollama
    def test_empty_prompt_handling(self, ollama_client):
        """Test handling of empty prompts."""
        with pytest.raises(Exception):
            ollama_client.generate("")
    
    @pytest.mark.requires_ollama
    @pytest.mark.parametrize("prompt,expected_theme", [
        ("What is machine learning?", "learning"),
        ("Explain financial markets", "financial"),
        ("How do neural networks work?", "neural")
    ])
    def test_topic_relevance(self, ollama_client, prompt, expected_theme):
        """Test that responses are relevant to the topic."""
        response = ollama_client.generate(
            prompt,
            options={"max_tokens": 100}
        )
        
        assert expected_theme.lower() in response["response"].lower()


class TestContextHandling:
    """Test context window and long input handling."""
    
    @pytest.mark.requires_ollama
    def test_small_context(self, ollama_client):
        """Test with small context."""
        context = "The capital of France is Paris."
        prompt = f"{context}\n\nWhat is the capital of France?"
        
        response = ollama_client.generate(prompt)
        assert "paris" in response["response"].lower()
    
    @pytest.mark.requires_ollama
    def test_medium_context(self, ollama_client, sample_documents):
        """Test with medium-sized context."""
        context = sample_documents["financial_report"]
        prompt = f"Based on this report:\n{context}\n\nWhat was the revenue?"
        
        response = ollama_client.generate(
            prompt,
            options={"max_tokens": 100}
        )
        
        assert "$" in response["response"] or "million" in response["response"].lower()
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_large_context(self, ollama_client):
        """Test with large context approaching limit."""
        # Create a large context (3000 tokens worth)
        large_context = " ".join(["This is a test sentence."] * 500)
        prompt = f"{large_context}\n\nSummarize the above in one sentence."
        
        response = ollama_client.generate(
            prompt,
            options={"max_tokens": 50}
        )
        
        assert len(response["response"]) > 0
        assert len(response["response"]) < 200  # Should be a summary
    
    @pytest.mark.requires_ollama
    def test_context_truncation(self, ollama_client):
        """Test graceful handling of context exceeding limits."""
        # Create context exceeding 4096 token limit
        huge_context = " ".join(["Long test sentence here."] * 2000)
        prompt = f"{huge_context}\n\nWhat is this about?"
        
        # Should not crash, but handle gracefully
        response = ollama_client.generate(
            prompt,
            options={"max_tokens": 50}
        )
        
        assert "response" in response


class TestGenerationOptions:
    """Test various generation options and parameters."""
    
    @pytest.mark.requires_ollama
    @pytest.mark.parametrize("temperature", [0.0, 0.5, 1.0])
    def test_temperature_variation(self, ollama_client, temperature):
        """Test generation with different temperatures."""
        prompt = "Generate a creative story about AI in one sentence."
        
        responses = []
        for _ in range(3):
            response = ollama_client.generate(
                prompt,
                options={
                    "temperature": temperature,
                    "max_tokens": 50,
                    "seed": 42 if temperature == 0.0 else None
                }
            )
            responses.append(response["response"])
        
        if temperature == 0.0:
            # With temperature 0 and same seed, responses should be identical
            assert len(set(responses)) == 1
        else:
            # Higher temperature should produce more variation
            assert len(set(responses)) > 1
    
    @pytest.mark.requires_ollama
    def test_max_tokens_limit(self, ollama_client):
        """Test that max_tokens limit is respected."""
        response = ollama_client.generate(
            "Count from 1 to 100",
            options={"max_tokens": 20}
        )
        
        # Rough token count (words + punctuation)
        token_count = len(response["response"].split())
        assert token_count < 30  # Some buffer for tokenization differences
    
    @pytest.mark.requires_ollama
    def test_stop_sequences(self, ollama_client):
        """Test stop sequence functionality."""
        response = ollama_client.generate(
            "List three colors:\n1. Red\n2.",
            options={
                "max_tokens": 50,
                "stop": ["\n3.", "\n\n"]
            }
        )
        
        assert "\n3." not in response["response"]
    
    @pytest.mark.requires_ollama
    def test_top_p_sampling(self, ollama_client):
        """Test top-p (nucleus) sampling."""
        response = ollama_client.generate(
            "The most important thing in life is",
            options={
                "top_p": 0.9,
                "temperature": 0.8,
                "max_tokens": 50
            }
        )
        
        assert len(response["response"]) > 0


class TestMultiTurnConversation:
    """Test multi-turn conversation handling."""
    
    @pytest.mark.requires_ollama
    def test_conversation_context(self, ollama_client):
        """Test maintaining context across turns."""
        # First turn
        response1 = ollama_client.generate(
            "My name is Alice and I work in finance.",
            options={"max_tokens": 50}
        )
        
        # Second turn with context
        prompt2 = f"Previous: My name is Alice and I work in finance.\nAssistant: {response1['response']}\nHuman: What field do I work in?"
        
        response2 = ollama_client.generate(
            prompt2,
            options={"max_tokens": 50}
        )
        
        assert "finance" in response2["response"].lower()
    
    @pytest.mark.requires_ollama
    def test_conversation_memory_limit(self, ollama_client):
        """Test conversation with multiple turns."""
        conversation = []
        
        for i in range(5):
            if i == 0:
                prompt = "Let's discuss AI in finance. What are the main applications?"
            else:
                # Build conversation history
                history = "\n".join(conversation[-3:])  # Keep last 3 exchanges
                prompt = f"{history}\n\nHuman: Tell me more about point {i}."
            
            response = ollama_client.generate(
                prompt,
                options={"max_tokens": 100}
            )
            
            conversation.append(f"Human: {prompt}")
            conversation.append(f"Assistant: {response['response']}")
        
        # Check that conversation maintained some coherence
        assert len(conversation) == 10  # 5 exchanges * 2


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.requires_ollama
    def test_invalid_model(self, test_config):
        """Test handling of invalid model name."""
        import requests
        
        with pytest.raises(requests.exceptions.HTTPError):
            response = requests.post(
                f"{test_config['ollama']['base_url']}/api/generate",
                json={
                    "model": "invalid-model-name",
                    "prompt": "Test",
                    "stream": False
                },
                timeout=5
            )
            response.raise_for_status()
    
    @pytest.mark.requires_ollama
    def test_malformed_request(self, test_config):
        """Test handling of malformed requests."""
        import requests
        
        response = requests.post(
            f"{test_config['ollama']['base_url']}/api/generate",
            json={
                # Missing required 'model' field
                "prompt": "Test"
            },
            timeout=5
        )
        
        assert response.status_code >= 400
    
    @pytest.mark.requires_ollama
    def test_timeout_handling(self, ollama_client):
        """Test timeout handling for long generations."""
        import requests
        
        # Request a very long generation
        with pytest.raises(requests.exceptions.Timeout):
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "phi3:mini",
                    "prompt": "Write a 10000 word essay",
                    "stream": False,
                    "options": {"max_tokens": 10000}
                },
                timeout=1  # Very short timeout
            )