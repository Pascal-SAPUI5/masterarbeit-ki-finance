#!/usr/bin/env python3
"""
RAG System Usage Examples
Demonstrates various ways to use the RAG system for document search and analysis.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.rag_system import RAGSystem
from scripts.search_literature import LiteratureSearcher
from scripts.manage_references import ReferenceManager
from memory_system import get_memory


def example_basic_rag_search():
    """Basic RAG search example."""
    print("=== Basic RAG Search Example ===")
    
    # Initialize RAG system
    rag = RAGSystem("config/rag_config.yaml", cpu_only=True)
    
    # Search for documents
    query = "AI agents in financial services"
    results = rag.search(query, top_k=5)
    
    print(f"Query: {query}")
    print(f"Found {len(results)} results:")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'Unknown Title')}")
        print(f"   Author: {result.get('author', 'Unknown')}")
        print(f"   Relevance: {result.get('relevance', 0):.3f}")
        print(f"   Text: {result.get('text', '')[:200]}...")


def example_literature_search_workflow():
    """Complete literature search workflow example."""
    print("\n=== Literature Search Workflow Example ===")
    
    # Initialize searcher
    searcher = LiteratureSearcher("config/research-criteria.yaml")
    
    # Search multiple databases
    search_terms = [
        "multi-agent systems banking",
        "RAG finance applications",
        "conversational AI financial services"
    ]
    
    all_results = []
    for term in search_terms:
        print(f"\nSearching for: {term}")
        results = searcher.search(
            query=term,
            databases=["scopus", "web_of_science"],
            max_results=25
        )
        all_results.extend(results)
        print(f"Found {len(results)} papers")
    
    # Filter by quality
    q1_papers = searcher.filter_by_quality(
        all_results, 
        min_impact_factor=3.0,
        quality_levels=["Q1"]
    )
    
    print(f"\nAfter quality filtering: {len(q1_papers)} Q1 papers")
    
    # Sort by relevance and recency
    sorted_papers = sorted(
        q1_papers, 
        key=lambda x: (x.get('year', 0), x.get('citation_count', 0)), 
        reverse=True
    )
    
    # Display top results
    print("\nTop 5 papers:")
    for i, paper in enumerate(sorted_papers[:5], 1):
        print(f"{i}. {paper.get('title', 'Unknown Title')}")
        print(f"   Year: {paper.get('year', 'N/A')}")
        print(f"   Journal: {paper.get('journal', 'N/A')}")
        print(f"   Impact Factor: {paper.get('impact_factor', 'N/A')}")
        print(f"   Citations: {paper.get('citation_count', 'N/A')}")


def example_rag_with_context():
    """RAG search with context and memory integration."""
    print("\n=== RAG with Context Example ===")
    
    # Get memory system
    memory = get_memory()
    
    # Store research context
    context = {
        "research_topic": "AI agents in finance",
        "focus_areas": [
            "customer service automation",
            "risk management",
            "regulatory compliance",
            "process optimization"
        ],
        "excluded_topics": [
            "cryptocurrency",
            "high-frequency trading"
        ]
    }
    
    memory.store_context("research_focus", context)
    print("Stored research context in memory")
    
    # Initialize RAG with context awareness
    rag = RAGSystem("config/rag_config.yaml", cpu_only=True)
    
    # Contextual searches
    queries = [
        "How do AI agents improve customer service in banking?",
        "What are the regulatory challenges for AI agents in finance?",
        "How can AI agents help with risk management processes?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        
        # Get contextual results
        results = rag.search(query, top_k=3)
        
        # Get LLM-enhanced answer if available
        try:
            answer = rag.get_answer(query, context=context)
            print(f"Answer: {answer[:300]}...")
        except Exception as e:
            print(f"LLM answer not available: {e}")
        
        # Show source documents
        print("Sources:")
        for i, result in enumerate(results[:2], 1):
            print(f"  {i}. {result.get('title', 'Unknown')} (Relevance: {result.get('relevance', 0):.3f})")


def example_document_indexing():
    """Document indexing and processing example."""
    print("\n=== Document Indexing Example ===")
    
    rag = RAGSystem("config/rag_config.yaml", cpu_only=True)
    
    # Index documents from a specific directory
    docs_path = "./literatur/finance/"
    
    if Path(docs_path).exists():
        print(f"Indexing documents from: {docs_path}")
        
        # Index with progress tracking
        result = rag.index_documents(
            docs_path,
            force_reindex=False,
            extract_metadata=True
        )
        
        print(f"Indexing results:")
        print(f"  Processed: {result.get('processed_count', 0)} documents")
        print(f"  Indexed: {result.get('indexed_count', 0)} documents")
        print(f"  Skipped: {result.get('skipped_count', 0)} documents")
        print(f"  Errors: {result.get('error_count', 0)} documents")
        
        # Get index statistics
        stats = rag.get_index_stats()
        print(f"\nIndex statistics:")
        print(f"  Total documents: {stats.get('total_documents', 0)}")
        print(f"  Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  Index size: {stats.get('index_size', 'N/A')}")
    else:
        print(f"Documents directory not found: {docs_path}")


def example_citation_management():
    """Citation management and formatting example."""
    print("\n=== Citation Management Example ===")
    
    ref_manager = ReferenceManager("config/research-criteria.yaml")
    
    # Example paper metadata
    papers = [
        {
            "title": "Multi-Agent Systems in Banking: A Comprehensive Review",
            "authors": ["Smith, J.", "Doe, A.", "Johnson, M."],
            "year": 2024,
            "journal": "Journal of Financial Technology",
            "volume": 15,
            "issue": 3,
            "pages": "45-72",
            "doi": "10.1000/jft.2024.15.3.45"
        },
        {
            "title": "RAG-based Customer Service Automation in Finance",
            "authors": ["Brown, K.", "Wilson, L."],
            "year": 2023,
            "journal": "AI in Finance Quarterly",
            "volume": 8,
            "issue": 2,
            "pages": "123-145",
            "doi": "10.1000/aifq.2023.8.2.123"
        }
    ]
    
    # Format citations
    print("APA 7 Citations:")
    for paper in papers:
        citation = ref_manager.format_citation(paper, style="apa7")
        print(f"  {citation}")
    
    # Create bibliography
    bibliography = ref_manager.create_bibliography(papers, style="apa7")
    print(f"\nBibliography ({len(bibliography)} entries):")
    for entry in bibliography:
        print(f"  {entry}")
    
    # Export to different formats
    formats = ["bibtex", "ris"]
    for fmt in formats:
        try:
            exported = ref_manager.export_references(papers, format=fmt)
            print(f"\n{fmt.upper()} export preview:")
            print(exported[:200] + "..." if len(exported) > 200 else exported)
        except Exception as e:
            print(f"Export to {fmt} failed: {e}")


def example_advanced_rag_features():
    """Advanced RAG features demonstration."""
    print("\n=== Advanced RAG Features Example ===")
    
    rag = RAGSystem("config/rag_config.yaml", cpu_only=True)
    
    # Multi-step reasoning query
    complex_query = """
    Based on the literature, what are the key success factors for implementing 
    AI agents in German banking institutions, considering regulatory requirements 
    and customer acceptance factors?
    """
    
    print(f"Complex Query: {complex_query}")
    
    # Get comprehensive results
    results = rag.search(complex_query, top_k=10)
    
    # Analyze results by theme
    themes = {
        "regulatory": ["regulation", "compliance", "GDPR", "BaFin"],
        "technical": ["implementation", "architecture", "integration"],
        "customer": ["acceptance", "trust", "user experience"],
        "business": ["ROI", "cost", "efficiency", "productivity"]
    }
    
    theme_results = {}
    for theme, keywords in themes.items():
        theme_docs = []
        for result in results:
            text = result.get('text', '').lower()
            if any(keyword.lower() in text for keyword in keywords):
                theme_docs.append(result)
        theme_results[theme] = theme_docs
    
    # Summary by theme
    print("\nResults by theme:")
    for theme, docs in theme_results.items():
        print(f"  {theme.capitalize()}: {len(docs)} relevant documents")
        if docs:
            top_doc = max(docs, key=lambda x: x.get('relevance', 0))
            print(f"    Top result: {top_doc.get('title', 'Unknown')[:60]}...")
    
    # Generate summary if LLM available
    try:
        summary = rag.generate_summary(
            query=complex_query,
            documents=results[:5],
            focus_areas=list(themes.keys())
        )
        print(f"\nAI-Generated Summary:")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
    except Exception as e:
        print(f"Summary generation not available: {e}")


def example_performance_monitoring():
    """Performance monitoring and optimization example."""
    print("\n=== Performance Monitoring Example ===")
    
    import time
    import psutil
    import os
    
    # Monitor system resources
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Initial memory usage: {initial_memory:.1f} MB")
    
    # Time multiple operations
    rag = RAGSystem("config/rag_config.yaml", cpu_only=True)
    
    # Benchmark search performance
    test_queries = [
        "AI agents customer service",
        "machine learning risk management",
        "automated financial analysis",
        "regulatory compliance AI",
        "chatbot banking applications"
    ]
    
    search_times = []
    for query in test_queries:
        start_time = time.time()
        results = rag.search(query, top_k=5)
        end_time = time.time()
        
        search_time = end_time - start_time
        search_times.append(search_time)
        
        print(f"Query '{query[:30]}...': {search_time:.2f}s ({len(results)} results)")
    
    # Performance statistics
    avg_search_time = sum(search_times) / len(search_times)
    max_search_time = max(search_times)
    min_search_time = min(search_times)
    
    print(f"\nSearch Performance Statistics:")
    print(f"  Average: {avg_search_time:.2f}s")
    print(f"  Min: {min_search_time:.2f}s")
    print(f"  Max: {max_search_time:.2f}s")
    
    # Final memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f"\nMemory Usage:")
    print(f"  Initial: {initial_memory:.1f} MB")
    print(f"  Final: {final_memory:.1f} MB")
    print(f"  Increase: {memory_increase:.1f} MB")


def main():
    """Run all examples."""
    examples = [
        example_basic_rag_search,
        example_literature_search_workflow,
        example_rag_with_context,
        example_document_indexing,
        example_citation_management,
        example_advanced_rag_features,
        example_performance_monitoring
    ]
    
    for example_func in examples:
        try:
            example_func()
            print("\n" + "="*80)
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")
            print("="*80)


if __name__ == "__main__":
    main()