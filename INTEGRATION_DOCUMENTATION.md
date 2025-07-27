# Ollama & Windows Claude Desktop Integration Documentation

## Overview

This document provides comprehensive instructions for setting up and using the integrated Ollama LLM system with Windows Claude Desktop through WSL2.

## Architecture

```
Windows Claude Desktop
         |
         | (MCP Protocol)
         v
    WSL2 Bridge (Port 3001)
         |
         v
   MCP Server (Docker)
         |
         v
   Ollama Service (Docker)
         |
         v
    phi3:mini Model
```

## Phase 1: Ollama Docker Setup

### 1. Prerequisites

- Docker installed and running in WSL2
- At least 8GB free disk space
- 16GB RAM recommended

### 2. Starting Services

```bash
# Option 1: Using setup script
./scripts/setup_ollama.sh

# Option 2: Manual setup
docker-compose up -d

# Pull phi3:mini model
docker exec masterarbeit-ollama ollama pull phi3:mini
```

### 3. Configuration

The system is optimized for Intel i5-13600K with:
- 16 CPU threads allocated
- Memory-mapped file loading
- Response caching enabled
- Batch size of 4 requests

### 4. Verification

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test generation
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "phi3:mini", "prompt": "Hello, world!"}'
```

## Phase 2: Windows Integration

### 1. Network Configuration

Services are configured to bind on 0.0.0.0 for Windows access:
- Ollama: Port 11434
- MCP Server: Port 3001 (changed from 3000 to avoid Grafana conflict)

### 2. Windows Setup

Run PowerShell as Administrator:
```powershell
# Navigate to project directory in Windows
cd \\wsl$\Ubuntu\home\a503038\Projects\masterarbeit-ki-finance

# Run setup script
powershell -ExecutionPolicy Bypass -File scripts\setup_windows_bridge.ps1
```

### 3. Claude Desktop Configuration

The script automatically updates `%APPDATA%\Claude\claude_desktop_config.json` with:
```json
{
  "mcpServers": {
    "masterarbeit-rag": {
      "command": "node",
      "args": ["C:\\Users\\[username]\\wsl-mcp-bridge.js", "http://[WSL_IP]:3001"]
    }
  }
}
```

### 4. Firewall Rules

The setup script automatically creates firewall rules for:
- Port 3001 (MCP Server)
- Port 11434 (Ollama)

## Usage

### Starting All Services

```bash
# In WSL2
./start_mcp_server.sh
```

This will:
1. Start Ollama if not running
2. Check model availability
3. Start MCP server
4. Display connection information

### Using from Claude Desktop

1. Restart Claude Desktop after configuration
2. The MCP server will appear in Claude's settings
3. Use RAG queries naturally in conversations

### MCP Tools Available

1. **generate_with_ollama** - Generate text with caching
2. **batch_generate_ollama** - Process multiple prompts
3. **query_rag_system** - Search documents and generate answers
4. **check_ollama_status** - Monitor service health

## Performance Optimization

### Caching System

Responses are cached in:
- Memory (100 items, LRU eviction)
- Disk (`~/.cache/ollama_responses/`)
- 1-hour TTL

### Batch Processing

The system processes requests in batches of 4 for optimal CPU utilization.

### Resource Limits

Docker containers have resource limits:
- Ollama: 12 CPU cores, 16GB memory
- MCP Server: Default Docker limits

## Troubleshooting

### Common Issues

1. **Port 3000 conflict**
   - Solution: We changed to port 3001

2. **Ollama not responding**
   ```bash
   docker logs masterarbeit-ollama
   docker restart masterarbeit-ollama
   ```

3. **Windows can't connect**
   - Check WSL2 IP: `wsl hostname -I`
   - Verify firewall rules
   - Test connection: `curl http://[WSL_IP]:3001/health`

4. **Model not found**
   ```bash
   docker exec masterarbeit-ollama ollama list
   docker exec masterarbeit-ollama ollama pull phi3:mini
   ```

### Logs

- MCP Server: `docker logs masterarbeit-mcp-server`
- Ollama: `docker logs masterarbeit-ollama`
- Windows Bridge: Check Claude Desktop developer console

## Performance Benchmarks

With Intel i5-13600K:
- Single query: ~500ms (cached: ~10ms)
- Batch of 4: ~1.5s
- RAG query: ~2s (depending on document retrieval)

## Security Considerations

1. Services bind to 0.0.0.0 for LAN access
2. No authentication on Ollama API
3. Firewall rules restrict to local machine
4. Consider VPN for remote access

## Maintenance

### Updating Models

```bash
# List models
docker exec masterarbeit-ollama ollama list

# Update model
docker exec masterarbeit-ollama ollama pull phi3:mini

# Remove old model
docker exec masterarbeit-ollama ollama rm old-model
```

### Clearing Cache

```python
from src.utils.ollama_cache import OllamaResponseCache
cache = OllamaResponseCache()
cache.clear()
```

### Backup

Important data locations:
- Ollama models: Docker volume `ollama-data`
- Cache: `~/.cache/ollama_responses/`
- MCP memory: `./.claude_memory/`

## Next Steps

1. Monitor performance with included benchmarking tools
2. Adjust batch sizes based on workload
3. Consider adding more models for specialized tasks
4. Implement request queuing for high load scenarios