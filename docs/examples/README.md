# Examples Directory

This directory contains practical examples demonstrating how to use the Masterarbeit KI-Finance system components.

## Available Examples

### 1. RAG System Usage (`rag_usage_example.py`)

Comprehensive examples of using the RAG (Retrieval-Augmented Generation) system:

- **Basic RAG Search**: Simple document search and retrieval
- **Literature Search Workflow**: Complete academic literature search process
- **Context-Aware Search**: Using memory system for contextual queries
- **Document Indexing**: Adding new documents to the search index
- **Citation Management**: Formatting and managing academic citations
- **Advanced Features**: Complex queries and multi-step reasoning
- **Performance Monitoring**: Benchmarking and optimization

**Usage:**
```bash
# Run all examples
python docs/examples/rag_usage_example.py

# Run specific example functions individually
python -c "
from docs.examples.rag_usage_example import example_basic_rag_search
example_basic_rag_search()
"
```

### 2. MCP Integration (`mcp_integration_example.py`)

Examples of integrating with the MCP (Model Context Protocol) server:

- **Document Search via MCP**: Using MCP tools for document retrieval
- **Literature Search**: Academic database search through MCP
- **Citation Verification**: Validating and formatting citations
- **Reference Management**: Export to various bibliography formats
- **Memory Operations**: Storing and retrieving research context
- **Quality Assessment**: Evaluating research paper quality
- **Workflow Automation**: Automated research workflows
- **Async Operations**: Concurrent processing examples
- **Error Handling**: Robust error management patterns

**Usage:**
```bash
# Run all MCP examples
python docs/examples/mcp_integration_example.py

# Run async examples
python -c "
import asyncio
from docs.examples.mcp_integration_example import example_async_operations
asyncio.run(example_async_operations())
"
```

## Mermaid Diagrams

The `diagrams/` subdirectory contains Mermaid diagrams illustrating system architecture and workflows:

### 1. System Architecture (`system_architecture.mmd`)

High-level system architecture showing:
- Client layer (Claude Code, Web UI, CLI)
- MCP interface layer
- Core processing components
- AI/ML services
- Data storage systems
- External service integrations

### 2. RAG Workflow (`rag_workflow.mmd`)

Detailed RAG processing workflow:
- Document ingestion and processing
- Text extraction and chunking
- Embedding generation
- Vector storage and retrieval
- LLM-enhanced response generation

### 3. Literature Search Flow (`literature_search_flow.mmd`)

Academic literature search process:
- Multi-database querying
- Quality filtering criteria
- Result aggregation and deduplication
- Citation formatting and export

### 4. MCP Integration (`mcp_integration.mmd`)

Sequence diagram showing MCP protocol interactions:
- Client-server communication
- Tool invocation patterns
- Error handling flows
- Async operation patterns

## Running Examples

### Prerequisites

1. **System Setup**: Ensure the main system is installed and configured
2. **Services Running**: Start Docker services if using containerized setup
3. **Environment**: Activate Python virtual environment

```bash
# Activate virtual environment
source venv/bin/activate

# Start services (if using Docker)
docker-compose up -d

# Verify system health
python scripts/rag_system.py test --self-test
```

### Example Execution

```bash
# Navigate to project root
cd /path/to/masterarbeit-ki-finance/

# Run RAG examples
python docs/examples/rag_usage_example.py

# Run MCP examples
python docs/examples/mcp_integration_example.py

# Run specific example functions
python -c "
from docs.examples.rag_usage_example import example_basic_rag_search
from docs.examples.mcp_integration_example import MCPExamples

# RAG example
example_basic_rag_search()

# MCP example
mcp = MCPExamples()
mcp.example_document_search()
"
```

### Viewing Mermaid Diagrams

1. **GitHub/GitLab**: Diagrams render automatically in markdown files
2. **VS Code**: Install Mermaid Preview extension
3. **Online**: Use [Mermaid Live Editor](https://mermaid-js.github.io/mermaid-live-editor/)
4. **Local**: Use mermaid-cli tool

```bash
# Install mermaid-cli (optional)
npm install -g @mermaid-js/mermaid-cli

# Generate PNG from mermaid
mmdc -i docs/diagrams/system_architecture.mmd -o system_architecture.png
```

## Customizing Examples

### Adding New Examples

1. **Create new Python file** in `docs/examples/`
2. **Follow naming convention**: `{component}_example.py`
3. **Include docstrings** and error handling
4. **Add to this README** with usage instructions

### Modifying Existing Examples

1. **Test thoroughly** before committing changes
2. **Update docstrings** to reflect changes
3. **Maintain backward compatibility** where possible
4. **Update README** if usage changes

### Example Template

```python
#!/usr/bin/env python3
"""
Component Name Examples
Brief description of what this example demonstrates.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import required modules
from scripts.component import ComponentClass

def example_basic_functionality():
    """Example of basic component functionality."""
    print("=== Basic Functionality Example ===")
    
    try:
        # Your example code here
        component = ComponentClass()
        result = component.do_something()
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all examples."""
    examples = [
        example_basic_functionality,
        # Add more examples here
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
```

## Troubleshooting Examples

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Service Unavailable**: Check Docker services are running
3. **Configuration Errors**: Verify config files are valid
4. **Permission Errors**: Check file and directory permissions

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run examples with debug output
python docs/examples/rag_usage_example.py
```

### Test Data

Some examples require test data:

```bash
# Create test documents
mkdir -p literatur/test/
echo "This is a test document about AI agents." > literatur/test/test_doc.txt

# Create test configuration
cp config/rag_config.yaml config/test_config.yaml
```

## Contributing Examples

1. **Focus on practical use cases** that users commonly need
2. **Include error handling** and edge cases
3. **Add comprehensive docstrings** explaining the purpose
4. **Test with various configurations** and data sets
5. **Update documentation** to include new examples

## Support

- **Documentation**: Refer to main project documentation
- **Issues**: Create GitHub issues for example-specific problems  
- **Community**: Join discussions for best practices
- **Academic**: Contact thesis supervisor for research-specific guidance

These examples provide a comprehensive starting point for using the system components and can be adapted for specific research needs.