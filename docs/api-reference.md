# API Reference

## MCP Server Tools

The MCP server exposes several tools for research automation and document processing. All tools follow the MCP (Model Context Protocol) specification.

### Literature Search Tools

#### `search_literature`

Search academic databases for research papers.

**Parameters:**
- `query` (string, required): Search query
- `databases` (array, optional): Target databases ['scopus', 'web_of_science', 'acm', 'ieee']
- `years` (string, optional): Publication year range (e.g., "2020-2025")
- `quality` (string, optional): Quality filter ['q1', 'a*', 'any']
- `max_results` (integer, optional): Maximum results (default: 50)

**Example:**
```json
{
  "name": "search_literature",
  "arguments": {
    "query": "AI agents finance banking",
    "databases": ["scopus", "web_of_science"],
    "years": "2022-2025",
    "quality": "q1",
    "max_results": 25
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "title": "Multi-Agent Systems in Financial Services",
      "authors": ["Smith, J.", "Doe, A."],
      "year": 2024,
      "journal": "Journal of Financial Technology",
      "impact_factor": 4.2,
      "doi": "10.1000/example",
      "abstract": "This paper explores...",
      "url": "https://example.com/paper",
      "citation_count": 15,
      "database": "scopus"
    }
  ],
  "total_found": 127,
  "search_time": 2.3,
  "databases_searched": ["scopus", "web_of_science"]
}
```

#### `verify_citations`

Validate and format citations according to academic standards.

**Parameters:**
- `citations` (array, required): List of citation objects
- `style` (string, optional): Citation style ['apa7', 'ieee', 'chicago'] (default: 'apa7')
- `include_doi` (boolean, optional): Include DOI in citation (default: true)

**Example:**
```json
{
  "name": "verify_citations",
  "arguments": {
    "citations": [
      {
        "title": "AI in Banking",
        "authors": ["Smith, J."],
        "year": 2024,
        "journal": "Finance Tech Journal",
        "doi": "10.1000/example"
      }
    ],
    "style": "apa7"
  }
}
```

### Document Processing Tools

#### `index_documents`

Index PDF documents for RAG-based searching.

**Parameters:**
- `document_path` (string, required): Path to documents or single document
- `force_reindex` (boolean, optional): Force reindexing of existing documents
- `extract_metadata` (boolean, optional): Extract document metadata (default: true)
- `use_ocr` (boolean, optional): Use OCR for scanned documents (default: true)

**Example:**
```json
{
  "name": "index_documents",
  "arguments": {
    "document_path": "./literatur/finance/",
    "force_reindex": false,
    "extract_metadata": true,
    "use_ocr": true
  }
}
```

**Response:**
```json
{
  "indexed_count": 15,
  "skipped_count": 3,
  "error_count": 0,
  "processing_time": 45.2,
  "index_size": "256MB",
  "documents": [
    {
      "file": "paper_2024.pdf",
      "pages": 12,
      "chunks": 24,
      "metadata": {
        "title": "AI Agents in Finance",
        "author": "Smith, J.",
        "year": 2024
      }
    }
  ]
}
```

#### `search_documents`

Search indexed documents using RAG.

**Parameters:**
- `query` (string, required): Search query
- `top_k` (integer, optional): Number of results (default: 5)
- `include_context` (boolean, optional): Include surrounding context (default: true)
- `use_llm` (boolean, optional): Use LLM for answer generation (default: true)

**Example:**
```json
{
  "name": "search_documents",
  "arguments": {
    "query": "What are the main challenges of implementing AI agents in banking?",
    "top_k": 5,
    "include_context": true,
    "use_llm": true
  }
}
```

**Response:**
```json
{
  "answer": "The main challenges include regulatory compliance, data security, customer trust, and integration with legacy systems...",
  "sources": [
    {
      "document": "AI_Banking_2024.pdf",
      "page": 15,
      "relevance_score": 0.89,
      "text": "Regulatory compliance remains the primary challenge...",
      "metadata": {
        "title": "AI in Banking: Challenges and Opportunities",
        "author": "Smith, J.",
        "year": 2024
      }
    }
  ],
  "query_time": 1.2,
  "llm_response_time": 3.1
}
```

### Reference Management Tools

#### `manage_references`

Import, export, and manage bibliographic references.

**Parameters:**
- `action` (string, required): Action to perform ['import', 'export', 'validate', 'format']
- `format` (string, optional): Bibliography format ['bibtex', 'ris', 'citavi', 'endnote']
- `input_data` (string/object, optional): Input data for import/processing
- `output_path` (string, optional): Output file path

**Example:**
```json
{
  "name": "manage_references",
  "arguments": {
    "action": "export",
    "format": "citavi",
    "output_path": "./output/references.xml"
  }
}
```

#### `create_writing_template`

Generate structured writing templates for academic sections.

**Parameters:**
- `section_type` (string, required): Type of section ['introduction', 'methodology', 'results', 'discussion', 'conclusion']
- `language` (string, optional): Template language ['german', 'english'] (default: 'german')
- `style` (string, optional): Academic style ['mba', 'phd', 'journal'] (default: 'mba')
- `include_examples` (boolean, optional): Include example content (default: true)

**Example:**
```json
{
  "name": "create_writing_template",
  "arguments": {
    "section_type": "methodology",
    "language": "german",
    "style": "mba",
    "include_examples": true
  }
}
```

### Memory and Context Tools

#### `store_context`

Store research context and progress for session persistence.

**Parameters:**
- `context_type` (string, required): Type of context ['research_progress', 'findings', 'todo', 'notes']
- `data` (object, required): Context data to store
- `session_id` (string, optional): Session identifier
- `tags` (array, optional): Tags for categorization

**Example:**
```json
{
  "name": "store_context",
  "arguments": {
    "context_type": "research_progress",
    "data": {
      "chapter": "methodology",
      "completion": 75,
      "last_modified": "2025-01-15",
      "notes": "PRISMA framework implemented"
    },
    "tags": ["methodology", "progress"]
  }
}
```

#### `retrieve_context`

Retrieve stored research context and session data.

**Parameters:**
- `context_type` (string, optional): Filter by context type
- `session_id` (string, optional): Specific session
- `tags` (array, optional): Filter by tags
- `limit` (integer, optional): Maximum results (default: 50)

**Example:**
```json
{
  "name": "retrieve_context",
  "arguments": {
    "context_type": "research_progress",
    "tags": ["methodology"],
    "limit": 10
  }
}
```

## REST API Endpoints

When running as HTTP server (`mcp_server_http.py`), the following endpoints are available:

### Document Search

#### `POST /api/search`

Search documents using RAG.

**Request Body:**
```json
{
  "query": "AI agents in finance",
  "top_k": 5,
  "use_llm": true
}
```

**Response:** Same as `search_documents` tool

### Literature Search

#### `POST /api/literature/search`

Search academic literature.

**Request Body:**
```json
{
  "query": "multi-agent systems banking",
  "databases": ["scopus"],
  "years": "2020-2025"
}
```

**Response:** Same as `search_literature` tool

### Document Indexing

#### `POST /api/documents/index`

Index new documents.

**Request Body:**
```json
{
  "document_path": "./literatur/new_papers/",
  "force_reindex": false
}
```

### System Status

#### `GET /api/status`

Get system status and health information.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "ollama": "running",
    "rag_system": "ready",
    "vector_index": "loaded"
  },
  "statistics": {
    "indexed_documents": 245,
    "total_chunks": 5420,
    "index_size": "1.2GB",
    "last_update": "2025-01-15T10:30:00Z"
  },
  "system_info": {
    "memory_usage": "68%",
    "cpu_usage": "12%",
    "disk_space": "85% free"
  }
}
```

#### `GET /api/statistics`

Get detailed system statistics.

**Response:**
```json
{
  "documents": {
    "total_indexed": 245,
    "by_year": {
      "2024": 89,
      "2023": 76,
      "2022": 54,
      "2021": 26
    },
    "by_journal_quality": {
      "Q1": 198,
      "Q2": 32,
      "conference": 15
    }
  },
  "search_statistics": {
    "total_queries": 1284,
    "avg_response_time": 1.4,
    "cache_hit_rate": 0.76
  },
  "performance": {
    "index_size": "1.2GB",
    "embeddings_count": 54200,
    "last_optimization": "2025-01-14T22:00:00Z"
  }
}
```

## Python API

For direct Python integration:

### RAG System

```python
from scripts.rag_system import RAGSystem

# Initialize RAG system
rag = RAGSystem("config/rag_config.yaml", cpu_only=True)

# Index documents
rag.index_documents("./literatur/finance/")

# Search documents
results = rag.search("AI agents in banking", top_k=5)

# Get LLM-enhanced answer
answer = rag.get_answer("What are the benefits of AI agents?")
```

### Literature Search

```python
from scripts.search_literature import LiteratureSearcher

# Initialize searcher
searcher = LiteratureSearcher("config/research-criteria.yaml")

# Search literature
results = searcher.search(
    query="multi-agent systems finance",
    databases=["scopus", "web_of_science"],
    max_results=50
)

# Filter by quality
q1_papers = searcher.filter_by_quality(results, min_impact_factor=3.0)
```

### Memory System

```python
from memory_system import get_memory

# Get memory instance
memory = get_memory()

# Store context
memory.store_context("research_progress", {
    "chapter": "introduction",
    "status": "completed",
    "word_count": 2500
})

# Retrieve context
progress = memory.retrieve_context("research_progress")

# Create checkpoint
memory.create_checkpoint("chapter_1_complete")
```

## Error Handling

All APIs return consistent error responses:

```json
{
  "error": true,
  "error_type": "ValidationError",
  "message": "Invalid query parameter",
  "details": {
    "parameter": "top_k",
    "expected": "integer between 1 and 100",
    "received": "150"
  },
  "timestamp": "2025-01-15T10:30:00Z",
  "request_id": "req_123456"
}
```

Common error types:
- `ValidationError`: Invalid input parameters
- `ProcessingError`: Document processing failures
- `ServiceUnavailable`: External service unavailable
- `RateLimitExceeded`: API rate limits reached
- `AuthenticationError`: Invalid API credentials

## Rate Limits

- Literature search: 100 requests/hour per API key
- Document indexing: 1000 documents/hour
- RAG search: 1000 queries/hour
- Context storage: 10,000 operations/hour

## Authentication

For production deployment, API keys are required:

```bash
export SCOPUS_API_KEY="your_scopus_key"
export WOS_API_KEY="your_wos_key"
export MCP_SERVER_TOKEN="your_server_token"
```

Include in requests:
```bash
curl -H "Authorization: Bearer your_token" \
     -H "Content-Type: application/json" \
     -d '{"query": "AI agents"}' \
     http://localhost:3001/api/search
```