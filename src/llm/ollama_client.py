#!/usr/bin/env python3
"""
Ollama LLM Client for RAG System
================================

Provides integration with Ollama for local LLM inference using phi3:mini.
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional, Generator, Union
from pathlib import Path
import yaml
import logging
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize Ollama client with configuration."""
        self.config = self._load_config(config_path)
        self.base_url = self.config['ollama']['base_url']
        self.model = self.config['ollama']['model']
        self.default_options = self.config['ollama']['options']
        self.timeout = self.config['ollama']['timeout']
        self.retry_attempts = self.config['ollama']['retry_attempts']
        
        # Performance settings
        self.cache_enabled = self.config['performance']['cache_responses']
        self.max_concurrent = self.config['performance']['max_concurrent_requests']
        
        # Thread pool for concurrent requests
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent)
        
        # Response cache
        if self.cache_enabled:
            self._cache = {}
            self._cache_lock = threading.Lock()
        
        # Verify connection on init
        self._verify_connection()
    
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'ollama': {
                'base_url': 'http://localhost:11434',
                'model': 'phi3:mini',
                'options': {
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40,
                    'num_predict': 512,
                    'num_ctx': 4096
                },
                'timeout': 30,
                'retry_attempts': 3
            },
            'performance': {
                'cache_responses': True,
                'max_concurrent_requests': 2
            }
        }
    
    def _verify_connection(self):
        """Verify Ollama service is accessible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json()
                available_models = [m['name'] for m in models['models']]
                if self.model not in available_models:
                    raise ValueError(f"Model {self.model} not found. Available: {available_models}")
                logger.info(f"Connected to Ollama. Using model: {self.model}")
            else:
                raise ConnectionError(f"Ollama service returned status: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise
    
    def generate(self, 
                 prompt: str, 
                 context: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None,
                 stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """Generate response from the LLM."""
        # Build full prompt with context if provided
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"
        else:
            full_prompt = prompt
        
        # Check cache if enabled
        if self.cache_enabled and not stream:
            cache_key = self._get_cache_key(full_prompt, options)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.debug("Returning cached response")
                return cached_response
        
        # Merge options
        request_options = self.default_options.copy()
        if options:
            request_options.update(options)
        
        # Prepare request
        request_data = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": stream,
            "options": request_options
        }
        
        # Make request with retries
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=request_data,
                    timeout=self.timeout,
                    stream=stream
                )
                
                if response.status_code == 200:
                    if stream:
                        return self._handle_stream_response(response)
                    else:
                        result = response.json()
                        generated_text = result['response']
                        
                        # Cache response if enabled
                        if self.cache_enabled:
                            self._cache_response(cache_key, generated_text)
                        
                        return generated_text
                else:
                    logger.error(f"Generation failed with status: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        
        raise RuntimeError("Failed to generate response after all retries")
    
    def _handle_stream_response(self, response) -> Generator[str, None, None]:
        """Handle streaming response from Ollama."""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse streaming response: {line}")
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Generate responses for multiple prompts concurrently."""
        futures = []
        
        for prompt in prompts:
            future = self.executor.submit(self.generate, prompt, **kwargs)
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result(timeout=self.timeout * 2)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch generation failed for prompt: {e}")
                results.append("")
        
        return results
    
    def _get_cache_key(self, prompt: str, options: Optional[Dict]) -> str:
        """Generate cache key for prompt and options."""
        import hashlib
        key_data = f"{prompt}_{json.dumps(options or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Retrieve cached response if available."""
        with self._cache_lock:
            if cache_key in self._cache:
                # Simple LRU: move to end
                response = self._cache.pop(cache_key)
                self._cache[cache_key] = response
                return response
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache response with simple LRU eviction."""
        max_cache_size = 100
        
        with self._cache_lock:
            # Remove oldest if cache is full
            if len(self._cache) >= max_cache_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            
            self._cache[cache_key] = response
    
    def clear_cache(self):
        """Clear response cache."""
        if self.cache_enabled:
            with self._cache_lock:
                self._cache.clear()
            logger.info("Response cache cleared")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": self.model}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get model info: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


class OllamaRAGClient(OllamaClient):
    """Extended Ollama client optimized for RAG applications."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize RAG-optimized client."""
        super().__init__(config_path)
        self.rag_settings = self.config.get('rag_settings', {})
    
    def generate_with_context(self,
                            query: str,
                            retrieved_chunks: List[Dict[str, Any]],
                            max_context_length: int = 2048) -> str:
        """Generate response using retrieved context chunks."""
        # Build context from retrieved chunks
        context_parts = []
        current_length = 0
        
        for chunk in retrieved_chunks:
            chunk_text = chunk.get('text', '')
            chunk_length = len(chunk_text.split())
            
            if current_length + chunk_length > max_context_length:
                break
                
            context_parts.append(f"[{chunk.get('source', 'Unknown')}]: {chunk_text}")
            current_length += chunk_length
        
        context = "\n\n".join(context_parts)
        
        # Create RAG-optimized prompt
        prompt = f"""You are a helpful AI assistant specializing in financial analysis and multi-agent systems.
        
Based on the following retrieved information, please answer the user's question accurately and concisely.
If the information doesn't contain the answer, say so clearly.

Retrieved Information:
{context}

User Question: {query}

Please provide a comprehensive answer based on the retrieved information:"""
        
        return self.generate(prompt, options={
            'temperature': 0.3,  # Lower temperature for factual responses
            'top_p': 0.9,
            'num_predict': 512
        })
    
    def summarize_chunks(self, chunks: List[str], max_summary_length: int = 200) -> str:
        """Summarize multiple text chunks."""
        combined_text = "\n\n".join(chunks[:5])  # Limit to prevent context overflow
        
        prompt = f"""Please provide a concise summary of the following text chunks in no more than {max_summary_length} words:

{combined_text}

Summary:"""
        
        return self.generate(prompt, options={
            'temperature': 0.5,
            'num_predict': max_summary_length * 2  # Approximate tokens
        })
    
    def answer_with_citations(self,
                            query: str,
                            retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer with source citations."""
        # Generate answer
        answer = self.generate_with_context(query, retrieved_chunks)
        
        # Extract which sources were likely used
        used_sources = []
        for i, chunk in enumerate(retrieved_chunks):
            # Simple heuristic: check if answer mentions key terms from chunk
            chunk_keywords = set(chunk['text'].lower().split()[:20])
            answer_keywords = set(answer.lower().split())
            
            overlap = len(chunk_keywords & answer_keywords)
            if overlap > 3:  # Threshold for considering source as used
                used_sources.append({
                    'index': i,
                    'source': chunk.get('source', 'Unknown'),
                    'relevance': chunk.get('score', 0.0)
                })
        
        return {
            'answer': answer,
            'sources': used_sources,
            'chunks_used': len(used_sources),
            'total_chunks': len(retrieved_chunks)
        }


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = OllamaRAGClient()
    
    # Test basic generation
    response = client.generate("What is a RAG system?")
    print(f"Response: {response}")
    
    # Test with context
    test_chunks = [
        {
            'text': 'RAG (Retrieval-Augmented Generation) combines retrieval mechanisms with generative models.',
            'source': 'AI Textbook',
            'score': 0.95
        },
        {
            'text': 'Financial applications of RAG include document analysis and automated reporting.',
            'source': 'FinTech Journal',
            'score': 0.87
        }
    ]
    
    rag_response = client.generate_with_context(
        "How does RAG work in finance?",
        test_chunks
    )
    print(f"\nRAG Response: {rag_response}")