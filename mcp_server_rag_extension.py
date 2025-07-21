"""
MCP Server RAG Extension
Provides RAG-specific tools for the MCP server
"""
from typing import Dict, Any, List
import json
from pathlib import Path
from scripts.rag_system import RAGSystem, PDFProcessor

class MCPRAGExtension:
    """RAG extensions for MCP server."""
    
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
        """Search indexed documents using RAG."""
        if not self.rag_system:
            return {"error": "RAG system not initialized"}
        
        try:
            result = self.rag_system.query(query, top_k)
            return result
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
    
    def index_documents(self, path: str) -> Dict[str, Any]:
        """Index documents from a directory."""
        if not self.rag_system:
            return {"error": "RAG system not initialized"}
        
        try:
            self.rag_system.indexer.index_directory(path)
            return {"status": "success", "message": f"Indexed documents from {path}"}
        except Exception as e:
            return {"error": f"Indexing failed: {str(e)}"}
    
    def extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content from a PDF file."""
        try:
            pages = self.pdf_processor.extract_text_with_ocr(pdf_path)
            metadata = self.pdf_processor.extract_metadata(pdf_path)
            
            return {
                "metadata": metadata,
                "pages": pages,
                "total_pages": len(pages)
            }
        except Exception as e:
            return {"error": f"PDF extraction failed: {str(e)}"}
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        if not self.rag_system or not self.rag_system.indexer:
            return {"error": "RAG system not initialized"}
        
        try:
            stats = {
                "indexed_documents": len(self.rag_system.indexer.metadata),
                "index_size": self.rag_system.indexer.index.ntotal if hasattr(self.rag_system.indexer.index, 'ntotal') else 0,
                "embedding_dimension": self.rag_system.indexer.dimension,
                "llm_available": self._check_llm_availability()
            }
            return stats
        except Exception as e:
            return {"error": f"Failed to get stats: {str(e)}"}
    
    def _check_llm_availability(self) -> bool:
        """Check if Ollama LLM is available."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_additional_tools(self) -> List[Dict[str, Any]]:
        """Returns list of additional RAG-specific tools."""
        return [
            {
                "name": "search_documents",
                "description": "Durchsucht indizierte Dokumente mit RAG-System",
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
                "description": "Extrahiert Inhalt aus einer PDF-Datei",
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
            },
            {
                "name": "get_rag_stats",
                "description": "Zeigt RAG-System Statistiken",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
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
        elif tool_name == "index_documents":
            return self.index_documents(path=args.get("path"))
        elif tool_name == "extract_pdf_content":
            return self.extract_pdf_content(pdf_path=args.get("pdf_path"))
        elif tool_name == "get_rag_stats":
            return self.get_rag_stats()
        else:
            return {"error": f"Unknown RAG tool: {tool_name}"}