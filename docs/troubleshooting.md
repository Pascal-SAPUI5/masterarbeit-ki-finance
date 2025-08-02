# Troubleshooting Guide

## Common Issues and Solutions

### 1. Installation and Setup Issues

#### Python Dependencies

**Issue: Package installation fails with dependency conflicts**
```bash
ERROR: pip's dependency resolver does not currently consider all the packages that are installed
```

**Solution:**
```bash
# Clean install with constraints
pip uninstall -y torch torchvision torchaudio
pip cache purge
pip install -r requirements.txt --constraint constraints.txt

# Alternative: Use conda for complex dependencies
conda create -n masterarbeit python=3.10
conda activate masterarbeit
conda install pytorch cpuonly -c pytorch
pip install -r requirements.txt
```

**Issue: CUDA/GPU errors on CPU-only system**
```bash
RuntimeError: Found no NVIDIA driver on your system
```

**Solution:**
```bash
# Ensure CPU-only installation
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Verify CPU-only configuration
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
# Should output: CUDA available: False
```

#### Virtual Environment Issues

**Issue: Virtual environment not activating**
```bash
bash: venv/bin/activate: No such file or directory
```

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate

# On Windows WSL2, ensure proper path
ls -la venv/bin/activate
chmod +x venv/bin/activate
```

### 2. Docker and Container Issues

#### Docker Compose Problems

**Issue: Services fail to start**
```bash
ERROR: for ollama Cannot start service ollama: driver failed programming external connectivity
```

**Solution:**
```bash
# Check port conflicts
sudo netstat -tlnp | grep :11434
sudo lsof -i :11434

# Stop conflicting services
sudo systemctl stop ollama
docker-compose down

# Restart with fresh containers
docker-compose up -d --force-recreate
```

**Issue: Volume mount permissions**
```bash
Permission denied: '/app/.claude_memory'
```

**Solution:**
```bash
# Fix directory permissions
sudo chown -R $USER:$USER .claude_memory research output
chmod -R 755 .claude_memory research output

# Update docker-compose.yml with user mapping
services:
  mcp-server:
    user: "${UID}:${GID}"
    environment:
      - UID=${UID}
      - GID=${GID}
```

#### Ollama Container Issues

**Issue: Ollama model not loading**
```bash
Error: model 'phi3:mini' not found
```

**Solution:**
```bash
# Check Ollama status
docker-compose exec ollama ollama list

# Pull model manually
docker-compose exec ollama ollama pull phi3:mini

# Check available models
docker-compose exec ollama ollama list

# Restart Ollama if needed
docker-compose restart ollama
```

**Issue: Ollama memory errors**
```bash
SIGKILL: OutOfMemoryError
```

**Solution:**
```bash
# Increase memory limits in docker-compose.yml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 16G  # Increase from default
        reservations:
          memory: 8G

# Monitor memory usage
docker stats
```

### 3. RAG System Issues

#### Document Indexing Problems

**Issue: PDF processing fails**
```bash
PyMuPDF Error: cannot open document
```

**Solution:**
```bash
# Check file permissions and corruption
ls -la literatur/finance/
file literatur/finance/document.pdf

# Test PDF integrity
python -c "import fitz; doc = fitz.open('literatur/finance/document.pdf'); print(f'Pages: {len(doc)}')"

# Alternative: Use different PDF processor
# In config/rag_config.yaml:
document_processing:
  pdf_extraction_method: "pdfplumber"  # Instead of "pymupdf"
```

**Issue: OCR fails on scanned documents**
```bash
TesseractNotFoundError: tesseract is not installed
```

**Solution:**
```bash
# Install Tesseract
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng

# Verify installation
tesseract --version
which tesseract

# Test OCR functionality
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

#### Embedding and Search Issues

**Issue: Embedding model download fails**
```bash
ConnectionError: Failed to download sentence-transformers/all-MiniLM-L6-v2
```

**Solution:**
```bash
# Manual model download
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model downloaded successfully')
"

# Alternative: Use local model cache
export SENTENCE_TRANSFORMERS_HOME=./models/
mkdir -p ./models/
```

**Issue: FAISS index corruption**
```bash
RuntimeError: Error in faiss::FileIOReader::operator() 
```

**Solution:**
```bash
# Rebuild FAISS index
rm -rf indexes/
python scripts/rag_system.py index --force-rebuild

# Verify index integrity
python scripts/rag_system.py verify --check-index

# Monitor index size and stats
ls -lh indexes/
python scripts/rag_system.py stats
```

### 4. Memory and Performance Issues

#### Memory Leaks and High Usage

**Issue: Python process consuming excessive memory**
```bash
MemoryError: Unable to allocate array
```

**Solution:**
```bash
# Monitor memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"

# Reduce batch sizes in config/rag_config.yaml:
performance:
  batch_size: 16        # Reduce from 32
  chunk_size: 256       # Reduce from 512
  max_memory_usage: 60  # Reduce from 80

# Clear Python cache
python -c "
import gc
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
gc.collect()
"
```

#### Slow Performance

**Issue: RAG search taking too long**
```bash
Search taking 30+ seconds per query
```

**Solution:**
```bash
# Optimize FAISS index
python scripts/rag_system.py optimize --method IVF

# Enable caching
# In config/rag_config.yaml:
performance:
  cache_responses: true
  cache_embeddings: true
  cache_ttl: 3600

# Monitor query performance
python scripts/rag_system.py benchmark --queries 100
```

### 5. API and Network Issues

#### External API Problems

**Issue: Scopus API rate limiting**
```bash
HTTPError: 429 Client Error: Too Many Requests
```

**Solution:**
```bash
# Check API quota
curl -H "X-ELS-APIKey: YOUR_KEY" \
     "https://api.elsevier.com/analytics/scival/author/metrics"

# Implement exponential backoff
# In config/research-criteria.yaml:
api_settings:
  rate_limits:
    scopus: 50        # Reduce from 100
  retry_policy:
    max_retries: 5
    backoff_factor: 3
```

**Issue: Network connectivity problems**
```bash
ConnectionError: Failed to establish a new connection
```

**Solution:**
```bash
# Test network connectivity
curl -I https://api.elsevier.com/
ping google.com

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Configure proxy in requests
# In Python code:
proxies = {
    'http': 'http://proxy.company.com:8080',
    'https': 'https://proxy.company.com:8080'
}
requests.get(url, proxies=proxies)
```

### 6. Configuration Issues

#### YAML Configuration Errors

**Issue: YAML parsing fails**
```bash
YAMLError: while parsing a block mapping
```

**Solution:**
```bash
# Validate YAML syntax
python -c "
import yaml
with open('config/rag_config.yaml') as f:
    yaml.safe_load(f)
print('YAML is valid')
"

# Check indentation (must be spaces, not tabs)
cat -A config/rag_config.yaml | grep -E "\\t"

# Use YAML linter
yamllint config/rag_config.yaml
```

#### Environment Variable Issues

**Issue: Environment variables not loading**
```bash
KeyError: 'SCOPUS_API_KEY'
```

**Solution:**
```bash
# Check environment variables
env | grep -E "(SCOPUS|WOS|OLLAMA)"

# Load from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Verify in Python
python -c "
import os
print('SCOPUS_API_KEY:', os.getenv('SCOPUS_API_KEY', 'Not set'))
"
```

### 7. File System and Path Issues

#### Path Resolution Problems

**Issue: File paths not resolving correctly**
```bash
FileNotFoundError: [Errno 2] No such file or directory: './literatur/finance/paper.pdf'
```

**Solution:**
```bash
# Check current working directory
pwd
ls -la literatur/

# Use absolute paths
python -c "
import os
print('Current dir:', os.getcwd())
print('Literature dir exists:', os.path.exists('./literatur/'))
"

# Fix relative path issues
export PYTHONPATH=$(pwd)
```

#### File Permission Issues

**Issue: Permission denied errors**
```bash
PermissionError: [Errno 13] Permission denied: './output/results.json'
```

**Solution:**
```bash
# Fix file permissions
chmod 755 output/
chmod 644 output/*.json

# Check file ownership
ls -la output/
chown -R $USER:$USER output/

# Ensure directories exist
mkdir -p {output,research,memory,indexes}
```

### 8. Logging and Debugging

#### Enable Debug Logging

```python
# Add to your script
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# For specific modules
logging.getLogger('scripts.rag_system').setLevel(logging.DEBUG)
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
```

#### Health Check Script

```bash
#!/bin/bash
# health_check.sh

echo "=== System Health Check ==="

# Python environment
echo "Python version:"
python --version

echo -e "\nVirtual environment:"
which python
echo $VIRTUAL_ENV

# Dependencies
echo -e "\nKey dependencies:"
python -c "
import torch; print(f'PyTorch: {torch.__version__}')
import sentence_transformers; print(f'SentenceTransformers: {sentence_transformers.__version__}')
import faiss; print(f'FAISS: {faiss.__version__}')
"

# Services
echo -e "\nDocker services:"
docker-compose ps

# API connectivity
echo -e "\nOllama connectivity:"
curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "Ollama not responding"

# File system
echo -e "\nFile system:"
df -h | grep -E "(/$|/var|/home)"

# Memory
echo -e "\nMemory usage:"
free -h

echo -e "\n=== Health Check Complete ==="
```

### 9. Recovery Procedures

#### System Recovery

```bash
#!/bin/bash
# recovery.sh - System recovery script

echo "Starting system recovery..."

# Stop all services
docker-compose down

# Clean up containers and volumes
docker system prune -f
docker volume prune -f

# Rebuild containers
docker-compose build --no-cache

# Restart services
docker-compose up -d

# Wait for services to start
sleep 30

# Reinitialize system
python scripts/rag_system.py init
python memory_system.py init

# Verify functionality
python scripts/rag_system.py test --self-test

echo "Recovery complete"
```

#### Data Recovery

```bash
#!/bin/bash
# data_recovery.sh - Recover from backup

BACKUP_DIR="/backup/masterarbeit"
LATEST_BACKUP=$(ls -t $BACKUP_DIR | head -1)

echo "Recovering from backup: $LATEST_BACKUP"

# Stop services
docker-compose down

# Restore data
cp -r "$BACKUP_DIR/$LATEST_BACKUP/research" ./
cp -r "$BACKUP_DIR/$LATEST_BACKUP/memory" ./
cp -r "$BACKUP_DIR/$LATEST_BACKUP/output" ./
cp -r "$BACKUP_DIR/$LATEST_BACKUP/indexes" ./

# Restart services
docker-compose up -d

echo "Data recovery complete"
```

### 10. Support and Resources

#### Getting Help

1. **Check logs first:**
   ```bash
   docker-compose logs -f mcp-server
   tail -f logs/application.log
   ```

2. **Search existing issues:**
   - GitHub Issues
   - Documentation FAQ
   - Community forums

3. **Collect diagnostic information:**
   ```bash
   # System information
   uname -a
   docker --version
   python --version
   
   # Error logs
   docker-compose logs --tail=50 > debug.log
   
   # Configuration
   cat config/rag_config.yaml > config_dump.yaml
   ```

4. **Create minimal reproduction:**
   ```python
   # Minimal test case
   from scripts.rag_system import RAGSystem
   
   try:
       rag = RAGSystem("config/rag_config.yaml", cpu_only=True)
       result = rag.search("test query")
       print("Success:", result)
   except Exception as e:
       print("Error:", str(e))
       import traceback
       traceback.print_exc()
   ```

#### Emergency Contacts

- **Technical Issues**: Check GitHub Issues
- **Academic Support**: Contact thesis supervisor
- **Infrastructure**: Contact IT support
- **API Issues**: Contact respective API providers (Scopus, Web of Science)

#### Backup and Recovery

```bash
# Create emergency backup
tar -czf emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    research/ memory/ output/ config/ .env

# Quick system reset
docker-compose down
docker system prune -f
git reset --hard HEAD
git clean -fd
./setup.sh
```

This troubleshooting guide covers the most common issues and their solutions. For persistent problems, enable debug logging and collect diagnostic information before seeking help.