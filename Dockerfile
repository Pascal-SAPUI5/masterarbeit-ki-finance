FROM python:3.10-slim

WORKDIR /app

# System-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install aiohttp for HTTP server
RUN pip install aiohttp

# Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p /app/.claude_memory /app/research/q1-sources /app/output /app/writing/chapters

# Port
EXPOSE 3000

# Starte MCP Server mit HTTP wrapper
CMD ["python", "mcp_server_http.py"]