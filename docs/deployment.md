# Deployment Guide

## System Requirements

### Minimum Requirements
- **OS**: Linux/WSL2 with Ubuntu 22.04+
- **CPU**: 4+ cores (Intel/AMD x64)
- **RAM**: 16 GB (32 GB recommended for large document sets)
- **Storage**: 50 GB free space (100 GB+ for extensive literature)
- **Network**: Stable internet connection for API access

### Recommended Configuration
- **CPU**: 8+ cores with AVX2 support
- **RAM**: 32 GB
- **Storage**: SSD with 200+ GB free space
- **GPU**: Not required (CPU-optimized)

### Software Dependencies
- **Python**: 3.10 or higher
- **Docker**: 20.10+ with Docker Compose
- **Git**: For version control
- **curl**: For health checks and API testing

## Installation Methods

### Method 1: Docker Deployment (Recommended)

#### 1. Clone Repository
```bash
git clone <repository-url>
cd masterarbeit-ki-finance
```

#### 2. Environment Setup
```bash
# Create environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

Required environment variables:
```env
# API Keys (optional but recommended)
SCOPUS_API_KEY=your_scopus_api_key
WOS_API_KEY=your_web_of_science_key
CROSSREF_EMAIL=your.email@university.edu

# System Configuration
PYTHONUNBUFFERED=1
MCP_MODE=claude
RESEARCH_ENV=production

# Resource Limits
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_PARALLEL=4
NUM_THREAD=16
```

#### 3. Build and Start Services
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 4. Initialize System
```bash
# Wait for Ollama to start
sleep 30

# Pull language model
docker-compose exec ollama ollama pull phi3:mini

# Initialize indices (if needed)
docker-compose exec mcp-server python scripts/rag_system.py init
```

#### 5. Verify Installation
```bash
# Test Ollama
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Hello world",
  "stream": false
}'

# Test MCP Server
curl http://localhost:3001/health

# Test RAG system
docker-compose exec mcp-server python scripts/rag_system.py test --self-test
```

### Method 2: Native Installation

#### 1. Python Environment Setup
```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### 2. Install Dependencies
```bash
# Install CPU-optimized packages
pip install -r requirements.txt --constraint constraints.txt

# Install Tesseract for OCR
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng

# Install additional system dependencies
sudo apt-get install poppler-utils libpoppler-cpp-dev
```

#### 3. Install Ollama
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Pull model
ollama pull phi3:mini
```

#### 4. Initialize System
```bash
# Create required directories
mkdir -p {research,output,indexes,memory,.claude_memory}

# Initialize memory system
python memory_system.py init

# Test installation
python scripts/rag_system.py test --self-test
```

## Configuration

### Core Configuration Files

#### 1. Research Criteria (`config/research-criteria.yaml`)
```yaml
quality_criteria:
  journal_rankings:
    - Q1
    - A*
  impact_factor:
    minimum: 3.0
    preferred: 5.0
  publication_years:
    start: 2020
    end: 2025

search_databases:
  primary:
    - scopus
    - web_of_science
    - proquest
  secondary:
    - ieee_xplore
    - acm_digital_library

keywords:
  primary:
    - "AI agents finance"
    - "multi-agent systems banking"
  secondary:
    - "autonomous agents fintech"
    - "knowledge graphs banking"
```

#### 2. RAG Configuration (`config/rag_config.yaml`)
```yaml
system:
  embedding_model: "all-MiniLM-L6-v2"
  llm_model: "phi3:mini"
  chunk_size: 512
  chunk_overlap: 50

performance:
  cpu_only: true
  max_memory_usage: 80
  ollama_batch_size: 4
  cache_responses: true
  max_concurrent_requests: 8

paths:
  index_path: "./indexes/"
  documents_path: "./literatur/"
  output_path: "./output/"
```

#### 3. Docker Configuration Customization

For production deployment, modify `docker-compose.yml`:

```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          cpus: '16'        # Adjust based on available CPUs
          memory: 32G       # Adjust based on available RAM
        reservations:
          cpus: '8'
          memory: 8G
    environment:
      - OLLAMA_NUM_PARALLEL=8  # Increase for better performance
      - NUM_THREAD=32          # Match CPU cores

  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
```

### Security Configuration

#### 1. API Key Management
```bash
# Store API keys securely
echo "SCOPUS_API_KEY=your_key" >> .env
echo "WOS_API_KEY=your_key" >> .env

# Set proper permissions
chmod 600 .env
```

#### 2. Network Security
```yaml
# docker-compose.yml - Production network configuration
networks:
  masterarbeit-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  mcp-server:
    networks:
      masterarbeit-net:
        ipv4_address: 172.20.0.10
```

#### 3. Container Security
```yaml
services:
  mcp-server:
    security_opt:
      - no-new-privileges:true
    user: "1000:1000"  # Non-root user
    read_only: true
    tmpfs:
      - /tmp
      - /var/tmp
```

## Production Deployment

### 1. Reverse Proxy Setup (Nginx)

```nginx
# /etc/nginx/sites-available/masterarbeit-mcp
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for long-running operations
        proxy_read_timeout 300s;
        proxy_connect_timeout 30s;
        proxy_send_timeout 300s;
    }
}
```

Enable and start:
```bash
sudo ln -s /etc/nginx/sites-available/masterarbeit-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. SSL/TLS Configuration

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Monitoring Setup

#### Docker Health Checks
```yaml
services:
  mcp-server:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  ollama:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Log Management
```bash
# Configure log rotation
sudo tee /etc/logrotate.d/masterarbeit-docker <<EOF
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    size 100M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### 4. Backup Configuration

#### Automated Backup Script
```bash
#!/bin/bash
# /usr/local/bin/backup-masterarbeit.sh

BACKUP_DIR="/backup/masterarbeit"
PROJECT_DIR="/path/to/masterarbeit-ki-finance"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup critical data
cp -r "$PROJECT_DIR/research" "$BACKUP_DIR/$DATE/"
cp -r "$PROJECT_DIR/output" "$BACKUP_DIR/$DATE/"
cp -r "$PROJECT_DIR/memory" "$BACKUP_DIR/$DATE/"
cp -r "$PROJECT_DIR/config" "$BACKUP_DIR/$DATE/"
cp -r "$PROJECT_DIR/indexes" "$BACKUP_DIR/$DATE/"

# Backup Docker volumes
docker run --rm -v masterarbeit-ki-finance_ollama-data:/source -v "$BACKUP_DIR/$DATE":/backup alpine tar czf /backup/ollama-data.tar.gz -C /source .

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR/$DATE"
```

Schedule backup:
```bash
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-masterarbeit.sh
```

## Performance Optimization

### 1. Resource Tuning

#### CPU Optimization
```bash
# Set CPU governor to performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Optimize Python threading
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
```

#### Memory Optimization
```bash
# Increase virtual memory
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. Docker Optimization

```yaml
# docker-compose.override.yml for production
version: '3.8'
services:
  ollama:
    deploy:
      resources:
        limits:
          cpus: '16'
          memory: 32G
    environment:
      - OLLAMA_KEEP_ALIVE=24h
      - OLLAMA_MAX_LOADED_MODELS=1
      - OLLAMA_NUM_PARALLEL=8

  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
    environment:
      - WORKERS=4  # Adjust based on CPU cores
```

### 3. Index Optimization

```bash
# Optimize FAISS index
python scripts/rag_system.py optimize --rebuild-index

# Clean up unused embeddings
python scripts/rag_system.py cleanup --remove-orphaned

# Update index statistics
python scripts/rag_system.py stats --update-metadata
```

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Issues
```bash
# Check Ollama status
docker-compose exec ollama ollama list

# Restart Ollama
docker-compose restart ollama

# Check logs
docker-compose logs ollama
```

#### 2. Memory Issues
```bash
# Monitor memory usage
docker stats

# Clear Python cache
python -c "import torch; torch.cuda.empty_cache()" 2>/dev/null || true

# Restart services
docker-compose restart mcp-server
```

#### 3. Index Corruption
```bash
# Rebuild index
docker-compose exec mcp-server python scripts/rag_system.py index --force-rebuild

# Verify index integrity
docker-compose exec mcp-server python scripts/rag_system.py verify --check-index
```

### Health Monitoring

#### Service Status Check
```bash
#!/bin/bash
# health-check.sh

echo "=== Masterarbeit System Health Check ==="

# Check Docker services
echo "Docker Services:"
docker-compose ps

# Check Ollama
echo -e "\nOllama Status:"
curl -s http://localhost:11434/api/tags | jq -r '.models[].name' || echo "Ollama not responding"

# Check MCP Server
echo -e "\nMCP Server Status:"
curl -s http://localhost:3001/health | jq . || echo "MCP Server not responding"

# Check disk space
echo -e "\nDisk Usage:"
df -h | grep -E "(/$|/var|/home)"

# Check memory
echo -e "\nMemory Usage:"
free -h
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f mcp-server

# Search for errors
docker-compose logs mcp-server 2>&1 | grep -i error

# Monitor real-time performance
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

## Scaling Considerations

### Horizontal Scaling

For multiple instances:

```yaml
services:
  mcp-server:
    deploy:
      replicas: 3
    ports:
      - "3001-3003:3000"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - mcp-server
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Database Scaling

For large document collections:

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  qdrant_data:
```

This deployment guide provides comprehensive instructions for setting up the system in various environments, from development to production scale.