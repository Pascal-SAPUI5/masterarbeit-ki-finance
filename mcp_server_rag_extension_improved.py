"""
MCP Server RAG Extension - Improved Version
Provides enhanced RAG-specific tools with better output formatting
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime
from scripts.rag_system import RAGSystem, PDFProcessor
import os

class MCPRAGExtensionImproved:
    """Enhanced RAG extensions for MCP server with better output."""
    
    def __init__(self):
        self.rag_system = None
        self.pdf_processor = PDFProcessor()
        self._init_rag_system()
    
    def _init_rag_system(self):
        """Initialize RAG system if not already done."""
        try:
            self.rag_system = RAGSystem("config/rag_config.yaml", cpu_only=True)
        except Exception as e:
            print(f"RAG system initialization failed: {e}")
    
    def search_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search indexed documents using RAG with enhanced output."""
        if not self.rag_system:
            return {"error": "RAG system not initialized"}
        
        try:
            # Get raw search results
            results = self.rag_system.searcher.search(query, top_k)
            
            # Format results for better display
            formatted_results = []
            for i, result in enumerate(results):
                meta = result.get("metadata", {})
                formatted_result = {
                    "rank": i + 1,
                    "relevance_score": round(result.get("relevance", 0), 4),
                    "document": {
                        "title": meta.get("title", "Unknown Title"),
                        "author": meta.get("author", "Unknown Author"),
                        "year": meta.get("year", "Unknown Year"),
                        "doi": meta.get("doi", ""),
                        "file_path": result.get("path", ""),
                        "page": result.get("page", 0)
                    },
                    "chunk": {
                        "text": result.get("chunk", ""),
                        "length": len(result.get("chunk", "")),
                        "context": self._get_extended_context(result)
                    },
                    "citation": {
                        "apa": self._generate_apa_citation(meta),
                        "in_text": f"({meta.get('author', 'Unknown')}, {meta.get('year', 'n.d.')}, S. {result.get('page', '?')})"
                    }
                }
                formatted_results.append(formatted_result)
            
            # Generate summary
            summary = self._generate_search_summary(query, formatted_results)
            
            return {
                "query": query,
                "total_results": len(formatted_results),
                "results": formatted_results,
                "summary": summary,
                "search_time": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {"error": f"Search failed: {str(e)}", "status": "error"}
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get comprehensive RAG system statistics."""
        if not self.rag_system or not self.rag_system.indexer:
            return {"error": "RAG system not initialized", "status": "error"}
        
        try:
            # Get index stats
            index_size = self.rag_system.indexer.index.ntotal if hasattr(self.rag_system.indexer.index, 'ntotal') else 0
            
            # Analyze metadata
            documents = {}
            total_chunks = len(self.rag_system.indexer.metadata)
            total_pages = 0
            
            for item in self.rag_system.indexer.metadata:
                doc_path = item.get("path", "")
                if doc_path not in documents:
                    documents[doc_path] = {
                        "metadata": item.get("metadata", {}),
                        "chunks": 0,
                        "pages": set()
                    }
                documents[doc_path]["chunks"] += 1
                documents[doc_path]["pages"].add(item.get("page", 0))
                
            # Calculate document stats
            doc_stats = []
            for path, info in documents.items():
                doc_stats.append({
                    "file": Path(path).name,
                    "title": info["metadata"].get("title", "Unknown"),
                    "author": info["metadata"].get("author", "Unknown"),
                    "year": info["metadata"].get("year", "Unknown"),
                    "chunks": info["chunks"],
                    "pages": len(info["pages"])
                })
                total_pages += len(info["pages"])
            
            # Get index file size
            index_path = Path(self.rag_system.config["paths"]["index_path"])
            index_size_mb = 0
            if index_path.exists():
                for file in index_path.iterdir():
                    if file.is_file():
                        index_size_mb += file.stat().st_size / (1024 * 1024)
            
            # Check last indexing time
            metadata_file = index_path / "metadata.json"
            last_indexed = "Unknown"
            if metadata_file.exists():
                last_indexed = datetime.fromtimestamp(metadata_file.stat().st_mtime).isoformat()
            
            stats = {
                "overview": {
                    "total_documents": len(documents),
                    "total_chunks": total_chunks,
                    "total_pages": total_pages,
                    "average_chunks_per_doc": round(total_chunks / len(documents), 2) if documents else 0,
                    "index_size_entries": index_size,
                    "index_size_mb": round(index_size_mb, 2),
                    "embedding_dimension": self.rag_system.indexer.dimension,
                    "embedding_model": self.rag_system.config.get("system", {}).get("embedding_model", "Unknown"),
                    "last_indexed": last_indexed
                },
                "documents": sorted(doc_stats, key=lambda x: x["year"], reverse=True)[:10],  # Top 10 recent
                "system_info": {
                    "llm_available": self._check_llm_availability(),
                    "llm_model": self.rag_system.config.get("system", {}).get("llm_model", "Unknown"),
                    "index_path": str(index_path),
                    "config_path": "config/rag_config.yaml"
                },
                "status": "success"
            }
            
            return stats
            
        except Exception as e:
            return {"error": f"Failed to get stats: {str(e)}", "status": "error"}
    
    def search_and_summarize(self, query: str, top_k: int = 5, use_claude: bool = False) -> Dict[str, Any]:
        """Search documents and generate a comprehensive summary."""
        if not self.rag_system:
            return {"error": "RAG system not initialized", "status": "error"}
        
        try:
            # First, perform the search
            search_results = self.search_documents(query, top_k)
            
            if search_results.get("status") != "success":
                return search_results
            
            # Extract chunks for summarization
            chunks = []
            citations = []
            for result in search_results["results"]:
                chunks.append(result["chunk"]["text"])
                citations.append(result["citation"]["in_text"])
            
            # Generate summary
            if use_claude:
                # This would use Claude API if available
                summary = self._generate_claude_summary(query, chunks, citations)
            else:
                # Use the built-in LLM or fallback
                summary = self._generate_local_summary(query, chunks, citations)
            
            return {
                "query": query,
                "summary": summary,
                "sources_used": len(chunks),
                "citations": citations,
                "search_results": search_results["results"],
                "generated_at": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            return {"error": f"Search and summarize failed: {str(e)}", "status": "error"}
    
    def _get_extended_context(self, result: Dict) -> str:
        """Get extended context around the chunk."""
        # For now, return the chunk itself
        # Could be enhanced to fetch more context from the original document
        return result.get("chunk", "")
    
    def _generate_apa_citation(self, metadata: Dict) -> str:
        """Generate APA format citation."""
        author = metadata.get("author", "Unknown Author")
        year = metadata.get("year", "n.d.")
        title = metadata.get("title", "Unknown Title")
        return f"{author} ({year}). {title}."
    
    def _generate_search_summary(self, query: str, results: List[Dict]) -> str:
        """Generate a summary of search results."""
        if not results:
            return f"No results found for query: '{query}'"
        
        summary_parts = [
            f"Found {len(results)} relevant documents for query: '{query}'",
            "",
            "Top results:"
        ]
        
        for result in results[:3]:  # Top 3
            doc = result["document"]
            summary_parts.append(
                f"- {doc['title']} by {doc['author']} ({doc['year']}) - "
                f"Relevance: {result['relevance_score']:.2f}"
            )
        
        return "\n".join(summary_parts)
    
    def _generate_local_summary(self, query: str, chunks: List[str], citations: List[str]) -> str:
        """Generate summary using local LLM or fallback method."""
        try:
            # Try using the RAG system's query method
            context = "\n\n".join([f"[{i+1}] {chunk}" for i, chunk in enumerate(chunks)])
            result = self.rag_system.query(query, top_k=len(chunks))
            
            if "answer" in result:
                # Add citations to the answer
                answer = result["answer"]
                # Append citations
                answer += "\n\nSources: " + ", ".join(citations)
                return answer
            else:
                # Fallback to simple concatenation
                return self._fallback_summary(query, chunks, citations)
                
        except Exception:
            return self._fallback_summary(query, chunks, citations)
    
    def _fallback_summary(self, query: str, chunks: List[str], citations: List[str]) -> str:
        """Fallback summary when LLM is not available."""
        summary = f"Based on the search for '{query}', here are the key findings:\n\n"
        
        for i, (chunk, citation) in enumerate(zip(chunks[:3], citations[:3])):
            # Truncate chunk to first 200 characters
            truncated = chunk[:200] + "..." if len(chunk) > 200 else chunk
            summary += f"{i+1}. {truncated} {citation}\n\n"
        
        summary += f"\nTotal sources analyzed: {len(chunks)}"
        return summary
    
    def _generate_claude_summary(self, query: str, chunks: List[str], citations: List[str]) -> str:
        """Generate summary using Claude API (placeholder)."""
        # This would integrate with Claude API if available
        # For now, return a message
        return "Claude API integration not yet implemented. Using local summarization."
    
    def _check_llm_availability(self) -> bool:
        """Check if Ollama LLM is available."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def index_documents(self, path: str) -> Dict[str, Any]:
        """Index documents from a directory."""
        if not self.rag_system:
            return {"error": "RAG system not initialized"}
        
        try:
            # Check if path exists
            doc_path = Path(path)
            if not doc_path.exists():
                return {"error": f"Path does not exist: {path}", "status": "error"}
            
            # Count PDFs
            pdfs = list(doc_path.rglob("*.pdf"))
            if not pdfs:
                return {"error": f"No PDF files found in {path}", "status": "error"}
            
            # Index documents
            self.rag_system.indexer.index_directory(path)
            
            # Get updated stats
            stats = self.get_rag_stats()
            
            return {
                "status": "success",
                "message": f"Successfully indexed {len(pdfs)} documents from {path}",
                "documents_indexed": len(pdfs),
                "total_documents": stats.get("overview", {}).get("total_documents", 0),
                "total_chunks": stats.get("overview", {}).get("total_chunks", 0)
            }
        except Exception as e:
            return {"error": f"Indexing failed: {str(e)}", "status": "error"}
    
    def extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content from a PDF file."""
        try:
            pages = self.pdf_processor.extract_text_with_ocr(pdf_path)
            metadata = self.pdf_processor.extract_metadata(pdf_path)
            
            # Calculate statistics
            total_chars = sum(len(page["text"]) for page in pages)
            total_words = sum(len(page["text"].split()) for page in pages)
            
            return {
                "metadata": metadata,
                "pages": pages,
                "statistics": {
                    "total_pages": len(pages),
                    "total_characters": total_chars,
                    "total_words": total_words,
                    "average_words_per_page": round(total_words / len(pages), 2) if pages else 0
                },
                "status": "success"
            }
        except Exception as e:
            return {"error": f"PDF extraction failed: {str(e)}", "status": "error"}
    
    def get_additional_tools(self) -> List[Dict[str, Any]]:
        """Returns list of additional RAG-specific tools."""
        return [
            {
                "name": "search_documents",
                "description": "Durchsucht indizierte Dokumente mit detaillierten Ergebnissen und Scores",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Suchanfrage"
                        },
                        "top_k": {
                            "type": "integer",
                            "default": 5,
                            "description": "Anzahl der Ergebnisse"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_rag_stats",
                "description": "Zeigt umfassende RAG-System Statistiken mit Dokumentendetails",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "search_and_summarize",
                "description": "Sucht Dokumente und generiert eine Zusammenfassung mit Zitaten",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Suchanfrage"
                        },
                        "top_k": {
                            "type": "integer",
                            "default": 5,
                            "description": "Anzahl der Quellen"
                        },
                        "use_claude": {
                            "type": "boolean",
                            "default": False,
                            "description": "Claude API für Zusammenfassung verwenden"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "index_documents",
                "description": "Indiziert Dokumente aus einem Verzeichnis für RAG",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Pfad zum Dokumentenverzeichnis"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "extract_pdf_content",
                "description": "Extrahiert Inhalt und Metadaten aus einer PDF-Datei",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pdf_path": {
                            "type": "string",
                            "description": "Pfad zur PDF-Datei"
                        }
                    },
                    "required": ["pdf_path"]
                }
            }
        ]
    
    async def handle_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handles RAG-specific tool calls."""
        if tool_name == "search_documents":
            return self.search_documents(
                query=args.get("query"),
                top_k=args.get("top_k", 5)
            )
        elif tool_name == "get_rag_stats":
            return self.get_rag_stats()
        elif tool_name == "search_and_summarize":
            return self.search_and_summarize(
                query=args.get("query"),
                top_k=args.get("top_k", 5),
                use_claude=args.get("use_claude", False)
            )
        elif tool_name == "index_documents":
            return self.index_documents(path=args.get("path"))
        elif tool_name == "extract_pdf_content":
            return self.extract_pdf_content(pdf_path=args.get("pdf_path"))
        else:
            return {"error": f"Unknown RAG tool: {tool_name}", "status": "error"}