#!/usr/bin/env python3
"""
Response caching system for Ollama to improve performance.
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OllamaResponseCache:
    """Cache system for Ollama responses."""
    
    def __init__(self, cache_dir: str = "~/.cache/ollama_responses"):
        """Initialize cache with directory."""
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.max_memory_items = 100
        self.ttl = 3600  # 1 hour TTL
        
    def _generate_key(self, prompt: str, model: str, options: Dict[str, Any]) -> str:
        """Generate cache key from prompt and parameters."""
        cache_data = {
            "prompt": prompt,
            "model": model,
            "options": options
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, options: Dict[str, Any]) -> Optional[str]:
        """Get cached response if available."""
        key = self._generate_key(prompt, model, options)
        
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                logger.debug(f"Cache hit (memory): {key[:8]}...")
                return entry["response"]
            else:
                del self.memory_cache[key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    entry = json.load(f)
                if time.time() - entry["timestamp"] < self.ttl:
                    logger.debug(f"Cache hit (disk): {key[:8]}...")
                    # Add to memory cache
                    self._add_to_memory(key, entry)
                    return entry["response"]
                else:
                    cache_file.unlink()
            except Exception as e:
                logger.error(f"Error reading cache: {e}")
        
        logger.debug(f"Cache miss: {key[:8]}...")
        return None
    
    def set(self, prompt: str, model: str, options: Dict[str, Any], response: str):
        """Cache a response."""
        key = self._generate_key(prompt, model, options)
        
        entry = {
            "prompt": prompt,
            "model": model,
            "options": options,
            "response": response,
            "timestamp": time.time()
        }
        
        # Add to memory cache
        self._add_to_memory(key, entry)
        
        # Save to disk
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(entry, f)
            logger.debug(f"Cached response: {key[:8]}...")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _add_to_memory(self, key: str, entry: Dict[str, Any]):
        """Add entry to memory cache with LRU eviction."""
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove oldest entry
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k]["timestamp"])
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = entry
    
    def clear(self):
        """Clear all cache."""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        logger.info("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        disk_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in disk_files)
        
        return {
            "memory_items": len(self.memory_cache),
            "disk_items": len(disk_files),
            "disk_size_mb": total_size / 1024 / 1024,
            "cache_dir": str(self.cache_dir)
        }