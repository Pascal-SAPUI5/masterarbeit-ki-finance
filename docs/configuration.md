# Configuration Guide

## Overview

The Masterarbeit KI-Finance system uses multiple configuration files to control various aspects of the research automation environment. This guide covers all configuration options and best practices.

## Configuration Structure

```
config/
├── research-criteria.yaml    # Literature search and quality criteria
├── rag_config.yaml          # RAG system and LLM configuration
├── writing-style.yaml       # Academic writing guidelines
├── ollama_config.yaml       # LLM model configuration
└── mba-standards.json       # MBA thesis standards and requirements
```

## Core Configuration Files

### 1. Research Criteria (`config/research-criteria.yaml`)

Controls literature search parameters, quality filters, and database selection.

```yaml
# Quality criteria for literature selection
quality_criteria:
  journal_rankings:
    - Q1          # First quartile journals (highest quality)
    - A*          # Top-tier conferences
    - Q2          # Second quartile (optional)
  
  impact_factor:
    minimum: 3.0     # Minimum journal impact factor
    preferred: 5.0   # Preferred impact factor for high-quality papers
    threshold: 2.0   # Absolute minimum for inclusion
  
  publication_years:
    start: 2020      # Earliest publication year
    end: 2025        # Latest publication year (current)
    focus: 2022-2025 # Most recent developments (prioritized)
    exclude_before: 2018  # Hard cutoff for relevance

# Database configuration
search_databases:
  primary:           # Primary sources (always searched)
    - scopus
    - web_of_science
    - proquest
    - acm_digital_library
  
  secondary:         # Secondary sources (optional)
    - ieee_xplore
    - google_scholar
    - arxiv
    - crossref
    - pubmed          # For interdisciplinary health-finance papers
  
  specialized:       # Domain-specific databases
    - ssrn           # Social Science Research Network
    - repec          # Research Papers in Economics
    - jstor          # Academic journals archive

# Search keywords and terms
keywords:
  primary:           # Main research terms (highest priority)
    - "AI agents finance"
    - "multi-agent systems banking"
    - "RAG enterprise finance"
    - "LLM financial services"
    - "conversational AI banking"
  
  secondary:         # Supporting terms
    - "autonomous agents fintech"
    - "knowledge graphs banking"
    - "retrieval augmented generation finance"
    - "conversational AI financial advisory"
    - "intelligent financial assistants"
  
  technical:         # Technical implementation terms
    - "SAP BTP AI"
    - "enterprise AI architecture"
    - "financial process automation"
    - "regulatory compliance AI"
  
  domain_specific:   # Finance-specific terms
    - "robo-advisor"
    - "algorithmic trading agents"
    - "risk management AI"
    - "regulatory technology"
    - "financial data processing"

# Exclusion criteria
exclusion_criteria:
  document_types:
    - preprints_only      # Exclude non-peer-reviewed preprints
    - conference_posters  # Exclude poster presentations
    - workshop_papers     # Exclude workshop papers
    - editorial_comments  # Exclude editorials and comments
    - book_reviews       # Exclude book reviews
  
  content_filters:
    - non_english       # Exclude non-English papers (optional)
    - no_full_text      # Exclude papers without full text access
    - duplicate_studies # Exclude duplicate or very similar studies
  
  quality_filters:
    - low_citation_count   # Exclude papers with <5 citations (adjustable)
    - predatory_journals   # Exclude known predatory journals
    - non_peer_reviewed   # Exclude non-peer-reviewed content

# Validation requirements
validation_requirements:
  minimum_citations: 5        # Minimum citation count for inclusion
  peer_reviewed: true         # Must be peer-reviewed
  full_text_available: true   # Full text must be accessible
  abstract_required: true     # Abstract must be available
  doi_required: false         # DOI preferred but not required
  
  quality_checks:
    impact_factor_verification: true
    journal_ranking_verification: true
    author_affiliation_check: false
    methodology_quality_check: true

# API configuration
api_settings:
  rate_limits:
    scopus: 100          # Requests per hour
    web_of_science: 50   # Requests per hour
    crossref: 1000       # Requests per hour
  
  timeout_settings:
    default: 30          # Default timeout in seconds
    large_queries: 120   # Timeout for complex queries
    download: 300        # Timeout for file downloads
  
  retry_policy:
    max_retries: 3
    backoff_factor: 2
    retry_on_errors: [429, 500, 502, 503, 504]

# System performance settings
system:
  llm_model: "phi3:mini"           # LLM model for intelligent processing
  use_gpu: false                   # CPU-only processing
  chunk_size: 256                  # Text chunk size for processing
  embedding_model: "all-MiniLM-L6-v2"  # Embedding model
  max_concurrent_requests: 8       # Maximum concurrent API requests
  cache_duration: 86400           # Cache duration in seconds (24 hours)

# File paths
paths:
  literature_base: "./literatur/"     # Base directory for literature
  index_path: "./indexes/"           # Vector index storage
  cache_path: "./cache/"             # API response cache
  output_path: "./output/"           # Output directory
  temp_path: "./temp/"               # Temporary files

# Citation configuration
citation:
  style: "apa7"                    # Citation style (APA 7th edition)
  include_page_numbers: true       # Include page numbers in citations
  include_doi: true                # Include DOI when available
  include_url: false               # Include URL for online sources
  date_format: "YYYY-MM-DD"        # Date format for citations
```

### 2. RAG Configuration (`config/rag_config.yaml`)

Controls the RAG (Retrieval-Augmented Generation) system behavior and performance.

```yaml
# Core system configuration
system:
  embedding_model: "all-MiniLM-L6-v2"  # Sentence transformer model
  llm_model: "phi3:mini"               # Ollama model for generation
  chunk_size: 512                      # Text chunk size (tokens)
  chunk_overlap: 50                    # Overlap between chunks
  max_context_length: 4096             # Maximum context for LLM
  temperature: 0.1                     # LLM temperature (0.0-1.0)
  top_p: 0.9                          # Nucleus sampling parameter

# File and directory paths
paths:
  index_path: "./indexes/"             # Vector index storage
  documents_path: "./literatur/"       # Source documents
  output_path: "./output/"             # Generated outputs
  cache_path: "./cache/"               # Embedding cache
  models_path: "./models/"             # Downloaded models
  logs_path: "./logs/"                 # Log files

# Search configuration
search:
  top_k: 5                            # Number of results to return
  relevance_threshold: 0.7            # Minimum relevance score
  max_results: 100                    # Maximum results per query
  similarity_metric: "cosine"         # Distance metric (cosine/euclidean)
  rerank_results: true                # Enable result reranking
  diversify_results: true             # Diversify results to avoid redundancy
  
  # Advanced search options
  semantic_search_weight: 0.7         # Weight for semantic search
  keyword_search_weight: 0.3          # Weight for keyword search
  boost_recent_papers: true           # Boost papers from recent years
  boost_high_impact: true             # Boost high-impact journals

# Performance optimization
performance:
  cpu_only: true                      # Use CPU-only processing
  max_memory_usage: 80                # Maximum memory usage (percentage)
  batch_size: 32                      # Batch size for embedding
  num_threads: 8                      # Number of CPU threads
  
  # Ollama-specific settings
  ollama_batch_size: 4                # Batch size for Ollama requests
  ollama_timeout: 30                  # Timeout for Ollama requests
  ollama_max_tokens: 2048             # Maximum tokens per response
  
  # Caching settings
  cache_responses: true               # Cache LLM responses
  cache_embeddings: true              # Cache embeddings
  cache_ttl: 86400                    # Cache time-to-live (seconds)
  max_cache_size: "2GB"               # Maximum cache size
  
  # Concurrency settings
  max_concurrent_requests: 8          # Maximum concurrent requests
  request_timeout: 60                 # Request timeout (seconds)
  retry_attempts: 3                   # Number of retry attempts

# Document processing
document_processing:
  # PDF processing
  pdf_extraction_method: "pymupdf"    # PDF text extraction method
  use_ocr: true                       # Enable OCR for scanned documents
  ocr_language: "deu+eng"             # OCR languages
  ocr_confidence_threshold: 60        # Minimum OCR confidence
  
  # Text processing
  min_chunk_length: 100               # Minimum chunk length
  max_chunk_length: 1000              # Maximum chunk length
  remove_headers_footers: true        # Remove headers and footers
  clean_whitespace: true              # Clean excess whitespace
  preserve_formatting: false          # Preserve original formatting
  
  # Metadata extraction
  extract_metadata: true              # Extract document metadata
  extract_references: true            # Extract reference lists
  extract_figures: false              # Extract figure captions
  extract_tables: false               # Extract table content

# Quality control
quality_control:
  # Text quality filters
  min_text_length: 50                 # Minimum text length per chunk
  max_noise_ratio: 0.3                # Maximum noise-to-content ratio
  filter_duplicates: true             # Remove duplicate chunks
  similarity_threshold: 0.95          # Threshold for duplicate detection
  
  # Content validation
  validate_encoding: true             # Validate text encoding
  validate_language: true             # Validate document language
  expected_languages: ["en", "de"]    # Expected languages
  
  # Error handling
  skip_corrupted_files: true          # Skip corrupted documents
  log_processing_errors: true         # Log processing errors
  continue_on_error: true             # Continue processing despite errors

# Logging and monitoring
logging:
  level: "INFO"                       # Log level (DEBUG/INFO/WARNING/ERROR)
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_logging: true                  # Enable file logging
  console_logging: true               # Enable console logging
  max_log_size: "10MB"                # Maximum log file size
  backup_count: 5                     # Number of log backups
  
  # Performance monitoring
  track_performance: true             # Track processing performance
  log_slow_queries: true              # Log slow queries (>5 seconds)
  monitor_memory: true                # Monitor memory usage
  alert_on_errors: false              # Send alerts on errors

# Advanced features
advanced:
  # Experimental features
  enable_gpu_fallback: false          # Enable GPU fallback if available
  use_quantized_models: false         # Use quantized models for speed
  enable_model_caching: true          # Cache loaded models in memory
  
  # Custom preprocessing
  custom_preprocessors: []            # List of custom preprocessing functions
  custom_postprocessors: []           # List of custom postprocessing functions
  
  # Integration settings
  mcp_integration: true               # Enable MCP server integration
  api_server: false                   # Enable REST API server
  webhook_notifications: false       # Enable webhook notifications
  
  # Security settings
  sanitize_inputs: true               # Sanitize user inputs
  validate_file_types: true          # Validate uploaded file types
  max_file_size: "100MB"              # Maximum file size
  allowed_extensions: [".pdf", ".txt", ".docx"]  # Allowed file extensions
```

### 3. Writing Style Configuration (`config/writing-style.yaml`)

Defines academic writing standards and style guidelines for German MBA theses.

```yaml
# Academic writing standards for German MBA thesis
academic_standards:
  citation_style: "apa7"              # APA 7th edition
  language: "german"                  # Primary language
  formality_level: "academic"         # Academic formality
  perspective: "third_person"         # Writing perspective
  tense_preference: "present"         # Preferred tense for literature review
  
  # Structure requirements
  chapter_structure:
    - "Einleitung"
    - "Theoretische Grundlagen"
    - "Methodik"
    - "Analyse und Ergebnisse"
    - "Diskussion"
    - "Fazit und Ausblick"
    - "Literaturverzeichnis"
    - "Anhang"
  
  # Formatting standards
  formatting:
    font_family: "Times New Roman"
    font_size: 12
    line_spacing: 1.5
    margin_top: 2.5
    margin_bottom: 2.0
    margin_left: 2.5
    margin_right: 2.5
    page_numbering: true
    header_footer: true

# German academic writing conventions
german_conventions:
  # Terminology preferences
  terminology:
    "AI": "Künstliche Intelligenz (KI)"
    "machine learning": "maschinelles Lernen"
    "artificial intelligence": "künstliche Intelligenz"
    "chatbot": "Chatbot"
    "natural language processing": "Verarbeitung natürlicher Sprache"
  
  # Style guidelines
  style_rules:
    use_passive_voice: false          # Prefer active voice
    avoid_contractions: true          # No contractions in academic writing
    use_formal_pronouns: true         # Use formal pronouns (Sie/Ihnen)
    capitalize_nouns: true            # German noun capitalization
    use_compound_words: true          # German compound word preference
  
  # Sentence structure
  sentence_guidelines:
    max_sentence_length: 25           # Maximum words per sentence
    preferred_sentence_length: 15     # Preferred words per sentence
    avoid_run_on_sentences: true      # Avoid overly complex sentences
    use_transition_words: true        # Use appropriate transitions
  
  # Paragraph structure
  paragraph_guidelines:
    max_paragraph_length: 150         # Maximum words per paragraph
    preferred_paragraph_length: 100   # Preferred words per paragraph
    topic_sentence_required: true     # Require clear topic sentences
    conclusion_sentence_preferred: true  # Prefer concluding sentences

# Citation and referencing
citation_rules:
  # In-text citations
  in_text_format: "(Autor, Jahr, S. X)"  # German APA format
  multiple_authors_format: "(Autor1 & Autor2, Jahr)"
  page_number_format: "S. X-Y"           # German page format
  
  # Reference list
  reference_format: "apa7_german"        # German APA 7 format
  sort_references: "alphabetical"        # Alphabetical sorting
  include_doi: true                       # Include DOI when available
  include_url: false                      # URLs only for online-only sources
  
  # Special cases
  corporate_authors: true                 # Allow corporate authors
  edited_volumes: true                    # Include edited volume format
  conference_papers: true                 # Include conference paper format
  website_citations: "minimal"           # Minimal website citations

# Quality standards
quality_standards:
  # Content quality
  argumentation:
    require_evidence: true              # Require evidence for claims
    logical_flow: true                  # Ensure logical argument flow
    critical_analysis: true             # Require critical analysis
    balanced_perspective: true          # Present balanced viewpoints
  
  # Language quality
  language_checks:
    grammar_check: true                 # Enable grammar checking
    spell_check: true                   # Enable spell checking
    style_consistency: true             # Check style consistency
    readability_score: true             # Calculate readability scores
  
  # Academic integrity
  integrity_checks:
    plagiarism_detection: true          # Enable plagiarism detection
    self_citation_limit: 10             # Maximum self-citations (%)
    source_diversity: true              # Require diverse sources
    recent_sources_ratio: 60            # Minimum recent sources (%)

# Templates and examples
templates:
  # Introduction templates
  introduction:
    problem_statement: |
      Die fortschreitende Digitalisierung im Finanzwesen stellt Unternehmen vor 
      neue Herausforderungen bei der Implementierung intelligenter Systeme...
    
    research_gap: |
      Während bestehende Studien die technischen Aspekte von KI-Agenten untersuchen,
      fehlt eine umfassende Analyse der praktischen Implementierung im deutschen 
      Finanzsektor...
    
    research_questions: |
      Vor diesem Hintergrund stellt sich die Frage: Wie können KI-Agenten 
      erfolgreich in deutsche Finanzinstitute integriert werden?
  
  # Methodology templates
  methodology:
    research_design: |
      Die vorliegende Arbeit folgt einem Design-Science-Ansatz nach Hevner et al. (2004)
      und kombiniert systematische Literaturanalyse mit explorativer Fallstudienforschung...
    
    data_collection: |
      Die Datenerhebung erfolgt durch eine systematische Literaturanalyse nach dem
      PRISMA-Framework (Page et al., 2021) sowie semi-strukturierte Experteninterviews...
  
  # Results templates
  results:
    findings_introduction: |
      Die Analyse der erhobenen Daten zeigt folgende zentrale Erkenntnisse...
    
    evidence_presentation: |
      Wie aus Abbildung X hervorgeht, bestätigen die empirischen Befunde...

# Automated checks and suggestions
automation:
  # Style checking
  style_checks:
    consistency_checks: true            # Check formatting consistency
    citation_format_check: true         # Verify citation formatting
    reference_completeness: true        # Check reference completeness
    figure_caption_format: true         # Check figure caption formatting
  
  # Content suggestions
  content_suggestions:
    transition_improvement: true        # Suggest better transitions
    argument_strengthening: true        # Suggest argument improvements
    evidence_suggestions: true          # Suggest additional evidence
    structure_optimization: true        # Suggest structural improvements
  
  # Language improvements
  language_improvements:
    vocabulary_enhancement: true        # Suggest vocabulary improvements
    sentence_variety: true              # Suggest sentence structure variety
    academic_tone: true                 # Ensure academic tone
    conciseness: true                   # Suggest more concise phrasing

# Output formatting
output_settings:
  # Document formats
  supported_formats:
    - "docx"                           # Microsoft Word
    - "pdf"                            # PDF export
    - "latex"                          # LaTeX format
    - "markdown"                       # Markdown format
  
  # Export options
  export_options:
    include_comments: false            # Include review comments
    include_tracked_changes: false     # Include tracked changes
    compress_images: true              # Compress embedded images
    optimize_file_size: true           # Optimize output file size
  
  # Formatting presets
  preset_styles:
    "mba_thesis": "config/styles/mba_thesis.docx"
    "journal_article": "config/styles/journal_article.docx"
    "conference_paper": "config/styles/conference_paper.docx"
```

### 4. Ollama Configuration (`config/ollama_config.yaml`)

Controls the local language model behavior and performance.

```yaml
# Ollama LLM configuration
model_settings:
  # Primary model
  primary_model: "phi3:mini"           # Main model for generation
  fallback_model: "llama2:7b"          # Fallback if primary unavailable
  
  # Model parameters
  temperature: 0.1                     # Creativity level (0.0-1.0)
  top_p: 0.9                          # Nucleus sampling
  top_k: 40                           # Top-k sampling
  repeat_penalty: 1.1                 # Repetition penalty
  seed: 42                            # Random seed for reproducibility
  
  # Generation limits
  max_tokens: 2048                    # Maximum output tokens
  context_length: 4096                # Maximum context length
  timeout: 30                         # Request timeout (seconds)

# Performance optimization
performance:
  # Resource allocation
  num_threads: 8                      # CPU threads for inference
  num_gpu: 0                          # Number of GPUs (0 = CPU only)
  memory_limit: "8GB"                 # Memory limit for model
  
  # Batching
  batch_size: 4                       # Batch size for requests
  max_concurrent: 8                   # Maximum concurrent requests
  queue_size: 50                      # Request queue size
  
  # Caching
  keep_alive: "24h"                   # Keep model loaded duration
  cache_responses: true               # Cache responses
  cache_size: "1GB"                   # Response cache size

# Connection settings
connection:
  host: "localhost"                   # Ollama server host
  port: 11434                         # Ollama server port
  protocol: "http"                    # Connection protocol
  
  # Retry configuration
  max_retries: 3                      # Maximum retry attempts
  retry_delay: 1                      # Delay between retries (seconds)
  exponential_backoff: true           # Use exponential backoff
  
  # Health checking
  health_check_interval: 30           # Health check interval (seconds)
  health_check_timeout: 5             # Health check timeout
  auto_restart: true                  # Auto-restart on failure

# Prompt templates
prompts:
  # RAG answer generation
  rag_answer_template: |
    Du bist ein wissenschaftlicher Assistent für eine Masterarbeit über KI-Agenten im Finanzwesen.
    Beantworte die folgende Frage basierend auf den bereitgestellten Quellen.
    
    Frage: {query}
    
    Relevante Quellen:
    {sources}
    
    Anweisungen:
    - Verwende nur Informationen aus den bereitgestellten Quellen
    - Zitiere korrekt im APA-Format
    - Schreibe in akademischem Deutsch
    - Sei präzise und objektiv
    
    Antwort:
  
  # Literature summarization
  summarization_template: |
    Erstelle eine prägnante Zusammenfassung des folgenden wissenschaftlichen Textes:
    
    Text: {text}
    
    Zusammenfassung (max. 200 Wörter):
  
  # Citation verification
  citation_template: |
    Überprüfe und formatiere die folgende Zitation nach APA 7 Standard:
    
    Zitation: {citation}
    
    Korrekte APA-Formatierung:

# Quality control
quality_control:
  # Response validation
  response_validation:
    min_length: 50                     # Minimum response length
    max_length: 2000                   # Maximum response length
    check_relevance: true              # Check response relevance
    check_citations: true              # Validate citations
  
  # Content filtering
  content_filters:
    inappropriate_content: true        # Filter inappropriate content
    factual_accuracy: false            # Check factual accuracy (experimental)
    bias_detection: false              # Detect potential bias (experimental)
  
  # Output formatting
  output_formatting:
    clean_whitespace: true             # Clean excess whitespace
    fix_encoding: true                 # Fix character encoding issues
    validate_markdown: true            # Validate markdown formatting

# Logging and monitoring
monitoring:
  # Request logging
  log_requests: true                  # Log all requests
  log_responses: false                # Log responses (privacy concern)
  log_performance: true               # Log performance metrics
  
  # Metrics collection
  collect_metrics: true               # Collect usage metrics
  metrics_interval: 60               # Metrics collection interval
  export_metrics: false              # Export metrics to external system
  
  # Alerting
  enable_alerts: false               # Enable alerting
  alert_on_errors: true              # Alert on error conditions
  alert_threshold: 5                 # Alert after N consecutive errors

# Development and debugging
development:
  debug_mode: false                  # Enable debug mode
  verbose_logging: false             # Enable verbose logging
  save_requests: false               # Save requests for debugging
  mock_responses: false              # Use mock responses for testing
  
  # Testing
  test_model_on_startup: true        # Test model availability on startup
  run_health_checks: true            # Run periodic health checks
  benchmark_performance: false       # Run performance benchmarks
```

### 5. MBA Standards (`config/mba-standards.json`)

Defines MBA thesis requirements and evaluation criteria.

```json
{
  "thesis_requirements": {
    "structure": {
      "required_chapters": [
        "Einleitung",
        "Theoretische Grundlagen", 
        "Methodik",
        "Analyse und Ergebnisse",
        "Diskussion",
        "Fazit und Ausblick"
      ],
      "optional_chapters": [
        "Executive Summary",
        "Danksagung",
        "Anhang"
      ],
      "min_pages": 60,
      "max_pages": 80,
      "bibliography_min_sources": 50,
      "recent_sources_percentage": 60
    },
    
    "formatting": {
      "font": "Times New Roman",
      "font_size": 12,
      "line_spacing": 1.5,
      "margins": {
        "top": 2.5,
        "bottom": 2.0,
        "left": 2.5,
        "right": 2.5
      },
      "citation_style": "apa7",
      "page_numbering": true,
      "table_of_contents": true,
      "list_of_figures": true,
      "list_of_tables": true
    },
    
    "content_quality": {
      "min_journal_quality": "Q1",
      "min_impact_factor": 3.0,
      "max_self_citations": 10,
      "plagiarism_threshold": 15,
      "required_methodologies": [
        "systematic_literature_review",
        "empirical_analysis"
      ]
    }
  },
  
  "evaluation_criteria": {
    "content": {
      "weight": 60,
      "subcriteria": {
        "problem_formulation": 15,
        "theoretical_foundation": 20,
        "methodology": 25,
        "analysis_quality": 25,
        "conclusions": 15
      }
    },
    "methodology": {
      "weight": 25,
      "subcriteria": {
        "research_design": 30,
        "data_collection": 25,
        "data_analysis": 25,
        "validity": 20
      }
    },
    "presentation": {
      "weight": 15,
      "subcriteria": {
        "structure": 30,
        "language": 30,
        "formatting": 20,
        "citations": 20
      }
    }
  },
  
  "deadlines": {
    "proposal_submission": "2025-03-01",
    "literature_review": "2025-04-15",
    "methodology_chapter": "2025-05-01",
    "first_draft": "2025-06-15",
    "final_submission": "2025-08-01",
    "defense_date": "2025-09-01"
  },
  
  "supervision": {
    "meeting_frequency": "biweekly",
    "progress_reports": "monthly",
    "review_cycles": 3,
    "feedback_turnaround": 7
  }
}
```

## Environment Variables

### Required Environment Variables

```bash
# API Keys (Optional but recommended)
SCOPUS_API_KEY=your_scopus_api_key
WOS_API_KEY=your_web_of_science_key
CROSSREF_EMAIL=your.email@university.edu

# System Configuration
PYTHONUNBUFFERED=1
MCP_MODE=claude
RESEARCH_ENV=production

# Ollama Configuration
OLLAMA_HOST=0.0.0.0
OLLAMA_KEEP_ALIVE=24h
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_PARALLEL=4
NUM_THREAD=16

# Resource Limits
MAX_MEMORY_USAGE=80
MAX_CONCURRENT_REQUESTS=8
CACHE_TTL=86400

# Security Settings
SANITIZE_INPUTS=true
MAX_FILE_SIZE=100MB
ALLOWED_EXTENSIONS=.pdf,.txt,.docx
```

### Development Environment Variables

```bash
# Development Mode
DEBUG_MODE=true
VERBOSE_LOGGING=true
SAVE_REQUESTS=false
MOCK_RESPONSES=false

# Testing
RUN_TESTS_ON_STARTUP=true
BENCHMARK_PERFORMANCE=false
HEALTH_CHECK_INTERVAL=30

# Debugging
LOG_LEVEL=DEBUG
LOG_TO_FILE=true
LOG_REQUESTS=true
LOG_PERFORMANCE=true
```

## Configuration Validation

The system includes configuration validation to ensure all settings are correct:

```python
# Validate configuration
python scripts/validate_config.py

# Check specific configuration file
python scripts/validate_config.py --file config/rag_config.yaml

# Validate all configurations
python scripts/validate_config.py --all
```

## Best Practices

### 1. Configuration Management
- Keep sensitive data in environment variables
- Use separate configurations for development/production
- Validate configurations before deployment
- Document all configuration changes

### 2. Performance Tuning
- Adjust `chunk_size` based on document types
- Optimize `batch_size` for your hardware
- Monitor memory usage and adjust limits
- Use caching for frequently accessed data

### 3. Quality Control
- Set appropriate quality thresholds
- Regularly update keyword lists
- Monitor API rate limits
- Validate citation formats

### 4. Security
- Never commit API keys to version control
- Use strong authentication for production
- Regularly rotate API keys
- Monitor access logs

This configuration guide provides comprehensive control over all aspects of the research automation system, enabling customization for different research contexts and institutional requirements.