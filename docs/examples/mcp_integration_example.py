#!/usr/bin/env python3
"""
MCP Integration Examples
Demonstrates how to integrate with the MCP server for research automation.
"""

import json
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp_server_rag_extension_improved import MCPRAGExtensionImproved


class MCPExamples:
    """Examples for MCP server integration."""
    
    def __init__(self):
        self.mcp_rag = MCPRAGExtensionImproved()
    
    def example_document_search(self):
        """Example of document search via MCP."""
        print("=== MCP Document Search Example ===")
        
        # Search query
        query = "What are the benefits of AI agents in banking?"
        
        # Call MCP search function
        result = self.mcp_rag.search_documents(query, top_k=5)
        
        print(f"Query: {query}")
        print(f"Results: {json.dumps(result, indent=2)}")
        
        return result
    
    def example_document_indexing(self):
        """Example of document indexing via MCP."""
        print("\n=== MCP Document Indexing Example ===")
        
        # Index documents
        docs_path = "./literatur/finance/"
        
        try:
            result = self.mcp_rag.index_documents(
                document_path=docs_path,
                force_reindex=False,
                extract_metadata=True
            )
            
            print(f"Indexing result: {json.dumps(result, indent=2)}")
            return result
        except Exception as e:
            print(f"Indexing failed: {e}")
            return {"error": str(e)}
    
    def example_literature_search(self):
        """Example of literature search via MCP."""
        print("\n=== MCP Literature Search Example ===")
        
        # Search parameters
        search_params = {
            "query": "multi-agent systems finance",
            "databases": ["scopus", "web_of_science"],
            "years": "2020-2025",
            "quality": "q1",
            "max_results": 20
        }
        
        try:
            result = self.mcp_rag.search_literature(**search_params)
            
            print(f"Search parameters: {json.dumps(search_params, indent=2)}")
            print(f"Results: {json.dumps(result, indent=2)}")
            return result
        except Exception as e:
            print(f"Literature search failed: {e}")
            return {"error": str(e)}
    
    def example_citation_verification(self):
        """Example of citation verification via MCP."""
        print("\n=== MCP Citation Verification Example ===")
        
        # Example citations to verify
        citations = [
            {
                "title": "AI Agents in Financial Services",
                "authors": ["Smith, J.", "Doe, A."],
                "year": 2024,
                "journal": "Journal of Finance Technology",
                "doi": "10.1000/example"
            },
            {
                "title": "Multi-Agent Banking Systems",
                "authors": ["Brown, K."],
                "year": 2023,
                "journal": "AI Finance Review"
            }
        ]
        
        try:
            result = self.mcp_rag.verify_citations(
                citations=citations,
                style="apa7",
                include_doi=True
            )
            
            print(f"Citations to verify: {json.dumps(citations, indent=2)}")
            print(f"Verification result: {json.dumps(result, indent=2)}")
            return result
        except Exception as e:
            print(f"Citation verification failed: {e}")
            return {"error": str(e)}
    
    def example_reference_management(self):
        """Example of reference management via MCP."""
        print("\n=== MCP Reference Management Example ===")
        
        # Example references
        references = [
            {
                "title": "Artificial Intelligence in Banking",
                "authors": ["Wilson, M.", "Taylor, R."],
                "year": 2024,
                "journal": "Banking Technology Review",
                "volume": 45,
                "issue": 2,
                "pages": "12-28"
            }
        ]
        
        # Export to different formats
        formats = ["bibtex", "ris", "citavi"]
        
        for fmt in formats:
            try:
                result = self.mcp_rag.manage_references(
                    action="export",
                    format=fmt,
                    input_data=references
                )
                
                print(f"\nExport to {fmt.upper()}:")
                print(f"Result: {json.dumps(result, indent=2)}")
            except Exception as e:
                print(f"Export to {fmt} failed: {e}")
    
    def example_memory_operations(self):
        """Example of memory operations via MCP."""
        print("\n=== MCP Memory Operations Example ===")
        
        # Store research context
        context_data = {
            "research_topic": "AI agents in German banking",
            "methodology": "systematic literature review + case studies",
            "key_findings": [
                "Regulatory compliance is main challenge",
                "Customer acceptance varies by age group",
                "ROI achieved within 18 months average"
            ],
            "next_steps": ["Expert interviews", "Case study analysis"]
        }
        
        try:
            # Store context
            store_result = self.mcp_rag.store_context(
                context_type="research_progress",
                data=context_data,
                tags=["methodology", "findings"]
            )
            
            print(f"Stored context: {json.dumps(store_result, indent=2)}")
            
            # Retrieve context
            retrieve_result = self.mcp_rag.retrieve_context(
                context_type="research_progress",
                tags=["findings"]
            )
            
            print(f"Retrieved context: {json.dumps(retrieve_result, indent=2)}")
            
            return {"store": store_result, "retrieve": retrieve_result}
        except Exception as e:
            print(f"Memory operations failed: {e}")
            return {"error": str(e)}
    
    def example_quality_assessment(self):
        """Example of research quality assessment via MCP."""
        print("\n=== MCP Quality Assessment Example ===")
        
        # Example paper for quality assessment
        paper = {
            "title": "Machine Learning Applications in Risk Management",
            "authors": ["Anderson, P.", "Lee, S.", "Chen, W."],
            "year": 2023,
            "journal": "Risk Management Quarterly",
            "impact_factor": 4.2,
            "citation_count": 47,
            "methodology": "empirical study",
            "sample_size": 250,
            "peer_reviewed": True
        }
        
        try:
            result = self.mcp_rag.assess_quality(
                paper=paper,
                criteria={
                    "min_impact_factor": 3.0,
                    "min_citation_count": 10,
                    "required_methodology": ["empirical", "case study"],
                    "min_sample_size": 50
                }
            )
            
            print(f"Paper: {json.dumps(paper, indent=2)}")
            print(f"Quality assessment: {json.dumps(result, indent=2)}")
            return result
        except Exception as e:
            print(f"Quality assessment failed: {e}")
            return {"error": str(e)}
    
    def example_workflow_automation(self):
        """Example of automated research workflow."""
        print("\n=== MCP Workflow Automation Example ===")
        
        workflow_steps = [
            "search_literature",
            "filter_quality", 
            "extract_findings",
            "generate_summary",
            "create_bibliography"
        ]
        
        # Research query
        research_query = "AI chatbots customer service banking"
        
        results = {}
        
        try:
            # Step 1: Literature search
            print("Step 1: Searching literature...")
            lit_results = self.mcp_rag.search_literature(
                query=research_query,
                databases=["scopus"],
                quality="q1",
                max_results=10
            )
            results["literature_search"] = lit_results
            
            # Step 2: Document search in indexed papers
            print("Step 2: Searching indexed documents...")
            doc_results = self.mcp_rag.search_documents(
                query=research_query,
                top_k=5
            )
            results["document_search"] = doc_results
            
            # Step 3: Generate research summary
            print("Step 3: Generating research summary...")
            summary_data = {
                "query": research_query,
                "literature_count": len(lit_results.get("results", [])),
                "document_count": len(doc_results.get("results", [])),
                "key_themes": ["customer satisfaction", "implementation challenges", "ROI"]
            }
            results["summary"] = summary_data
            
            print(f"Workflow completed successfully:")
            print(f"Results: {json.dumps(results, indent=2)}")
            
            return results
        except Exception as e:
            print(f"Workflow automation failed: {e}")
            return {"error": str(e)}


async def example_async_operations():
    """Example of asynchronous MCP operations."""
    print("\n=== Async MCP Operations Example ===")
    
    mcp = MCPExamples()
    
    # Multiple concurrent searches
    queries = [
        "AI agents customer service",
        "machine learning risk assessment", 
        "automated financial analysis",
        "regulatory compliance technology"
    ]
    
    async def search_async(query):
        """Async wrapper for search operations."""
        return mcp.mcp_rag.search_documents(query, top_k=3)
    
    try:
        # Run multiple searches concurrently
        tasks = [search_async(query) for query in queries]
        results = await asyncio.gather(*tasks)
        
        print("Concurrent search results:")
        for query, result in zip(queries, results):
            print(f"  Query: {query}")
            print(f"  Results: {len(result.get('results', []))} documents found")
        
        return dict(zip(queries, results))
    except Exception as e:
        print(f"Async operations failed: {e}")
        return {"error": str(e)}


def example_error_handling():
    """Example of error handling in MCP operations."""
    print("\n=== MCP Error Handling Example ===")
    
    mcp = MCPExamples()
    
    # Test various error conditions
    error_tests = [
        {
            "name": "Invalid document path",
            "operation": lambda: mcp.mcp_rag.index_documents("/nonexistent/path/")
        },
        {
            "name": "Empty query search",
            "operation": lambda: mcp.mcp_rag.search_documents("")
        },
        {
            "name": "Invalid citation format",
            "operation": lambda: mcp.mcp_rag.verify_citations(
                citations=[{"invalid": "data"}],
                style="invalid_style"
            )
        }
    ]
    
    for test in error_tests:
        try:
            print(f"\nTesting: {test['name']}")
            result = test["operation"]()
            print(f"Unexpected success: {result}")
        except Exception as e:
            print(f"Expected error caught: {type(e).__name__}: {e}")


def example_configuration_validation():
    """Example of configuration validation."""
    print("\n=== Configuration Validation Example ===")
    
    # Test different configuration scenarios
    configs = [
        {
            "name": "Valid config",
            "config": {
                "embedding_model": "all-MiniLM-L6-v2",
                "llm_model": "phi3:mini",
                "cpu_only": True,
                "top_k": 5
            }
        },
        {
            "name": "Invalid model config",
            "config": {
                "embedding_model": "nonexistent-model",
                "llm_model": "invalid-model",
                "cpu_only": True
            }
        }
    ]
    
    for config_test in configs:
        try:
            print(f"\nTesting: {config_test['name']}")
            # Simulate configuration validation
            config = config_test["config"]
            
            # Basic validation
            required_fields = ["embedding_model", "llm_model", "cpu_only"]
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            print(f"Configuration valid: {json.dumps(config, indent=2)}")
            
        except Exception as e:
            print(f"Configuration error: {e}")


def main():
    """Run all MCP integration examples."""
    mcp_examples = MCPExamples()
    
    # Synchronous examples
    sync_examples = [
        mcp_examples.example_document_search,
        mcp_examples.example_document_indexing,
        mcp_examples.example_literature_search,
        mcp_examples.example_citation_verification,
        mcp_examples.example_reference_management,
        mcp_examples.example_memory_operations,
        mcp_examples.example_quality_assessment,
        mcp_examples.example_workflow_automation,
        example_error_handling,
        example_configuration_validation
    ]
    
    for example_func in sync_examples:
        try:
            example_func()
            print("\n" + "="*80)
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")
            print("="*80)
    
    # Asynchronous example
    try:
        asyncio.run(example_async_operations())
    except Exception as e:
        print(f"Error in async operations: {e}")


if __name__ == "__main__":
    main()