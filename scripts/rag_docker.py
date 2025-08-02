#!/usr/bin/env python3
"""
RAG System wrapper for Docker Ollama usage
"""

import os
import sys

# Configure Ollama to use Docker instance on port 11435
os.environ["OLLAMA_HOST"] = "http://localhost:11435"

# Import and run the original RAG system
from rag_system import main

if __name__ == "__main__":
    print("Starting RAG System with Docker Ollama (port 11435)...")
    main()