#!/usr/bin/env python3
"""
RAG System with Ollama Integration
==================================

Enhanced RAG system using local Ollama phi3:mini for inference.
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import faiss
from sentence_transformers import SentenceTransformer
import yaml
import logging
from datetime import datetime

# Import our Ollama client
from src.llm.ollama_client import OllamaRAGClient

logger = logging.getLogger(__name__)


class OllamaRAGSystem:
    """RAG system with Ollama LLM integration."""
    
    def __init__(self, config_path: Path = Path("config/rag_config.yaml")):
        """Initialize RAG system with configuration."""
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.embedding_model = self._init_embedding_model()
        self.llm_client = self._init_llm_client()
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Load existing index if available
        self._load_index()
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load RAG configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _init_embedding_model(self):
        """Initialize the embedding model."""
        model_name = self.config['system']['embedding_model']
        logger.info(f"Loading embedding model: {model_name}")
        return SentenceTransformer(model_name)
    
    def _init_llm_client(self):
        """Initialize Ollama LLM client."""
        ollama_config_path = Path("config/ollama_config.yaml")
        logger.info(f"Initializing Ollama client with model: {self.config['system']['llm_model']}")
        return OllamaRAGClient(ollama_config_path)
    
    def _load_index(self):
        """Load existing FAISS index and metadata."""
        index_path = Path(self.config['paths']['index_path'])
        index_file = index_path / "faiss_index"
        metadata_file = index_path / "metadata.json"
        
        if index_file.exists() and metadata_file.exists():
            logger.info("Loading existing index...")
            self.index = faiss.read_index(str(index_file))
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            logger.info(f"Loaded index with {self.index.ntotal} vectors")
        else:
            logger.info("No existing index found. Creating new index...")
            self._create_index()
    
    def _create_index(self):
        """Create new FAISS index."""
        dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Use IndexFlatL2 for simplicity (can be optimized later)
        self.index = faiss.IndexFlatL2(dimension)
        logger.info(f"Created new index with dimension {dimension}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the RAG system."""
        if not documents:
            return
        
        logger.info(f"Adding {len(documents)} documents to index...")
        
        # Process documents in chunks
        chunk_size = self.config['system']['chunk_size']
        chunk_overlap = self.config['system']['chunk_overlap']
        
        all_chunks = []
        all_metadata = []
        
        for doc in documents:
            chunks = self._chunk_document(doc['content'], chunk_size, chunk_overlap)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({
                    'source': doc.get('source', 'unknown'),
                    'title': doc.get('title', ''),
                    'chunk_id': i,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
        embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=True)
        
        # Add to index
        self.index.add(embeddings)
        self.documents.extend(all_chunks)
        self.metadata.extend(all_metadata)
        
        # Save index
        self._save_index()
        
        logger.info(f"Successfully added documents. Total vectors: {self.index.ntotal}")
    
    def _chunk_document(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split document into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        if self.index is None or self.index.ntotal == 0:
            logger.warning("No documents in index")
            return []
        
        top_k = top_k or self.config['search']['top_k']
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Filter by relevance threshold
        threshold = self.config['search']['relevance_threshold']
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score
                similarity = 1 / (1 + dist)
                
                if similarity >= threshold:
                    results.append({
                        'text': self.documents[idx],
                        'score': float(similarity),
                        'metadata': self.metadata[idx],
                        'source': self.metadata[idx].get('source', 'unknown')
                    })
        
        return results
    
    def query(self, question: str, use_context: bool = True) -> Dict[str, Any]:
        """Query the RAG system with a question."""
        start_time = datetime.now()
        
        # Search for relevant documents
        if use_context:
            retrieved_docs = self.search(question)
            logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
        else:
            retrieved_docs = []
        
        # Generate response using Ollama
        if retrieved_docs:
            response_data = self.llm_client.answer_with_citations(question, retrieved_docs)
        else:
            # Direct query without context
            response_data = {
                'answer': self.llm_client.generate(question),
                'sources': [],
                'chunks_used': 0,
                'total_chunks': 0
            }
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'question': question,
            'answer': response_data['answer'],
            'sources': response_data['sources'],
            'retrieved_chunks': len(retrieved_docs),
            'processing_time': processing_time,
            'model': self.config['system']['llm_model']
        }
    
    def _save_index(self):
        """Save FAISS index and metadata."""
        index_path = Path(self.config['paths']['index_path'])
        index_path.mkdir(exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_path / "faiss_index"))
        
        # Save metadata
        with open(index_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        
        logger.info("Index saved successfully")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        return {
            'total_documents': self.index.ntotal if self.index else 0,
            'embedding_model': self.config['system']['embedding_model'],
            'llm_model': self.config['system']['llm_model'],
            'chunk_size': self.config['system']['chunk_size'],
            'index_type': 'FAISS',
            'ollama_status': 'connected' if self.llm_client else 'disconnected'
        }
    
    def clear_index(self):
        """Clear the entire index."""
        self._create_index()
        self.documents = []
        self.metadata = []
        self._save_index()
        logger.info("Index cleared")


# Example usage and testing
if __name__ == "__main__":
    # Initialize RAG system
    rag = OllamaRAGSystem()
    
    # Print system stats
    print("RAG System Stats:")
    for key, value in rag.get_stats().items():
        print(f"  {key}: {value}")
    
    # Test with sample documents
    test_docs = [
        {
            'content': """RAG (Retrieval-Augmented Generation) ist eine KI-Architektur, die 
            Informationsabruf mit Textgenerierung kombiniert. Im Finanzsektor ermöglicht RAG 
            die Analyse großer Dokumentenmengen und die Generierung präziser Antworten basierend 
            auf spezifischem Kontext.""",
            'source': 'AI Finance Handbook',
            'title': 'RAG Systeme im Finanzwesen'
        },
        {
            'content': """Multi-Agent-Systeme bestehen aus mehreren autonomen Agenten, die 
            zusammenarbeiten, um komplexe Aufgaben zu lösen. In der Finanzbranche werden sie 
            für Risikobewertung, Portfoliooptimierung und automatisierten Handel eingesetzt.""",
            'source': 'Multi-Agent Finance',
            'title': 'Multi-Agent-Systeme'
        }
    ]
    
    # Add documents
    rag.add_documents(test_docs)
    
    # Test queries
    test_queries = [
        "Was ist ein RAG System?",
        "Wie werden Multi-Agent-Systeme im Finanzbereich eingesetzt?",
        "Erkläre die Vorteile von lokalen LLMs"
    ]
    
    print("\n\nTesting RAG queries:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = rag.query(query)
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources used: {len(result['sources'])}")
        print(f"Processing time: {result['processing_time']:.2f}s")