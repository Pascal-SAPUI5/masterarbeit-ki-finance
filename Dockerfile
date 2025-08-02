FROM python:3.10-slim

WORKDIR /app

# System-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Configure pip for better SSL handling and retries
RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org download.pytorch.org" && \
    pip config set global.timeout 120 && \
    pip config set global.retries 5

# Install aiohttp for HTTP server
RUN pip install --upgrade pip && \
    pip install aiohttp

# Python-Abhängigkeiten with retry mechanism
COPY requirements.txt constraints.txt ./
# Install PyTorch CPU version first to avoid downloading GPU version
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==2.1.0+cpu torchvision==0.16.0+cpu -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install --no-cache-dir -c constraints.txt -r requirements.txt || \
    (sleep 5 && pip install --no-cache-dir -c constraints.txt -r requirements.txt) || \
    (sleep 10 && pip install --no-cache-dir --index-url https://pypi.org/simple -c constraints.txt -r requirements.txt)

# Anwendungscode
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p /app/.claude_memory /app/research/q1-sources /app/output /app/writing/chapters

# Port
EXPOSE 3000

# Starte MCP Server mit HTTP wrapper
CMD ["python", "mcp_server_http.py"]