#!/usr/bin/env python3
"""
Configuration for RAG system to use Docker Ollama
"""

import os

# Ollama configuration for Docker
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11435")

# Set environment variable for ollama library
os.environ["OLLAMA_HOST"] = OLLAMA_HOST

print(f"RAG System configured to use Ollama at: {OLLAMA_HOST}")